# 🚀 Quick Start Guide - Document Verification Workflow

## Prerequisites

1. **Blockchain Service Running** (Port 8001)
2. **AI Service Running** (Port 8000)
3. **Frontend Running** (Port 3000)

---

## Step 1: Start All Services

### Terminal 1: Blockchain Service
```powershell
cd blockchain-service
npm install  # First time only
node server.js
```
**Expected:** ✅ Blockchain service running on port 8001

---

### Terminal 2: AI Service
```powershell
cd ai-service
python main.py
```
**Expected:**
```
🤖 Starting FRA Atlas AI Service...
📄 OCR Engine: ✅ Tesseract (Real OCR)
🛰️ Satellite Analysis: Enabled
🌲 Forest Monitoring: Enabled
🔗 Blockchain Integration: Enabled
🚀 Server running on http://localhost:8000
```

---

### Terminal 3: Frontend
```powershell
cd frontend-main
npm start
```
**Expected:** ✅ React app on http://localhost:3000

---

## Step 2: Test the Complete Workflow

### Option A: Using cURL (Command Line)

```powershell
# Prepare test image (use any patta/document image)
$imagePath = "path\to\your\document.jpg"

# Submit for verification
curl -X POST http://localhost:8000/api/document/comprehensive-verification `
  -F "file=@$imagePath" `
  -F "applicant_name=Ram Kumar" `
  -F "applicant_location=Bhamragad, Gadchiroli, Maharashtra" `
  -F "latitude=18.9217" `
  -F "longitude=77.0038" `
  -F "language=auto"
```

---

### Option B: Using Python Script

Create `test_workflow.py`:

```python
import requests

url = "http://localhost:8000/api/document/comprehensive-verification"

files = {
    'file': open('document.jpg', 'rb')
}

data = {
    'applicant_name': 'Ram Kumar',
    'applicant_location': 'Bhamragad, Gadchiroli, Maharashtra',
    'latitude': 18.9217,
    'longitude': 77.0038,
    'language': 'auto'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

Run:
```powershell
python test_workflow.py
```

---

### Option C: Using Postman

1. **Method:** POST
2. **URL:** `http://localhost:8000/api/document/comprehensive-verification`
3. **Body Type:** form-data
4. **Fields:**
   - `file` (File) → Select document image
   - `applicant_name` (Text) → "Ram Kumar"
   - `applicant_location` (Text) → "Bhamragad, Gadchiroli"
   - `latitude` (Text) → "18.9217"
   - `longitude` (Text) → "77.0038"
   - `language` (Text) → "auto"

---

## Step 3: Check Workflow Status

### Get Specific Workflow
```powershell
# Use workflow_id from previous response
curl http://localhost:8000/api/document/workflow/WF-20251008123045-0001
```

### Get All Workflows
```powershell
# All workflows
curl http://localhost:8000/api/document/workflows

# Filter by status
curl "http://localhost:8000/api/document/workflows?status=approved&limit=50"
```

---

## Step 4: Check Officer Reports

```powershell
# All reports
curl http://localhost:8000/api/officer/reports

# Filter by status
curl "http://localhost:8000/api/officer/reports?status=pending_review&priority=high"
```

---

## Step 5: Resolve a Report (Officer Action)

```powershell
curl -X POST http://localhost:8000/api/officer/report/RPT-20251008123045-0001/resolve `
  -H "Content-Type: application/json" `
  -d '{
    \"resolution\": \"Verified manually - Document is authentic\",
    \"action_taken\": \"Approved application manually\"
  }'
```

---

## 🎯 Expected Outcomes

### ✅ Successful Workflow (High Forest Area)
**Input:**
- Location: Bhamragad, Gadchiroli (known forest area)
- Coordinates: 18.9217, 77.0038

**Result:**
```json
{
  "success": true,
  "workflow_id": "WF-...",
  "status": "approved",
  "blockchain_hash": "abc123...",
  "hyperledger_hash": "def456...",
  "location_match_score": 85.5,
  "dss_recommendation": {
    "score": 85,
    "recommendation": "Highly eligible",
    "eligible_schemes": [
      "Community Forest Rights (CFR)",
      "Individual Forest Rights (IFR)",
      "Forest Dwelling Certificate"
    ]
  },
  "final_decision": "approved"
}
```

