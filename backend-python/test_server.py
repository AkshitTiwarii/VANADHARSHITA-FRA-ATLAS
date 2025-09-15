from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import pandas as pd
import io

# Simple FastAPI app for testing
app = FastAPI(title="FRA Atlas API - Test Mode", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
validations_store = []
claims_store = []

# Simple validation function
def simple_data_validation(df: pd.DataFrame, dataset_type: str) -> Dict:
    """Simple data validation for CSV files"""
    issues = []
    confidence_score = 1.0
    
    # Check for missing values
    missing_pct = df.isnull().mean().mean()
    if missing_pct > 0.2:
        issues.append("high_missing_values")
        confidence_score -= 0.3
    elif missing_pct > 0.1:
        issues.append("moderate_missing_values")
        confidence_score -= 0.1
    
    # Check for duplicates
    duplicate_pct = df.duplicated().sum() / len(df) if len(df) > 0 else 0
    if duplicate_pct > 0.05:
        issues.append("duplicate_records")
        confidence_score -= 0.2
    
    # Ensure confidence is between 0 and 1
    confidence_score = max(0.0, min(1.0, confidence_score))
    
    return {
        'confidence_score': confidence_score,
        'issues': issues,
        'total_rows': len(df),
        'total_columns': len(df.columns)
    }

# Models
class DashboardStats(BaseModel):
    total_villages: int
    total_claims: int
    approved_claims: int
    pending_claims: int
    disputed_claims: int
    ocr_accuracy: float
    schemes_integrated: int
    total_budget_linked: float

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    return DashboardStats(
        total_villages=150,
        total_claims=1245,
        approved_claims=892,
        pending_claims=253,
        disputed_claims=45,
        ocr_accuracy=87.5,
        schemes_integrated=4,
        total_budget_linked=125000000.0
    )

@app.post("/api/data/validate-csv")
async def validate_csv_data(file: UploadFile = File(...), dataset_type: str = Form(...)):
    """Upload and validate CSV data for quality issues and potential fake data"""
    try:
        # Read uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate the data
        validation_result = simple_data_validation(df, dataset_type)
        
        # Generate unique ID for this validation
        validation_id = str(uuid.uuid4())
        validation_doc = {
            "id": validation_id,
            "dataset_name": file.filename,
            "validation_status": "pending",
            "confidence_score": validation_result.get('confidence_score', 0.0),
            "issues_found": validation_result.get('issues', []),
            "record_count": len(df),
            "validated_at": datetime.now().isoformat(),
            "validated_by": None,
            "notes": None
        }
        
        # Store in memory
        validations_store.append(validation_doc)
        print(f"📊 Validation completed for {file.filename}")
        
        return {
            "id": validation_id,
            "validation_id": validation_id,
            "status": "validation_complete",
            "confidence_score": validation_result.get('confidence_score', 0.0),
            "issues_found": validation_doc["issues_found"],
            "record_count": len(df),
            "validation_status": "pending",
            "requires_manual_review": validation_result.get('confidence_score', 0.0) < 0.7
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")

@app.get("/api/data/validations")
async def get_data_validations():
    """Get all data validation results"""
    return validations_store

@app.put("/api/data/validations/{validation_id}")
async def update_validation_status(validation_id: str, status: str = Form(...), notes: str = Form(None), validated_by: str = Form(None)):
    """Update validation status (pass/fail) after manual review"""
    try:
        # Find validation in store
        validation = None
        for i, v in enumerate(validations_store):
            if v["id"] == validation_id:
                validation = v
                break
        
        if not validation:
            raise HTTPException(status_code=404, detail="Validation not found")
        
        # Update status
        validation["validation_status"] = status
        validation["validated_at"] = datetime.now().isoformat()
        
        if notes:
            validation["notes"] = notes
        if validated_by:
            validation["validated_by"] = validated_by
            
        return {"message": "Validation status updated", "status": status}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

@app.get("/api/claims")
async def get_claims(limit: Optional[int] = None):
    """Get forest claims - returning empty list for testing"""
    return []

@app.get("/api/villages") 
async def get_villages():
    """Get villages - returning empty list for testing"""
    return []

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FRA Atlas API Test Mode is running"}

if __name__ == "__main__":
    import uvicorn
    print("🌱 FRA Atlas API Test Mode Starting...")
    uvicorn.run("test_server:app", host="127.0.0.1", port=3001, reload=True)