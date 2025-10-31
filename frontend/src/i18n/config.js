import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import translationsEN from './translations/en.json';
import translationsPT from './translations/pt.json';
import translationsFR from './translations/fr.json';

// Get saved language or default to English
const savedLanguage = localStorage.getItem('fidus_language') || 'en';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: translationsEN },
      pt: { translation: translationsPT },
      fr: { translation: translationsFR }
    },
    lng: savedLanguage,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
