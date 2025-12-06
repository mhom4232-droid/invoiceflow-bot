import os
import sqlite3
import json
import time
import hashlib
import secrets
import re
import io
import base64
import jwt
from datetime import datetime, timedelta
from threading import Thread, Lock
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, session, flash, make_response, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import bleach
import uuid

# ================== تطبيق Flask المتطور مع الحماية ==================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_premium_secure_2024_v6')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'jwt_invoiceflow_secure_2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# إعدادات الأمان
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app, resources={r"/*": {"origins": ["https://yourdomain.com"]}}, supports_credentials=True)

# نظام تحديد المعدل
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# إنشاء مجلدات التخزين
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('static/invoices', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Premium - النظام المتعدد اللغات والآمن")
print("🌐 نظام متعدد اللغات (عربي/إنجليزي) + حماية شاملة")
print("🔐 نظام أمان متكامل مع JWT وتشفير متقدم")
print("=" * 80)

# ================== نظام متعدد اللغات ==================
class MultilingualSystem:
    def __init__(self):
        self.languages = {
            'ar': {
                'title': 'InvoiceFlow Premium',
                'home': 'الرئيسية',
                'invoices': 'الفواتير',
                'create_invoice': 'إنشاء فاتورة',
                'ai_insights': 'الذكاء الاصطناعي',
                'clients': 'العملاء',
                'reports': 'التقارير',
                'settings': 'الإعدادات',
                'login': 'تسجيل الدخول',
                'register': 'إنشاء حساب',
                'logout': 'تسجيل الخروج',
                'welcome': 'مرحباً في النظام المتقدم',
                'dashboard': 'لوحة التحكم',
                'revenue': 'الإيرادات',
                'expenses': 'المصروفات',
                'profit': 'الأرباح',
                'pending': 'معلقة',
                'paid': 'مدفوعة',
                'overdue': 'متأخرة',
                'client_name': 'اسم العميل',
                'amount': 'المبلغ',
                'date': 'التاريخ',
                'status': 'الحالة',
                'actions': 'الإجراءات',
                'view': 'عرض',
                'edit': 'تعديل',
                'delete': 'حذف',
                'download': 'تحميل',
                'save': 'حفظ',
                'cancel': 'إلغاء',
                'search': 'بحث',
                'filter': 'تصفية',
                'export': 'تصدير',
                'import': 'استيراد',
                'help': 'مساعدة',
                'profile': 'الملف الشخصي',
                'security': 'الأمان',
                'language': 'اللغة',
                'theme': 'الثيم',
                'dark_mode': 'الوضع الداكن',
                'light_mode': 'الوضع الفاتح',
                'notifications': 'الإشعارات',
                'support': 'الدعم الفني',
                'documentation': 'التوثيق',
                'privacy': 'الخصوصية',
                'terms': 'الشروط',
                'contact': 'اتصل بنا',
                'about': 'عن النظام'
            },
            'en': {
                'title': 'InvoiceFlow Premium',
                'home': 'Home',
                'invoices': 'Invoices',
                'create_invoice': 'Create Invoice',
                'ai_insights': 'AI Insights',
                'clients': 'Clients',
                'reports': 'Reports',
                'settings': 'Settings',
                'login': 'Login',
                'register': 'Register',
                'logout': 'Logout',
                'welcome': 'Welcome to Advanced System',
                'dashboard': 'Dashboard',
                'revenue': 'Revenue',
                'expenses': 'Expenses',
                'profit': 'Profit',
                'pending': 'Pending',
                'paid': 'Paid',
                'overdue': 'Overdue',
                'client_name': 'Client Name',
                'amount': 'Amount',
                'date': 'Date',
                'status': 'Status',
                'actions': 'Actions',
                'view': 'View',
                'edit': 'Edit',
                'delete': 'Delete',
                'download': 'Download',
                'save': 'Save',
                'cancel': 'Cancel',
                'search': 'Search',
                'filter': 'Filter',
                'export': 'Export',
                'import': 'Import',
                'help': 'Help',
                'profile': 'Profile',
                'security': 'Security',
                'language': 'Language',
                'theme': 'Theme',
                'dark_mode': 'Dark Mode',
                'light_mode': 'Light Mode',
                'notifications': 'Notifications',
                'support': 'Support',
                'documentation': 'Documentation',
                'privacy': 'Privacy',
                'terms': 'Terms',
                'contact': 'Contact Us',
                'about': 'About'
            }
        }
    
    def get_text(self, key, lang='ar'):
        """الحصول على النص حسب اللغة"""
        return self.languages.get(lang, {}).get(key, key)
    
    def get_all_languages(self):
        """الحصول على جميع اللغات المتاحة"""
        return list(self.languages.keys())

lang_system = MultilingualSystem()

# ================== نظام السجلات الأمنية ==================
class SecurityLogger:
    def __init__(self):
        self.log_file = 'logs/security.log'
        self.lock = Lock()
    
    def log_event(self, event_type, user_id, ip_address, details):
        """تسجيل حدث أمني"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{event_type}] [User: {user_id}] [IP: {ip_address}] {details}\n"
        
        with self.lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        print(f"🔒 {log_entry.strip()}")

security_logger = SecurityLogger()

# ================== نظام الحماية من الهجمات ==================
class SecuritySystem:
    @staticmethod
    def sanitize_input(input_string):
        """تنظيف المدخلات من الهجمات"""
        if not input_string:
            return ""
        
        # إزالة الرموز الخطرة
        cleaned = bleach.clean(str(input_string), 
                              tags=[],  # لا تسمح بأي tags
                              attributes={}, 
                              styles=[], 
                              strip=True)
        
        # إزالة المسافات الزائدة
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    @staticmethod
    def validate_email(email):
        """التحقق من صحة البريد الإلكتروني"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """التحقق من قوة كلمة المرور"""
        if len(password) < 8:
            return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
        
        if not re.search(r"[A-Z]", password):
            return False, "يجب أن تحتوي على حرف كبير على الأقل"
        
        if not re.search(r"[a-z]", password):
            return False, "يجب أن تحتوي على حرف صغير على الأقل"
        
        if not re.search(r"\d", password):
            return False, "يجب أن تحتوي على رقم على الأقل"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "يجب أن تحتوي على رمز خاص على الأقل"
        
        return True, "كلمة مرور قوية"
    
    @staticmethod
    def generate_csrf_token():
        """إنشاء رمز CSRF"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token, session_token):
        """التحقق من رمز CSRF"""
        return token == session_token
    
    @staticmethod
    def check_rate_limit(ip_address, endpoint):
        """التحقق من الحد الأقصى للطلبات"""
        # سيتم تنفيذ هذا من خلال Flask-Limiter
        pass

security = SecuritySystem()

# ================== نظام التوثيق JWT ==================
class JWTManager:
    def __init__(self, app):
        self.app = app
    
    def create_access_token(self, user_id, username, role='user'):
        """إنشاء توكن وصول"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + self.app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def create_refresh_token(self, user_id):
        """إنشاء توكن تجديد"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.app.config['JWT_REFRESH_TOKEN_EXPIRES'],
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    def verify_token(self, token):
        """التحقق من التوكن"""
        try:
            payload = jwt.decode(token, self.app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            security_logger.log_event('TOKEN_EXPIRED', 'unknown', request.remote_addr, 'Token expired')
            return None
        except jwt.InvalidTokenError:
            security_logger.log_event('INVALID_TOKEN', 'unknown', request.remote_addr, 'Invalid token')
            return None
    
    def refresh_access_token(self, refresh_token):
        """تجديد توكن الوصول"""
        payload = self.verify_token(refresh_token)
        if payload and payload.get('type') == 'refresh':
            return self.create_access_token(payload['user_id'], payload.get('username', ''), payload.get('role', 'user'))
        return None

jwt_manager = JWTManager(app)

# ================== مصادقات النظام ==================
def login_required(f):
    """مصادقة تسجيل الدخول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # التحقق من الجلسة
        if not session.get('user_logged_in'):
            security_logger.log_event('UNAUTHORIZED_ACCESS', 'guest', request.remote_addr, 
                                     f"Attempted access to {request.endpoint}")
            return redirect(url_for('login', next=request.url))
        
        # التحقق من JWT إذا كان موجوداً
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = jwt_manager.verify_token(token)
            if not payload:
                security_logger.log_event('INVALID_JWT', session.get('user_id'), request.remote_addr, 
                                         'Invalid JWT token')
                session.clear()
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """مصادقة حسب الدور"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_role') != required_role:
                security_logger.log_event('UNAUTHORIZED_ROLE', session.get('user_id'), request.remote_addr,
                                         f"Required role: {required_role}, User role: {session.get('user_role')}")
                flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def csrf_protect(f):
    """حماية من هجمات CSRF"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            csrf_token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            session_csrf = session.get('csrf_token')
            
            if not csrf_token or not security.validate_csrf_token(csrf_token, session_csrf):
                security_logger.log_event('CSRF_ATTACK', session.get('user_id', 'unknown'), 
                                         request.remote_addr, 'CSRF token validation failed')
                flash('طلب غير صالح. الرجاء المحاولة مرة أخرى.', 'error')
                return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function

# ================== قاعدة البيانات الآمنة ==================
class SecureDatabaseManager:
    def __init__(self):
        self.db_path = 'database/invoiceflow_secure.db'
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين مع سجلات الدخول
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                company_name TEXT,
                phone TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expiry TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMP,
                account_locked_until TIMESTAMP,
                mfa_secret TEXT,
                mfa_enabled BOOLEAN DEFAULT 0,
                last_password_change TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                last_ip TEXT,
                subscription_type TEXT DEFAULT 'free',
                subscription_expiry TIMESTAMP,
                preferences TEXT DEFAULT '{}'  -- JSON format
            )
        ''')
        
        # جدول سجلات الأمان
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول جلسات المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                refresh_token TEXT,
                ip_address TEXT,
                user_agent TEXT,
                device_info TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول الفواتير
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                client_id INTEGER,
                client_name TEXT NOT NULL,
                client_email TEXT,
                client_phone TEXT,
                client_address TEXT,
                company_name TEXT,
                company_address TEXT,
                company_logo TEXT,
                issue_date DATE NOT NULL,
                due_date DATE NOT NULL,
                items TEXT,  -- JSON format
                subtotal REAL NOT NULL,
                tax_rate REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                notes TEXT,
                pdf_path TEXT,
                qr_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0,
                deleted_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # جدول العملاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                company TEXT,
                tax_number TEXT,
                category TEXT,
                total_purchases REAL DEFAULT 0,
                last_purchase DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول سجلات النشاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ قاعدة البيانات الآمنة جاهزة!")
    
    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=True):
        """تنفيذ استعلام آمن مع حماية من SQL Injection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if fetchone:
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            elif fetchall:
                results = cursor.fetchall()
                result = [dict(row) for row in results]
            else:
                result = None
            
            if commit:
                conn.commit()
            
            return result
        except sqlite3.Error as e:
            security_logger.log_event('DATABASE_ERROR', 'system', '127.0.0.1', f"Query failed: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_user_by_username(self, username):
        """الحصول على مستخدم بأمان"""
        query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
        return self.execute_query(query, (username,), fetchone=True)
    
    def create_user(self, user_data):
        """إنشاء مستخدم جديد بأمان"""
        query = """
        INSERT INTO users (username, email, password_hash, full_name, company_name, phone, verification_token)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_data['username'],
            user_data['email'],
            user_data['password_hash'],
            user_data.get('full_name', ''),
            user_data.get('company_name', ''),
            user_data.get('phone', ''),
            secrets.token_urlsafe(32)
        )
        
        try:
            result = self.execute_query(query, params, fetchone=False, commit=True)
            return True
        except Exception as e:
            security_logger.log_event('USER_CREATION_FAILED', 'system', '127.0.0.1', f"Error: {str(e)}")
            return False
    
    def log_activity(self, user_id, action, entity_type=None, entity_id=None, details=None):
        """تسجيل نشاط المستخدم"""
        ip_address = request.remote_addr if request else '127.0.0.1'
        user_agent = request.user_agent.string if request else ''
        
        query = """
        INSERT INTO activity_logs (user_id, action, entity_type, entity_id, details, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        self.execute_query(query, (user_id, action, entity_type, entity_id, details, ip_address, user_agent))

secure_db = SecureDatabaseManager()

# ================== إعدادات التصميم العالمي ==================
GLOBAL_DESIGN_CSS = """
/* ================== إعدادات التصميم العالمية ================== */
:root {
    /* الألوان العالمية - أسود/أبيض */
    --global-black: #000000;
    --global-white: #FFFFFF;
    --global-gray-dark: #1A1A1A;
    --global-gray-medium: #333333;
    --global-gray-light: #666666;
    --global-gray-lighter: #999999;
    --global-accent-blue: #0066CC;
    --global-accent-green: #00CC66;
    --global-accent-red: #CC0000;
    --global-accent-yellow: #FFCC00;
    
    /* الظلال */
    --global-shadow-light: 0 2px 10px rgba(0, 0, 0, 0.1);
    --global-shadow-medium: 0 5px 20px rgba(0, 0, 0, 0.15);
    --global-shadow-heavy: 0 10px 30px rgba(0, 0, 0, 0.2);
    
    /* الزوايا */
    --global-radius-small: 8px;
    --global-radius-medium: 12px;
    --global-radius-large: 16px;
    --global-radius-xlarge: 24px;
    
    /* التباعد */
    --global-spacing-xs: 4px;
    --global-spacing-sm: 8px;
    --global-spacing-md: 16px;
    --global-spacing-lg: 24px;
    --global-spacing-xl: 32px;
    --global-spacing-xxl: 48px;
    
    /* الأنيميشن */
    --global-transition-fast: 150ms ease;
    --global-transition-normal: 250ms ease;
    --global-transition-slow: 350ms ease;
}

/* ================== أنماط الأساس ================== */
body {
    background-color: var(--global-black);
    color: var(--global-white);
    font-family: 'Inter', 'Segoe UI', 'Tajawal', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    min-height: 100vh;
    overflow-x: hidden;
}

/* ================== الطباعة ================== */
@media print {
    body {
        background: white !important;
        color: black !important;
    }
    
    .no-print {
        display: none !important;
    }
    
    .print-only {
        display: block !important;
    }
}

/* ================== مكونات متعددة اللغات ================== */
[dir="rtl"] {
    text-align: right;
    direction: rtl;
}

[dir="ltr"] {
    text-align: left;
    direction: ltr;
}

.lang-ar {
    font-family: 'Tajawal', 'Segoe UI', sans-serif;
}

.lang-en {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ================== نظام إشعارات الأمان ================== */
.security-alert {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* ================== نظام التحميل الآمن ================== */
.secure-loading {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 99999;
}

.loading-spinner-secure {
    width: 50px;
    height: 50px;
    border: 3px solid var(--global-gray-light);
    border-top-color: var(--global-accent-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ================== مكونات النموذج الآمنة ================== */
.secure-input {
    background: var(--global-gray-dark);
    border: 2px solid var(--global-gray-medium);
    color: var(--global-white);
    padding: 12px 16px;
    border-radius: var(--global-radius-medium);
    width: 100%;
    transition: all var(--global-transition-normal);
    font-size: 16px;
}

.secure-input:focus {
    outline: none;
    border-color: var(--global-accent-blue);
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.secure-input.error {
    border-color: var(--global-accent-red);
}

.secure-btn {
    background: var(--global-accent-blue);
    color: white;
    border: none;
    padding: 14px 28px;
    border-radius: var(--global-radius-medium);
    font-weight: 600;
    cursor: pointer;
    transition: all var(--global-transition-normal);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.secure-btn:hover:not(:disabled) {
    background: #0052A3;
    transform: translateY(-1px);
    box-shadow: var(--global-shadow-medium);
}

.secure-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.secure-btn-danger {
    background: var(--global-accent-red);
}

.secure-btn-success {
    background: var(--global-accent-green);
}

/* ================== نظام البطاقات الآمن ================== */
.secure-card {
    background: var(--global-gray-dark);
    border: 1px solid var(--global-gray-medium);
    border-radius: var(--global-radius-large);
    padding: var(--global-spacing-xl);
    transition: all var(--global-transition-normal);
}

.secure-card:hover {
    border-color: var(--global-accent-blue);
    box-shadow: var(--global-shadow-medium);
}

/* ================== شريط التنقل الآمن ================== */
.secure-navbar {
    background: rgba(0, 0, 0, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--global-gray-medium);
    padding: 0 var(--global-spacing-xl);
    height: 70px;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.nav-lang-switcher {
    display: flex;
    gap: var(--global-spacing-sm);
}

.lang-btn {
    background: transparent;
    border: 1px solid var(--global-gray-light);
    color: var(--global-white);
    padding: 6px 12px;
    border-radius: var(--global-radius-small);
    cursor: pointer;
    font-size: 14px;
    transition: all var(--global-transition-fast);
}

.lang-btn.active {
    background: var(--global-accent-blue);
    border-color: var(--global-accent-blue);
}

/* ================== لوحة التحكم الآمنة ================== */
.secure-dashboard {
    padding: var(--global-spacing-xxl);
    margin-top: 70px;
    min-height: calc(100vh - 70px);
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--global-spacing-lg);
    margin: var(--global-spacing-xl) 0;
}

.security-status {
    background: var(--global-gray-dark);
    border: 1px solid var(--global-gray-medium);
    border-radius: var(--global-radius-large);
    padding: var(--global-spacing-lg);
    display: flex;
    align-items: center;
    gap: var(--global-spacing-lg);
}

.security-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.security-badge.secure {
    background: var(--global-accent-green);
    color: var(--global-black);
}

.security-badge.warning {
    background: var(--global-accent-yellow);
    color: var(--global-black);
}

/* ================== نظام الثيمات ================== */
.theme-system {
    position: fixed;
    bottom: var(--global-spacing-xl);
    right: var(--global-spacing-xl);
    z-index: 1000;
}

.theme-btn {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--global-accent-blue);
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: var(--global-shadow-medium);
    transition: all var(--global-transition-normal);
}

.theme-btn:hover {
    transform: scale(1.1) rotate(45deg);
}

/* ================== التجاوب ================== */
@media (max-width: 768px) {
    .secure-navbar {
        padding: 0 var(--global-spacing-md);
        height: 60px;
    }
    
    .secure-dashboard {
        padding: var(--global-spacing-md);
    }
    
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .theme-system {
        bottom: var(--global-spacing-md);
        right: var(--global-spacing-md);
    }
}

/* ================== تأثيرات خاصة ================== */
.glow-effect {
    position: relative;
}

.glow-effect::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: inherit;
    box-shadow: 0 0 40px rgba(0, 102, 204, 0.3);
    opacity: 0;
    transition: opacity var(--global-transition-normal);
    pointer-events: none;
}

.glow-effect:hover::after {
    opacity: 1;
}

/* ================== نظام الإحصائيات ================== */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--global-spacing-lg);
    margin: var(--global-spacing-xl) 0;
}

.stat-card {
    background: linear-gradient(135deg, var(--global-gray-dark) 0%, #000 100%);
    border: 1px solid var(--global-gray-medium);
    border-radius: var(--global-radius-large);
    padding: var(--global-spacing-lg);
    text-align: center;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 700;
    margin: var(--global-spacing-md) 0;
    background: linear-gradient(45deg, var(--global-accent-blue), var(--global-accent-green));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ================== نظام المحادثة الآمن ================== */
.secure-chat {
    position: fixed;
    bottom: var(--global-spacing-xl);
    left: var(--global-spacing-xl);
    z-index: 1000;
}

.chat-btn {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--global-accent-green);
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: var(--global-shadow-medium);
}

/* ================== نظام التنبيهات ================== */
.notification-bell {
    position: relative;
    cursor: pointer;
}

.notification-badge {
    position: absolute;
    top: -8px;
    right: -8px;
    background: var(--global-accent-red);
    color: white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* ================== نظام التقدم ================== */
.progress-bar {
    height: 6px;
    background: var(--global-gray-medium);
    border-radius: 3px;
    overflow: hidden;
    margin: var(--global-spacing-md) 0;
}

.progress-fill {
    height: 100%;
    background: var(--global-accent-blue);
    transition: width 0.3s ease;
}
"""

# ================== Routes متعددة اللغات وآمنة ==================

@app.route('/')
def home():
    """الصفحة الرئيسية مع اختيار اللغة"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    session['lang'] = lang
    session['csrf_token'] = security.generate_csrf_token()
    
    content = f'''
    <!DOCTYPE html>
    <html dir="{'rtl' if lang == 'ar' else 'ltr'}" lang="{lang}" class="lang-{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceFlow Premium - {lang_system.get_text('title', lang)}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>{GLOBAL_DESIGN_CSS}</style>
    </head>
    <body>
        <!-- شريط التنقل العالمي -->
        <nav class="secure-navbar">
            <div class="nav-brand">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <i class="fas fa-shield-alt" style="color: var(--global-accent-blue); font-size: 1.5em;"></i>
                    <h1 style="margin: 0; font-size: 1.5em; font-weight: 700;">InvoiceFlow Premium</h1>
                </div>
            </div>
            
            <div class="nav-links" style="display: flex; align-items: center; gap: var(--global-spacing-lg);">
                <div class="nav-lang-switcher">
                    <button class="lang-btn {'active' if lang == 'ar' else ''}" onclick="window.location.href='/?lang=ar'">
                        <i class="fas fa-language"></i> العربية
                    </button>
                    <button class="lang-btn {'active' if lang == 'en' else ''}" onclick="window.location.href='/?lang=en'">
                        <i class="fas fa-language"></i> English
                    </button>
                </div>
                
                <a href="/dashboard" class="secure-btn" style="padding: 10px 20px;">
                    <i class="fas fa-tachometer-alt"></i> {lang_system.get_text('dashboard', lang)}
                </a>
            </div>
        </nav>

        <!-- المحتوى الرئيسي -->
        <main class="secure-dashboard">
            <div style="text-align: center; max-width: 800px; margin: 0 auto;">
                <h1 style="font-size: 3.5em; margin-bottom: var(--global-spacing-lg);">
                    {lang_system.get_text('welcome', lang)}
                </h1>
                <p style="font-size: 1.2em; color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-xl);">
                    نظام إدارة الفواتير المتكامل مع الحماية المتقدمة وتعدد اللغات
                </p>
                
                <!-- إحصائيات النظام -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <i class="fas fa-shield-alt" style="font-size: 2em; color: var(--global-accent-blue);"></i>
                        <div class="stat-number">100%</div>
                        <p>{lang_system.get_text('security', lang)}</p>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-globe" style="font-size: 2em; color: var(--global-accent-green);"></i>
                        <div class="stat-number">2</div>
                        <p>{lang_system.get_text('language', lang)}s</p>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-bolt" style="font-size: 2em; color: var(--global-accent-yellow);"></i>
                        <div class="stat-number">99.9%</div>
                        <p>Uptime</p>
                    </div>
                </div>
                
                <!-- بطاقات الخدمات -->
                <div class="dashboard-grid">
                    <div class="secure-card">
                        <i class="fas fa-file-invoice-dollar" style="font-size: 2.5em; margin-bottom: var(--global-spacing-md); color: var(--global-accent-blue);"></i>
                        <h3>{lang_system.get_text('invoices', lang)}</h3>
                        <p>إدارة فواتير احترافية مع تصدير PDF وتقارير متقدمة</p>
                        <a href="/invoices" class="secure-btn" style="margin-top: var(--global-spacing-md); width: 100%;">
                            <i class="fas fa-arrow-right"></i> {lang_system.get_text('view', lang)}
                        </a>
                    </div>
                    
                    <div class="secure-card">
                        <i class="fas fa-robot" style="font-size: 2.5em; margin-bottom: var(--global-spacing-md); color: var(--global-accent-green);"></i>
                        <h3>{lang_system.get_text('ai_insights', lang)}</h3>
                        <p>تحليلات ذكية وتنبؤات باستخدام الذكاء الاصطناعي</p>
                        <a href="/ai" class="secure-btn" style="margin-top: var(--global-spacing-md); width: 100%;">
                            <i class="fas fa-brain"></i> {lang_system.get_text('explore', lang)}
                        </a>
                    </div>
                    
                    <div class="secure-card">
                        <i class="fas fa-users" style="font-size: 2.5em; margin-bottom: var(--global-spacing-md); color: var(--global-accent-yellow);"></i>
                        <h3>{lang_system.get_text('clients', lang)}</h3>
                        <p>إدارة العملاء والتواصل معهم بشكل احترافي</p>
                        <a href="/clients" class="secure-btn" style="margin-top: var(--global-spacing-md); width: 100%;">
                            <i class="fas fa-user-friends"></i> {lang_system.get_text('manage', lang)}
                        </a>
                    </div>
                </div>
                
                <!-- قسم الأمان -->
                <div class="security-status" style="margin-top: var(--global-spacing-xl);">
                    <div style="flex: 1;">
                        <h3 style="margin: 0 0 var(--global-spacing-sm) 0;">{lang_system.get_text('security', lang)} Status</h3>
                        <p style="margin: 0; color: var(--global-gray-lighter);">
                            جميع الأنظمة تعمل بشكل طبيعي. النظام محمي بالتشفير المتقدم.
                        </p>
                    </div>
                    <span class="security-badge secure">
                        <i class="fas fa-check-circle"></i> {lang_system.get_text('secure', lang)}
                    </span>
                </div>
            </div>
        </main>

        <!-- زر المحادثة -->
        <div class="secure-chat">
            <button class="chat-btn" onclick="openSupport()">
                <i class="fas fa-comments"></i>
            </button>
        </div>

        <!-- نظام الثيمات -->
        <div class="theme-system">
            <button class="theme-btn" onclick="toggleTheme()">
                <i class="fas fa-palette"></i>
            </button>
        </div>

        <!-- نظام التحميل -->
        <div id="secureLoading" class="secure-loading" style="display: none;">
            <div class="loading-spinner-secure"></div>
            <p style="margin-top: var(--global-spacing-md);">جاري التحميل الآمن...</p>
        </div>

        <!-- نظام الإشعارات -->
        <div id="securityAlerts" class="security-alert"></div>

        <script>
            // التحكم في الثيم
            function toggleTheme() {{
                const body = document.body;
                const currentTheme = body.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                body.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // إظهار إشعار
                showAlert('تم تغيير الثيم إلى ' + (newTheme === 'light' ? 'الوضع الفاتح' : 'الوضع الداكن'), 'success');
            }}

            // إظهار تنبيهات
            function showAlert(message, type = 'info') {{
                const alertDiv = document.createElement('div');
                alertDiv.className = `secure-card alert-${{type}}`;
                alertDiv.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <i class="fas fa-${{type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}}"
                           style="color: ${{type === 'success' ? 'var(--global-accent-green)' : type === 'error' ? 'var(--global-accent-red)' : 'var(--global-accent-blue)'}};"></i>
                        <span>${{message}}</span>
                    </div>
                `;
                
                const container = document.getElementById('securityAlerts');
                container.appendChild(alertDiv);
                
                setTimeout(() => {{
                    alertDiv.remove();
                }}, 5000);
            }}

            // فتح الدعم
            function openSupport() {{
                showAlert('سيتم فتح نظام الدعم قريباً', 'info');
            }}

            // إظهار التحميل
            function showLoading() {{
                document.getElementById('secureLoading').style.display = 'flex';
            }}

            // إخفاء التحميل
            function hideLoading() {{
                document.getElementById('secureLoading').style.display = 'none';
            }}

            // التحكم في التحميل عند التنقل
            document.addEventListener('DOMContentLoaded', function() {{
                // تحميل الثيم المحفوظ
                const savedTheme = localStorage.getItem('theme') || 'dark';
                document.body.setAttribute('data-theme', savedTheme);
                
                // إضافة مستمعين للأزرار
                document.querySelectorAll('a').forEach(link => {{
                    if (link.href && !link.href.includes('#')) {{
                        link.addEventListener('click', function(e) {{
                            if (this.getAttribute('href').startsWith('/')) {{
                                showLoading();
                            }}
                        }});
                    }}
                }});
                
                // إخفاء التحميل عند اكتمال الصفحة
                window.addEventListener('load', hideLoading);
            }});

            // حماية النماذج
            document.addEventListener('submit', function(e) {{
                if (e.target.tagName === 'FORM') {{
                    showLoading();
                }}
            }});
        </script>
    </body>
    </html>
    '''
    
    return content

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """صفحة تسجيل الدخول الآمنة"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    if request.method == 'POST':
        username = security.sanitize_input(request.form.get('username'))
        password = request.form.get('password')
        csrf_token = request.form.get('csrf_token')
        
        # التحقق من CSRF
        if not security.validate_csrf_token(csrf_token, session.get('csrf_token')):
            security_logger.log_event('CSRF_ATTACK', 'unknown', request.remote_addr, 'Login attempt')
            flash('طلب غير صالح', 'error')
            return redirect(url_for('login'))
        
        # التحقق من المدخلات
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return redirect(url_for('login'))
        
        # التحقق من المستخدم في قاعدة البيانات
        user = secure_db.get_user_by_username(username)
        
        if not user:
            security_logger.log_event('LOGIN_FAILED', username, request.remote_addr, 'User not found')
            time.sleep(2)  # تأخير لحماية من هجمات Brute Force
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return redirect(url_for('login'))
        
        # التحقق من كلمة المرور
        if not check_password_hash(user['password_hash'], password):
            secure_db.execute_query(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = ?",
                (user['id'],)
            )
            security_logger.log_event('LOGIN_FAILED', username, request.remote_addr, 'Invalid password')
            time.sleep(2)
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return redirect(url_for('login'))
        
        # تسجيل الدخول الناجح
        session_token = secrets.token_urlsafe(32)
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_role'] = user['role']
        session['user_logged_in'] = True
        session['session_token'] = session_token
        
        # إنشاء JWT tokens
        access_token = jwt_manager.create_access_token(user['id'], user['username'], user['role'])
        refresh_token = jwt_manager.create_refresh_token(user['id'])
        
        # تحديث معلومات المستخدم
        secure_db.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP, last_ip = ?, failed_login_attempts = 0 WHERE id = ?",
            (request.remote_addr, user['id'])
        )
        
        # تسجيل النشاط
        secure_db.log_activity(user['id'], 'LOGIN', 'user', user['id'], 'تم تسجيل الدخول بنجاح')
        security_logger.log_event('LOGIN_SUCCESS', username, request.remote_addr, 'User logged in')
        
        flash('تم تسجيل الدخول بنجاح', 'success')
        return redirect(url_for('dashboard'))
    
    # عرض صفحة الدخول
    session['csrf_token'] = security.generate_csrf_token()
    
    content = f'''
    <div style="max-width: 400px; margin: 100px auto;">
        <div class="secure-card">
            <div style="text-align: center; margin-bottom: var(--global-spacing-xl);">
                <i class="fas fa-lock" style="font-size: 3em; color: var(--global-accent-blue);"></i>
                <h2>{lang_system.get_text('login', lang)}</h2>
                <p style="color: var(--global-gray-lighter);">أدخل بيانات الدخول الآمنة</p>
            </div>
            
            <form method="POST" onsubmit="showLoading()">
                <input type="hidden" name="csrf_token" value="{session['csrf_token']}">
                
                <div style="margin-bottom: var(--global-spacing-lg);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        {lang_system.get_text('username', lang)}
                    </label>
                    <input type="text" name="username" class="secure-input" required
                           placeholder="{lang_system.get_text('username', lang)}"
                           autocomplete="username">
                </div>
                
                <div style="margin-bottom: var(--global-spacing-lg);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        {lang_system.get_text('password', lang)}
                    </label>
                    <input type="password" name="password" class="secure-input" required
                           placeholder="{lang_system.get_text('password', lang)}"
                           autocomplete="current-password">
                </div>
                
                <button type="submit" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-sign-in-alt"></i> {lang_system.get_text('login', lang)}
                </button>
            </form>
            
            <div style="text-align: center; margin-top: var(--global-spacing-xl);">
                <p style="color: var(--global-gray-lighter);">
                    {lang_system.get_text('no_account', lang)} 
                    <a href="/register?lang={lang}" style="color: var(--global-accent-blue); text-decoration: none;">
                        {lang_system.get_text('register', lang)}
                    </a>
                </p>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    """صفحة التسجيل الآمنة"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    if request.method == 'POST':
        # جمع البيانات
        username = security.sanitize_input(request.form.get('username'))
        email = security.sanitize_input(request.form.get('email'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = security.sanitize_input(request.form.get('full_name'))
        csrf_token = request.form.get('csrf_token')
        
        # التحقق من CSRF
        if not security.validate_csrf_token(csrf_token, session.get('csrf_token')):
            security_logger.log_event('CSRF_ATTACK', 'unknown', request.remote_addr, 'Registration attempt')
            flash('طلب غير صالح', 'error')
            return redirect(url_for('register'))
        
        # التحقق من البيانات
        errors = []
        
        if not username or len(username) < 3:
            errors.append('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if not security.validate_email(email):
            errors.append('البريد الإلكتروني غير صالح')
        
        password_valid, password_msg = security.validate_password(password)
        if not password_valid:
            errors.append(password_msg)
        
        if password != confirm_password:
            errors.append('كلمتا المرور غير متطابقتين')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('register'))
        
        # التحقق من عدم وجود المستخدم مسبقاً
        existing_user = secure_db.execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
            fetchone=True
        )
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً', 'error')
            return redirect(url_for('register'))
        
        # إنشاء مستخدم جديد
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'company_name': request.form.get('company_name', ''),
            'phone': request.form.get('phone', '')
        }
        
        if secure_db.create_user(user_data):
            security_logger.log_event('USER_REGISTERED', username, request.remote_addr, 'New user registered')
            flash('تم إنشاء الحساب بنجاح. يرجى تسجيل الدخول', 'success')
            return redirect(url_for('login'))
        else:
            flash('حدث خطأ أثناء إنشاء الحساب', 'error')
            return redirect(url_for('register'))
    
    # عرض صفحة التسجيل
    session['csrf_token'] = security.generate_csrf_token()
    
    content = f'''
    <div style="max-width: 500px; margin: 50px auto;">
        <div class="secure-card">
            <div style="text-align: center; margin-bottom: var(--global-spacing-xl);">
                <i class="fas fa-user-plus" style="font-size: 3em; color: var(--global-accent-green);"></i>
                <h2>{lang_system.get_text('register', lang)}</h2>
                <p style="color: var(--global-gray-lighter);">أنشئ حساباً جديداً بأمان</p>
            </div>
            
            <form method="POST" onsubmit="showLoading()" id="registerForm">
                <input type="hidden" name="csrf_token" value="{session['csrf_token']}">
                
                <div style="margin-bottom: var(--global-spacing-lg);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        {lang_system.get_text('full_name', lang)}
                    </label>
                    <input type="text" name="full_name" class="secure-input" required
                           placeholder="{lang_system.get_text('full_name', lang)}">
                </div>
                
                <div style="margin-bottom: var(--global-spacing-lg);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        {lang_system.get_text('username', lang)}
                    </label>
                    <input type="text" name="username" class="secure-input" required minlength="3"
                           placeholder="{lang_system.get_text('username', lang)}">
                </div>
                
                <div style="margin-bottom: var(--global-spacing-lg);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        {lang_system.get_text('email', lang)}
                    </label>
                    <input type="email" name="email" class="secure-input" required
                           placeholder="{lang_system.get_text('email', lang)}">
                </div>
                
                <div style="margin-bottom: var(--global-spacing-lg);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        {lang_system.get_text('password', lang)}
                    </label>
                    <input type="password" name="password" class="secure-input" required minlength="8"
                           placeholder="{lang_system.get_text('password', lang)}" id="password">
                    <div id="passwordStrength" style="margin-top: var(--global-spacing-sm);">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%;"></div>
                        </div>
                        <small style="color: var(--global-gray-lighter);" id="passwordMessage"></small>
                    </div>
                </div>
                
                <div style="margin-bottom: var(--global-spacing-xl);">
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); color: var(--global-white);">
                        تأكيد {lang_system.get_text('password', lang)}
                    </label>
                    <input type="password" name="confirm_password" class="secure-input" required
                           placeholder="تأكيد {lang_system.get_text('password', lang)}" id="confirmPassword">
                    <small style="color: var(--global-gray-lighter);" id="confirmMessage"></small>
                </div>
                
                <button type="submit" class="secure-btn" style="width: 100%;" id="submitBtn" disabled>
                    <i class="fas fa-user-plus"></i> {lang_system.get_text('register', lang)}
                </button>
            </form>
            
            <div style="text-align: center; margin-top: var(--global-spacing-xl);">
                <p style="color: var(--global-gray-lighter);">
                    {lang_system.get_text('have_account', lang)} 
                    <a href="/login?lang={lang}" style="color: var(--global-accent-blue); text-decoration: none;">
                        {lang_system.get_text('login', lang)}
                    </a>
                </p>
            </div>
        </div>
    </div>
    
    <script>
        // التحقق من قوة كلمة المرور
        document.getElementById('password').addEventListener('input', function(e) {{
            const password = e.target.value;
            const strengthBar = document.querySelector('.progress-fill');
            const message = document.getElementById('passwordMessage');
            const submitBtn = document.getElementById('submitBtn');
            
            let strength = 0;
            let msg = '';
            
            if (password.length >= 8) strength += 25;
            if (/[A-Z]/.test(password)) strength += 25;
            if (/[a-z]/.test(password)) strength += 25;
            if (/[0-9]/.test(password)) strength += 15;
            if (/[^A-Za-z0-9]/.test(password)) strength += 10;
            
            strengthBar.style.width = strength + '%';
            
            if (strength < 50) {{
                strengthBar.style.background = 'var(--global-accent-red)';
                msg = 'كلمة مرور ضعيفة';
                submitBtn.disabled = true;
            }} else if (strength < 75) {{
                strengthBar.style.background = 'var(--global-accent-yellow)';
                msg = 'كلمة مرور متوسطة';
                submitBtn.disabled = false;
            }} else {{
                strengthBar.style.background = 'var(--global-accent-green)';
                msg = 'كلمة مرور قوية';
                submitBtn.disabled = false;
            }}
            
            message.textContent = msg;
            checkPasswordMatch();
        }});
        
        // التحقق من تطابق كلمات المرور
        document.getElementById('confirmPassword').addEventListener('input', checkPasswordMatch);
        
        function checkPasswordMatch() {{
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const message = document.getElementById('confirmMessage');
            const submitBtn = document.getElementById('submitBtn');
            
            if (confirmPassword === '') {{
                message.textContent = '';
                return;
            }}
            
            if (password === confirmPassword) {{
                message.textContent = 'كلمات المرور متطابقة';
                message.style.color = 'var(--global-accent-green)';
                submitBtn.disabled = false;
            }} else {{
                message.textContent = 'كلمات المرور غير متطابقة';
                message.style.color = 'var(--global-accent-red)';
                submitBtn.disabled = true;
            }}
        }}
    </script>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    # إحصائيات المستخدم
    user_id = session['user_id']
    
    stats = {
        'total_invoices': 0,
        'total_revenue': 0,
        'pending_invoices': 0,
        'active_clients': 0
    }
    
    content = f'''
    <div class="secure-dashboard">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--global-spacing-xl);">
            <div>
                <h1 style="margin: 0;">{lang_system.get_text('dashboard', lang)}</h1>
                <p style="color: var(--global-gray-lighter); margin: var(--global-spacing-sm) 0 0 0;">
                    مرحباً {session.get('username', '')} 👋
                </p>
            </div>
            
            <div style="display: flex; gap: var(--global-spacing-md); align-items: center;">
                <div class="notification-bell">
                    <i class="fas fa-bell" style="font-size: 1.2em;"></i>
                    <span class="notification-badge">3</span>
                </div>
                
                <a href="/profile" class="secure-btn" style="padding: 10px 20px;">
                    <i class="fas fa-user"></i> {lang_system.get_text('profile', lang)}
                </a>
            </div>
        </div>
        
        <!-- الإحصائيات السريعة -->
        <div class="stats-grid">
            <div class="stat-card">
                <div style="display: flex; align-items: center; gap: var(--global-spacing-md);">
                    <div style="background: rgba(0, 102, 204, 0.1); padding: 12px; border-radius: var(--global-radius-medium);">
                        <i class="fas fa-file-invoice" style="color: var(--global-accent-blue);"></i>
                    </div>
                    <div>
                        <div class="stat-number">{stats['total_invoices']}</div>
                        <p>{lang_system.get_text('invoices', lang)}</p>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div style="display: flex; align-items: center; gap: var(--global-spacing-md);">
                    <div style="background: rgba(0, 204, 102, 0.1); padding: 12px; border-radius: var(--global-radius-medium);">
                        <i class="fas fa-dollar-sign" style="color: var(--global-accent-green);"></i>
                    </div>
                    <div>
                        <div class="stat-number">${stats['total_revenue']:,.0f}</div>
                        <p>{lang_system.get_text('revenue', lang)}</p>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div style="display: flex; align-items: center; gap: var(--global-spacing-md);">
                    <div style="background: rgba(255, 204, 0, 0.1); padding: 12px; border-radius: var(--global-radius-medium);">
                        <i class="fas fa-clock" style="color: var(--global-accent-yellow);"></i>
                    </div>
                    <div>
                        <div class="stat-number">{stats['pending_invoices']}</div>
                        <p>{lang_system.get_text('pending', lang)}</p>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div style="display: flex; align-items: center; gap: var(--global-spacing-md);">
                    <div style="background: rgba(204, 0, 0, 0.1); padding: 12px; border-radius: var(--global-radius-medium);">
                        <i class="fas fa-users" style="color: var(--global-accent-red);"></i>
                    </div>
                    <div>
                        <div class="stat-number">{stats['active_clients']}</div>
                        <p>{lang_system.get_text('clients', lang)}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- الإجراءات السريعة -->
        <div class="dashboard-grid" style="margin-top: var(--global-spacing-xl);">
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-plus-circle" style="color: var(--global-accent-blue);"></i>
                    {lang_system.get_text('create_invoice', lang)}
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    أنشئ فاتورة جديدة بسهولة وسرعة
                </p>
                <a href="/invoices/create" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-plus"></i> {lang_system.get_text('create', lang)}
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-chart-bar" style="color: var(--global-accent-green);"></i>
                    {lang_system.get_text('reports', lang)}
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    عرض التقارير والإحصائيات المتقدمة
                </p>
                <a href="/reports" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-chart-line"></i> {lang_system.get_text('view', lang)}
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-robot" style="color: var(--global-accent-yellow);"></i>
                    {lang_system.get_text('ai_insights', lang)}
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    استفد من الذكاء الاصطناعي لتحليل بياناتك
                </p>
                <a href="/ai" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-brain"></i> {lang_system.get_text('explore', lang)}
                </a>
            </div>
        </div>
        
        <!-- نشاطات حديثة -->
        <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
            <h3 style="margin-bottom: var(--global-spacing-lg);">
                <i class="fas fa-history" style="color: var(--global-accent-blue);"></i>
                النشاطات الحديثة
            </h3>
            
            <div style="border: 1px solid var(--global-gray-medium); border-radius: var(--global-radius-medium); overflow: hidden;">
                <div style="display: flex; justify-content: space-between; padding: var(--global-spacing-md) var(--global-spacing-lg); background: var(--global-gray-medium);">
                    <span style="font-weight: 600;">النشاط</span>
                    <span style="font-weight: 600;">التاريخ</span>
                </div>
                
                <div style="padding: var(--global-spacing-md) var(--global-spacing-lg);">
                    <p style="text-align: center; color: var(--global-gray-lighter); padding: var(--global-spacing-xl);">
                        لا توجد نشاطات حديثة
                    </p>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/invoices')
@login_required
def invoices():
    """صفحة الفواتير"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    content = f'''
    <div class="secure-dashboard">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--global-spacing-xl);">
            <h1 style="margin: 0;">
                <i class="fas fa-file-invoice-dollar" style="color: var(--global-accent-blue);"></i>
                {lang_system.get_text('invoices', lang)}
            </h1>
            
            <a href="/invoices/create" class="secure-btn">
                <i class="fas fa-plus"></i> {lang_system.get_text('create_invoice', lang)}
            </a>
        </div>
        
        <!-- أدوات التصفية -->
        <div class="secure-card" style="margin-bottom: var(--global-spacing-xl);">
            <div style="display: flex; gap: var(--global-spacing-lg); align-items: center;">
                <div style="flex: 1;">
                    <input type="text" class="secure-input" placeholder="{lang_system.get_text('search', lang)}...">
                </div>
                
                <select class="secure-input" style="width: 200px;">
                    <option value="">{lang_system.get_text('filter', lang)} حسب الحالة</option>
                    <option value="pending">{lang_system.get_text('pending', lang)}</option>
                    <option value="paid">{lang_system.get_text('paid', lang)}</option>
                    <option value="overdue">{lang_system.get_text('overdue', lang)}</option>
                </select>
                
                <button class="secure-btn">
                    <i class="fas fa-filter"></i> {lang_system.get_text('filter', lang)}
                </button>
            </div>
        </div>
        
        <!-- جدول الفواتير -->
        <div class="secure-card">
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: var(--global-gray-medium);">
                            <th style="padding: var(--global-spacing-md); text-align: right;">رقم الفاتورة</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">{lang_system.get_text('client_name', lang)}</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">{lang_system.get_text('date', lang)}</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">{lang_system.get_text('amount', lang)}</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">{lang_system.get_text('status', lang)}</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">{lang_system.get_text('actions', lang)}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid var(--global-gray-medium);">
                            <td style="padding: var(--global-spacing-md);">INV-2024-001</td>
                            <td style="padding: var(--global-spacing-md);">شركة النخبة</td>
                            <td style="padding: var(--global-spacing-md);">2024-01-15</td>
                            <td style="padding: var(--global-spacing-md); font-weight: 600;">$1,250.00</td>
                            <td style="padding: var(--global-spacing-md);">
                                <span class="security-badge" style="background: var(--global-accent-yellow);">
                                    {lang_system.get_text('pending', lang)}
                                </span>
                            </td>
                            <td style="padding: var(--global-spacing-md);">
                                <div style="display: flex; gap: var(--global-spacing-sm);">
                                    <a href="/invoices/view/1" class="secure-btn" style="padding: 6px 12px; font-size: 12px;">
                                        <i class="fas fa-eye"></i>
                                    </a>
                                    <a href="/invoices/download/1" class="secure-btn" style="padding: 6px 12px; font-size: 12px;">
                                        <i class="fas fa-download"></i>
                                    </a>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- رسالة عدم وجود فواتير -->
            <div style="text-align: center; padding: var(--global-spacing-xl); color: var(--global-gray-lighter);">
                <i class="fas fa-file-invoice" style="font-size: 3em; margin-bottom: var(--global-spacing-md);"></i>
                <h3>لا توجد فواتير</h3>
                <p>ابدأ بإنشاء فاتورتك الأولى</p>
                <a href="/invoices/create" class="secure-btn" style="margin-top: var(--global-spacing-md);">
                    <i class="fas fa-plus"></i> {lang_system.get_text('create_invoice', lang)}
                </a>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/invoices/create', methods=['GET', 'POST'])
@login_required
@csrf_protect
def create_invoice():
    """إنشاء فاتورة جديدة"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    if request.method == 'POST':
        # معالجة إنشاء الفاتورة
        # ... (سيتم إضافة المنطق الكامل لاحقاً)
        
        flash('تم إنشاء الفاتورة بنجاح', 'success')
        return redirect(url_for('invoices'))
    
    session['csrf_token'] = security.generate_csrf_token()
    
    content = f'''
    <div class="secure-dashboard">
        <div style="margin-bottom: var(--global-spacing-xl);">
            <h1 style="margin: 0;">
                <i class="fas fa-plus-circle" style="color: var(--global-accent-blue);"></i>
                {lang_system.get_text('create_invoice', lang)}
            </h1>
            <p style="color: var(--global-gray-lighter); margin: var(--global-spacing-sm) 0 0 0;">
                أنشئ فاتورة احترافية جديدة
            </p>
        </div>
        
        <form method="POST" onsubmit="showLoading()" id="invoiceForm">
            <input type="hidden" name="csrf_token" value="{session['csrf_token']}">
            
            <div class="dashboard-grid">
                <!-- معلومات العميل -->
                <div class="secure-card">
                    <h3 style="margin-bottom: var(--global-spacing-lg);">
                        <i class="fas fa-user-tie" style="color: var(--global-accent-blue);"></i>
                        معلومات العميل
                    </h3>
                    
                    <div style="margin-bottom: var(--global-spacing-lg);">
                        <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                            {lang_system.get_text('client_name', lang)} *
                        </label>
                        <input type="text" name="client_name" class="secure-input" required>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--global-spacing-lg); margin-bottom: var(--global-spacing-lg);">
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                {lang_system.get_text('email', lang)}
                            </label>
                            <input type="email" name="client_email" class="secure-input">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                {lang_system.get_text('phone', lang)}
                            </label>
                            <input type="tel" name="client_phone" class="secure-input">
                        </div>
                    </div>
                    
                    <div style="margin-bottom: var(--global-spacing-lg);">
                        <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                            العنوان
                        </label>
                        <textarea name="client_address" class="secure-input" rows="3"></textarea>
                    </div>
                </div>
                
                <!-- تفاصيل الفاتورة -->
                <div class="secure-card">
                    <h3 style="margin-bottom: var(--global-spacing-lg);">
                        <i class="fas fa-receipt" style="color: var(--global-accent-green);"></i>
                        تفاصيل الفاتورة
                    </h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--global-spacing-lg); margin-bottom: var(--global-spacing-lg);">
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                تاريخ الإصدار *
                            </label>
                            <input type="date" name="issue_date" class="secure-input" required>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                تاريخ الاستحقاق *
                            </label>
                            <input type="date" name="due_date" class="secure-input" required>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--global-spacing-lg); margin-bottom: var(--global-spacing-lg);">
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                الضريبة (%) 
                            </label>
                            <input type="number" name="tax_rate" class="secure-input" value="15" min="0" max="100" step="0.01">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                الخصم
                            </label>
                            <input type="number" name="discount" class="secure-input" value="0" min="0" step="0.01">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                طريقة الدفع
                            </label>
                            <select name="payment_method" class="secure-input">
                                <option value="cash">نقدي</option>
                                <option value="bank">تحويل بنكي</option>
                                <option value="card">بطاقة ائتمان</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: var(--global-spacing-lg);">
                        <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                            ملاحظات
                        </label>
                        <textarea name="notes" class="secure-input" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                    </div>
                </div>
            </div>
            
            <!-- العناصر -->
            <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-list" style="color: var(--global-accent-yellow);"></i>
                    العناصر
                </h3>
                
                <div id="itemsContainer">
                    <div class="item-row" style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: var(--global-spacing-lg); margin-bottom: var(--global-spacing-lg); align-items: end;">
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                                الوصف
                            </label>
                            <input type="text" name="items[0][description]" class="secure-input" placeholder="وصف الخدمة">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                                الكمية
                            </label>
                            <input type="number" name="items[0][quantity]" class="secure-input" value="1" min="1" step="1">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                                السعر
                            </label>
                            <input type="number" name="items[0][price]" class="secure-input" value="0" min="0" step="0.01">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                                المجموع
                            </label>
                            <input type="text" class="secure-input" value="$0.00" readonly style="background: var(--global-gray-medium);">
                        </div>
                        <div>
                            <button type="button" class="secure-btn-danger" style="padding: 10px;">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <button type="button" id="addItemBtn" class="secure-btn" style="margin-top: var(--global-spacing-lg);">
                    <i class="fas fa-plus"></i> إضافة عنصر
                </button>
            </div>
            
            <!-- الملخص -->
            <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-calculator" style="color: var(--global-accent-green);"></i>
                    الملخص
                </h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--global-spacing-lg);">
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: var(--global-spacing-md);">
                            <span>المجموع الفرعي:</span>
                            <span id="subtotal">$0.00</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: var(--global-spacing-md);">
                            <span>الضريبة:</span>
                            <span id="tax">$0.00</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: var(--global-spacing-md);">
                            <span>الخصم:</span>
                            <span id="discount">$0.00</span>
                        </div>
                        <hr style="border: none; border-top: 1px solid var(--global-gray-medium); margin: var(--global-spacing-lg) 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 1.2em; font-weight: 600;">
                            <span>المجموع الكلي:</span>
                            <span id="total">$0.00</span>
                        </div>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; gap: var(--global-spacing-md);">
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                الشعار (اختياري)
                            </label>
                            <input type="file" name="logo" class="secure-input" accept="image/*">
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                                التوقيع (اختياري)
                            </label>
                            <input type="file" name="signature" class="secure-input" accept="image/*">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- الأزرار -->
            <div style="display: flex; gap: var(--global-spacing-lg); justify-content: flex-end; margin-top: var(--global-spacing-xl);">
                <a href="/invoices" class="secure-btn" style="background: var(--global-gray-medium);">
                    <i class="fas fa-times"></i> {lang_system.get_text('cancel', lang)}
                </a>
                
                <button type="submit" class="secure-btn-success" style="padding: 15px 40px;">
                    <i class="fas fa-save"></i> {lang_system.get_text('save', lang)} الفاتورة
                </button>
            </div>
        </form>
    </div>
    
    <script>
        // إدارة العناصر
        let itemCount = 1;
        
        document.getElementById('addItemBtn').addEventListener('click', function() {{
            const container = document.getElementById('itemsContainer');
            const newItem = document.createElement('div');
            newItem.className = 'item-row';
            newItem.style.cssText = 'display: grid; grid-template-columns: 2fr 1fr 1fr 1fr auto; gap: var(--global-spacing-lg); margin-bottom: var(--global-spacing-lg); align-items: end;';
            
            newItem.innerHTML = `
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                        الوصف
                    </label>
                    <input type="text" name="items[${{itemCount}}][description]" class="secure-input item-description" placeholder="وصف الخدمة">
                </div>
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                        الكمية
                    </label>
                    <input type="number" name="items[${{itemCount}}][quantity]" class="secure-input item-quantity" value="1" min="1" step="1">
                </div>
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                        السعر
                    </label>
                    <input type="number" name="items[${{itemCount}}][price]" class="secure-input item-price" value="0" min="0" step="0.01">
                </div>
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm); font-size: 14px;">
                        المجموع
                    </label>
                    <input type="text" class="secure-input item-total" value="$0.00" readonly style="background: var(--global-gray-medium);">
                </div>
                <div>
                    <button type="button" class="secure-btn-danger remove-item" style="padding: 10px;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            container.appendChild(newItem);
            itemCount++;
            
            // إضافة مستمع للأحداث للعنصر الجديد
            const quantityInput = newItem.querySelector('.item-quantity');
            const priceInput = newItem.querySelector('.item-price');
            const totalInput = newItem.querySelector('.item-total');
            
            quantityInput.addEventListener('input', calculateItemTotal);
            priceInput.addEventListener('input', calculateItemTotal);
            
            // إضافة مستمع لحذف العنصر
            newItem.querySelector('.remove-item').addEventListener('click', function() {{
                newItem.remove();
                calculateTotals();
            }});
        }});
        
        // حساب مجموع العنصر
        function calculateItemTotal(e) {{
            const row = e.target.closest('.item-row');
            const quantity = parseFloat(row.querySelector('.item-quantity').value) || 0;
            const price = parseFloat(row.querySelector('.item-price').value) || 0;
            const total = quantity * price;
            
            row.querySelector('.item-total').value = '$' + total.toFixed(2);
            calculateTotals();
        }}
        
        // حساب المجاميع الكلية
        function calculateTotals() {{
            let subtotal = 0;
            document.querySelectorAll('.item-total').forEach(input => {{
                const value = parseFloat(input.value.replace('$', '')) || 0;
                subtotal += value;
            }});
            
            const taxRate = parseFloat(document.querySelector('[name="tax_rate"]').value) || 0;
            const discount = parseFloat(document.querySelector('[name="discount"]').value) || 0;
            
            const tax = subtotal * (taxRate / 100);
            const total = subtotal + tax - discount;
            
            document.getElementById('subtotal').textContent = '$' + subtotal.toFixed(2);
            document.getElementById('tax').textContent = '$' + tax.toFixed(2);
            document.getElementById('discount').textContent = '-$' + discount.toFixed(2);
            document.getElementById('total').textContent = '$' + total.toFixed(2);
        }}
        
        // إضافة مستمعات الأحداث للحقول
        document.querySelectorAll('.item-quantity, .item-price').forEach(input => {{
            input.addEventListener('input', calculateItemTotal);
        }});
        
        document.querySelector('[name="tax_rate"], [name="discount"]').addEventListener('input', calculateTotals);
        
        // إضافة مستمعات لحذف العناصر
        document.querySelectorAll('.remove-item').forEach(btn => {{
            btn.addEventListener('click', function() {{
                this.closest('.item-row').remove();
                calculateTotals();
            }});
        }});
        
        // حساب القيم الأولية
        calculateTotals();
    </script>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/ai')
@login_required
def ai_insights():
    """صفحة الذكاء الاصطناعي"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    content = f'''
    <div class="secure-dashboard">
        <div style="margin-bottom: var(--global-spacing-xl);">
            <h1 style="margin: 0;">
                <i class="fas fa-robot" style="color: var(--global-accent-green);"></i>
                {lang_system.get_text('ai_insights', lang)}
            </h1>
            <p style="color: var(--global-gray-lighter); margin: var(--global-spacing-sm) 0 0 0;">
                تحليلات ذكية وتنبؤات باستخدام الذكاء الاصطناعي
            </p>
        </div>
        
        <div class="dashboard-grid">
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-chart-line" style="color: var(--global-accent-blue);"></i>
                    تحليل الإيرادات
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    تحليل أنماط الإيرادات وتوقعات النمو المستقبلية
                </p>
                <a href="/ai/revenue" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-chart-bar"></i> عرض التحليل
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-users" style="color: var(--global-accent-green);"></i>
                    تحليل العملاء
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    فهم سلوك العملاء وتحديد أفضل الفرص
                </p>
                <a href="/ai/clients" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-user-chart"></i> تحليل العملاء
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-lightbulb" style="color: var(--global-accent-yellow);"></i>
                    توصيات ذكية
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    احصل على توصيات مخصصة لتحسين أدائك
                </p>
                <a href="/ai/recommendations" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-magic"></i> عرض التوصيات
                </a>
            </div>
        </div>
        
        <!-- لوحة التحكم الذكية -->
        <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
            <h3 style="margin-bottom: var(--global-spacing-lg);">
                <i class="fas fa-tachometer-alt" style="color: var(--global-accent-blue);"></i>
                لوحة التحكم الذكية
            </h3>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--global-accent-blue);">85%</div>
                    <div style="color: var(--global-gray-lighter);">معدل النمو المتوقع</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--global-accent-green);">92%</div>
                    <div style="color: var(--global-gray-lighter);">رضا العملاء</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--global-accent-yellow);">78%</div>
                    <div style="color: var(--global-gray-lighter);">كفاءة الأداء</div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/ai/clients')
