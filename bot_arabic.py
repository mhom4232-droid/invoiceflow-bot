import os
import sqlite3
import json
import time
import hashlib
import secrets
import re
import io
import base64
import random
import uuid
from datetime import datetime, timedelta
from threading import Thread
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from PIL import Image as PILImage

# ================== تهيئة التطبيق ==================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_secure_pro_2024_v1')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['DATABASE_PATH'] = 'database/invoiceflow.db'

# إعدادات الأمان
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# إنشاء المجلدات
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('static/invoices', exist_ok=True)
os.makedirs('static/qrcodes', exist_ok=True)
os.makedirs('static/logos', exist_ok=True)

port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🚀 InvoiceFlow Pro - النظام الاحترافي المتكامل")
print("🎨 تصميم أسود/أبيض عالمي • نظام فواتير متكامل • ذكاء اصطناعي احترافي")
print("👑 فريق العمل المحترف - النسخة النهائية الكاملة")
print("=" * 80)

# ================== نظام قاعدة البيانات ==================
class DatabaseSystem:
    def __init__(self):
        self.db_path = app.config['DATABASE_PATH']
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                company_name TEXT DEFAULT 'شركتي',
                phone TEXT,
                address TEXT,
                logo TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # جدول العملاء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                company TEXT,
                tax_number TEXT,
                category TEXT DEFAULT 'عام',
                total_purchases REAL DEFAULT 0,
                last_purchase DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول الفواتير
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                client_id INTEGER,
                client_name TEXT NOT NULL,
                client_email TEXT,
                client_phone TEXT,
                client_address TEXT,
                issue_date DATE NOT NULL,
                due_date DATE NOT NULL,
                items TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax_rate REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_method TEXT DEFAULT 'نقدي',
                notes TEXT,
                pdf_path TEXT,
                qr_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # جدول المنتجات/الخدمات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                unit TEXT DEFAULT 'قطعة',
                tax_rate REAL DEFAULT 0,
                category TEXT DEFAULT 'عام',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # إضافة مستخدم افتراضي إذا لم يكن موجود
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            default_hash = generate_password_hash("admin123")
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, company_name, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@invoiceflow.com', default_hash, 'مدير النظام', 'InvoiceFlow Pro', 'admin'))
        
        conn.commit()
        conn.close()
        print("✅ قاعدة البيانات جاهزة!")
    
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=(), fetchone=False, fetchall=False):
        """تنفيذ استعلام"""
        conn = self.get_connection()
        cursor = conn.cursor()
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
        
        conn.commit()
        conn.close()
        return result

db = DatabaseSystem()

# ================== نظام المصادقة ==================
def login_required(f):
    """مصادقة تسجيل الدخول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """مصادقة المدير"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('يرجى تسجيل الدخول', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ================== نظام التصميم ==================
BASE_CSS = """
/* ================== إعدادات التصميم الأساسية ================== */
:root {
    /* الألوان الأساسية - أسود/أبيض */
    --primary-black: #000000;
    --primary-white: #FFFFFF;
    --dark-gray: #1A1A1A;
    --medium-gray: #2D2D2D;
    --light-gray: #3D3D3D;
    --lighter-gray: #4D4D4D;
    --border-gray: #555555;
    --text-primary: #FFFFFF;
    --text-secondary: #CCCCCC;
    --text-muted: #999999;
    
    /* ألوان التنبيه */
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --error-color: #EF4444;
    --info-color: #3B82F6;
    
    /* ظلال */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
    --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);
    
    /* زوايا */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --radius-full: 9999px;
    
    /* التباعد */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;
    --space-3xl: 64px;
    
    /* الأنيميشن */
    --transition-fast: 150ms ease;
    --transition-normal: 250ms ease;
    --transition-slow: 350ms ease;
}

/* ================== إعدادات الأساس ================== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', 'Tajawal', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--primary-black);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    direction: rtl;
    text-align: right;
}

/* ================== التمرير المخصص ================== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--dark-gray);
}

::-webkit-scrollbar-thumb {
    background: var(--medium-gray);
    border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--light-gray);
}

/* ================== الأنيميشن ================== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ================== الطباعة ================== */
@media print {
    .no-print {
        display: none !important;
    }
    
    body {
        background: white !important;
        color: black !important;
    }
}

/* ================== التجاوب ================== */
@media (max-width: 768px) {
    :root {
        --space-lg: 16px;
        --space-xl: 24px;
        --space-2xl: 32px;
    }
    
    .container {
        padding-left: var(--space-md);
        padding-right: var(--space-md);
    }
}

/* ================== تنسيق النصوص العربية ================== */
.arabic-text {
    font-family: 'Tajawal', 'Segoe UI', sans-serif;
    line-height: 1.8;
}

/* ================== فئات المساعدة ================== */
.fade-in {
    animation: fadeIn var(--transition-normal);
}

.slide-in {
    animation: slideIn var(--transition-normal);
}

.pulse {
    animation: pulse 2s infinite;
}

.hidden {
    display: none !important;
}

.text-center {
    text-align: center !important;
}

.text-right {
    text-align: right !important;
}

.text-left {
    text-align: left !important;
}

.flex {
    display: flex !important;
}

.flex-col {
    flex-direction: column !important;
}

.items-center {
    align-items: center !important;
}

.justify-center {
    justify-content: center !important;
}

.justify-between {
    justify-content: space-between !important;
}

.gap-sm {
    gap: var(--space-sm) !important;
}

.gap-md {
    gap: var(--space-md) !important;
}

.gap-lg {
    gap: var(--space-lg) !important;
}

.w-full {
    width: 100% !important;
}

.h-full {
    height: 100% !important;
}

.mt-sm { margin-top: var(--space-sm) !important; }
.mt-md { margin-top: var(--space-md) !important; }
.mt-lg { margin-top: var(--space-lg) !important; }
.mt-xl { margin-top: var(--space-xl) !important; }

.mb-sm { margin-bottom: var(--space-sm) !important; }
.mb-md { margin-bottom: var(--space-md) !important; }
.mb-lg { margin-bottom: var(--space-lg) !important; }
.mb-xl { margin-bottom: var(--space-xl) !important; }

.p-sm { padding: var(--space-sm) !important; }
.p-md { padding: var(--space-md) !important; }
.p-lg { padding: var(--space-lg) !important; }
.p-xl { padding: var(--space-xl) !important; }

.rounded-sm { border-radius: var(--radius-sm) !important; }
.rounded-md { border-radius: var(--radius-md) !important; }
.rounded-lg { border-radius: var(--radius-lg) !important; }
.rounded-xl { border-radius: var(--radius-xl) !important; }
.rounded-full { border-radius: var(--radius-full) !important; }

.shadow-sm { box-shadow: var(--shadow-sm) !important; }
.shadow-md { box-shadow: var(--shadow-md) !important; }
.shadow-lg { box-shadow: var(--shadow-lg) !important; }

.bg-dark { background-color: var(--dark-gray) !important; }
.bg-medium { background-color: var(--medium-gray) !important; }
.bg-light { background-color: var(--light-gray) !important; }

.border {
    border: 1px solid var(--border-gray) !important;
}

.text-success { color: var(--success-color) !important; }
.text-warning { color: var(--warning-color) !important; }
.text-error { color: var(--error-color) !important; }
.text-info { color: var(--info-color) !important; }
.text-muted { color: var(--text-muted) !important; }

.text-sm { font-size: 0.875rem !important; }
.text-base { font-size: 1rem !important; }
.text-lg { font-size: 1.125rem !important; }
.text-xl { font-size: 1.25rem !important; }
.text-2xl { font-size: 1.5rem !important; }
.text-3xl { font-size: 1.875rem !important; }
.text-4xl { font-size: 2.25rem !important; }

.font-light { font-weight: 300 !important; }
.font-normal { font-weight: 400 !important; }
.font-medium { font-weight: 500 !important; }
.font-semibold { font-weight: 600 !important; }
.font-bold { font-weight: 700 !important; }
"""

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvoiceFlow Pro - تسجيل الدخول</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>{{ css }}</style>
</head>
<body class="flex items-center justify-center min-h-screen bg-black">
    <div class="container max-w-md mx-auto p-xl">
        <!-- الشعار -->
        <div class="text-center mb-2xl">
            <div class="inline-block p-lg bg-medium rounded-xl mb-lg">
                <i class="fas fa-file-invoice-dollar text-4xl text-info"></i>
            </div>
            <h1 class="text-3xl font-bold mb-sm">InvoiceFlow Pro</h1>
            <p class="text-muted">نظام إدارة الفواتير الاحترافي</p>
        </div>
        
        <!-- رسائل التنبيه -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="mb-lg">
                    {% for category, message in messages %}
                        <div class="p-md rounded-lg mb-sm {% if category == 'error' %}bg-error/20 border border-error/30{% elif category == 'success' %}bg-success/20 border border-success/30{% else %}bg-warning/20 border border-warning/30{% endif %}">
                            <div class="flex items-center gap-md">
                                <i class="fas {% if category == 'error' %}fa-exclamation-circle text-error{% elif category == 'success' %}fa-check-circle text-success{% else %}fa-info-circle text-warning{% endif %}"></i>
                                <span>{{ message }}</span>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        
        <!-- نموذج الدخول -->
        <div class="bg-dark rounded-xl shadow-lg border border-light p-xl fade-in">
            <h2 class="text-xl font-semibold mb-lg text-center">تسجيل الدخول</h2>
            
            <form method="POST" action="{{ url_for('login') }}">
                <input type="hidden" name="next" value="{{ request.args.get('next', '') }}">
                
                <div class="mb-lg">
                    <label class="block text-sm font-medium mb-sm text-secondary">
                        <i class="fas fa-user ml-sm"></i> اسم المستخدم
                    </label>
                    <input type="text" name="username" required 
                           class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent transition"
                           placeholder="أدخل اسم المستخدم">
                </div>
                
                <div class="mb-lg">
                    <label class="block text-sm font-medium mb-sm text-secondary">
                        <i class="fas fa-lock ml-sm"></i> كلمة المرور
                    </label>
                    <input type="password" name="password" required 
                           class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent transition"
                           placeholder="أدخل كلمة المرور">
                </div>
                
                <div class="flex items-center justify-between mb-lg">
                    <label class="flex items-center gap-sm cursor-pointer">
                        <input type="checkbox" name="remember" class="rounded border-light bg-medium">
                        <span class="text-sm text-secondary">تذكرني</span>
                    </label>
                    
                    <a href="#" class="text-sm text-info hover:underline">نسيت كلمة المرور؟</a>
                </div>
                
                <button type="submit" 
                        class="w-full p-md bg-info text-white rounded-lg font-semibold hover:bg-blue-600 transition duration-300 flex items-center justify-center gap-sm">
                    <i class="fas fa-sign-in-alt"></i>
                    دخول إلى النظام
                </button>
            </form>
            
            <!-- معلومات الحساب الافتراضي -->
            <div class="mt-lg p-md bg-medium rounded-lg border border-light">
                <p class="text-sm text-muted mb-sm">
                    <i class="fas fa-info-circle ml-sm"></i> 
                    معلومات الدخول الافتراضية للاختبار:
                </p>
                <div class="text-sm">
                    <div class="flex items-center gap-sm mb-xs">
                        <span class="text-secondary">المستخدم:</span>
                        <code class="bg-black px-sm py-xs rounded">admin</code>
                    </div>
                    <div class="flex items-center gap-sm">
                        <span class="text-secondary">كلمة المرور:</span>
                        <code class="bg-black px-sm py-xs rounded">admin123</code>
                    </div>
                </div>
            </div>
            
            <!-- روابط إضافية -->
            <div class="mt-xl pt-lg border-t border-light">
                <p class="text-center text-secondary">
                    ليس لديك حساب؟ 
                    <a href="{{ url_for('register') }}" class="text-info font-medium hover:underline">
                        إنشاء حساب جديد
                    </a>
                </p>
            </div>
        </div>
        
        <!-- حقوق النشر -->
        <div class="mt-xl text-center">
            <p class="text-sm text-muted">
                <i class="fas fa-copyright ml-sm"></i>
                2024 InvoiceFlow Pro. جميع الحقوق محفوظة.
            </p>
            <p class="text-xs text-muted mt-sm">
                النسخة الاحترافية - فريق العمل المحترف
            </p>
        </div>
    </div>
