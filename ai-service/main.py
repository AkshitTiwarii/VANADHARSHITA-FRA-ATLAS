from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
import os
import aiofiles
import logging
from datetime import datetime
import json
import hashlib
import asyncio
import requests
from typing import List, Dict
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FRA Atlas AI Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Auto-detect and configure Tesseract path
def configure_tesseract():
    """Auto-detect Tesseract installation and configure path"""
    import shutil
    import subprocess
    
    # Try to load custom config first
    try:
        from tesseract_config import TESSERACT_PATH
        if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
            logger.info(f"✅ Using configured Tesseract path: {TESSERACT_PATH}")
            try:
                result = subprocess.run([TESSERACT_PATH, '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0] if result.stdout else 'unknown'
                    logger.info(f"✅ Tesseract version: {version}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to verify configured Tesseract: {e}")
    except ImportError:
        pass
    
    # First, try to find tesseract in PATH
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        logger.info(f"✅ Tesseract found in PATH: {tesseract_path}")
        try:
            result = subprocess.run([tesseract_path, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0] if result.stdout else 'unknown'
                logger.info(f"✅ Tesseract version: {version}")
                return True
        except Exception as e:
            logger.warning(f"Failed to verify Tesseract in PATH: {e}")
    
    # If not in PATH, try common Windows installation locations
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
        r'C:\Users\Public\Tesseract-OCR\tesseract.exe',
        r'D:\Tesseract-OCR\tesseract.exe',
        r'E:\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"✅ Tesseract found at: {path}")
            # Test if it works
            try:
                result = subprocess.run([path, '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0] if result.stdout else 'unknown'
                    logger.info(f"✅ Tesseract version: {version}")
                    return True
            except Exception as e:
                logger.warning(f"Failed to verify Tesseract at {path}: {e}")
                continue
    
    logger.warning("⚠️ Tesseract not found. Using mock OCR mode.")
    logger.warning("💡 To enable real OCR:")
    logger.warning("   1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
    logger.warning("   2. Add to PATH or set path in tesseract_config.py")
    logger.warning("   3. Restart this service")
    return False

# Configure Tesseract on startup
TESSERACT_AVAILABLE = configure_tesseract()

class DocumentProcessor:
    def __init__(self):
        self.patterns = {
            'holder_name': [
                r'(?:name|holder|applicant)[\s:]*([a-zA-Z\s]+)',
                r'श्री/श्रीमती[\s:]*([^\n]+)',
                r'नाम[\s:]*([^\n]+)'
            ],
            'father_name': [
                r'(?:father|husband|पिता|पति)[\s:]*([a-zA-Z\s]+)',
                r'स/पु[\s:]*([^\n]+)',
                r'पिता का नाम[\s:]*([^\n]+)'
            ],
            'village': [
                r'(?:village|गांव|ग्राम)[\s:]*([a-zA-Z\s]+)',
                r'गांव[\s:]*([^\n]+)',
                r'ग्राम[\s:]*([^\n]+)'
            ],
            'district': [
                r'(?:district|जिला)[\s:]*([a-zA-Z\s]+)',
                r'जिला[\s:]*([^\n]+)'
            ],
            'area': [
                r'(?:area|क्षेत्र|क्षेत्रफल)[\s:]*([0-9.]+)',
                r'([0-9.]+)[\s]*(?:hectare|हेक्टेयर|एकड़)',
                r'क्षेत्रफल[\s:]*([0-9.]+)'
            ],
            'survey_number': [
                r'(?:survey|सर्वे)[\s]*(?:no|नं|number)[\s:]*([0-9/]+)',
                r'खसरा[\s]*(?:नं|संख्या)[\s:]*([0-9/]+)',
                r'सर्वे नं[\s:]*([0-9/]+)'
            ]
        }

    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image")

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to remove noise
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            return processed
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            return None

    def extract_text_from_image(self, image_path, language="auto"):
        """Extract text using OCR with multilingual support"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                # Fallback to original image
                processed_img = cv2.imread(image_path)
            
            # Language mapping for Tesseract
            language_map = {
                'auto': 'eng+hin+ori+tel+ben+san',  # Multi-language detection
                'eng': 'eng',
                'hin': 'hin',
                'ori': 'ori',  # Odia
                'tel': 'tel',  # Telugu
                'ben': 'ben',  # Bengali
                'san': 'san'   # Sanskrit
            }
            
            # Get Tesseract language parameter
            tesseract_lang = language_map.get(language, 'eng+hin')
            
            # OCR configuration for better results
            custom_config = f'--oem 3 --psm 6 -l {tesseract_lang}'
            
            # Extract text
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            
            # Detect language from extracted text
            detected_language = self.detect_language(text)
            
            logger.info(f"Extracted text length: {len(text)}, Detected language: {detected_language}")
            return text.strip(), detected_language
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return "", "unknown"

    def detect_language(self, text):
        """Simple language detection based on character patterns"""
        if not text:
            return "unknown"
        
        # Count different script characters
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        odia_chars = len(re.findall(r'[\u0B00-\u0B7F]', text))
        telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = len(text.replace(' ', ''))
        
        if total_chars == 0:
            return "unknown"
        
        # Determine dominant language
        if hindi_chars / total_chars > 0.3:
            return "hindi"
        elif odia_chars / total_chars > 0.3:
            return "odia"
        elif telugu_chars / total_chars > 0.3:
            return "telugu"
        elif bengali_chars / total_chars > 0.3:
            return "bengali"
        elif english_chars / total_chars > 0.5:
            return "english"
        else:
            return "mixed"

    def detect_form_type(self, text):
        """Detect FRA form type based on text content"""
        text_lower = text.lower()
        
        # Form-A (Individual Forest Rights) indicators
        form_a_indicators = [
            'form-a', 'form a', 'forestland', 'individual forest rights',
            'ifr', 'individual rights', 'forest land rights',
            'वन भूमि के अधिकारों', 'व्यक्तिगत वन अधिकार',
            'holder', 'claimant', 'applicant for forest rights'
        ]
        
        # Form-B (Community Rights) indicators  
        form_b_indicators = [
            'form-b', 'form b', 'community rights', 'cfr',
            'community forest rights', 'collective rights',
            'सामुदायिक अधिकार', 'सामुदायिक वन अधिकार',
            'gram sabha', 'village community', 'community claim'
        ]
        
        # Form-C (Community Forest Resource Rights) indicators
        form_c_indicators = [
            'form-c', 'form c', 'community forest resource',
            'forest resource rights', 'cfrr', 'resource rights',
            'सामुदायिक वन संसाधन अधिकार', 'वन संसाधन',
            'nistar rights', 'minor forest produce', 'mfp'
        ]
        
        # Count matches for each form type
        form_a_score = sum(1 for indicator in form_a_indicators if indicator in text_lower)
        form_b_score = sum(1 for indicator in form_b_indicators if indicator in text_lower)
        form_c_score = sum(1 for indicator in form_c_indicators if indicator in text_lower)
        
        # Additional contextual clues
        if 'individual' in text_lower and ('forest' in text_lower or 'land' in text_lower):
            form_a_score += 2
        if 'community' in text_lower and 'gram sabha' in text_lower:
            form_b_score += 2
        if 'resource' in text_lower and 'community' in text_lower:
            form_c_score += 2
            
        # Determine form type based on highest score
        max_score = max(form_a_score, form_b_score, form_c_score)
        
        if max_score == 0:
            return "Unknown", 0.0
        elif form_a_score == max_score:
            return "FORM-A", form_a_score / (form_a_score + form_b_score + form_c_score)
        elif form_b_score == max_score:
            return "FORM-B", form_b_score / (form_a_score + form_b_score + form_c_score)
        else:
            return "FORM-C", form_c_score / (form_a_score + form_b_score + form_c_score)

    def extract_entities(self, text, form_type="FORM-A"):
        """Extract structured data from OCR text based on form type"""
        entities = {}
        
        # Update patterns based on form type
        if form_type == "FORM-A":
            # Individual Forest Rights specific patterns
            self.patterns.update({
                'claimant_name': [
                    r'(?:name of claimant|claimant name|applicant name)[\s:]*([a-zA-Z\s]+)',
                    r'नाम[\s:]*([^\n]+)',
                    r'आवेदक का नाम[\s:]*([^\n]+)'
                ],
                'husband_father_name': [
                    r'(?:father|husband|spouse)[\s:]*([a-zA-Z\s]+)',
                    r'पिता/पति का नाम[\s:]*([^\n]+)',
                    r'स/पु[\s:]*([^\n]+)'
                ],
                'forest_village_name': [
                    r'(?:forest village|वन ग्राम)[\s:]*([^\n]+)',
                    r'forest village name[\s:]*([^\n]+)'
                ]
            })
        elif form_type == "FORM-B":
            # Community Rights specific patterns
            self.patterns.update({
                'gram_sabha_name': [
                    r'(?:gram sabha|ग्राम सभा)[\s:]*([^\n]+)',
                    r'name of gram sabha[\s:]*([^\n]+)'
                ],
                'community_name': [
                    r'(?:community name|समुदाय का नाम)[\s:]*([^\n]+)',
                    r'name of community[\s:]*([^\n]+)'
                ],
                'total_families': [
                    r'(?:total families|कुल परिवार)[\s:]*([0-9]+)',
                    r'number of families[\s:]*([0-9]+)'
                ]
            })
        elif form_type == "FORM-C":
            # Community Forest Resource Rights specific patterns
            self.patterns.update({
                'resource_type': [
                    r'(?:type of resource|संसाधन का प्रकार)[\s:]*([^\n]+)',
                    r'forest resource[\s:]*([^\n]+)'
                ],
                'seasonal_access': [
                    r'(?:seasonal access|मौसमी पहुंच)[\s:]*([^\n]+)',
                    r'access period[\s:]*([^\n]+)'
                ],
                'traditional_use': [
                    r'(?:traditional use|पारंपरिक उपयोग)[\s:]*([^\n]+)',
                    r'customary use[\s:]*([^\n]+)'
                ]
            })
        
        # Extract entities using patterns
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean up the extracted value
                    value = re.sub(r'[^\w\s.-]', '', value).strip()
                    if value and len(value) > 1:
                        entities[field] = value
                        break
        
        # Post-process extracted data
        if 'area' in entities:
            # Extract numeric value from area
            area_match = re.search(r'([0-9.]+)', entities['area'])
            if area_match:
                entities['area'] = float(area_match.group(1))
        
        # Generate mock coordinates for demonstration
        entities['coordinates'] = [21.2514, 81.6296]  # Chhattisgarh coordinates
        
        return entities

    def validate_extraction(self, entities):
        """Validate extracted data quality"""
        quality_score = 0
        total_fields = len(self.patterns)
        
        for field in self.patterns.keys():
            if field in entities and entities[field]:
                quality_score += 1
        
        confidence = (quality_score / total_fields) * 100
        return {
            'confidence': confidence,
            'extracted_fields': quality_score,
            'total_fields': total_fields,
            'quality': 'high' if confidence > 70 else 'medium' if confidence > 40 else 'low'
        }

processor = DocumentProcessor()

@app.get("/")
async def root():
    return {"message": "FRA Atlas AI Service", "status": "running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FRA Atlas AI Service"
    }

@app.post("/api/process-document")
async def process_document(
    file: UploadFile = File(...),
    language: str = "auto",
    target_language: str = "en"
):
    """Process uploaded document and extract forest rights claim information"""
    
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join("uploads", filename)
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Processing file: {filename} with language: {language}")
        
        # Extract text from image with language support
        extracted_text, detected_language = processor.extract_text_from_image(file_path, language)
        
        if not extracted_text:
            raise HTTPException(status_code=422, detail="Could not extract text from image")
        
        # Detect form type
        form_type, confidence = processor.detect_form_type(extracted_text)
        
        # Extract structured entities based on detected form type
        entities = processor.extract_entities(extracted_text, form_type)
        
        # Validate extraction quality
        validation = processor.validate_extraction(entities)
        
        # Clean up - remove uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        response_data = {
            "success": True,
            "message": "Document processed successfully",
            "filename": file.filename,
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "language_detected": detected_language,
            "ocr_language": language,
            "target_language": target_language,
            "form_type": form_type,
            "form_detection_confidence": confidence,
            "entities": entities,
            "validation": validation,
            "confidence_score": validation['confidence'] / 100,
            "processing_time": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully processed {filename} - Confidence: {validation['confidence']:.1f}%")
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        # Clean up file if it exists
        try:
            if 'file_path' in locals():
                os.remove(file_path)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/analyze-satellite")
async def analyze_satellite(coordinates: dict):
    """Analyze satellite imagery for land verification with realistic varying data"""
    
    try:
        lat = coordinates.get('latitude', 21.2514)
        lng = coordinates.get('longitude', 81.6296)
        
        # Generate realistic NDVI based on location
        # Use lat/lng to create variation (pseudo-random but consistent)
        import hashlib
        location_hash = hashlib.md5(f"{lat:.4f},{lng:.4f}".encode()).hexdigest()
        hash_value = int(location_hash[:8], 16) / 0xffffffff  # 0-1 range
        
        # Realistic NDVI for Central India forests (0.3-0.9 range)
        base_ndvi = 0.3 + (hash_value * 0.6)  # 0.3 to 0.9
        
        # Add slight variation based on coordinates
        lat_factor = (lat - 20) * 0.05  # Latitude variation
        ndvi = max(0.0, min(1.0, base_ndvi + lat_factor))
        
        # Calculate tree cover from NDVI (rough correlation)
        tree_cover_pct = ndvi * 100 if ndvi > 0.3 else ndvi * 50
        
        # Determine forest type
        if ndvi > 0.7:
            land_cover_type = "Dense Forest / Tree cover"
            forest_type = "Dense Sal Forest"
            deforestation_risk = "Low"
        elif ndvi > 0.5:
            land_cover_type = "Moderate Forest"
            forest_type = "Mixed Deciduous Forest"
            deforestation_risk = "Medium"
        elif ndvi > 0.3:
            land_cover_type = "Open Forest / Scrubland"
            forest_type = "Sparse Forest"
            deforestation_risk = "Medium"
        else:
            land_cover_type = "Barren / Non-forest"
            forest_type = "Non-forest"
            deforestation_risk = "High"
        
        # Enhanced satellite analysis results with correct structure
        analysis_result = {
            "success": True,
            "coordinates": {
                "lat": lat,
                "lon": lng,
                "latitude": lat,
                "longitude": lng
            },
            
            # Core vegetation metrics (matching frontend expectations)
            "ndvi": round(ndvi, 3),  # Direct number, not object!
            "tree_cover_percentage": round(tree_cover_pct, 1),
            "land_cover_type": land_cover_type,
            
            # Detailed land classification
            "land_classification": {
                "primary_type": land_cover_type,
                "forest_type": forest_type,
                "confidence": "High" if ndvi > 0.5 else "Medium"
            },
            
            # Change detection and risk
            "change_detection": {
                "deforestation_risk": deforestation_risk,
                "trend": "Stable" if ndvi > 0.5 else "Declining",
                "change_percentage": round((hash_value - 0.5) * 10, 1),
                "encroachment_detected": ndvi < 0.3,
                "vegetation_loss": max(0, round((0.5 - ndvi) * 20, 1)) if ndvi < 0.5 else 0
            },
            
            # Recommendations based on analysis
            "recommendations": [
                f"NDVI: {ndvi:.2f} - {'Healthy forest' if ndvi > 0.7 else 'Moderate vegetation' if ndvi > 0.5 else 'Sparse vegetation' if ndvi > 0.3 else 'Degraded area'}",
                f"Tree cover: {tree_cover_pct:.1f}% - {'Suitable for FRA claims' if tree_cover_pct > 40 else 'Marginal forest area'}",
                "Regular monitoring recommended" if deforestation_risk != "Low" else "Area stable, low risk"
            ],
            
            # Data quality and metadata
            "data_quality": {
                "score": 0.85,
                "status": "Good"
            },
            "metadata": {
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "date_range": "Last 6 months",
                "imagery_count": int(hash_value * 20) + 5,
                "data_source": "Satellite Analysis (Enhanced Mock)"
            }
        }
        
        logger.info(f"🛰️ Satellite analysis for ({lat}, {lng}): NDVI={ndvi:.3f}, Cover={tree_cover_pct:.1f}%")
        
        return JSONResponse(content=analysis_result)
        
    except Exception as e:
        logger.error(f"Satellite analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/stats")
async def get_processing_stats():
    """Get AI service processing statistics"""
    
    # Count processed files
    upload_files = len([f for f in os.listdir("uploads") if os.path.isfile(os.path.join("uploads", f))])
    
    return {
        "total_processed": upload_files,
        "service_uptime": "Running",
        "ocr_engine": "Tesseract 5.x",
        "supported_languages": ["English", "Hindi"],
        "supported_formats": ["JPEG", "PNG", "TIFF", "BMP"],
        "features": [
            "Document OCR",
            "Entity Extraction", 
            "Satellite Analysis",
            "Forest Monitoring",
            "Multi-language Support"
        ]
    }


# ============================================
# FOREST MONITORING ENDPOINTS
# ============================================

# Simple in-memory storage for alerts and monitoring locations
monitoring_alerts = []
monitoring_locations_db = [
    # Maharashtra - Gadchiroli District (Original + Expanded)
    {"id": "LOC-001", "village": "Bhamragad", "district": "Gadchiroli", "state": "Maharashtra", "lat": 18.9217, "lon": 77.0038, "added_date": "2025-10-01"},
    {"id": "LOC-002", "village": "Korchi", "district": "Gadchiroli", "state": "Maharashtra", "lat": 20.0931, "lon": 79.8794, "added_date": "2025-10-01"},
    {"id": "LOC-003", "village": "Dhanora", "district": "Gadchiroli", "state": "Maharashtra", "lat": 19.9503, "lon": 80.0342, "added_date": "2025-10-01"},
    {"id": "LOC-004", "village": "Aheri", "district": "Gadchiroli", "state": "Maharashtra", "lat": 19.5854, "lon": 79.9988, "added_date": "2025-10-01"},
    {"id": "LOC-005", "village": "Etapalli", "district": "Gadchiroli", "state": "Maharashtra", "lat": 19.9875, "lon": 80.0589, "added_date": "2025-10-01"},
    
    # Madhya Pradesh - Tribal Belts
    {"id": "LOC-006", "village": "Balaghat", "district": "Balaghat", "state": "Madhya Pradesh", "lat": 21.8087, "lon": 80.1869, "added_date": "2025-10-01"},
    {"id": "LOC-007", "village": "Mandla", "district": "Mandla", "state": "Madhya Pradesh", "lat": 22.5993, "lon": 80.3711, "added_date": "2025-10-01"},
    {"id": "LOC-008", "village": "Dindori", "district": "Dindori", "state": "Madhya Pradesh", "lat": 22.9414, "lon": 81.0792, "added_date": "2025-10-01"},
    {"id": "LOC-009", "village": "Jhabua", "district": "Jhabua", "state": "Madhya Pradesh", "lat": 22.7676, "lon": 74.5911, "added_date": "2025-10-01"},
    {"id": "LOC-010", "village": "Alirajpur", "district": "Alirajpur", "state": "Madhya Pradesh", "lat": 22.3045, "lon": 74.3619, "added_date": "2025-10-01"},
    {"id": "LOC-011", "village": "Betul", "district": "Betul", "state": "Madhya Pradesh", "lat": 21.9011, "lon": 77.8989, "added_date": "2025-10-01"},
    {"id": "LOC-012", "village": "Chhindwara", "district": "Chhindwara", "state": "Madhya Pradesh", "lat": 22.0576, "lon": 78.9384, "added_date": "2025-10-01"},
    
    # Odisha - Dense Forest Regions
    {"id": "LOC-013", "village": "Kalahandi", "district": "Kalahandi", "state": "Odisha", "lat": 19.9143, "lon": 83.1645, "added_date": "2025-10-01"},
    {"id": "LOC-014", "village": "Koraput", "district": "Koraput", "state": "Odisha", "lat": 18.8132, "lon": 82.7109, "added_date": "2025-10-01"},
    {"id": "LOC-015", "village": "Rayagada", "district": "Rayagada", "state": "Odisha", "lat": 19.1678, "lon": 83.4142, "added_date": "2025-10-01"},
    {"id": "LOC-016", "village": "Malkangiri", "district": "Malkangiri", "state": "Odisha", "lat": 18.3479, "lon": 81.8896, "added_date": "2025-10-01"},
    {"id": "LOC-017", "village": "Nabarangpur", "district": "Nabarangpur", "state": "Odisha", "lat": 19.2306, "lon": 82.5456, "added_date": "2025-10-01"},
    {"id": "LOC-018", "village": "Kandhamal", "district": "Kandhamal", "state": "Odisha", "lat": 20.1473, "lon": 84.1355, "added_date": "2025-10-01"},
    {"id": "LOC-019", "village": "Sundargarh", "district": "Sundargarh", "state": "Odisha", "lat": 22.1185, "lon": 84.0354, "added_date": "2025-10-01"},
    
    # Telangana - Forest Regions
    {"id": "LOC-020", "village": "Adilabad", "district": "Adilabad", "state": "Telangana", "lat": 19.6683, "lon": 78.5319, "added_date": "2025-10-01"},
    {"id": "LOC-021", "village": "Khammam", "district": "Khammam", "state": "Telangana", "lat": 17.2473, "lon": 80.1514, "added_date": "2025-10-01"},
    {"id": "LOC-022", "village": "Warangal", "district": "Warangal", "state": "Telangana", "lat": 17.9784, "lon": 79.5941, "added_date": "2025-10-01"},
    {"id": "LOC-023", "village": "Bhadradri Kothagudem", "district": "Bhadradri Kothagudem", "state": "Telangana", "lat": 17.5501, "lon": 80.6186, "added_date": "2025-10-01"},
    {"id": "LOC-024", "village": "Mancherial", "district": "Mancherial", "state": "Telangana", "lat": 18.8718, "lon": 79.4632, "added_date": "2025-10-01"},
    
    # Tripura - Forest Areas
    {"id": "LOC-025", "village": "Dhalai", "district": "Dhalai", "state": "Tripura", "lat": 23.8373, "lon": 91.9352, "added_date": "2025-10-01"},
    {"id": "LOC-026", "village": "North Tripura", "district": "North Tripura", "state": "Tripura", "lat": 23.9651, "lon": 91.9800, "added_date": "2025-10-01"},
    {"id": "LOC-027", "village": "Khowai", "district": "Khowai", "state": "Tripura", "lat": 24.0698, "lon": 91.6059, "added_date": "2025-10-01"},
    {"id": "LOC-028", "village": "Gomati", "district": "Gomati", "state": "Tripura", "lat": 23.5316, "lon": 91.4715, "added_date": "2025-10-01"},
    
    # Chhattisgarh - Critical Forest Areas
    {"id": "LOC-029", "village": "Bastar", "district": "Bastar", "state": "Chhattisgarh", "lat": 19.0757, "lon": 81.9544, "added_date": "2025-10-01"},
    {"id": "LOC-030", "village": "Dantewada", "district": "Dantewada", "state": "Chhattisgarh", "lat": 18.8932, "lon": 81.3525, "added_date": "2025-10-01"},
    {"id": "LOC-031", "village": "Kanker", "district": "Kanker", "state": "Chhattisgarh", "lat": 20.2713, "lon": 81.4932, "added_date": "2025-10-01"},
    {"id": "LOC-032", "village": "Surguja", "district": "Surguja", "state": "Chhattisgarh", "lat": 23.1190, "lon": 83.1976, "added_date": "2025-10-01"},
    
    # Jharkhand - Tribal Forest Regions
    {"id": "LOC-033", "village": "Gumla", "district": "Gumla", "state": "Jharkhand", "lat": 23.0438, "lon": 84.5383, "added_date": "2025-10-01"},
    {"id": "LOC-034", "village": "Lohardaga", "district": "Lohardaga", "state": "Jharkhand", "lat": 23.4341, "lon": 84.6805, "added_date": "2025-10-01"},
    {"id": "LOC-035", "village": "Simdega", "district": "Simdega", "state": "Jharkhand", "lat": 22.6186, "lon": 84.5022, "added_date": "2025-10-01"},
    
    # Andhra Pradesh - Forest Regions
    {"id": "LOC-036", "village": "Visakhapatnam Agency", "district": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.8041, "lon": 82.7914, "added_date": "2025-10-01"},
    {"id": "LOC-037", "village": "East Godavari", "district": "East Godavari", "state": "Andhra Pradesh", "lat": 17.2840, "lon": 81.9849, "added_date": "2025-10-01"},
    {"id": "LOC-038", "village": "Srikakulam", "district": "Srikakulam", "state": "Andhra Pradesh", "lat": 18.2949, "lon": 83.8974, "added_date": "2025-10-01"},
    
    # Western Ghats - Karnataka
    {"id": "LOC-039", "village": "Uttara Kannada", "district": "Uttara Kannada", "state": "Karnataka", "lat": 14.7951, "lon": 74.6869, "added_date": "2025-10-01"},
    {"id": "LOC-040", "village": "Kodagu", "district": "Kodagu", "state": "Karnataka", "lat": 12.4244, "lon": 75.7382, "added_date": "2025-10-01"},
    
    # Kerala - Western Ghats
    {"id": "LOC-041", "village": "Wayanad", "district": "Wayanad", "state": "Kerala", "lat": 11.6854, "lon": 76.1320, "added_date": "2025-10-01"},
    {"id": "LOC-042", "village": "Idukki", "district": "Idukki", "state": "Kerala", "lat": 9.9189, "lon": 77.0989, "added_date": "2025-10-01"},
]

# ============================================
# LOCATION MANAGEMENT ENDPOINTS
# ============================================

from pydantic import BaseModel, Field
from typing import Optional

class MonitoringLocation(BaseModel):
    village: str = Field(..., min_length=1, max_length=100)
    district: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

@app.post("/api/monitoring/locations")
async def add_monitoring_location(location: MonitoringLocation):
    """Add a new monitoring location"""
    try:
        # Generate unique ID
        location_id = f"LOC-{len(monitoring_locations_db) + 1:03d}"
        
        # Check for duplicate coordinates
        for existing in monitoring_locations_db:
            if abs(existing["lat"] - location.latitude) < 0.001 and abs(existing["lon"] - location.longitude) < 0.001:
                raise HTTPException(status_code=400, detail="Location with similar coordinates already exists")
        
        # Create new location entry
        new_location = {
            "id": location_id,
            "village": location.village,
            "district": location.district,
            "state": location.state,
            "lat": location.latitude,
            "lon": location.longitude,
            "added_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        monitoring_locations_db.append(new_location)
        
        logger.info(f"✅ Added new monitoring location: {location.village}, {location.district}")
        
        return {
            "success": True,
            "message": f"Successfully added monitoring location: {location.village}",
            "location": new_location
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error adding monitoring location: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/locations")
async def get_monitoring_locations():
    """Get all monitoring locations"""
    try:
        return {
            "success": True,
            "count": len(monitoring_locations_db),
            "locations": monitoring_locations_db
        }
    except Exception as e:
        logger.error(f"Error fetching monitoring locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/monitoring/locations/{location_id}")
async def delete_monitoring_location(location_id: str):
    """Delete a monitoring location"""
    try:
        # Find and remove location
        location_to_remove = None
        for i, loc in enumerate(monitoring_locations_db):
            if loc["id"] == location_id:
                location_to_remove = monitoring_locations_db.pop(i)
                break
        
        if not location_to_remove:
            raise HTTPException(status_code=404, detail="Location not found")
        
        logger.info(f"🗑️ Deleted monitoring location: {location_to_remove['village']}")
        
        return {
            "success": True,
            "message": f"Successfully deleted location: {location_to_remove['village']}",
            "deleted_location": location_to_remove
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting monitoring location: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MONITORING CYCLE (Updated to use dynamic locations)
# ============================================

@app.post("/api/monitoring/run-cycle")
async def run_monitoring_cycle():
    """Run forest monitoring cycle and generate alerts"""
    try:
        # Use dynamic monitoring locations from database
        monitoring_locations = [
            {"village": loc["village"], "district": loc["district"], "lat": loc["lat"], "lon": loc["lon"]}
            for loc in monitoring_locations_db
        ]
        
        if not monitoring_locations:
            return {
                "success": True,
                "cycle_completed": True,
                "alerts_generated": 0,
                "alerts": [],
                "message": "No monitoring locations configured. Please add locations first."
            }
        
        logger.info(f"🌲 Starting monitoring cycle for {len(monitoring_locations)} locations...")
        
        new_alerts = []
        
        for location in monitoring_locations:
            # Analyze each location
            lat, lon = location["lat"], location["lon"]
            
            # Use the same NDVI calculation as analyze_satellite
            import hashlib
            location_hash = hashlib.md5(f"{lat:.4f},{lon:.4f}".encode()).hexdigest()
            hash_value = int(location_hash[:8], 16) / 0xffffffff
            current_ndvi = 0.3 + (hash_value * 0.6)
            
            # Simulate previous NDVI (slightly higher for decline)
            previous_ndvi = current_ndvi + 0.15
            
            # Calculate vegetation loss
            veg_loss_pct = ((previous_ndvi - current_ndvi) / previous_ndvi) * 100 if previous_ndvi > 0 else 0
            
            # Determine risk level
            if current_ndvi < 0.3 or veg_loss_pct > 20:
                risk = "high"
            elif current_ndvi < 0.5 or veg_loss_pct > 10:
                risk = "medium"
            else:
                risk = "low"
            
            # Only create alerts for significant changes
            if veg_loss_pct > 5:
                alert = {
                    "alert_id": f"ALERT-{datetime.now().strftime('%Y%m%d')}-{len(monitoring_alerts) + len(new_alerts) + 1:04d}",
                    "village_name": location["village"],
                    "district": location["district"],
                    "state": "Maharashtra",
                    "latitude": lat,
                    "longitude": lon,
                    "ndvi_previous": round(previous_ndvi, 3),
                    "ndvi_current": round(current_ndvi, 3),
                    "vegetation_loss_percentage": round(veg_loss_pct, 1),
                    "deforestation_risk": risk,
                    "detected_date": datetime.now().isoformat(),
                    "status": "new"
                }
                new_alerts.append(alert)
                monitoring_alerts.append(alert)
        
        return {
            "success": True,
            "cycle_completed": True,
            "alerts_generated": len(new_alerts),
            "alerts": new_alerts,
            "message": f"Monitoring cycle completed. {len(new_alerts)} alerts generated."
        }
        
    except Exception as e:
        logger.error(f"Error running monitoring cycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/monitoring/alerts")
async def get_recent_alerts(limit: int = 100):
    """Get recent deforestation alerts"""
    try:
        # Return most recent alerts (limited)
        recent = monitoring_alerts[-limit:] if len(monitoring_alerts) > limit else monitoring_alerts
        
        return {
            "success": True,
            "total_alerts": len(recent),
            "alerts": recent
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/monitoring/statistics")
async def get_monitoring_statistics():
    """Get forest monitoring statistics"""
    try:
        # Calculate statistics from alerts
        total_alerts = len(monitoring_alerts)
        high_risk = sum(1 for a in monitoring_alerts if a.get("deforestation_risk") == "high")
        medium_risk = sum(1 for a in monitoring_alerts if a.get("deforestation_risk") == "medium")
        low_risk = sum(1 for a in monitoring_alerts if a.get("deforestation_risk") == "low")
        
        return {
            "success": True,
            "statistics": {
                "total_alerts": total_alerts,
                "high_risk_count": high_risk,
                "medium_risk_count": medium_risk,
                "low_risk_count": low_risk,
                "villages_monitored": 4,
                "last_monitoring_cycle": datetime.now().isoformat() if total_alerts > 0 else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/monitoring/test-alert")
async def send_test_alert():
    """Send a test alert for demonstration"""
    try:
        test_alert = {
            "alert_id": f"ALERT-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "village_name": "Bhamragad (TEST)",
            "district": "Gadchiroli",
            "state": "Maharashtra",
            "latitude": 18.9217,
            "longitude": 77.0038,
            "ndvi_previous": 0.78,
            "ndvi_current": 0.42,
            "vegetation_loss_percentage": 46.2,
            "deforestation_risk": "high",
            "detected_date": datetime.now().isoformat(),
            "status": "new"
        }
        
        monitoring_alerts.append(test_alert)
        
        return {
            "success": True,
            "message": "Test alert generated successfully",
            "alert": test_alert
        }
    except Exception as e:
        logger.error(f"Error creating test alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FRA Atlas AI Service",
        "version": "1.0.0"
    }


@app.post("/api/ocr/extract")
async def extract_ocr_data(file: UploadFile = File(...)):
    """
    Extract structured data from document images for citizen portal auto-fill.
    Optimized for Aadhaar, Voter ID, Land Records, and other ID documents.
    """
    
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp', 'application/pdf']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: JPEG, PNG, TIFF, BMP, PDF"
        )
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ocr_{timestamp}_{file.filename}"
        file_path = os.path.join("uploads", filename)
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Processing OCR extraction for: {filename}")
        
        # Use global Tesseract availability flag
        if TESSERACT_AVAILABLE:
            # Real OCR extraction using Tesseract
            try:
                extracted_text, detected_language = processor.extract_text_from_image(file_path, "auto")
                
                if not extracted_text:
                    raise ValueError("No text extracted")
                
                # Extract structured data using patterns
                extracted_data = {
                    "name": None,
                    "father_name": None,
                    "land_area": None,
                    "location": None,
                    "village": None,
                    "district": None,
                    "survey_number": None
                }
                
                # Extract name (beneficiary name)
                for pattern in processor.patterns['holder_name']:
                    match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data["name"] = match.group(1).strip()
                        break
                
                # Extract father's name
                for pattern in processor.patterns['father_name']:
                    match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data["father_name"] = match.group(1).strip()
                        break
                
                # Extract land area
                for pattern in processor.patterns['area']:
                    match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data["land_area"] = match.group(1).strip()
                        break
                
                # Extract village
                for pattern in processor.patterns['village']:
                    match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data["village"] = match.group(1).strip()
                        break
                
                # Extract district
                for pattern in processor.patterns['district']:
                    match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data["district"] = match.group(1).strip()
                        break
                
                # Extract survey number
                for pattern in processor.patterns['survey_number']:
                    match = re.search(pattern, extracted_text, re.IGNORECASE | re.MULTILINE)
                    if match:
                        extracted_data["survey_number"] = match.group(1).strip()
                        break
                
                # Build location string from village and district
                location_parts = []
                if extracted_data["village"]:
                    location_parts.append(extracted_data["village"])
                if extracted_data["district"]:
                    location_parts.append(extracted_data["district"])
                
                if location_parts:
                    extracted_data["location"] = ", ".join(location_parts)
                
                logger.info(f"OCR extraction completed with Tesseract. Extracted fields: {sum(1 for v in extracted_data.values() if v)}/7")
                
                # Clean up uploaded file
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete file {file_path}: {str(e)}")
                
                return {
                    "success": True,
                    "extracted_data": extracted_data,
                    "detected_language": detected_language,
                    "raw_text": extracted_text[:500] if extracted_text else None,
                    "mode": "tesseract"
                }
            except Exception as ocr_error:
                logger.error(f"Tesseract OCR failed: {str(ocr_error)}")
                # Fall through to mock data
        
        # Fallback: Mock data for demo/testing when Tesseract is not available
        if not TESSERACT_AVAILABLE:
            logger.warning("Using mock OCR data - Tesseract not available")
            
            # Generate realistic mock data based on filename
            import hashlib
            file_hash = hashlib.md5(filename.encode()).hexdigest()
            seed = int(file_hash[:8], 16) % 100
            
            # Sample Indian names
            names = ["राम कुमार", "सीता देवी", "मोहन लाल", "गीता शर्मा", "रवि प्रसाद"]
            father_names = ["श्याम लाल", "राधे श्याम", "बृज मोहन", "हरि प्रसाद", "राम नाथ"]
            villages = ["खरगोन", "बस्तर", "धार", "खंडवा", "सिवनी"]
            districts = ["मध्य प्रदेश", "छत्तीसगढ़", "ओडिशा", "तेलंगाना", "महाराष्ट्र"]
            
            extracted_data = {
                "name": names[seed % len(names)],
                "father_name": father_names[seed % len(father_names)],
                "land_area": f"{(seed % 5) + 0.5 + (seed % 10) * 0.1:.1f}",
                "village": villages[seed % len(villages)],
                "district": districts[seed % len(districts)],
                "survey_number": f"{100 + seed}/{seed % 10 + 1}",
                "location": f"{villages[seed % len(villages)]}, {districts[seed % len(districts)]}"
            }
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not delete file {file_path}: {str(e)}")
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "detected_language": "hin",
                "raw_text": "Mock data generated for testing. Install Tesseract for real OCR.",
                "mode": "mock",
                "warning": "Tesseract OCR not installed. Using demo data. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR extraction error: {str(e)}")
        # Clean up file on error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing document: {str(e)}"
        )


# ==================== COMPREHENSIVE DOCUMENT VERIFICATION WORKFLOW ====================

# In-memory storage for document workflow tracking
document_workflows = []
officer_reports = []

# Real-time event stream for officers
realtime_events = deque(maxlen=100)  # Keep last 100 events
active_connections: List[asyncio.Queue] = []

class DocumentWorkflowStatus:
    """Document workflow status tracking"""
    UPLOADED = "uploaded"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"
    BLOCKCHAIN_FAILED = "blockchain_failed"
    BLOCKCHAIN_VERIFIED = "blockchain_verified"
    PENDING_LOCATION_CHECK = "pending_location_check"
    LOCATION_CONTRADICTION = "location_contradiction"
    MANUAL_REVIEW = "manual_review"
    DSS_EVALUATION = "dss_evaluation"
    APPROVED = "approved"
    REJECTED = "rejected"


# ==================== REAL-TIME EVENT BROADCASTING ====================

async def broadcast_event(event_type: str, workflow_id: str, data: dict):
    """Broadcast real-time event to all connected officers"""
    event = {
        "event_type": event_type,
        "workflow_id": workflow_id,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    # Store in recent events
    realtime_events.append(event)
    
    # Broadcast to all active connections
    disconnected = []
    for queue in active_connections:
        try:
            await queue.put(event)
        except:
            disconnected.append(queue)
    
    # Remove disconnected clients
    for queue in disconnected:
        if queue in active_connections:
            active_connections.remove(queue)
    
    logger.info(f"📡 Broadcasted event: {event_type} for {workflow_id} to {len(active_connections)} officers")


async def event_generator():
    """Generate Server-Sent Events for real-time updates"""
    queue = asyncio.Queue()
    active_connections.append(queue)
    
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'event_type': 'connected', 'message': 'Real-time monitoring active', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Send recent events (last 10)
        recent = list(realtime_events)[-10:]
        for event in recent:
            yield f"data: {json.dumps(event)}\n\n"
        
        # Stream new events
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            
    except asyncio.CancelledError:
        pass
    finally:
        if queue in active_connections:
            active_connections.remove(queue)


@app.get("/api/officer/realtime-events")
async def realtime_events_stream():
    """
    Server-Sent Events endpoint for real-time workflow monitoring
    Officers can connect to this to receive live updates
    """
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/officer/recent-events")
async def get_recent_events(limit: int = 50):
    """Get recent real-time events (last 50 by default)"""
    recent = list(realtime_events)[-limit:]
    return {
        "success": True,
        "total": len(recent),
        "events": recent,
        "active_connections": len(active_connections)
    }


# ==================== END OF REAL-TIME BROADCASTING ====================

@app.post("/api/document/comprehensive-verification")
async def comprehensive_document_verification(
    file: UploadFile = File(...),
    applicant_name: str = Form(...),
    applicant_location: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    language: str = Form(default="auto")
):
    """
    Comprehensive Document Verification Workflow
    
    Flow:
    1. Upload → Blockchain verification
    2. Blockchain Fail → Report to officer
    3. Blockchain Pass → Create Hyperledger hash
    4. Status → "Pending"
    5. Location Verification → Earth Engine/Bhuvan matching
    6. Contradiction Found → Manual review
    7. No Contradiction → DSS eligibility check
    8. End → Final status update
    """
    
    workflow_id = f"WF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(document_workflows) + 1:04d}"
    
    workflow = {
        "workflow_id": workflow_id,
        "applicant_name": applicant_name,
        "applicant_location": applicant_location,
        "latitude": latitude,
        "longitude": longitude,
        "status": DocumentWorkflowStatus.UPLOADED,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "steps": [],
        "blockchain_hash": None,
        "hyperledger_hash": None,
        "location_match_score": None,
        "dss_recommendation": None,
        "final_decision": None
    }
    
    try:
        # ========== STEP 1: Save and Process Document ==========
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join("uploads", filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        workflow["steps"].append({
            "step": "document_upload",
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "filename": filename
        })
        
        # 📡 BROADCAST: Document uploaded
        await broadcast_event(
            "document_uploaded",
            workflow_id,
            {
                "applicant_name": applicant_name,
                "applicant_location": applicant_location,
                "filename": filename,
                "message": f"Document uploaded by {applicant_name}"
            }
        )
        
        # Extract text from document
        extracted_text, detected_language = processor.extract_text_from_image(file_path, language)
        form_type, confidence = processor.detect_form_type(extracted_text)
        entities = processor.extract_entities(extracted_text, form_type)
        
        workflow["document_data"] = {
            "filename": filename,
            "extracted_text": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
            "form_type": form_type,
            "confidence": confidence,
            "entities": entities
        }
        
        # ========== STEP 2: Blockchain Verification ==========
        workflow["status"] = DocumentWorkflowStatus.BLOCKCHAIN_VERIFICATION
        workflow["updated_at"] = datetime.now().isoformat()
        
        # Call blockchain service for verification
        blockchain_url = "http://localhost:8001/api/submit-verification"
        
        # 📡 BROADCAST: Starting blockchain verification
        await broadcast_event(
            "blockchain_verification_started",
            workflow_id,
            {
                "applicant_name": applicant_name,
                "document_type": form_type,
                "message": "Starting blockchain verification..."
            }
        )
        
        try:
            blockchain_response = await asyncio.to_thread(
                requests.post,
                blockchain_url,
                json={
                    "documentHash": hashlib.sha256(content).hexdigest(),
                    "applicantName": applicant_name,
                    "location": applicant_location,
                    "documentType": form_type,
                    "metadata": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "entities": entities
                    }
                },
                timeout=10
            )
            
            if blockchain_response.status_code == 200:
                blockchain_data = blockchain_response.json()
                
                # Check if blockchain verification passed
                if blockchain_data.get("verified", False):
                    workflow["status"] = DocumentWorkflowStatus.BLOCKCHAIN_VERIFIED
                    workflow["blockchain_hash"] = blockchain_data.get("transactionId")
                    
                    workflow["steps"].append({
                        "step": "blockchain_verification",
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "transaction_id": blockchain_data.get("transactionId"),
                        "block_number": blockchain_data.get("blockNumber")
                    })
                    
                    # 📡 BROADCAST: Blockchain verified
                    await broadcast_event(
                        "blockchain_verified",
                        workflow_id,
                        {
                            "transaction_id": blockchain_data.get("transactionId"),
                            "block_number": blockchain_data.get("blockNumber"),
                            "message": "✅ Blockchain verification successful"
                        }
                    )
                    
                    # ========== STEP 3: Create Hyperledger Hash ==========
                    hyperledger_hash = hashlib.sha256(
                        f"{workflow_id}-{applicant_name}-{datetime.now().isoformat()}".encode()
                    ).hexdigest()
                    
                    workflow["hyperledger_hash"] = hyperledger_hash
                    workflow["steps"].append({
                        "step": "hyperledger_hash_created",
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "hash": hyperledger_hash
                    })
                    
                    # 📡 BROADCAST: Hyperledger hash created
                    await broadcast_event(
                        "hyperledger_hash_created",
                        workflow_id,
                        {
                            "hash": hyperledger_hash[:16] + "...",
                            "message": "Hyperledger hash generated"
                        }
                    )
                    
                    # ========== STEP 4: Set Status to Pending ==========
                    workflow["status"] = DocumentWorkflowStatus.PENDING_LOCATION_CHECK
                    workflow["updated_at"] = datetime.now().isoformat()
                    
                    # 📡 BROADCAST: Status pending location check
                    await broadcast_event(
                        "status_pending_location",
                        workflow_id,
                        {
                            "message": "Awaiting location verification..."
                        }
                    )
                    
                else:
                    # Blockchain verification failed
                    workflow["status"] = DocumentWorkflowStatus.BLOCKCHAIN_FAILED
                    workflow["steps"].append({
                        "step": "blockchain_verification",
                        "status": "failed",
                        "timestamp": datetime.now().isoformat(),
                        "reason": blockchain_data.get("message", "Verification failed")
                    })
                    
                    # 📡 BROADCAST: Blockchain failed
                    await broadcast_event(
                        "blockchain_failed",
                        workflow_id,
                        {
                            "reason": blockchain_data.get("message", "Verification failed"),
                            "message": "❌ Blockchain verification failed"
                        }
                    )
                    
                    # ========== Report to Officer ==========
                    officer_report = {
                        "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(officer_reports) + 1:04d}",
                        "workflow_id": workflow_id,
                        "applicant_name": applicant_name,
                        "issue_type": "blockchain_verification_failed",
                        "details": blockchain_data.get("message", "Blockchain verification failed"),
                        "priority": "high",
                        "status": "pending_review",
                        "created_at": datetime.now().isoformat()
                    }
                    officer_reports.append(officer_report)
                    
                    workflow["officer_report_id"] = officer_report["report_id"]
                    
                    # 📡 BROADCAST: Officer report created
                    await broadcast_event(
                        "officer_report_created",
                        workflow_id,
                        {
                            "report_id": officer_report["report_id"],
                            "issue_type": "blockchain_verification_failed",
                            "message": "Report sent to officer for review"
                        }
                    )
                    
                    document_workflows.append(workflow)
                    
                    return {
                        "success": False,
                        "workflow_id": workflow_id,
                        "status": "blockchain_failed",
                        "message": "Blockchain verification failed. Reported to officer for review.",
                        "officer_report_id": officer_report["report_id"],
                        "workflow": workflow
                    }
        
        except Exception as blockchain_error:
            logger.error(f"Blockchain service error: {blockchain_error}")
            # If blockchain service is down, report to officer
            workflow["status"] = DocumentWorkflowStatus.BLOCKCHAIN_FAILED
            workflow["steps"].append({
                "step": "blockchain_verification",
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(blockchain_error)
            })
            
            officer_report = {
                "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(officer_reports) + 1:04d}",
                "workflow_id": workflow_id,
                "applicant_name": applicant_name,
                "issue_type": "blockchain_service_error",
                "details": f"Blockchain service unavailable: {str(blockchain_error)}",
                "priority": "high",
                "status": "pending_review",
                "created_at": datetime.now().isoformat()
            }
            officer_reports.append(officer_report)
            workflow["officer_report_id"] = officer_report["report_id"]
        
        # ========== STEP 5: Location Verification (Earth Engine / Bhuvan) ==========
        if workflow["status"] == DocumentWorkflowStatus.PENDING_LOCATION_CHECK:
            # 📡 BROADCAST: Starting location verification
            await broadcast_event(
                "location_verification_started",
                workflow_id,
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "message": "Analyzing satellite imagery..."
                }
            )
            
            # Analyze satellite imagery for the claimed location
            satellite_analysis = await analyze_satellite({
                "latitude": latitude,
                "longitude": longitude,
                "radius": 500
            })
            
            # Check for contradictions
            # Logic: If NDVI is too low or land type doesn't match forest, flag contradiction
            ndvi = satellite_analysis.get("ndvi", 0)
            land_type = satellite_analysis.get("land_type", "")
            
            contradiction_found = False
            contradiction_reasons = []
            
            # Check 1: NDVI too low (barren land)
            if ndvi < 0.2:
                contradiction_found = True
                contradiction_reasons.append(f"Low vegetation index (NDVI: {ndvi:.2f}). Area appears barren.")
            
            # Check 2: Non-forest land type
            if land_type.lower() not in ["forest", "dense_vegetation", "woodland"]:
                contradiction_found = True
                contradiction_reasons.append(f"Land type mismatch. Detected: {land_type}")
            
            # Check 3: Check against existing monitoring locations
            location_match_found = False
            match_score = 0
            
            for loc in monitoring_locations_db:
                # Calculate distance (simple approximation)
                loc_lat = loc["lat"]
                loc_lon = loc["lon"]
                distance = ((latitude - loc_lat) ** 2 + (longitude - loc_lon) ** 2) ** 0.5 * 111  # km
                
                if distance < 5:  # Within 5 km
                    location_match_found = True
                    match_score = max(match_score, (5 - distance) / 5 * 100)
            
            workflow["location_match_score"] = round(match_score, 2)
            workflow["satellite_analysis"] = {
                "ndvi": ndvi,
                "land_type": land_type,
                "location_match_found": location_match_found
            }
            
            workflow["steps"].append({
                "step": "location_verification",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "ndvi": ndvi,
                "land_type": land_type,
                "match_score": match_score,
                "contradiction_found": contradiction_found
            })
            
            if contradiction_found:
                # 📡 BROADCAST: Location contradiction detected
                await broadcast_event(
                    "location_contradiction",
                    workflow_id,
                    {
                        "reasons": contradiction_reasons,
                        "ndvi": ndvi,
                        "land_type": land_type,
                        "message": "⚠️ Location contradiction detected"
                    }
                )
                
                # ========== STEP 6: Manual Review Required ==========
                workflow["status"] = DocumentWorkflowStatus.MANUAL_REVIEW
                workflow["updated_at"] = datetime.now().isoformat()
                
                officer_report = {
                    "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(officer_reports) + 1:04d}",
                    "workflow_id": workflow_id,
                    "applicant_name": applicant_name,
                    "issue_type": "location_contradiction",
                    "details": " | ".join(contradiction_reasons),
                    "priority": "medium",
                    "status": "pending_review",
                    "created_at": datetime.now().isoformat(),
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "ndvi": ndvi,
                        "land_type": land_type
                    }
                }
                officer_reports.append(officer_report)
                workflow["officer_report_id"] = officer_report["report_id"]
                
                # 📡 BROADCAST: Officer report created
                await broadcast_event(
                    "officer_report_created",
                    workflow_id,
                    {
                        "report_id": officer_report["report_id"],
                        "issue_type": "location_contradiction",
                        "message": "Report sent to officer for manual review"
                    }
                )
                
                document_workflows.append(workflow)
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "status": "manual_review_required",
                    "message": "Location contradiction detected. Sent for manual review.",
                    "contradictions": contradiction_reasons,
                    "officer_report_id": officer_report["report_id"],
                    "workflow": workflow
                }
            
            else:
                # 📡 BROADCAST: Location verified
                await broadcast_event(
                    "location_verified",
                    workflow_id,
                    {
                        "ndvi": ndvi,
                        "land_type": land_type,
                        "match_score": match_score,
                        "message": "✅ Location verification successful"
                    }
                )
                
                # ========== STEP 7: DSS Eligibility Check ==========
                workflow["status"] = DocumentWorkflowStatus.DSS_EVALUATION
                workflow["updated_at"] = datetime.now().isoformat()
                
                # 📡 BROADCAST: DSS evaluation started
                await broadcast_event(
                    "dss_evaluation_started",
                    workflow_id,
                    {
                        "message": "Evaluating DSS eligibility criteria..."
                    }
                )
                
                # Simplified DSS logic
                dss_score = 0
                dss_factors = []
                
                # Factor 1: NDVI (vegetation health)
                if ndvi > 0.6:
                    dss_score += 30
                    dss_factors.append("Good vegetation health")
                elif ndvi > 0.4:
                    dss_score += 20
                    dss_factors.append("Moderate vegetation")
                else:
                    dss_score += 10
                    dss_factors.append("Low vegetation")
                
                # Factor 2: Location match
                if location_match_found:
                    dss_score += 25
                    dss_factors.append("Location within monitored forest area")
                
                # Factor 3: Document confidence
                if confidence > 0.8:
                    dss_score += 25
                    dss_factors.append("High document authenticity")
                elif confidence > 0.6:
                    dss_score += 15
                    dss_factors.append("Moderate document confidence")
                
                # Factor 4: Blockchain verified
                dss_score += 20
                dss_factors.append("Blockchain verified")
                
                # Determine eligibility
                eligible_schemes = []
                
                if dss_score >= 80:
                    eligible_schemes = ["Community Forest Rights (CFR)", "Individual Forest Rights (IFR)", "Forest Dwelling Certificate"]
                    recommendation = "Highly eligible"
                elif dss_score >= 60:
                    eligible_schemes = ["Individual Forest Rights (IFR)", "Forest Dwelling Certificate"]
                    recommendation = "Eligible with conditions"
                else:
                    eligible_schemes = []
                    recommendation = "Additional verification required"
                
                workflow["dss_recommendation"] = {
                    "score": dss_score,
                    "recommendation": recommendation,
                    "eligible_schemes": eligible_schemes,
                    "factors": dss_factors
                }
                
                workflow["steps"].append({
                    "step": "dss_evaluation",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat(),
                    "score": dss_score,
                    "recommendation": recommendation,
                    "schemes": eligible_schemes
                })
                
                # 📡 BROADCAST: DSS evaluation complete
                await broadcast_event(
                    "dss_evaluation_complete",
                    workflow_id,
                    {
                        "score": dss_score,
                        "recommendation": recommendation,
                        "eligible_schemes": eligible_schemes,
                        "message": f"DSS Score: {dss_score}/100 - {recommendation}"
                    }
                )
                
                # ========== STEP 8: Final Decision ==========
                if dss_score >= 60:
                    workflow["status"] = DocumentWorkflowStatus.APPROVED
                    workflow["final_decision"] = "approved"
                    
                    # 📡 BROADCAST: Workflow approved
                    await broadcast_event(
                        "workflow_approved",
                        workflow_id,
                        {
                            "dss_score": dss_score,
                            "eligible_schemes": eligible_schemes,
                            "message": "✅ Workflow approved! Eligible for forest rights."
                        }
                    )
                else:
                    workflow["status"] = DocumentWorkflowStatus.MANUAL_REVIEW
                    workflow["final_decision"] = "requires_review"
                    
                    # 📡 BROADCAST: Manual review required
                    await broadcast_event(
                        "workflow_manual_review",
                        workflow_id,
                        {
                            "dss_score": dss_score,
                            "message": "⚠️ Manual review required (DSS score < 60)"
                        }
                    )
                
                workflow["updated_at"] = datetime.now().isoformat()
        
        # Save workflow
        document_workflows.append(workflow)
        
        # Clean up file
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "message": "Document verification workflow completed successfully",
            "workflow": workflow,
            "blockchain_hash": workflow.get("blockchain_hash"),
            "hyperledger_hash": workflow.get("hyperledger_hash"),
            "location_match_score": workflow.get("location_match_score"),
            "dss_recommendation": workflow.get("dss_recommendation"),
            "final_decision": workflow.get("final_decision")
        }
    
    except Exception as e:
        logger.error(f"Comprehensive verification error: {str(e)}")
        
        workflow["status"] = "error"
        workflow["error"] = str(e)
        document_workflows.append(workflow)
        
        raise HTTPException(status_code=500, detail=f"Verification workflow failed: {str(e)}")


@app.get("/api/document/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get document workflow status by ID"""
    for workflow in document_workflows:
        if workflow["workflow_id"] == workflow_id:
            return {
                "success": True,
                "workflow": workflow
            }
    
    raise HTTPException(status_code=404, detail="Workflow not found")


@app.get("/api/document/workflows")
async def get_all_workflows(
    status: str = None,
    limit: int = 50
):
    """Get all document workflows with optional status filter"""
    filtered_workflows = document_workflows
    
    if status:
        filtered_workflows = [w for w in document_workflows if w["status"] == status]
    
    return {
        "success": True,
        "total": len(filtered_workflows),
        "workflows": filtered_workflows[-limit:]
    }


@app.get("/api/officer/reports")
async def get_officer_reports(
    status: str = None,
    priority: str = None,
    limit: int = 50
):
    """Get officer reports with optional filters"""
    filtered_reports = officer_reports
    
    if status:
        filtered_reports = [r for r in filtered_reports if r["status"] == status]
    
    if priority:
        filtered_reports = [r for r in filtered_reports if r["priority"] == priority]
    
    return {
        "success": True,
        "total": len(filtered_reports),
        "reports": filtered_reports[-limit:]
    }


@app.post("/api/officer/report/{report_id}/resolve")
async def resolve_officer_report(
    report_id: str,
    resolution: str,
    action_taken: str
):
    """Resolve an officer report"""
    for report in officer_reports:
        if report["report_id"] == report_id:
            report["status"] = "resolved"
            report["resolution"] = resolution
            report["action_taken"] = action_taken
            report["resolved_at"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "Report resolved successfully",
                "report": report
            }
    
    raise HTTPException(status_code=404, detail="Report not found")


# ==================== END OF DOCUMENT VERIFICATION WORKFLOW ====================


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Fix Unicode encoding for Windows console
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    print("Starting FRA Atlas AI Service...")
    print(f"OCR Engine: {'Tesseract (Real OCR)' if TESSERACT_AVAILABLE else 'Mock Mode (Tesseract not found)'}")
    print("Satellite Analysis: Enabled")
    print("Forest Monitoring: Enabled")
    print("Blockchain Integration: Enabled")
    print("CORS: Enabled for all origins")
    print("Real-time Officer Monitoring: Enabled (SSE)")
    print("")
    print("Document Processing Endpoints:")
    print("  - POST /api/process-document (Basic document processing)")
    print("  - POST /api/ocr/extract (Citizen Portal Auto-fill)")
    print("  - POST /api/document/comprehensive-verification (Full workflow)")
    print("  - GET  /api/document/workflow/{workflow_id}")
    print("  - GET  /api/document/workflows")
    print("")
    print("Satellite & Monitoring:")
    print("  - POST /api/analyze-satellite")
    print("  - POST /api/monitoring/run-cycle")
    print("  - GET  /api/monitoring/alerts")
    print("  - GET  /api/monitoring/statistics")
    print("  - POST /api/monitoring/test-alert")
    print("")
    print("Officer Reports:")
    print("  - GET  /api/officer/reports")
    print("  - POST /api/officer/report/{report_id}/resolve")
    print("")
    print("Real-time Monitoring (NEW):")
    print("  - GET  /api/officer/realtime-events (SSE Stream)")
    print("  - GET  /api/officer/recent-events (Event History)")
    print("")
    print("System:")
    print("  - GET  /api/stats")
    print("  - GET  /health")
    print("")
    print("Server running on http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Real-time Dashboard: officer_realtime_dashboard.html")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )