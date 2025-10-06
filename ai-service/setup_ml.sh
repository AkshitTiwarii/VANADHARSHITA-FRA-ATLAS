#!/bin/bash

echo "========================================"
echo "FRA Atlas AI Service v2.0 Setup"
echo "Production ML Models Installation"
echo "========================================"
echo

# Check if running in correct directory
if [ ! -f "requirements_ml.txt" ]; then
    echo "ERROR: Please run this script from the ai-service directory"
    exit 1
fi

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.8+"
    exit 1
fi
echo "    ✓ Python found: $(python3 --version)"

# Install dependencies
echo
echo "[2/5] Installing Python dependencies..."
pip3 install -r requirements_ml.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "    ✓ Dependencies installed successfully!"

# Download SpaCy models
echo
echo "[3/5] Downloading SpaCy NER models..."
echo "    This may take a few minutes (downloading ~500MB)..."

python3 -m spacy download en_core_web_trf
if [ $? -ne 0 ]; then
    echo "    Transformer model failed, trying smaller model..."
    python3 -m spacy download en_core_web_sm
    if [ $? -ne 0 ]; then
        echo "WARNING: SpaCy models installation failed"
        echo "You can install manually later with: python3 -m spacy download en_core_web_sm"
    fi
fi
echo "    ✓ SpaCy models installed!"

# Check Tesseract
echo
echo "[4/5] Checking Tesseract OCR..."
if ! command -v tesseract &> /dev/null; then
    echo "WARNING: Tesseract not found"
    echo
    echo "Please install Tesseract OCR:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "  Mac: brew install tesseract"
    echo
else
    echo "    ✓ Tesseract found: $(tesseract --version | head -n 1)"
fi

# Check Redis
echo
echo "[5/5] Checking Redis (optional)..."
if ! command -v redis-cli &> /dev/null; then
    echo "INFO: Redis not found (optional for batch processing)"
    echo "Service will run in in-memory mode"
    echo
    echo "To install Redis:"
    echo "  Ubuntu/Debian: sudo apt-get install redis-server"
    echo "  Mac: brew install redis"
else
    echo "    ✓ Redis found: $(redis-cli --version)"
fi

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Start the service: python3 main_v2.py"
echo "2. Or use old version: python3 main.py"
echo "3. Open API docs: http://localhost:8000/docs"
echo
echo "Read README_V2.md for detailed usage instructions"
echo
