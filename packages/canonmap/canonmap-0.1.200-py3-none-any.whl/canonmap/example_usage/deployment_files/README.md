# CanonMap Example Usage with Response Models

This directory contains comprehensive examples demonstrating how to use CanonMap with the new response models. The examples show both direct library usage and API-based usage.

## 🚀 Quick Start

### 1. Setup Configuration

```bash
# From the canonmap-2 directory
cd canonmap/example_usage

# Run the interactive setup script
./setup.sh
```

The setup script will help you configure:
- Local development mode (recommended for getting started)
- GCP integration (for production use)
- Environment variables
- Required directories

### 2. Start the FastAPI Server

```bash
# Start the server with your configuration
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### 3. Run the Examples

#### Direct Library Usage
```bash
# Run the comprehensive example with response models
python example_with_response_models.py
```

#### API Client Usage
```bash
# Run the API client example
python api_client_example.py
```

## 📁 File Structure

```
example_usage/
├── app/                          # FastAPI application
│   ├── main.py                   # Updated with response models
│   ├── context/                  # Application context
│   │   └── context_helpers/
│   │       └── get_canonmap_helper.py  # Configurable CanonMap initialization
│   └── utils/                    # Utilities
├── example_with_response_models.py  # Direct library usage example
├── api_client_example.py         # API client example
├── setup.sh                      # Interactive setup script
├── env.template                  # Environment configuration template
├── deploy_local.sh              # Deployment script
├── Dockerfile                   # Docker configuration
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

The CanonMap API uses environment variables for configuration. You can set these in a `.env` file or as system environment variables.

#### GCP Configuration
```bash
# Enable/disable GCP integration
USE_GCP=false

# GCP credentials (only used when USE_GCP=true)
GCP_PROJECT_ID=your-gcp-project-id
GCP_BUCKET_NAME=your-gcp-bucket-name
GCP_SERVICE_ACCOUNT_PATH=your-service-account.json
```

#### Artifacts Configuration
```bash
# Local storage
ARTIFACTS_LOCAL_PATH=artifacts
ARTIFACTS_GCP_PREFIX=artifacts
ARTIFACTS_SYNC_STRATEGY=refresh  # none, missing, overwrite, refresh
```

#### Embedding Configuration
```bash
# Model configuration
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L12-v2
EMBEDDING_LOCAL_PATH=models/sentence-transformers/all-MiniLM-L12-v2
EMBEDDING_GCP_PREFIX=models/sentence-transformers/all-MiniLM-L12-v2
EMBEDDING_SYNC_STRATEGY=refresh
```

#### General Configuration
```bash
# Logging and debugging
CANONMAP_VERBOSE=true
CANONMAP_TROUBLESHOOTING=false
```

### Configuration Examples

#### Local Development (Recommended for getting started)
```bash
# .env file
USE_GCP=false
CANONMAP_VERBOSE=true
CANONMAP_TROUBLESHOOTING=false
ARTIFACTS_LOCAL_PATH=artifacts
EMBEDDING_LOCAL_PATH=models/sentence-transformers/all-MiniLM-L12-v2
```

#### Production with GCP
```bash
# .env file
USE_GCP=true
GCP_PROJECT_ID=my-production-project
GCP_BUCKET_NAME=my-canonmap-artifacts
GCP_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
CANONMAP_VERBOSE=false
CANONMAP_TROUBLESHOOTING=false
```

### Helper Functions

The `get_canonmap_helper.py` provides several helper functions:

```python
from app.context.context_helpers.get_canonmap_helper import (
    get_canonmap,
    get_canonmap_local_only,
    get_canonmap_with_gcp,
    print_configuration_help
)

# Use environment variables
canonmap = get_canonmap()

# Force local-only mode
canonmap = get_canonmap_local_only()

# Configure with specific GCP settings
canonmap = get_canonmap_with_gcp(
    project_id="my-project",
    bucket_name="my-bucket", 
    service_account_path="sa.json"
)

# Print configuration help
print_configuration_help()
```