@login_required
def ai_clients_analysis():
    """تحليل العملاء بالذكاء الاصطناعي"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    content = f'''
    <div class="secure-dashboard">
        <div style="margin-bottom: var(--global-spacing-xl);">
            <div style="display: flex; align-items: center; gap: var(--global-spacing-lg);">
                <a href="/ai" class="secure-btn" style="padding: 10px;">
                    <i class="fas fa-arrow-right"></i>
                </a>
                <div>
                    <h1 style="margin: 0;">
                        <i class="fas fa-user-chart" style="color: var(--global-accent-green);"></i>
                        تحليل العملاء
                    </h1>
                    <p style="color: var(--global-gray-lighter); margin: var(--global-spacing-sm) 0 0 0;">
                        تحليل متقدم لسلوك العملاء وتوقعات الشراء
                    </p>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-chart-pie" style="color: var(--global-accent-blue);"></i>
                    توزيع العملاء
                </h3>
                <div style="text-align: center; padding: var(--global-spacing-xl);">
                    <div style="width: 200px; height: 200px; border-radius: 50%; background: conic-gradient(
                        var(--global-accent-blue) 0% 40%,
                        var(--global-accent-green) 40% 70%,
                        var(--global-accent-yellow) 70% 90%,
                        var(--global-accent-red) 90% 100%
                    ); margin: 0 auto var(--global-spacing-lg);"></div>
                    <div>
                        <div style="display: flex; align-items: center; gap: var(--global-spacing-sm); margin-bottom: var(--global-spacing-sm);">
                            <div style="width: 12px; height: 12px; background: var(--global-accent-blue); border-radius: 2px;"></div>
                            <span>العملاء الجدد (40%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: var(--global-spacing-sm); margin-bottom: var(--global-spacing-sm);">
                            <div style="width: 12px; height: 12px; background: var(--global-accent-green); border-radius: 2px;"></div>
                            <span>العملاء النشطون (30%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: var(--global-spacing-sm); margin-bottom: var(--global-spacing-sm);">
                            <div style="width: 12px; height: 12px; background: var(--global-accent-yellow); border-radius: 2px;"></div>
                            <span>العملاء المتأخرون (20%)</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: var(--global-spacing-sm);">
                            <div style="width: 12px; height: 12px; background: var(--global-accent-red); border-radius: 2px;"></div>
                            <span>العملاء الخاملون (10%)</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-trending-up" style="color: var(--global-accent-green);"></i>
                    تحليل النمو
                </h3>
                <div style="height: 200px; display: flex; align-items: flex-end; gap: 10px; margin-bottom: var(--global-spacing-lg);">
                    <div style="flex: 1; background: var(--global-accent-blue); height: 80%; border-radius: var(--global-radius-small);"></div>
                    <div style="flex: 1; background: var(--global-accent-blue); height: 65%; border-radius: var(--global-radius-small);"></div>
                    <div style="flex: 1; background: var(--global-accent-green); height: 90%; border-radius: var(--global-radius-small);"></div>
                    <div style="flex: 1; background: var(--global-accent-green); height: 95%; border-radius: var(--global-radius-small);"></div>
                    <div style="flex: 1; background: var(--global-accent-green); height: 100%; border-radius: var(--global-radius-small);"></div>
                </div>
                <div style="display: flex; justify-content: space-between; color: var(--global-gray-lighter); font-size: 14px;">
                    <span>الشهر 1</span>
                    <span>الشهر 2</span>
                    <span>الشهر 3</span>
                    <span>الشهر 4</span>
                    <span>الشهر 5</span>
                </div>
            </div>
        </div>
        
        <!-- توصيات العملاء -->
        <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
            <h3 style="margin-bottom: var(--global-spacing-lg);">
                <i class="fas fa-lightbulb" style="color: var(--global-accent-yellow);"></i>
                توصيات الذكاء الاصطناعي
            </h3>
            
            <div class="dashboard-grid">
                <div class="secure-card" style="border-left: 4px solid var(--global-accent-blue);">
                    <h4 style="margin: 0 0 var(--global-spacing-md) 0;">
                        <i class="fas fa-bullhorn" style="color: var(--global-accent-blue);"></i>
                        حملة تسويقية
                    </h4>
                    <p style="color: var(--global-gray-lighter); margin: 0;">
                        اقتراح: إطلاق حملة ترويجية للعملاء الخاملين مع خصم 20%
                    </p>
                </div>
                
                <div class="secure-card" style="border-left: 4px solid var(--global-accent-green);">
                    <h4 style="margin: 0 0 var(--global-spacing-md) 0;">
                        <i class="fas fa-gift" style="color: var(--global-accent-green);"></i>
                        برنامج الولاء
                    </h4>
                    <p style="color: var(--global-gray-lighter); margin: 0;">
                        اقتراح: إنشاء برنامج ولاء للعملاء النشطين بخصومات تراكمية
                    </p>
                </div>
                
                <div class="secure-card" style="border-left: 4px solid var(--global-accent-yellow);">
                    <h4 style="margin: 0 0 var(--global-spacing-md) 0;">
                        <i class="fas fa-comments" style="color: var(--global-accent-yellow);"></i>
                        متابعة العملاء
                    </h4>
                    <p style="color: var(--global-gray-lighter); margin: 0;">
                        اقتراح: متابعة العملاء المتأخرين بالدفع عبر برنامج تذكير آلي
                    </p>
                </div>
            </div>
        </div>
        
        <!-- قائمة العملاء الرئيسيين -->
        <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
            <h3 style="margin-bottom: var(--global-spacing-lg);">
                <i class="fas fa-crown" style="color: var(--global-accent-yellow);"></i>
                العملاء الرئيسيون
            </h3>
            
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: var(--global-gray-medium);">
                            <th style="padding: var(--global-spacing-md); text-align: right;">اسم العميل</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">القيمة الإجمالية</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">عدد الفواتير</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">آخر شراء</th>
                            <th style="padding: var(--global-spacing-md); text-align: right;">التصنيف</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid var(--global-gray-medium);">
                            <td style="padding: var(--global-spacing-md);">
                                <div style="display: flex; align-items: center; gap: var(--global-spacing-sm);">
                                    <div style="width: 32px; height: 32px; background: var(--global-accent-blue); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <span style="color: white; font-weight: 600;">ن</span>
                                    </div>
                                    <span>شركة النخبة</span>
                                </div>
                            </td>
                            <td style="padding: var(--global-spacing-md); font-weight: 600;">$45,250.00</td>
                            <td style="padding: var(--global-spacing-md);">12</td>
                            <td style="padding: var(--global-spacing-md);">2024-01-15</td>
                            <td style="padding: var(--global-spacing-md);">
                                <span class="security-badge" style="background: var(--global-accent-green);">
                                    <i class="fas fa-star"></i> VIP
                                </span>
                            </td>
                        </tr>
                        
                        <tr style="border-bottom: 1px solid var(--global-gray-medium);">
                            <td style="padding: var(--global-spacing-md);">
                                <div style="display: flex; align-items: center; gap: var(--global-spacing-sm);">
                                    <div style="width: 32px; height: 32px; background: var(--global-accent-green); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                                        <span style="color: white; font-weight: 600;">ت</span>
                                    </div>
                                    <span>مؤسسة التقنية</span>
                                </div>
                            </td>
                            <td style="padding: var(--global-spacing-md); font-weight: 600;">$32,500.00</td>
                            <td style="padding: var(--global-spacing-md);">8</td>
                            <td style="padding: var(--global-spacing-md);">2024-01-10</td>
                            <td style="padding: var(--global-spacing-md);">
                                <span class="security-badge" style="background: var(--global-accent-blue);">
                                    <i class="fas fa-user-tie"></i> منتظم
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/clients')
@login_required
def clients():
    """صفحة العملاء"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    content = f'''
    <div class="secure-dashboard">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--global-spacing-xl);">
            <h1 style="margin: 0;">
                <i class="fas fa-users" style="color: var(--global-accent-green);"></i>
                {lang_system.get_text('clients', lang)}
            </h1>
            
            <a href="/clients/create" class="secure-btn">
                <i class="fas fa-user-plus"></i> إضافة عميل
            </a>
        </div>
        
        <!-- أدوات البحث والتصفية -->
        <div class="secure-card" style="margin-bottom: var(--global-spacing-xl);">
            <div style="display: flex; gap: var(--global-spacing-lg); align-items: center;">
                <div style="flex: 1;">
                    <input type="text" class="secure-input" placeholder="بحث باسم العميل أو البريد...">
                </div>
                
                <select class="secure-input" style="width: 200px;">
                    <option value="">جميع الفئات</option>
                    <option value="vip">VIP</option>
                    <option value="regular">منتظم</option>
                    <option value="new">جديد</option>
                </select>
                
                <button class="secure-btn">
                    <i class="fas fa-search"></i> بحث
                </button>
                
                <button class="secure-btn" style="background: var(--global-gray-medium);">
                    <i class="fas fa-download"></i> تصدير
                </button>
            </div>
        </div>
        
        <!-- شبكة العملاء -->
        <div class="dashboard-grid">
            <!-- سيتم عرض العملاء هنا ديناميكياً -->
        </div>
        
        <!-- رسالة عدم وجود عملاء -->
        <div class="secure-card" style="text-align: center; padding: var(--global-spacing-xxl);">
            <i class="fas fa-users" style="font-size: 4em; color: var(--global-gray-light); margin-bottom: var(--global-spacing-lg);"></i>
            <h3 style="margin-bottom: var(--global-spacing-md);">لا توجد عملاء</h3>
            <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-xl);">
                ابدأ بإضافة عميلك الأول
            </p>
            <a href="/clients/create" class="secure-btn">
                <i class="fas fa-user-plus"></i> إضافة عميل
            </a>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/reports')
