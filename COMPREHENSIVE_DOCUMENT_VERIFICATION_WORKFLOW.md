# 📄 Comprehensive Document Verification Workflow

## 🎯 Complete Pipeline Implementation

This document describes the **end-to-end automated document verification workflow** for Forest Rights Act (FRA) patta/document submissions.

---

## 🔄 Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT UPLOAD (Step 1)                         │
│  Citizen/Admin uploads patta or forest rights document             │
└───────────────────────┬─────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BLOCKCHAIN VERIFICATION (Step 2)                       │
│  Document hash sent to blockchain for authenticity check            │
└───────┬───────────────────────────────────────────┬─────────────────┘
        │ FAIL                                      │ PASS
        ▼                                           ▼
┌──────────────────────┐              ┌────────────────────────────────┐
│  REPORT TO OFFICER   │              │  CREATE HYPERLEDGER HASH       │
│  (Manual Review)     │              │  (Step 3)                      │
└──────────────────────┘              └────────────┬───────────────────┘
                                                   ▼
                                      ┌────────────────────────────────┐
                                      │  STATUS: PENDING (Step 4)      │
                                      │  Workflow continues...          │
                                      └────────────┬───────────────────┘
                                                   ▼
                                      ┌────────────────────────────────┐
                                      │  LOCATION VERIFICATION         │
                                      │  Earth Engine / Bhuvan         │
                                      │  (Step 5)                      │
                                      └────┬───────────────────┬───────┘
                                           │ CONTRADICTION     │ NO CONTRADICTION
                                           ▼                   ▼
                                  ┌────────────────┐  ┌──────────────────────┐
                                  │ MANUAL REVIEW  │  │  DSS ELIGIBILITY     │
                                  │ (Report)       │  │  CHECK (Step 7)      │
                                  └────────────────┘  └──────────┬───────────┘
                                                                 ▼
                                                      ┌──────────────────────┐
                                                      │  FINAL DECISION      │
                                                      │  (Step 8)            │
                                                      │  - Approved          │
                                                      │  - Requires Review   │
                                                      └──────────────────────┘
```

---

## 📋 Detailed Step-by-Step Process

### **Step 1: Document Upload**
- **Action:** Citizen or admin uploads patta/document
- **Processing:**
  - File saved temporarily
  - OCR extraction of text
  - Form type detection
  - Entity extraction (name, location, dates, etc.)
- **Output:** Workflow ID created, document data extracted

---

### **Step 2: Blockchain Verification**
- **Action:** Document hash sent to blockchain service
- **URL:** `http://localhost:8001/api/submit-verification`
- **Verification Checks:**
  - Document hash integrity
  - Applicant name validation
  - Location verification
  - Metadata consistency
- **Outcomes:**
  - ✅ **PASS** → Continue to Step 3
  - ❌ **FAIL** → Report to officer (END)

---

### **Step 3: Create Hyperledger Hash** (If blockchain passes)
- **Action:** Generate immutable hash in Hyperledger
- **Hash Format:** SHA-256 of `{workflow_id}-{applicant_name}-{timestamp}`
- **Purpose:** Permanent record of verification attempt
- **Storage:** Hash stored in workflow record

---

### **Step 4: Status Update to "Pending"**
- **Action:** Workflow status → `PENDING_LOCATION_CHECK`
- **Purpose:** Indicates blockchain verified, awaiting location check
- **Notification:** Status visible to applicant and officers

---

### **Step 5: Location Verification (Earth Engine / Bhuvan)**
- **Action:** Satellite imagery analysis of claimed location
- **Data Sources:**
  - Google Earth Engine (simulated)
  - Bhuvan API (simulated)
  - Internal monitoring locations database
- **Checks Performed:**
  
  **A. NDVI Analysis (Vegetation Index)**
  - NDVI < 0.2 → ⚠️ Barren land (contradiction)
  - NDVI 0.2-0.4 → ⚠️ Sparse vegetation
  - NDVI 0.4-0.6 → ✅ Moderate vegetation
  - NDVI > 0.6 → ✅ Dense forest

  **B. Land Type Verification**
  - Expected: Forest, Dense Vegetation, Woodland
  - Contradiction if: Urban, Agricultural, Barren

  **C. Location Matching**
  - Check against 42 monitoring locations
  - Match if within 5 km of known forest area
  - Match score calculated (0-100%)

- **Outcomes:**
  - ⚠️ **CONTRADICTION FOUND** → Manual Review (Step 6)
  - ✅ **NO CONTRADICTION** → DSS Evaluation (Step 7)

---

### **Step 6: Manual Review** (If contradictions found)
- **Trigger Conditions:**
  - Low NDVI (barren land)
  - Non-forest land type
  - Location mismatch