</body>
</html>
"""

# ================== الصفحات الرئيسية ==================

@app.route('/')
def index():
    """الصفحة الرئيسية - إعادة توجيه للدخول"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if session.get('user_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return redirect(url_for('login'))
        
        # البحث عن المستخدم
        user = db.execute_query(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,),
            fetchone=True
        )
        
        if not user or not check_password_hash(user['password_hash'], password):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return redirect(url_for('login'))
        
        # تحديث وقت الدخول الأخير
        db.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        
        # إنشاء الجلسة
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_role'] = user['role']
        session['company_name'] = user['company_name']
        session['user_logged_in'] = True
        session.permanent = bool(remember)
        
        flash(f'مرحباً بك {user["full_name"] or user["username"]}!', 'success')
        
        next_page = request.form.get('next') or url_for('dashboard')
        return redirect(next_page)
    
    return render_template_string(LOGIN_PAGE_HTML, css=BASE_CSS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if session.get('user_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        company_name = request.form.get('company_name', '').strip()
        
        # التحقق من المدخلات
        errors = []
        
        if not username or len(username) < 3:
            errors.append('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if not email or '@' not in email:
            errors.append('البريد الإلكتروني غير صالح')
        
        if not password or len(password) < 6:
            errors.append('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
        
        if password != confirm_password:
            errors.append('كلمتا المرور غير متطابقتين')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('register'))
        
        # التحقق من عدم وجود المستخدم مسبقاً
        existing_user = db.execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
            fetchone=True
        )
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً', 'error')
            return redirect(url_for('register'))
        
        # إنشاء المستخدم الجديد
        password_hash = generate_password_hash(password)
        db.execute_query('''
            INSERT INTO users (username, email, password_hash, full_name, company_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, company_name))
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('login'))
    
    # صفحة التسجيل
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceFlow Pro - إنشاء حساب</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>{{ css }}</style>
    </head>
    <body class="flex items-center justify-center min-h-screen bg-black">
        <div class="container max-w-md mx-auto p-xl">
            <!-- الشعار -->
            <div class="text-center mb-xl">
                <div class="inline-block p-lg bg-medium rounded-xl mb-lg">
                    <i class="fas fa-user-plus text-4xl text-info"></i>
                </div>
                <h1 class="text-3xl font-bold mb-sm">إنشاء حساب جديد</h1>
                <p class="text-muted">انضم إلى نظام InvoiceFlow Pro</p>
            </div>
            
            <!-- رسائل التنبيه -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="mb-lg">
                        {% for category, message in messages %}
                            <div class="p-md rounded-lg mb-sm {% if category == 'error' %}bg-error/20 border border-error/30{% elif category == 'success' %}bg-success/20 border border-success/30{% else %}bg-warning/20 border border-warning/30{% endif %}">
                                <div class="flex items-center gap-md">
                                    <i class="fas {% if category == 'error' %}fa-exclamation-circle text-error{% elif category == 'success' %}fa-check-circle text-success{% else %}fa-info-circle text-warning{% endif %}"></i>
                                    <span>{{ message }}</span>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}
            
            <!-- نموذج التسجيل -->
            <div class="bg-dark rounded-xl shadow-lg border border-light p-xl fade-in">
                <form method="POST" action="{{ url_for('register') }}">
                    <div class="mb-lg">
                        <label class="block text-sm font-medium mb-sm text-secondary">
                            <i class="fas fa-user ml-sm"></i> اسم المستخدم *
                        </label>
                        <input type="text" name="username" required 
                               class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent"
                               placeholder="اختر اسم مستخدم فريد">
                    </div>
                    
                    <div class="mb-lg">
                        <label class="block text-sm font-medium mb-sm text-secondary">
                            <i class="fas fa-envelope ml-sm"></i> البريد الإلكتروني *
                        </label>
                        <input type="email" name="email" required 
                               class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent"
                               placeholder="example@email.com">
                    </div>
                    
                    <div class="mb-lg">
                        <label class="block text-sm font-medium mb-sm text-secondary">
                            <i class="fas fa-id-card ml-sm"></i> الاسم الكامل
                        </label>
                        <input type="text" name="full_name" 
                               class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent"
                               placeholder="الاسم الثلاثي">
                    </div>
                    
                    <div class="mb-lg">
                        <label class="block text-sm font-medium mb-sm text-secondary">
                            <i class="fas fa-building ml-sm"></i> اسم الشركة
                        </label>
                        <input type="text" name="company_name" 
                               class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent"
                               placeholder="اسم شركتك">
                    </div>
                    
                    <div class="mb-lg">
                        <label class="block text-sm font-medium mb-sm text-secondary">
                            <i class="fas fa-lock ml-sm"></i> كلمة المرور *
                        </label>
                        <input type="password" name="password" required 
                               class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent"
                               placeholder="6 أحرف على الأقل">
                    </div>
                    
                    <div class="mb-lg">
                        <label class="block text-sm font-medium mb-sm text-secondary">
                            <i class="fas fa-lock ml-sm"></i> تأكيد كلمة المرور *
                        </label>
                        <input type="password" name="confirm_password" required 
                               class="w-full p-md bg-medium border border-light rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-info focus:border-transparent"
                               placeholder="أعد إدخال كلمة المرور">
                    </div>
                    
                    <button type="submit" 
                            class="w-full p-md bg-success text-white rounded-lg font-semibold hover:bg-green-600 transition duration-300 flex items-center justify-center gap-sm">
                        <i class="fas fa-user-plus"></i>
                        إنشاء الحساب
                    </button>
                </form>
                
                <!-- روابط إضافية -->
                <div class="mt-xl pt-lg border-t border-light">
                    <p class="text-center text-secondary">
                        لديك حساب بالفعل؟ 
                        <a href="{{ url_for('login') }}" class="text-info font-medium hover:underline">
                            سجل الدخول
                        </a>
                    </p>
                </div>
            </div>
            
            <!-- حقوق النشر -->
            <div class="mt-xl text-center">
                <p class="text-sm text-muted">
                    <i class="fas fa-copyright ml-sm"></i>
                    2024 InvoiceFlow Pro. جميع الحقوق محفوظة.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, css=BASE_CSS)

# ================== قالب لوحة التحكم ==================
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - InvoiceFlow Pro</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        {{ css }}
        
        /* ================== تصميم لوحة التحكم ================== */
        .dashboard-layout {
            display: grid;
            grid-template-columns: 280px 1fr;
            min-height: 100vh;
        }
        
        /* الشريط الجانبي */
        .sidebar {
            background: linear-gradient(180deg, var(--primary-black) 0%, var(--dark-gray) 100%);
            border-left: 1px solid var(--border-gray);
            padding: var(--space-xl) 0;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }
        
        .sidebar-header {
            padding: 0 var(--space-xl) var(--space-xl);
            border-bottom: 1px solid var(--border-gray);
            margin-bottom: var(--space-xl);
        }
        
        .sidebar-nav {
            padding: 0 var(--space-xl);
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: var(--space-md);
            padding: var(--space-md) var(--space-lg);
            margin-bottom: var(--space-sm);
            border-radius: var(--radius-lg);
            color: var(--text-secondary);
            text-decoration: none;
            transition: all var(--transition-fast);
        }
        
        .nav-item:hover {
            background: var(--medium-gray);
            color: var(--text-primary);
            transform: translateX(-5px);
        }
        
        .nav-item.active {
            background: var(--info-color);
            color: white;
            font-weight: 500;
        }
        
        /* المحتوى الرئيسي */
        .main-content {
            background: var(--dark-gray);
            overflow-y: auto;
            max-height: 100vh;
        }
        
        .navbar {
            background: var(--primary-black);
            border-bottom: 1px solid var(--border-gray);
            padding: var(--space-lg) var(--space-xl);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .content-container {
            padding: var(--space-xl);
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* الكروت */
        .card {
            background: var(--medium-gray);
            border: 1px solid var(--border-gray);
            border-radius: var(--radius-xl);
            padding: var(--space-xl);
            transition: all var(--transition-normal);
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--info-color);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--space-lg);
        }
        
        /* الشبكات */
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: var(--space-lg);
        }
        
        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--space-lg);
        }
        
        .grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--space-lg);
        }
        
        /* الأزرار */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: var(--space-sm);
            padding: var(--space-md) var(--space-lg);
            border-radius: var(--radius-lg);
            font-weight: 500;
            text-decoration: none;
            transition: all var(--transition-fast);
            border: none;
            cursor: pointer;
        }
        
        .btn-primary {
            background: var(--info-color);
            color: white;
        }
        
        .btn-primary:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        
        .btn-success {
            background: var(--success-color);
            color: white;
        }
        
        .btn-danger {
            background: var(--error-color);
            color: white;
        }
        
        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-gray);
            color: var(--text-secondary);
        }
        
        .btn-outline:hover {
            border-color: var(--info-color);
            color: var(--info-color);
        }
        
        /* الجداول */
        .table-container {
            overflow-x: auto;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-gray);
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .table th {
            background: var(--light-gray);
            padding: var(--space-lg);
            text-align: right;
            font-weight: 600;
            border-bottom: 1px solid var(--border-gray);
        }
        
        .table td {
            padding: var(--space-md) var(--space-lg);
            border-bottom: 1px solid var(--border-gray);
        }
        
        .table tr:hover {
            background: var(--medium-gray);
        }
        
        /* البطاقات الإحصائية */
        .stat-card {
            text-align: center;
            padding: var(--space-xl);
        }
        
        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: var(--radius-full);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto var(--space-lg);
            font-size: 1.5rem;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: var(--space-sm);
        }
        
        /* الأشكال الهندسية */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: var(--space-xs);
            padding: var(--space-xs) var(--space-md);
            border-radius: var(--radius-full);
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .badge-success {
            background: var(--success-color)/20;
            color: var(--success-color);
        }
        
        .badge-warning {
            background: var(--warning-color)/20;
            color: var(--warning-color);
        }
        
        .badge-error {
            background: var(--error-color)/20;
            color: var(--error-color);
        }
        
        .badge-info {
            background: var(--info-color)/20;
            color: var(--info-color);
        }
        
        /* النماذج */
        .form-group {
            margin-bottom: var(--space-lg);
        }
        
        .form-label {
            display: block;
            margin-bottom: var(--space-sm);
            font-weight: 500;
            color: var(--text-secondary);
        }
        
        .form-control {
            width: 100%;
            padding: var(--space-md);
            background: var(--light-gray);
            border: 1px solid var(--border-gray);
            border-radius: var(--radius-lg);
            color: var(--text-primary);
            font-size: 1rem;
            transition: all var(--transition-fast);
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--info-color);
            box-shadow: 0 0 0 3px var(--info-color)/20;
        }
        
        /* التجاوب */
        @media (max-width: 1024px) {
            .dashboard-layout {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                display: none;
            }
            
            .grid-3, .grid-4 {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 {
                grid-template-columns: 1fr;
            }
            
            .content-container {
                padding: var(--space-md);
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-layout">
        <!-- الشريط الجانبي -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="flex items-center gap-md mb-lg">
                    <div class="p-md bg-info rounded-lg">
                        <i class="fas fa-file-invoice-dollar text-white text-xl"></i>
                    </div>
                    <div>
                        <h2 class="font-bold text-lg">InvoiceFlow Pro</h2>
                        <p class="text-sm text-muted">النظام الاحترافي</p>
                    </div>
                </div>
                
                <div class="p-md bg-medium rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="w-10 h-10 bg-info rounded-full flex items-center justify-center">
                            <span class="font-bold text-white">{{ session.username[0].upper() }}</span>
                        </div>
                        <div>
                            <p class="font-medium">{{ session.username }}</p>
                            <p class="text-xs text-muted">{{ session.company_name }}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <nav class="sidebar-nav">
                <a href="{{ url_for('dashboard') }}" class="nav-item {% if request.endpoint == 'dashboard' %}active{% endif %}">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>لوحة التحكم</span>
                </a>
                
                <a href="{{ url_for('invoices') }}" class="nav-item {% if request.endpoint == 'invoices' %}active{% endif %}">
                    <i class="fas fa-file-invoice-dollar"></i>
                    <span>الفواتير</span>
                </a>
                
                <a href="{{ url_for('create_invoice') }}" class="nav-item {% if request.endpoint == 'create_invoice' %}active{% endif %}">
                    <i class="fas fa-plus-circle"></i>
                    <span>إنشاء فاتورة</span>
                </a>
                
                <a href="{{ url_for('clients') }}" class="nav-item {% if request.endpoint == 'clients' %}active{% endif %}">
                    <i class="fas fa-users"></i>
                    <span>العملاء</span>
                </a>
                
                <a href="{{ url_for('products') }}" class="nav-item {% if request.endpoint == 'products' %}active{% endif %}">
                    <i class="fas fa-box"></i>
                    <span>المنتجات</span>
                </a>
                
                <a href="{{ url_for('reports') }}" class="nav-item {% if request.endpoint == 'reports' %}active{% endif %}">
                    <i class="fas fa-chart-bar"></i>
                    <span>التقارير</span>
                </a>
                
                <a href="{{ url_for('ai_insights') }}" class="nav-item {% if request.endpoint == 'ai_insights' %}active{% endif %}">
                    <i class="fas fa-robot"></i>
                    <span>الذكاء الاصطناعي</span>
                </a>
                
                <div class="my-xl border-t border-light"></div>
                
                <a href="{{ url_for('profile') }}" class="nav-item {% if request.endpoint == 'profile' %}active{% endif %}">
                    <i class="fas fa-user-cog"></i>
                    <span>الملف الشخصي</span>
                </a>
                
                <a href="{{ url_for('settings') }}" class="nav-item {% if request.endpoint == 'settings' %}active{% endif %}">
                    <i class="fas fa-cog"></i>
                    <span>الإعدادات</span>
                </a>
                
                <a href="{{ url_for('logout') }}" class="nav-item">
                    <i class="fas fa-sign-out-alt"></i>
                    <span>تسجيل الخروج</span>
                </a>
            </nav>
            
            <div class="px-xl mt-auto pt-xl border-t border-light">
                <div class="text-center">
                    <p class="text-sm text-muted mb-sm">InvoiceFlow Pro</p>
                    <p class="text-xs text-muted">النسخة الاحترافية 2024</p>
                </div>
            </div>
        </aside>
        
        <!-- المحتوى الرئيسي -->
        <main class="main-content">
            <!-- شريط التنقل العلوي -->
            <nav class="navbar">
                <div class="flex items-center justify-between">
                    <div>
                        <h1 class="text-xl font-bold">{{ title }}</h1>
                        <p class="text-sm text-muted">{{ subtitle }}</p>
                    </div>
                    
                    <div class="flex items-center gap-md">
                        <div class="relative">
                            <button class="btn btn-outline flex items-center gap-sm">
                                <i class="fas fa-bell"></i>
                                <span class="hidden md:inline">الإشعارات</span>
                                <span class="badge badge-error absolute -top-1 -right-1">3</span>
                            </button>
                        </div>
                        
                        <div class="hidden md:block">
                            <div class="flex items-center gap-sm text-sm">
                                <i class="fas fa-clock text-muted"></i>
                                <span id="current-time">{{ current_time }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
            
            <!-- محتوى الصفحة -->
            <div class="content-container">
                {{ content|safe }}
            </div>
        </main>
    </div>
    
    <script>
        // تحديث الوقت
        function updateTime() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('ar-SA');
            document.getElementById('current-time').textContent = timeStr;
        }
        
        setInterval(updateTime, 1000);
        updateTime();
        
        // تحميل الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.3s ease';
            
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
        });
    </script>
</body>
</html>
"""

# ================== لوحة التحكم ==================

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    user_id = session['user_id']
    
    # إحصائيات المستخدم
    stats = {
        'total_invoices': db.execute_query(
            "SELECT COUNT(*) FROM invoices WHERE user_id = ?", 
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0,
        
        'total_revenue': db.execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE user_id = ? AND status = 'paid'", 
            (user_id,), fetchone=True
        )['COALESCE(SUM(total_amount), 0)'] or 0,
        
        'pending_invoices': db.execute_query(
            "SELECT COUNT(*) FROM invoices WHERE user_id = ? AND status = 'pending'", 
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0,
        
        'total_clients': db.execute_query(
            "SELECT COUNT(*) FROM clients WHERE user_id = ?", 
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0
    }
    
    # الفواتير الأخيرة
    recent_invoices = db.execute_query(
        """SELECT i.*, c.name as client_name 
           FROM invoices i 
           LEFT JOIN clients c ON i.client_id = c.id 
           WHERE i.user_id = ? 
           ORDER BY i.created_at DESC 
           LIMIT 5""",
        (user_id,), fetchall=True
    )
    
    content = f"""
    <!-- الإحصائيات -->
    <div class="grid-4 mb-xl">
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--info-color);">
                <i class="fas fa-file-invoice-dollar"></i>
            </div>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p class="text-muted">إجمالي الفواتير</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--success-color);">
                <i class="fas fa-dollar-sign"></i>
            </div>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p class="text-muted">إجمالي الإيرادات</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.1); color: var(--warning-color);">
                <i class="fas fa-clock"></i>
            </div>
            <div class="stat-number">{stats['pending_invoices']}</div>
            <p class="text-muted">فواتير معلقة</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(239, 68, 68, 0.1); color: var(--error-color);">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-number">{stats['total_clients']}</div>
            <p class="text-muted">إجمالي العملاء</p>
        </div>
    </div>
    
    <!-- الإجراءات السريعة -->
    <div class="grid-2 mb-xl">
        <div class="card">
            <div class="card-header">
                <h3 class="font-bold text-lg">إجراءات سريعة</h3>
            </div>
            <div class="grid-2 gap-md">
                <a href="{{ url_for('create_invoice') }}" class="btn btn-primary">
                    <i class="fas fa-plus-circle"></i>
                    إنشاء فاتورة
                </a>
                
                <a href="{{ url_for('clients') }}" class="btn btn-outline">
                    <i class="fas fa-user-plus"></i>
                    إضافة عميل
                </a>
                
                <a href="{{ url_for('products') }}" class="btn btn-outline">
                    <i class="fas fa-box"></i>
                    إضافة منتج
                </a>
                
                <a href="{{ url_for('reports') }}" class="btn btn-outline">
                    <i class="fas fa-chart-bar"></i>
                    عرض التقارير
                </a>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="font-bold text-lg">نظرة سريعة</h3>
            </div>
            <div class="space-y-md">
                <div class="flex items-center justify-between">
                    <span class="text-muted">فواتير هذا الشهر:</span>
                    <span class="font-bold">12</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">إيرادات هذا الشهر:</span>
                    <span class="font-bold text-success">$5,250</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">عملاء جدد:</span>
                    <span class="font-bold">3</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">معدل التحصيل:</span>
                    <span class="font-bold text-warning">85%</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- الفواتير الأخيرة -->
    <div class="card">
        <div class="card-header">
            <h3 class="font-bold text-lg">الفواتير الأخيرة</h3>
            <a href="{{ url_for('invoices') }}" class="text-sm text-info hover:underline">
                عرض الكل <i class="fas fa-arrow-left"></i>
            </a>
        </div>
        
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>رقم الفاتورة</th>
                        <th>العميل</th>
                        <th>التاريخ</th>
                        <th>المبلغ</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td class="font-medium">{inv['invoice_number']}</td>
                        <td>{inv['client_name'] or inv['client_name']}</td>
                        <td>{inv['issue_date']}</td>
                        <td class="font-bold">${inv['total_amount']:,.2f}</td>
                        <td>
                            <span class="badge {{
                                'badge-success' if inv['status'] == 'paid' else 
                                'badge-warning' if inv['status'] == 'pending' else 
                                'badge-error'
                            }}">
                                {{'مدفوعة' if inv['status'] == 'paid' else 'معلقة' if inv['status'] == 'pending' else 'ملغاة'}}
                            </span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="/invoice/view/{inv['id']}" class="text-info hover:underline">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="/invoice/download/{inv['id']}" class="text-success hover:underline">
                                    <i class="fas fa-download"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    ''' for inv in recent_invoices]) if recent_invoices else '''
                    <tr>
                        <td colspan="6" class="text-center p-xl text-muted">
                            <i class="fas fa-file-invoice-dollar text-3xl mb-md block"></i>
                            <p>لا توجد فواتير بعد</p>
                            <a href="{{ url_for('create_invoice') }}" class="btn btn-primary mt-md">
                                أنشئ أول فاتورة
                            </a>
                        </td>
                    </tr>
                    '''}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- ملخص الأداء -->
    <div class="grid-2 mt-xl">
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">ملخص الأداء</h3>
            <div class="space-y-md">
                <div>
                    <div class="flex justify-between mb-sm">
                        <span class="text-muted">فواتير مدفوعة</span>
                        <span class="font-bold">75%</span>
                    </div>
                    <div class="w-full bg-light rounded-full h-2">
                        <div class="bg-success h-2 rounded-full" style="width: 75%"></div>
                    </div>
                </div>
                
                <div>
                    <div class="flex justify-between mb-sm">
                        <span class="text-muted">فواتير معلقة</span>
                        <span class="font-bold">20%</span>
                    </div>
                    <div class="w-full bg-light rounded-full h-2">
                        <div class="bg-warning h-2 rounded-full" style="width: 20%"></div>
                    </div>
                </div>
                
                <div>
                    <div class="flex justify-between mb-sm">
                        <span class="text-muted">فواتير متأخرة</span>
                        <span class="font-bold">5%</span>
                    </div>
                    <div class="w-full bg-light rounded-full h-2">
                        <div class="bg-error h-2 rounded-full" style="width: 5%"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">نشاطات حديثة</h3>
            <div class="space-y-md">
                <div class="flex items-center gap-md p-md bg-dark rounded-lg">
                    <div class="p-sm bg-info/20 rounded-lg">
                        <i class="fas fa-file-invoice text-info"></i>
                    </div>
                    <div>
                        <p class="font-medium">فاتورة جديدة #INV-2024-001</p>
                        <p class="text-sm text-muted">منذ 2 ساعة</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-md p-md bg-dark rounded-lg">
                    <div class="p-sm bg-success/20 rounded-lg">
                        <i class="fas fa-check-circle text-success"></i>
                    </div>
                    <div>
                        <p class="font-medium">دفع فاتورة #INV-2023-125</p>
                        <p class="text-sm text-muted">منذ 5 ساعات</p>
                    </div>
                </div>
                
                <div class="flex items-center gap-md p-md bg-dark rounded-lg">
                    <div class="p-sm bg-warning/20 rounded-lg">
                        <i class="fas fa-user-plus text-warning"></i>
                    </div>
                    <div>
                        <p class="font-medium">إضافة عميل جديد</p>
                        <p class="text-sm text-muted">منذ يوم</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE, 
        css=BASE_CSS,
        title="لوحة التحكم",
        subtitle="نظرة عامة على أدائك وإحصائياتك",
        current_time=current_time,
        content=content
    )