---

### ⚠️ Blockchain Failure
**Scenario:** Blockchain service down or verification fails

**Result:**
```json
{
  "success": false,
  "workflow_id": "WF-...",
  "status": "blockchain_failed",
  "message": "Blockchain verification failed. Reported to officer for review.",
  "officer_report_id": "RPT-..."
}
```

---

### 📍 Location Contradiction
**Input:**
- Location: Mumbai City (urban area)
- Coordinates: 19.0760, 72.8777

**Result:**
```json
{
  "success": true,
  "workflow_id": "WF-...",
  "status": "manual_review_required",
  "message": "Location contradiction detected. Sent for manual review.",
  "contradictions": [
    "Low vegetation index (NDVI: 0.15). Area appears barren.",
    "Land type mismatch. Detected: urban"
  ],
  "officer_report_id": "RPT-..."
}
```

---

## 🔍 Monitoring & Debugging

### Check Service Health

```powershell
# AI Service
curl http://localhost:8000/health

# Blockchain Service
curl http://localhost:8001/health
```

### View Logs

**AI Service Console:**
- OCR processing logs
- Blockchain communication
- Location verification results
- DSS scoring details

**Blockchain Service Console:**
- Transaction submissions
- Block creation
- Verification results

---

## 🎨 Frontend Integration (TODO)

To integrate with frontend, create a form component:

```jsx
// DocumentVerificationForm.js
const handleSubmit = async (formData) => {
  const data = new FormData();
  data.append('file', documentFile);
  data.append('applicant_name', applicantName);
  data.append('applicant_location', location);
  data.append('latitude', latitude);
  data.append('longitude', longitude);
  data.append('language', 'auto');

  const response = await fetch(
    'http://localhost:8000/api/document/comprehensive-verification',
    {
      method: 'POST',
      body: data
    }
  );

  const result = await response.json();
  
  if (result.success) {
    if (result.status === 'approved') {
      // Show success message
      toast.success('Application approved! Eligible schemes: ' + 
        result.dss_recommendation.eligible_schemes.join(', '));
    } else if (result.status === 'manual_review_required') {
      // Show review message
      toast.info('Application sent for manual review. Report ID: ' + 
        result.officer_report_id);
    }
  }
};
```

---

## 📊 Test Scenarios

### Scenario 1: Perfect Case (Should Approve)
```
Applicant: Ram Kumar
Location: Bhamragad, Gadchiroli, Maharashtra
Coordinates: 18.9217, 77.0038
Document: Clear patta image with all details
Expected: APPROVED (DSS score ≥ 80)
```

### Scenario 2: Urban Area (Should Reject)
```
Applicant: Test User
Location: Mumbai
Coordinates: 19.0760, 72.8777
Document: Any document
Expected: MANUAL_REVIEW (Location contradiction)
```

### Scenario 3: Blockchain Down (Should Report)
```
Stop blockchain service first
Upload any document
Expected: BLOCKCHAIN_FAILED (Officer report created)
```

---

## 🛠️ Troubleshooting

### Issue: "Blockchain service unavailable"
**Solution:**
1. Check if blockchain service is running on port 8001
2. Verify `http://localhost:8001/health` returns success
3. Check firewall settings

### Issue: "Tesseract not found"
**Solution:**
1. Install Tesseract OCR
2. System will use mock mode if Tesseract unavailable
3. See `TESSERACT_INSTALLATION.md` for setup

### Issue: "File upload failed"
**Solution:**
1. Check file size (< 10MB)
2. Ensure file type is image (jpg, png, tiff, bmp)
3. Verify `uploads/` directory exists

---

## ✅ Success Checklist

- [ ] Blockchain service running (port 8001)
- [ ] AI service running (port 8000)
- [ ] Test document uploaded successfully
- [ ] Workflow ID received
- [ ] Blockchain hash created
- [ ] Hyperledger hash generated
- [ ] Location verification completed
- [ ] DSS score calculated
- [ ] Final decision received
- [ ] Officer reports accessible

---

## 📞 Support

- API Documentation: http://localhost:8000/docs
- Workflow Status: `GET /api/document/workflows`
- Officer Reports: `GET /api/officer/reports`

---

*Quick Start Guide - FRA Atlas Document Verification System*  
*Version 1.0 - October 8, 2025*