- **Action:** Create officer report
- **Report Contains:**
  - Workflow ID
  - Applicant details
  - Issue type: `location_contradiction`
  - Detailed reasons
  - Priority level: MEDIUM
  - Satellite data (NDVI, land type, coordinates)
- **Officer Dashboard:** Report visible for review
- **End of automated process** → Awaits human decision

---

### **Step 7: DSS Eligibility Check** (If no contradictions)
- **Action:** Decision Support System evaluates eligibility
- **Scoring Factors:**

| Factor | Max Points | Criteria |
|--------|-----------|----------|
| Vegetation Health | 30 | NDVI > 0.6: 30pts, 0.4-0.6: 20pts, <0.4: 10pts |
| Location Match | 25 | Within monitored area: 25pts |
| Document Confidence | 25 | OCR confidence > 80%: 25pts, 60-80%: 15pts |
| Blockchain Verified | 20 | Always 20pts if reached this step |

- **Total Score:** 0-100

**Eligibility Determination:**
- **Score ≥ 80:** Highly eligible
  - Schemes: CFR, IFR, Forest Dwelling Certificate
- **Score 60-79:** Eligible with conditions
  - Schemes: IFR, Forest Dwelling Certificate
- **Score < 60:** Additional verification required
  - Outcome: Manual review

---

### **Step 8: Final Decision**
- **If DSS Score ≥ 60:**
  - Status: `APPROVED`
  - Decision: `approved`
  - Eligible schemes listed
  
- **If DSS Score < 60:**
  - Status: `MANUAL_REVIEW`
  - Decision: `requires_review`
  - Officer report created

---

## 🔧 API Endpoints

### 1. Submit Document for Verification
```http
POST /api/document/comprehensive-verification
Content-Type: multipart/form-data

Parameters:
- file: UploadFile (required) - Document image
- applicant_name: string (required)
- applicant_location: string (required)
- latitude: float (required)
- longitude: float (required)
- language: string (default: "auto")

Response:
{
  "success": true,
  "workflow_id": "WF-20251008123045-0001",
  "status": "approved",
  "message": "Document verification workflow completed successfully",
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
    ],
    "factors": [
      "Good vegetation health",
      "Location within monitored forest area",
      "High document authenticity",
      "Blockchain verified"
    ]
  },
  "final_decision": "approved"
}
```

### 2. Get Workflow Status
```http
GET /api/document/workflow/{workflow_id}

Response:
{
  "success": true,
  "workflow": {
    "workflow_id": "WF-20251008123045-0001",
    "status": "approved",
    "applicant_name": "Ram Kumar",
    "steps": [ /* all steps */ ],
    "blockchain_hash": "...",
    "hyperledger_hash": "...",
    "dss_recommendation": { /* ... */ }
  }
}
```

### 3. Get All Workflows
```http
GET /api/document/workflows?status=approved&limit=50

Response:
{
  "success": true,
  "total": 15,
  "workflows": [ /* workflow objects */ ]
}
```

### 4. Get Officer Reports
```http
GET /api/officer/reports?status=pending_review&priority=high

Response:
{
  "success": true,
  "total": 3,
  "reports": [
    {
      "report_id": "RPT-20251008123045-0001",
      "workflow_id": "WF-20251008123045-0001",
      "applicant_name": "Ram Kumar",
      "issue_type": "blockchain_verification_failed",
      "details": "Document hash mismatch",
      "priority": "high",
      "status": "pending_review",
      "created_at": "2025-10-08T12:30:45Z"
    }
  ]
}
```

### 5. Resolve Officer Report
```http
POST /api/officer/report/{report_id}/resolve

Body:
{
  "resolution": "Verified manually - Document is authentic",
  "action_taken": "Approved application manually"
}

Response:
{
  "success": true,
  "message": "Report resolved successfully",
  "report": { /* updated report */ }
}
```

---

## 📊 Workflow Status Codes

| Status | Description |
|--------|-------------|
| `uploaded` | Document uploaded, processing started |
| `blockchain_verification` | Being verified on blockchain |
| `blockchain_failed` | Blockchain verification failed → Officer review |
| `blockchain_verified` | Blockchain verification passed |
| `pending_location_check` | Awaiting satellite location verification |
| `location_contradiction` | Location issues found → Manual review |
| `manual_review` | Requires officer intervention |
| `dss_evaluation` | Decision Support System evaluating |
| `approved` | Workflow completed - Application approved |
| `rejected` | Application rejected |

---

## 🎯 Integration Points

### 1. **Blockchain Service** (Port 8001)
- **Endpoint:** `POST /api/submit-verification`
- **Purpose:** Document authenticity verification
- **Technology:** Simple in-memory blockchain (can upgrade to Hyperledger)

