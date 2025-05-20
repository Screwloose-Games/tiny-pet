# gltf-renderer/Dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  libgl1-mesa-dri \
  xvfb \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev \
  && rm -rf /var/lib/apt/lists/*

# Set up a virtual display
ENV DISPLAY=:99

# Install Python dependencies
RUN pip install --no-cache-dir \
  numpy \
  pygltflib \
  trimesh \
  pyrender \
  pillow \
  pyyaml

# Create app directory
WORKDIR /app

# Copy the render script and any local modules
COPY validate_gltf.py .
COPY spec_image_tools.py .

# Set the entrypoint
ENTRYPOINT ["python", "validate_gltf.py"]