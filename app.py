import os
import sqlite3
import json
import time
import hashlib
import secrets
import re
import logging
from datetime import datetime, timedelta
from threading import Thread
from functools import lru_cache
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session, send_file, g
from email_validator import validate_email, EmailNotValidError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path
import shutil

# ================== إعدادات التطبيق ==================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_pro_enterprise_2024_v5_secure_key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

port = int(os.environ.get("PORT", 10000))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

print("=" * 80)
print("InvoiceFlow Pro - نظام إدارة الفواتير الاحترافي")
print("الإصدار النهائي المتكامل v5.0 - جاهز للإنتاج")
print("=" * 80)

# ================== نظام تعدد اللغات المتقدم ==================
class LanguageManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.translations = {
            'ar': {
                # العناوين الرئيسية
                'app_name': 'InvoiceFlow Pro',
                'app_subtitle': 'نظام إدارة الفواتير الاحترافي',
                'dashboard': 'لوحة التحكم',
                'invoices': 'الفواتير',
                'clients': 'العملاء',
                'reports': 'التقارير',
                'settings': 'الإعدادات',
                'admin': 'الإدارة',
                'profile': 'الملف الشخصي',
                'logout': 'تسجيل خروج',
                'login': 'تسجيل الدخول',
                'register': 'إنشاء حساب',
                
                # النماذج
                'username': 'اسم المستخدم',
                'email': 'البريد الإلكتروني',
                'password': 'كلمة المرور',
                'confirm_password': 'تأكيد كلمة المرور',
                'full_name': 'الاسم الكامل',
                'company_name': 'اسم الشركة',
                'phone': 'رقم الهاتف',
                'address': 'العنوان',
                'submit': 'إرسال',
                'cancel': 'إلغاء',
                'save': 'حفظ',
                'delete': 'حذف',
                'edit': 'تعديل',
                'view': 'عرض',
                'search': 'بحث',
                'filter': 'فلترة',
                
                # الفواتير
                'new_invoice': 'فاتورة جديدة',
                'invoice_number': 'رقم الفاتورة',
                'client_name': 'اسم العميل',
                'issue_date': 'تاريخ الإصدار',
                'due_date': 'تاريخ الاستحقاق',
                'total_amount': 'المبلغ الإجمالي',
                'status': 'الحالة',
                'payment_status': 'حالة الدفع',
                'subtotal': 'المجموع الفرعي',
                'tax': 'الضريبة',
                'discount': 'الخصم',
                'notes': 'ملاحظات',
                'payment_terms': 'شروط الدفع',
                'services': 'الخدمات',
                'service_name': 'اسم الخدمة',
                'quantity': 'الكمية',
                'unit_price': 'سعر الوحدة',
                'add_service': 'إضافة خدمة',
                'remove_service': 'حذف الخدمة',
                'generate_pdf': 'إنشاء PDF',
                'download_pdf': 'تحميل PDF',
                'send_invoice': 'إرسال الفاتورة',
                
                # الحالات
                'draft': 'مسودة',
                'pending': 'معلقة',
                'paid': 'مسددة',
                'overdue': 'متأخرة',
                'cancelled': 'ملغاة',
                'unpaid': 'غير مدفوع',
                
                # الإحصائيات
                'total_invoices': 'إجمالي الفواتير',
                'total_revenue': 'إجمالي الإيرادات',
                'pending_invoices': 'فواتير معلقة',
                'paid_amount': 'المبلغ المسدد',
                'tax_amount': 'مبلغ الضريبة',
                'average_invoice': 'متوسط الفاتورة',
                'growth_rate': 'معدل النمو',
                'collection_efficiency': 'كفاءة التحصيل',
                
                # التقارير
                'financial_report': 'التقرير المالي',
                'tax_report': 'التقرير الضريبي',
                'client_report': 'تقرير العملاء',
                'monthly_report': 'التقرير الشهري',
                'yearly_report': 'التقرير السنوي',
                'export_report': 'تصدير التقرير',
                'advanced_reports': 'تقارير متقدمة',
                
                # الإعدادات
                'general_settings': 'الإعدادات العامة',
                'appearance': 'المظهر',
                'language': 'اللغة',
                'currency': 'العملة',
                'tax_rate': 'نسبة الضريبة',
                'theme': 'السمة',
                'notifications': 'الإشعارات',
                'backup': 'النسخ الاحتياطي',
                'security': 'الأمان',
                
                # الرسائل
                'welcome': 'مرحباً',
                'success': 'تم بنجاح',
                'error': 'خطأ',
                'warning': 'تحذير',
                'info': 'معلومات',
                'confirm': 'تأكيد',
                'loading': 'جاري التحميل...',
                'no_data': 'لا توجد بيانات',
                'no_invoices': 'لا توجد فواتير',
                'no_clients': 'لا يوجد عملاء',
                'login_success': 'تم تسجيل الدخول بنجاح',
                'login_failed': 'فشل تسجيل الدخول',
                'invalid_credentials': 'بيانات الدخول غير صحيحة',
                'account_created': 'تم إنشاء الحساب بنجاح',
                'invoice_created': 'تم إنشاء الفاتورة بنجاح',
                'invoice_updated': 'تم تحديث الفاتورة بنجاح',
                'invoice_deleted': 'تم حذف الفاتورة',
                'client_added': 'تم إضافة العميل بنجاح',
                'settings_saved': 'تم حفظ الإعدادات',
                'backup_created': 'تم إنشاء النسخة الاحتياطية',
                
                # الذكاء الاصطناعي
                'ai_assistant': 'المساعد الذكي',
                'ai_analysis': 'تحليل ذكي',
                'ai_recommendations': 'توصيات ذكية',
                'ai_predictions': 'تنبؤات',
                'performance_analysis': 'تحليل الأداء',
                
                # الأزرار والإجراءات
                'quick_actions': 'إجراءات سريعة',
                'view_all': 'عرض الكل',
                'create_new': 'إنشاء جديد',
                'export': 'تصدير',
                'import': 'استيراد',
                'print': 'طباعة',
                'refresh': 'تحديث',
                'back': 'رجوع',
                'next': 'التالي',
                'previous': 'السابق',
                
                # الوقت
                'today': 'اليوم',
                'yesterday': 'أمس',
                'this_week': 'هذا الأسبوع',
                'this_month': 'هذا الشهر',
                'this_year': 'هذه السنة',
                'uptime': 'وقت التشغيل',
                'hours': 'ساعة',
                'minutes': 'دقيقة',
                
                # الأمان
                'secure_connection': 'اتصال آمن ومشفر',
                'system_admin': 'مدير النظام',
                'ip_blocked': 'تم حظر عنوان IP',
                'too_many_attempts': 'محاولات كثيرة جداً',
                
                # العملاء
                'add_client': 'إضافة عميل',
                'client_details': 'تفاصيل العميل',
                'client_history': 'سجل العميل',
                'top_clients': 'أفضل العملاء',
                
                # النسخ الاحتياطي
                'create_backup': 'إنشاء نسخة احتياطية',
                'restore_backup': 'استعادة نسخة احتياطية',
                'auto_backup': 'نسخ احتياطي تلقائي',
                'backup_history': 'سجل النسخ الاحتياطية',
                
                # Footer
                'all_rights_reserved': 'جميع الحقوق محفوظة',
                'version': 'الإصدار',
                'contact_us': 'اتصل بنا',
                'help': 'المساعدة',
                
                # Misc
                'overview': 'نظرة عامة',
                'details': 'التفاصيل',
                'description': 'الوصف',
                'category': 'الفئة',
                'active': 'نشط',
                'inactive': 'غير نشط',
                'yes': 'نعم',
                'no': 'لا',
                'or': 'أو',
                'and': 'و',
                'from': 'من',
                'to': 'إلى',
                'total': 'الإجمالي',
            },
            'en': {
                # Main titles
                'app_name': 'InvoiceFlow Pro',
                'app_subtitle': 'Professional Invoice Management System',
                'dashboard': 'Dashboard',
                'invoices': 'Invoices',
                'clients': 'Clients',
                'reports': 'Reports',
                'settings': 'Settings',
                'admin': 'Admin',
                'profile': 'Profile',
                'logout': 'Logout',
                'login': 'Login',
                'register': 'Register',
                
                # Forms
                'username': 'Username',
                'email': 'Email',
                'password': 'Password',
                'confirm_password': 'Confirm Password',
                'full_name': 'Full Name',
                'company_name': 'Company Name',
                'phone': 'Phone',
                'address': 'Address',
                'submit': 'Submit',
                'cancel': 'Cancel',
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'view': 'View',
                'search': 'Search',
                'filter': 'Filter',
                
                # Invoices
                'new_invoice': 'New Invoice',
                'invoice_number': 'Invoice Number',
                'client_name': 'Client Name',
                'issue_date': 'Issue Date',
                'due_date': 'Due Date',
                'total_amount': 'Total Amount',
                'status': 'Status',
                'payment_status': 'Payment Status',
                'subtotal': 'Subtotal',
                'tax': 'Tax',
                'discount': 'Discount',
                'notes': 'Notes',
                'payment_terms': 'Payment Terms',
                'services': 'Services',
                'service_name': 'Service Name',
                'quantity': 'Quantity',
                'unit_price': 'Unit Price',
                'add_service': 'Add Service',
                'remove_service': 'Remove Service',
                'generate_pdf': 'Generate PDF',
                'download_pdf': 'Download PDF',
                'send_invoice': 'Send Invoice',
                
                # Statuses
                'draft': 'Draft',
                'pending': 'Pending',
                'paid': 'Paid',
                'overdue': 'Overdue',
                'cancelled': 'Cancelled',
                'unpaid': 'Unpaid',
                
                # Statistics
                'total_invoices': 'Total Invoices',
                'total_revenue': 'Total Revenue',
                'pending_invoices': 'Pending Invoices',
                'paid_amount': 'Paid Amount',
                'tax_amount': 'Tax Amount',
                'average_invoice': 'Average Invoice',
                'growth_rate': 'Growth Rate',
                'collection_efficiency': 'Collection Efficiency',
                
                # Reports
                'financial_report': 'Financial Report',
                'tax_report': 'Tax Report',
                'client_report': 'Client Report',
                'monthly_report': 'Monthly Report',
                'yearly_report': 'Yearly Report',
                'export_report': 'Export Report',
                'advanced_reports': 'Advanced Reports',
                
                # Settings
                'general_settings': 'General Settings',
                'appearance': 'Appearance',
                'language': 'Language',
                'currency': 'Currency',
                'tax_rate': 'Tax Rate',
                'theme': 'Theme',
                'notifications': 'Notifications',
                'backup': 'Backup',
                'security': 'Security',
                
                # Messages
                'welcome': 'Welcome',
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Info',
                'confirm': 'Confirm',
                'loading': 'Loading...',
                'no_data': 'No data available',
                'no_invoices': 'No invoices found',
                'no_clients': 'No clients found',
                'login_success': 'Login successful',
                'login_failed': 'Login failed',
                'invalid_credentials': 'Invalid credentials',
                'account_created': 'Account created successfully',
                'invoice_created': 'Invoice created successfully',
                'invoice_updated': 'Invoice updated successfully',
                'invoice_deleted': 'Invoice deleted',
                'client_added': 'Client added successfully',
                'settings_saved': 'Settings saved',
                'backup_created': 'Backup created',
                
                # AI
                'ai_assistant': 'AI Assistant',
                'ai_analysis': 'AI Analysis',
                'ai_recommendations': 'Smart Recommendations',
                'ai_predictions': 'Predictions',
                'performance_analysis': 'Performance Analysis',
                
                # Buttons and actions
                'quick_actions': 'Quick Actions',
                'view_all': 'View All',
                'create_new': 'Create New',
                'export': 'Export',
                'import': 'Import',
                'print': 'Print',
                'refresh': 'Refresh',
                'back': 'Back',
                'next': 'Next',
                'previous': 'Previous',
                
                # Time
                'today': 'Today',
                'yesterday': 'Yesterday',
                'this_week': 'This Week',
                'this_month': 'This Month',
                'this_year': 'This Year',
                'uptime': 'Uptime',
                'hours': 'hours',
                'minutes': 'minutes',
                
                # Security
                'secure_connection': 'Secure encrypted connection',
                'system_admin': 'System Admin',
                'ip_blocked': 'IP address blocked',
                'too_many_attempts': 'Too many attempts',
                
                # Clients
                'add_client': 'Add Client',
                'client_details': 'Client Details',
                'client_history': 'Client History',
                'top_clients': 'Top Clients',
                
                # Backup
                'create_backup': 'Create Backup',
                'restore_backup': 'Restore Backup',
                'auto_backup': 'Auto Backup',
                'backup_history': 'Backup History',
                
                # Footer
                'all_rights_reserved': 'All rights reserved',
                'version': 'Version',
                'contact_us': 'Contact Us',
                'help': 'Help',
                
                # Misc
                'overview': 'Overview',
                'details': 'Details',
                'description': 'Description',
                'category': 'Category',
                'active': 'Active',
                'inactive': 'Inactive',
                'yes': 'Yes',
                'no': 'No',
                'or': 'or',
                'and': 'and',
                'from': 'From',
                'to': 'To',
                'total': 'Total',
            }
        }
        
        self.default_language = 'ar'
    
    def get_text(self, key, lang=None):
        """الحصول على النص المترجم"""
        if lang is None:
            lang = session.get('language', self.default_language)
        
        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]
        
        # Fallback to Arabic
        if key in self.translations['ar']:
            return self.translations['ar'][key]
        
        return key
    
    def get_direction(self, lang=None):
        """الحصول على اتجاه اللغة"""
        if lang is None:
            lang = session.get('language', self.default_language)
        return 'rtl' if lang == 'ar' else 'ltr'
    
    def get_available_languages(self):
        """الحصول على اللغات المتاحة"""
        return {
            'ar': 'العربية',
            'en': 'English'
        }

