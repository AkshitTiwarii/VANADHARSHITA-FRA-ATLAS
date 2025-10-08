import React, { createContext, useContext, useState, useEffect } from 'react';
import translationService from '../services/translationService';

// Keep minimal English base translations for initial render
// Everything else will be translated via Google Translate API on-demand
import enTranslations from '../translations/en.json';

const LanguageContext = createContext();

export const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [apiTranslations, setApiTranslations] = useState({});
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationQueue, setTranslationQueue] = useState(new Set());

  // Get supported languages from translation service
  const supportedLanguages = translationService.getAllSupportedLanguages();

  // Smart translation function - uses API for all non-English languages
  const translate = (key) => {
    // If English, return base translation immediately
    if (currentLanguage === 'en') {
      return enTranslations[key] || key;
    }

    // Check if we have this translation cached in API translations
    const cacheKey = `${currentLanguage}-${key}`;
    if (apiTranslations[cacheKey]) {
      return apiTranslations[cacheKey];
    }

    // If not cached, queue for translation and return English temporarily
    const englishText = enTranslations[key] || key;
    
    // Queue this translation for background processing
    if (!translationQueue.has(cacheKey)) {
      setTranslationQueue(prev => new Set(prev).add(cacheKey));
      translateInBackground(englishText, key);
    }

    // Return English text while translation is pending
    return englishText;
  };

  // Background translation - doesn't block UI
  const translateInBackground = async (text, key) => {
    try {
      const translated = await translationService.translateText(text, currentLanguage, 'en');
      const cacheKey = `${currentLanguage}-${key}`;
      
      setApiTranslations(prev => ({
        ...prev,
        [cacheKey]: translated
      }));
      
      // Remove from queue
      setTranslationQueue(prev => {
        const newQueue = new Set(prev);
        newQueue.delete(cacheKey);
        return newQueue;
      });
    } catch (error) {
      console.error(`Translation failed for ${key}:`, error);
    }
  };

  // Translate dynamic text (for user-generated content, etc.)
  const translateDynamic = async (text, targetLang = currentLanguage) => {
    if (!text || targetLang === 'en') return text;
    
    setIsTranslating(true);
    try {
      const translated = await translationService.translateText(text, targetLang, 'en');
      return translated;
    } catch (error) {
      console.error('Dynamic translation failed:', error);
      return text;
    } finally {
      setIsTranslating(false);
    }
  };

  const changeLanguage = async (language) => {
    if (supportedLanguages.find(lang => lang.code === language)) {
      setCurrentLanguage(language);
      console.log(`Language changed to: ${language}`);
      
      // Store language preference
      localStorage.setItem('fra-language', language);

      // Clear API translations cache when changing language
      // New translations will be fetched as needed
      setApiTranslations({});
      setTranslationQueue(new Set());
    }
  };

  const getLanguagesByRegion = (region) => {
    return translationService.getLanguagesByRegion(region);
  };

  const clearTranslationCache = () => {
    translationService.clearCache();
    setApiTranslations({});
    setTranslationQueue(new Set());
  };

  // Load saved language preference on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('fra-language');
    if (savedLanguage && supportedLanguages.find(lang => lang.code === savedLanguage)) {
      setCurrentLanguage(savedLanguage);
    }
  }, [supportedLanguages]);

  // Trigger re-render when language changes or translations update
  useEffect(() => {
    // Force component updates when API translations are loaded
    // This ensures UI updates with new translations
  }, [apiTranslations]);

  const value = {
    currentLanguage,
    changeLanguage,
    translate,
    translateDynamic,
    getLanguagesByRegion,
    clearTranslationCache,
    supportedLanguages,
    isTranslating,
    t: translate // Short alias
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export default LanguageProvider;