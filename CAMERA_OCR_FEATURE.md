# 📸 Camera OCR Feature - Complete Documentation

## ✅ Feature Overview
The Citizen Portal now includes **AI-powered document scanning** with automatic form auto-fill capabilities.

---

## 🎯 Key Features

### 1. **Smart Document Scanner**
- 📸 Live camera preview with positioning guide
- 📤 File upload alternative option
- 🤖 AI-powered OCR text extraction
- ⚡ Real-time processing with visual feedback

### 2. **Auto-fill Capabilities**
The OCR automatically extracts and fills:
- ✅ **Beneficiary Name** - from ID cards
- ✅ **Father's Name** - from documents
- ✅ **Land Area** - from land records
- ✅ **Location** - from address details

### 3. **Supported Documents**
- 🆔 Aadhaar Card
- 🗳️ Voter ID
- 📄 Land Records (Khasra/Khatauni)
- 🏠 Residence Proof
- 📋 Any government-issued ID

### 4. **User Experience**
- **Camera Modal** - Full-screen camera interface
- **Guide Overlay** - Helps position document correctly
- **Processing Indicator** - Shows "Processing document with AI..."
- **Success Toast** - Confirms extraction and auto-fill
- **Editable Fields** - User can review and correct extracted data

---

## 🔧 Technical Implementation

### API Endpoint
```
POST http://localhost:8000/api/ocr/extract
Content-Type: multipart/form-data
```

### Request Format
```javascript
FormData {
  file: [image blob or file]
}
```

### Response Format
```javascript
{
  "extracted_data": {
    "name": "John Doe",
    "father_name": "Robert Doe",
    "land_area": "2.5",
    "location": "Village Khargone, MP"
  }
}
```

### Frontend Implementation
- **Camera Access**: Uses `navigator.mediaDevices.getUserMedia()`
- **Image Capture**: HTML5 Canvas for snapshot
- **OCR Processing**: Axios POST to AI service
- **Auto-fill**: React state update with extracted data

---

## 📋 How to Use

### For Citizens:

1. **Login**
   - Navigate to home page
   - Click "User Login"
   - Use credentials: `viewer` / `viewer123`

2. **Access File Claim**
   - In dashboard sidebar, click "File Claim"
   - Navigate to "File New Claim" tab

3. **Scan Document**
   - Click "Scan Document" button
   - Allow camera access when prompted
   - Position document within the guide frame
   - Click "Capture & Process"

4. **Review & Submit**
   - Verify auto-filled information
   - Edit any incorrect fields
   - Complete remaining fields
   - Submit claim

### Alternative: File Upload
- Click "Choose Files" instead
- Select image from device
- OCR processes automatically
- Form auto-fills same way

---

## 🎨 UI Components

### Document Scanner Button
```jsx
<Button onClick={startCamera}>
  <Camera className="w-4 h-4" />
  Scan Document
</Button>
```

### Camera Modal Features
- ✅ Live video preview
- ✅ Positioning guide overlay
- ✅ Capture button
- ✅ Close/cancel option
- ✅ Instructions and tips

### Processing State
```jsx
{processingOCR && (
  <Loader2 className="animate-spin" />
  <span>Processing document with AI...</span>
)}
```

---

## 🔐 Security & Privacy

- **Camera Access**: Requested only when needed
- **Image Processing**: Images sent to local AI service (not cloud)
- **Data Storage**: Extracted data stored in form state only
- **User Control**: All auto-filled data is editable

---

## 🚀 Benefits

### For Citizens:
- ⏱️ **Saves Time** - No manual typing needed
- ✍️ **Reduces Errors** - OCR extracts exact text
- 📱 **Mobile Friendly** - Works on smartphones
- 🌐 **Language Support** - Processes Hindi/English docs

### For Officers:
- 📊 **Better Data Quality** - Accurate information
- 🔄 **Faster Processing** - Pre-filled applications
- ✅ **Easy Verification** - Consistent format

---

## 🧪 Testing the Feature

### Manual Test:
1. Start all services (Frontend, AI service)
2. Login as viewer
3. Go to File Claim
4. Click "Scan Document"
5. Use any ID card or document
6. Verify form auto-fills

### Test Documents:
- Sample Aadhaar card image
- Voter ID card
- Land record document
- Any clear text document

---

## 📊 System Flow

```
User clicks "Scan Document"
         ↓
Camera modal opens
         ↓
User positions document
         ↓
Click "Capture & Process"
         ↓
Image captured to canvas
         ↓
Sent to AI service OCR endpoint
         ↓
Text extracted by AI
         ↓
Form fields auto-filled
         ↓
User reviews and submits
```

---

## 🔄 Future Enhancements

- [ ] Multi-document scanning (upload multiple pages)
- [ ] PDF support with page selection
- [ ] Confidence score display for extracted fields
- [ ] Document type auto-detection
- [ ] Batch processing for multiple claims
- [ ] Offline OCR capability

---

## 🆘 Troubleshooting

### Camera Not Working?
- Check browser permissions
- Ensure HTTPS or localhost
- Try "Choose Files" instead

### OCR Not Extracting?
- Ensure AI service is running on port 8000
- Check document is clear and well-lit
- Verify image quality

### Form Not Auto-filling?
- Check browser console for errors
- Verify API response format
- Ensure field names match

---

## 📞 Support

For issues or questions:
- Check browser console for errors
- Verify all services are running
- Test with sample documents first

---

**Status**: ✅ Fully Implemented and Ready to Use!

**Last Updated**: October 7, 2025