### 2. **Satellite Analysis** (Internal)
- **Function:** `analyze_satellite(lat, lng, radius)`
- **Returns:** NDVI, land type, vegetation health
- **Source:** Simulated (ready for Earth Engine/Bhuvan API)

### 3. **Monitoring Locations Database**
- **Storage:** `monitoring_locations_db` (42 locations across India)
- **Purpose:** Verify claimed location is in known forest area

### 4. **OCR & Document Processing**
- **Engine:** Tesseract OCR
- **Extracts:** Names, dates, locations, form type
- **Confidence:** Validation score included

---

## 🧪 Testing the Workflow

### Test Case 1: Successful Approval
```bash
curl -X POST http://localhost:8000/api/document/comprehensive-verification \
  -F "file=@patta_document.jpg" \
  -F "applicant_name=Ram Kumar" \
  -F "applicant_location=Bhamragad, Gadchiroli" \
  -F "latitude=18.9217" \
  -F "longitude=77.0038" \
  -F "language=auto"
```

**Expected:** Status `approved`, DSS score ≥ 80

---

### Test Case 2: Blockchain Failure
```bash
# Ensure blockchain service is down or returns error
curl -X POST http://localhost:8000/api/document/comprehensive-verification \
  -F "file=@invalid_doc.jpg" \
  -F "applicant_name=Test User" \
  -F "applicant_location=Unknown" \
  -F "latitude=0" \
  -F "longitude=0"
```

**Expected:** Status `blockchain_failed`, officer report created

---

### Test Case 3: Location Contradiction
```bash
# Use coordinates of barren/urban area
curl -X POST http://localhost:8000/api/document/comprehensive-verification \
  -F "file=@document.jpg" \
  -F "applicant_name=Test User" \
  -F "applicant_location=Mumbai City" \
  -F "latitude=19.0760" \
  -F "longitude=72.8777"  # Mumbai coordinates
```

**Expected:** Status `manual_review`, contradiction report

---

## 🚀 Deployment Checklist

- [ ] Start blockchain service: `node blockchain-service/server.js` (Port 8001)
- [ ] Start AI service: `python ai-service/main.py` (Port 8000)
- [ ] Verify Tesseract OCR installed
- [ ] Test blockchain connectivity
- [ ] Upload test documents
- [ ] Review officer dashboard for reports
- [ ] Monitor workflow status transitions

---

## 📈 Future Enhancements

1. **Real Satellite Integration:**
   - Google Earth Engine API
   - ISRO Bhuvan API
   - Historical imagery comparison

2. **Enhanced DSS:**
   - Machine learning eligibility prediction
   - Historical approval patterns
   - Multi-factor risk scoring

3. **Blockchain Upgrade:**
   - Hyperledger Fabric integration
   - Smart contract automation
   - Distributed verification nodes

4. **Notification System:**
   - SMS alerts to applicants
   - Email reports to officers
   - Real-time dashboard updates

5. **Advanced Location Verification:**
   - Boundary polygon matching
   - Multi-temporal analysis
   - Change detection algorithms

---

## 📝 Data Models

### Workflow Object
```javascript
{
  "workflow_id": "WF-YYYYMMDDHHMMSS-XXXX",
  "applicant_name": "string",
  "applicant_location": "string",
  "latitude": float,
  "longitude": float,
  "status": "status_code",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "steps": [
    {
      "step": "step_name",
      "status": "success|failed|error",
      "timestamp": "ISO 8601",
      /* step-specific data */
    }
  ],
  "blockchain_hash": "string|null",
  "hyperledger_hash": "string|null",
  "location_match_score": float|null,
  "dss_recommendation": object|null,
  "final_decision": "approved|requires_review|rejected|null"
}
```

### Officer Report Object
```javascript
{
  "report_id": "RPT-YYYYMMDDHHMMSS-XXXX",
  "workflow_id": "WF-...",
  "applicant_name": "string",
  "issue_type": "blockchain_verification_failed|location_contradiction|blockchain_service_error",
  "details": "string",
  "priority": "high|medium|low",
  "status": "pending_review|resolved",
  "created_at": "ISO 8601",
  "resolved_at": "ISO 8601|null",
  "resolution": "string|null",
  "action_taken": "string|null"
}
```

---

## ✅ Success Criteria

- ✅ Document uploaded and OCR extraction successful
- ✅ Blockchain verification integrated
- ✅ Failed verifications reported to officers
- ✅ Hyperledger hash created for verified documents
- ✅ Status transitions to "Pending"
- ✅ Location verified using satellite data
- ✅ Contradictions trigger manual review
- ✅ DSS evaluates eligibility automatically
- ✅ Final decision made (approved/review)
- ✅ Complete audit trail maintained

---

*Generated: October 8, 2025*  
*FRA Atlas - Comprehensive Document Verification System*  
*Version 1.0*
