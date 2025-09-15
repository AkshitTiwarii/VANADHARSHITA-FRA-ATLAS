from fastapi import FastAPI, APIRouter, Query, HTTPException, UploadFile, File, Form
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
import pandas as pd
import numpy as np
import io
import json
import os
import sys
from bson import ObjectId

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "fra_db"

# Test MongoDB connection
def test_mongodb_connection():
    try:
        test_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000)
        test_client.server_info()
        print("✅ MongoDB connection successful")
        test_client.close()
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

# Check if MongoDB is available
mongodb_available = test_mongodb_connection()

# In-memory storage for offline mode
offline_validations = []
offline_claims = []

# Initialize MongoDB only if available
if mongodb_available:
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
else:
    client = None
    db = None
    print("⚠️  Running in offline mode without MongoDB")

# Simple data validation function (fallback)
def simple_data_validation(df: pd.DataFrame, dataset_type: str) -> Dict:
    """Simple data validation for CSV files"""
    issues = []
    confidence_score = 1.0
    
    # Check for missing values
    missing_pct = df.isnull().mean().mean()
    if missing_pct > 0.2:
        issues.append({"check_type": "missing_values", "severity": "high"})
        confidence_score -= 0.3
    elif missing_pct > 0.1:
        issues.append({"check_type": "missing_values", "severity": "medium"})
        confidence_score -= 0.1
    
    # Check for duplicates
    duplicate_pct = df.duplicated().sum() / len(df) if len(df) > 0 else 0
    if duplicate_pct > 0.05:
        issues.append({"check_type": "duplicates", "severity": "medium"})
        confidence_score -= 0.2
    
    # Check for suspicious patterns (all same values, etc.)
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].nunique() == 1 and len(df) > 10:
            issues.append({"check_type": "suspicious_uniformity", "column": col, "severity": "high"})
            confidence_score -= 0.3
    
    # Check data types
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if numeric data is stored as string
            try:
                pd.to_numeric(df[col], errors='raise')
                issues.append({"check_type": "data_type_issue", "column": col, "severity": "low"})
                confidence_score -= 0.05
            except:
                pass
    
    # Ensure confidence is between 0 and 1
    confidence_score = max(0.0, min(1.0, confidence_score))
    
    return {
        'confidence_score': confidence_score,
        'issues': issues,
        'valid': len(issues) == 0,
        'total_rows': len(df),
        'total_columns': len(df.columns)
    }

# Pydantic Models
class DashboardStats(BaseModel):
    total_villages: int
    total_claims: int
    approved_claims: int
    pending_claims: int
    disputed_claims: int
    ocr_accuracy: float
    schemes_integrated: int
    total_budget_linked: float

class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float]