# ================== نظام إدارة قاعدة البيانات المحسن ==================
class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db_path = self.ensure_database_path()
        
    def ensure_database_path(self):
        """تأكيد وجود مسار قاعدة البيانات"""
        try:
            db_dir = os.path.join(os.getcwd(), 'database')
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            db_path = os.path.join(db_dir, 'invoiceflow_pro.db')
            logger.info(f"مسار قاعدة البيانات: {db_path}")
            return db_path
        except Exception as e:
            logger.error(f"خطأ في إنشاء المسار: {e}")
            return 'invoiceflow_pro.db'
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            return conn
        except Exception as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            try:
                conn = sqlite3.connect(self.db_path, timeout=30)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                logger.info("تم إنشاء قاعدة بيانات جديدة")
                return conn
            except Exception as e2:
                logger.error(f"فشل إنشاء قاعدة بيانات جديدة: {e2}")
                raise

# ================== نظام الأمان المتقدم ==================
class SecurityManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.failed_attempts = {}
        self.lockout_time = 1800  # 30 دقيقة
        self.max_attempts = 5
        self.blocked_ips = set()
        self.suspicious_patterns = []
        
    def check_brute_force(self, ip_address):
        """الكشف عن هجمات القوة الغاشمة"""
        if ip_address in self.blocked_ips:
            return True
            
        if ip_address in self.failed_attempts:
            attempts, last_attempt = self.failed_attempts[ip_address]
            if attempts >= self.max_attempts and time.time() - last_attempt < self.lockout_time:
                logger.warning(f"محاولة دخول محظورة من IP: {ip_address}")
                return True
            elif time.time() - last_attempt >= self.lockout_time:
                # إعادة تعيين بعد انتهاء فترة الحظر
                del self.failed_attempts[ip_address]
        return False
    
    def record_failed_attempt(self, ip_address):
        """تسجيل محاولة فاشلة"""
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = [1, time.time()]
        else:
            self.failed_attempts[ip_address][0] += 1
            self.failed_attempts[ip_address][1] = time.time()
        
        logger.warning(f"محاولة دخول فاشلة من IP: {ip_address} - المحاولة رقم {self.failed_attempts[ip_address][0]}")
    
    def reset_attempts(self, ip_address):
        """إعادة تعيين المحاولات"""
        if ip_address in self.failed_attempts:
            del self.failed_attempts[ip_address]
            logger.info(f"تم إعادة تعيين محاولات الدخول لـ IP: {ip_address}")
    
    def generate_secure_token(self, length=32):
        """إنشاء رمز أمان آمن"""
        return secrets.token_urlsafe(length)
    
    def validate_input(self, input_data, input_type='text'):
        """التحقق من صحة بيانات الإدخال"""
        if not input_data or not isinstance(input_data, str):
            return False
            
        if input_type == 'email':
            try:
                validate_email(input_data)
                return True
            except EmailNotValidError:
                return False
        elif input_type == 'phone':
            phone_pattern = r'^[\+]?[0-9]{10,15}$'
            return bool(re.match(phone_pattern, input_data))
        elif input_type == 'name':
            name_pattern = r'^[a-zA-Z\u0600-\u06FF\s]{2,50}$'
            return bool(re.match(name_pattern, input_data))
        else:
            dangerous_patterns = ['<script>', 'SELECT', 'INSERT', 'DELETE', 'UPDATE', 'DROP', 'UNION', '--', ';']
            input_upper = input_data.upper()
            return not any(pattern in input_upper for pattern in dangerous_patterns)
    
    def sanitize_input(self, input_data):
        """تنظيف المدخلات"""
        if not input_data:
            return input_data
        
        # إزالة الأحرف الخطرة
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '--']
        result = input_data
        for char in dangerous_chars:
            result = result.replace(char, '')
        
        return result.strip()
    
    def hash_data(self, data):
        """تشفير البيانات"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def log_security_event(self, event_type, details):
        """تسجيل أحداث الأمان"""
        logger.info(f"[SECURITY] {event_type}: {details}")

# ================== نظام إدارة المستخدمين المتقدم ==================
class UserManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db = DatabaseManager()
        self.security = SecurityManager()
        self.init_user_system()

    def init_user_system(self):
        """تهيئة نظام المستخدمين المتقدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    company_name TEXT,
                    phone TEXT,
                    user_role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    plan_type TEXT DEFAULT 'professional',
                    language TEXT DEFAULT 'ar',
                    theme TEXT DEFAULT 'default',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    email_verified BOOLEAN DEFAULT 0,
                    verification_token TEXT,
                    reset_token TEXT,
                    profile_data TEXT DEFAULT '{}',
                    login_attempts INTEGER DEFAULT 0,
                    last_attempt TIMESTAMP
                )
            ''')

            # إنشاء المستخدم الإداري الافتراضي
            admin_password = self.hash_password("Admin123!@#")
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (username, email, password_hash, full_name, company_name, user_role, plan_type, email_verified) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@invoiceflow.com', admin_password, 'مدير النظام', 'InvoiceFlow Pro', 'admin', 'enterprise', 1))

            conn.commit()
            conn.close()
            logger.info("نظام المستخدمين المتقدم جاهز")
        except Exception as e:
            logger.error(f"خطأ في نظام المستخدمين: {e}")

    def hash_password(self, password):
        """تشفير كلمة المرور باستخدام salt عشوائي"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt

    def verify_password(self, stored_password, provided_password):
        """التحقق من كلمة المرور"""
        try:
            password_hash, salt = stored_password.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000).hex()
            return password_hash == computed_hash
        except:
            return False

    def authenticate_user(self, identifier, password, ip_address):
        """مصادقة المستخدم مع التحقق من الأمان"""
        lang = session.get('language', 'ar')
        t = language_manager.get_text
        
        if self.security.check_brute_force(ip_address):
            return False, 'user', '', '', '', 'professional', '', t('ip_blocked', lang)
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT password_hash, user_role, email, full_name, company_name, plan_type, username, login_attempts, language
                FROM users WHERE (username = ? OR email = ?) AND is_active = 1
            ''', (identifier, identifier))
            
            result = cursor.fetchone()
            
            if result:
                if self.verify_password(result[0], password):
                    cursor.execute('UPDATE users SET last_login = ?, login_attempts = 0 WHERE username = ?', 
                                 (datetime.now(), result[6]))
                    conn.commit()
                    conn.close()
                    
                    self.security.reset_attempts(ip_address)
                    logger.info(f"تسجيل دخول ناجح للمستخدم: {result[6]}")
                    return True, result[1], result[2], result[3], result[4], result[5], result[6], ""
                else:
                    cursor.execute('UPDATE users SET login_attempts = login_attempts + 1, last_attempt = ? WHERE username = ?', 
                                 (datetime.now(), result[6]))
                    conn.commit()
                    conn.close()
                    
                    self.security.record_failed_attempt(ip_address)
                    logger.warning(f"فشل تسجيل دخول للمستخدم: {identifier}")
            else:
                conn.close()
                self.security.record_failed_attempt(ip_address)
            
            return False, 'user', '', '', '', 'professional', '', t('invalid_credentials', lang)
        except Exception as e:
            logger.error(f"خطأ في المصادقة: {e}")
            return False, 'user', '', '', '', 'professional', '', t('error', lang)

    def register_user(self, username, email, password, full_name, company_name='', phone=''):
        """تسجيل مستخدم جديد"""
        lang = session.get('language', 'ar')
        t = language_manager.get_text
        
        try:
            if not self.security.validate_input(username, 'name'):
                return False, "اسم المستخدم غير صالح" if lang == 'ar' else "Invalid username"
            
            if not self.security.validate_input(email, 'email'):
                return False, "بريد إلكتروني غير صحيح" if lang == 'ar' else "Invalid email"
            
            if not self.security.validate_input(full_name, 'name'):
                return False, "الاسم الكامل غير صالح" if lang == 'ar' else "Invalid full name"
            
            if phone and not self.security.validate_input(phone, 'phone'):
                return False, "رقم الهاتف غير صالح" if lang == 'ar' else "Invalid phone number"

            if len(password) < 8:
                return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل" if lang == 'ar' else "Password must be at least 8 characters"
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً" if lang == 'ar' else "Username or email already exists"
            
            password_hash = self.hash_password(password)
            verification_token = self.security.generate_secure_token()
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, company_name, phone, verification_token, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, company_name, phone, verification_token, lang))
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء حساب جديد: {username}")
            return True, t('account_created', lang)
        except Exception as e:
            logger.error(f"خطأ في التسجيل: {e}")
            return False, f"خطأ في إنشاء الحساب: {str(e)}"
    
    def update_user_language(self, username, language):
        """تحديث لغة المستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET language = ? WHERE username = ?', (language, username))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث اللغة: {e}")
            return False

# ================== نظام إدارة الفواتير المتكامل ==================
class InvoiceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db = DatabaseManager()
        self.security = SecurityManager()
        self.init_invoice_system()

    def init_invoice_system(self):
        """تهيئة نظام الفواتير المتكامل"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    client_id INTEGER,
                    client_name TEXT NOT NULL,
                    client_email TEXT,
                    client_phone TEXT,
                    client_address TEXT,
                    company_name TEXT,
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    services_json TEXT NOT NULL,
                    subtotal DECIMAL(15,2) NOT NULL,
                    tax_rate DECIMAL(5,2) DEFAULT 0.0,
                    tax_amount DECIMAL(15,2) DEFAULT 0.0,
                    discount DECIMAL(15,2) DEFAULT 0.0,
                    total_amount DECIMAL(15,2) NOT NULL,
                    currency TEXT DEFAULT 'SAR',
                    payment_terms TEXT DEFAULT '30 يوم',
                    notes TEXT,
                    status TEXT DEFAULT 'مسودة',
                    payment_status TEXT DEFAULT 'غير مدفوع',
                    pdf_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    company_name TEXT,
                    tax_number TEXT,
                    category TEXT DEFAULT 'عام',
                    payment_terms TEXT DEFAULT '30 يوم',
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(issue_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number)')

            conn.commit()
            conn.close()
            logger.info("نظام الفواتير المتكامل جاهز")
        except Exception as e:
            logger.error(f"خطأ في نظام الفواتير: {e}")

    def create_invoice(self, invoice_data):
        """إنشاء فاتورة جديدة"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
            
            cursor.execute('''
                INSERT INTO invoices 
                (invoice_number, user_id, client_name, client_email, client_phone, client_address,
                 issue_date, due_date, services_json, subtotal, tax_rate, tax_amount, total_amount,
                 payment_terms, notes, status, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_number,
                invoice_data['user_id'],
                invoice_data['client_name'],
                invoice_data.get('client_email', ''),
                invoice_data.get('client_phone', ''),
                invoice_data.get('client_address', ''),
                invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
                invoice_data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
                json.dumps(invoice_data['services'], ensure_ascii=False),
                invoice_data.get('subtotal', 0),
                invoice_data.get('tax_rate', 0),
                invoice_data.get('tax_amount', 0),
                invoice_data['total_amount'],
                invoice_data.get('payment_terms', '30 يوم'),
                invoice_data.get('notes', ''),
                invoice_data.get('status', 'مسودة'),
                invoice_data.get('company_name', 'InvoiceFlow Pro')
            ))

            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء فاتورة جديدة: {invoice_number}")
            return True, invoice_number, "تم إنشاء الفاتورة بنجاح"
        except Exception as e:
            logger.error(f"خطأ في إنشاء الفاتورة: {e}")
            return False, None, f"خطأ في إنشاء الفاتورة: {str(e)}"

    def get_user_invoices(self, user_id):
        """جلب فواتير المستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT invoice_number, client_name, total_amount, issue_date, due_date, status, payment_status
                FROM invoices WHERE user_id = ? ORDER BY created_at DESC
            ''', (user_id,))
            
            invoices = []
            for row in cursor.fetchall():
                invoices.append({
                    'number': row[0],
                    'client': row[1],
                    'amount': row[2],
                    'issue_date': row[3],
                    'due_date': row[4],
                    'status': row[5],
                    'payment_status': row[6]
                })
            
            conn.close()
            return invoices
        except Exception as e:
            logger.error(f"خطأ في جلب الفواتير: {e}")
            return []

    def get_user_stats(self, user_id):
        """إحصائيات المستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_invoices,
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    SUM(CASE WHEN status = 'مسددة' THEN total_amount ELSE 0 END) as paid_amount,
                    COUNT(CASE WHEN status = 'معلقة' THEN 1 END) as pending_invoices,
                    COALESCE(SUM(tax_amount), 0) as tax_amount
                FROM invoices WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_invoices': result[0] or 0,
                'total_revenue': result[1] or 0,
                'paid_amount': result[2] or 0,
                'pending_invoices': result[3] or 0,
                'tax_amount': result[4] or 0
            }
        except Exception as e:
            logger.error(f"خطأ في جلب الإحصائيات: {e}")
            return {'total_invoices': 0, 'total_revenue': 0, 'paid_amount': 0, 'pending_invoices': 0, 'tax_amount': 0}
    
    def get_invoice_by_number(self, invoice_number):
        """جلب فاتورة بواسطة رقمها"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
        except Exception as e:
            logger.error(f"خطأ في جلب الفاتورة: {e}")
            return None
    
    def update_invoice_status(self, invoice_number, status, payment_status=None):
        """تحديث حالة الفاتورة"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if payment_status:
                cursor.execute('''
                    UPDATE invoices SET status = ?, payment_status = ?, updated_at = ? WHERE invoice_number = ?
                ''', (status, payment_status, datetime.now(), invoice_number))
            else:
                cursor.execute('''
                    UPDATE invoices SET status = ?, updated_at = ? WHERE invoice_number = ?
                ''', (status, datetime.now(), invoice_number))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"خطأ في تحديث الفاتورة: {e}")
            return False

# ================== نظام إنشاء PDF الاحترافي ==================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor('#2563EB')
        self.secondary_color = colors.HexColor('#1E293B')
    
    def generate_invoice_pdf(self, invoice_data):
        """إنشاء ملف PDF للفاتورة"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        elements = []
        elements.extend(self.create_header(invoice_data))
        elements.extend(self.create_company_client_info(invoice_data))
        elements.extend(self.create_services_table(invoice_data))
        elements.extend(self.create_totals_section(invoice_data))
        elements.extend(self.create_professional_footer())
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def arabic_text(self, text):
        """معالجة النص العربي للعرض في PDF"""
        try:
            if text:
                reshaped_text = arabic_reshaper.reshape(text)
                return get_display(reshaped_text)
            return text
        except:
            return text
    
    def create_header(self, invoice_data):
        """إنشاء رأس الفاتورة"""
        elements = []
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=self.primary_color,
            alignment=1,
            spaceAfter=20
        )
        
        title = Paragraph(self.arabic_text("فاتورة ضريبية"), title_style)
        elements.append(title)
        elements.append(Spacer(1, 10))
        
        header_data = [
            [self.arabic_text('رقم الفاتورة'), invoice_data.get('invoice_number', 'N/A')],
            [self.arabic_text('تاريخ الإصدار'), invoice_data.get('issue_date', 'N/A')],
            [self.arabic_text('تاريخ الاستحقاق'), invoice_data.get('due_date', 'N/A')]
        ]
        
        header_table = Table(header_data, colWidths=[200, 200])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.secondary_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0'))
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_company_client_info(self, invoice_data):
        """معلومات الشركة والعميل"""
        elements = []
        
        company_name = invoice_data.get('company_name', 'InvoiceFlow Pro')
        company_info = self.arabic_text(f"{company_name}\nنظام إدارة الفواتير الاحترافي\ninfo@invoiceflow.com")
        
        client_info = self.arabic_text(f"{invoice_data['client_name']}\n{invoice_data.get('client_email', '')}\n{invoice_data.get('client_phone', '')}")
        
        info_data = [
            [self.arabic_text('معلومات البائع'), self.arabic_text('معلومات العميل')],
            [Paragraph(company_info.replace('\n', '<br/>'), self.styles['Normal']), 
             Paragraph(client_info.replace('\n', '<br/>'), self.styles['Normal'])]
        ]
        
        info_table = Table(info_data, colWidths=[250, 250])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F1F5F9')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0'))
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 25))
        
        return elements
    
    def create_services_table(self, invoice_data):
        """جدول الخدمات"""
        elements = []
        
        section_title = Paragraph(self.arabic_text("الخدمات والمنتجات"), self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 10))
        
        header = [self.arabic_text('الخدمة'), self.arabic_text('الوصف'), self.arabic_text('الكمية'), self.arabic_text('سعر الوحدة'), self.arabic_text('المجموع')]
        data = [header]
        
        services = invoice_data.get('services', [])
        if isinstance(services, str):
            services = json.loads(services)
        
        for service in services:
            total = service['quantity'] * service['price']
            data.append([
                self.arabic_text(service['name']),
                self.arabic_text(service.get('description', '')),
                str(service['quantity']),
                f"{service['price']:,.2f}",
                f"{total:,.2f}"
            ])
        
        services_table = Table(data, colWidths=[120, 150, 60, 80, 80])
        services_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ]))
        
        elements.append(services_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_totals_section(self, invoice_data):
        """قسم الإجماليات"""
        elements = []
        
        subtotal = invoice_data.get('subtotal', 0)
        tax_rate = invoice_data.get('tax_rate', 0)
        tax_amount = invoice_data.get('tax_amount', 0)
        total = invoice_data.get('total_amount', 0)
        
        totals_data = [
            [self.arabic_text('المجموع الفرعي:'), f"{subtotal:,.2f}"],
            [self.arabic_text(f'الضريبة ({tax_rate}%):'), f"{tax_amount:,.2f}"],
            [self.arabic_text('الإجمالي النهائي:'), f"{total:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[300, 100])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.primary_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def create_professional_footer(self):
        """تذييل الفاتورة"""
        elements = []
        
        footer_text = self.arabic_text("InvoiceFlow Pro - نظام إدارة الفواتير الاحترافي\nشكراً لتعاملكم معنا")
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#475569'),
            alignment=1,
            spaceBefore=20
        )
        
        footer = Paragraph(footer_text.replace('\n', '<br/>'), footer_style)
        elements.append(footer)
        
        return elements

# ================== نظام الذكاء الاصطناعي المتقدم ==================
class AdvancedInvoiceAI:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.user_profiles = {}
        self.conversation_history = {}
        
    def smart_welcome(self, username):
        """ترحيب ذكي مخصص"""
        user_stats = invoice_manager.get_user_stats(username)
        invoices = invoice_manager.get_user_invoices(username)
        
        return self._generate_welcome_dashboard(username, user_stats, invoices)
    
    def _generate_welcome_dashboard(self, username, stats, invoices):
        """إنشاء لوحة ترحيب ذكية"""
        lang = session.get('language', 'ar')
        t = language_manager.get_text
        
        performance_analysis = self._analyze_performance(stats, invoices)
        recommendations = self._generate_recommendations(stats, invoices, lang)
        predictions = self._generate_predictions(stats)
        
        if lang == 'ar':
            return f"""
            <div class="ai-dashboard" style="background: linear-gradient(135deg, #0F172A, #1a237e); color: white; border-radius: 16px; padding: 25px; margin: 20px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: #0D9488; padding: 12px; border-radius: 12px; margin-left: 15px;">
                        <i class="fas fa-robot" style="font-size: 1.5em;"></i>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: white;">{t('ai_assistant', lang)} - InvoiceAI</h3>
                        <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 0.9em;">{t('welcome', lang)} {username}!
                        <span style="color: #0D9488;">• {performance_analysis['mood']}</span></p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div class="ai-card" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h4 style="color: #0D9488; margin-bottom: 15px; display: flex; align-items: center;">
                            <i class="fas fa-chart-line" style="margin-left: 8px;"></i>
                            {t('performance_analysis', lang)}
                        </h4>
                        <div style="color: #E2E8F0;">
                            <p><b>{t('growth_rate', lang)}:</b> {performance_analysis['growth_rate']}%</p>
                            <p><b>{t('average_invoice', lang)}:</b> ${performance_analysis['avg_invoice']:,.0f}</p>
                            <p><b>{t('collection_efficiency', lang)}:</b> {performance_analysis['collection_efficiency']}%</p>
                        </div>
                    </div>
                    
                    <div class="ai-card" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h4 style="color: #0D9488; margin-bottom: 15px; display: flex; align-items: center;">
                            <i class="fas fa-lightbulb" style="margin-left: 8px;"></i>
                            {t('ai_recommendations', lang)}
                        </h4>
                        <div style="color: #E2E8F0; font-size: 0.9em;">
                            {recommendations}
                        </div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #0D9488;">{predictions['revenue_next_month']}</div>
                        <div style="font-size: 0.8em; color: #94A3B8;">الإيرادات المتوقعة</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #2563EB;">{predictions['invoices_next_month']}</div>
                        <div style="font-size: 0.8em; color: #94A3B8;">فواتير متوقعة</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #10B981;">{predictions['success_probability']}%</div>
                        <div style="font-size: 0.8em; color: #94A3B8;">احتمالية النجاح</div>
                    </div>
                </div>
            </div>
            """
        else:
            return f"""
            <div class="ai-dashboard" style="background: linear-gradient(135deg, #0F172A, #1a237e); color: white; border-radius: 16px; padding: 25px; margin: 20px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <div style="background: #0D9488; padding: 12px; border-radius: 12px; margin-right: 15px;">
                        <i class="fas fa-robot" style="font-size: 1.5em;"></i>
                    </div>
                    <div>
                        <h3 style="margin: 0; color: white;">{t('ai_assistant', lang)} - InvoiceAI</h3>
                        <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 0.9em;">{t('welcome', lang)} {username}!
                        <span style="color: #0D9488;">• {performance_analysis['mood_en']}</span></p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div class="ai-card" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h4 style="color: #0D9488; margin-bottom: 15px; display: flex; align-items: center;">
                            <i class="fas fa-chart-line" style="margin-right: 8px;"></i>
                            {t('performance_analysis', lang)}
                        </h4>
                        <div style="color: #E2E8F0;">
                            <p><b>{t('growth_rate', lang)}:</b> {performance_analysis['growth_rate']}%</p>
                            <p><b>{t('average_invoice', lang)}:</b> ${performance_analysis['avg_invoice']:,.0f}</p>
                            <p><b>{t('collection_efficiency', lang)}:</b> {performance_analysis['collection_efficiency']}%</p>
                        </div>
                    </div>
                    
                    <div class="ai-card" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px);">
                        <h4 style="color: #0D9488; margin-bottom: 15px; display: flex; align-items: center;">
                            <i class="fas fa-lightbulb" style="margin-right: 8px;"></i>
                            {t('ai_recommendations', lang)}
                        </h4>
                        <div style="color: #E2E8F0; font-size: 0.9em;">
                            {recommendations}
                        </div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #0D9488;">{predictions['revenue_next_month']}</div>
                        <div style="font-size: 0.8em; color: #94A3B8;">Expected Revenue</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #2563EB;">{predictions['invoices_next_month']}</div>
                        <div style="font-size: 0.8em; color: #94A3B8;">Expected Invoices</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 2em; font-weight: bold; color: #10B981;">{predictions['success_probability']}%</div>
                        <div style="font-size: 0.8em; color: #94A3B8;">Success Probability</div>
                    </div>
                </div>
            </div>
            """
    
    def _analyze_performance(self, stats, invoices):
        """تحليل أداء المستخدم"""
        total_invoices = stats['total_invoices']
        total_revenue = stats['total_revenue']
        
        avg_invoice = total_revenue / max(total_invoices, 1)
        paid_amount = stats.get('paid_amount', 0)
        collection_efficiency = (paid_amount / max(total_revenue, 1)) * 100
        growth_rate = min(25, total_invoices * 2)
        
        if total_invoices == 0:
            mood = "ابدأ رحلتك الأولى"
            mood_en = "Start your journey"
        elif total_invoices < 5:
            mood = "أداء جيد للبداية"
            mood_en = "Good start"
        elif total_invoices < 20:
            mood = "أداء ممتاز"
            mood_en = "Excellent performance"
        else:
            mood = "خبير في الإدارة"
            mood_en = "Management expert"
        
        return {
            'growth_rate': growth_rate,
            'avg_invoice': avg_invoice,
            'collection_efficiency': round(collection_efficiency, 1),
            'mood': mood,
            'mood_en': mood_en
        }
    
    def _generate_recommendations(self, stats, invoices, lang='ar'):
        """توليد توصيات ذكية"""
        recommendations = []
        total_invoices = stats['total_invoices']
        pending_invoices = stats['pending_invoices']
        
        if lang == 'ar':
            if total_invoices == 0:
                recommendations.append("ابدأ بإنشاء فاتورتك الأولى اليوم")
                recommendations.append("أضف عملاءك لتبدأ في بناء قاعدة عملائك")
            else:
                if pending_invoices > 2:
                    recommendations.append("لديك فواتير معلقة تحتاج متابعة")
                recommendations.append("استخدم التقارير لمتابعة أدائك")
                recommendations.append("استمر في استخدام النظام لتحقيق أفضل النتائج")
        else:
            if total_invoices == 0:
                recommendations.append("Create your first invoice today")
                recommendations.append("Add clients to build your customer base")
            else:
                if pending_invoices > 2:
                    recommendations.append("You have pending invoices that need follow-up")
                recommendations.append("Use reports to track your performance")
                recommendations.append("Keep using the system for best results")
        
        return "".join(f'<p>• {rec}</p>' for rec in recommendations[:4])
    
    def _generate_predictions(self, stats):
        """توليد تنبؤات"""
        total_invoices = stats['total_invoices']
        total_revenue = stats['total_revenue']
        
        if total_invoices == 0:
            return {
                'revenue_next_month': "$0",
                'invoices_next_month': "0",
                'success_probability': "85"
            }
        
        revenue_growth = min(50, total_invoices * 5)
        predicted_revenue = total_revenue * (1 + revenue_growth/100)
        predicted_invoices = total_invoices + max(2, total_invoices // 3)
        success_probability = min(95, 70 + total_invoices * 2)
        
        return {
            'revenue_next_month': f"${predicted_revenue:,.0f}",
            'invoices_next_month': f"{predicted_invoices}",
            'success_probability': f"{success_probability}"
        }

# ================== نظام النسخ الاحتياطي المتقدم ==================
class AdvancedBackupManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.db = DatabaseManager()
        self.backup_dir = self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """تأكيد وجود مجلد النسخ الاحتياطي"""
        try:
            backup_dir = os.path.join(os.getcwd(), 'backups')
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            return backup_dir
        except Exception as e:
            logger.error(f"خطأ في إنشاء مجلد النسخ الاحتياطي: {e}")
            return 'backups'
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'backup_{timestamp}.db')
            
            shutil.copy2(self.db.db_path, backup_file)
            
            if os.path.exists('app.log'):
                log_backup = os.path.join(self.backup_dir, f'logs_{timestamp}.backup')
                shutil.copy2('app.log', log_backup)
            
            logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
            return True, backup_file
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False, str(e)
    
    def auto_backup(self):
        """نسخ احتياطي تلقائي"""
        try:
            success, backup_file = self.create_backup()
            if success:
                self.clean_old_backups()
            return success
        except Exception as e:
            logger.error(f"خطأ في النسخ الاحتياطي التلقائي: {e}")
            return False
    
    def clean_old_backups(self, keep_count=5):
        """تنظيف النسخ القديمة"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('backup_') and file.endswith('.db'):
                    backup_files.append(file)
            
            backup_files.sort()
            
            if len(backup_files) > keep_count:
                for file in backup_files[:-keep_count]:
                    os.remove(os.path.join(self.backup_dir, file))
                    logger.info(f"تم حذف النسخة القديمة: {file}")
        except Exception as e:
            logger.error(f"خطأ في تنظيف النسخ القديمة: {e}")
    
    def get_backup_list(self):
        """الحصول على قائمة النسخ الاحتياطية"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('backup_') and file.endswith('.db'):
                    file_path = os.path.join(self.backup_dir, file)
                    size = os.path.getsize(file_path)
                    backup_files.append({
                        'name': file,
                        'size': f"{size / 1024:.2f} KB",
                        'date': file.replace('backup_', '').replace('.db', '')
                    })
            return sorted(backup_files, key=lambda x: x['date'], reverse=True)
        except Exception as e:
            logger.error(f"خطأ في جلب قائمة النسخ: {e}")
            return []

# ================== نظام الإشعارات المتقدم ==================
class AdvancedNotificationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.notifications = {}
    
    def add_notification(self, user_id, title, message, type='info'):
        """إضافة إشعار جديد"""
        try:
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            
            notification = {
                'id': secrets.token_hex(8),
                'title': title,
                'message': message,
                'type': type,
                'timestamp': datetime.now().isoformat(),
                'read': False
            }
            
            self.notifications[user_id].append(notification)
            logger.info(f"إشعار جديد للمستخدم {user_id}: {title}")
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة الإشعار: {e}")
            return False
    
    def get_user_notifications(self, user_id, unread_only=False):
        """جلب إشعارات المستخدم"""
        try:
            if user_id not in self.notifications:
                return []
            
            notifications = self.notifications[user_id]
            if unread_only:
                notifications = [n for n in notifications if not n['read']]
            
            return notifications[-10:]
        except Exception as e:
            logger.error(f"خطأ في جلب الإشعارات: {e}")
            return []
    
    def mark_as_read(self, user_id, notification_id):
        """تحديد الإشعار كمقروء"""
        try:
            if user_id in self.notifications:
                for notification in self.notifications[user_id]:
                    if notification['id'] == notification_id:
                        notification['read'] = True
                        return True
            return False
        except Exception as e:
            logger.error(f"خطأ في تحديد الإشعار كمقروء: {e}")
            return False
    
    def get_unread_count(self, user_id):
        """الحصول على عدد الإشعارات غير المقروءة"""
        try:
            if user_id not in self.notifications:
                return 0
            return len([n for n in self.notifications[user_id] if not n['read']])
        except:
            return 0

# ================== نظام التحليلات المتقدم ==================
class AdvancedAnalyticsEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.user_behaviors = {}
        self.page_views = {}
        self.conversion_data = {}
    
    def track_user_behavior(self, user_id, action, metadata=None):
        """تتبع سلوك المستخدم"""
        try:
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = []
            
            behavior = {
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.user_behaviors[user_id].append(behavior)
            
            # الاحتفاظ بآخر 100 سلوك فقط
            if len(self.user_behaviors[user_id]) > 100:
                self.user_behaviors[user_id] = self.user_behaviors[user_id][-100:]
        except Exception as e:
            logger.error(f"خطأ في تتبع السلوك: {e}")
    
    def get_user_analytics(self, user_id):
        """الحصول على تحليلات المستخدم"""
        try:
            behaviors = self.user_behaviors.get(user_id, [])
            
            action_counts = {}
            for behavior in behaviors:
                action = behavior['action']
                action_counts[action] = action_counts.get(action, 0) + 1
            
            return {
                'total_actions': len(behaviors),
                'action_breakdown': action_counts,
                'last_activity': behaviors[-1]['timestamp'] if behaviors else None
            }
        except Exception as e:
            logger.error(f"خطأ في جلب التحليلات: {e}")
            return {}

# ================== نظام الإعدادات والمظهر ==================
class SettingsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.user_settings = {}
        self.system_settings = self.load_system_settings()
    
    def load_system_settings(self):
        """تحميل إعدادات النظام"""
        return {
            'company_name': 'InvoiceFlow Pro',
            'currency': 'SAR',
            'tax_rate': 15,
            'payment_terms': '30 يوم',
            'language': 'ar',
            'theme': 'default',
            'backup_interval': 24,
            'email_notifications': True,
            'sms_notifications': False,
            'auto_backup': True,
            'invoice_prefix': 'INV'
        }
    
    def get_user_settings(self, user_id):
        """جلب إعدادات المستخدم"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = self.system_settings.copy()
        return self.user_settings[user_id]
    
    def update_user_settings(self, user_id, new_settings):
        """تحديث إعدادات المستخدم"""
        if user_id not in self.user_settings:
            self.user_settings[user_id] = self.system_settings.copy()
        
        self.user_settings[user_id].update(new_settings)
        logger.info(f"تم تحديث إعدادات المستخدم {user_id}")
        return True
    
    def get_available_themes(self):
        """الحصول على السمات المتاحة"""
        return {
            'default': {'name': 'الافتراضي', 'name_en': 'Default'},
            'dark': {'name': 'الداكن', 'name_en': 'Dark'},
            'professional': {'name': 'احترافي', 'name_en': 'Professional'}
        }
    
    def get_available_currencies(self):
        """الحصول على العملات المتاحة"""
        return {
            'SAR': {'name': 'ريال سعودي', 'name_en': 'Saudi Riyal', 'symbol': 'ر.س'},
            'USD': {'name': 'دولار أمريكي', 'name_en': 'US Dollar', 'symbol': '$'},
            'EUR': {'name': 'يورو', 'name_en': 'Euro', 'symbol': '€'},
            'AED': {'name': 'درهم إماراتي', 'name_en': 'UAE Dirham', 'symbol': 'د.إ'},
            'EGP': {'name': 'جنيه مصري', 'name_en': 'Egyptian Pound', 'symbol': 'ج.م'}
        }

# ================== نظام التقارير المتقدم ==================
class AdvancedReportGenerator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
    
    def generate_financial_report(self, user_id, start_date, end_date):
        """إنشاء تقرير مالي"""
        invoices = invoice_manager.get_user_invoices(user_id)
        filtered_invoices = [
            inv for inv in invoices 
            if start_date <= inv['issue_date'] <= end_date
        ]
        
        return {
            'period': f'{start_date} - {end_date}',
            'total_invoices': len(filtered_invoices),
            'total_revenue': sum(inv['amount'] for inv in filtered_invoices),
            'average_invoice': sum(inv['amount'] for inv in filtered_invoices) / max(len(filtered_invoices), 1)
        }
    
    def generate_tax_report(self, user_id, year):
        """إنشاء تقرير ضريبي"""
        invoices = invoice_manager.get_user_invoices(user_id)
        yearly_invoices = [
            inv for inv in invoices 
            if inv['issue_date'].startswith(str(year))
        ]
        
        return {
            'year': year,
            'total_sales': sum(inv['amount'] for inv in yearly_invoices),
            'total_transactions': len(yearly_invoices)
        }

# ================== نظام التخزين المؤقت ==================
class CacheManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.cache = {}
        self.ttl = 300
    
    def get(self, key):
        """الحصول من التخزين المؤقت"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, data):
        """وضع في التخزين المؤقت"""
        self.cache[key] = (data, time.time())
    
    def clear(self, key=None):
        """مسح التخزين المؤقت"""
        if key:
            if key in self.cache:
                del self.cache[key]
        else:
            self.cache.clear()

# ================== إعداد الأنظمة ==================
language_manager = LanguageManager()
db_manager = DatabaseManager()
security_manager = SecurityManager()
user_manager = UserManager()
invoice_manager = InvoiceManager()
pdf_generator = ProfessionalPDFGenerator()
invoice_ai = AdvancedInvoiceAI()
backup_manager = AdvancedBackupManager()
notification_manager = AdvancedNotificationManager()
analytics_engine = AdvancedAnalyticsEngine()
settings_manager = SettingsManager()
advanced_reports = AdvancedReportGenerator()
cache_manager = CacheManager()

# ================== نظام المراقبة ==================
class SystemMonitor:
    def __init__(self):
        self.uptime_start = time.time()
        self.last_backup = time.time()
        self.performance_metrics = {
            'requests_served': 0,
            'errors_count': 0,
            'backups_created': 0
        }
        
    def start_monitoring(self):
        logger.info("بدء أنظمة InvoiceFlow Pro...")
        Thread(target=self._monitor, daemon=True).start()
        logger.info("أنظمة InvoiceFlow Pro مفعلة!")
    
    def _monitor(self):
        while True:
            time.sleep(60)
            uptime = time.time() - self.uptime_start
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            logger.info(f"تقرير النظام: {hours}س {minutes}د - نظام مستقر")
            
            user_settings = settings_manager.system_settings
            if user_settings.get('auto_backup', True) and time.time() - self.last_backup > 3600:
                if backup_manager.auto_backup():
                    self.last_backup = time.time()
                    self.performance_metrics['backups_created'] += 1
            
            cache_manager.clear()

monitor = SystemMonitor()
monitor.start_monitoring()

# ================== الدوال المساعدة ==================
def get_current_language():
    """الحصول على اللغة الحالية"""
    return session.get('language', 'ar')

def t(key):
    """اختصار للترجمة"""
    return language_manager.get_text(key, get_current_language())

def get_direction():
    """الحصول على اتجاه اللغة"""
    return language_manager.get_direction(get_current_language())

def validate_invoice_data(data):
    """التحقق من صحة بيانات الفاتورة"""
    required_fields = ['client_name', 'services']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"الحقل {field} مطلوب"
    
    if not isinstance(data['services'], list) or len(data['services']) == 0:
        return False, "يجب إضافة خدمة واحدة على الأقل"
    
    return True, "بيانات صحيحة"

def generate_invoices_table(invoices):
    """إنشاء جدول الفواتير"""
    lang = get_current_language()
    
    if not invoices:
        no_data_text = t('no_invoices')
        return f'''
        <tr>
            <td colspan="6" style="text-align: center; padding: 20px; color: var(--light-slate);">
                <i class="fas fa-receipt" style="font-size: 2em; margin-bottom: 10px; display: block; opacity: 0.5;"></i>
                {no_data_text}
            </td>
        </tr>
        '''
    
    html = ""
    for inv in invoices[:10]:
        status_class = inv['status']
        
        html += f"""
        <tr>
            <td><strong>{inv['number']}</strong></td>
            <td>{inv['client']}</td>
            <td>{inv['issue_date']}</td>
            <td style="font-weight: bold; color: var(--accent-blue);">${inv['amount']:,.2f}</td>
            <td><span class="status-badge {status_class}">{inv['status']}</span></td>
            <td>
                <a href="/invoices/{inv['number']}/pdf" class="btn-action" style="background: var(--accent-blue); color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8em;">
                    <i class="fas fa-download"></i> PDF
                </a>
            </td>
        </tr>
        """
    
    return html

# ================== التصميم المتجاوب الاحترافي ==================
def get_professional_design():
    """الحصول على التصميم مع دعم تعدد اللغات"""
    lang = get_current_language()
    direction = get_direction()
    
    return f"""
<!DOCTYPE html>
<html dir="{direction}" lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title }}}}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-dark: #0F172A;
            --dark-charcoal: #1E293B;
            --medium-slate: #334155;
            --light-slate: #475569;
            --accent-blue: #2563EB;
            --accent-teal: #0D9488;
            --accent-emerald: #059669;
            --pure-white: #FFFFFF;
            --light-gray: #F8FAFC;
            --border-light: #E2E8F0;
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            
            --blue-gradient: linear-gradient(135deg, var(--accent-blue), #1D4ED8);
            --teal-gradient: linear-gradient(135deg, var(--accent-teal), #0F766E);
            --dark-gradient: linear-gradient(135deg, var(--primary-dark), #020617);
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            font-family: {'"Tajawal"' if lang == 'ar' else '"Inter"'}, -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--light-gray);
            color: var(--primary-dark);
            min-height: 100vh;
            line-height: 1.7;
            width: 100%;
            height: 100%;
        }}
        
        .professional-container {{
            width: 100%;
            min-height: 100vh;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .auth-wrapper {{
            min-height: 100vh;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--dark-gradient);
            position: relative;
            padding: 20px;
            overflow: hidden;
        }}
        
        .auth-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(37, 99, 235, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(13, 148, 136, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(5, 150, 105, 0.05) 0%, transparent 50%);
            z-index: 1;
        }}
        
        .auth-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px 35px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: cardEntrance 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }}
        
        @keyframes cardEntrance {{
            0% {{
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }}
            100% {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}
        
        .brand-section {{
            text-align: center;
            margin-bottom: 35px;
        }}
        
        .brand-logo {{
            font-size: 3em;
            background: var(--blue-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            display: inline-block;
        }}
        
        .brand-title {{
            font-size: 2.2em;
            font-weight: 800;
            background: var(--blue-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }}
        
        .brand-subtitle {{
            color: var(--light-slate);
            font-size: 1em;
            font-weight: 400;
            line-height: 1.5;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-label {{
            display: block;
            margin-bottom: 8px;
            color: var(--primary-dark);
            font-weight: 600;
            font-size: 0.95em;
        }}
        
        .input-wrapper {{
            position: relative;
        }}
        
        .form-control {{
            width: 100%;
            padding: 16px 20px 16px 50px;
            background: rgba(248, 250, 252, 0.8);
            border: 2px solid var(--border-light);
            border-radius: 12px;
            color: var(--primary-dark);
            font-size: 1em;
            transition: all 0.3s ease;
            font-family: inherit;
            font-weight: 500;
        }}
        
        .form-control:focus {{
            outline: none;
            border-color: var(--accent-blue);
            background: var(--pure-white);
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }}
        
        .input-icon {{
            position: absolute;
            {'left' if lang == 'ar' else 'right'}: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-slate);
            font-size: 1.2em;
        }}
        
        .btn {{
            background: var(--blue-gradient);
            color: var(--pure-white);
            padding: 16px 32px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 700;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            font-family: inherit;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        .btn-secondary {{
            background: transparent;
            color: var(--accent-blue);
            border: 2px solid var(--accent-blue);
        }}
        
        .btn-secondary:hover {{
            background: var(--accent-blue);
            color: var(--pure-white);
        }}
        
        .auth-footer {{
            text-align: center;
            margin-top: 28px;
            padding-top: 20px;
            border-top: 1px solid var(--border-light);
        }}
        
        .footer-text {{
            color: var(--light-slate);
            font-size: 0.9em;
            margin-bottom: 14px;
        }}
        
        .security-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: var(--success);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-top: 15px;
        }}
        
        .language-switcher {{
            position: fixed;
            top: 20px;
            {'left' if lang == 'ar' else 'right'}: 20px;
            z-index: 1000;
            display: flex;
            gap: 8px;
        }}
        
        .lang-btn {{
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid var(--border-light);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            color: var(--primary-dark);
        }}
        
        .lang-btn:hover, .lang-btn.active {{
            background: var(--accent-blue);
            color: white;
            border-color: var(--accent-blue);
        }}
        
        .dashboard-header {{
            background: var(--pure-white);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-light);
            position: relative;
            width: 100%;
        }}
        
        .header-content h1 {{
            font-size: 2.3em;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 10px;
        }}
        
        .header-content p {{
            font-size: 1.05em;
            color: var(--light-slate);
            font-weight: 400;
        }}
        
        .user-nav {{
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            padding: 10px 18px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .admin-badge {{
            background: var(--accent-emerald);
            color: var(--pure-white);
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 0.75em;
            font-weight: 600;
        }}
        
        .nav-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
            width: 100%;
        }}
        
        .nav-card {{
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            border-radius: 14px;
            padding: 25px;
            text-align: center;
            color: inherit;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-sm);
            width: 100%;
        }}
        
        .nav-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--accent-blue);
        }}
        
        .nav-card i {{
            font-size: 2.5em;
            margin-bottom: 18px;
            color: var(--accent-blue);
        }}
        
        .nav-card h3 {{
            font-size: 1.3em;
            margin-bottom: 10px;
            color: var(--primary-dark);
            font-weight: 600;
        }}
        
        .nav-card p {{
            color: var(--light-slate);
            font-size: 0.92em;
            line-height: 1.6;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin: 30px 0;
            width: 100%;
        }}
        
        .stat-card {{
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            border-radius: 14px;
            padding: 25px;
            text-align: center;
            box-shadow: var(--shadow-sm);
            width: 100%;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: 700;
            margin: 12px 0;
            color: var(--primary-dark);
        }}
        
        .stat-card p {{
            font-size: 0.95em;
            color: var(--light-slate);
            font-weight: 500;
        }}
        
        .alert {{
            padding: 18px 22px;
            border-radius: 12px;
            margin: 18px 0;
            text-align: center;
            font-weight: 500;
            border: 1px solid;
            font-size: 0.95em;
            width: 100%;
        }}
        
        .alert-success {{
            background: rgba(16, 185, 129, 0.1);
            border-color: var(--success);
            color: var(--success);
        }}
        
        .alert-error {{
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--error);
            color: var(--error);
        }}
        
        .alert-info {{
            background: rgba(37, 99, 235, 0.1);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }}
        
        .content-section {{
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            border-radius: 14px;
            padding: 25px;
            margin: 22px 0;
            box-shadow: var(--shadow-sm);
            width: 100%;
        }}
        
        .services-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
        }}
        
        .services-table th,
        .services-table td {{
            padding: 12px 15px;
            text-align: {'right' if lang == 'ar' else 'left'};
            border-bottom: 1px solid var(--border-light);
        }}
        
        .services-table th {{
            background: var(--light-gray);
            font-weight: 600;
            color: var(--primary-dark);
        }}
        
        .services-table tr:hover {{
            background: var(--light-gray);
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
        }}
        
        .status-badge.مسددة, .status-badge.paid {{
            background: var(--success);
            color: white;
        }}
        
        .status-badge.معلقة, .status-badge.pending {{
            background: var(--warning);
            color: white;
        }}
        
        .status-badge.مسودة, .status-badge.draft {{
            background: var(--light-slate);
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .professional-container {{
                padding: 15px;
            }}
            
            .dashboard-header {{
                padding: 20px;
            }}
            
            .header-content h1 {{
                font-size: 1.8em;
            }}
            
            .nav-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .auth-card {{
                padding: 30px 25px;
                margin: 10px;
            }}
            
            .brand-logo {{
                font-size: 2.5em;
            }}
            
            .brand-title {{
                font-size: 1.8em;
            }}
        }}
        
        @media (max-width: 480px) {{
            .professional-container {{
                padding: 10px;
            }}
            
            .dashboard-header {{
                padding: 15px;
            }}
            
            .header-content h1 {{
                font-size: 1.6em;
            }}
            
            .nav-card, .stat-card {{
                padding: 20px;
            }}
            
            .stat-number {{
                font-size: 2em;
            }}
            
            .auth-card {{
                padding: 25px 20px;
            }}
            
            .brand-title {{
                font-size: 1.6em;
            }}
        }}
    </style>
</head>
<body>
    <div class="language-switcher">
        <a href="/set-language/ar" class="lang-btn {'active' if lang == 'ar' else ''}">العربية</a>
        <a href="/set-language/en" class="lang-btn {'active' if lang == 'en' else ''}">English</a>
    </div>
    
    {{% if not is_auth_page %}}
    <div class="professional-container">
        {{% if session.user_logged_in %}}
        <div class="user-nav">
            {{% if session.user_type == 'admin' %}}
            <span class="admin-badge">{t('system_admin')}</span>
            {{% endif %}}
            <i class="fas fa-user-circle"></i> {{{{ session.username }}}}
            | <a href="/profile" style="color: var(--accent-blue); margin: 0 10px;">{t('profile')}</a>
            | <a href="/settings" style="color: var(--accent-teal); margin: 0 10px;">{t('settings')}</a>
            | <a href="/logout" style="color: var(--light-slate);">{t('logout')}</a>
        </div>
        {{% endif %}}
        
        <div class="dashboard-header">
            <div class="header-content">
                <h1><i class="fas fa-file-invoice"></i> {t('app_name')}</h1>
                <p>{t('app_subtitle')} - Enterprise Edition</p>
                <p>{t('uptime')}: {{{{ uptime }}}}</p>
            </div>
        </div>
        
        {{% if session.user_logged_in %}}
        <div class="nav-grid">
            <a href="/" class="nav-card">
                <i class="fas fa-home"></i>
                <h3>{t('dashboard')}</h3>
                <p>{t('overview')}</p>
            </a>
            <a href="/invoices" class="nav-card">
                <i class="fas fa-receipt"></i>
                <h3>{t('invoices')}</h3>
                <p>{t('view_all')}</p>
            </a>
            <a href="/invoices/create" class="nav-card">
                <i class="fas fa-plus-circle"></i>
                <h3>{t('new_invoice')}</h3>
                <p>{t('create_new')}</p>
            </a>
            <a href="/clients" class="nav-card">
                <i class="fas fa-users"></i>
                <h3>{t('clients')}</h3>
                <p>{t('view_all')}</p>
            </a>
            {{% if session.user_type == 'admin' %}}
            <a href="/admin" class="nav-card">
                <i class="fas fa-cog"></i>
                <h3>{t('admin')}</h3>
                <p>{t('settings')}</p>
            </a>
            {{% endif %}}
            <a href="/reports" class="nav-card">
                <i class="fas fa-chart-bar"></i>
                <h3>{t('reports')}</h3>
                <p>{t('financial_report')}</p>
            </a>
            <a href="/advanced-reports" class="nav-card">
                <i class="fas fa-chart-pie"></i>
                <h3>{t('advanced_reports')}</h3>
                <p>{t('ai_analysis')}</p>
            </a>
            <a href="/backup" class="nav-card">
                <i class="fas fa-database"></i>
                <h3>{t('backup')}</h3>
                <p>{t('create_backup')}</p>
            </a>
        </div>
        {{% endif %}}

        {{{{ content | safe }}}}
    </div>
    {{% else %}}
    <div class="auth-wrapper">
        <div class="auth-background"></div>
        {{{{ content | safe }}}}
    </div>
    {{% endif %}}

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.nav-card, .stat-card');
            cards.forEach((card, index) => {{
                card.style.animationDelay = `${{index * 0.1}}s`;
            }});
        }});
    </script>
</body>
</html>
"""

# ================== Routes الأساسية ==================
@app.before_request
def check_security():
    """التحقق من الأمان قبل كل طلب"""
    if request.endpoint and not request.endpoint.startswith('static'):
        monitor.performance_metrics['requests_served'] += 1
        
        if security_manager.check_brute_force(request.remote_addr):
            logger.warning(f"طلب محظور من IP: {request.remote_addr}")
            return "IP blocked due to too many failed attempts", 429
        
        if session.get('user_logged_in'):
            analytics_engine.track_user_behavior(
                session['username'], 
                f"visited_{request.endpoint}",
                {'ip': request.remote_addr, 'method': request.method}
            )

@app.route('/set-language/<lang>')
def set_language(lang):
    """تغيير اللغة"""
    if lang in ['ar', 'en']:
        session['language'] = lang
        if session.get('user_logged_in'):
            user_manager.update_user_language(session['username'], lang)
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/')
def dashboard():
    """لوحة التحكم الرئيسية"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    stats = invoice_manager.get_user_stats(session['username'])
    ai_welcome = invoice_ai.smart_welcome(session['username'])
    
    admin_button = ''
    if session.get('user_type') == 'admin':
        admin_button = f'''
        <a href="/admin" class="btn" style="background: var(--accent-teal);">
            <i class="fas fa-cog"></i> {t('admin')}
        </a>
        '''
    
    content = ai_welcome + f"""
    
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-receipt" style="color: var(--accent-blue);"></i>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>{t('total_invoices')}</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign" style="color: var(--accent-emerald);"></i>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p>{t('total_revenue')}</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-clock" style="color: var(--warning);"></i>
            <div class="stat-number">{stats['pending_invoices']}</div>
            <p>{t('pending_invoices')}</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-check-circle" style="color: var(--success);"></i>
            <div class="stat-number">${stats['paid_amount']:,.0f}</div>
            <p>{t('paid_amount')}</p>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-top: 35px;">
        <div class="content-section">
            <h3 style="margin-bottom: 18px; color: var(--primary-dark);">
                <i class="fas fa-bolt"></i> {t('quick_actions')}
            </h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <a href="/invoices/create" class="btn">
                    <i class="fas fa-plus"></i> {t('new_invoice')}
                </a>
                <a href="/invoices" class="btn btn-secondary">
                    <i class="fas fa-list"></i> {t('view_all')} {t('invoices')}
                </a>
                {admin_button}
            </div>
        </div>
        
        <div class="content-section">
            <h3 style="margin-bottom: 18px; color: var(--primary-dark);">
                <i class="fas fa-chart-line"></i> {t('overview')}
            </h3>
            <div style="color: var(--light-slate); line-height: 2;">
                <p>{stats['total_invoices']} {t('total_invoices')}</p>
                <p>${stats['total_revenue']:,.2f} {t('total_revenue')}</p>
                <p>{stats['pending_invoices']} {t('pending_invoices')}</p>
                <p>${stats['paid_amount']:,.2f} {t('paid_amount')}</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('app_name')} - {t('dashboard')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    lang = get_current_language()
    
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        is_valid, user_role, email, full_name, company_name, plan_type, username, message = user_manager.authenticate_user(
            identifier, password, request.remote_addr
        )
        
        if is_valid:
            session['user_logged_in'] = True
            session['username'] = username
            session['user_type'] = user_role
            session['email'] = email
            session['full_name'] = full_name
            session['company_name'] = company_name
            session['plan_type'] = plan_type
            session.permanent = True
            
            notification_manager.add_notification(
                username, 
                t('welcome'),
                t('login_success'),
                'info'
            )
            
            return redirect(url_for('dashboard'))
        else:
            auth_content = f"""
            <div class="auth-card">
                <div class="brand-section">
                    <div class="brand-logo">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <div class="brand-title">{t('app_name')}</div>
                    <div class="brand-subtitle">{t('app_subtitle')}</div>
                </div>
                
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i> {message}
                </div>
                
                <form method="POST">
                    <div class="form-group">
                        <label class="form-label">{t('username')} / {t('email')}</label>
                        <div class="input-wrapper">
                            <input type="text" name="identifier" class="form-control" placeholder="{t('username')} / {t('email')}" required>
                            <div class="input-icon">
                                <i class="fas fa-user"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">{t('password')}</label>
                        <div class="input-wrapper">
                            <input type="password" name="password" class="form-control" placeholder="{t('password')}" required>
                            <div class="input-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">
                        <i class="fas fa-sign-in-alt"></i> {t('login')}
                    </button>
                </form>
                
                <div class="auth-footer">
                    <a href="/register" class="btn btn-secondary">
                        <i class="fas fa-user-plus"></i> {t('register')}
                    </a>
                    <div class="security-indicator">
                        <i class="fas fa-shield-alt"></i>
                        {t('secure_connection')}
                    </div>
                </div>
            </div>
            """
            return render_template_string(get_professional_design(), title=f"{t('login')} - {t('app_name')}", 
                                        content=auth_content, is_auth_page=True, uptime="")
    
    if 'user_logged_in' in session:
        return redirect(url_for('dashboard'))
    
    auth_content = f"""
    <div class="auth-card">
        <div class="brand-section">
            <div class="brand-logo">
                <i class="fas fa-file-invoice"></i>
            </div>
            <div class="brand-title">{t('app_name')}</div>
            <div class="brand-subtitle">{t('app_subtitle')}</div>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">{t('username')} / {t('email')}</label>
                <div class="input-wrapper">
                    <input type="text" name="identifier" class="form-control" placeholder="{t('username')} / {t('email')}" required>
                    <div class="input-icon">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">{t('password')}</label>
                <div class="input-wrapper">
                    <input type="password" name="password" class="form-control" placeholder="{t('password')}" required>
                    <div class="input-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-sign-in-alt"></i> {t('login')}
            </button>
        </form>
        
        <div class="auth-footer">
            <a href="/register" class="btn btn-secondary">
                <i class="fas fa-user-plus"></i> {t('register')}
            </a>
            <div class="security-indicator">
                <i class="fas fa-shield-alt"></i>
                {t('secure_connection')}
            </div>
        </div>
    </div>
    """
    return render_template_string(get_professional_design(), title=f"{t('login')} - {t('app_name')}", 
                                content=auth_content, is_auth_page=True, uptime="")

@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    lang = get_current_language()
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        company_name = request.form.get('company_name', '')
        phone = request.form.get('phone', '')
        
        success, message = user_manager.register_user(username, email, password, full_name, company_name, phone)
        
        if success:
            return redirect(url_for('login'))
        else:
            auth_content = f"""
            <div class="auth-card">
                <div class="brand-section">
                    <div class="brand-logo">
                        <i class="fas fa-user-plus"></i>
                    </div>
                    <div class="brand-title">{t('register')}</div>
                    <div class="brand-subtitle">{t('app_name')}</div>
                </div>
                
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i> {message}
                </div>
                
                <form method="POST">
                    <div class="form-group">
                        <label class="form-label">{t('username')}</label>
                        <div class="input-wrapper">
                            <input type="text" name="username" class="form-control" value="{username}" required>
                            <div class="input-icon"><i class="fas fa-  value="{username}" required>
                            <div class="input-icon"><i class="fas fa-user"></i></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">{t('email')}</label>
                        <div class="input-wrapper">
                            <input type="email" name="email" class="form-control" value="{email}" required>
                            <div class="input-icon"><i class="fas fa-envelope"></i></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">{t('password')}</label>
                        <div class="input-wrapper">
                            <input type="password" name="password" class="form-control" required>
                            <div class="input-icon"><i class="fas fa-lock"></i></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">{t('full_name')}</label>
                        <div class="input-wrapper">
                            <input type="text" name="full_name" class="form-control" value="{full_name}" required>
                            <div class="input-icon"><i class="fas fa-id-card"></i></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">{t('company_name')}</label>
                        <div class="input-wrapper">
                            <input type="text" name="company_name" class="form-control" value="{company_name}">
                            <div class="input-icon"><i class="fas fa-building"></i></div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">{t('phone')}</label>
                        <div class="input-wrapper">
                            <input type="text" name="phone" class="form-control" value="{phone}">
                            <div class="input-icon"><i class="fas fa-phone"></i></div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">
                        <i class="fas fa-user-plus"></i> {t('register')}
                    </button>
                </form>
                
                <div class="auth-footer">
                    <a href="/login" class="btn btn-secondary">
                        <i class="fas fa-sign-in-alt"></i> {t('login')}
                    </a>
                </div>
            </div>
            """
            return render_template_string(get_professional_design(), title=f"{t('register')} - {t('app_name')}", 
                                        content=auth_content, is_auth_page=True, uptime="")
    
    auth_content = f"""
    <div class="auth-card">
        <div class="brand-section">
            <div class="brand-logo">
                <i class="fas fa-user-plus"></i>
            </div>
            <div class="brand-title">{t('register')}</div>
            <div class="brand-subtitle">{t('app_name')}</div>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">{t('username')}</label>
                <div class="input-wrapper">
                    <input type="text" name="username" class="form-control" required>
                    <div class="input-icon"><i class="fas fa-user"></i></div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">{t('email')}</label>
                <div class="input-wrapper">
                    <input type="email" name="email" class="form-control" required>
                    <div class="input-icon"><i class="fas fa-envelope"></i></div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">{t('password')}</label>
                <div class="input-wrapper">
                    <input type="password" name="password" class="form-control" required>
                    <div class="input-icon"><i class="fas fa-lock"></i></div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">{t('full_name')}</label>
                <div class="input-wrapper">
                    <input type="text" name="full_name" class="form-control" required>
                    <div class="input-icon"><i class="fas fa-id-card"></i></div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">{t('company_name')}</label>
                <div class="input-wrapper">
                    <input type="text" name="company_name" class="form-control">
                    <div class="input-icon"><i class="fas fa-building"></i></div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">{t('phone')}</label>
                <div class="input-wrapper">
                    <input type="text" name="phone" class="form-control">
                    <div class="input-icon"><i class="fas fa-phone"></i></div>
                </div>
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-user-plus"></i> {t('register')}
            </button>
        </form>
        
        <div class="auth-footer">
            <a href="/login" class="btn btn-secondary">
                <i class="fas fa-sign-in-alt"></i> {t('login')}
            </a>
        </div>
    </div>
    """
    return render_template_string(get_professional_design(), title=f"{t('register')} - {t('app_name')}", 
                                content=auth_content, is_auth_page=True, uptime="")

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/invoices')
def invoices():
    """صفحة الفواتير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    user_invoices = invoice_manager.get_user_invoices(session['username'])
    invoices_table = generate_invoices_table(user_invoices)
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    content = f"""
    <div class="content-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2><i class="fas fa-receipt"></i> {t('invoices')}</h2>
            <a href="/invoices/create" class="btn" style="width: auto;">
                <i class="fas fa-plus"></i> {t('new_invoice')}
            </a>
        </div>
        
        <table class="services-table">
            <thead>
                <tr>
                    <th>{t('invoice_number')}</th>
                    <th>{t('client_name')}</th>
                    <th>{t('issue_date')}</th>
                    <th>{t('total_amount')}</th>
                    <th>{t('status')}</th>
                    <th>{t('quick_actions')}</th>
                </tr>
            </thead>
            <tbody>
                {invoices_table}
            </tbody>
        </table>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('invoices')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/invoices/create', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    if request.method == 'POST':
        try:
            services = []
            service_names = request.form.getlist('service_name[]')
            service_quantities = request.form.getlist('service_quantity[]')
            service_prices = request.form.getlist('service_price[]')
            
            for i in range(len(service_names)):
                if service_names[i]:
                    services.append({
                        'name': service_names[i],
                        'quantity': int(service_quantities[i]) if service_quantities[i] else 1,
                        'price': float(service_prices[i]) if service_prices[i] else 0,
                        'description': ''
                    })
            
            subtotal = sum(s['quantity'] * s['price'] for s in services)
            tax_rate = float(request.form.get('tax_rate', 15))
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            invoice_data = {
                'user_id': session['username'],
                'client_name': request.form['client_name'],
                'client_email': request.form.get('client_email', ''),
                'client_phone': request.form.get('client_phone', ''),
                'client_address': request.form.get('client_address', ''),
                'services': services,
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total_amount': total_amount,
                'notes': request.form.get('notes', ''),
                'status': 'معلقة'
            }
            
            success, invoice_number, message = invoice_manager.create_invoice(invoice_data)
            
            if success:
                notification_manager.add_notification(
                    session['username'],
                    t('invoice_created'),
                    f"{t('invoice_number')}: {invoice_number}",
                    'success'
                )
                return redirect(url_for('invoices'))
        except Exception as e:
            logger.error(f"خطأ في إنشاء الفاتورة: {e}")
    
    content = f"""
    <div class="content-section">
        <h2 style="margin-bottom: 25px;"><i class="fas fa-plus-circle"></i> {t('new_invoice')}</h2>
        
        <form method="POST">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label class="form-label">{t('client_name')} *</label>
                    <input type="text" name="client_name" class="form-control" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">{t('email')}</label>
                    <input type="email" name="client_email" class="form-control">
                </div>
                
                <div class="form-group">
                    <label class="form-label">{t('phone')}</label>
                    <input type="text" name="client_phone" class="form-control">
                </div>
                
                <div class="form-group">
                    <label class="form-label">{t('address')}</label>
                    <input type="text" name="client_address" class="form-control">
                </div>
            </div>
            
            <h3 style="margin: 30px 0 20px;"><i class="fas fa-list"></i> {t('services')}</h3>
            
            <div id="services-container">
                <div class="service-row" style="display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 15px; margin-bottom: 15px; align-items: end;">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">{t('service_name')}</label>
                        <input type="text" name="service_name[]" class="form-control" required>
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">{t('quantity')}</label>
                        <input type="number" name="service_quantity[]" class="form-control" value="1" min="1" required>
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label">{t('unit_price')}</label>
                        <input type="number" name="service_price[]" class="form-control" step="0.01" required>
                    </div>
                    <button type="button" onclick="removeService(this)" class="btn btn-secondary" style="width: auto; padding: 10px 15px;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            
            <button type="button" onclick="addService()" class="btn btn-secondary" style="width: auto; margin-bottom: 20px;">
                <i class="fas fa-plus"></i> {t('add_service')}
            </button>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label class="form-label">{t('tax_rate')} (%)</label>
                    <input type="number" name="tax_rate" class="form-control" value="15" step="0.01">
                </div>
                
                <div class="form-group">
                    <label class="form-label">{t('notes')}</label>
                    <textarea name="notes" class="form-control" rows="3"></textarea>
                </div>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 25px;">
                <button type="submit" class="btn">
                    <i class="fas fa-save"></i> {t('save')}
                </button>
                <a href="/invoices" class="btn btn-secondary">
                    <i class="fas fa-times"></i> {t('cancel')}
                </a>
            </div>
        </form>
    </div>
    
    <script>
        function addService() {{
            const container = document.getElementById('services-container');
            const newRow = document.createElement('div');
            newRow.className = 'service-row';
            newRow.style.cssText = 'display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 15px; margin-bottom: 15px; align-items: end;';
            newRow.innerHTML = `
                <div class="form-group" style="margin-bottom: 0;">
                    <input type="text" name="service_name[]" class="form-control" required>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <input type="number" name="service_quantity[]" class="form-control" value="1" min="1" required>
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                    <input type="number" name="service_price[]" class="form-control" step="0.01" required>
                </div>
                <button type="button" onclick="removeService(this)" class="btn btn-secondary" style="width: auto; padding: 10px 15px;">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            container.appendChild(newRow);
        }}
        
        function removeService(btn) {{
            const rows = document.querySelectorAll('.service-row');
            if (rows.length > 1) {{
                btn.closest('.service-row').remove();
            }}
        }}
    </script>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('new_invoice')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/invoices/<invoice_number>/pdf')
def download_invoice_pdf(invoice_number):
    """تحميل PDF للفاتورة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    invoice = invoice_manager.get_invoice_by_number(invoice_number)
    
    if not invoice:
        return "Invoice not found", 404
    
    invoice_data = {
        'invoice_number': invoice['invoice_number'],
        'client_name': invoice['client_name'],
        'client_email': invoice.get('client_email', ''),
        'client_phone': invoice.get('client_phone', ''),
        'issue_date': invoice['issue_date'],
        'due_date': invoice['due_date'],
        'services': json.loads(invoice['services_json']) if isinstance(invoice['services_json'], str) else invoice['services_json'],
        'subtotal': invoice['subtotal'],
        'tax_rate': invoice['tax_rate'],
        'tax_amount': invoice['tax_amount'],
        'total_amount': invoice['total_amount'],
        'company_name': invoice.get('company_name', 'InvoiceFlow Pro')
    }
    
    pdf_buffer = pdf_generator.generate_invoice_pdf(invoice_data)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{invoice_number}.pdf'
    )

@app.route('/clients')
def clients():
    """صفحة العملاء"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    content = f"""
    <div class="content-section">
        <h2><i class="fas fa-users"></i> {t('clients')}</h2>
        <p style="color: var(--light-slate); margin-top: 20px;">{t('no_clients')}</p>
        <a href="/clients/add" class="btn" style="width: auto; margin-top: 20px;">
            <i class="fas fa-plus"></i> {t('add_client')}
        </a>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('clients')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/reports')
def reports():
    """صفحة التقارير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    stats = invoice_manager.get_user_stats(session['username'])
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    content = f"""
    <div class="content-section">
        <h2><i class="fas fa-chart-bar"></i> {t('reports')}</h2>
        
        <div class="stats-grid" style="margin-top: 25px;">
            <div class="stat-card">
                <i class="fas fa-file-invoice" style="color: var(--accent-blue);"></i>
                <div class="stat-number">{stats['total_invoices']}</div>
                <p>{t('total_invoices')}</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-dollar-sign" style="color: var(--accent-emerald);"></i>
                <div class="stat-number">${stats['total_revenue']:,.0f}</div>
                <p>{t('total_revenue')}</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-percentage" style="color: var(--warning);"></i>
                <div class="stat-number">${stats['tax_amount']:,.0f}</div>
                <p>{t('tax_amount')}</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('reports')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/backup')
def backup():
    """صفحة النسخ الاحتياطي"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    backups = backup_manager.get_backup_list()
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    backup_rows = ""
    for b in backups[:10]:
        backup_rows += f"<tr><td>{b['name']}</td><td>{b['size']}</td><td>{b['date']}</td></tr>"
    
    if not backup_rows:
        backup_rows = f"<tr><td colspan='3' style='text-align: center;'>{t('no_data')}</td></tr>"
    
    content = f"""
    <div class="content-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2><i class="fas fa-database"></i> {t('backup')}</h2>
            <a href="/backup/create" class="btn" style="width: auto;">
                <i class="fas fa-plus"></i> {t('create_backup')}
            </a>
        </div>
        
        <table class="services-table">
            <thead>
                <tr>
                    <th>File</th>
                    <th>Size</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {backup_rows}
            </tbody>
        </table>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('backup')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/backup/create')
def create_backup():
    """إنشاء نسخة احتياطية"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    success, result = backup_manager.create_backup()
    
    if success:
        notification_manager.add_notification(
            session['username'],
            t('backup_created'),
            result,
            'success'
        )
    
    return redirect(url_for('backup'))

@app.route('/settings')
def settings():
    """صفحة الإعدادات"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    lang = get_current_language()
    user_settings = settings_manager.get_user_settings(session['username'])
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    content = f"""
    <div class="content-section">
        <h2><i class="fas fa-cog"></i> {t('settings')}</h2>
        
        <div style="margin-top: 25px;">
            <h3>{t('language')}</h3>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <a href="/set-language/ar" class="btn {'btn-secondary' if lang != 'ar' else ''}" style="width: auto;">العربية</a>
                <a href="/set-language/en" class="btn {'btn-secondary' if lang != 'en' else ''}" style="width: auto;">English</a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('settings')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/admin')
def admin():
    """لوحة الإدارة"""
    if 'user_logged_in' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('dashboard'))
    
    lang = get_current_language()
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} {t('hours')} {minutes} {t('minutes')}"
    
    content = f"""
    <div class="content-section">
        <h2><i class="fas fa-shield-alt"></i> {t('admin')}</h2>
        
        <div class="stats-grid" style="margin-top: 25px;">
            <div class="stat-card">
                <i class="fas fa-server" style="color: var(--accent-blue);"></i>
                <div class="stat-number">{monitor.performance_metrics['requests_served']}</div>
                <p>Requests Served</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-database" style="color: var(--accent-emerald);"></i>
                <div class="stat-number">{monitor.performance_metrics['backups_created']}</div>
                <p>Backups Created</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-clock" style="color: var(--warning);"></i>
                <div class="stat-number">{hours}h {minutes}m</div>
                <p>{t('uptime')}</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(get_professional_design(), title=f"{t('admin')} - {t('app_name')}", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/health')
def health():
    """فحص صحة النظام"""
    return jsonify({
        'status': 'healthy',
        'uptime': time.time() - monitor.uptime_start,
        'requests_served': monitor.performance_metrics['requests_served'],
        'version': '5.0'
    })

@app.route('/api/stats')
def api_stats():
    """API للإحصائيات"""
    if 'user_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = invoice_manager.get_user_stats(session['username'])
    return jsonify(stats)

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("=" * 60)
        print("InvoiceFlow Pro v5.0 - Enterprise Edition")
        print("=" * 60)
        print("Features:")
        print("  - Multi-language support (Arabic/English)")
        print("  - Advanced security system")
        print("  - AI-powered analytics")
        print("  - Automatic backup system")
        print("  - Professional PDF generation")
        print("  - Real-time notifications")
        print("  - Advanced reporting")
        print("")
        print("Default credentials:")
        print("  Username: admin")
        print("  Password: Admin123!@#")
        print("")
        print(f"Server running on: http://0.0.0.0:{port}")
        print("=" * 60)
        
        user_manager.init_user_system()
        invoice_manager.init_invoice_system()
        backup_manager.create_backup()
        
        app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
        time.sleep(5)
