// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 1. Define your translations
const resources = {
  en: {
    translation: {
      "dashboard": "Dashboard",
      "srs_analyst": "SRS Analyst",
      "sign_out": "Sign out",
      "type_message": "Type your answer… (Enter to send)",
      "change_language": "عربي"
    }
  },
  ar: {
    translation: {
      "dashboard": "لوحة القيادة",
      "srs_analyst": "محلل SRS",
      "sign_out": "تسجيل خروج",
      "type_message": "اكتب إجابتك... (اضغط Enter للإرسال)",
      "change_language": "English"
    }
  }
};

i18n
  .use(LanguageDetector) // Remembers the user's choice in localStorage
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already protects from XSS
    }
  });

export default i18n;