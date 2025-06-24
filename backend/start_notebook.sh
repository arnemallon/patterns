#!/bin/bash

# Navigate to the backend directory
cd "$(dirname "$0")"

# Activate the notebook virtual environment
source notebook_venv/bin/activate

# Start Jupyter notebook
echo "Starting Jupyter notebook with TensorFlow 2.13 environment..."
echo "Available kernels:"
jupyter kernelspec list

echo ""
echo "Starting Jupyter notebook..."
jupyter notebook 