# ================== صفحات الفواتير ==================

@app.route('/invoices')
@login_required
def invoices():
    """صفحة الفواتير"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">الفواتير</h2>
                <p class="text-muted">إدارة وعرض جميع فواتيرك</p>
            </div>
            <a href="{{ url_for('create_invoice') }}" class="btn btn-primary">
                <i class="fas fa-plus-circle"></i>
                إنشاء فاتورة جديدة
            </a>
        </div>
    </div>
    
    <!-- أدوات التصفية -->
    <div class="card mb-lg">
        <div class="grid-4 gap-md">
            <div>
                <label class="form-label">بحث</label>
                <input type="text" class="form-control" placeholder="بحث برقم الفاتورة أو اسم العميل...">
            </div>
            
            <div>
                <label class="form-label">الحالة</label>
                <select class="form-control">
                    <option value="">جميع الحالات</option>
                    <option value="paid">مدفوعة</option>
                    <option value="pending">معلقة</option>
                    <option value="overdue">متأخرة</option>
                    <option value="cancelled">ملغاة</option>
                </select>
            </div>
            
            <div>
                <label class="form-label">من تاريخ</label>
                <input type="date" class="form-control">
            </div>
            
            <div>
                <label class="form-label">إلى تاريخ</label>
                <input type="date" class="form-control">
            </div>
        </div>
        
        <div class="flex gap-md mt-lg">
            <button class="btn btn-primary">
                <i class="fas fa-filter"></i>
                تطبيق التصفية
            </button>
            
            <button class="btn btn-outline">
                <i class="fas fa-redo"></i>
                إعادة تعيين
            </button>
            
            <button class="btn btn-outline">
                <i class="fas fa-download"></i>
                تصدير البيانات
            </button>
        </div>
    </div>
    
    <!-- جدول الفواتير -->
    <div class="card">
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>
                            <input type="checkbox" class="rounded border-light">
                        </th>
                        <th>رقم الفاتورة</th>
                        <th>العميل</th>
                        <th>تاريخ الإصدار</th>
                        <th>تاريخ الاستحقاق</th>
                        <th>المبلغ</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><input type="checkbox" class="rounded border-light"></td>
                        <td class="font-medium">INV-2024-001</td>
                        <td>شركة النخبة للتجارة</td>
                        <td>2024-01-15</td>
                        <td>2024-02-15</td>
                        <td class="font-bold">$1,250.00</td>
                        <td>
                            <span class="badge badge-warning">
                                <i class="fas fa-clock mr-1"></i>
                                معلقة
                            </span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-info hover:underline" title="عرض">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="تحميل">
                                    <i class="fas fa-download"></i>
                                </a>
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-error hover:underline" title="حذف">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td><input type="checkbox" class="rounded border-light"></td>
                        <td class="font-medium">INV-2024-002</td>
                        <td>مؤسسة التقنية المتطورة</td>
                        <td>2024-01-10</td>
                        <td>2024-01-31</td>
                        <td class="font-bold">$3,500.00</td>
                        <td>
                            <span class="badge badge-success">
                                <i class="fas fa-check-circle mr-1"></i>
                                مدفوعة
                            </span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-info hover:underline" title="عرض">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="تحميل">
                                    <i class="fas fa-download"></i>
                                </a>
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td><input type="checkbox" class="rounded border-light"></td>
                        <td class="font-medium">INV-2024-003</td>
                        <td>مركز الخدمات الطبية</td>
                        <td>2024-01-05</td>
                        <td>2024-01-20</td>
                        <td class="font-bold">$850.00</td>
                        <td>
                            <span class="badge badge-error">
                                <i class="fas fa-exclamation-circle mr-1"></i>
                                متأخرة
                            </span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-info hover:underline" title="عرض">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="تحميل">
                                    <i class="fas fa-download"></i>
                                </a>
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-error hover:underline" title="إرسال تذكير">
                                    <i class="fas fa-envelope"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- الترقيم -->
        <div class="flex items-center justify-between p-lg border-t border-light">
            <div class="text-sm text-muted">
                عرض 1 إلى 3 من 45 فاتورة
            </div>
            
            <div class="flex gap-sm">
                <button class="btn btn-outline">
                    <i class="fas fa-chevron-right"></i>
                </button>
                <button class="btn btn-outline">1</button>
                <button class="btn btn-outline">2</button>
                <button class="btn btn-outline">3</button>
                <button class="btn btn-outline">...</button>
                <button class="btn btn-outline">10</button>
                <button class="btn btn-outline">
                    <i class="fas fa-chevron-left"></i>
                </button>
            </div>
        </div>
    </div>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="الفواتير",
        subtitle="إدارة وعرض جميع الفواتير",
        current_time=current_time,
        content=content
    )

@app.route('/invoices/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    """إنشاء فاتورة جديدة"""
    if request.method == 'POST':
        # معالجة إنشاء الفاتورة
        try:
            # جمع البيانات من النموذج
            client_name = request.form.get('client_name', '').strip()
            client_email = request.form.get('client_email', '').strip()
            client_phone = request.form.get('client_phone', '').strip()
            client_address = request.form.get('client_address', '').strip()
            issue_date = request.form.get('issue_date', '')
            due_date = request.form.get('due_date', '')
            tax_rate = float(request.form.get('tax_rate', 0))
            discount = float(request.form.get('discount', 0))
            payment_method = request.form.get('payment_method', 'نقدي')
            notes = request.form.get('notes', '').strip()
            
            # معالجة العناصر
            items = []
            subtotal = 0
            
            item_names = request.form.getlist('item_name[]')
            item_quantities = request.form.getlist('item_quantity[]')
            item_prices = request.form.getlist('item_price[]')
            
            for name, qty_str, price_str in zip(item_names, item_quantities, item_prices):
                if name.strip():
                    quantity = float(qty_str) if qty_str else 1
                    price = float(price_str) if price_str else 0
                    total = quantity * price
                    
                    items.append({
                        'name': name.strip(),
                        'quantity': quantity,
                        'price': price,
                        'total': total
                    })
                    
                    subtotal += total
            
            # حساب الضريبة والخصم
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount - discount
            
            # إنشاء رقم فاتورة فريد
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            # حفظ الفاتورة في قاعدة البيانات
            db.execute_query('''
                INSERT INTO invoices (
                    invoice_number, user_id, client_name, client_email, client_phone,
                    client_address, issue_date, due_date, items, subtotal, tax_rate,
                    tax_amount, discount, total_amount, payment_method, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_number, session['user_id'], client_name, client_email,
                client_phone, client_address, issue_date, due_date,
                json.dumps(items, ensure_ascii=False), subtotal, tax_rate,
                tax_amount, discount, total_amount, payment_method, notes, 'pending'
            ))
            
            flash('تم إنشاء الفاتورة بنجاح!', 'success')
            return redirect(url_for('invoices'))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء إنشاء الفاتورة: {str(e)}', 'error')
            return redirect(url_for('create_invoice'))
    
    # عرض نموذج إنشاء الفاتورة
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">إنشاء فاتورة جديدة</h2>
                <p class="text-muted">أدخل تفاصيل الفاتورة واضغط حفظ</p>
            </div>
            <a href="{{ url_for('invoices') }}" class="btn btn-outline">
                <i class="fas fa-arrow-right"></i>
                العودة للفواتير
            </a>
        </div>
    </div>
    
    <form method="POST" action="{{ url_for('create_invoice') }}" id="invoiceForm">
        <div class="grid-2 gap-xl">
            <!-- معلومات العميل -->
            <div class="space-y-lg">
                <div class="card">
                    <h3 class="font-bold text-lg mb-lg">معلومات العميل</h3>
                    
                    <div class="form-group">
                        <label class="form-label">اسم العميل *</label>
                        <input type="text" name="client_name" class="form-control" required 
                               placeholder="أدخل اسم العميل">
                    </div>
                    
                    <div class="grid-2 gap-md">
                        <div class="form-group">
                            <label class="form-label">البريد الإلكتروني</label>
                            <input type="email" name="client_email" class="form-control" 
                                   placeholder="client@example.com">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">رقم الهاتف</label>
                            <input type="tel" name="client_phone" class="form-control" 
                                   placeholder="+966 5X XXX XXXX">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">العنوان</label>
                        <textarea name="client_address" class="form-control" rows="3" 
                                  placeholder="أدخل عنوان العميل"></textarea>
                    </div>
                </div>
                
                <!-- تفاصيل الفاتورة -->
                <div class="card">
                    <h3 class="font-bold text-lg mb-lg">تفاصيل الفاتورة</h3>
                    
                    <div class="grid-2 gap-md">
                        <div class="form-group">
                            <label class="form-label">تاريخ الإصدار *</label>
                            <input type="date" name="issue_date" class="form-control" required 
                                   value="{{ datetime.now().strftime('%Y-%m-%d') }}">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">تاريخ الاستحقاق *</label>
                            <input type="date" name="due_date" class="form-control" required 
                                   value="{{ (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d') }}">
                        </div>
                    </div>
                    
                    <div class="grid-3 gap-md">
                        <div class="form-group">
                            <label class="form-label">نسبة الضريبة %</label>
                            <input type="number" name="tax_rate" class="form-control" 
                                   value="15" min="0" max="100" step="0.01">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">الخصم $</label>
                            <input type="number" name="discount" class="form-control" 
                                   value="0" min="0" step="0.01">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">طريقة الدفع</label>
                            <select name="payment_method" class="form-control">
                                <option value="نقدي">نقدي</option>
                                <option value="تحويل بنكي">تحويل بنكي</option>
                                <option value="بطاقة ائتمان">بطاقة ائتمان</option>
                                <option value="شيك">شيك</option>
                                <option value="أخرى">أخرى</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">ملاحظات إضافية</label>
                        <textarea name="notes" class="form-control" rows="3" 
                                  placeholder="أي ملاحظات أو شروط خاصة..."></textarea>
                    </div>
                </div>
            </div>
            
            <!-- العناصر -->
            <div class="space-y-lg">
                <div class="card">
                    <div class="flex items-center justify-between mb-lg">
                        <h3 class="font-bold text-lg">عناصر الفاتورة</h3>
                        <button type="button" onclick="addItem()" class="btn btn-primary">
                            <i class="fas fa-plus"></i>
                            إضافة عنصر
                        </button>
                    </div>
                    
                    <div id="itemsContainer">
                        <!-- العناصر ستضاف هنا ديناميكياً -->
                        <div class="item-row grid grid-cols-12 gap-md mb-md">
                            <div class="col-span-5">
                                <input type="text" name="item_name[]" class="form-control" 
                                       placeholder="اسم المنتج/الخدمة" required>
                            </div>
                            <div class="col-span-2">
                                <input type="number" name="item_quantity[]" class="form-control" 
                                       value="1" min="1" step="1" required>
                            </div>
                            <div class="col-span-3">
                                <input type="number" name="item_price[]" class="form-control" 
                                       placeholder="السعر" min="0" step="0.01" required>
                            </div>
                            <div class="col-span-2">
                                <button type="button" onclick="removeItem(this)" class="btn btn-danger w-full">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-lg p-md bg-dark rounded-lg">
                        <div class="grid-2 gap-md">
                            <div>
                                <div class="flex justify-between mb-sm">
                                    <span class="text-muted">المجموع الفرعي:</span>
                                    <span id="subtotal">$0.00</span>
                                </div>
                                <div class="flex justify-between mb-sm">
                                    <span class="text-muted">الضريبة:</span>
                                    <span id="tax">$0.00</span>
                                </div>
                                <div class="flex justify-between mb-sm">
                                    <span class="text-muted">الخصم:</span>
                                    <span id="discount">$0.00</span>
                                </div>
                            </div>
                            <div class="text-right">
                                <div class="text-2xl font-bold text-success mb-sm">
                                    الإجمالي: <span id="total">$0.00</span>
                                </div>
                                <p class="text-sm text-muted">شامل الضريبة والخصم</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- خيارات الحفظ -->
                <div class="card">
                    <h3 class="font-bold text-lg mb-lg">خيارات الحفظ</h3>
                    
                    <div class="grid-3 gap-md">
                        <button type="submit" name="action" value="save" class="btn btn-primary">
                            <i class="fas fa-save"></i>
                            حفظ الفاتورة
                        </button>
                        
                        <button type="submit" name="action" value="save_and_print" class="btn btn-success">
                            <i class="fas fa-print"></i>
                            حفظ وطباعة
                        </button>
                        
                        <a href="{{ url_for('invoices') }}" class="btn btn-outline">
                            <i class="fas fa-times"></i>
                            إلغاء
                        </a>
                    </div>
                    
                    <div class="mt-lg p-md bg-dark rounded-lg">
                        <label class="flex items-center gap-sm cursor-pointer">
                            <input type="checkbox" name="send_email" class="rounded border-light">
                            <span class="text-sm">إرسال نسخة بالبريد الإلكتروني للعميل</span>
                        </label>
                        
                        <label class="flex items-center gap-sm cursor-pointer mt-md">
                            <input type="checkbox" name="save_client" class="rounded border-light">
                            <span class="text-sm">حفظ العميل في قائمة العملاء</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    </form>
    
    <script>
        let itemCount = 1;
        
        function addItem() {
            const container = document.getElementById('itemsContainer');
            const newItem = document.createElement('div');
            newItem.className = 'item-row grid grid-cols-12 gap-md mb-md';
            newItem.innerHTML = `
                <div class="col-span-5">
                    <input type="text" name="item_name[]" class="form-control" 
                           placeholder="اسم المنتج/الخدمة" required>
                </div>
                <div class="col-span-2">
                    <input type="number" name="item_quantity[]" class="form-control" 
                           value="1" min="1" step="1" required>
                </div>
                <div class="col-span-3">
                    <input type="number" name="item_price[]" class="form-control" 
                           placeholder="السعر" min="0" step="0.01" required>
                </div>
                <div class="col-span-2">
                    <button type="button" onclick="removeItem(this)" class="btn btn-danger w-full">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(newItem);
            itemCount++;
            
            // إضافة مستمعات الأحداث للحقول الجديدة
            const inputs = newItem.querySelectorAll('input[type="number"]');
            inputs.forEach(input => {
                input.addEventListener('input', calculateTotals);
            });
        }
        
        function removeItem(button) {
            if (document.querySelectorAll('.item-row').length > 1) {
                button.closest('.item-row').remove();
                calculateTotals();
            }
        }
        
        function calculateTotals() {
            let subtotal = 0;
            
            document.querySelectorAll('.item-row').forEach(row => {
                const quantity = parseFloat(row.querySelector('input[name="item_quantity[]"]').value) || 0;
                const price = parseFloat(row.querySelector('input[name="item_price[]"]').value) || 0;
                subtotal += quantity * price;
            });
            
            const taxRate = parseFloat(document.querySelector('input[name="tax_rate"]').value) || 0;
            const discount = parseFloat(document.querySelector('input[name="discount"]').value) || 0;
            
            const tax = subtotal * (taxRate / 100);
            const total = subtotal + tax - discount;
            
            document.getElementById('subtotal').textContent = '$' + subtotal.toFixed(2);
            document.getElementById('tax').textContent = '$' + tax.toFixed(2);
            document.getElementById('discount').textContent = '$' + discount.toFixed(2);
            document.getElementById('total').textContent = '$' + total.toFixed(2);
        }
        
        // إضافة مستمعات الأحداث للحقول
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('input[name="tax_rate"], input[name="discount"]').forEach(input => {
                input.addEventListener('input', calculateTotals);
            });
            
            document.querySelectorAll('.item-row input[type="number"]').forEach(input => {
                input.addEventListener('input', calculateTotals);
            });
            
            calculateTotals();
        });
    </script>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="إنشاء فاتورة",
        subtitle="أدخل تفاصيل الفاتورة الجديدة",
        current_time=current_time,
        content=content,
        datetime=datetime,
        timedelta=timedelta
    )

# ================== صفحات العملاء ==================

@app.route('/clients')
@login_required
def clients():
    """صفحة العملاء"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">العملاء</h2>
                <p class="text-muted">إدارة قاعدة عملائك</p>
            </div>
            <button onclick="showAddClientModal()" class="btn btn-primary">
                <i class="fas fa-user-plus"></i>
                إضافة عميل جديد
            </button>
        </div>
    </div>
    
    <!-- إحصائيات العملاء -->
    <div class="grid-4 mb-lg">
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-info/20 rounded-lg">
                    <i class="fas fa-users text-info"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">45</p>
                    <p class="text-sm text-muted">إجمالي العملاء</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-success/20 rounded-lg">
                    <i class="fas fa-star text-success"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">12</p>
                    <p class="text-sm text-muted">عملاء VIP</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-warning/20 rounded-lg">
                    <i class="fas fa-clock text-warning"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">8</p>
                    <p class="text-sm text-muted">عملاء جدد</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-error/20 rounded-lg">
                    <i class="fas fa-exclamation-circle text-error"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">3</p>
                    <p class="text-sm text-muted">عملاء متأخرين</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- جدول العملاء -->
    <div class="card">
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>العميل</th>
                        <th>التواصل</th>
                        <th>الشركة</th>
                        <th>إجمالي المشتريات</th>
                        <th>آخر عملية</th>
                        <th>التصنيف</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <div class="flex items-center gap-md">
                                <div class="w-10 h-10 bg-info rounded-full flex items-center justify-center">
                                    <span class="font-bold text-white">ن</span>
                                </div>
                                <div>
                                    <p class="font-medium">شركة النخبة للتجارة</p>
                                    <p class="text-sm text-muted">محمد أحمد</p>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="space-y-xs">
                                <p class="text-sm">
                                    <i class="fas fa-envelope text-muted ml-xs"></i>
                                    info@elite.com
                                </p>
                                <p class="text-sm">
                                    <i class="fas fa-phone text-muted ml-xs"></i>
                                    +966 50 123 4567
                                </p>
                            </div>
                        </td>
                        <td>شركة النخبة</td>
                        <td class="font-bold">$45,250.00</td>
                        <td>2024-01-15</td>
                        <td>
                            <span class="badge badge-success">VIP</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-info hover:underline" title="عرض">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="إنشاء فاتورة">
                                    <i class="fas fa-file-invoice-dollar"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td>
                            <div class="flex items-center gap-md">
                                <div class="w-10 h-10 bg-success rounded-full flex items-center justify-center">
                                    <span class="font-bold text-white">ت</span>
                                </div>
                                <div>
                                    <p class="font-medium">مؤسسة التقنية المتطورة</p>
                                    <p class="text-sm text-muted">خالد سعيد</p>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="space-y-xs">
                                <p class="text-sm">
                                    <i class="fas fa-envelope text-muted ml-xs"></i>
                                    tech@advanced.com
                                </p>
                                <p class="text-sm">
                                    <i class="fas fa-phone text-muted ml-xs"></i>
                                    +966 55 987 6543
                                </p>
                            </div>
                        </td>
                        <td>مؤسسة التقنية</td>
                        <td class="font-bold">$32,500.00</td>
                        <td>2024-01-10</td>
                        <td>
                            <span class="badge badge-info">منتظم</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-info hover:underline" title="عرض">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="إنشاء فاتورة">
                                    <i class="fas fa-file-invoice-dollar"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td>
                            <div class="flex items-center gap-md">
                                <div class="w-10 h-10 bg-warning rounded-full flex items-center justify-center">
                                    <span class="font-bold text-white">خ</span>
                                </div>
                                <div>
                                    <p class="font-medium">مركز الخدمات الطبية</p>
                                    <p class="text-sm text-muted">د. فاطمة علي</p>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="space-y-xs">
                                <p class="text-sm">
                                    <i class="fas fa-envelope text-muted ml-xs"></i>
                                    medical@services.com
                                </p>
                                <p class="text-sm">
                                    <i class="fas fa-phone text-muted ml-xs"></i>
                                    +966 11 234 5678
                                </p>
                            </div>
                        </td>
                        <td>المركز الطبي</td>
                        <td class="font-bold">$8,750.00</td>
                        <td>2024-01-05</td>
                        <td>
                            <span class="badge badge-warning">جديد</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-info hover:underline" title="عرض">
                                    <i class="fas fa-eye"></i>
                                </a>
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="إنشاء فاتورة">
                                    <i class="fas fa-file-invoice-dollar"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- نموذج إضافة عميل (مودال) -->
    <div id="addClientModal" class="hidden fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-md">
        <div class="bg-dark rounded-xl border border-light w-full max-w-2xl">
            <div class="p-lg border-b border-light">
                <div class="flex items-center justify-between">
                    <h3 class="text-lg font-bold">إضافة عميل جديد</h3>
                    <button onclick="hideAddClientModal()" class="text-muted hover:text-white">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="p-lg">
                <form id="clientForm">
                    <div class="grid-2 gap-md">
                        <div class="form-group">
                            <label class="form-label">اسم العميل *</label>
                            <input type="text" class="form-control" required placeholder="الاسم الكامل">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">اسم الشركة</label>
                            <input type="text" class="form-control" placeholder="اسم الشركة">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">البريد الإلكتروني</label>
                            <input type="email" class="form-control" placeholder="example@email.com">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">رقم الهاتف</label>
                            <input type="tel" class="form-control" placeholder="+966 5X XXX XXXX">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">العنوان</label>
                        <textarea class="form-control" rows="2" placeholder="أدخل العنوان الكامل"></textarea>
                    </div>
                    
                    <div class="grid-2 gap-md">
                        <div class="form-group">
                            <label class="form-label">رقم الضريبي</label>
                            <input type="text" class="form-control" placeholder="الرقم الضريبي">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">التصنيف</label>
                            <select class="form-control">
                                <option value="عام">عام</option>
                                <option value="VIP">VIP</option>
                                <option value="منتظم">منتظم</option>
                                <option value="جديد">جديد</option>
                                <option value="خاص">خاص</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">ملاحظات</label>
                        <textarea class="form-control" rows="3" placeholder="أي ملاحظات إضافية..."></textarea>
                    </div>
                    
                    <div class="flex gap-md mt-lg">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i>
                            حفظ العميل
                        </button>
                        
                        <button type="button" onclick="hideAddClientModal()" class="btn btn-outline">
                            <i class="fas fa-times"></i>
                            إلغاء
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        function showAddClientModal() {
            document.getElementById('addClientModal').classList.remove('hidden');
        }
        
        function hideAddClientModal() {
            document.getElementById('addClientModal').classList.add('hidden');
        }
        
        // إغلاق المودال عند الضغط على ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                hideAddClientModal();
            }
        });
        
        // إغلاق المودال عند الضغط خارج المحتوى
        document.getElementById('addClientModal').addEventListener('click', function(e) {
            if (e.target === this) {
                hideAddClientModal();
            }
        });
    </script>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="العملاء",
        subtitle="إدارة قاعدة عملائك",
        current_time=current_time,
        content=content
    )

