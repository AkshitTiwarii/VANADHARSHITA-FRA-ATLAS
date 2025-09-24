from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# Configure Tesseract path (adjust based on your system)
# For Windows, uncomment and adjust the path below:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

    def extract_text_from_image(self, image_path):
        """Extract text using OCR"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                # Fallback to original image
                processed_img = cv2.imread(image_path)
            
            # OCR configuration for better results
            custom_config = r'--oem 3 --psm 6 -l eng+hin'
            
            # Extract text
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            
            logger.info(f"Extracted text length: {len(text)}")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}")
            return ""

    def extract_entities(self, text):
        """Extract structured data from OCR text"""
        entities = {}
        
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
async def process_document(file: UploadFile = File(...)):
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
        
        logger.info(f"Processing file: {filename}")
        
        # Extract text from image
        extracted_text = processor.extract_text_from_image(file_path)
        
        if not extracted_text:
            raise HTTPException(status_code=422, detail="Could not extract text from image")
        
        # Extract structured entities
        entities = processor.extract_entities(extracted_text)
        
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
            "entities": entities,
            "validation": validation,
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
    """Analyze satellite imagery for land verification (mock implementation)"""
    
    try:
        lat = coordinates.get('latitude', 21.2514)
        lng = coordinates.get('longitude', 81.6296)
        
        # Mock satellite analysis results
        analysis_result = {
            "success": True,
            "coordinates": [lat, lng],
            "land_type": "forest_land",
            "vegetation_index": 0.75,
            "forest_cover": 85.2,
            "land_classification": {
                "dense_forest": 60.5,
                "open_forest": 24.7,
                "scrub_land": 10.3,
                "agricultural": 4.5
            },
            "change_detection": {
                "deforestation_risk": "low",
                "encroachment_detected": False,
                "last_updated": "2024-09-15"
            },
            "recommendations": [
                "Land suitable for forest rights claim",
                "No significant encroachment detected",
                "Regular monitoring recommended"
            ]
        }
        
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
            "Multi-language Support"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🤖 Starting FRA Atlas AI Service...")
    print("📄 OCR Engine: Tesseract")
    print("🛰️ Satellite Analysis: Enabled")
    print("🌐 CORS: Enabled for all origins")
    print("📊 Endpoints:")
    print("  - POST /api/process-document")
    print("  - POST /api/analyze-satellite") 
    print("  - GET /api/stats")
    print("  - GET /health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )