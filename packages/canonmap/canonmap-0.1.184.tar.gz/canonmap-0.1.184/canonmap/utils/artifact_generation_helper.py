import logging
import pickle
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
import os
import zipfile

from canonmap.logger import setup_logger
from canonmap.config import CanonMapArtifactsConfig, CanonMapEmbeddingConfig
from canonmap.requests.artifact_generation_request import ArtifactGenerationRequest
from canonmap.utils.convert_input import convert_data_to_df
from canonmap.utils.process_table import process_table
from canonmap.utils.clean_columns import clean_and_format_columns, _clean_column_name
from canonmap.utils.infer_schema import generate_db_schema_from_df
from canonmap.utils.canonical_entities_generator import generate_canonical_entities
from canonmap.utils.generate_mariadb_loader_script import generate_mariadb_loader_script
from canonmap.utils.embedding_model_factory import get_embedder_from_config
from canonmap.utils.artifact_validation import upload_artifacts_to_gcs

logger = setup_logger()


def _create_filtered_schema(
    full_schema: Dict[str, Dict[str, Any]],
    source_name: str,
    table_name: str,
    field_names: List[str],
    clean_field_names: bool = False
) -> Dict[str, Dict[str, Any]]:
    """
    Create a filtered schema containing only the specified fields.
    
    Args:
        full_schema: The complete schema dictionary
        source_name: Name of the data source
        table_name: Name of the table
        field_names: List of field names to include
        clean_field_names: Whether field names were cleaned
        
    Returns:
        Filtered schema dictionary
    """
    if not field_names:
        return {}
    
    # Create case-insensitive mapping for field matching
    table_schema = full_schema.get(source_name, {}).get(table_name, {})
    field_mapping = {}
    
    for field_name in field_names:
        # Try different variations of the field name
        cleaned_field = _clean_column_name(field_name) if clean_field_names else field_name
        field_variations = [field_name, cleaned_field]
        
        for variation in field_variations:
            # Case-insensitive matching
            for actual_field in table_schema.keys():
                if actual_field.lower() == variation.lower():
                    field_mapping[field_name] = actual_field
                    break
            if field_name in field_mapping:
                break
    
    # Create filtered schema
    filtered_schema = {source_name: {table_name: {}}}
    for original_field, actual_field in field_mapping.items():
        if actual_field in table_schema:
            filtered_schema[source_name][table_name][actual_field] = table_schema[actual_field]
    
    return filtered_schema


def _normalize(name: str) -> str:
    """Lowercase, strip, and replace spaces with underscores."""
    return name.lower().strip().replace(" ", "_")


def _get_paths(
    base: Path, source: str, table: str, db_type: str
) -> Dict[str, Path]:
    """
    Returns the artifact file paths for a single table.
    'base' is already the correct directory (nested for multi, root for single).
    """
    base.mkdir(parents=True, exist_ok=True)
    return {
        "schema": base / f"{source}_{table}_schema.pkl",
        "entity_fields_schema": base / f"{source}_{table}_entity_fields_schema.pkl",
        "semantic_fields_schema": base / f"{source}_{table}_semantic_fields_schema.pkl",
        "processed_data": base / f"{source}_{table}_processed_data.pkl",
        "canonical_entities": base / f"{source}_{table}_canonical_entities.pkl",
        "canonical_entity_embeddings": base / f"{source}_{table}_canonical_entity_embeddings.npz",
        "data_loader_script": base / f"load_{table}_table_to_{db_type}.py",
        "semantic_texts": base / f"{source}_{table}_semantic_texts.zip",
    }


