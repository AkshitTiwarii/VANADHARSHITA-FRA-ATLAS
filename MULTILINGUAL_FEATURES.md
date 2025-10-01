# FRA Atlas - Multilingual Support System

## Overview

The FRA Atlas now includes comprehensive multilingual support for tribal languages used in forest rights management across Madhya Pradesh, Tripura, Odisha, and Telangana.

## Supported Languages

### National Languages
- **English** 🇬🇧 - Primary interface language
- **Hindi** 🇮🇳 - हिन्दी - National language support

### Regional Languages
- **Odia** 🏛️ - ଓଡ଼ିଆ - Odisha regional language
- **Telugu** 🏛️ - తెలుగు - Telangana regional language  
- **Bengali** 🏛️ - বাংলা - Tripura regional language

### Tribal Languages
- **Santali** 🌿 - ᱥᱟᱱᱛᱟᱲᱤ - Odisha/MP tribal language
- **Gondi** 🌿 - गोंडी - MP/Telangana tribal language
- **Kokborok** 🌿 - কোকবরোক - Tripura tribal language

## Features

### 1. Dynamic Language Switching
- Real-time interface translation
- Region-based language filtering
- Persistent language preferences
- Smooth translation transitions

### 2. Multilingual OCR Processing
- **Auto-detection**: Automatically detects document language
- **Multi-script support**: Handles Devanagari, Odia, Telugu, Bengali, and Latin scripts
- **Language-specific optimization**: Optimized OCR engines for each script
- **Confidence scoring**: Quality assessment for extracted text

### 3. AI-Powered Translation
- **LibreTranslate Integration**: Open-source translation API
- **Fallback Support**: MyMemory API as backup
- **Tribal Language Support**: Smart fallback to regional languages
- **Context-aware Translation**: Forest rights terminology preservation

### 4. Enhanced Document Processing
- **Multilingual Entity Extraction**: Names, places, areas in any supported language
- **Cross-language Form Auto-fill**: Extracted data auto-populates forms
- **Translation Display**: Shows both original and translated text
- **Language Confidence Metrics**: Quality indicators for each process

## Technical Implementation

### Translation Service Architecture
```javascript
// services/translationService.js
- Language detection and mapping
- API endpoint management (LibreTranslate, MyMemory)
- Caching system for translations
- Tribal language fallback logic
```

### Language Context System
```javascript
// contexts/LanguageContext.js  
- React context for global language state
- Dynamic translation loading
- Regional language filtering
- Persistent user preferences
```

### Enhanced OCR Pipeline
```python
# ai-service/main.py
- Tesseract multilingual configuration
- Script-based language detection
- Quality assessment algorithms
- Translation integration
```

## Usage Guide

### For End Users

1. **Changing Interface Language**
   - Click the language selector in the header
   - Filter by region (Madhya Pradesh, Odisha, etc.)
   - Select your preferred language
   - Interface updates automatically

2. **Document Processing**
   - Upload document in any supported language
   - Select source language (or use auto-detect)
   - Choose target language for translation
   - View both original and translated results

3. **Case Management**
   - Create cases in your preferred language
   - OCR automatically translates documents
   - Form fields auto-fill with extracted data
   - All data stored with language metadata

### For Administrators

1. **Language Configuration**
   - Manage supported languages in translation service
   - Configure regional language mappings
   - Set fallback languages for tribal languages
   - Monitor translation quality metrics

2. **OCR Optimization**
   - Configure Tesseract language packs
   - Adjust confidence thresholds
   - Monitor processing performance
   - Manage translation cache

## API Endpoints

### Translation Service
```javascript
POST /api/translate
{
  "text": "Forest rights claim",
  "source": "en", 
  "target": "hi"
}
```

### Multilingual OCR
```javascript
POST /api/process-document
FormData: {
  file: document.jpg,
  language: "auto",
  target_language: "hi"
}
```

### Language Detection
```javascript
GET /api/detect-language?text=sample_text
```

## Regional Language Coverage

### Madhya Pradesh
- **Hindi**: Primary administrative language
- **Gondi**: Major tribal language (Central India)
- **Bhili**: Supported through Hindi fallback
- **Korku**: Supported through Hindi fallback

### Odisha  
- **Odia**: State language with full support
- **Santali**: Direct tribal language support
- **Ho**: Supported through Hindi fallback
- **Mundari**: Supported through Hindi fallback

### Telangana
- **Telugu**: Full regional language support
- **Gondi**: Shared with MP, full support
- **Kolam**: Supported through Telugu fallback
- **Pradhan**: Supported through Telugu fallback

### Tripura
- **Bengali**: Regional administrative language
- **Kokborok**: Primary tribal language support
- **Manipuri**: Supported through Bengali fallback
- **Halam**: Supported through Kokborok fallback

## Installation & Setup

### Prerequisites
```bash
# Install Tesseract with language packs
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-hin tesseract-ocr-ori tesseract-ocr-tel tesseract-ocr-ben
```

### Frontend Setup
```bash
npm install
# Translation service automatically loads
# Language files are pre-configured
```

### Backend Configuration
```python
# Install Python dependencies
pip install fastapi pytesseract pillow opencv-python

# Configure Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Performance Optimization

### Translation Caching
- 24-hour cache expiry for translations
- LRU cache management
- Regional translation clustering
- Persistent storage for common phrases

### OCR Processing
- Image preprocessing for better accuracy
- Language-specific configuration optimization
- Confidence-based quality filtering
- Parallel processing for batch operations

### API Rate Limiting
- LibreTranslate: Public instance rate limits
- MyMemory: 5000 characters/day free tier
- Local caching to minimize API calls
- Intelligent fallback routing

## Troubleshooting

### Common Issues

1. **Translation not working**
   - Check LibreTranslate service availability
   - Verify internet connection
   - Clear translation cache
   - Check browser console for errors

2. **OCR accuracy issues**
   - Ensure Tesseract language packs installed
   - Check image quality and resolution
   - Verify correct language selection
   - Consider manual language override

3. **Language switching problems**
   - Clear browser localStorage
   - Refresh the application
   - Check translation file integrity
   - Verify language context loading

### Error Codes
- `TRANSLATION_SERVICE_UNAVAILABLE`: API endpoint unreachable
- `UNSUPPORTED_LANGUAGE`: Language not in mapping
- `OCR_PROCESSING_FAILED`: Document processing error
- `CACHE_WRITE_ERROR`: Local storage issue

## Future Enhancements

### Planned Features
1. **Voice Input**: Speech-to-text in tribal languages
2. **Offline Translation**: Local translation models
3. **Cultural Context**: Region-specific terminology
4. **User Contributions**: Community translation improvements
5. **Advanced NLP**: Better entity extraction for tribal languages

### Language Expansion
- **Assam**: Bodo, Mising, Karbi languages
- **Jharkhand**: Additional Mundari dialects
- **Chhattisgarh**: Halbi, Gondi variants
- **West Bengal**: Santhali script support

## Support & Documentation

- **Technical Support**: Contact system administrators
- **Language Issues**: Report through feedback system  
- **Translation Quality**: Community review system
- **Feature Requests**: GitHub issues or admin panel

---

*This multilingual system enhances accessibility for tribal communities and forest rights stakeholders across India, ensuring that language is not a barrier to accessing forest rights services.*