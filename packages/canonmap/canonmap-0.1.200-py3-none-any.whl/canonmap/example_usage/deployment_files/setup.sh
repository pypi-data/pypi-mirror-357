#!/bin/bash

# CanonMap API Setup Script
# This script helps you set up the CanonMap API with proper configuration

set -e

echo "🚀 CanonMap API Setup"
echo "===================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
    echo "   Current configuration:"
    grep -E "^(USE_GCP|GCP_PROJECT_ID|GCP_BUCKET_NAME|CANONMAP_VERBOSE)" .env || echo "   No GCP configuration found"
    echo ""
    read -p "Do you want to reconfigure? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Using existing configuration."
        exit 0
    fi
fi

# Copy template if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created"
    echo ""
fi

# Configuration options
echo "🔧 Configuration Options:"
echo "1. Local development (no GCP) - Recommended for getting started"
echo "2. With GCP integration"
echo "3. View current configuration"
echo "4. Exit"
echo ""

read -p "Choose an option (1-4): " -n 1 -r
echo ""

case $REPLY in
    1)
        echo "🔧 Configuring for local development..."
        sed -i.bak 's/USE_GCP=.*/USE_GCP=false/' .env
        sed -i.bak 's/CANONMAP_VERBOSE=.*/CANONMAP_VERBOSE=true/' .env
        sed -i.bak 's/CANONMAP_TROUBLESHOOTING=.*/CANONMAP_TROUBLESHOOTING=false/' .env
        rm -f .env.bak
        echo "✅ Configured for local development"
        echo ""
        echo "📋 Configuration summary:"
        echo "   - GCP integration: Disabled"
        echo "   - Verbose logging: Enabled"
        echo "   - Troubleshooting: Disabled"
        echo "   - Artifacts will be stored locally in 'artifacts/' directory"
        echo "   - Embedding model will be downloaded to 'models/' directory"
        ;;
    2)
        echo "🔧 Configuring for GCP integration..."
        echo ""
        read -p "Enter your GCP Project ID: " gcp_project_id
        read -p "Enter your GCP Bucket Name: " gcp_bucket_name
        read -p "Enter path to your service account JSON file: " service_account_path
        
        # Validate service account file
        if [ ! -f "$service_account_path" ]; then
            echo "❌ Service account file not found: $service_account_path"
            echo "Please provide a valid path to your service account JSON file."
            exit 1
        fi
        
        # Update .env file
        sed -i.bak "s/USE_GCP=.*/USE_GCP=true/" .env
        sed -i.bak "s/GCP_PROJECT_ID=.*/GCP_PROJECT_ID=$gcp_project_id/" .env
        sed -i.bak "s/GCP_BUCKET_NAME=.*/GCP_BUCKET_NAME=$gcp_bucket_name/" .env
        sed -i.bak "s|GCP_SERVICE_ACCOUNT_PATH=.*|GCP_SERVICE_ACCOUNT_PATH=$service_account_path|" .env
        sed -i.bak 's/CANONMAP_VERBOSE=.*/CANONMAP_VERBOSE=true/' .env
        sed -i.bak 's/CANONMAP_TROUBLESHOOTING=.*/CANONMAP_TROUBLESHOOTING=true/' .env
        rm -f .env.bak
        
        echo "✅ Configured for GCP integration"
        echo ""
        echo "📋 Configuration summary:"
        echo "   - GCP integration: Enabled"
        echo "   - Project ID: $gcp_project_id"
        echo "   - Bucket: $gcp_bucket_name"
        echo "   - Service account: $service_account_path"
        echo "   - Verbose logging: Enabled"
        echo "   - Troubleshooting: Enabled"
        ;;
    3)
        echo "📋 Current Configuration:"
        echo ""
        if [ -f ".env" ]; then
            cat .env
        else
            echo "No .env file found. Run setup again to create one."
        fi
        ;;
    4)
        echo "Setup cancelled."
        exit 0
        ;;
    *)
        echo "❌ Invalid option. Please choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "🔧 Next Steps:"
echo ""

# Check if required directories exist
if [ ! -d "artifacts" ]; then
    echo "📁 Creating artifacts directory..."
    mkdir -p artifacts
    echo "✅ Created artifacts directory"
fi

if [ ! -d "models" ]; then
    echo "📁 Creating models directory..."
    mkdir -p models
    echo "✅ Created models directory"
fi

echo ""
echo "🚀 Ready to start the API server!"
echo ""
echo "To start the server:"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "To test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "To view API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "📚 Additional resources:"
echo "   - README.md: Detailed usage instructions"
echo "   - example_with_response_models.py: Direct library usage example"
echo "   - api_client_example.py: API client example"
echo ""
echo "✅ Setup completed successfully!" 