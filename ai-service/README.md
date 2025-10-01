# FRA Atlas AI Service Setup Guide

## 🤖 AI Service Overview

The AI service provides OCR (Optical Character Recognition) and document processing capabilities for automatically extracting information from forest rights documents.

## 📋 Prerequisites

### Python Requirements
- Python 3.8+ installed
- pip package manager

### System Requirements  
- **Windows**: Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-hin`
- **macOS**: `brew install tesseract tesseract-lang`

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
cd ai-service
pip install -r requirements.txt
```

### 2. Configure Tesseract (Windows only)
Edit `main.py` and uncomment/adjust this line:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### 3. Start the Service
```bash
python main.py
```

The service will start on **http://localhost:8000**

## ✅ Test the Service

### Method 1: Web Browser
- Open http://localhost:8000
- You should see: `{"message": "FRA Atlas AI Service", "status": "running"}`

### Method 2: Test Script
```bash
python test_ai_service.py
```

### Method 3: Health Check
```bash
curl http://localhost:8000/health
```

## 📄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/health` | GET | Health check |
| `/api/process-document` | POST | OCR document processing |
| `/api/analyze-satellite` | POST | Satellite imagery analysis |
| `/api/stats` | GET | Service statistics |

## 🔧 Troubleshooting

### Issue: "Tesseract not found"
**Solution**: Install Tesseract OCR and configure the path in `main.py`

### Issue: "AI Service Offline" in frontend
**Solutions**:
1. Check if service is running: `http://localhost:8000/health`
2. Verify port 8000 is not blocked by firewall
3. Check console for error messages

### Issue: Poor OCR accuracy
**Solutions**:
1. Ensure document images are clear and high resolution
2. Use good lighting when taking photos
3. Crop documents to remove unnecessary background

### Issue: "Failed to process document"
**Solutions**:
1. Check file format (supported: JPG, PNG, TIFF, BMP)
2. Ensure file size is under 10MB
3. Verify image contains readable text

## 📊 Supported Features

### ✅ Document Processing
- Extracts holder name, father name, village, district
- Detects area claimed and survey numbers
- Multi-language support (English + Hindi)
- Confidence scoring for extraction quality

### ✅ Image Preprocessing
- Noise reduction and enhancement
- Binary thresholding for better OCR
- Morphological operations for cleanup

### ✅ Smart Validation
- Entity validation and cleanup
- Quality assessment of extracted data
- Auto-correction of common OCR errors

## 🎯 Usage in Frontend

1. Click **"OCR Scan"** button in Case Management
2. Upload document image or use camera
3. Click **"Process with AI"** 
4. Review extracted data and confidence score
5. Form fields auto-fill with extracted information

## 🔒 Security Notes

- Service runs on localhost only by default
- Uploaded files are automatically deleted after processing
- No data is stored permanently on the AI service
- All processing happens locally on your machine

## 🌟 Performance Tips

### For Better Results:
- Use high-resolution images (300 DPI minimum)
- Ensure good contrast between text and background
- Crop documents to focus on relevant text areas
- Use proper lighting when photographing documents

### For Faster Processing:
- Keep image file sizes reasonable (1-5MB)
- Close other resource-intensive applications
- Use SSD storage for faster file I/O

## 📈 Monitoring

Check service statistics:
```bash
curl http://localhost:8000/api/stats
```

Monitor logs in the console where you started the service.

---

**🎉 Your AI service is now ready to process forest rights documents!**