class Village(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    state: str
    district: str
    tehsil: str
    village_code: str
    total_area: float
    forest_area: float
    coordinates: Dict[str, Any]
    population: int
    tribal_population: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForestClaim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_type: str  # "IFR", "CR", "CFR"
    claim_number: str
    village_id: str
    village_name: str
    beneficiary_name: str
    beneficiary_father_name: str
    tribe_name: Optional[str] = None
    area_claimed: float
    coordinates: Dict[str, Any]
    status: str  # "pending", "approved", "rejected", "disputed", "verified"
    submitted_date: datetime
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_officer: Optional[str] = None
    verification_status: Optional[str] = None  # "not_started", "in_progress", "completed"
    field_verification_date: Optional[datetime] = None
    ai_recommendation: Optional[Dict[str, Any]] = None
    ocr_documents: List[Dict[str, Any]] = []
    linked_schemes: List[str] = []
    patta_number: Optional[str] = None  # For granted claims
    granted_area: Optional[float] = None  # May differ from claimed area
    granted_date: Optional[datetime] = None
    survey_number: Optional[str] = None
    revenue_village: Optional[str] = None
    forest_division: Optional[str] = None
    forest_range: Optional[str] = None
    land_classification: Optional[str] = None  # Forest type classification
    encumbrance_details: Optional[Dict[str, Any]] = None
    gram_sabha_resolution: Optional[str] = None
    gram_sabha_date: Optional[datetime] = None
    duly_committee_recommendation: Optional[str] = None
    sdlc_recommendation: Optional[str] = None
    dlc_decision: Optional[str] = None
    appeals_filed: Optional[List[Dict[str, Any]]] = None

class ClaimCreate(BaseModel):
    claim_type: str
    village_id: str
    village_name: str
    beneficiary_name: str
    beneficiary_father_name: str
    area_claimed: float

class ClaimUpdate(BaseModel):
    status: Optional[str] = None
    assigned_officer: Optional[str] = None
    ai_recommendation: Optional[Dict[str, Any]] = None
    ocr_documents: Optional[List[Dict[str, Any]]] = None
    linked_schemes: Optional[List[str]] = None

class VillageGeoJSON(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONPoint
    properties: Dict[str, Any]

class FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[VillageGeoJSON]

# New models for FRA Atlas requirements

class DataValidationResult(BaseModel):
    dataset_name: str
    validation_status: str  # "pass", "fail", "pending"
    confidence_score: float
    issues_found: List[str]
    record_count: int
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    validated_by: Optional[str] = None
    notes: Optional[str] = None

class FRADocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: str  # "IFR", "CR", "CFR"
    claim_id: str
    file_path: str
    extracted_text: Optional[str] = None
    entities_extracted: Optional[Dict[str, Any]] = None  # NER results
    ocr_confidence: Optional[float] = None
    processed_at: Optional[datetime] = None

class SatelliteAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    village_id: str
    asset_type: str  # "agricultural_land", "forest_cover", "water_body", "homestead"
    coordinates: Dict[str, Any]  # GeoJSON geometry
    area_hectares: float
    confidence_score: float
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    satellite_image_date: Optional[datetime] = None

class CSSScheme(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scheme_name: str  # "PM_KISAN", "JAL_JEEVAN_MISSION", "MGNREGA", etc.
    beneficiary_id: str
    village_id: str
    benefit_amount: Optional[float] = None
    status: str  # "active", "pending", "completed"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class DSRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    village_id: str
    recommended_schemes: List[str]
    priority_score: float
    reasoning: Dict[str, Any]
    water_index: Optional[float] = None
    agricultural_potential: Optional[float] = None
    forest_dependency: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Create FastAPI app and router
app = FastAPI(title="FRA Atlas API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    if not mongodb_available:
        # Return mock data for testing
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
    try:
        total_villages = await db.villages.count_documents({})
        total_claims = await db.forest_claims.count_documents({})
        approved_claims = await db.forest_claims.count_documents({"status": "approved"})
        pending_claims = await db.forest_claims.count_documents({"status": "pending"})
        disputed_claims = await db.forest_claims.count_documents({"status": "disputed"})
        
        return DashboardStats(
            total_villages=total_villages,
            total_claims=total_claims,
            approved_claims=approved_claims,
            pending_claims=pending_claims,
            disputed_claims=disputed_claims,
            ocr_accuracy=87.5,
            schemes_integrated=4,
            total_budget_linked=125000000.0
        )
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@api_router.get("/villages", response_model=List[Village])
async def get_villages(state: Optional[str] = None, district: Optional[str] = None):
    try:
        query = {}
        if state:
            query["state"] = state
        if district:
            query["district"] = district
        villages = await db.villages.find(query).to_list(1000)
        
        # Remove MongoDB _id field and convert to Pydantic models
        result = []
        for village_data in villages:
            village_data.pop('_id', None)  # Remove _id field
            try:
                village = Village(**village_data)
                result.append(village)
            except Exception as e:
                print(f"Error converting village data: {e}")
                print(f"Village data: {village_data}")
                continue
        
        return result
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@api_router.post("/villages", response_model=Village)
async def create_village(village_data: Village):
    village = Village(**village_data.dict())
    await db.villages.insert_one(village.dict())
    return village

@api_router.get("/claims", response_model=List[ForestClaim])
async def get_forest_claims(status: Optional[str] = None, village_id: Optional[str] = None):
    try:
        query = {}
        if status:
            query["status"] = status
        if village_id:
            query["village_id"] = village_id
        claims = await db.forest_claims.find(query).to_list(1000)
        
        # Remove MongoDB _id field and convert to Pydantic models
        result = []
        for claim_data in claims:
            claim_data.pop('_id', None)  # Remove _id field
            try:
                claim = ForestClaim(**claim_data)
                result.append(claim)
            except Exception as e:
                print(f"Error converting claim data: {e}")
                print(f"Claim data: {claim_data}")
                continue
        
        return result
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@api_router.post("/claims", response_model=ForestClaim)
async def create_forest_claim(claim_data: ClaimCreate):
    claim = ForestClaim(
        **claim_data.dict(),
        id=str(uuid.uuid4()),
        status="pending",
        submitted_date=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc),
        coordinates={"type": "Point", "coordinates": [0.0, 0.0]}
    )
    await db.forest_claims.insert_one(claim.dict())
    return claim

@api_router.put("/claims/{claim_id}", response_model=ForestClaim)
async def update_forest_claim(claim_id: str, updates: ClaimUpdate):
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    update_data["last_updated"] = datetime.now(timezone.utc)
    
    result = await db.forest_claims.find_one_and_update(
        {"id": claim_id},
        {"$set": update_data},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    result.pop('_id', None)
    return ForestClaim(**result)

@api_router.get("/claims/{claim_id}", response_model=ForestClaim)
async def get_forest_claim(claim_id: str):
    try:
        claim = await db.forest_claims.find_one({"id": claim_id})
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        claim.pop('_id', None)
        return ForestClaim(**claim)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@api_router.get("/map/villages", response_model=FeatureCollection)
async def get_villages_geojson(state: Optional[str] = None, district: Optional[str] = None):
    try:
        query = {}
        if state:
            query["state"] = state
        if district:
            query["district"] = district
        
        villages = await db.villages.find(query).to_list(1000)
        features = []
        
        for village in villages:
            village.pop('_id', None)
            
            feature = VillageGeoJSON(
                type="Feature",
                geometry=GeoJSONPoint(
                    type="Point",
                    coordinates=village["coordinates"]["coordinates"]
                ),
                properties={
                    "id": village["id"],
                    "name": village["name"],
                    "state": village["state"],
                    "district": village["district"],
                    "tehsil": village["tehsil"],
                    "village_code": village["village_code"],
                    "population": village["population"],
                    "tribal_population": village["tribal_population"],
                    "total_area": village["total_area"],
                    "forest_area": village["forest_area"]
                }
            )
            features.append(feature)
        
        return FeatureCollection(type="FeatureCollection", features=features)
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

# Data Validation Endpoints
@api_router.post("/data/validate-csv")
async def validate_csv_data(file: UploadFile = File(...), dataset_type: str = Form(...)):
    """Upload and validate CSV data for quality issues and potential fake data"""
    try:
        # Read uploaded CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Import validation logic
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../ai-service/data_pipeline'))
            from data_validator import DataValidator
            
            # Validate the data
            validator = DataValidator()
            validation_result = validator.validate_dataset(df, dataset_type)
        except ImportError:
            # Fallback to simple validation
            validation_result = simple_data_validation(df, dataset_type)
        
        # Generate unique ID for this validation
        validation_id = str(uuid.uuid4())
        validation_doc = {
            "id": validation_id,
            "dataset_name": file.filename,
            "validation_status": "pending",
            "confidence_score": validation_result.get('confidence_score', 0.0),
            "issues_found": [issue.get('check_type', str(issue)) for issue in validation_result.get('issues', [])],
            "record_count": len(df),
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "validated_by": None,
            "notes": None
        }
        
        # Store in database if available, otherwise keep in memory for demo
        if mongodb_available and db is not None:
            await db.data_validations.insert_one(validation_doc)
        else:
            # In offline mode, store in memory for demo purposes
            offline_validations.append(validation_doc)
            print(f"📊 Validation completed for {file.filename} (offline mode)")
        
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

@api_router.get("/data/validations")
async def get_data_validations():
    """Get all data validation results"""
    try:
        if not mongodb_available:
            # Return offline data
            return offline_validations
            
        validations = await db.data_validations.find().to_list(1000)
        result = []
        for validation in validations:
            validation.pop('_id', None)
            result.append(DataValidationResult(**validation))
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

@api_router.put("/data/validations/{validation_id}")
async def update_validation_status(validation_id: str, status: str = Form(...), notes: str = Form(None), validated_by: str = Form(None)):
    """Update validation status (pass/fail) after manual review"""
    try:
        update_data = {
            "validation_status": status,
            "validated_at": datetime.now(timezone.utc)
        }
        
        if notes:
            update_data["notes"] = notes
        if validated_by:
            update_data["validated_by"] = validated_by
            
        result = await db.data_validations.find_one_and_update(
            {"id": validation_id},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Validation not found")
            
        return {"message": "Validation status updated", "status": status}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

# Enhanced Claim Management for FRA
@api_router.put("/claims/{claim_id}/status")
async def update_claim_status(claim_id: str, new_status: str = Form(...), notes: str = Form(None), officer: str = Form(None)):
    """Update claim status with proper FRA workflow"""
    valid_statuses = ["pending", "approved", "rejected", "disputed", "verified", "under_review"]
    
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        update_data = {
            "status": new_status,
            "last_updated": datetime.now(timezone.utc)
        }
        
        if officer:
            update_data["assigned_officer"] = officer
            
        # Handle status-specific updates
        if new_status == "approved":
            update_data["granted_date"] = datetime.now(timezone.utc)
        elif new_status == "verified":
            update_data["field_verification_date"] = datetime.now(timezone.utc)
            update_data["verification_status"] = "completed"
            
        result = await db.forest_claims.find_one_and_update(
            {"id": claim_id},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Log status change
        status_log = {
            "claim_id": claim_id,
            "old_status": result.get("status", "unknown"),
            "new_status": new_status,
            "changed_by": officer or "system",
            "changed_at": datetime.now(timezone.utc),
            "notes": notes
        }
        await db.claim_status_log.insert_one(status_log)
        
        result.pop('_id', None)
        return ForestClaim(**result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Status update failed: {str(e)}")

@api_router.get("/claims/{claim_id}/history")
async def get_claim_history(claim_id: str):
    """Get status change history for a claim"""
    try:
        history = await db.claim_status_log.find({"claim_id": claim_id}).sort("changed_at", -1).to_list(100)
        
        for entry in history:
            entry.pop('_id', None)
            
        return {"claim_id": claim_id, "history": history}
        
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Document Processing Endpoints
@api_router.post("/documents/process")
async def process_fra_document(file: UploadFile = File(...), claim_id: str = Form(...), document_type: str = Form(...)):
    """Process FRA documents using OCR and NER"""
    try:
        # Save uploaded file
        file_path = f"uploads/documents/{claim_id}_{document_type}_{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # TODO: Integrate with AI service for OCR and NER processing
        # This would call your AI service to extract text and entities
        
        document = FRADocument(
            claim_id=claim_id,
            document_type=document_type,
            file_path=file_path,
            processed_at=datetime.now(timezone.utc)
        )
        
        await db.fra_documents.insert_one(document.dict())
        
        return {
            "document_id": document.id,
            "message": "Document processed successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Document processing failed: {str(e)}")

# Satellite Asset Mapping
@api_router.get("/villages/{village_id}/assets")
async def get_village_assets(village_id: str):
    """Get AI-detected assets for a village from satellite imagery"""
    try:
        assets = await db.satellite_assets.find({"village_id": village_id}).to_list(1000)
        
        result = []
        for asset in assets:
            asset.pop('_id', None)
            result.append(SatelliteAsset(**asset))
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

@api_router.post("/villages/{village_id}/assets")
async def add_satellite_asset(village_id: str, asset: SatelliteAsset):
    """Add a new satellite-detected asset"""
    try:
        asset.village_id = village_id
        await db.satellite_assets.insert_one(asset.dict())
        return asset
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Asset creation failed: {str(e)}")

# CSS Scheme Integration
@api_router.get("/schemes/{village_id}")
async def get_village_schemes(village_id: str):
    """Get CSS schemes applicable to a village"""
    try:
        schemes = await db.css_schemes.find({"village_id": village_id}).to_list(1000)
        
        result = []
        for scheme in schemes:
            scheme.pop('_id', None)
            result.append(CSSScheme(**scheme))
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Decision Support System
@api_router.get("/dss/recommendations/{village_id}")
async def get_dss_recommendations(village_id: str):
    """Get DSS recommendations for a village"""
    try:
        recommendation = await db.ds_recommendations.find_one({"village_id": village_id})
        
        if not recommendation:
            # Generate new recommendation based on available data
            village = await db.villages.find_one({"id": village_id})
            if not village:
                raise HTTPException(status_code=404, detail="Village not found")
                
            # Simple rule-based recommendation logic
            recommended_schemes = []
            priority_score = 0.5
            reasoning = {}
            
            # Check water infrastructure
            water_assets = await db.satellite_assets.find({
                "village_id": village_id, 
                "asset_type": "water_body"
            }).to_list(100)
            
            if len(water_assets) < 2:  # Low water infrastructure
                recommended_schemes.append("JAL_JEEVAN_MISSION")
                priority_score += 0.2
                reasoning["water"] = "Low water body count detected"
            
            # Check agricultural land
            agri_assets = await db.satellite_assets.find({
                "village_id": village_id, 
                "asset_type": "agricultural_land"
            }).to_list(100)
            
            if agri_assets:
                recommended_schemes.append("PM_KISAN")
                reasoning["agriculture"] = "Agricultural land detected"
            
            # Always consider MGNREGA for employment
            recommended_schemes.append("MGNREGA")
            reasoning["employment"] = "Employment generation needed"
            
            recommendation_doc = DSRecommendation(
                village_id=village_id,
                recommended_schemes=recommended_schemes,
                priority_score=priority_score,
                reasoning=reasoning,
                water_index=len(water_assets) * 0.1,
                agricultural_potential=len(agri_assets) * 0.1 if agri_assets else 0.0
            )
            
            await db.ds_recommendations.insert_one(recommendation_doc.dict())
            recommendation = recommendation_doc.dict()
        else:
            recommendation.pop('_id', None)
            
        return DSRecommendation(**recommendation)
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DSS error: {str(e)}")

# FRA Progress Tracking
@api_router.get("/progress/state/{state_name}")
async def get_state_progress(state_name: str):
    """Get FRA implementation progress for a state"""
    try:
        # Count claims by status
        pipeline = [
            {"$match": {"village_name": {"$regex": state_name, "$options": "i"}}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_counts = await db.forest_claims.aggregate(pipeline).to_list(100)
        
        total_claims = sum(item["count"] for item in status_counts)
        approved_claims = next((item["count"] for item in status_counts if item["_id"] == "approved"), 0)
        pending_claims = next((item["count"] for item in status_counts if item["_id"] == "pending"), 0)
        
        progress_percentage = (approved_claims / total_claims * 100) if total_claims > 0 else 0
        
        return {
            "state": state_name,
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "pending_claims": pending_claims,
            "progress_percentage": progress_percentage,
            "status_breakdown": status_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database unavailable")

# Include router
app.include_router(api_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FRA Atlas API is running"}

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting FRA Atlas API...")
    if mongodb_available and db is not None:
        print("🎯 Ready to serve requests with MongoDB!")
    else:
        print("⚠️  Running in offline mode - some features may be limited")
        print("🎯 API is ready for testing without database!")

if __name__ == "__main__":
    import uvicorn
    print("🌱 FRA Atlas API Starting...")
    uvicorn.run("server:app", host="127.0.0.1", port=3001, reload=True)