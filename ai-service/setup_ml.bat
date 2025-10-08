@echo off
echo ========================================
echo FRA Atlas AI Service v2.0 Setup
echo Production ML Models Installation
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo     Python found!

echo.
echo [2/5] Installing Python dependencies...
pip install -r requirements_ml.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo     Dependencies installed successfully!

echo.
echo [3/5] Downloading SpaCy NER models...
echo     This may take a few minutes (downloading ~500MB)...

python -m spacy download en_core_web_trf
if errorlevel 1 (
    echo     Transformer model failed, trying smaller model...
    python -m spacy download en_core_web_sm
    if errorlevel 1 (
        echo WARNING: SpaCy models installation failed
        echo You can install manually later with: python -m spacy download en_core_web_sm
    )
)
echo     SpaCy models installed!

echo.
echo [4/5] Checking Tesseract OCR...
where tesseract >nul 2>&1
if errorlevel 1 (
    echo WARNING: Tesseract not found in PATH
    echo.
    echo Please install Tesseract OCR:
    echo 1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. Install to: C:\Program Files\Tesseract-OCR
    echo 3. Add to PATH or configure in code
    echo.
) else (
    echo     Tesseract found!
)

echo.
echo [5/5] Checking Redis (optional)...
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo INFO: Redis not found (optional for batch processing)
    echo Service will run in in-memory mode
    echo.
    echo To install Redis:
    echo 1. Download from: https://github.com/microsoftarchive/redis/releases
    echo 2. Or use: choco install redis-64
) else (
    echo     Redis found!
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the service: python main_v2.py
echo 2. Or use old version: python main.py
echo 3. Open API docs: http://localhost:8000/docs
echo.
echo Read README_V2.md for detailed usage instructions
echo.
pause
