"""
Production NER Model using SpaCy with transfer learning
No training data required - uses pre-trained models + rule-based improvements
"""

import spacy
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span
import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FRANERModel:
    """
    Enhanced NER for FRA documents using SpaCy's pre-trained models
    + custom rules for domain-specific entities
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize with SpaCy model for NER
        Falls back to smaller model if preferred not available
        
        Args:
            model_name: SpaCy model ('en_core_web_sm', 'en_core_web_md', 'en_core_web_trf')
        """
        # List of models to try in order of preference
        models_to_try = [model_name, "en_core_web_sm", "en_core_web_md"]
        
        self.nlp = None
        for model in models_to_try:
            try:
                self.nlp = spacy.load(model)
                logger.info(f"Loaded SpaCy model: {model}")
                break
            except OSError:
                logger.warning(f"Model {model} not found, trying next...")
                try:
                    logger.info(f"Downloading {model}...")
                    spacy.cli.download(model)
                    self.nlp = spacy.load(model)
                    logger.info(f"Successfully loaded {model}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to download {model}: {e}")
                    continue
        
        if self.nlp is None:
            raise RuntimeError(
                "Could not load any SpaCy model. Please install manually:\n"
                "  python -m spacy download en_core_web_sm"
            )
        
        # Add custom pipeline components
        self.matcher = Matcher(self.nlp.vocab)
        self._add_custom_patterns()
        
        # Custom entity labels for FRA
        self.entity_labels = {
            'PERSON': ['holder_name', 'father_name', 'husband_name'],
            'LOC': ['village', 'district', 'state', 'tehsil'],
            'SURVEY_NO': ['survey_number', 'khasra_number', 'plot_number'],
            'AREA': ['land_area'],
            'DATE': ['application_date', 'approval_date'],
            'ORG': ['gram_sabha', 'sdlc_name'],
            'CLAIM_TYPE': ['claim_type'],
        }
    
    def _add_custom_patterns(self):
        """Add domain-specific patterns for FRA documents"""
        
        # Survey number patterns
        survey_patterns = [
            [{"TEXT": {"REGEX": r"^[0-9]+/[0-9]+$"}}],  # 123/45
            [{"TEXT": {"REGEX": r"^[0-9]+-[0-9]+$"}}],  # 123-45
            [{"LOWER": "survey"}, {"LOWER": {"IN": ["no", "number"]}}, {"IS_DIGIT": True}],
            [{"LOWER": {"IN": ["खसरा", "सर्वे"]}}, {"TEXT": {"REGEX": r"^[0-9/]+$"}}],
        ]
        self.matcher.add("SURVEY_NUMBER", survey_patterns)
        
        # Area patterns
        area_patterns = [
            [{"LIKE_NUM": True}, {"LOWER": {"IN": ["hectare", "hectares", "ha", "acre", "acres"]}}],
            [{"LIKE_NUM": True}, {"LOWER": {"IN": ["हेक्टेयर", "एकड़"]}}],
            [{"TEXT": {"REGEX": r"^[0-9]+\.[0-9]+$"}}, {"LOWER": "ha"}],
        ]
        self.matcher.add("LAND_AREA", area_patterns)
        
        # Form type patterns
        form_patterns = [
            [{"TEXT": {"REGEX": r"^FORM-[ABC]$"}}],
            [{"LOWER": "individual"}, {"LOWER": "forest"}, {"LOWER": "rights"}],
            [{"LOWER": "community"}, {"LOWER": "forest"}, {"LOWER": {"IN": ["rights", "resource"]}}],
        ]
        self.matcher.add("CLAIM_TYPE", form_patterns)
        
        # Indian state patterns
        state_patterns = [
            [{"TEXT": {"IN": ["MP", "CG", "OR", "TN", "TR"]}}],
            [{"LOWER": {"IN": ["madhya", "chhattisgarh", "odisha", "tripura", "telangana"]}}, 
             {"LOWER": "pradesh", "OP": "?"}],
        ]
        self.matcher.add("STATE", state_patterns)
    
    def extract_entities(self, text: str) -> Dict[str, any]:
        """
        Extract entities from FRA document text
        Returns structured data with confidence scores
        """
        doc = self.nlp(text)
        entities = {}
        confidence_scores = {}
        
        # Extract standard NER entities (PERSON, LOC, DATE, ORG)
        for ent in doc.ents:
            entity_type = ent.label_
            
            if entity_type == 'PERSON':
                # Determine if it's holder name or father name based on context
                context = text[max(0, ent.start_char - 30):ent.start_char].lower()
                
                if any(marker in context for marker in ['father', 'पिता', 's/o', 'son of', 'husband', 'पति']):
                    entities['father_name'] = ent.text
                    confidence_scores['father_name'] = 0.85
                elif 'holder_name' not in entities:
                    entities['holder_name'] = ent.text
                    confidence_scores['holder_name'] = 0.85
            
            elif entity_type == 'GPE' or entity_type == 'LOC':
                # Determine if village, district, or state
                context = text[max(0, ent.start_char - 20):ent.start_char].lower()
                
                if any(marker in context for marker in ['village', 'गांव', 'ग्राम']):
                    entities['village'] = ent.text
                    confidence_scores['village'] = 0.80
                elif any(marker in context for marker in ['district', 'जिला']):
                    entities['district'] = ent.text
                    confidence_scores['district'] = 0.80
                elif any(marker in context for marker in ['state', 'राज्य']):
                    entities['state'] = ent.text
                    confidence_scores['state'] = 0.75
            
            elif entity_type == 'DATE':
                if 'application_date' not in entities:
                    entities['application_date'] = ent.text
                    confidence_scores['application_date'] = 0.90
            
            elif entity_type == 'ORG':
                if 'gram sabha' in ent.text.lower() or 'ग्राम सभा' in ent.text:
                    entities['gram_sabha'] = ent.text
                    confidence_scores['gram_sabha'] = 0.75
        
        # Apply custom matchers
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            match_label = self.nlp.vocab.strings[match_id]
            
            if match_label == "SURVEY_NUMBER":
                entities['survey_number'] = span.text
                confidence_scores['survey_number'] = 0.90
            
            elif match_label == "LAND_AREA":
                # Extract numeric value
                area_text = span.text
                area_match = re.search(r'([0-9]+\.?[0-9]*)', area_text)
                if area_match:
                    entities['land_area'] = float(area_match.group(1))
                    confidence_scores['land_area'] = 0.95
            
            elif match_label == "CLAIM_TYPE":
                entities['claim_type'] = span.text
                confidence_scores['claim_type'] = 0.85
            
            elif match_label == "STATE":
                entities['state'] = span.text
                confidence_scores['state'] = 0.80
        
        # Apply regex fallbacks for critical fields
        entities, confidence_scores = self._apply_regex_fallbacks(text, entities, confidence_scores)
        
        return {
            'entities': entities,
            'confidence_scores': confidence_scores,
            'raw_ner_entities': [(ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
        }
    
    def _apply_regex_fallbacks(self, text: str, entities: Dict, confidence_scores: Dict) -> Tuple[Dict, Dict]:
        """Apply regex patterns as fallback if NER didn't find entities"""
        
        # Survey number fallback
        if 'survey_number' not in entities:
            survey_match = re.search(r'(?:survey|सर्वे|खसरा)[\s:]*(?:no|नं)?[\s:]*([0-9]+[/-]?[0-9]*)', text, re.IGNORECASE)
            if survey_match:
                entities['survey_number'] = survey_match.group(1)
                confidence_scores['survey_number'] = 0.70
        
        # Area fallback
        if 'land_area' not in entities:
            area_match = re.search(r'([0-9]+\.?[0-9]*)\s*(?:hectare|हेक्टेयर|acre|एकड़|ha)', text, re.IGNORECASE)
            if area_match:
                entities['land_area'] = float(area_match.group(1))
                confidence_scores['land_area'] = 0.75
        
        # Village fallback
        if 'village' not in entities:
            village_match = re.search(r'(?:village|गांव|ग्राम)[\s:]*([A-Za-z\s]+?)(?:\s+(?:district|जिला)|$)', text, re.IGNORECASE)
            if village_match:
                entities['village'] = village_match.group(1).strip()
                confidence_scores['village'] = 0.65
        
        # District fallback
        if 'district' not in entities:
            district_match = re.search(r'(?:district|जिला)[\s:]*([A-Za-z\s]+?)(?:\s+(?:state|राज्य)|$|,)', text, re.IGNORECASE)
            if district_match:
                entities['district'] = district_match.group(1).strip()
                confidence_scores['district'] = 0.65
        
        return entities, confidence_scores
    
    def detect_form_type(self, text: str) -> Tuple[str, float]:
        """
        Detect FRA form type (FORM-A, FORM-B, FORM-C)
        Returns (form_type, confidence)
        """
        text_lower = text.lower()
        
        # Direct form type mentions
        if 'form-a' in text_lower or 'form a' in text_lower:
            return 'FORM-A', 0.95
        if 'form-b' in text_lower or 'form b' in text_lower:
            return 'FORM-B', 0.95
        if 'form-c' in text_lower or 'form c' in text_lower:
            return 'FORM-C', 0.95
        
        # Keyword-based detection
        individual_keywords = ['individual', 'ifr', 'individual forest rights', 'व्यक्तिगत वन अधिकार']
        community_keywords = ['community', 'cfr', 'community forest rights', 'सामुदायिक वन अधिकार']
        resource_keywords = ['community forest resource', 'cfrr', 'seasonal access', 'मौसमी पहुंच']
        
        if any(kw in text_lower for kw in individual_keywords):
            return 'FORM-A', 0.75
        if any(kw in text_lower for kw in resource_keywords):
            return 'FORM-C', 0.75
        if any(kw in text_lower for kw in community_keywords):
            return 'FORM-B', 0.70
        
        # Default fallback
        return 'FORM-A', 0.50
    
    def calculate_overall_confidence(self, confidence_scores: Dict) -> float:
        """Calculate overall extraction confidence"""
        if not confidence_scores:
            return 0.0
        
        # Weighted average based on entity importance
        weights = {
            'holder_name': 0.20,
            'father_name': 0.15,
            'village': 0.20,
            'district': 0.15,
            'land_area': 0.15,
            'survey_number': 0.10,
            'application_date': 0.05
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for entity, score in confidence_scores.items():
            weight = weights.get(entity, 0.05)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5


class MultilingualOCR:
    """
    Enhanced OCR with better multilingual support using EasyOCR
    Falls back to Tesseract if EasyOCR not available
    """
    
    def __init__(self, use_easyocr: bool = True):
        self.use_easyocr = use_easyocr
        self.reader = None
        
        if use_easyocr:
            try:
                import easyocr
                self.reader = easyocr.Reader(['en', 'hi', 'or', 'te', 'bn'], gpu=False)
                logger.info("EasyOCR initialized with multilingual support")
            except Exception as e:
                logger.warning(f"EasyOCR not available, falling back to Tesseract: {e}")
                self.use_easyocr = False
    
    def extract_text(self, image_path: str, language: str = 'auto') -> Tuple[str, float]:
        """
        Extract text with confidence score
        Returns (text, average_confidence)
        """
        if self.use_easyocr and self.reader:
            return self._easyocr_extract(image_path)
        else:
            return self._tesseract_extract(image_path, language)
    
    def _easyocr_extract(self, image_path: str) -> Tuple[str, float]:
        """Extract using EasyOCR"""
        results = self.reader.readtext(image_path)
        
        if not results:
            return "", 0.0
        
        # Combine text and calculate average confidence
        text_parts = []
        confidences = []
        
        for (bbox, text, conf) in results:
            text_parts.append(text)
            confidences.append(conf)
        
        full_text = '\n'.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return full_text, avg_confidence
    
    def _tesseract_extract(self, image_path: str, language: str) -> Tuple[str, float]:
        """Extract using Tesseract (fallback)"""
        import pytesseract
        from PIL import Image
        import cv2
        
        # Preprocess image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # OCR with confidence
        lang_map = {
            'auto': 'eng+hin+ori+tel+ben',
            'en': 'eng',
            'hi': 'hin',
            'or': 'ori',
            'te': 'tel',
            'bn': 'ben'
        }
        
        tesseract_lang = lang_map.get(language, 'eng+hin')
        
        # Extract text
        text = pytesseract.image_to_string(thresh, lang=tesseract_lang, config='--oem 3 --psm 6')
        
        # Get confidence from OCR data
        data = pytesseract.image_to_data(thresh, lang=tesseract_lang, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.5
        
        return text, avg_confidence
