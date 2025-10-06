# 🔧 Tesseract OCR Installation Guide

## Current Status: ✅ WORKING (Mock Mode)

The OCR feature is **currently working in MOCK MODE**, which means:
- ✅ Camera captures documents
- ✅ Form auto-fills with realistic demo data
- ✅ You can test the full workflow
- ⚠️ Not extracting real text yet (needs Tesseract)

---

## 📥 Installing Tesseract (Optional - For Real OCR)

### Windows Installation:

#### Step 1: Download Tesseract
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: **tesseract-ocr-w64-setup-5.3.3.exe** (or latest version)
3. File size: ~40 MB

#### Step 2: Run Installer
1. Double-click the downloaded `.exe` file
2. Click "Next" through the welcome screens
3. **Important**: Choose installation directory:
   ```
   C:\Program Files\Tesseract-OCR
   ```

#### Step 3: Select Components
During installation, make sure to install:
- ✅ **Tesseract Core** (required)
- ✅ **English Language Data** (required)
- ✅ **Hindi Language Data** (recommended for Indian documents)
- ✅ **Additional Language Data** (optional)

#### Step 4: Add to PATH
- ✅ Check the box: **"Add Tesseract to PATH"**
- This allows the AI service to find Tesseract automatically

#### Step 5: Complete Installation
1. Click "Install"
2. Wait for installation to complete
3. Click "Finish"

---

## ✅ Verify Installation

### Test 1: Check Version
Open PowerShell and run:
```powershell
tesseract --version
```

Expected output:
```
tesseract 5.3.3
 leptonica-1.83.1
 ...
```

### Test 2: Check PATH
```powershell
where tesseract
```

Expected output:
```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## 🔄 Restart AI Service

After installing Tesseract:

1. Stop the current AI service (Ctrl+C in terminal)
2. Restart it:
   ```powershell
   cd ai-service
   python main.py
   ```
3. Look for: `"Using Tesseract OCR"` in startup messages

---

## 🧪 Test Real OCR

After installation:

1. Refresh browser
2. Go to File Claim page
3. Scan or upload a real document (Aadhaar, Voter ID)
4. Form should auto-fill with **actual extracted text**! ✨

---

## 🎯 Mock Mode vs Real OCR

### Mock Mode (Current - No Tesseract)
```json
{
  "mode": "mock",
  "extracted_data": {
    "name": "राम कुमार",  // Generated demo data
    "father_name": "श्याम लाल",
    "land_area": "2.5"
  },
  "warning": "Using demo data - Tesseract not installed"
}
```

### Real OCR Mode (With Tesseract)
```json
{
  "mode": "tesseract",
  "extracted_data": {
    "name": "ACTUAL NAME FROM DOCUMENT",  // Real extracted text
    "father_name": "ACTUAL FATHER NAME",
    "land_area": "3.2"
  }
}
```

---

## 🔧 Troubleshooting

### Issue: "tesseract is not recognized"
**Solution**: Restart PowerShell/Terminal after installation for PATH to update

### Issue: Still getting mock data after install
**Solution**: 
1. Restart AI service
2. Check `tesseract --version` works
3. Look at AI service logs for "Using Tesseract" message

### Issue: "Error 0xc000007b"
**Solution**: Install Visual C++ Redistributables:
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 📊 Language Support

### English Documents:
- ✅ Automatic (included by default)

### Hindi Documents:
- ✅ Install "Hindi Language Data" during setup
- ✅ Auto-detected by the system

### Additional Languages:
During installation, you can also install:
- Marathi
- Bengali  
- Telugu
- Tamil
- Oriya
- And more...

---

## 💡 Current Workflow (Mock Mode)

**No Tesseract Required!**

```
User scans document
       ↓
Mock data generated (realistic)
       ↓
Form auto-fills
       ↓
User can test full feature
```

**Works perfectly for:**
- ✅ Testing the UI
- ✅ Demonstrating the feature
- ✅ Training users
- ✅ Development/testing

---

## 🚀 When to Install Tesseract?

### Install if you need:
- Real text extraction from documents
- Production deployment
- Actual Aadhaar/Voter ID processing
- Accurate land record extraction

### Don't install if you're:
- Just testing the UI
- Doing a demo/presentation  
- Developing other features
- Happy with mock data for now

---

## 📞 Support

### Tesseract Issues:
- Official docs: https://tesseract-ocr.github.io/
- GitHub: https://github.com/tesseract-ocr/tesseract

### AI Service Issues:
- Check logs in terminal
- Look for "Tesseract not available" warnings
- Verify file permissions

---

## ✅ Summary

**Current Status:**
- ✅ OCR Feature: WORKING (Mock Mode)
- ✅ Camera: WORKING
- ✅ Auto-fill: WORKING
- ⏳ Real Text Extraction: Needs Tesseract

**Action Required:**
- None! System works now with mock data
- Optional: Install Tesseract for real OCR

**Next Steps:**
1. Test the current mock mode
2. Decide if you need real OCR
3. Install Tesseract when ready
4. Restart AI service
5. Enjoy real text extraction! 🎉
