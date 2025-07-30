#!/bin/bash

# Production Configuration Demo Runner
# This script helps you test different configuration scenarios

echo "🎯 Production Configuration Demo Runner"
echo "====================================="
echo ""

# Function to run demo with specific environment
run_demo() {
    local env=$1
    echo "🚀 Running in $env mode..."
    echo ""
    ENVIRONMENT=$env python main.py
}

# Check command line argument
case "$1" in
    "dev")
        run_demo "dev"
        ;;
    "prod")
        run_demo "prod"
        ;;
    "override")
        echo "🔧 Testing environment variable overrides..."
        echo "  Setting: APP_DATABASE__HOST=custom.example.com"
        echo "  Setting: APP_REDIS__PORT=7000"
        echo "  Setting: APP_LOGGER__LEVEL=ERROR"
        echo ""
        APP_DATABASE__HOST=custom.example.com \
        APP_REDIS__PORT=7000 \
        APP_LOGGER__LEVEL=ERROR \
        python main.py
        ;;
    "validate")
        echo "✅ Validating production configuration..."
        echo ""
        ENVIRONMENT=prod python -c "
from settings import AppSettings
try:
    settings = AppSettings()
    settings.validate_production_config()
    print('✅ Production configuration is valid!')
except Exception as e:
    print(f'❌ Validation failed: {e}')
"
        ;;
    *)
        echo "Usage: $0 [dev|prod|override|validate]"
        echo ""
        echo "Options:"
        echo "  dev       - Run with development configuration"
        echo "  prod      - Run with production configuration"
        echo "  override  - Demo environment variable overrides"
        echo "  validate  - Validate production configuration"
        echo ""
        echo "Examples:"
        echo "  $0 dev"
        echo "  $0 prod"
        echo "  $0 override"
        echo ""
        exit 1
        ;;
esac