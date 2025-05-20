#!/bin/bash

# Exit on error
set -e

# Create output directory
mkdir -p validation_output

# Build the Docker image
echo "Building Docker image..."
docker build -t gltf-validator .

# Get all GLTF files from the current directory and subdirectories
echo "Finding GLTF files..."
find . -type f \( -name "*.gltf" -o -name "*.glb" \) > gltf_files.txt

# Run the validator for each GLTF file
echo "Running validator..."
while IFS= read -r gltf_file; do
    echo "Processing $gltf_file..."
    # Create a directory for this file's output
    file_output_dir="validation_output/$(basename "$gltf_file" .gltf)"
    mkdir -p "$file_output_dir"
    
    # Run the validator with absolute paths
    docker run --rm \
        -v "$PWD:/workspace" \
        -w /workspace \
        gltf-validator "/workspace/validation_output" "/workspace/$gltf_file"
done < gltf_files.txt

echo "Validation complete! Results are in the validation_output directory"
echo "You can find the GitHub comment content in validation_output/github_comment.md" 