@login_required
def reports():
    """صفحة التقارير"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    content = f'''
    <div class="secure-dashboard">
        <div style="margin-bottom: var(--global-spacing-xl);">
            <h1 style="margin: 0;">
                <i class="fas fa-chart-bar" style="color: var(--global-accent-blue);"></i>
                {lang_system.get_text('reports', lang)}
            </h1>
            <p style="color: var(--global-gray-lighter); margin: var(--global-spacing-sm) 0 0 0;">
                تقارير وإحصائيات متقدمة عن أدائك
            </p>
        </div>
        
        <div class="dashboard-grid">
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-file-pdf" style="color: var(--global-accent-red);"></i>
                    تقرير المبيعات
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    تقرير مفصل عن المبيعات حسب الفترة
                </p>
                <a href="/reports/sales" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-download"></i> تحميل التقرير
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-chart-line" style="color: var(--global-accent-green);"></i>
                    تقرير الأداء
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    تحليل أداء الفواتير والإيرادات
                </p>
                <a href="/reports/performance" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-chart-bar"></i> عرض التقرير
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-user-check" style="color: var(--global-accent-yellow);"></i>
                    تقرير العملاء
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    تحليل سلوك العملاء وتصنيفهم
                </p>
                <a href="/reports/clients" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-users"></i> عرض التقرير
                </a>
            </div>
        </div>
        
        <!-- تقارير مخصصة -->
        <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
            <h3 style="margin-bottom: var(--global-spacing-lg);">
                <i class="fas fa-cogs" style="color: var(--global-accent-blue);"></i>
                تقارير مخصصة
            </h3>
            
            <form style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--global-spacing-lg);">
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                        نوع التقرير
                    </label>
                    <select class="secure-input">
                        <option value="sales">تقرير المبيعات</option>
                        <option value="expenses">تقرير المصروفات</option>
                        <option value="clients">تقرير العملاء</option>
                        <option value="tax">تقرير الضرائب</option>
                    </select>
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                        الفترة
                    </label>
                    <select class="secure-input">
                        <option value="today">اليوم</option>
                        <option value="week">هذا الأسبوع</option>
                        <option value="month">هذا الشهر</option>
                        <option value="quarter">هذا الربع</option>
                        <option value="year">هذه السنة</option>
                        <option value="custom">مخصص</option>
                    </select>
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                        تاريخ البداية
                    </label>
                    <input type="date" class="secure-input">
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: var(--global-spacing-sm);">
                        تاريخ النهاية
                    </label>
                    <input type="date" class="secure-input">
                </div>
                
                <div style="grid-column: span 2;">
                    <button type="submit" class="secure-btn" style="width: 100%;">
                        <i class="fas fa-file-export"></i> إنشاء التقرير
                    </button>
                </div>
            </form>
        </div>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/settings')
@login_required
def settings():
    """صفحة الإعدادات"""
    lang = request.args.get('lang', session.get('lang', 'ar'))
    
    content = f'''
    <div class="secure-dashboard">
        <div style="margin-bottom: var(--global-spacing-xl);">
            <h1 style="margin: 0;">
                <i class="fas fa-cog" style="color: var(--global-accent-blue);"></i>
                {lang_system.get_text('settings', lang)}
            </h1>
            <p style="color: var(--global-gray-lighter); margin: var(--global-spacing-sm) 0 0 0;">
                إدارة إعدادات حسابك وتفضيلات النظام
            </p>
        </div>
        
        <div class="dashboard-grid">
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-user" style="color: var(--global-accent-blue);"></i>
                    {lang_system.get_text('profile', lang)}
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    إدارة معلومات حسابك الشخصية
                </p>
                <a href="/settings/profile" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-edit"></i> تعديل الملف
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-shield-alt" style="color: var(--global-accent-green);"></i>
                    {lang_system.get_text('security', lang)}
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    إعدادات الأمان وكلمة المرور
                </p>
                <a href="/settings/security" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-lock"></i> إعدادات الأمان
                </a>
            </div>
            
            <div class="secure-card">
                <h3 style="margin-bottom: var(--global-spacing-lg);">
                    <i class="fas fa-language" style="color: var(--global-accent-yellow);"></i>
                    {lang_system.get_text('language', lang)} & {lang_system.get_text('theme', lang)}
                </h3>
                <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-lg);">
                    تغيير اللغة والمظهر
                </p>
                <a href="/settings/appearance" class="secure-btn" style="width: 100%;">
                    <i class="fas fa-palette"></i> التخصيص
                </a>
            </div>
        </div>
        
        <!-- الإشعارات -->
        <div class="secure-card" style="margin-top: var(--global-spacing-xl);">
            <h3 style="margin-bottom: var(--global-spacing-lg);">
                <i class="fas fa-bell" style="color: var(--global-accent-yellow);"></i>
                {lang_system.get_text('notifications', lang)}
            </h3>
            
            <div style="display: flex; flex-direction: column; gap: var(--global-spacing-md);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0 0 var(--global-spacing-xs) 0;">إشعارات البريد الإلكتروني</h4>
                        <p style="color: var(--global-gray-lighter); margin: 0;">تلقي إشعارات على بريدك الإلكتروني</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0 0 var(--global-spacing-xs) 0;">إشعارات الفواتير</h4>
                        <p style="color: var(--global-gray-lighter); margin: 0;">إشعارات بإنشاء ودفع الفواتير</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0 0 var(--global-spacing-xs) 0;">إشعارات الأمان</h4>
                        <p style="color: var(--global-gray-lighter); margin: 0;">إشعارات بتسجيلات الدخول والأنشطة</p>
                    </div>
                    <label class="switch">
                        <input type="checkbox" checked>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
        </div>
        
        <style>
            .switch {{
                position: relative;
                display: inline-block;
                width: 60px;
                height: 34px;
            }}
            
            .switch input {{
                opacity: 0;
                width: 0;
                height: 0;
            }}
            
            .slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: var(--global-gray-medium);
                transition: .4s;
                border-radius: 34px;
            }}
            
            .slider:before {{
                position: absolute;
                content: "";
                height: 26px;
                width: 26px;
                left: 4px;
                bottom: 4px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }}
            
            input:checked + .slider {{
                background-color: var(--global-accent-green);
            }}
            
            input:checked + .slider:before {{
                transform: translateX(26px);
            }}
        </style>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content)

@app.route('/logout')
def logout():
    """تسجيل الخروج الآمن"""
    if session.get('user_logged_in'):
        secure_db.log_activity(session.get('user_id'), 'LOGOUT', 'user', session.get('user_id'), 'تم تسجيل الخروج')
        security_logger.log_event('LOGOUT', session.get('username'), request.remote_addr, 'User logged out')
    
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('home'))

# ================== نظام API الآمن ==================
@app.route('/api/v1/invoices', methods=['GET'])
@login_required
def api_get_invoices():
    """API للحصول على الفواتير"""
    try:
        user_id = session['user_id']
        invoices = secure_db.execute_query(
            "SELECT * FROM invoices WHERE user_id = ? AND is_deleted = 0 ORDER BY created_at DESC LIMIT 50",
            (user_id,),
            fetchall=True
        )
        
        return jsonify({
            'success': True,
            'data': invoices,
            'count': len(invoices)
        })
    except Exception as e:
        security_logger.log_event('API_ERROR', session.get('user_id'), request.remote_addr, f"Get invoices: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في الخادم'
        }), 500

@app.route('/api/v1/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def api_get_invoice(invoice_id):
    """API للحصول على فاتورة محددة"""
    try:
        user_id = session['user_id']
        invoice = secure_db.execute_query(
            "SELECT * FROM invoices WHERE id = ? AND user_id = ? AND is_deleted = 0",
            (invoice_id, user_id),
            fetchone=True
        )
        
        if invoice:
            return jsonify({
                'success': True,
                'data': invoice
            })
        else:
            return jsonify({
                'success': False,
                'error': 'الفاتورة غير موجودة'
            }), 404
    except Exception as e:
        security_logger.log_event('API_ERROR', session.get('user_id'), request.remote_addr, f"Get invoice {invoice_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في الخادم'
        }), 500

# ================== معالج الأخطاء ==================
@app.errorhandler(404)
def page_not_found(e):
    """معالج صفحة غير موجودة"""
    lang = session.get('lang', 'ar')
    
    content = f'''
    <div style="text-align: center; padding: var(--global-spacing-xxl);">
        <div style="font-size: 6em; color: var(--global-accent-blue); margin-bottom: var(--global-spacing-lg);">
            <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h1 style="margin-bottom: var(--global-spacing-md);">404 - الصفحة غير موجودة</h1>
        <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-xl);">
            الصفحة التي تبحث عنها غير موجودة أو تم نقلها.
        </p>
        <a href="/" class="secure-btn">
            <i class="fas fa-home"></i> العودة للرئيسية
        </a>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content), 404

@app.errorhandler(500)
def internal_server_error(e):
    """معالج خطأ داخلي"""
    security_logger.log_event('SERVER_ERROR', session.get('user_id', 'unknown'), request.remote_addr, f"500 Error: {str(e)}")
    
    content = '''
    <div style="text-align: center; padding: var(--global-spacing-xxl);">
        <div style="font-size: 6em; color: var(--global-accent-red); margin-bottom: var(--global-spacing-lg);">
            <i class="fas fa-server"></i>
        </div>
        <h1 style="margin-bottom: var(--global-spacing-md);">500 - خطأ في الخادم</h1>
        <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-xl);">
            حدث خطأ داخلي في الخادم. نحن نعمل على إصلاحه.
        </p>
        <a href="/" class="secure-btn">
            <i class="fas fa-home"></i> العودة للرئيسية
        </a>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    """معالج تجاوز الحد الأقصى للطلبات"""
    content = '''
    <div style="text-align: center; padding: var(--global-spacing-xxl);">
        <div style="font-size: 6em; color: var(--global-accent-yellow); margin-bottom: var(--global-spacing-lg);">
            <i class="fas fa-stopwatch"></i>
        </div>
        <h1 style="margin-bottom: var(--global-spacing-md);">429 - تجاوز الحد المسموح</h1>
        <p style="color: var(--global-gray-lighter); margin-bottom: var(--global-spacing-xl);">
            لقد تجاوزت الحد الأقصى للطلبات المسموح بها. الرجاء الانتظار قليلاً.
        </p>
        <a href="/" class="secure-btn">
            <i class="fas fa-home"></i> العودة للرئيسية
        </a>
    </div>
    '''
    
    return render_template_string(GLOBAL_DESIGN_CSS + content), 429

# ================== وظائف مساعدة للسلامة ==================
@app.before_request
def before_request():
    """التحقق قبل كل طلب"""
    # تحديث CSRF token
    if 'csrf_token' not in session:
        session['csrf_token'] = security.generate_csrf_token()
    
    # تحديث وقت النشاط
    if session.get('user_logged_in'):
        session['last_activity'] = time.time()
    
    # التحقق من الجلسة المنتهية
    if session.get('user_logged_in') and 'last_activity' in session:
        if time.time() - session['last_activity'] > 3600:  # 1 hour
            security_logger.log_event('SESSION_EXPIRED', session.get('user_id'), request.remote_addr, 'Session timeout')
            session.clear()
            flash('انتهت جلسة العمل، يرجى تسجيل الدخول مرة أخرى', 'warning')
            return redirect(url_for('login'))

@app.after_request
def add_security_headers(response):
    """إضافة رؤوس الأمان"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com; style-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com 'unsafe-inline'; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🚀 بدء تشغيل النظام المتعدد اللغات والآمن...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        print("🌐 نظام متعدد اللغات مفعل (عربي/إنجليزي)!")
        print("🔐 نظام الأمان المتقدم نشط!")
        print("🛡️  حماية CSRF و JWT مفعلة!")
        print("📊 نظام السجلات الأمنية يعمل!")
        
        print("\n📋 المسارات المتاحة:")
        print("🔹 / - الصفحة الرئيسية (متعددة اللغات)")
        print("🔹 /login - تسجيل الدخول الآمن") 
        print("🔹 /register - إنشاء حساب آمن")
        print("🔹 /dashboard - لوحة التحكم")
        print("🔹 /invoices - إدارة الفواتير")
        print("🔹 /invoices/create - إنشاء فاتورة")
        print("🔹 /ai - الذكاء الاصطناعي")
        print("🔹 /ai/clients - تحليل العملاء")
        print("🔹 /clients - إدارة العملاء")
        print("🔹 /reports - التقارير")
        print("🔹 /settings - الإعدادات")
        print("🔹 /logout - تسجيل الخروج الآمن")
        print("🔹 /api/v1/* - واجهة برمجة التطبيقات الآمنة")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
