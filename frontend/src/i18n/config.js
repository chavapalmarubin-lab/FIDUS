import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import translationsES from './translations/es.json';
import translationsEN from './translations/en.json';
import translationsPT from './translations/pt.json';
import translationsFR from './translations/fr.json';

// Get saved language or default to Spanish (original language)
const savedLanguage = localStorage.getItem('fidus_language') || 'es';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      es: { translation: translationsES },
      en: { translation: translationsEN },
      pt: { translation: translationsPT },
      fr: { translation: translationsFR }
    },
    lng: savedLanguage,
    fallbackLng: 'es',  // Spanish as fallback since it's the original
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