## 🔧 Response Models Overview

### ArtifactGenerationResponse

Comprehensive response for artifact generation operations:

```python
from canonmap import ArtifactGenerationResponse

response = canonmap.generate_artifacts(request)

# Access response information
print(f"Status: {response.status}")
print(f"Generated artifacts: {len(response.generated_artifacts)}")
print(f"Processing time: {response.processing_stats.processing_time_seconds:.2f}s")

# Handle errors and warnings
if response.errors:
    for error in response.errors:
        print(f"Error: {error.error_type} - {error.error_message}")

if response.warnings:
    for warning in response.warnings:
        print(f"Warning: {warning}")
```

**Key Features:**
- ✅ Generated artifacts with metadata
- ✅ Processing statistics and performance metrics
- ✅ Detailed error and warning information
- ✅ GCP upload details (if applicable)
- ✅ Convenience paths for common artifacts
- ✅ JSON serialization support

### EntityMappingResponse

Comprehensive response for entity mapping operations:

```python
from canonmap import EntityMappingResponse

response = canonmap.map_entities(request)

# Access response information
print(f"Total entities processed: {response.total_entities_processed}")
print(f"Total matches found: {response.total_matches_found}")
print(f"Processing time: {response.processing_time_seconds:.3f}s")

# Process detailed results
for result in response.results:
    print(f"Entity: {result.query}")
    if result.best_match:
        print(f"  Best match: {result.best_match.entity} (score: {result.best_match.score:.3f})")
    
    for match in result.matches[:3]:  # Top 3 matches
        print(f"  - {match.entity} (score: {match.score:.3f})")
```

**Key Features:**
- ✅ Detailed mapping results with scores
- ✅ Processing statistics and performance metrics
- ✅ Configuration summary
- ✅ Error and warning information
- ✅ JSON serialization support

## 🛠️ API Endpoints

### Generate Artifacts

**Endpoint:** `POST /generate-artifacts`

**Request:**
```json
{
  "input_path": "data.csv",
  "source_name": "my_source",
  "table_name": "my_table",
  "entity_fields": [
    {"table_name": "my_table", "field_name": "name"},
    {"table_name": "my_table", "field_name": "company"}
  ],
  "semantic_fields": [
    {"table_name": "my_table", "field_name": "description"}
  ],
  "generate_schema": true,
  "generate_canonical_entities": true,
  "generate_embeddings": true,
  "generate_semantic_texts": true,
  "save_processed_data": true,
  "clean_field_names": true
}
```

**Response:** `ArtifactGenerationResponse`

### Entity Mapping

**Endpoint:** `POST /entity-mapping`

**Request:**
```json
{
  "entities": ["Entity 1", "Entity 2", "Entity 3"],
  "filters": [
    {
      "table_name": "my_table",
      "table_fields": ["name", "company"]
    }
  ],
  "num_results": 5,
  "weights": {
    "semantic": 0.40,
    "fuzzy": 0.40,
    "initial": 0.10,
    "keyword": 0.05,
    "phonetic": 0.05
  },
  "use_semantic_search": true,
  "threshold": 0.0
}
```

**Response:** `EntityMappingResponse`

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "CanonMap API",
  "version": "1.0.0"
}
```

## 📊 Example Output

### Artifact Generation Response

```
📦 Calling Generate Artifacts API...
  Request payload:
    - Source: electronics
    - Table: products
    - Entity fields: 2
    - Semantic fields: 2
  ✅ API call successful

📊 Artifact Generation Response Analysis:
  Status: success
  Message: Artifacts generated successfully
  Source: electronics
  Tables: ['products']
  Generated artifacts: 6
    - schema: artifacts/electronics_schema.pkl
      Size: 2048 bytes
    - canonical_entities: artifacts/electronics_canonical_entities.pkl
      Size: 4096 bytes
    - embeddings: artifacts/electronics_canonical_entity_embeddings.npz
      Size: 8192 bytes
  Processing Statistics:
    - Tables: 1
    - Rows: 4
    - Entities: 8
    - Embeddings: 8
    - Time: 2.34s
