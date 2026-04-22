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
      "delete_project_title": "Delete project",

      //Edit Modal
      "edit_req_title": "Edit Requirement",
      "description_label": "Description",
      "desc_placeholder": "The system shall...",
      "reason_label": "Reason for change",
      "optional": "(optional)",
      "reason_placeholder": "e.g. Clarified scope based on client feedback",
      "save_success": "Saved successfully — no conflicts detected.",
      "close": "Close",
      "save_check_conflicts": "Save & Check Conflicts",
      "version_prefix": "v",
      "Functional": "Functional",
      "Non-Functional": "Non-Functional",

      //Model Selector
      "select_model": "Select model",

      // Requirement card
      "conflict_badge": "Conflict",
      "edit_req_btn_title": "Edit requirement",

      // Interview Page
      "model_label": "Model:",
      "change_btn": "Change",
      "info_complete": "Information gathering complete.",
      "ready_generate": "Ready to generate your SRS document.",
      "generate_srs": "Generate SRS",
      "type_answer": "Type your answer… (Enter to send)",
      "message_singular": "message",
      "messages_plural": "messages",
      "reset_conv": "Reset conversation",
      "archive_confirm": "Archive this conversation? Previous requirements will remain accessible.",
      "err_generate_srs": "Failed to generate SRS",
      "err_update_model": "Failed to update model",
      "change_ai_model": "Change AI Model",
      "change_model_desc": "The selected model will be used for all future AI responses in this project.",
      "save": "Save",

      // SRS Page
      "srs_title": "Software Requirements Specification",
      "total_reqs": "total requirements",
      "continue_interview": "Continue Interview",
      "req_has_conflict_singular": "requirement has detected conflicts. Review and resolve them below.",
      "req_has_conflict_plural": "requirements have detected conflicts. Review and resolve them below.",
      "no_reqs_yet": "No {{type}} requirements yet.",
      "interview_back": "Interview",
      "functional_lower": "functional",
      "non_functional_lower": "non-functional",

      // Login Page
      "srs_analyst_subtitle": "AI-driven requirements engineering",
      "create_account_title": "Create an account",
      "sign_in_title": "Sign in to continue",
      "auth_failed": "Authentication failed. Please try again.",
      "email_label": "Email",
      "email_placeholder": "you@example.com",
      "password_label": "Password",
      "password_placeholder": "••••••••",
      "create_account_btn": "Create account",
      "sign_in_btn": "Sign in",
      "already_have_account": "Already have an account?",
      "dont_have_account": "Don't have an account?",
      "register_link": "Register"
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
      "delete_project_title": "حذف المشروع",

      // Edit Modal
      "edit_req_title": "تعديل المتطلب",
      "description_label": "الوصف",
      "desc_placeholder": "يجب على النظام أن...",
      "reason_label": "سبب التغيير",
      "optional": "(اختياري)",
      "reason_placeholder": "مثال: توضيح النطاق بناءً على ملاحظات العميل",
      "save_success": "تم الحفظ بنجاح — لم يتم اكتشاف أي تعارض.",
      "close": "إغلاق",
      "save_check_conflicts": "حفظ وفحص التعارضات",
      "version_prefix": "إصدار ",
      "Functional": "وظيفي",
      "Non-Functional": "غير وظيفي",

      // Model Selector
      "select_model": "اختر النموذج",

      // Requirement Card
      "conflict_badge": "تعارض",
      "edit_req_btn_title": "تعديل المتطلب",

      // Interview Page
      "model_label": "النموذج:",
      "change_btn": "تغيير",
      "info_complete": "اكتمل جمع المعلومات.",
      "ready_generate": "جاهز لإنشاء مستند SRS الخاص بك.",
      "generate_srs": "إنشاء SRS",
      "type_answer": "اكتب إجابتك... (اضغط Enter للإرسال)",
      "message_singular": "رسالة",
      "messages_plural": "رسائل",
      "reset_conv": "إعادة ضبط المحادثة",
      "archive_confirm": "هل تريد أرشفة هذه المحادثة؟ ستظل المتطلبات السابقة متاحة.",
      "err_generate_srs": "فشل في إنشاء SRS",
      "err_update_model": "فشل في تحديث النموذج",
      "change_ai_model": "تغيير نموذج الذكاء الاصطناعي",
      "change_model_desc": "سيتم استخدام النموذج المحدد لجميع ردود الذكاء الاصطناعي المستقبلية في هذا المشروع.",
      "save": "حفظ",

      // SRS Page
      "srs_title": "مواصفات متطلبات البرنامج",
      "total_reqs": "إجمالي المتطلبات",
      "continue_interview": "متابعة المقابلة",
      "req_has_conflict_singular": "متطلب به تعارضات مكتشفة. يرجى مراجعتها وحلها أدناه.",
      "req_has_conflict_plural": "متطلبات بها تعارضات مكتشفة. يرجى مراجعتها وحلها أدناه.",
      "no_reqs_yet": "لا توجد متطلبات {{type}} بعد.",
      "interview_back": "المقابلة",
      "functional_lower": "وظيفية",
      "non_functional_lower": "غير وظيفية",

      // Login Page
      "srs_analyst_subtitle": "هندسة المتطلبات بالذكاء الاصطناعي",
      "create_account_title": "إنشاء حساب جديد",
      "sign_in_title": "تسجيل الدخول للمتابعة",
      "auth_failed": "فشلت المصادقة. يرجى المحاولة مرة أخرى.",
      "email_label": "البريد الإلكتروني",
      "email_placeholder": "you@example.com",
      "password_label": "كلمة المرور",
      "password_placeholder": "••••••••",
      "create_account_btn": "إنشاء حساب",
      "sign_in_btn": "تسجيل الدخول",
      "already_have_account": "لديك حساب بالفعل؟",
      "dont_have_account": "ليس لديك حساب؟",
      "register_link": "تسجيل حساب جديد"
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