// Translation Service for FRA Atlas
// Uses Google Translate API for automatic translation to 100+ languages
// No hardcoded translations needed - everything translates dynamically!

class TranslationService {
  constructor() {
    this.apiEndpoints = {
      // Free Google Translate API (via public endpoint)
      google: 'https://translate.googleapis.com/translate_a/single',
      // Backup: MyMemory API (free tier: 1000 chars/day)
      mymemory: 'https://api.mymemory.translated.net/get',
      // Backup: LibreTranslate (open source)
      libretranslate: 'https://libretranslate.com/translate'
    };
    
    // All supported languages (Google Translate supports 100+)
    // ALL 22 Official Indian languages + Major Tribal languages first
    // International languages at the bottom
    this.supportedLanguages = {
      // === INDIAN LANGUAGES (22 Official + Tribal) ===
      
      // National Languages
      'en': { name: 'English', nativeName: 'English', region: 'National', googleCode: 'en' },
      'hi': { name: 'Hindi', nativeName: 'हिन्दी', region: 'National', googleCode: 'hi' },
      
      // 22 Official Indian Languages (in Devanagari alphabetical order)
      'as': { name: 'Assamese', nativeName: 'অসমীয়া', region: 'Assam', googleCode: 'as' },
      'bn': { name: 'Bengali', nativeName: 'বাংলা', region: 'West Bengal/Tripura', googleCode: 'bn' },
      'brx': { name: 'Bodo', nativeName: 'बड़ो', region: 'Assam', googleCode: 'hi', fallback: true },
      'doi': { name: 'Dogri', nativeName: 'डोगरी', region: 'Jammu & Kashmir', googleCode: 'hi', fallback: true },
      'gu': { name: 'Gujarati', nativeName: 'ગુજરાતી', region: 'Gujarat', googleCode: 'gu' },
      'kn': { name: 'Kannada', nativeName: 'ಕನ್ನಡ', region: 'Karnataka', googleCode: 'kn' },
      'ks': { name: 'Kashmiri', nativeName: 'कॉशुर / كٲشُر', region: 'Jammu & Kashmir', googleCode: 'ur', fallback: true },
      'kok': { name: 'Konkani', nativeName: 'कोंकणी', region: 'Goa/Maharashtra', googleCode: 'hi', fallback: true },
      'mai': { name: 'Maithili', nativeName: 'मैथिली', region: 'Bihar', googleCode: 'hi', fallback: true },
      'ml': { name: 'Malayalam', nativeName: 'മലയാളം', region: 'Kerala', googleCode: 'ml' },
      'mni': { name: 'Manipuri (Meitei)', nativeName: 'মৈতৈলোন্', region: 'Manipur', googleCode: 'bn', fallback: true },
      'mr': { name: 'Marathi', nativeName: 'मराठी', region: 'Maharashtra', googleCode: 'mr' },
      'ne': { name: 'Nepali', nativeName: 'नेपाली', region: 'Sikkim/West Bengal', googleCode: 'ne' },
      'or': { name: 'Odia', nativeName: 'ଓଡ଼ିଆ', region: 'Odisha', googleCode: 'or' },
      'pa': { name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', region: 'Punjab', googleCode: 'pa' },
      'sa': { name: 'Sanskrit', nativeName: 'संस्कृतम्', region: 'National', googleCode: 'sa' },
      'sat': { name: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ', region: 'Jharkhand/Odisha', googleCode: 'hi', fallback: true },
      'sd': { name: 'Sindhi', nativeName: 'سنڌي / सिन्धी', region: 'Gujarat', googleCode: 'sd' },
      'ta': { name: 'Tamil', nativeName: 'தமிழ்', region: 'Tamil Nadu', googleCode: 'ta' },
      'te': { name: 'Telugu', nativeName: 'తెలుగు', region: 'Telangana/Andhra Pradesh', googleCode: 'te' },
      'ur': { name: 'Urdu', nativeName: 'اُردُو', region: 'Jammu & Kashmir', googleCode: 'ur' },
      
      // Major Tribal Languages (Important for FRA)
      'gon': { name: 'Gondi', nativeName: 'गोंडी', region: 'MP/Chhattisgarh/Telangana', googleCode: 'hi', fallback: true },
      'kha': { name: 'Khasi', nativeName: 'খাসি', region: 'Meghalaya', googleCode: 'bn', fallback: true },
      'ho': { name: 'Ho', nativeName: 'होो', region: 'Jharkhand/Odisha', googleCode: 'hi', fallback: true },
      'mun': { name: 'Mundari', nativeName: 'मुण्डारी', region: 'Jharkhand/Odisha', googleCode: 'hi', fallback: true },
      'kur': { name: 'Kurukh (Oraon)', nativeName: 'कुड़ुख़', region: 'Jharkhand/Chhattisgarh', googleCode: 'hi', fallback: true },
      'bh': { name: 'Bhili', nativeName: 'भीली', region: 'MP/Rajasthan/Gujarat', googleCode: 'hi', fallback: true },
      'krx': { name: 'Kokborok', nativeName: 'কোকবরোক', region: 'Tripura', googleCode: 'bn', fallback: true },
      'grt': { name: 'Garo', nativeName: 'মান্দি', region: 'Meghalaya', googleCode: 'bn', fallback: true },
      
      // Other Indian Regional Languages
      'raj': { name: 'Rajasthani', nativeName: 'राजस्थानी', region: 'Rajasthan', googleCode: 'hi', fallback: true },
      'bho': { name: 'Bhojpuri', nativeName: 'भोजपुरी', region: 'Bihar/UP', googleCode: 'hi', fallback: true },
      'mag': { name: 'Magahi', nativeName: 'मगही', region: 'Bihar', googleCode: 'hi', fallback: true },
      'awa': { name: 'Awadhi', nativeName: 'अवधी', region: 'Uttar Pradesh', googleCode: 'hi', fallback: true },
      'bgc': { name: 'Haryanvi', nativeName: 'हरियाणवी', region: 'Haryana', googleCode: 'hi', fallback: true },
      'hne': { name: 'Chhattisgarhi', nativeName: 'छत्तीसगढ़ी', region: 'Chhattisgarh', googleCode: 'hi', fallback: true },
      
      // === INTERNATIONAL LANGUAGES (Bottom of Menu) ===
      'es': { name: 'Spanish', nativeName: 'Español', region: 'International', googleCode: 'es' },
      'fr': { name: 'French', nativeName: 'Français', region: 'International', googleCode: 'fr' },
      'de': { name: 'German', nativeName: 'Deutsch', region: 'International', googleCode: 'de' },
      'zh-CN': { name: 'Chinese (Simplified)', nativeName: '简体中文', region: 'International', googleCode: 'zh-CN' },
      'ja': { name: 'Japanese', nativeName: '日本語', region: 'International', googleCode: 'ja' },
      'ko': { name: 'Korean', nativeName: '한국어', region: 'International', googleCode: 'ko' },
      'pt': { name: 'Portuguese', nativeName: 'Português', region: 'International', googleCode: 'pt' },
      'ru': { name: 'Russian', nativeName: 'Русский', region: 'International', googleCode: 'ru' },
      'ar': { name: 'Arabic', nativeName: 'العربية', region: 'International', googleCode: 'ar' },
      'it': { name: 'Italian', nativeName: 'Italiano', region: 'International', googleCode: 'it' },
      'nl': { name: 'Dutch', nativeName: 'Nederlands', region: 'International', googleCode: 'nl' },
      'pl': { name: 'Polish', nativeName: 'Polski', region: 'International', googleCode: 'pl' },
      'tr': { name: 'Turkish', nativeName: 'Türkçe', region: 'International', googleCode: 'tr' },
      'vi': { name: 'Vietnamese', nativeName: 'Tiếng Việt', region: 'International', googleCode: 'vi' },
      'th': { name: 'Thai', nativeName: 'ไทย', region: 'International', googleCode: 'th' },
      'id': { name: 'Indonesian', nativeName: 'Bahasa Indonesia', region: 'International', googleCode: 'id' },
      'ms': { name: 'Malay', nativeName: 'Bahasa Melayu', region: 'International', googleCode: 'ms' },
      'fil': { name: 'Filipino', nativeName: 'Filipino', region: 'International', googleCode: 'fil' },
      'sw': { name: 'Swahili', nativeName: 'Kiswahili', region: 'International', googleCode: 'sw' },
      'uk': { name: 'Ukrainian', nativeName: 'Українська', region: 'International', googleCode: 'uk' }
    };

    // Cache for translated strings (in-memory, could use localStorage)
    this.cache = new Map();
    this.cacheExpiry = 24 * 60 * 60 * 1000; // 24 hours
    
    // Initialize cache from localStorage
    this.loadCacheFromStorage();
  }

  // Load cache from localStorage on init
  loadCacheFromStorage() {
    try {
      const stored = localStorage.getItem('translation_cache');
      if (stored) {
        const parsed = JSON.parse(stored);
        Object.entries(parsed).forEach(([key, value]) => {
          this.cache.set(key, value);
        });
      }
    } catch (error) {
      console.warn('Failed to load translation cache:', error);
    }
  }

  // Save cache to localStorage
  saveCacheToStorage() {
    try {
      const cacheObj = {};
      this.cache.forEach((value, key) => {
        cacheObj[key] = value;
      });
      localStorage.setItem('translation_cache', JSON.stringify(cacheObj));
    } catch (error) {
      console.warn('Failed to save translation cache:', error);
    }
  }

  // Main translation method - uses Google Translate API
  async translateText(text, targetLang, sourceLang = 'en') {
    // Don't translate if target is same as source
    if (targetLang === sourceLang || !text || text.trim() === '') {
      return text;
    }

    const cacheKey = `${sourceLang}-${targetLang}-${text}`;
    const cached = this.cache.get(cacheKey);
    
    // Return cached translation if available and not expired
    if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
      return cached.translation;
    }

    try {
      const targetLanguage = this.supportedLanguages[targetLang];
      const googleCode = targetLanguage?.googleCode || targetLang;
      
      // Try Google Translate first (fastest and most accurate)
      let translation = await this.callGoogleTranslateAPI(text, googleCode, sourceLang);
      
      // Add tribal language hint if it's a fallback language
      if (targetLanguage?.fallback) {
        translation = this.addTribalContext(translation, targetLang);
      }

      // Cache the successful translation
      this.cache.set(cacheKey, {
        translation,
        timestamp: Date.now()
      });

      // Persist cache to localStorage (debounced)
      this.debouncedSaveCache();

      return translation;
    } catch (error) {
      console.error('Translation failed:', error);
      return text; // Return original text on failure
    }
  }

  // Google Translate API (Free, no API key needed for basic usage)
  async callGoogleTranslateAPI(text, targetLang, sourceLang = 'en') {
    try {
      // Using the public Google Translate endpoint
      const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${sourceLang}&tl=${targetLang}&dt=t&q=${encodeURIComponent(text)}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Google Translate returns array: [[[translated, original, ...], ...], ...]
      if (data && data[0] && data[0][0] && data[0][0][0]) {
        return data[0][0][0];
      }
      
      throw new Error('Invalid response from Google Translate');
    } catch (error) {
      console.warn('Google Translate failed, trying backup:', error);
      return await this.callMyMemoryAPI(text, targetLang, sourceLang);
    }
  }

  // Fallback to MyMemory API (free, 1000 words/day limit)
  async callMyMemoryAPI(text, targetLang, sourceLang) {
    try {
      const url = `${this.apiEndpoints.mymemory}?q=${encodeURIComponent(text)}&langpair=${sourceLang}|${targetLang}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.responseData && data.responseData.translatedText) {
        return data.responseData.translatedText;
      }
      
      throw new Error('Invalid response from MyMemory');
    } catch (error) {
      console.error('All translation APIs failed:', error);
      return text; // Return original text as last resort
    }
  }

  // Debounced save to prevent excessive localStorage writes
  debouncedSaveCache() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
    this.saveTimeout = setTimeout(() => {
      this.saveCacheToStorage();
    }, 2000); // Save after 2 seconds of inactivity
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