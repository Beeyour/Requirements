// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 1. Define your translations
const resources = {
  en: {
    translation: {
      // Navbar (from before)
      "dashboard": "Dashboard",
      "srs_analyst": "SRS Analyst",
      "sign_out": "Sign out",
      "change_language": "عربي",
      
      // Dashboard Page
      "projects": "Projects",
      "project_singular": "project",
      "projects_plural": "projects",
      "new_project": "New Project",
      "app_name_label": "Application name",
      "app_name_placeholder": "e.g. E-commerce Platform",
      "ai_model_label": "AI Model",
      "creating": "Creating…",
      "create_start": "Create & Start Interview",
      "cancel": "Cancel",
      "loading_projects": "Loading projects…",
      "no_projects": "No projects yet",
      "no_projects_desc": "Create your first project to start an AI requirements interview.",
      "delete_title": "Delete project?",
      "delete_desc": "This will permanently delete the project, all conversations, and all requirements.",
      "delete": "Delete",

      // Project card
      "interview_btn": "Interview",
      "view_srs_btn": "View SRS",
      "req_singular": "req",
      "reqs_plural": "reqs",
      "delete_project_title": "Delete project"
    }
  },
  ar: {
    translation: {
      // Navbar (from before)
      "dashboard": "لوحة القيادة",
      "srs_analyst": "محلل SRS",
      "sign_out": "تسجيل خروج",
      "change_language": "English",
      
      // Dashboard Page
      "projects": "المشاريع",
      "project_singular": "مشروع",
      "projects_plural": "مشاريع",
      "new_project": "مشروع جديد",
      "app_name_label": "اسم التطبيق",
      "app_name_placeholder": "مثال: منصة تجارة إلكترونية",
      "ai_model_label": "نموذج الذكاء الاصطناعي",
      "creating": "جاري الإنشاء...",
      "create_start": "إنشاء وبدء المقابلة",
      "cancel": "إلغاء",
      "loading_projects": "جاري تحميل المشاريع...",
      "no_projects": "لا توجد مشاريع بعد",
      "no_projects_desc": "قم بإنشاء مشروعك الأول لبدء مقابلة المتطلبات مع الذكاء الاصطناعي.",
      "delete_title": "حذف المشروع؟",
      "delete_desc": "سيؤدي هذا إلى حذف المشروع وجميع المحادثات والمتطلبات بشكل دائم.",
      "delete": "حذف",

      // Project Card
      "interview_btn": "مقابلة",
      "view_srs_btn": "عرض SRS",
      "req_singular": "متطلب",
      "reqs_plural": "متطلبات",
      "delete_project_title": "حذف المشروع"
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