def _write_combined_artifacts(
    config: ArtifactGenerationRequest,
    output_path: Path,
    entities: Dict[str, list[dict]],
    embeddings: Dict[str, np.ndarray],
    tables: Dict[str, pd.DataFrame],
) -> Dict[str, Path]:
    combined: Dict[str, Path] = {}

    # 1) processed_data
    if config.save_processed_data:
        processed_path = output_path / f"{config.source_name}_processed_data.pkl"
        combined_data = {
            "metadata": {"source_name": config.source_name, "tables": list(tables.keys())},
            "tables": {
                name: clean_and_format_columns(df)
                if config.clean_field_names else df
                for name, df in tables.items()
            },
        }
        with open(processed_path, "wb") as f:
            pickle.dump(combined_data, f)
        combined["processed_data"] = processed_path

    # 2) schema
    if config.generate_schema:
        schema = {config.source_name: {}}
        for name, df in tables.items():
            schema[config.source_name][name] = generate_db_schema_from_df(
                df, config.schema_database_type, config.clean_field_names
            )
        schema_path = output_path / f"{config.source_name}_schema.pkl"
        with open(schema_path, "wb") as f:
            pickle.dump(schema, f)
        combined["schema"] = schema_path
        
        # Create filtered schemas for entity fields and semantic fields
        if config.entity_fields:
            # Extract unique field names from entity_fields
            entity_field_names = list(set([
                ef.field_name for ef in config.entity_fields
                if ef.table_name in tables.keys()
            ]))
            
            if entity_field_names:
                entity_schema = {}
                for table_name in tables.keys():
                    table_entity_fields = [
                        ef.field_name for ef in config.entity_fields
                        if ef.table_name == table_name
                    ]
                    if table_entity_fields:
                        entity_schema.update(_create_filtered_schema(
                            schema, config.source_name, table_name, 
                            table_entity_fields, config.clean_field_names
                        ))
                
                if entity_schema:
                    entity_schema_path = output_path / f"{config.source_name}_entity_fields_schema.pkl"
                    with open(entity_schema_path, "wb") as f:
                        pickle.dump(entity_schema, f)
                    combined["entity_fields_schema"] = entity_schema_path
        
        if config.semantic_fields:
            # Extract unique field names from semantic_fields
            semantic_field_names = list(set([
                sf.field_name for sf in config.semantic_fields
                if sf.table_name in tables.keys()
            ]))
            
            if semantic_field_names:
                semantic_schema = {}
                for table_name in tables.keys():
                    table_semantic_fields = [
                        sf.field_name for sf in config.semantic_fields
                        if sf.table_name == table_name
                    ]
                    if table_semantic_fields:
                        semantic_schema.update(_create_filtered_schema(
                            schema, config.source_name, table_name, 
                            table_semantic_fields, config.clean_field_names
                        ))
                
                if semantic_schema:
                    semantic_schema_path = output_path / f"{config.source_name}_semantic_fields_schema.pkl"
                    with open(semantic_schema_path, "wb") as f:
                        pickle.dump(semantic_schema, f)
                    combined["semantic_fields_schema"] = semantic_schema_path

    # 3) flat canonical entities
    if config.generate_canonical_entities:
        flat_list: list[dict] = []
        for tbl in tables.keys():
            flat_list.extend(entities.get(tbl, []))

        ents_path = output_path / f"{config.source_name}_canonical_entities.pkl"
        with open(ents_path, "wb") as f:
            pickle.dump(flat_list, f)
        combined["canonical_entities"] = ents_path

    # 4) flat combined embeddings
    if config.generate_embeddings and embeddings:
        arrays = [embeddings[tbl] for tbl in tables.keys()]
        flat_embs = np.vstack(arrays) if arrays else np.empty((0,))
        emb_path = output_path / f"{config.source_name}_canonical_entity_embeddings.npz"
        np.savez_compressed(emb_path, embeddings=flat_embs)
        combined["canonical_entity_embeddings"] = emb_path

    # 5) loader script
    if config.generate_schema:
        loader_path = output_path / f"load_{config.source_name}_to_{config.schema_database_type}.py"
        script = generate_mariadb_loader_script(
            schema[config.source_name], list(tables.keys()), str(loader_path), is_combined=True
        )
        loader_path.write_text(script)
        combined["data_loader_script"] = loader_path

    # 6) combined semantic texts
    if config.generate_semantic_texts and config.semantic_fields:
        combined_semantic_path = output_path / f"{config.source_name}_semantic_texts.zip"
        
        with zipfile.ZipFile(combined_semantic_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            used_filenames = {}  # Track used filenames to handle duplicates
            
            for table_name, df in tables.items():
                # Create case-insensitive column mapping for this table
                column_map = {col.lower(): col for col in df.columns}
                
                # Filter semantic fields for this table
                table_semantic_fields = [
                    sf for sf in (config.semantic_fields or [])
                    if sf.table_name == table_name
                ]
                
                # Create a dictionary to store all semantic field values for each row
                row_semantic_fields = {}
                row_title_values = {}  # Store title field values for each row
                
                # Get title field for this table if specified
                title_field = None
                if config.semantic_text_title_fields:
                    for tf in config.semantic_text_title_fields:
                        if tf.table_name == table_name:
                            title_field_name = tf.field_name
                            cleaned_title = _clean_column_name(title_field_name)
                            field_to_check = cleaned_title if config.clean_field_names else title_field_name
                            
                            # Try to find the title field (case-insensitive)
                            field_lower = title_field_name.lower()
                            cleaned_lower = cleaned_title.lower()
                            field_to_check_lower = field_to_check.lower()
                            
                            if field_to_check_lower in column_map:
                                title_field = column_map[field_to_check_lower]
                            elif field_lower in column_map:
                                title_field = column_map[field_lower]
                            elif cleaned_lower in column_map:
                                title_field = column_map[cleaned_lower]
                            
                            if title_field and title_field in df.columns:
                                # Get title values for each row
                                for row_idx, row in df.iterrows():
                                    value = row[title_field]
                                    if not pd.isna(value):
                                        value_str = str(value).strip()
                                        if value_str and value_str.lower() not in {"", "nan", "none", "null"}:
                                            # Clean the value to make it filesystem-safe
                                            safe_value = "".join(c for c in value_str if c.isalnum() or c in " -_")
                                            safe_value = safe_value.strip().replace(" ", "_")
                                            row_title_values[row_idx] = safe_value
                            else:
                                logger.warning(f"Title field '{title_field_name}' not found in table '{table_name}'")
                            break  # Only use the first matching title field
                
                for sf in table_semantic_fields:
                    field_name = sf.field_name
                    cleaned_field = _clean_column_name(field_name)
                    field_to_check = cleaned_field if config.clean_field_names else field_name
                    
                    # Try to find the field in the DataFrame (case-insensitive)
                    field_lower = field_name.lower()
                    cleaned_lower = cleaned_field.lower()
                    field_to_check_lower = field_to_check.lower()
                    
                    actual_field = None
                    if field_to_check_lower in column_map:
                        actual_field = column_map[field_to_check_lower]
                    elif field_lower in column_map:
                        actual_field = column_map[field_lower]
                    elif cleaned_lower in column_map:
                        actual_field = column_map[cleaned_lower]
                    
                    if actual_field and actual_field in df.columns:
                        # Process each row for this semantic field
                        for row_idx, row in df.iterrows():
                            value = row[actual_field]
                            
                            # Skip null/empty values
                            if pd.isna(value):
                                continue
                            
                            value_str = str(value).strip()
                            if not value_str or value_str.lower() in {"", "nan", "none", "null"}:
                                continue
                            
                            # Initialize dict for this row if not exists
                            if row_idx not in row_semantic_fields:
                                row_semantic_fields[row_idx] = []
                            
                            # Add field and value to the row's data
                            row_semantic_fields[row_idx].append(f"{actual_field}: {value_str}")
                
                # Create one text file per row containing all semantic fields
                for row_idx, field_values in row_semantic_fields.items():
                    if field_values:  # Only create file if there are non-empty values
                        # Use title field value if available, otherwise use row index
                        if row_idx in row_title_values:
                            base_filename = f"{table_name}_{row_title_values[row_idx]}"
                        else:
                            base_filename = f"{table_name}_row_{row_idx}"
                        
                        # Handle duplicate filenames by adding a counter
                        filename = f"{base_filename}.txt"
                        counter = used_filenames.get(base_filename, 0)
                        while filename in zipf.namelist():
                            counter += 1
                            filename = f"{base_filename}_{counter}.txt"
                        used_filenames[base_filename] = counter
                        
                        content = "\n".join(field_values)
                        zipf.writestr(filename, content)
        
        combined["semantic_texts"] = combined_semantic_path

    return combined


def generate_artifacts_helper(
    request: ArtifactGenerationRequest,
    artifacts_config: CanonMapArtifactsConfig,
    embedder=None,
) -> Dict[str, Any]:
    """
    Generate artifacts based on the request and current configuration.
    
    Args:
        request: ArtifactGenerationRequest specifying what to generate
        artifacts_config: Configuration for artifacts storage
        embedder: Optional embedder instance for generating embeddings
        
    Returns:
        Dict containing generation results and metadata
        
    Raises:
        ValueError: If request validation fails
        FileNotFoundError: If input path doesn't exist
        Exception: If generation process fails
    """
    # Validate request
    if not request.input_path:
        raise ValueError("input_path is required in ArtifactGenerationRequest")
    
    # Use artifacts_config for storage settings
    output_path = artifacts_config.artifacts_local_path
    
    # Normalize input_path: convert Path → str
    raw_input = request.input_path
    if isinstance(raw_input, Path):
        raw_input = str(raw_input)

    # 1) ingest
    if isinstance(raw_input, str) and Path(raw_input).is_dir():
        logger.info(f"Directory input detected at '{raw_input}'")
        if not request.file_pattern:
            logger.warning("A 'file_pattern' must be provided when passing a directory.")
        else:
            logger.info(f"Using file pattern '{request.file_pattern}' to match files.")
    
    # Validate input path exists
    if isinstance(request.input_path, (str, Path)):
        input_path = Path(request.input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input path does not exist: {request.input_path}")

    tables = convert_data_to_df(
        raw_input,
        request.num_rows,
        request.recursive,
        request.file_pattern
    )
    logger.info(f"Ingested {len(tables)} tables")
    logger.info(f"Tables: {tables}")

    # 2) wrap single DataFrame in a dict
    if isinstance(tables, pd.DataFrame):
        # Prioritize config.table_name if provided, otherwise use file name or default
        if request.table_name:
            raw = request.table_name
        elif isinstance(raw_input, str) and Path(raw_input).is_file():
            raw = Path(raw_input).stem
        else:
            raw = "data"
        tables = {raw: tables}

    is_multi = len(tables) > 1

    # 3) optionally normalize all table names and entity_fields
    if request.normalize_table_names:
        normalized: Dict[str, pd.DataFrame] = {}
        for raw_name, df in tables.items():
            norm = _normalize(raw_name)
            normalized[norm] = df
        tables = normalized

        if request.entity_fields:
            for ef in request.entity_fields:
                ef.table_name = _normalize(ef.table_name)
        
        if request.semantic_fields:
            for sf in request.semantic_fields:
                sf.table_name = _normalize(sf.table_name)

    result_paths: Dict[str, Dict[str, Path]] = {}
    entity_map: Dict[str, list[dict]] = {}
    embedding_jobs: list[tuple[str, list[str]]] = []
    logger.info(f"Normalized tables: {tables}")
    logger.info(f"Entity fields: {request.entity_fields}")
    logger.info(f"Semantic fields: {request.semantic_fields}")

    # 4) per-table processing
    for table_name, df in tables.items():
        logger.info(f"Processing table: {table_name}")
        local_cfg = request.model_copy(deep=True)
        local_cfg.table_name = table_name

        base_dir = Path(output_path) / table_name if is_multi else Path(output_path)
        paths = _get_paths(
            base_dir, request.source_name, table_name, request.schema_database_type
        )

        paths, entities, emb_strs = process_table(df, local_cfg, paths)
        result_paths[table_name] = paths
        entity_map[table_name] = entities

        if request.generate_embeddings:
            embedding_jobs.append((table_name, emb_strs))

    # 5) embeddings (parallel per-table for speed)
    embedding_map: Dict[str, np.ndarray] = {}
    if request.generate_embeddings and embedder:
        logger.info(f"Embedding canonical entities for {len(embedding_jobs)} tables…")
        embedding_map = embedder.embed_texts(embedding_jobs)
        for tbl, arr in embedding_map.items():
            emb_path = result_paths[tbl]["canonical_entity_embeddings"]
            np.savez_compressed(emb_path, embeddings=arr)

    # 6) combined (multi-table) artifacts
    if is_multi:
        logger.info("Writing combined artifacts…")
        output_dir = Path(output_path)
        result_paths[request.source_name] = _write_combined_artifacts(
            request, output_dir, entity_map, embedding_map, tables
        )

    logger.info("Artifact generation pipeline finished")

    # After artifact generation, handle GCP upload if requested
    if request.upload_to_gcp:
        logger.info("Uploading all artifacts in local directory to GCS as requested...")
        uploaded = upload_artifacts_to_gcs(
            str(artifacts_config.artifacts_local_path),
            artifacts_config.artifacts_gcp_service_account_json_path,
            artifacts_config.artifacts_gcp_bucket_name,
            artifacts_config.artifacts_gcp_bucket_prefix,
        )
        logger.info(f"Uploaded {len(uploaded)} artifact files to GCS: {uploaded}")

    # Return a basic response since generation logic is not yet implemented
    return {
        "status": "success",
        "message": "Artifact generation endpoint is working. Generation logic is not yet implemented.",
    } 