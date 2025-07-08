#!/bin/bash

# Script to install graph-tool for exact research feature calculations
# This is optional - the system will fallback to BlockCypher API if graph-tool is not available

echo "Installing graph-tool for exact research feature calculations..."

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS. Installing graph-tool via conda..."
    
    # Check if conda is available
    if command -v conda &> /dev/null; then
        echo "Conda found. Installing graph-tool..."
        conda install -c conda-forge graph-tool -y
    else
        echo "Conda not found. Please install Anaconda or Miniconda first:"
        echo "https://docs.conda.io/en/latest/miniconda.html"
        echo ""
        echo "Then run: conda install -c conda-forge graph-tool"
        exit 1
    fi
else
    echo "For other operating systems, please install graph-tool manually:"
    echo "https://graph-tool.skewed.de/download"
    echo ""
    echo "Or use conda: conda install -c conda-forge graph-tool"
fi

echo ""
echo "Graph-tool installation complete!"
echo "The system will now use exact research calculations when available."
echo "If graph-tool is not available, it will fallback to BlockCypher API." 