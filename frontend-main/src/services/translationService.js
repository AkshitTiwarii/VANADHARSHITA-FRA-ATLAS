// Translation Service for FRA Atlas
// Supports multiple APIs including LibreTranslate for tribal languages

class TranslationService {
  constructor() {
    this.apiEndpoints = {
      libretranslate: 'https://libretranslate.com/translate',
      mymemory: 'https://api.mymemory.translated.net/get'
    };
    
    // Language mappings for different regions and their tribal languages
    this.supportedLanguages = {
      // Indian Official Languages
      'hi': { name: 'हिन्दी', nativeName: 'हिन्दी', region: 'National' },
      'en': { name: 'English', nativeName: 'English', region: 'National' },
      
      // Regional Languages with significant tribal populations
      'or': { name: 'Odia', nativeName: 'ଓଡ଼ିଆ', region: 'Odisha' },
      'te': { name: 'Telugu', nativeName: 'తెలుగు', region: 'Telangana' },
      'bn': { name: 'Bengali', nativeName: 'বাংলা', region: 'Tripura' },
      
      // Approximations for tribal languages (using closest available languages)
      'sat': { name: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ', region: 'Odisha/MP', fallback: 'hi' },
      'ho': { name: 'Ho', nativeName: 'होो', region: 'Odisha', fallback: 'hi' },
      'mun': { name: 'Mundari', nativeName: 'मुण्डारी', region: 'Odisha', fallback: 'hi' },
      'gon': { name: 'Gondi', nativeName: 'गोंडी', region: 'MP/Telangana', fallback: 'hi' },
      'kha': { name: 'Khasi', nativeName: 'খাসি', region: 'Tripura', fallback: 'bn' },
      'kok': { name: 'Kokborok', nativeName: 'কোকবরোক', region: 'Tripura', fallback: 'bn' }
    };

    this.cache = new Map();
    this.cacheExpiry = 24 * 60 * 60 * 1000; // 24 hours
  }

  // Get cached translation or fetch new one
  async translateText(text, targetLang, sourceLang = 'en') {
    const cacheKey = `${sourceLang}-${targetLang}-${text}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
      return cached.translation;
    }

    try {
      let translation;
      
      // Handle tribal languages with fallback
      const targetLanguage = this.supportedLanguages[targetLang];
      if (targetLanguage && targetLanguage.fallback) {
        // First translate to fallback language
        translation = await this.callTranslationAPI(text, targetLanguage.fallback, sourceLang);
        
        // Add tribal language context hint
        translation = this.addTribalContext(translation, targetLang);
      } else {
        translation = await this.callTranslationAPI(text, targetLang, sourceLang);
      }

      // Cache the result
      this.cache.set(cacheKey, {
        translation,
        timestamp: Date.now()
      });

      return translation;
    } catch (error) {
      console.error('Translation failed:', error);
      return text; // Return original text on failure
    }
  }

  // Call LibreTranslate API
  async callTranslationAPI(text, targetLang, sourceLang) {
    try {
      const response = await fetch(this.apiEndpoints.libretranslate, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          q: text,
          source: sourceLang,
          target: targetLang,
          format: 'text'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.translatedText || text;
    } catch (error) {
      console.warn('LibreTranslate failed, trying MyMemory:', error);
      return await this.callMyMemoryAPI(text, targetLang, sourceLang);
    }
  }

  // Fallback to MyMemory API
  async callMyMemoryAPI(text, targetLang, sourceLang) {
    try {
      const url = `${this.apiEndpoints.mymemory}?q=${encodeURIComponent(text)}&langpair=${sourceLang}|${targetLang}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.responseData.translatedText || text;
    } catch (error) {
      console.error('MyMemory API failed:', error);
      throw error;
    }
  }

  // Add tribal language context to translation
  addTribalContext(translation, tribalLang) {
    const tribalPrefixes = {
      'sat': 'ᱥᱟᱱᱛᱟᱲᱤ: ',
      'ho': 'होो: ',
      'mun': 'मुण्डारी: ',
      'gon': 'गोंडी: ',
      'kha': 'খাসি: ',
      'kok': 'কোকবরোক: '
    };

    const prefix = tribalPrefixes[tribalLang] || '';
    return prefix + translation;
  }

  // Batch translate multiple texts
  async batchTranslate(texts, targetLang, sourceLang = 'en') {
    const promises = texts.map(text => this.translateText(text, targetLang, sourceLang));
    return await Promise.all(promises);
  }

  // Get supported languages for a region
  getLanguagesByRegion(region) {
    return Object.entries(this.supportedLanguages)
      .filter(([code, lang]) => lang.region.includes(region))
      .map(([code, lang]) => ({ code, ...lang }));
  }

  // Get all supported languages
  getAllSupportedLanguages() {
    return Object.entries(this.supportedLanguages)
      .map(([code, lang]) => ({ code, ...lang }));
  }

  // Clear translation cache
  clearCache() {
    this.cache.clear();
  }

  // Get cache size
  getCacheSize() {
    return this.cache.size;
  }
}

export default new TranslationService();