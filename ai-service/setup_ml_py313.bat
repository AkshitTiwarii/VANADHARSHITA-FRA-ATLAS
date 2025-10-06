@echo off
echo ========================================
echo FRA Atlas AI Service v2.0 Setup
echo Python 3.13 Compatible Version
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo     Python found!
echo.

echo [2/5] Upgrading pip...
python -m pip install --upgrade pip --user
echo.

echo [3/5] Installing Python dependencies...
python -m pip install -r requirements_ml_py313.txt --user
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo     Dependencies installed successfully!
echo.

echo [4/5] Downloading SpaCy language model...
echo     This will download ~40MB for the small English model
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo WARNING: Failed to download SpaCy model automatically
    echo You can download it manually later with: python -m spacy download en_core_web_sm
)
echo.

echo [5/5] Checking Tesseract OCR...
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Tesseract OCR not found!
    echo.
    echo Tesseract is required for OCR functionality.
    echo Please install from: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo Windows installer: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
    echo.
    echo After installation, add Tesseract to your system PATH
    echo Default path: C:\Program Files\Tesseract-OCR
) else (
    echo     Tesseract found!
    tesseract --version
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. If Tesseract warning shown above, install it from:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 2. (Optional) For better accuracy, install larger SpaCy model:
echo    python -m spacy download en_core_web_md
echo.
echo 3. Start the service:
echo    python main_v2.py
echo.
echo 4. Test the service:
echo    python test_service_v2.py
echo.
echo NOTE: EasyOCR is disabled for Python 3.13 compatibility.
echo       Service will use Tesseract OCR (works great!).
echo.
pause