```

### Entity Mapping Response

```
🔍 Calling Entity Mapping API...
  Request payload:
    - Entities: 6
    - Number of results: 3
    - Use semantic search: true
  ✅ API call successful

📊 Entity Mapping Response Analysis:
  Status: success
  Message: Entity mapping completed successfully
  Total entities processed: 6
  Total matches found: 18
  Processing time: 0.156s
  Average time per entity: 26.0ms
  Detailed Results (6 entities):
    Entity 1: 'iPhone 14 Pro'
      Total matches: 3
      Best match: 'iPhone 14 Pro' (score: 1.000)
        Passes: 5
        Field: product_name
        Table: products
      Match 1: 'iPhone 14 Pro' (score: 1.000)
      Match 2: 'iPhone 14 Pro Max' (score: 0.850)
```

## 🔍 Error Handling

The response models include comprehensive error handling:

```python
# Check for errors
if response.errors:
    for error in response.errors:
        print(f"Error: {error.error_type}")
        print(f"  Message: {error.error_message}")
        print(f"  Table: {error.table_name}")
        print(f"  Field: {error.field_name}")
        if error.row_index is not None:
            print(f"  Row: {error.row_index}")

# Check for warnings
if response.warnings:
    for warning in response.warnings:
        print(f"Warning: {warning}")
```

## 🚀 Advanced Usage

### Serialization and Deserialization

```python
# Convert to dictionary
response_dict = response.to_dict()

# Convert to JSON
import json
response_json = json.dumps(response_dict, indent=2)

# Reconstruct from dictionary
reconstructed_response = ArtifactGenerationResponse.from_dict(response_dict)
```

### Performance Monitoring

```python
# Access processing statistics
stats = response.processing_stats
print(f"Processing time: {stats.processing_time_seconds:.2f}s")
print(f"Start time: {stats.start_time}")
print(f"End time: {stats.end_time}")
print(f"Tables processed: {stats.total_tables_processed}")
print(f"Rows processed: {stats.total_rows_processed}")
```

### Convenience Paths

```python
# Easy access to common artifacts
if response.schema_path:
    print(f"Schema: {response.schema_path}")

if response.canonical_entities_path:
    print(f"Canonical entities: {response.canonical_entities_path}")

if response.canonical_entity_embeddings_path:
    print(f"Embeddings: {response.canonical_entity_embeddings_path}")
```

## 🐳 Docker Deployment

```bash
# Build the Docker image
docker build -t canonmap-api .

# Run the container
docker run -p 8000:8000 canonmap-api
```

## 📝 Configuration

The examples use the following configuration:

- **Local artifacts path:** `./artifacts`
- **Embedding model:** `sentence-transformers/all-MiniLM-L12-v2`
- **API port:** `8000`
- **CORS:** Enabled for all origins

## 🔧 Troubleshooting

### Common Issues

1. **API not available:**
   ```bash
   # Make sure the server is running
   python -m uvicorn app.main:app --reload
   ```

2. **Missing dependencies:**
   ```bash
   # Install required packages
   pip install fastapi uvicorn requests pandas python-dotenv
   ```

3. **Configuration issues:**
   ```bash
   # Run the setup script
   ./setup.sh
   
   # Or check configuration help
   python -c "from app.context.context_helpers.get_canonmap_helper import print_configuration_help; print_configuration_help()"
   ```

4. **Model download issues:**
   ```bash
   # The embedding model will be downloaded automatically
   # Check the models/ directory for downloaded files
   ```

### Logging

The examples include comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 📚 Additional Resources

- [CanonMap Documentation](../README.md)
- [Response Models Implementation](../../RESPONSE_MODELS_IMPLEMENTATION.md)
- [Filtered Schemas Implementation](../../FILTERED_SCHEMAS_IMPLEMENTATION.md)

## 🤝 Contributing

When adding new examples:

1. Follow the existing code structure
2. Include comprehensive error handling
3. Add proper documentation
4. Test with the new response models
5. Update this README if needed 