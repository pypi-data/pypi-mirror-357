#!/usr/bin/env python3
"""
API Client Example for CanonMap with Response Models

This script demonstrates how to:
1. Make API calls to the CanonMap FastAPI server
2. Handle the new response models
3. Process detailed response information
4. Handle errors and warnings
"""

import requests
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

# API Configuration
API_BASE_URL = "http://localhost:8000"
GENERATE_ARTIFACTS_ENDPOINT = f"{API_BASE_URL}/generate-artifacts"
ENTITY_MAPPING_ENDPOINT = f"{API_BASE_URL}/entity-mapping"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

def check_api_health() -> bool:
    """Check if the API is running and healthy."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Health Check: {health_data}")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Health Check Error: {e}")
        return False

def create_sample_data() -> str:
    """Create sample data for the API demonstration."""
    data = {
        'product_name': ['iPhone 14 Pro', 'Samsung Galaxy S23', 'Google Pixel 7', 'OnePlus 11'],
        'brand': ['Apple', 'Samsung', 'Google', 'OnePlus'],
        'category': ['Smartphone', 'Smartphone', 'Smartphone', 'Smartphone'],
        'description': [
            'Premium smartphone with advanced camera system and A16 Bionic chip',
            'Flagship Android device with S Pen support and powerful performance',
            'Pure Android experience with exceptional camera capabilities',
            'Fast performance with 100W charging and Hasselblad cameras'
        ],
        'specifications': [
            '6.1" display, A16 Bionic, 48MP camera, iOS 16',
            '6.8" display, Snapdragon 8 Gen 2, 200MP camera, Android 13',
            '6.3" display, Google Tensor G2, 50MP camera, Android 13',
            '6.7" display, Snapdragon 8 Gen 2, 50MP camera, Android 13'
        ],
        'price': [999, 1199, 599, 699],
        'rating': [4.8, 4.6, 4.7, 4.5]
    }
    
    df = pd.DataFrame(data)
    file_path = "sample_products.csv"
    df.to_csv(file_path, index=False)
    return file_path

def call_generate_artifacts(data_file: str) -> Optional[Dict[str, Any]]:
    """Call the generate-artifacts endpoint."""
    print(f"\n📦 Calling Generate Artifacts API...")
    
    # Prepare request payload
    request_data = {
        "input_path": data_file,
        "source_name": "electronics",
        "table_name": "products",
        "entity_fields": [
            {"table_name": "products", "field_name": "product_name"},
            {"table_name": "products", "field_name": "brand"}
        ],
        "semantic_fields": [
            {"table_name": "products", "field_name": "description"},
            {"table_name": "products", "field_name": "specifications"}
        ],
        "generate_schema": True,
        "generate_canonical_entities": True,
        "generate_embeddings": True,
        "generate_semantic_texts": True,
        "save_processed_data": True,
        "clean_field_names": True
    }
    
    try:
        print(f"  Request payload:")
        print(f"    - Source: {request_data['source_name']}")
        print(f"    - Table: {request_data['table_name']}")
        print(f"    - Entity fields: {len(request_data['entity_fields'])}")
        print(f"    - Semantic fields: {len(request_data['semantic_fields'])}")
        
        # Make API call
        response = requests.post(
            GENERATE_ARTIFACTS_ENDPOINT,
            json=request_data,
            timeout=60  # Longer timeout for artifact generation
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ API call successful")
            return result
        else:
            print(f"  ❌ API call failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API call error: {e}")
        return None

def call_entity_mapping(entities: list) -> Optional[Dict[str, Any]]:
    """Call the entity-mapping endpoint."""
    print(f"\n🔍 Calling Entity Mapping API...")
    
    # Prepare request payload
    request_data = {
        "entities": entities,
        "filters": [
            {
                "table_name": "products",
                "table_fields": ["product_name", "brand"]
            }
        ],
        "num_results": 3,
        "weights": {
            "semantic": 0.40,
            "fuzzy": 0.40,
            "initial": 0.10,
            "keyword": 0.05,
            "phonetic": 0.05
        },
        "use_semantic_search": True,
        "threshold": 0.0
    }
    
    try:
        print(f"  Request payload:")
        print(f"    - Entities: {len(request_data['entities'])}")
        print(f"    - Number of results: {request_data['num_results']}")
        print(f"    - Use semantic search: {request_data['use_semantic_search']}")
        
        # Make API call
        response = requests.post(
            ENTITY_MAPPING_ENDPOINT,
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ API call successful")
            return result
        else:
            print(f"  ❌ API call failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API call error: {e}")
        return None

def analyze_artifact_response(response_data: Dict[str, Any]):
    """Analyze the artifact generation response."""
    print(f"\n📊 Artifact Generation Response Analysis:")
    print(f"  Status: {response_data.get('status', 'unknown')}")
    print(f"  Message: {response_data.get('message', 'No message')}")
    print(f"  Source: {response_data.get('source_name', 'unknown')}")
    print(f"  Tables: {response_data.get('table_names', [])}")
    
    # Generated artifacts
    artifacts = response_data.get('generated_artifacts', [])
    print(f"  Generated artifacts: {len(artifacts)}")
    for artifact in artifacts:
        print(f"    - {artifact.get('artifact_type', 'unknown')}: {artifact.get('file_path', 'unknown')}")
        if artifact.get('file_size_bytes'):
            print(f"      Size: {artifact['file_size_bytes']} bytes")
    
    # Processing statistics
    stats = response_data.get('processing_stats')
    if stats:
        print(f"  Processing Statistics:")
        print(f"    - Tables: {stats.get('total_tables_processed', 0)}")
        print(f"    - Rows: {stats.get('total_rows_processed', 0)}")
        print(f"    - Entities: {stats.get('total_entities_generated', 0)}")
        print(f"    - Embeddings: {stats.get('total_embeddings_generated', 0)}")
        print(f"    - Time: {stats.get('processing_time_seconds', 0):.2f}s")
    
    # Errors and warnings
    errors = response_data.get('errors', [])
    warnings = response_data.get('warnings', [])
    
    if errors:
        print(f"  Errors ({len(errors)}):")
        for error in errors:
            print(f"    - {error.get('error_type', 'unknown')}: {error.get('error_message', 'No message')}")
    
    if warnings:
        print(f"  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"    - {warning}")
    
    # Convenience paths
    print(f"  Convenience Paths:")
    for path_key in ['schema_path', 'entity_fields_schema_path', 'semantic_fields_schema_path', 
                     'canonical_entities_path', 'canonical_entity_embeddings_path', 'semantic_texts_path']:
        path_value = response_data.get(path_key)
        if path_value:
            print(f"    - {path_key}: {path_value}")

def analyze_mapping_response(response_data: Dict[str, Any]):
    """Analyze the entity mapping response."""
    print(f"\n📊 Entity Mapping Response Analysis:")
    print(f"  Status: {response_data.get('status', 'unknown')}")
    print(f"  Message: {response_data.get('message', 'No message')}")
    print(f"  Total entities processed: {response_data.get('total_entities_processed', 0)}")
    print(f"  Total matches found: {response_data.get('total_matches_found', 0)}")
    print(f"  Processing time: {response_data.get('processing_time_seconds', 0):.3f}s")
    print(f"  Average time per entity: {response_data.get('average_processing_time_ms', 0):.1f}ms")
    
    # Configuration summary
    print(f"  Configuration Summary:")
    print(f"    - Results requested: {response_data.get('num_results_requested', 0)}")
    print(f"    - Threshold used: {response_data.get('threshold_used', 0)}")
    print(f"    - Weights used: {response_data.get('weights_used', {})}")
    print(f"    - Semantic search used: {response_data.get('use_semantic_search', False)}")
    
    # Detailed results
    results = response_data.get('results', [])
    print(f"  Detailed Results ({len(results)} entities):")
    
    for i, result in enumerate(results):
        query = result.get('query', 'unknown')
        matches = result.get('matches', [])
        best_match = result.get('best_match')
        
        print(f"    Entity {i+1}: '{query}'")
        print(f"      Total matches: {len(matches)}")
        
        if best_match:
            print(f"      Best match: '{best_match.get('entity', 'unknown')}' (score: {best_match.get('score', 0):.3f})")
            print(f"        Passes: {best_match.get('passes', 0)}")
            print(f"        Field: {best_match.get('field_name', 'unknown')}")
            print(f"        Table: {best_match.get('table_name', 'unknown')}")
        
        # Show top 2 matches
        for j, match in enumerate(matches[:2]):
            print(f"      Match {j+1}: '{match.get('entity', 'unknown')}' (score: {match.get('score', 0):.3f})")
    
    # Errors and warnings
    errors = response_data.get('errors', [])
    warnings = response_data.get('warnings', [])
    
    if errors:
        print(f"  Errors ({len(errors)}):")
        for error in errors:
            print(f"    - {error.get('error_type', 'unknown')}: {error.get('error_message', 'No message')}")
    
    if warnings:
        print(f"  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"    - {warning}")

def demonstrate_error_handling():
    """Demonstrate error handling with invalid requests."""
    print(f"\n⚠️  Error Handling Demonstration:")
    
    # Test with invalid entity mapping request (no entities)
    print(f"  Testing invalid entity mapping request...")
    invalid_request = {
        "entities": [],  # Empty list should cause an error
        "num_results": 5
    }
    
    try:
        response = requests.post(
            ENTITY_MAPPING_ENDPOINT,
            json=invalid_request,
            timeout=10
        )
        
        if response.status_code == 422:  # Validation error
            print(f"    ✅ Properly handled validation error: {response.status_code}")
        else:
            print(f"    ⚠️  Unexpected response: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Request error: {e}")

def main():
    """Main demonstration function."""
    print("🚀 CanonMap API Client with Response Models")
    print("="*60)
    
    # Check API health
    if not check_api_health():
        print("❌ API is not available. Please start the FastAPI server first.")
        print("   Run: cd canonmap/example_usage && python -m uvicorn app.main:app --reload")
        return
    
    try:
        # Create sample data
        print("\n📁 Creating sample data...")
        data_file = create_sample_data()
        
        # Generate artifacts
        artifact_response = call_generate_artifacts(data_file)
        if artifact_response:
            analyze_artifact_response(artifact_response)
        
        # Map entities
        entities_to_map = [
            "iPhone 14 Pro",
            "Samsung Galaxy S23", 
            "Google Pixel 7",
            "OnePlus 11",
            "iPhone 15",  # This might not match exactly
            "Samsung S24"  # This might not match exactly
        ]
        
        mapping_response = call_entity_mapping(entities_to_map)
        if mapping_response:
            analyze_mapping_response(mapping_response)
        
        # Demonstrate error handling
        demonstrate_error_handling()
        
        print(f"\n" + "="*60)
        print("✅ API Client Demonstration Completed Successfully")
        print("="*60)
        print(f"\nKey Benefits Demonstrated:")
        print(f"  - Comprehensive API responses with detailed information")
        print(f"  - Proper error handling and validation")
        print(f"  - Processing statistics and performance metrics")
        print(f"  - Easy JSON serialization for API communication")
        print(f"  - Type-safe response handling")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if Path("sample_products.csv").exists():
            Path("sample_products.csv").unlink()
            print(f"\n🧹 Cleaned up sample data file")

if __name__ == "__main__":
    main() 