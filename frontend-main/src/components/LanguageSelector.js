import React, { useState } from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { ChevronDown, Globe, Loader2 } from 'lucide-react';

const LanguageSelector = () => {
  const { 
    currentLanguage, 
    changeLanguage, 
    supportedLanguages, 
    getLanguagesByRegion,
    isTranslating,
    t 
  } = useTranslation();
  
  const [isOpen, setIsOpen] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState('all');

  // Group languages by region
  const regions = {
    all: 'All Languages',
    National: 'National Languages',
    'Madhya Pradesh': 'Madhya Pradesh',
    'Odisha': 'Odisha',
    'Telangana': 'Telangana',
    'Tripura': 'Tripura'
  };

  const getFilteredLanguages = () => {
    if (selectedRegion === 'all') {
      return supportedLanguages;
    }
    return getLanguagesByRegion(selectedRegion);
  };

  const handleLanguageChange = async (langCode) => {
    await changeLanguage(langCode);
    setIsOpen(false);
  };

  const getCurrentLanguageName = () => {
    const current = supportedLanguages.find(lang => lang.code === currentLanguage);
    return current ? current.nativeName : 'English';
  };

  const getLanguageIcon = (langCode) => {
    const iconMap = {
      'en': '🇬🇧',
      'hi': '🇮🇳',
      'or': '🏛️',
      'te': '🏛️',
      'bn': '🏛️',
      'sat': '🌿',
      'gon': '🌿',
      'kok': '🌿',
      'ho': '🌿',
      'mun': '🌿',
      'kha': '🌿'
    };
    return iconMap[langCode] || '🗣️';
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 min-w-[160px]"
        disabled={isTranslating}
      >
        {isTranslating ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Globe className="h-4 w-4" />
        )}
        <span className="text-sm font-medium">
          {getCurrentLanguageName()}
        </span>
        <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[280px] max-h-96 overflow-y-auto">
          {/* Region Filter */}
          <div className="p-3 border-b border-gray-100">
            <label className="block text-xs font-medium text-gray-700 mb-2">
              Filter by Region:
            </label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full text-xs border border-gray-200 rounded px-2 py-1 bg-white"
            >
              {Object.entries(regions).map(([key, name]) => (
                <option key={key} value={key}>{name}</option>
              ))}
            </select>
          </div>

          {/* Language List */}
          <div className="py-2">
            {getFilteredLanguages().map((language) => (
              <button
                key={language.code}
                onClick={() => handleLanguageChange(language.code)}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors duration-150 flex items-center space-x-3 ${
                  currentLanguage === language.code ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                }`}
              >
                <span className="text-lg">
                  {getLanguageIcon(language.code)}
                </span>
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900">
                    {language.nativeName}
                  </div>
                  <div className="text-xs text-gray-500">
                    {language.name} • {language.region}
                  </div>
                  {language.fallback && (
                    <div className="text-xs text-amber-600">
                      Via {supportedLanguages.find(l => l.code === language.fallback)?.name}
                    </div>
                  )}
                </div>
                {currentLanguage === language.code && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                )}
              </button>
            ))}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-gray-100 bg-gray-50">
            <div className="text-xs text-gray-600 mb-2">
              🌿 = Tribal Languages • 🏛️ = Regional Languages
            </div>
            <div className="text-xs text-gray-500">
              Translation powered by LibreTranslate
            </div>
          </div>
        </div>
      )}

      {/* Click overlay to close */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default LanguageSelector;