# ================== صفحات المنتجات ==================

@app.route('/products')
@login_required
def products():
    """صفحة المنتجات"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">المنتجات والخدمات</h2>
                <p class="text-muted">إدارة قائمة منتجاتك وخدماتك</p>
            </div>
            <button onclick="showAddProductModal()" class="btn btn-primary">
                <i class="fas fa-plus-circle"></i>
                إضافة منتج/خدمة
            </button>
        </div>
    </div>
    
    <!-- إحصائيات المنتجات -->
    <div class="grid-3 mb-lg">
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-info/20 rounded-lg">
                    <i class="fas fa-box text-info"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">24</p>
                    <p class="text-sm text-muted">إجمالي المنتجات</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-success/20 rounded-lg">
                    <i class="fas fa-bolt text-success"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">18</p>
                    <p class="text-sm text-muted">منتجات نشطة</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md">
                <div class="p-sm bg-warning/20 rounded-lg">
                    <i class="fas fa-tags text-warning"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">6</p>
                    <p class="text-sm text-muted">فئات المنتجات</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- جدول المنتجات -->
    <div class="card">
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>المنتج/الخدمة</th>
                        <th>الفئة</th>
                        <th>الوصف</th>
                        <th>السعر</th>
                        <th>الوحدة</th>
                        <th>الضريبة</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="font-medium">استشارة تقنية</td>
                        <td>
                            <span class="badge badge-info">استشارات</span>
                        </td>
                        <td class="text-sm text-muted">استشارة تقنية متخصصة لمدة ساعة</td>
                        <td class="font-bold">$150.00</td>
                        <td>ساعة</td>
                        <td>15%</td>
                        <td>
                            <span class="badge badge-success">نشط</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-error hover:underline" title="حذف">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td class="font-medium">تصميم موقع ويب</td>
                        <td>
                            <span class="badge badge-success">تصميم</span>
                        </td>
                        <td class="text-sm text-muted">تصميم موقع ويب احترافي متكامل</td>
                        <td class="font-bold">$1,200.00</td>
                        <td>مشروع</td>
                        <td>15%</td>
                        <td>
                            <span class="badge badge-success">نشط</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td class="font-medium">صيانة شهرية</td>
                        <td>
                            <span class="badge badge-warning">صيانة</span>
                        </td>
                        <td class="text-sm text-muted">خدمة صيانة وتحديثات شهرية</td>
                        <td class="font-bold">$300.00</td>
                        <td>شهر</td>
                        <td>15%</td>
                        <td>
                            <span class="badge badge-success">نشط</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    
                    <tr>
                        <td class="font-medium">تطبيق جوال</td>
                        <td>
                            <span class="badge badge-info">تطوير</span>
                        </td>
                        <td class="text-sm text-muted">تطوير تطبيق جوال متكامل</td>
                        <td class="font-bold">$5,000.00</td>
                        <td>مشروع</td>
                        <td>15%</td>
                        <td>
                            <span class="badge badge-error">غير نشط</span>
                        </td>
                        <td>
                            <div class="flex gap-sm">
                                <a href="#" class="text-warning hover:underline" title="تعديل">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="#" class="text-success hover:underline" title="تفعيل">
                                    <i class="fas fa-check"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- فئات المنتجات -->
    <div class="grid-2 mt-xl">
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">فئات المنتجات</h3>
            <div class="space-y-md">
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="p-sm bg-info/20 rounded-lg">
                            <i class="fas fa-code text-info"></i>
                        </div>
                        <span>تطوير</span>
                    </div>
                    <span class="text-sm text-muted">8 منتجات</span>
                </div>
                
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="p-sm bg-success/20 rounded-lg">
                            <i class="fas fa-paint-brush text-success"></i>
                        </div>
                        <span>تصميم</span>
                    </div>
                    <span class="text-sm text-muted">6 منتجات</span>
                </div>
                
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="p-sm bg-warning/20 rounded-lg">
                            <i class="fas fa-tools text-warning"></i>
                        </div>
                        <span>صيانة</span>
                    </div>
                    <span class="text-sm text-muted">4 منتجات</span>
                </div>
                
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="p-sm bg-error/20 rounded-lg">
                            <i class="fas fa-headset text-error"></i>
                        </div>
                        <span>استشارات</span>
                    </div>
                    <span class="text-sm text-muted">6 منتجات</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">المنتجات الأكثر مبيعاً</h3>
            <div class="space-y-md">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-md">
                        <div class="w-10 h-10 bg-info/20 rounded-lg flex items-center justify-center">
                            <i class="fas fa-code text-info"></i>
                        </div>
                        <div>
                            <p class="font-medium">تطوير موقع تجارة إلكترونية</p>
                            <p class="text-sm text-muted">12 عملية بيع</p>
                        </div>
                    </div>
                    <span class="font-bold text-success">$24,000</span>
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-md">
                        <div class="w-10 h-10 bg-success/20 rounded-lg flex items-center justify-center">
                            <i class="fas fa-paint-brush text-success"></i>
                        </div>
                        <div>
                            <p class="font-medium">تصميم هوية بصرية</p>
                            <p class="text-sm text-muted">8 عمليات بيع</p>
                        </div>
                    </div>
                    <span class="font-bold text-success">$9,600</span>
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-md">
                        <div class="w-10 h-10 bg-warning/20 rounded-lg flex items-center justify-center">
                            <i class="fas fa-tools text-warning"></i>
                        </div>
                        <div>
                            <p class="font-medium">صيانة سنوية</p>
                            <p class="text-sm text-muted">15 عملية بيع</p>
                        </div>
                    </div>
                    <span class="font-bold text-success">$4,500</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showAddProductModal() {
            alert('نموذج إضافة منتج/خدمة - سيتم تنفيذه في النسخة النهائية');
        }
    </script>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="المنتجات",
        subtitle="إدارة المنتجات والخدمات",
        current_time=current_time,
        content=content
    )

# ================== صفحات التقارير ==================

@app.route('/reports')
@login_required
def reports():
    """صفحة التقارير"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">التقارير والإحصائيات</h2>
                <p class="text-muted">تحليل أداء أعمالك وتقارير مفصلة</p>
            </div>
            <button onclick="generateReport()" class="btn btn-primary">
                <i class="fas fa-file-export"></i>
                تصدير تقرير
            </button>
        </div>
    </div>
    
    <!-- بطاقات التقارير -->
    <div class="grid-4 mb-lg">
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(59, 130, 246, 0.1); color: var(--info-color);">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-number">$125K</div>
            <p class="text-muted">إيرادات السنة</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(16, 185, 129, 0.1); color: var(--success-color);">
                <i class="fas fa-arrow-up"></i>
            </div>
            <div class="stat-number">+24%</div>
            <p class="text-muted">نمو الإيرادات</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(245, 158, 11, 0.1); color: var(--warning-color);">
                <i class="fas fa-file-invoice"></i>
            </div>
            <div class="stat-number">156</div>
            <p class="text-muted">فواتير السنة</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon" style="background: rgba(239, 68, 68, 0.1); color: var(--error-color);">
                <i class="fas fa-percentage"></i>
            </div>
            <div class="stat-number">92%</div>
            <p class="text-muted">معدل التحصيل</p>
        </div>
    </div>
    
    <!-- الرسوم البيانية -->
    <div class="grid-2 gap-xl mb-xl">
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">الإيرادات الشهرية</h3>
            <div class="h-64 flex items-end gap-sm">
                <div class="flex-1">
                    <div class="bg-info h-3/4 rounded-t-lg"></div>
                    <p class="text-center text-sm mt-sm">يناير</p>
                </div>
                <div class="flex-1">
                    <div class="bg-info h-2/3 rounded-t-lg"></div>
                    <p class="text-center text-sm mt-sm">فبراير</p>
                </div>
                <div class="flex-1">
                    <div class="bg-info h-full rounded-t-lg"></div>
                    <p class="text-center text-sm mt-sm">مارس</p>
                </div>
                <div class="flex-1">
                    <div class="bg-info h-4/5 rounded-t-lg"></div>
                    <p class="text-center text-sm mt-sm">أبريل</p>
                </div>
                <div class="flex-1">
                    <div class="bg-info h-3/4 rounded-t-lg"></div>
                    <p class="text-center text-sm mt-sm">مايو</p>
                </div>
                <div class="flex-1">
                    <div class="bg-success h-5/6 rounded-t-lg"></div>
                    <p class="text-center text-sm mt-sm">يونيو</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">توزيع الفواتير</h3>
            <div class="h-64 flex items-center justify-center">
                <div class="relative w-48 h-48">
                    <div class="absolute inset-0 rounded-full border-8 border-info" 
                         style="clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);"></div>
                    <div class="absolute inset-0 rounded-full border-8 border-success" 
                         style="clip-path: polygon(50% 50%, 100% 0, 100% 100%, 50% 50%);"></div>
                    <div class="absolute inset-0 rounded-full border-8 border-warning" 
                         style="clip-path: polygon(0 0, 50% 50%, 100% 0, 0 0);"></div>
                    <div class="absolute inset-0 flex items-center justify-center">
                        <div class="text-center">
                            <p class="text-2xl font-bold">100%</p>
                            <p class="text-sm text-muted">إجمالي</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="grid-3 gap-md mt-lg">
                <div class="text-center">
                    <div class="w-3 h-3 bg-info rounded-full inline-block ml-sm"></div>
                    <span class="text-sm">مدفوعة (65%)</span>
                </div>
                <div class="text-center">
                    <div class="w-3 h-3 bg-success rounded-full inline-block ml-sm"></div>
                    <span class="text-sm">معلقة (25%)</span>
                </div>
                <div class="text-center">
                    <div class="w-3 h-3 bg-warning rounded-full inline-block ml-sm"></div>
                    <span class="text-sm">متأخرة (10%)</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- التقارير المتاحة -->
    <div class="grid-3 gap-lg">
        <div class="card">
            <div class="p-sm bg-info/20 rounded-lg w-12 h-12 flex items-center justify-center mb-lg">
                <i class="fas fa-file-invoice-dollar text-info text-xl"></i>
            </div>
            <h4 class="font-bold text-lg mb-sm">تقرير المبيعات</h4>
            <p class="text-muted mb-lg">تحليل مفصل للمبيعات حسب الفترة والمنتجات</p>
            <a href="#" class="btn btn-outline w-full">
                <i class="fas fa-download ml-sm"></i>
                تحميل التقرير
            </a>
        </div>
        
        <div class="card">
            <div class="p-sm bg-success/20 rounded-lg w-12 h-12 flex items-center justify-center mb-lg">
                <i class="fas fa-users text-success text-xl"></i>
            </div>
            <h4 class="font-bold text-lg mb-sm">تقرير العملاء</h4>
            <p class="text-muted mb-lg">تحليل سلوك العملاء وتصنيفهم</p>
            <a href="#" class="btn btn-outline w-full">
                <i class="fas fa-download ml-sm"></i>
                تحميل التقرير
            </a>
        </div>
        
        <div class="card">
            <div class="p-sm bg-warning/20 rounded-lg w-12 h-12 flex items-center justify-center mb-lg">
                <i class="fas fa-chart-pie text-warning text-xl"></i>
            </div>
            <h4 class="font-bold text-lg mb-sm">تقرير الأداء</h4>
            <p class="text-muted mb-lg">قياس أداء الأعمال والمقارنات</p>
            <a href="#" class="btn btn-outline w-full">
                <i class="fas fa-download ml-sm"></i>
                تحميل التقرير
            </a>
        </div>
        
        <div class="card">
            <div class="p-sm bg-error/20 rounded-lg w-12 h-12 flex items-center justify-center mb-lg">
                <i class="fas fa-money-bill-wave text-error text-xl"></i>
            </div>
            <h4 class="font-bold text-lg mb-sm">تقرير الضرائب</h4>
            <p class="text-muted mb-lg">تقرير مفصل للضرائب والالتزامات</p>
            <a href="#" class="btn btn-outline w-full">
                <i class="fas fa-download ml-sm"></i>
                تحميل التقرير
            </a>
        </div>
        
        <div class="card">
            <div class="p-sm bg-purple-500/20 rounded-lg w-12 h-12 flex items-center justify-center mb-lg">
                <i class="fas fa-box text-purple-500 text-xl"></i>
            </div>
            <h4 class="font-bold text-lg mb-sm">تقرير المنتجات</h4>
            <p class="text-muted mb-lg">تحليل مبيعات المنتجات والأداء</p>
            <a href="#" class="btn btn-outline w-full">
                <i class="fas fa-download ml-sm"></i>
                تحميل التقرير
            </a>
        </div>
        
        <div class="card">
            <div class="p-sm bg-pink-500/20 rounded-lg w-12 h-12 flex items-center justify-center mb-lg">
                <i class="fas fa-cog text-pink-500 text-xl"></i>
            </div>
            <h4 class="font-bold text-lg mb-sm">تقرير مخصص</h4>
            <p class="text-muted mb-lg">إنشاء تقرير حسب احتياجاتك</p>
            <a href="#" onclick="showCustomReport()" class="btn btn-primary w-full">
                <i class="fas fa-plus ml-sm"></i>
                إنشاء تقرير
            </a>
        </div>
    </div>
    
    <script>
        function generateReport() {
            alert('سيتم تنفيذ تصدير التقارير في النسخة النهائية');
        }
        
        function showCustomReport() {
            alert('نموذج إنشاء تقرير مخصص - سيتم تنفيذه في النسخة النهائية');
        }
    </script>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="التقارير",
        subtitle="تحليل أداء أعمالك",
        current_time=current_time,
        content=content
    )

