#!/bin/bash
set -e

# Start Xvfb in the background
Xvfb :99 &

# Run the validator with all arguments passed to the container
exec python /app/validate_gltf.py "$@"
