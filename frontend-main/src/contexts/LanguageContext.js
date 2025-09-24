import React, { createContext, useContext, useState, useEffect } from 'react';
import translationService from '../services/translationService';

// Import all translation files
import enTranslations from '../translations/en.json';
import hiTranslations from '../translations/hi.json';
import tribalTranslations from '../translations/tribal.json';
import orTranslations from '../translations/or.json';
import teTranslations from '../translations/te.json';
import bnTranslations from '../translations/bn.json';
import satTranslations from '../translations/sat.json';
import gonTranslations from '../translations/gon.json';
import kokTranslations from '../translations/kok.json';

const translations = {
  en: enTranslations,
  hi: hiTranslations,
  tribal: tribalTranslations,
  or: orTranslations,
  te: teTranslations,
  bn: bnTranslations,
  sat: satTranslations,
  gon: gonTranslations,
  kok: kokTranslations
};

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
  const [dynamicTranslations, setDynamicTranslations] = useState({});
  const [isTranslating, setIsTranslating] = useState(false);

  // Get supported languages from translation service
  const supportedLanguages = translationService.getAllSupportedLanguages();

  const translate = (key) => {
    // First try local translations
    const localTranslation = translations[currentLanguage]?.[key];
    if (localTranslation) {
      return localTranslation;
    }

    // Then try dynamic translations
    const dynamicKey = `${currentLanguage}-${key}`;
    const dynamicTranslation = dynamicTranslations[dynamicKey];
    if (dynamicTranslation) {
      return dynamicTranslation;
    }

    // Fallback to English or the key itself
    return translations.en[key] || key;
  };

  const translateDynamic = async (text, targetLang = currentLanguage) => {
    if (!text || targetLang === 'en') return text;
    
    setIsTranslating(true);
    try {
      const translated = await translationService.translateText(text, targetLang, 'en');
      const dynamicKey = `${targetLang}-${text}`;
      setDynamicTranslations(prev => ({
        ...prev,
        [dynamicKey]: translated
      }));
      return translated;
    } catch (error) {
      console.error('Dynamic translation failed:', error);
      return text;
    } finally {
      setIsTranslating(false);
    }
  };

  const changeLanguage = async (language) => {
    if (translations[language] || supportedLanguages.find(lang => lang.code === language)) {
      setCurrentLanguage(language);
      console.log(`Language changed to: ${language}`);
      
      // Store language preference
      localStorage.setItem('fra-language', language);

      // Pre-load common translations for dynamic languages
      if (!translations[language] && language !== 'en') {
        await preloadTranslations(language);
      }
    }
  };

  const preloadTranslations = async (language) => {
    const commonKeys = ['welcome', 'dashboard', 'forestAtlas', 'caseManagement', 'analytics'];
    const englishTexts = commonKeys.map(key => translations.en[key]).filter(Boolean);
    
    if (englishTexts.length > 0) {
      try {
        const translatedTexts = await translationService.batchTranslate(englishTexts, language, 'en');
        const newDynamicTranslations = {};
        
        englishTexts.forEach((text, index) => {
          const dynamicKey = `${language}-${text}`;
          newDynamicTranslations[dynamicKey] = translatedTexts[index];
        });
        
        setDynamicTranslations(prev => ({
          ...prev,
          ...newDynamicTranslations
        }));
      } catch (error) {
        console.error('Preload translations failed:', error);
      }
    }
  };

  const getLanguagesByRegion = (region) => {
    return translationService.getLanguagesByRegion(region);
  };

  const clearTranslationCache = () => {
    translationService.clearCache();
    setDynamicTranslations({});
  };

  // Load saved language preference on mount
  useEffect(() => {
    const savedLanguage = localStorage.getItem('fra-language');
    if (savedLanguage && (translations[savedLanguage] || supportedLanguages.find(lang => lang.code === savedLanguage))) {
      setCurrentLanguage(savedLanguage);
    }
  }, []);

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