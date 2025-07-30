#!/usr/bin/env python3
"""
Comprehensive example demonstrating the new response models in CanonMap.

This script shows how to:
1. Generate artifacts and handle the detailed response
2. Map entities and process the comprehensive results
3. Handle errors and warnings properly
4. Access processing statistics and metadata
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from canonmap import (
    CanonMap,
    CanonMapArtifactsConfig,
    CanonMapEmbeddingConfig,
    ArtifactGenerationRequest,
    EntityMappingRequest,
    EntityField,
    SemanticField,
    TableFieldFilter,
    ArtifactGenerationResponse,
    EntityMappingResponse
)

def setup_canonmap() -> CanonMap:
    """Set up CanonMap with configuration."""
    artifacts_config = CanonMapArtifactsConfig(
        artifacts_local_path=Path("./example_artifacts"),
        artifacts_gcp_bucket_name="",
        artifacts_gcp_bucket_prefix="",
        artifacts_gcp_service_account_json_path="",
        troubleshooting=False
    )
    
    embedding_config = CanonMapEmbeddingConfig(
        embedding_model_name="sentence-transformers/all-MiniLM-L12-v2",
        embedding_model_path=Path("./models/sentence-transformers/all-MiniLM-L12-v2"),
        troubleshooting=False
    )
    
    return CanonMap(artifacts_config, embedding_config, verbose=True)

def create_sample_data() -> str:
    """Create sample data for demonstration."""
    data = {
        'player_name': ['LeBron James', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo'],
        'team': ['Los Angeles Lakers', 'Golden State Warriors', 'Phoenix Suns', 'Milwaukee Bucks'],
        'position': ['Small Forward', 'Point Guard', 'Small Forward', 'Power Forward'],
        'description': [
            'Versatile forward with exceptional basketball IQ and leadership',
            'Elite shooter and playmaker with incredible range',
            'Scoring machine with smooth offensive game',
            'Dominant two-way player with incredible athleticism'
        ],
        'biography': [
            'Born in Akron, Ohio. 4x NBA Champion, 4x MVP, 18x All-Star',
            'Born in Akron, Ohio. 4x NBA Champion, 2x MVP, 8x All-Star',
            'Born in Washington, D.C. 2x NBA Champion, 1x MVP, 12x All-Star',
            'Born in Athens, Greece. 1x NBA Champion, 2x MVP, 8x All-Star'
        ],
        'age': [38, 35, 34, 28],
        'salary_millions': [47.6, 51.9, 44.1, 45.6]
    }
    
    df = pd.DataFrame(data)
    file_path = "sample_players.csv"
    df.to_csv(file_path, index=False)
    return file_path

def demonstrate_artifact_generation(canonmap: CanonMap, data_file: str):
    """Demonstrate artifact generation with response handling."""
    print("\n" + "="*60)
    print("ARTIFACT GENERATION EXAMPLE")
    print("="*60)
    
    # Create request
    request = ArtifactGenerationRequest(
        input_path=data_file,
        source_name="basketball",
        table_name="players",
        entity_fields=[
            EntityField(table_name="players", field_name="player_name"),
            EntityField(table_name="players", field_name="team")
        ],
        semantic_fields=[
            SemanticField(table_name="players", field_name="description"),
            SemanticField(table_name="players", field_name="biography")
        ],
        generate_schema=True,
        generate_canonical_entities=True,
        generate_embeddings=True,
        generate_semantic_texts=True,
        save_processed_data=True,
        clean_field_names=True
    )
    
    print(f"Request configuration:")
    print(f"  - Source: {request.source_name}")
    print(f"  - Table: {request.table_name}")
    print(f"  - Entity fields: {len(request.entity_fields)}")
    print(f"  - Semantic fields: {len(request.semantic_fields)}")
    print(f"  - Generate schema: {request.generate_schema}")
    print(f"  - Generate embeddings: {request.generate_embeddings}")
    
    # Generate artifacts
    print("\nGenerating artifacts...")
    response: ArtifactGenerationResponse = canonmap.generate_artifacts(request)
    
    # Process response
    print(f"\nResponse Analysis:")
    print(f"  Status: {response.status}")
    print(f"  Message: {response.message}")
    print(f"  Source: {response.source_name}")
    print(f"  Tables: {response.table_names}")
    print(f"  Timestamp: {response.timestamp}")
    
    # Generated artifacts
    print(f"\nGenerated Artifacts ({len(response.generated_artifacts)}):")
    for artifact in response.generated_artifacts:
        print(f"  - {artifact.artifact_type}: {artifact.file_path}")
        if artifact.file_size_bytes:
            print(f"    Size: {artifact.file_size_bytes} bytes")
        if artifact.table_name:
            print(f"    Table: {artifact.table_name}")
    
    # Processing statistics
    if response.processing_stats:
        stats = response.processing_stats
        print(f"\nProcessing Statistics:")
        print(f"  Tables processed: {stats.total_tables_processed}")
        print(f"  Rows processed: {stats.total_rows_processed}")
        print(f"  Entities generated: {stats.total_entities_generated}")
        print(f"  Embeddings generated: {stats.total_embeddings_generated}")
        print(f"  Processing time: {stats.processing_time_seconds:.2f} seconds")
        print(f"  Start time: {stats.start_time}")
        print(f"  End time: {stats.end_time}")
    
    # Convenience paths
    print(f"\nConvenience Paths:")
    if response.schema_path:
        print(f"  Schema: {response.schema_path}")
    if response.entity_fields_schema_path:
        print(f"  Entity fields schema: {response.entity_fields_schema_path}")
    if response.semantic_fields_schema_path:
        print(f"  Semantic fields schema: {response.semantic_fields_schema_path}")
    if response.canonical_entities_path:
        print(f"  Canonical entities: {response.canonical_entities_path}")
    if response.canonical_entity_embeddings_path:
        print(f"  Embeddings: {response.canonical_entity_embeddings_path}")
    if response.semantic_texts_path:
        print(f"  Semantic texts: {response.semantic_texts_path}")
    
    # Errors and warnings
    if response.errors:
        print(f"\nErrors ({len(response.errors)}):")
        for error in response.errors:
            print(f"  - {error.error_type}: {error.error_message}")
            if error.table_name:
                print(f"    Table: {error.table_name}")
            if error.field_name:
                print(f"    Field: {error.field_name}")
            if error.row_index is not None:
                print(f"    Row: {error.row_index}")
    
    if response.warnings:
        print(f"\nWarnings ({len(response.warnings)}):")
        for warning in response.warnings:
            print(f"  - {warning}")
    
    # GCP upload info
    if response.gcp_upload_info:
        print(f"\nGCP Upload Information:")
        print(f"  {json.dumps(response.gcp_upload_info, indent=2)}")
    
    return response

def demonstrate_entity_mapping(canonmap: CanonMap):
    """Demonstrate entity mapping with response handling."""
    print("\n" + "="*60)
    print("ENTITY MAPPING EXAMPLE")
    print("="*60)
    
    # Create request
    request = EntityMappingRequest(
        entities=[
            "LeBron James",
            "Stephen Curry", 
            "Kevin Durant",
            "Giannis Antetokounmpo",
            "Michael Jordan",  # This won't match exactly
            "Kobe Bryant"      # This won't match exactly
        ],
        filters=[
            TableFieldFilter(
                table_name="players",
                table_fields=["player_name", "team"]
            )
        ],
        num_results=3,
        weights={
            'semantic': 0.40,
            'fuzzy': 0.40,
            'initial': 0.10,
            'keyword': 0.05,
            'phonetic': 0.05,
        },
        use_semantic_search=True,
        threshold=0.0
    )
    
    print(f"Request configuration:")
    print(f"  Entities to map: {len(request.entities)}")
    print(f"  Number of results: {request.num_results}")
    print(f"  Use semantic search: {request.use_semantic_search}")
    print(f"  Threshold: {request.threshold}")
    print(f"  Weights: {request.weights}")
    
    # Map entities
    print("\nMapping entities...")
    response: EntityMappingResponse = canonmap.map_entities(request)
    
    # Process response
    print(f"\nResponse Analysis:")
    print(f"  Status: {response.status}")
    print(f"  Message: {response.message}")
    print(f"  Total entities processed: {response.total_entities_processed}")
    print(f"  Total matches found: {response.total_matches_found}")
    print(f"  Processing time: {response.processing_time_seconds:.3f} seconds")
    print(f"  Average time per entity: {response.average_processing_time_ms:.1f}ms")
    print(f"  Timestamp: {response.timestamp}")
    
    # Configuration summary
    print(f"\nConfiguration Summary:")
    print(f"  Results requested: {response.num_results_requested}")
    print(f"  Threshold used: {response.threshold_used}")
    print(f"  Weights used: {response.weights_used}")
    print(f"  Semantic search used: {response.use_semantic_search}")
    
    # Detailed results
    print(f"\nDetailed Results:")
    for i, result in enumerate(response.results):
        print(f"\n  Entity {i+1}: '{result.query}'")
        print(f"    Total matches: {result.total_matches}")
        print(f"    Processing time: {result.processing_time_ms:.1f}ms")
        
        if result.best_match:
            print(f"    Best match: '{result.best_match.entity}' (score: {result.best_match.score:.3f})")
            print(f"      Passes: {result.best_match.passes}")
            print(f"      Field: {result.best_match.field_name}")
            print(f"      Table: {result.best_match.table_name}")
            print(f"      Source: {result.best_match.source_name}")
        
        print(f"    All matches:")
        for j, match in enumerate(result.matches[:3]):  # Show top 3
            print(f"      {j+1}. '{match.entity}' (score: {match.score:.3f}, passes: {match.passes})")
            if match.metadata:
                print(f"         Metadata: {match.metadata}")
    
    # Errors and warnings
    if response.errors:
        print(f"\nErrors ({len(response.errors)}):")
        for error in response.errors:
            print(f"  - {error['error_type']}: {error['error_message']}")
            if 'entity' in error:
                print(f"    Entity: {error['entity']}")
    
    if response.warnings:
        print(f"\nWarnings ({len(response.warnings)}):")
        for warning in response.warnings:
            print(f"  - {warning}")
    
    return response

def demonstrate_response_serialization(artifact_response: ArtifactGenerationResponse, 
                                     mapping_response: EntityMappingResponse):
    """Demonstrate response serialization capabilities."""
    print("\n" + "="*60)
    print("RESPONSE SERIALIZATION EXAMPLE")
    print("="*60)
    
    # Convert to dictionaries
    artifact_dict = artifact_response.to_dict()
    mapping_dict = mapping_response.to_dict()
    
    print(f"Artifact Generation Response (serialized):")
    print(f"  Keys: {list(artifact_dict.keys())}")
    print(f"  Status: {artifact_dict['status']}")
    print(f"  Generated artifacts: {len(artifact_dict['generated_artifacts'])}")
    print(f"  Errors: {len(artifact_dict['errors'])}")
    print(f"  Warnings: {len(artifact_dict['warnings'])}")
    
    print(f"\nEntity Mapping Response (serialized):")
    print(f"  Keys: {list(mapping_dict.keys())}")
    print(f"  Status: {mapping_dict['status']}")
    print(f"  Total entities: {mapping_dict['total_entities_processed']}")
    print(f"  Total matches: {mapping_dict['total_matches_found']}")
    print(f"  Results: {len(mapping_dict['results'])}")
    
    # Demonstrate JSON serialization
    print(f"\nJSON Serialization:")
    try:
        artifact_json = json.dumps(artifact_dict, indent=2)
        mapping_json = json.dumps(mapping_dict, indent=2)
        print(f"  Artifact response JSON length: {len(artifact_json)} characters")
        print(f"  Mapping response JSON length: {len(mapping_json)} characters")
        print(f"  ✅ Both responses can be serialized to JSON successfully")
    except Exception as e:
        print(f"  ❌ JSON serialization failed: {e}")
    
    # Demonstrate reconstruction
    print(f"\nResponse Reconstruction:")
    try:
        reconstructed_artifact = ArtifactGenerationResponse.from_dict(artifact_dict)
        reconstructed_mapping = EntityMappingResponse.from_dict(mapping_dict)
        print(f"  ✅ Artifact response reconstructed successfully")
        print(f"  ✅ Mapping response reconstructed successfully")
        print(f"  Reconstructed status: {reconstructed_artifact.status}")
        print(f"  Reconstructed entities: {reconstructed_mapping.total_entities_processed}")
    except Exception as e:
        print(f"  ❌ Response reconstruction failed: {e}")

def main():
    """Main demonstration function."""
    print("🚀 CanonMap Response Models Demonstration")
    print("="*60)
    
    try:
        # Setup
        print("Setting up CanonMap...")
        canonmap = setup_canonmap()
        
        # Create sample data
        print("Creating sample data...")
        data_file = create_sample_data()
        
        # Demonstrate artifact generation
        artifact_response = demonstrate_artifact_generation(canonmap, data_file)
        
        # Demonstrate entity mapping
        mapping_response = demonstrate_entity_mapping(canonmap)
        
        # Demonstrate serialization
        demonstrate_response_serialization(artifact_response, mapping_response)
        
        print("\n" + "="*60)
        print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nKey Benefits Demonstrated:")
        print("  - Comprehensive response information")
        print("  - Detailed error and warning handling")
        print("  - Processing statistics and performance metrics")
        print("  - Easy serialization and reconstruction")
        print("  - Type safety and clear API contracts")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if Path("sample_players.csv").exists():
            Path("sample_players.csv").unlink()
            print("\n🧹 Cleaned up sample data file")

if __name__ == "__main__":
    main() 