# ================== صفحات الذكاء الاصطناعي ==================

@app.route('/ai')
@login_required
def ai_insights():
    """صفحة الذكاء الاصطناعي"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">الذكاء الاصطناعي</h2>
                <p class="text-muted">تحليلات ذكية وتنبؤات مبنية على بياناتك</p>
            </div>
            <div class="flex items-center gap-sm text-success">
                <i class="fas fa-circle pulse"></i>
                <span class="text-sm">النظام نشط</span>
            </div>
        </div>
    </div>
    
    <!-- بطاقات الذكاء الاصطناعي -->
    <div class="grid-3 mb-lg">
        <div class="card">
            <div class="flex items-center gap-md mb-lg">
                <div class="p-sm bg-info/20 rounded-lg">
                    <i class="fas fa-brain text-info"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">94%</p>
                    <p class="text-sm text-muted">دقة التحليل</p>
                </div>
            </div>
            <p class="text-sm text-muted">معدل دقة تحليل البيانات والتنبؤات</p>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md mb-lg">
                <div class="p-sm bg-success/20 rounded-lg">
                    <i class="fas fa-bolt text-success"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">0.8s</p>
                    <p class="text-sm text-muted">سرعة الاستجابة</p>
                </div>
            </div>
            <p class="text-sm text-muted">متوسط وقت استجابة النظام</p>
        </div>
        
        <div class="card">
            <div class="flex items-center gap-md mb-lg">
                <div class="p-sm bg-warning/20 rounded-lg">
                    <i class="fas fa-chart-line text-warning"></i>
                </div>
                <div>
                    <p class="text-2xl font-bold">+28%</p>
                    <p class="text-sm text-muted">تحسين الأداء</p>
                </div>
            </div>
            <p class="text-sm text-muted">معدل التحسين المقترح لأدائك</p>
        </div>
    </div>
    
    <!-- لوحة الذكاء الاصطناعي -->
    <div class="grid-2 gap-xl mb-xl">
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">تحليل توقعات الإيرادات</h3>
            <div class="space-y-md">
                <div>
                    <div class="flex justify-between mb-sm">
                        <span class="text-muted">التوقعات لـ 2024:</span>
                        <span class="font-bold text-success">$185,000</span>
                    </div>
                    <div class="w-full bg-light rounded-full h-2">
                        <div class="bg-success h-2 rounded-full" style="width: 85%"></div>
                    </div>
                </div>
                
                <div>
                    <div class="flex justify-between mb-sm">
                        <span class="text-muted">نمو متوقع:</span>
                        <span class="font-bold text-info">+22%</span>
                    </div>
                    <div class="w-full bg-light rounded-full h-2">
                        <div class="bg-info h-2 rounded-full" style="width: 75%"></div>
                    </div>
                </div>
                
                <div>
                    <div class="flex justify-between mb-sm">
                        <span class="text-muted">أفضل ربع متوقع:</span>
                        <span class="font-bold text-warning">Q4 2024</span>
                    </div>
                    <div class="w-full bg-light rounded-full h-2">
                        <div class="bg-warning h-2 rounded-full" style="width: 90%"></div>
                    </div>
                </div>
            </div>
            
            <div class="mt-lg p-md bg-dark rounded-lg">
                <p class="text-sm font-medium mb-sm">توصية الذكاء الاصطناعي:</p>
                <p class="text-sm text-muted">ركز على العملاء في قطاع التجزئة خلال الربع الثالث لتعزيز الإيرادات بنسبة 15%.</p>
            </div>
        </div>
        
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">تحليل سلوك العملاء</h3>
            <div class="space-y-md">
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="w-8 h-8 bg-success rounded-full flex items-center justify-center">
                            <i class="fas fa-user-tie text-white text-sm"></i>
                        </div>
                        <div>
                            <p class="font-medium">العملاء المخلصون</p>
                            <p class="text-xs text-muted">35% من إجمالي العملاء</p>
                        </div>
                    </div>
                    <span class="text-success font-bold">+18%</span>
                </div>
                
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="w-8 h-8 bg-warning rounded-full flex items-center justify-center">
                            <i class="fas fa-clock text-white text-sm"></i>
                        </div>
                        <div>
                            <p class="font-medium">العملاء المتأخرون</p>
                            <p class="text-xs text-muted">12% من إجمالي العملاء</p>
                        </div>
                    </div>
                    <span class="text-warning font-bold">-8%</span>
                </div>
                
                <div class="flex items-center justify-between p-md bg-dark rounded-lg">
                    <div class="flex items-center gap-md">
                        <div class="w-8 h-8 bg-error rounded-full flex items-center justify-center">
                            <i class="fas fa-user-slash text-white text-sm"></i>
                        </div>
                        <div>
                            <p class="font-medium">العملاء الخاملون</p>
                            <p class="text-xs text-muted">5% من إجمالي العملاء</p>
                        </div>
                    </div>
                    <span class="text-error font-bold">-3%</span>
                </div>
            </div>
            
            <div class="mt-lg p-md bg-dark rounded-lg">
                <p class="text-sm font-medium mb-sm">توصية الذكاء الاصطناعي:</p>
                <p class="text-sm text-muted">إطلاق برنامج ولاء للعملاء المخلصين مع خصومات حصرية لزيادة الاحتفاظ بالعملاء.</p>
            </div>
        </div>
    </div>
    
    <!-- تحليل المنتجات -->
    <div class="card mb-xl">
        <h3 class="font-bold text-lg mb-lg">تحليل أداء المنتجات</h3>
        <div class="overflow-x-auto">
            <table class="table">
                <thead>
                    <tr>
                        <th>المنتج</th>
                        <th>الإيرادات</th>
                        <th>عدد المبيعات</th>
                        <th>هامش الربح</th>
                        <th>معدل النمو</th>
                        <th>التوصية</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="font-medium">تطوير مواقع ويب</td>
                        <td class="font-bold">$85,000</td>
                        <td>42</td>
                        <td>
                            <span class="badge badge-success">45%</span>
                        </td>
                        <td>
                            <span class="badge badge-success">+32%</span>
                        </td>
                        <td class="text-sm text-muted">زيادة التسعير بنسبة 10%</td>
                    </tr>
                    
                    <tr>
                        <td class="font-medium">استشارات تقنية</td>
                        <td class="font-bold">$35,000</td>
                        <td>78</td>
                        <td>
                            <span class="badge badge-warning">28%</span>
                        </td>
                        <td>
                            <span class="badge badge-success">+15%</span>
                        </td>
                        <td class="text-sm text-muted">حزمة استشارات شهرية</td>
                    </tr>
                    
                    <tr>
                        <td class="font-medium">صيانة دورية</td>
                        <td class="font-bold">$25,000</td>
                        <td>65</td>
                        <td>
                            <span class="badge badge-success">52%</span>
                        </td>
                        <td>
                            <span class="badge badge-error">-5%</span>
                        </td>
                        <td class="text-sm text-muted">تحسين التسويق للخدمة</td>
                    </tr>
                    
                    <tr>
                        <td class="font-medium">تصميم جرافيك</td>
                        <td class="font-bold">$15,000</td>
                        <td>24</td>
                        <td>
                            <span class="badge badge-success">38%</span>
                        </td>
                        <td>
                            <span class="badge badge-success">+45%</span>
                        </td>
                        <td class="text-sm text-muted">توسيع نطاق الخدمة</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- أداة الذكاء الاصطناعي التفاعلية -->
    <div class="card">
        <h3 class="font-bold text-lg mb-lg">مساعد الذكاء الاصطناعي</h3>
        <div class="space-y-md">
            <div class="p-md bg-dark rounded-lg">
                <div class="flex items-start gap-md">
                    <div class="p-sm bg-info/20 rounded-lg">
                        <i class="fas fa-robot text-info"></i>
                    </div>
                    <div class="flex-1">
                        <p class="font-medium mb-sm">مرحباً! أنا مساعد الذكاء الاصطناعي الخاص بك.</p>
                        <p class="text-sm text-muted">يمكنني مساعدتك في تحليل بياناتك، تقديم توصيات، والإجابة على أسئلتك المتعلقة بأعمالك.</p>
                    </div>
                </div>
            </div>
            
            <div class="grid-3 gap-md">
                <button onclick="askAI('تحليل أداء هذا الشهر')" class="btn btn-outline">
                    <i class="fas fa-chart-bar ml-sm"></i>
                    تحليل الأداء
                </button>
                
                <button onclick="askAI('توصيات لزيادة الإيرادات')" class="btn btn-outline">
                    <i class="fas fa-lightbulb ml-sm"></i>
                    الحصول على توصيات
                </button>
                
                <button onclick="askAI('تحليل العملاء الأفضل')" class="btn btn-outline">
                    <i class="fas fa-users ml-sm"></i>
                    تحليل العملاء
                </button>
            </div>
            
            <div class="flex gap-md">
                <input type="text" id="aiQuestion" class="form-control flex-1" 
                       placeholder="اطرح سؤالاً لمساعد الذكاء الاصطناعي...">
                <button onclick="askAICustom()" class="btn btn-primary">
                    <i class="fas fa-paper-plane"></i>
                    إرسال
                </button>
            </div>
            
            <div id="aiResponse" class="hidden p-md bg-dark rounded-lg">
                <!-- الاستجابة ستظهر هنا -->
            </div>
        </div>
    </div>
    
    <script>
        function askAI(question) {
            document.getElementById('aiQuestion').value = question;
            askAICustom();
        }
        
        function askAICustom() {
            const question = document.getElementById('aiQuestion').value;
            const responseDiv = document.getElementById('aiResponse');
            
            if (!question.trim()) {
                alert('يرجى إدخال سؤال');
                return;
            }
            
            // عرض رسالة تحميل
            responseDiv.innerHTML = `
                <div class="flex items-center gap-md">
                    <div class="animate-spin">
                        <i class="fas fa-circle-notch text-info"></i>
                    </div>
                    <span>جاري تحليل سؤالك...</span>
                </div>
            `;
            responseDiv.classList.remove('hidden');
            
            // محاكاة استجابة الذكاء الاصطناعي
            setTimeout(() => {
                const responses = [
                    `بناءً على تحليل بياناتك، ${question.toLowerCase()}، أوصي بالتركيز على تحسين تجربة العملاء وزيادة التفاعل مع العملاء الحاليين.`,
                    `تحليل بياناتك يشير إلى أن ${question.toLowerCase()} يحتاج إلى تحسين في عمليات المتابعة والتواصل المنتظم.`,
                    `لتحقيق أفضل نتائج في ${question.toLowerCase()}، أنصح بتنويع مصادر الدخل وتحسين جودة الخدمات المقدمة.`,
                    `بناءً على الأنماط التي اكتشفتها في بياناتك، ${question.toLowerCase()} يمكن تحسينه من خلال استراتيجية تسويقية أكثر استهدافاً.`
                ];
                
                const randomResponse = responses[Math.floor(Math.random() * responses.length)];
                
                responseDiv.innerHTML = `
                    <div class="flex items-start gap-md">
                        <div class="p-sm bg-info/20 rounded-lg">
                            <i class="fas fa-robot text-info"></i>
                        </div>
                        <div class="flex-1">
                            <p class="font-medium mb-sm">تحليل الذكاء الاصطناعي:</p>
                            <p class="text-sm">${randomResponse}</p>
                            <div class="mt-sm text-xs text-muted">
                                <i class="fas fa-info-circle ml-sm"></i>
                                هذا التحليل مبني على بياناتك التاريخية والأنماط المكتشفة.
                            </div>
                        </div>
                    </div>
                `;
            }, 1500);
        }
    </script>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="الذكاء الاصطناعي",
        subtitle="تحليلات ذكية وتنبؤات",
        current_time=current_time,
        content=content
    )

# ================== الصفحات الشخصية والإعدادات ==================

@app.route('/profile')
@login_required
def profile():
    """الملف الشخصي"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">الملف الشخصي</h2>
                <p class="text-muted">إدارة معلومات حسابك الشخصية</p>
            </div>
        </div>
    </div>
    
    <div class="grid-2 gap-xl">
        <!-- معلومات الحساب -->
        <div class="card">
            <h3 class="font-bold text-lg mb-lg">معلومات الحساب</h3>
            
            <div class="space-y-lg">
                <div class="flex items-center gap-md">
                    <div class="w-20 h-20 bg-info rounded-full flex items-center justify-center">
                        <span class="text-2xl font-bold text-white">{{ session.username[0].upper() }}</span>
                    </div>
                    <div>
                        <p class="font-bold text-lg">{{ session.username }}</p>
                        <p class="text-sm text-muted">{{ session.company_name }}</p>
                        <button class="btn btn-outline btn-sm mt-sm">
                            <i class="fas fa-camera ml-sm"></i>
                            تغيير الصورة
                        </button>
                    </div>
                </div>
                
                <div class="grid-2 gap-md">
                    <div class="form-group">
                        <label class="form-label">اسم المستخدم</label>
                        <input type="text" class="form-control" value="{{ session.username }}" readonly>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">الدور</label>
                        <input type="text" class="form-control" value="{{ session.user_role }}" readonly>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">اسم الشركة</label>
                        <input type="text" class="form-control" value="{{ session.company_name }}">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">البريد الإلكتروني</label>
                        <input type="email" class="form-control" placeholder="أدخل بريدك الإلكتروني">
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">رقم الهاتف</label>
                    <input type="tel" class="form-control" placeholder="+966 5X XXX XXXX">
                </div>
                
                <div class="form-group">
                    <label class="form-label">العنوان</label>
                    <textarea class="form-control" rows="3" placeholder="أدخل عنوانك"></textarea>
                </div>
                
                <button class="btn btn-primary w-full">
                    <i class="fas fa-save ml-sm"></i>
                    حفظ التغييرات
                </button>
            </div>
        </div>
        
        <!-- الأمان والإعدادات -->
        <div class="space-y-lg">
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">الأمان</h3>
                
                <div class="space-y-md">
                    <div>
                        <label class="form-label">كلمة المرور الحالية</label>
                        <input type="password" class="form-control" placeholder="أدخل كلمة المرور الحالية">
                    </div>
                    
                    <div>
                        <label class="form-label">كلمة المرور الجديدة</label>
                        <input type="password" class="form-control" placeholder="أدخل كلمة المرور الجديدة">
                    </div>
                    
                    <div>
                        <label class="form-label">تأكيد كلمة المرور الجديدة</label>
                        <input type="password" class="form-control" placeholder="أعد إدخال كلمة المرور الجديدة">
                    </div>
                    
                    <button class="btn btn-success w-full">
                        <i class="fas fa-key ml-sm"></i>
                        تغيير كلمة المرور
                    </button>
                </div>
            </div>
            
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">تفضيلات الإشعارات</h3>
                
                <div class="space-y-md">
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-envelope text-info"></i>
                            <span>إشعارات البريد الإلكتروني</span>
                        </div>
                        <input type="checkbox" class="rounded border-light" checked>
                    </label>
                    
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-bell text-warning"></i>
                            <span>إشعارات الفواتير الجديدة</span>
                        </div>
                        <input type="checkbox" class="rounded border-light" checked>
                    </label>
                    
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-exclamation-triangle text-error"></i>
                            <span>تنبيهات الدفع المتأخر</span>
                        </div>
                        <input type="checkbox" class="rounded border-light" checked>
                    </label>
                    
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-chart-line text-success"></i>
                            <span>تقارير الأداء الأسبوعية</span>
                        </div>
                        <input type="checkbox" class="rounded border-light">
                    </label>
                </div>
            </div>
            
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">معلومات النظام</h3>
                
                <div class="space-y-sm">
                    <div class="flex justify-between">
                        <span class="text-muted">رقم العضو:</span>
                        <span class="font-medium">#{{ session.user_id }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-muted">تاريخ الانضمام:</span>
                        <span class="font-medium">2024-01-01</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-muted">آخر دخول:</span>
                        <span class="font-medium">{{ current_time }}</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-muted">حالة الحساب:</span>
                        <span class="badge badge-success">نشط</span>
                    </div>
                    
                    <div class="flex justify-between">
                        <span class="text-muted">النسخة:</span>
                        <span class="font-medium">Pro 2024</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    current_time = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="الملف الشخصي",
        subtitle="إدارة معلومات حسابك",
        current_time=current_time,
        content=content
    )

