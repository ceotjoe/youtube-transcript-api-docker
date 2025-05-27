#!/bin/bash

# Define the image name
IMAGE_NAME="youtube-transcript-api-service"

echo "Building Docker image: $IMAGE_NAME..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "Docker image built successfully."
    echo "Stopping existing container (if any)..."
    docker-compose down
    
    echo "Starting Docker container: $IMAGE_NAME..."
    docker-compose up -d

    if [ $? -eq 0 ]; then
        echo "API service is running. Access it at http://localhost:8000"
        echo "Swagger UI (interactive docs): http://localhost:8000/docs"
        echo "ReDoc UI: http://localhost:8000/redoc"
        echo ""
        echo "--- API Keys ---"
        echo "For this PoC, hardcoded keys are: my-secret-api-key-123, another-secret-key-456"
        echo "In production, use environment variables."
        echo "----------------"
        echo ""
        echo "To test (example video ID: dQw4w9WgXcQ):"
        echo "  1. Using Header (Recommended for production):"
        echo "     curl -H \"X-API-Key: my-secret-api-key-123\" http://localhost:8000/transcript/dQw4w9WgXcQ"
        echo ""
        echo "  2. Using Query Parameter (Less secure, for quick testing):"
        echo "     http://localhost:8000/transcript/dQw4w9WgXcQ?api_key=my-secret-api-key-123"
        echo ""
        echo "  3. Attempting without API Key (will fail):"
        echo "     http://localhost:8000/transcript/dQw4w9WgXcQ"
        echo ""
        echo "To stop the service later, run: docker-compose down"
    else
        echo "Failed to start Docker container."
        exit 1
    fi
else
    echo "Docker image build failed."
    exit 1
fi
