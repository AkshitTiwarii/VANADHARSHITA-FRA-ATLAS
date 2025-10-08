import React, { useState } from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { ChevronDown, Globe, Loader2, Home, Building2, Leaf, MapPin } from 'lucide-react';

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

  // Group languages by region - Enhanced categorization
  const regions = {
    all: 'All Languages',
    indian: 'Indian Languages',
    official: '22 Official Languages',
    tribal: 'Tribal Languages',
    National: 'National',
    International: 'International Languages'
  };

  const getFilteredLanguages = () => {
    if (selectedRegion === 'all') {
      // Show Indian languages first, then International
      const indian = supportedLanguages.filter(lang => lang.region !== 'International');
      const international = supportedLanguages.filter(lang => lang.region === 'International');
      return [...indian, ...international];
    }
    
    if (selectedRegion === 'indian') {
      return supportedLanguages.filter(lang => lang.region !== 'International');
    }
    
    if (selectedRegion === 'official') {
      // 22 official Indian languages
      const officialCodes = ['en', 'hi', 'as', 'bn', 'brx', 'doi', 'gu', 'kn', 'ks', 'kok', 
                           'mai', 'ml', 'mni', 'mr', 'ne', 'or', 'pa', 'sa', 'sat', 'sd', 'ta', 'te', 'ur'];
      return supportedLanguages.filter(lang => officialCodes.includes(lang.code));
    }
    
    if (selectedRegion === 'tribal') {
      return supportedLanguages.filter(lang => lang.fallback === true);
    }
    
    if (selectedRegion === 'International') {
      return supportedLanguages.filter(lang => lang.region === 'International');
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

  const getLanguageIcon = (language) => {
    // Get icon component based on region and language
    if (language.region === 'International') {
      return <Globe className="h-5 w-5 text-blue-600" />;
    }
    if (language.fallback) {
      return <Leaf className="h-5 w-5 text-green-600" />; // Tribal languages
    }
    if (language.region === 'National') {
      return <Home className="h-5 w-5 text-orange-600" />;
    }
    return <Building2 className="h-5 w-5 text-indigo-600" />; // Regional/Official Indian languages
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

          {/* Language List with Sections */}
          <div className="py-2">
            {getFilteredLanguages().map((language, index, array) => {
              // Add section headers
              const prevLang = array[index - 1];
              const showIndianHeader = index === 0 && selectedRegion === 'all' && language.region !== 'International';
              const showInternationalHeader = prevLang && prevLang.region !== 'International' && language.region === 'International';
              
              return (
                <React.Fragment key={language.code}>
                  {/* Section Headers */}
                  {showIndianHeader && (
                    <div className="px-4 py-2 bg-gradient-to-r from-green-50 to-blue-50 border-b border-green-100">
                      <div className="flex items-center gap-2 text-xs font-bold text-green-700">
                        <Home className="h-4 w-4" />
                        <span>INDIAN LANGUAGES</span>
                        <span className="text-green-600">({array.filter(l => l.region !== 'International').length})</span>
                      </div>
                    </div>
                  )}
                  {showInternationalHeader && (
                    <div className="px-4 py-2 bg-gradient-to-r from-gray-50 to-slate-50 border-y border-gray-200 mt-2">
                      <div className="flex items-center gap-2 text-xs font-bold text-gray-600">
                        <Globe className="h-4 w-4" />
                        <span>INTERNATIONAL LANGUAGES</span>
                        <span className="text-gray-500">({array.filter(l => l.region === 'International').length})</span>
                      </div>
                    </div>
                  )}
                  
                  {/* Language Button */}
                  <button
                    onClick={() => handleLanguageChange(language.code)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors duration-150 flex items-center space-x-3 ${
                      currentLanguage === language.code ? 'bg-blue-50 border-r-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {getLanguageIcon(language)}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-sm text-gray-900">
                        {language.nativeName}
                      </div>
                      <div className="text-xs text-gray-500">
                        {language.name}
                        {language.region && language.region !== 'International' && (
                          <span> • {language.region}</span>
                        )}
                      </div>
                      {language.fallback && (
                        <div className="text-xs text-amber-600 flex items-center gap-1 mt-0.5">
                          <Leaf className="h-3 w-3" />
                          <span>Translated via Google Translate</span>
                        </div>
                      )}
                    </div>
                    {currentLanguage === language.code && (
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <span className="text-xs text-blue-600 font-medium">Active</span>
                      </div>
                    )}
                  </button>
                </React.Fragment>
              );
            })}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-gray-100 bg-gradient-to-r from-green-50 to-blue-50">
            <div className="text-xs text-gray-700 mb-2 flex items-center gap-2 flex-wrap">
              <div className="flex items-center gap-1">
                <Leaf className="h-3 w-3 text-green-600" />
                <span>Tribal</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Building2 className="h-3 w-3 text-indigo-600" />
                <span>Official</span>
              </div>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Globe className="h-3 w-3 text-blue-600" />
                <span>International</span>
              </div>
            </div>
            <div className="text-xs text-green-700 font-medium flex items-center gap-1">
              <Globe className="h-3 w-3" />
              <span>Powered by Google Translate API</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {supportedLanguages.filter(l => l.region !== 'International').length} Indian + {' '}
              {supportedLanguages.filter(l => l.region === 'International').length} International Languages
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