@app.route('/settings')
@login_required
def settings():
    """صفحة الإعدادات"""
    content = """
    <div class="mb-xl">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold">الإعدادات</h2>
                <p class="text-muted">تخصيص النظام وإعداداته</p>
            </div>
        </div>
    </div>
    
    <div class="grid-2 gap-xl">
        <!-- إعدادات النظام -->
        <div class="space-y-lg">
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">إعدادات الفواتير</h3>
                
                <div class="space-y-md">
                    <div class="form-group">
                        <label class="form-label">بادئة رقم الفاتورة</label>
                        <input type="text" class="form-control" value="INV" placeholder="مثال: INV">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">نسبة الضريبة الافتراضية %</label>
                        <input type="number" class="form-control" value="15" min="0" max="100" step="0.01">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">عملة النظام</label>
                        <select class="form-control">
                            <option value="USD" selected>دولار أمريكي (USD)</option>
                            <option value="SAR">ريال سعودي (SAR)</option>
                            <option value="AED">درهم إماراتي (AED)</option>
                            <option value="EUR">يورو (EUR)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">عدد أيام الاستحقاق الافتراضي</label>
                        <input type="number" class="form-control" value="30" min="1" max="365">
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">المظهر واللغة</h3>
                
                <div class="space-y-md">
                    <div class="form-group">
                        <label class="form-label">اللغة</label>
                        <select class="form-control">
                            <option value="ar" selected>العربية</option>
                            <option value="en">الإنجليزية</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">الثيم</label>
                        <div class="grid-2 gap-md mt-sm">
                            <label class="cursor-pointer">
                                <div class="border-2 border-light rounded-lg p-md text-center hover:border-info">
                                    <div class="w-full h-20 bg-black rounded mb-sm"></div>
                                    <span>داكن</span>
                                </div>
                                <input type="radio" name="theme" class="hidden" checked>
                            </label>
                            
                            <label class="cursor-pointer">
                                <div class="border-2 border-light rounded-lg p-md text-center hover:border-info">
                                    <div class="w-full h-20 bg-white rounded mb-sm"></div>
                                    <span>فاتح</span>
                                </div>
                                <input type="radio" name="theme" class="hidden">
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">كثافة الظلال</label>
                        <select class="form-control">
                            <option value="light">خفيف</option>
                            <option value="medium" selected>متوسط</option>
                            <option value="heavy">ثقيل</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- الإعدادات المتقدمة -->
        <div class="space-y-lg">
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">الإعدادات المتقدمة</h3>
                
                <div class="space-y-md">
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-sync-alt text-info"></i>
                            <div>
                                <span>النسخ الاحتياطي التلقائي</span>
                                <p class="text-xs text-muted">نسخ احتياطي يومي للبيانات</p>
                            </div>
                        </div>
                        <input type="checkbox" class="rounded border-light" checked>
                    </label>
                    
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-robot text-success"></i>
                            <div>
                                <span>الذكاء الاصطناعي</span>
                                <p class="text-xs text-muted">تمكين تحليلات الذكاء الاصطناعي</p>
                            </div>
                        </div>
                        <input type="checkbox" class="rounded border-light" checked>
                    </label>
                    
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-shield-alt text-warning"></i>
                            <div>
                                <span>التوثيق الثنائي</span>
                                <p class="text-xs text-muted">طبقة أمان إضافية للحساب</p>
                            </div>
                        </div>
                        <input type="checkbox" class="rounded border-light">
                    </label>
                    
                    <label class="flex items-center justify-between cursor-pointer p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <i class="fas fa-bell text-error"></i>
                            <div>
                                <span>التنبيهات الصوتية</span>
                                <p class="text-xs text-muted">أصوات للتنبيهات المهمة</p>
                            </div>
                        </div>
                        <input type="checkbox" class="rounded border-light">
                    </label>
                </div>
            </div>
            
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">التكاملات</h3>
                
                <div class="space-y-md">
                    <div class="flex items-center justify-between p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <div class="p-sm bg-blue-500/20 rounded-lg">
                                <i class="fab fa-google text-blue-500"></i>
                            </div>
                            <div>
                                <span>Google Drive</span>
                                <p class="text-xs text-muted">مزامنة الفواتير والملفات</p>
                            </div>
                        </div>
                        <button class="btn btn-outline btn-sm">توصيل</button>
                    </div>
                    
                    <div class="flex items-center justify-between p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <div class="p-sm bg-green-500/20 rounded-lg">
                                <i class="fas fa-envelope text-green-500"></i>
                            </div>
                            <div>
                                <span>البريد الإلكتروني</span>
                                <p class="text-xs text-muted">إرسال الفواتير تلقائياً</p>
                            </div>
                        </div>
                        <button class="btn btn-outline btn-sm">تكوين</button>
                    </div>
                    
                    <div class="flex items-center justify-between p-sm hover:bg-dark rounded-lg">
                        <div class="flex items-center gap-sm">
                            <div class="p-sm bg-purple-500/20 rounded-lg">
                                <i class="fas fa-sms text-purple-500"></i>
                            </div>
                            <div>
                                <span>الرسائل النصية</span>
                                <p class="text-xs text-muted">إرسال تذكيرات بالدفع</p>
                            </div>
                        </div>
                        <button class="btn btn-outline btn-sm">تفعيل</button>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3 class="font-bold text-lg mb-lg">إجراءات النظام</h3>
                
                <div class="grid-2 gap-md">
                    <button class="btn btn-outline" onclick="backupData()">
                        <i class="fas fa-download ml-sm"></i>
                        نسخ احتياطي
                    </button>
                    
                    <button class="btn btn-outline" onclick="restoreData()">
                        <i class="fas fa-upload ml-sm"></i>
                        استعادة بيانات
                    </button>
                    
                    <button class="btn btn-outline" onclick="clearCache()">
                        <i class="fas fa-trash ml-sm"></i>
                        مسح الذاكرة
                    </button>
                    
                    <button class="btn btn-outline" onclick="exportData()">
                        <i class="fas fa-file-export ml-sm"></i>
                        تصدير البيانات
                    </button>
                </div>
                
                <div class="mt-lg">
                    <button class="btn btn-danger w-full" onclick="resetSettings()">
                        <i class="fas fa-redo ml-sm"></i>
                        إعادة تعيين الإعدادات
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function backupData() {
            if (confirm('هل تريد عمل نسخة احتياطية من جميع بياناتك؟')) {
                alert('جاري إنشاء النسخة الاحتياطية...');
                // سيتم تنفيذ النسخ الاحتياطي في النسخة النهائية
            }
        }
        
        function restoreData() {
            alert('سيتم تنفيذ استعادة البيانات في النسخة النهائية');
        }
        
        function clearCache() {
            if (confirm('هل تريد مسح ذاكرة التخزين المؤقت؟')) {
                alert('تم مسح الذاكرة المؤقتة بنجاح');
            }
        }
        
        function exportData() {
            alert('سيتم تنفيذ تصدير البيانات في النسخة النهائية');
        }
        
        function resetSettings() {
            if (confirm('هل تريد إعادة تعيين جميع الإعدادات إلى القيم الافتراضية؟')) {
                alert('تم إعادة تعيين الإعدادات بنجاح');
            }
        }
    </script>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        title="الإعدادات",
        subtitle="تخصيص النظام وإعداداته",
        current_time=current_time,
        content=content
    )

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

# ================== نظام توليد PDF ==================
class PDFGenerator:
    @staticmethod
    def generate_invoice_pdf(invoice_data):
        """إنشاء فاتورة PDF"""
        try:
            buffer = io.BytesIO()
            
            # إنشاء المستند
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            
            styles = getSampleStyleSheet()
            elements = []
            
            # العنوان
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.black,
                alignment=1,
                spaceAfter=30
            )
            
            elements.append(Paragraph("فاتورة ضريبية", title_style))
            elements.append(Spacer(1, 20))
            
            # معلومات الفاتورة
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                alignment=2  # Right
            )
            
            # معلومات الشركة
            company_info = f"""
            <b>معلومات البائع:</b><br/>
            {invoice_data.get('company_name', 'شركتي')}<br/>
            {invoice_data.get('company_address', 'العنوان')}<br/>
            الهاتف: {invoice_data.get('company_phone', '0000000000')}<br/>
            البريد الإلكتروني: {invoice_data.get('company_email', 'info@company.com')}
            """
            
            # معلومات العميل
            client_info = f"""
            <b>معلومات العميل:</b><br/>
            {invoice_data.get('client_name', 'عميل')}<br/>
            {invoice_data.get('client_address', 'العنوان')}<br/>
            الهاتف: {invoice_data.get('client_phone', '0000000000')}<br/>
            البريد الإلكتروني: {invoice_data.get('client_email', 'client@email.com')}
            """
            
            info_table = Table([
                [Paragraph(company_info, info_style), Paragraph(client_info, info_style)]
            ], colWidths=[250, 250])
            
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 30))
            
            # تفاصيل الفاتورة
            details_data = [
                ['رقم الفاتورة', invoice_data.get('invoice_number', 'INV-0001')],
                ['تاريخ الإصدار', invoice_data.get('issue_date', datetime.now().strftime('%Y/%m/%d'))],
                ['تاريخ الاستحقاق', invoice_data.get('due_date', datetime.now().strftime('%Y/%m/%d'))],
                ['طريقة الدفع', invoice_data.get('payment_method', 'نقدي')],
                ['الحالة', 'معلقة']
            ]
            
            details_table = Table(details_data, colWidths=[150, 150])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(details_table)
            elements.append(Spacer(1, 30))
            
            # جدول العناصر
            items = invoice_data.get('items', [])
            if not items:
                items = [
                    {'name': 'خدمة استشارية', 'quantity': 1, 'price': 1000, 'total': 1000},
                    {'name': 'تصميم جرافيك', 'quantity': 2, 'price': 500, 'total': 1000}
                ]
            
            items_data = [['الوصف', 'الكمية', 'السعر', 'المجموع']]
            
            for item in items:
                items_data.append([
                    item.get('name', ''),
                    str(item.get('quantity', 1)),
                    f"{item.get('price', 0):.2f}",
                    f"{item.get('total', 0):.2f}"
                ])
            
            # إضافة المجاميع
            subtotal = invoice_data.get('subtotal', 2000)
            tax = invoice_data.get('tax_amount', 300)
            discount = invoice_data.get('discount', 0)
            total = invoice_data.get('total_amount', 2300)
            
            items_data.append(['', '', 'المجموع الفرعي:', f"{subtotal:.2f}"])
            items_data.append(['', '', 'الضريبة:', f"{tax:.2f}"])
            items_data.append(['', '', 'الخصم:', f"-{discount:.2f}"])
            items_data.append(['', '', '<b>الإجمالي:</b>', f"<b>{total:.2f}</b>"])
            
            items_table = Table(items_data, colWidths=[250, 80, 80, 80])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-4, -4), colors.beige),
                ('TEXTCOLOR', (0, 1), (-4, -4), colors.black),
                ('GRID', (0, 0), (-4, -4), 1, colors.black),
                ('SPAN', (0, -4), (2, -4)),
                ('ALIGN', (0, -4), (2, -4), 'RIGHT'),
                ('BACKGROUND', (0, -4), (-1, -1), colors.lightgrey),
                ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 30))
            
            # الملاحظات
            if invoice_data.get('notes'):
                notes_style = ParagraphStyle(
                    'Notes',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.black,
                    alignment=2
                )
                
                notes_text = f"<b>ملاحظات:</b><br/>{invoice_data.get('notes')}"
                elements.append(Paragraph(notes_text, notes_style))
                elements.append(Spacer(1, 20))
            
            # التوقيع
            sign_style = ParagraphStyle(
                'Sign',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                alignment=1
            )
            
            elements.append(Spacer(1, 50))
            elements.append(Paragraph("_________________________", sign_style))
            elements.append(Paragraph("التوقيع", sign_style))
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("شكراً لتعاملك معنا", sign_style))
            
            # إنشاء PDF
            doc.build(elements)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"خطأ في إنشاء PDF: {e}")
            return None

# ================== API لإنشاء الفاتورة ==================
@app.route('/api/invoice/generate', methods=['POST'])
@login_required
def generate_invoice_api():
    """API لإنشاء فاتورة"""
    try:
        data = request.json
        
        # إنشاء بيانات الفاتورة
        invoice_data = {
            'invoice_number': f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            'company_name': session.get('company_name', 'شركتي'),
            'client_name': data.get('client_name', 'عميل'),
            'client_email': data.get('client_email', ''),
            'client_phone': data.get('client_phone', ''),
            'client_address': data.get('client_address', ''),
            'issue_date': data.get('issue_date', datetime.now().strftime('%Y-%m-%d')),
            'due_date': data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
            'items': data.get('items', []),
            'subtotal': data.get('subtotal', 0),
            'tax_amount': data.get('tax_amount', 0),
            'discount': data.get('discount', 0),
            'total_amount': data.get('total_amount', 0),
            'payment_method': data.get('payment_method', 'نقدي'),
            'notes': data.get('notes', '')
        }
        
        # إنشاء PDF
        pdf_buffer = PDFGenerator.generate_invoice_pdf(invoice_data)
        
        if pdf_buffer:
            # حفظ الفاتورة في قاعدة البيانات
            db.execute_query('''
                INSERT INTO invoices (
                    invoice_number, user_id, client_name, client_email, client_phone,
                    client_address, issue_date, due_date, items, subtotal,
                    tax_amount, discount, total_amount, payment_method, notes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_number'], session['user_id'],
                invoice_data['client_name'], invoice_data['client_email'],
                invoice_data['client_phone'], invoice_data['client_address'],
                invoice_data['issue_date'], invoice_data['due_date'],
                json.dumps(invoice_data['items'], ensure_ascii=False),
                invoice_data['subtotal'], invoice_data['tax_amount'],
                invoice_data['discount'], invoice_data['total_amount'],
                invoice_data['payment_method'], invoice_data['notes'], 'pending'
            ))
            
            # إرجاع PDF كاستجابة
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f"{invoice_data['invoice_number']}.pdf",
                mimetype='application/pdf'
            )
        else:
            return jsonify({'error': 'فشل في إنشاء الفاتورة'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ================== API للذكاء الاصطناعي ==================
@app.route('/api/ai/analyze', methods=['POST'])
@login_required
def ai_analyze():
    """API لتحليل البيانات بالذكاء الاصطناعي"""
    try:
        data = request.json
        analysis_type = data.get('type', 'revenue')
        user_id = session['user_id']
        
        # محاكاة تحليل الذكاء الاصطناعي
        analysis_results = {
            'revenue': {
                'prediction': random.randint(50000, 200000),
                'growth': random.randint(10, 40),
                'recommendation': 'ركز على العملاء الحاليين لتكرار المبيعات',
                'confidence': random.randint(85, 98)
            },
            'clients': {
                'segments': {
                    'vip': random.randint(5, 15),
                    'regular': random.randint(20, 40),
                    'new': random.randint(5, 10),
                    'inactive': random.randint(2, 5)
                },
                'recommendation': 'إطلاق برنامج ولاء للعملاء المخلصين',
                'retention_rate': random.randint(70, 95)
            },
            'products': {
                'top_performers': [
                    {'name': 'تطوير مواقع ويب', 'revenue': random.randint(20000, 80000)},
                    {'name': 'استشارات تقنية', 'revenue': random.randint(10000, 40000)},
                    {'name': 'صيانة دورية', 'revenue': random.randint(5000, 20000)}
                ],
                'recommendation': 'تحسين تسويق المنتجات عالية الربحية',
                'average_margin': random.randint(25, 50)
            }
        }
        
        result = analysis_results.get(analysis_type, {})
        
        return jsonify({
            'success': True,
            'analysis': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("\n" + "="*80)
        print("🚀 InvoiceFlow Pro - النظام الاحترافي الكامل")
        print("="*80)
        print("✅ النظام جاهز للعمل!")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("\n📋 المسارات المتاحة:")
        print("🔹 / - الصفحة الرئيسية (إعادة توجيه للدخول)")
        print("🔹 /login - تسجيل الدخول")
        print("🔹 /register - إنشاء حساب")
        print("🔹 /dashboard - لوحة التحكم")
        print("🔹 /invoices - إدارة الفواتير")
        print("🔹 /invoices/create - إنشاء فاتورة")
        print("🔹 /clients - إدارة العملاء")
        print("🔹 /products - المنتجات والخدمات")
        print("🔹 /reports - التقارير والإحصائيات")
        print("🔹 /ai - الذكاء الاصطناعي")
        print("🔹 /profile - الملف الشخصي")
        print("🔹 /settings - الإعدادات")
        print("🔹 /logout - تسجيل الخروج")
        print("\n🔧 واجهات API:")
        print("🔹 /api/invoice/generate - إنشاء فاتورة")
        print("🔹 /api/ai/analyze - تحليل ذكاء اصطناعي")
        print("\n👑 فريق العمل المحترف - النسخة النهائية")
        print("="*80)
        
        # تشغيل الخادم
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
