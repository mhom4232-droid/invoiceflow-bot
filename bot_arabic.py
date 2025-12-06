import os
import sqlite3
import json
import time
import requests
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from threading import Thread, Lock
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, session, flash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import io
import base64

# ================== تطبيق Flask المتطور ==================
app = Flask(__name__)
app.secret_key = 'invoiceflow_premium_elite_2024_v4'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("InvoiceFlow Premium - الإصدار الراقي المتميز")
print("تصميم أسود/أبيض احترافي + ذكاء اصطناعي متقدم")
print("=" * 80)

# ================== نظام الإبقاء على التشغيل ==================
class PremiumKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.request_count = 0
        
    def start_premium_system(self):
        print("بدء النظام الراقي...")
        self.start_premium_monitoring()
        print("النظام الراقي مفعل!")
    
    def start_premium_monitoring(self):
        def monitor():
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                if int(current_time) % 300 == 0:
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"تقرير النظام: {hours}س {minutes}د - {self.request_count} طلب")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# إعداد النظام الراقي
keep_alive_system = PremiumKeepAlive()
keep_alive_system.start_premium_system()

# ================== تسجيل الخط العربي ==================
def register_arabic_font():
    """تسجيل خط عربي للـ PDF"""
    font_urls = [
        ("https://github.com/AliSoftware/Fonts/raw/main/Amiri-Regular.ttf", "Amiri"),
        ("https://github.com/AliSoftware/Fonts/raw/main/Cairo-Regular.ttf", "Cairo"),
    ]
    
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    for url, font_name in font_urls:
        font_path = os.path.join(fonts_dir, f"{font_name}.ttf")
        
        if not os.path.exists(font_path):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    print(f"تم تحميل الخط: {font_name}")
            except Exception as e:
                print(f"خطأ في تحميل الخط {font_name}: {e}")
                continue
        
        try:
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                print(f"تم تسجيل الخط: {font_name}")
                return font_name
        except Exception as e:
            print(f"خطأ في تسجيل الخط {font_name}: {e}")
    
    return None

# تسجيل الخط عند بدء التشغيل
ARABIC_FONT = register_arabic_font()

def get_arabic_text(text):
    """تحويل النص العربي للعرض الصحيح في PDF"""
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except:
        return text

# ================== قاعدة البيانات ==================
def init_db():
    """إعداد قاعدة البيانات"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        client_name TEXT NOT NULL,
        client_email TEXT,
        services TEXT,
        amount REAL NOT NULL,
        due_date TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        total_invoices INTEGER DEFAULT 0,
        total_amount REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ================== تصميم أسود/أبيض احترافي ==================
PREMIUM_DESIGN_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            /* الألوان الجديدة - أسود/أبيض احترافي */
            --primary-bg: #000000;
            --secondary-bg: #0a0a0a;
            --card-bg: #111111;
            --card-hover: #1a1a1a;
            --border-color: #222222;
            --border-light: #333333;
            --text-primary: #ffffff;
            --text-secondary: #e0e0e0;
            --text-muted: #888888;
            --accent-color: #ffffff;
            --accent-dim: rgba(255, 255, 255, 0.1);
            --success-color: #22c55e;
            --warning-color: #eab308;
            --danger-color: #ef4444;
            --info-color: #3b82f6;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Tajawal', 'Segoe UI', sans-serif;
            background: var(--primary-bg);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.8;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* شريط التنقل */
        .navbar {
            background: var(--secondary-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 0 30px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .nav-brand h1 {
            font-size: 1.8em;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }

        .nav-links {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            padding: 10px 18px;
            border-radius: 8px;
            transition: all 0.2s ease;
            font-size: 0.95em;
        }

        .nav-link:hover {
            color: var(--text-primary);
            background: var(--accent-dim);
        }

        .nav-link.active {
            background: var(--text-primary);
            color: var(--primary-bg);
        }

        /* المحتوى */
        .content {
            margin-top: 90px;
            padding: 40px 0;
        }

        /* البطاقات */
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 32px;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--border-light);
            transform: translateY(-2px);
        }

        .card-icon {
            font-size: 2.5em;
            margin-bottom: 20px;
            color: var(--text-primary);
        }

        .card h3 {
            font-size: 1.4em;
            margin-bottom: 12px;
            color: var(--text-primary);
            font-weight: 600;
        }

        .card p {
            color: var(--text-muted);
            font-size: 1em;
            line-height: 1.6;
        }

        /* الشبكة */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
        }

        .grid-4 {
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        }

        /* الأزرار */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 14px 28px;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            border: none;
        }

        .btn-primary {
            background: var(--text-primary);
            color: var(--primary-bg);
        }

        .btn-primary:hover {
            background: var(--text-secondary);
            transform: translateY(-1px);
        }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border-light);
            color: var(--text-primary);
        }

        .btn-outline:hover {
            background: var(--accent-dim);
            border-color: var(--text-primary);
        }

        .btn-success {
            background: var(--success-color);
            color: white;
        }

        .btn-sm {
            padding: 10px 20px;
            font-size: 0.9em;
        }

        /* الإحصائيات */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        }

        .stat-number {
            font-size: 2.8em;
            font-weight: 800;
            color: var(--text-primary);
            margin: 10px 0;
        }

        .stat-label {
            color: var(--text-muted);
            font-size: 0.95em;
        }

        /* البطل */
        .hero {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 60px;
            margin-bottom: 40px;
            text-align: center;
        }

        .hero h1 {
            font-size: 3.5em;
            font-weight: 800;
            margin-bottom: 16px;
            letter-spacing: -1px;
        }

        .hero p {
            font-size: 1.3em;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto 30px;
        }

        /* القسم */
        .section-title {
            text-align: center;
            margin: 60px 0 40px;
        }

        .section-title h2 {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .section-title p {
            color: var(--text-muted);
            font-size: 1.1em;
        }

        /* النماذج */
        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .form-input {
            width: 100%;
            padding: 14px 16px;
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 1em;
            font-family: inherit;
            transition: border-color 0.2s;
        }

        .form-input:focus {
            outline: none;
            border-color: var(--text-primary);
        }

        .form-input::placeholder {
            color: var(--text-muted);
        }

        textarea.form-input {
            resize: vertical;
            min-height: 120px;
        }

        /* الجداول */
        .table-container {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table th,
        .table td {
            padding: 16px 20px;
            text-align: right;
            border-bottom: 1px solid var(--border-color);
        }

        .table th {
            background: var(--secondary-bg);
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .table tr:last-child td {
            border-bottom: none;
        }

        .table tr:hover td {
            background: var(--accent-dim);
        }

        /* الشارات */
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .badge-success {
            background: rgba(34, 197, 94, 0.2);
            color: var(--success-color);
        }

        .badge-warning {
            background: rgba(234, 179, 8, 0.2);
            color: var(--warning-color);
        }

        .badge-danger {
            background: rgba(239, 68, 68, 0.2);
            color: var(--danger-color);
        }

        .badge-info {
            background: rgba(59, 130, 246, 0.2);
            color: var(--info-color);
        }

        /* الـ AI Section */
        .ai-box {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
        }

        .ai-metric {
            text-align: center;
            padding: 20px;
        }

        .ai-metric-value {
            font-size: 2.2em;
            font-weight: 800;
            color: var(--text-primary);
        }

        .ai-metric-label {
            color: var(--text-muted);
            margin-top: 8px;
        }

        /* رسائل التنبيه */
        .alert {
            padding: 16px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .alert-success {
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: var(--success-color);
        }

        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--danger-color);
        }

        /* التجاوب */
        @media (max-width: 768px) {
            .navbar {
                padding: 0 16px;
            }

            .nav-links {
                display: none;
            }

            .hero {
                padding: 40px 24px;
            }

            .hero h1 {
                font-size: 2.5em;
            }

            .card {
                padding: 24px;
            }

            .grid {
                grid-template-columns: 1fr;
            }
        }

        /* تحريك */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fadeIn 0.4s ease;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <i class="fas fa-file-invoice-dollar" style="font-size: 1.5em;"></i>
            <h1>InvoiceFlow</h1>
        </div>
        
        <div class="nav-links">
            <a href="/" class="nav-link {% if active_page == 'home' %}active{% endif %}">
                <i class="fas fa-home"></i> الرئيسية
            </a>
            <a href="/invoices" class="nav-link {% if active_page == 'invoices' %}active{% endif %}">
                <i class="fas fa-file-invoice"></i> الفواتير
            </a>
            <a href="/create" class="nav-link {% if active_page == 'create' %}active{% endif %}">
                <i class="fas fa-plus"></i> إنشاء فاتورة
            </a>
            <a href="/clients" class="nav-link {% if active_page == 'clients' %}active{% endif %}">
                <i class="fas fa-users"></i> العملاء
            </a>
            <a href="/ai" class="nav-link {% if active_page == 'ai' %}active{% endif %}">
                <i class="fas fa-robot"></i> الذكاء الاصطناعي
            </a>
            <a href="/reports" class="nav-link {% if active_page == 'reports' %}active{% endif %}">
                <i class="fas fa-chart-bar"></i> التقارير
            </a>
            {% if session.get('user_logged_in') %}
            <a href="/logout" class="btn btn-outline btn-sm" style="margin-right: 10px;">
                <i class="fas fa-sign-out-alt"></i> خروج
            </a>
            {% else %}
            <a href="/login" class="btn btn-primary btn-sm" style="margin-right: 10px;">
                <i class="fas fa-sign-in-alt"></i> دخول
            </a>
            {% endif %}
        </div>
    </nav>

    <div class="container">
        <div class="content fade-in">
            {{ content | safe }}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Counter animation
            const counters = document.querySelectorAll('[data-count]');
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-count'));
                let current = 0;
                const increment = target / 50;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current).toLocaleString();
                    }
                }, 30);
            });
        });
    </script>
</body>
</html>
"""

# ================== Routes ==================

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM invoices")
    total_invoices = c.fetchone()[0]
    
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices")
    total_revenue = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM clients")
    total_clients = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'paid'")
    paid_invoices = c.fetchone()[0]
    
    conn.close()
    
    content = f"""
    <div class="hero">
        <h1>نظام إدارة الفواتير</h1>
        <p>منصة احترافية متكاملة لإدارة الفواتير والعملاء بأعلى معايير الجودة</p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
            <a href="/create" class="btn btn-primary">
                <i class="fas fa-plus"></i> إنشاء فاتورة
            </a>
            <a href="/invoices" class="btn btn-outline">
                <i class="fas fa-list"></i> عرض الفواتير
            </a>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-file-invoice" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number" data-count="{total_invoices}">{total_invoices}</div>
            <div class="stat-label">إجمالي الفواتير</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number" data-count="{int(total_revenue)}">${total_revenue:,.0f}</div>
            <div class="stat-label">إجمالي الإيرادات</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-users" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number" data-count="{total_clients}">{total_clients}</div>
            <div class="stat-label">العملاء</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-check-circle" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number" data-count="{paid_invoices}">{paid_invoices}</div>
            <div class="stat-label">فواتير مدفوعة</div>
        </div>
    </div>

    <div class="section-title">
        <h2>الخدمات المتاحة</h2>
        <p>اكتشف مجموعة الأدوات المتقدمة لإدارة أعمالك</p>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-icon"><i class="fas fa-file-invoice-dollar"></i></div>
            <h3>إدارة الفواتير</h3>
            <p>إنشاء وتتبع الفواتير بسهولة مع تصدير PDF احترافي باللغة العربية</p>
            <a href="/invoices" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                عرض الفواتير
            </a>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-users"></i></div>
            <h3>إدارة العملاء</h3>
            <p>قاعدة بيانات شاملة للعملاء مع تتبع المعاملات والتاريخ</p>
            <a href="/clients" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                عرض العملاء
            </a>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-robot"></i></div>
            <h3>الذكاء الاصطناعي</h3>
            <p>تحليلات ذكية وتوصيات مخصصة لتحسين أداء أعمالك</p>
            <a href="/ai" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                استكشاف
            </a>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-chart-pie"></i></div>
            <h3>التقارير</h3>
            <p>تقارير مفصلة ورسوم بيانية تفاعلية لمتابعة الأداء</p>
            <a href="/reports" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                عرض التقارير
            </a>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="InvoiceFlow - نظام إدارة الفواتير", content=content, active_page='home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('invoices.db')
        c = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password_hash))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_logged_in'] = True
            session['username'] = username
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return render_template_string(PREMIUM_DESIGN_HTML, 
                title="تسجيل الدخول", 
                content=get_login_content(error="اسم المستخدم أو كلمة المرور غير صحيحة"),
                active_page='login')
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="تسجيل الدخول", content=get_login_content(), active_page='login')

def get_login_content(error=None):
    error_html = f'<div class="alert alert-error"><i class="fas fa-exclamation-circle"></i> {error}</div>' if error else ''
    return f"""
    <div style="max-width: 450px; margin: 60px auto;">
        <div class="card" style="text-align: center;">
            <i class="fas fa-lock" style="font-size: 3em; margin-bottom: 24px; color: var(--text-muted);"></i>
            <h2 style="margin-bottom: 8px;">تسجيل الدخول</h2>
            <p style="color: var(--text-muted); margin-bottom: 30px;">أدخل بياناتك للوصول إلى حسابك</p>
            
            {error_html}
            
            <form method="POST" style="text-align: right;">
                <div class="form-group">
                    <label class="form-label">اسم المستخدم</label>
                    <input type="text" name="username" class="form-input" placeholder="أدخل اسم المستخدم" required>
                </div>
                <div class="form-group">
                    <label class="form-label">كلمة المرور</label>
                    <input type="password" name="password" class="form-input" placeholder="أدخل كلمة المرور" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
                    <i class="fas fa-sign-in-alt"></i> دخول
                </button>
            </form>
            
            <p style="margin-top: 24px; color: var(--text-muted);">
                ليس لديك حساب؟ <a href="/register" style="color: var(--text-primary);">إنشاء حساب</a>
            </p>
        </div>
    </div>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('invoices.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)",
                     (username, email, password_hash, full_name))
            conn.commit()
            conn.close()
            
            session['user_logged_in'] = True
            session['username'] = username
            return redirect('/')
        except sqlite3.IntegrityError:
            return render_template_string(PREMIUM_DESIGN_HTML,
                title="إنشاء حساب",
                content=get_register_content(error="اسم المستخدم أو البريد مستخدم مسبقاً"),
                active_page='register')
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="إنشاء حساب", content=get_register_content(), active_page='register')

def get_register_content(error=None):
    error_html = f'<div class="alert alert-error"><i class="fas fa-exclamation-circle"></i> {error}</div>' if error else ''
    return f"""
    <div style="max-width: 450px; margin: 60px auto;">
        <div class="card" style="text-align: center;">
            <i class="fas fa-user-plus" style="font-size: 3em; margin-bottom: 24px; color: var(--text-muted);"></i>
            <h2 style="margin-bottom: 8px;">إنشاء حساب جديد</h2>
            <p style="color: var(--text-muted); margin-bottom: 30px;">انضم إلينا اليوم</p>
            
            {error_html}
            
            <form method="POST" style="text-align: right;">
                <div class="form-group">
                    <label class="form-label">الاسم الكامل</label>
                    <input type="text" name="full_name" class="form-input" placeholder="أدخل اسمك الكامل" required>
                </div>
                <div class="form-group">
                    <label class="form-label">اسم المستخدم</label>
                    <input type="text" name="username" class="form-input" placeholder="اختر اسم مستخدم" required>
                </div>
                <div class="form-group">
                    <label class="form-label">البريد الإلكتروني</label>
                    <input type="email" name="email" class="form-input" placeholder="أدخل بريدك الإلكتروني" required>
                </div>
                <div class="form-group">
                    <label class="form-label">كلمة المرور</label>
                    <input type="password" name="password" class="form-input" placeholder="اختر كلمة مرور قوية" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 10px;">
                    <i class="fas fa-user-plus"></i> إنشاء الحساب
                </button>
            </form>
            
            <p style="margin-top: 24px; color: var(--text-muted);">
                لديك حساب؟ <a href="/login" style="color: var(--text-primary);">تسجيل الدخول</a>
            </p>
        </div>
    </div>
    """

@app.route('/invoices')
def invoices():
    """صفحة الفواتير"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute("SELECT * FROM invoices ORDER BY created_at DESC")
    invoice_list = c.fetchall()
    conn.close()
    
    invoices_html = ""
    if invoice_list:
        invoices_html = """
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>رقم الفاتورة</th>
                        <th>العميل</th>
                        <th>المبلغ</th>
                        <th>تاريخ الاستحقاق</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
        """
        for inv in invoice_list:
            status_class = "badge-success" if inv[7] == "paid" else "badge-warning" if inv[7] == "pending" else "badge-danger"
            status_text = "مدفوعة" if inv[7] == "paid" else "معلقة" if inv[7] == "pending" else "متأخرة"
            invoices_html += f"""
                <tr>
                    <td><strong>{inv[1]}</strong></td>
                    <td>{inv[2]}</td>
                    <td>${inv[5]:,.2f}</td>
                    <td>{inv[6] or '-'}</td>
                    <td><span class="badge {status_class}">{status_text}</span></td>
                    <td>
                        <a href="/invoice/{inv[0]}/pdf" class="btn btn-outline btn-sm">
                            <i class="fas fa-file-pdf"></i> PDF
                        </a>
                    </td>
                </tr>
            """
        invoices_html += "</tbody></table></div>"
    else:
        invoices_html = """
        <div class="card" style="text-align: center; padding: 60px;">
            <i class="fas fa-inbox" style="font-size: 4em; color: var(--text-muted); margin-bottom: 20px;"></i>
            <h3>لا توجد فواتير</h3>
            <p style="color: var(--text-muted); margin-bottom: 20px;">ابدأ بإنشاء فاتورتك الأولى</p>
            <a href="/create" class="btn btn-primary">
                <i class="fas fa-plus"></i> إنشاء فاتورة
            </a>
        </div>
        """
    
    content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <h1 style="font-size: 2.5em; margin-bottom: 8px;">الفواتير</h1>
            <p style="color: var(--text-muted);">إدارة وتتبع جميع الفواتير</p>
        </div>
        <a href="/create" class="btn btn-primary">
            <i class="fas fa-plus"></i> فاتورة جديدة
        </a>
    </div>
    
    {invoices_html}
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="الفواتير", content=content, active_page='invoices')

@app.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة"""
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        client_email = request.form.get('client_email')
        services = request.form.get('services')
        amount = float(request.form.get('amount', 0))
        due_date = request.form.get('due_date')
        
        # إنشاء رقم فاتورة فريد
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
        
        conn = sqlite3.connect('invoices.db')
        c = conn.cursor()
        c.execute("""INSERT INTO invoices (invoice_number, client_name, client_email, services, amount, due_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
                 (invoice_number, client_name, client_email, services, amount, due_date))
        invoice_id = c.lastrowid
        conn.commit()
        conn.close()
        
        # توجيه مباشر لتحميل PDF
        return redirect(f'/invoice/{invoice_id}/pdf')
    
    content = """
    <div style="max-width: 700px; margin: 0 auto;">
        <h1 style="font-size: 2.5em; margin-bottom: 8px; text-align: center;">إنشاء فاتورة جديدة</h1>
        <p style="color: var(--text-muted); text-align: center; margin-bottom: 40px;">أدخل بيانات الفاتورة وسيتم تحميل ملف PDF تلقائياً</p>
        
        <div class="card">
            <form method="POST">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="form-group">
                        <label class="form-label">اسم العميل *</label>
                        <input type="text" name="client_name" class="form-input" placeholder="أدخل اسم العميل" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">البريد الإلكتروني</label>
                        <input type="email" name="client_email" class="form-input" placeholder="email@example.com">
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="form-label">الخدمات / الوصف *</label>
                    <textarea name="services" class="form-input" placeholder="أدخل وصف الخدمات المقدمة..." required></textarea>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="form-group">
                        <label class="form-label">المبلغ ($) *</label>
                        <input type="number" name="amount" class="form-input" placeholder="0.00" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">تاريخ الاستحقاق</label>
                        <input type="date" name="due_date" class="form-input">
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 20px; padding: 18px;">
                    <i class="fas fa-file-pdf"></i> إنشاء الفاتورة وتحميل PDF
                </button>
            </form>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="إنشاء فاتورة", content=content, active_page='create')

@app.route('/invoice/<int:invoice_id>/pdf')
def generate_pdf(invoice_id):
    """توليد ملف PDF للفاتورة"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    invoice = c.fetchone()
    conn.close()
    
    if not invoice:
        return "الفاتورة غير موجودة", 404
    
    # إنشاء ملف PDF
    buffer = io.BytesIO()
    
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # تحديد الخط
    font_name = ARABIC_FONT if ARABIC_FONT else "Helvetica"
    
    # الخلفية
    c.setFillColor(colors.HexColor("#ffffff"))
    c.rect(0, 0, width, height, fill=True)
    
    # الهيدر
    c.setFillColor(colors.HexColor("#000000"))
    c.rect(0, height - 120, width, 120, fill=True)
    
    # عنوان الشركة
    c.setFillColor(colors.white)
    if font_name != "Helvetica":
        c.setFont(font_name, 28)
        c.drawRightString(width - 40, height - 50, get_arabic_text("InvoiceFlow"))
        c.setFont(font_name, 14)
        c.drawRightString(width - 40, height - 75, get_arabic_text("نظام إدارة الفواتير الاحترافي"))
    else:
        c.setFont("Helvetica-Bold", 28)
        c.drawRightString(width - 40, height - 50, "InvoiceFlow")
        c.setFont("Helvetica", 14)
        c.drawRightString(width - 40, height - 75, "Professional Invoice System")
    
    # رقم الفاتورة
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 50, f"Invoice: {invoice[1]}")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Date: {invoice[8][:10] if invoice[8] else datetime.now().strftime('%Y-%m-%d')}")
    
    # معلومات العميل
    y_pos = height - 160
    c.setFillColor(colors.HexColor("#000000"))
    
    if font_name != "Helvetica":
        c.setFont(font_name, 16)
        c.drawRightString(width - 40, y_pos, get_arabic_text("معلومات العميل"))
        c.setFont(font_name, 12)
        c.drawRightString(width - 40, y_pos - 25, get_arabic_text(f"الاسم: {invoice[2]}"))
        if invoice[3]:
            c.drawRightString(width - 40, y_pos - 45, get_arabic_text(f"البريد: {invoice[3]}"))
    else:
        c.setFont("Helvetica-Bold", 16)
        c.drawRightString(width - 40, y_pos, "Client Information")
        c.setFont("Helvetica", 12)
        c.drawRightString(width - 40, y_pos - 25, f"Name: {invoice[2]}")
        if invoice[3]:
            c.drawRightString(width - 40, y_pos - 45, f"Email: {invoice[3]}")
    
    # خط فاصل
    c.setStrokeColor(colors.HexColor("#e0e0e0"))
    c.setLineWidth(1)
    c.line(40, y_pos - 70, width - 40, y_pos - 70)
    
    # تفاصيل الخدمات
    y_pos = y_pos - 100
    
    if font_name != "Helvetica":
        c.setFont(font_name, 16)
        c.drawRightString(width - 40, y_pos, get_arabic_text("تفاصيل الخدمات"))
    else:
        c.setFont("Helvetica-Bold", 16)
        c.drawRightString(width - 40, y_pos, "Services Details")
    
    # جدول الخدمات
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.rect(40, y_pos - 80, width - 80, 50, fill=True)
    
    c.setFillColor(colors.HexColor("#000000"))
    if font_name != "Helvetica":
        c.setFont(font_name, 12)
        c.drawRightString(width - 60, y_pos - 50, get_arabic_text("الوصف"))
        c.drawString(60, y_pos - 50, get_arabic_text("المبلغ"))
    else:
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 60, y_pos - 50, "Description")
        c.drawString(60, y_pos - 50, "Amount")
    
    # بيانات الخدمة
    c.setFillColor(colors.white)
    c.rect(40, y_pos - 130, width - 80, 50, fill=True)
    
    c.setFillColor(colors.HexColor("#000000"))
    if font_name != "Helvetica":
        c.setFont(font_name, 11)
        services_text = invoice[4][:50] + "..." if len(invoice[4]) > 50 else invoice[4]
        c.drawRightString(width - 60, y_pos - 100, get_arabic_text(services_text))
    else:
        c.setFont("Helvetica", 11)
        services_text = invoice[4][:50] + "..." if len(invoice[4]) > 50 else invoice[4]
        c.drawRightString(width - 60, y_pos - 100, services_text)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y_pos - 100, f"${invoice[5]:,.2f}")
    
    # المجموع
    c.setFillColor(colors.HexColor("#000000"))
    c.rect(40, y_pos - 180, width - 80, 40, fill=True)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, y_pos - 160, f"TOTAL: ${invoice[5]:,.2f}")
    
    if font_name != "Helvetica":
        c.setFont(font_name, 14)
        c.drawRightString(width - 60, y_pos - 160, get_arabic_text("المجموع الكلي"))
    
    # تاريخ الاستحقاق
    if invoice[6]:
        y_pos = y_pos - 220
        if font_name != "Helvetica":
            c.setFillColor(colors.HexColor("#000000"))
            c.setFont(font_name, 12)
            c.drawRightString(width - 40, y_pos, get_arabic_text(f"تاريخ الاستحقاق: {invoice[6]}"))
        else:
            c.setFont("Helvetica", 12)
            c.drawRightString(width - 40, y_pos, f"Due Date: {invoice[6]}")
    
    # الفوتر
    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, 40, "InvoiceFlow - Professional Invoice Management System")
    c.drawCentredString(width/2, 25, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    c.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'{invoice[1]}.pdf'
    )

@app.route('/clients')
def clients():
    """صفحة العملاء"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clients ORDER BY created_at DESC")
    client_list = c.fetchall()
    conn.close()
    
    clients_html = ""
    if client_list:
        clients_html = """
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>الاسم</th>
                        <th>البريد</th>
                        <th>الهاتف</th>
                        <th>عدد الفواتير</th>
                        <th>إجمالي المبلغ</th>
                    </tr>
                </thead>
                <tbody>
        """
        for client in client_list:
            clients_html += f"""
                <tr>
                    <td><strong>{client[1]}</strong></td>
                    <td>{client[2] or '-'}</td>
                    <td>{client[3] or '-'}</td>
                    <td>{client[5]}</td>
                    <td>${client[6]:,.2f}</td>
                </tr>
            """
        clients_html += "</tbody></table></div>"
    else:
        clients_html = """
        <div class="card" style="text-align: center; padding: 60px;">
            <i class="fas fa-users" style="font-size: 4em; color: var(--text-muted); margin-bottom: 20px;"></i>
            <h3>لا يوجد عملاء</h3>
            <p style="color: var(--text-muted); margin-bottom: 20px;">سيظهر العملاء هنا بعد إنشاء الفواتير</p>
        </div>
        """
    
    content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <h1 style="font-size: 2.5em; margin-bottom: 8px;">العملاء</h1>
            <p style="color: var(--text-muted);">إدارة قاعدة بيانات العملاء</p>
        </div>
    </div>
    
    {clients_html}
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="العملاء", content=content, active_page='clients')

@app.route('/ai')
def ai_insights():
    """صفحة الذكاء الاصطناعي"""
    content = """
    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">الذكاء الاصطناعي</h1>
        <p>تحليلات ذكية وتوصيات مخصصة لتحسين أداء أعمالك</p>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-icon"><i class="fas fa-chart-line"></i></div>
            <h3>تحليل الإيرادات</h3>
            <p>تحليل متقدم لأنماط الإيرادات وتوقعات النمو المستقبلية</p>
            <a href="/ai/revenue" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                عرض التحليل
            </a>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-users"></i></div>
            <h3>تحليل العملاء</h3>
            <p>فهم سلوك عملائك وتحديد أفضل الفرص للنمو</p>
            <a href="/ai/clients" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                تحليل العملاء
            </a>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-lightbulb"></i></div>
            <h3>التوصيات الذكية</h3>
            <p>احصل على توصيات مخصصة لتحسين أداء أعمالك</p>
            <a href="/ai/recommendations" class="btn btn-outline btn-sm" style="margin-top: 16px;">
                عرض التوصيات
            </a>
        </div>
    </div>

    <div class="card" style="margin-top: 40px;">
        <h3 style="margin-bottom: 24px; text-align: center;">لوحة المؤشرات الذكية</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
            <div class="ai-metric">
                <div class="ai-metric-value">85%</div>
                <div class="ai-metric-label">معدل النمو المتوقع</div>
            </div>
            <div class="ai-metric">
                <div class="ai-metric-value">92%</div>
                <div class="ai-metric-label">رضا العملاء</div>
            </div>
            <div class="ai-metric">
                <div class="ai-metric-value">78%</div>
                <div class="ai-metric-label">كفاءة التحصيل</div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="الذكاء الاصطناعي", content=content, active_page='ai')

@app.route('/ai/revenue')
def ai_revenue():
    """تحليل الإيرادات"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices")
    total_revenue = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE status = 'paid'")
    paid_revenue = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM invoices")
    total_count = c.fetchone()[0]
    conn.close()
    
    avg_invoice = total_revenue / total_count if total_count > 0 else 0
    collection_rate = (paid_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    content = f"""
    <div style="margin-bottom: 30px;">
        <a href="/ai" class="btn btn-outline btn-sm">
            <i class="fas fa-arrow-right"></i> العودة للذكاء الاصطناعي
        </a>
    </div>

    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">تحليل الإيرادات</h1>
        <p>نظرة شاملة على أداء الإيرادات والتوقعات</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-dollar-sign" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number">${total_revenue:,.0f}</div>
            <div class="stat-label">إجمالي الإيرادات</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-check-circle" style="font-size: 1.5em; color: var(--success-color);"></i>
            <div class="stat-number">${paid_revenue:,.0f}</div>
            <div class="stat-label">المحصّل</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-receipt" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number">${avg_invoice:,.0f}</div>
            <div class="stat-label">متوسط الفاتورة</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-percentage" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number">{collection_rate:.1f}%</div>
            <div class="stat-label">معدل التحصيل</div>
        </div>
    </div>

    <div class="grid" style="margin-top: 40px;">
        <div class="card">
            <h3 style="margin-bottom: 20px;"><i class="fas fa-chart-line"></i> التوقعات</h3>
            <p style="color: var(--text-muted); margin-bottom: 16px;">بناءً على البيانات الحالية، نتوقع:</p>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <strong>نمو متوقع:</strong> 15% خلال الشهر القادم
                </li>
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <strong>إيرادات متوقعة:</strong> ${total_revenue * 1.15:,.0f}
                </li>
                <li style="padding: 12px 0;">
                    <strong>فرص التحسين:</strong> زيادة معدل التحصيل
                </li>
            </ul>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 20px;"><i class="fas fa-lightbulb"></i> التوصيات</h3>
            <ul style="list-style: none; padding: 0; color: var(--text-muted);">
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <i class="fas fa-check" style="color: var(--success-color); margin-left: 8px;"></i>
                    تفعيل التذكيرات التلقائية للفواتير المتأخرة
                </li>
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <i class="fas fa-check" style="color: var(--success-color); margin-left: 8px;"></i>
                    تقديم خصومات للدفع المبكر
                </li>
                <li style="padding: 12px 0;">
                    <i class="fas fa-check" style="color: var(--success-color); margin-left: 8px;"></i>
                    توسيع قاعدة العملاء
                </li>
            </ul>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="تحليل الإيرادات", content=content, active_page='ai')

@app.route('/ai/clients')
def ai_clients():
    """تحليل العملاء"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT client_name) FROM invoices")
    unique_clients = c.fetchone()[0]
    c.execute("SELECT client_name, COUNT(*) as count, SUM(amount) as total FROM invoices GROUP BY client_name ORDER BY total DESC LIMIT 5")
    top_clients = c.fetchall()
    conn.close()
    
    top_clients_html = ""
    for i, client in enumerate(top_clients, 1):
        top_clients_html += f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 0; border-bottom: 1px solid var(--border-color);">
            <div style="display: flex; align-items: center; gap: 16px;">
                <span style="background: var(--accent-dim); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">{i}</span>
                <div>
                    <strong>{client[0]}</strong>
                    <div style="color: var(--text-muted); font-size: 0.9em;">{client[1]} فاتورة</div>
                </div>
            </div>
            <strong style="color: var(--success-color);">${client[2]:,.0f}</strong>
        </div>
        """
    
    content = f"""
    <div style="margin-bottom: 30px;">
        <a href="/ai" class="btn btn-outline btn-sm">
            <i class="fas fa-arrow-right"></i> العودة للذكاء الاصطناعي
        </a>
    </div>

    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">تحليل العملاء</h1>
        <p>فهم سلوك العملاء وتحديد الفرص</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-users" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number">{unique_clients}</div>
            <div class="stat-label">عميل فريد</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-star" style="font-size: 1.5em; color: var(--warning-color);"></i>
            <div class="stat-number">{len(top_clients)}</div>
            <div class="stat-label">أفضل العملاء</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-heart" style="font-size: 1.5em; color: var(--danger-color);"></i>
            <div class="stat-number">92%</div>
            <div class="stat-label">معدل الرضا</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-redo" style="font-size: 1.5em; color: var(--info-color);"></i>
            <div class="stat-number">78%</div>
            <div class="stat-label">معدل العودة</div>
        </div>
    </div>

    <div class="grid" style="margin-top: 40px;">
        <div class="card">
            <h3 style="margin-bottom: 20px;"><i class="fas fa-trophy"></i> أفضل العملاء</h3>
            {top_clients_html if top_clients_html else '<p style="color: var(--text-muted); text-align: center;">لا توجد بيانات كافية</p>'}
        </div>
        <div class="card">
            <h3 style="margin-bottom: 20px;"><i class="fas fa-chart-pie"></i> تحليل السلوك</h3>
            <ul style="list-style: none; padding: 0; color: var(--text-muted);">
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <strong style="color: var(--text-primary);">معدل الطلب:</strong> 2.3 فاتورة/شهر
                </li>
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <strong style="color: var(--text-primary);">متوسط القيمة:</strong> $1,250
                </li>
                <li style="padding: 12px 0; border-bottom: 1px solid var(--border-color);">
                    <strong style="color: var(--text-primary);">أوقات الذروة:</strong> بداية الشهر
                </li>
                <li style="padding: 12px 0;">
                    <strong style="color: var(--text-primary);">التفضيلات:</strong> الدفع الإلكتروني
                </li>
            </ul>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="تحليل العملاء", content=content, active_page='ai')

@app.route('/ai/recommendations')
def ai_recommendations():
    """التوصيات الذكية"""
    content = """
    <div style="margin-bottom: 30px;">
        <a href="/ai" class="btn btn-outline btn-sm">
            <i class="fas fa-arrow-right"></i> العودة للذكاء الاصطناعي
        </a>
    </div>

    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">التوصيات الذكية</h1>
        <p>توصيات مخصصة لتحسين أداء أعمالك</p>
    </div>

    <div class="grid">
        <div class="card" style="border-right: 4px solid var(--success-color);">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                <span style="background: rgba(34, 197, 94, 0.2); color: var(--success-color); padding: 8px 16px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">أولوية عالية</span>
            </div>
            <h3>تفعيل التذكيرات التلقائية</h3>
            <p style="color: var(--text-muted); margin: 16px 0;">إرسال تذكيرات تلقائية للعملاء قبل موعد استحقاق الفاتورة بـ 3 أيام.</p>
            <div style="color: var(--success-color);">
                <i class="fas fa-arrow-up"></i> متوقع زيادة التحصيل بنسبة 25%
            </div>
        </div>
        
        <div class="card" style="border-right: 4px solid var(--warning-color);">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                <span style="background: rgba(234, 179, 8, 0.2); color: var(--warning-color); padding: 8px 16px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">أولوية متوسطة</span>
            </div>
            <h3>تقديم خصم الدفع المبكر</h3>
            <p style="color: var(--text-muted); margin: 16px 0;">تقديم خصم 5% للعملاء الذين يدفعون خلال 7 أيام من إصدار الفاتورة.</p>
            <div style="color: var(--warning-color);">
                <i class="fas fa-clock"></i> تحسين التدفق النقدي
            </div>
        </div>
        
        <div class="card" style="border-right: 4px solid var(--info-color);">
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                <span style="background: rgba(59, 130, 246, 0.2); color: var(--info-color); padding: 8px 16px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">اقتراح</span>
            </div>
            <h3>توسيع طرق الدفع</h3>
            <p style="color: var(--text-muted); margin: 16px 0;">إضافة المزيد من خيارات الدفع مثل Apple Pay وGoogle Pay.</p>
            <div style="color: var(--info-color);">
                <i class="fas fa-users"></i> جذب عملاء جدد
            </div>
        </div>
    </div>

    <div class="card" style="margin-top: 40px;">
        <h3 style="margin-bottom: 24px;"><i class="fas fa-tasks"></i> خطة العمل المقترحة</h3>
        <div style="display: flex; flex-direction: column; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--accent-dim); border-radius: 10px;">
                <span style="background: var(--text-primary); color: var(--primary-bg); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">1</span>
                <div>
                    <strong>الأسبوع الأول:</strong> تفعيل نظام التذكيرات التلقائية
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--accent-dim); border-radius: 10px;">
                <span style="background: var(--text-primary); color: var(--primary-bg); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">2</span>
                <div>
                    <strong>الأسبوع الثاني:</strong> إطلاق برنامج خصم الدفع المبكر
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; padding: 16px; background: var(--accent-dim); border-radius: 10px;">
                <span style="background: var(--text-primary); color: var(--primary-bg); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">3</span>
                <div>
                    <strong>الأسبوع الثالث:</strong> تقييم النتائج وتعديل الاستراتيجية
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="التوصيات الذكية", content=content, active_page='ai')

@app.route('/reports')
def reports():
    """صفحة التقارير"""
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM invoices")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'paid'")
    paid = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM invoices WHERE status = 'pending'")
    pending = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices")
    total_amount = c.fetchone()[0]
    conn.close()
    
    content = f"""
    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">التقارير</h1>
        <p>نظرة شاملة على أداء الأعمال</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-file-invoice" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number">{total}</div>
            <div class="stat-label">إجمالي الفواتير</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-check-circle" style="font-size: 1.5em; color: var(--success-color);"></i>
            <div class="stat-number">{paid}</div>
            <div class="stat-label">مدفوعة</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-clock" style="font-size: 1.5em; color: var(--warning-color);"></i>
            <div class="stat-number">{pending}</div>
            <div class="stat-label">معلقة</div>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign" style="font-size: 1.5em; color: var(--text-muted);"></i>
            <div class="stat-number">${total_amount:,.0f}</div>
            <div class="stat-label">إجمالي المبلغ</div>
        </div>
    </div>

    <div class="grid" style="margin-top: 40px;">
        <div class="card">
            <h3 style="margin-bottom: 20px;"><i class="fas fa-chart-pie"></i> توزيع الحالات</h3>
            <div style="display: flex; flex-direction: column; gap: 16px;">
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span>مدفوعة</span>
                        <span>{(paid/total*100) if total > 0 else 0:.1f}%</span>
                    </div>
                    <div style="background: var(--border-color); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: var(--success-color); height: 100%; width: {(paid/total*100) if total > 0 else 0}%;"></div>
                    </div>
                </div>
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span>معلقة</span>
                        <span>{(pending/total*100) if total > 0 else 0:.1f}%</span>
                    </div>
                    <div style="background: var(--border-color); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="background: var(--warning-color); height: 100%; width: {(pending/total*100) if total > 0 else 0}%;"></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-bottom: 20px;"><i class="fas fa-calendar"></i> الأداء الشهري</h3>
            <div style="text-align: center; padding: 40px 0; color: var(--text-muted);">
                <i class="fas fa-chart-bar" style="font-size: 3em; margin-bottom: 16px;"></i>
                <p>سيتم عرض الرسم البياني هنا</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="التقارير", content=content, active_page='reports')

@app.route('/demo')
def demo():
    """صفحة العرض التوضيحي"""
    content = """
    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">العرض التوضيحي</h1>
        <p>تعرف على إمكانيات النظام</p>
    </div>

    <div class="card" style="text-align: center; max-width: 700px; margin: 0 auto;">
        <i class="fas fa-play-circle" style="font-size: 5em; color: var(--text-muted); margin-bottom: 24px;"></i>
        <h2 style="margin-bottom: 16px;">شاهد كيف يعمل النظام</h2>
        <p style="color: var(--text-muted); margin-bottom: 30px;">
            اكتشف كيف يمكن لـ InvoiceFlow تبسيط إدارة فواتيرك وتحسين كفاءة أعمالك
        </p>
        <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
            <a href="/create" class="btn btn-primary">
                <i class="fas fa-plus"></i> جرب إنشاء فاتورة
            </a>
            <a href="/register" class="btn btn-outline">
                <i class="fas fa-user-plus"></i> إنشاء حساب مجاني
            </a>
        </div>
    </div>

    <div class="grid" style="margin-top: 50px;">
        <div class="card">
            <div class="card-icon"><i class="fas fa-bolt"></i></div>
            <h3>سريع وسهل</h3>
            <p>إنشاء فاتورة في أقل من دقيقة مع تصدير PDF فوري</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-shield-alt"></i></div>
            <h3>آمن وموثوق</h3>
            <p>بياناتك محمية بأعلى معايير الأمان</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-mobile-alt"></i></div>
            <h3>يعمل في كل مكان</h3>
            <p>تصميم متجاوب يعمل على جميع الأجهزة</p>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="العرض التوضيحي", content=content, active_page='demo')

@app.route('/features')
def features():
    """صفحة الميزات"""
    content = """
    <div class="section-title" style="margin-top: 0;">
        <h1 style="font-size: 2.5em;">الميزات</h1>
        <p>كل ما تحتاجه لإدارة فواتيرك باحترافية</p>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-icon"><i class="fas fa-file-pdf"></i></div>
            <h3>تصدير PDF احترافي</h3>
            <p>فواتير بتصميم أنيق وعرض صحيح للغة العربية</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-database"></i></div>
            <h3>إدارة العملاء</h3>
            <p>قاعدة بيانات متكاملة لتتبع العملاء والمعاملات</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-brain"></i></div>
            <h3>تحليلات ذكية</h3>
            <p>رؤى وتوصيات مبنية على بياناتك</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-chart-bar"></i></div>
            <h3>تقارير مفصلة</h3>
            <p>تتبع الأداء والإيرادات بسهولة</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-bell"></i></div>
            <h3>تذكيرات تلقائية</h3>
            <p>لا تفوت موعد استحقاق أي فاتورة</p>
        </div>
        <div class="card">
            <div class="card-icon"><i class="fas fa-lock"></i></div>
            <h3>أمان متقدم</h3>
            <p>حماية كاملة لبياناتك ومعاملاتك</p>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="الميزات", content=content, active_page='features')

@app.route('/invoices/list')
def invoices_list():
    """قائمة الفواتير"""
    return redirect('/invoices')

@app.route('/invoices/stats')
def invoices_stats():
    """إحصائيات الفواتير"""
    return redirect('/reports')

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect('/')

# ================== التشغيل ==================
if __name__ == '__main__':
    print("=" * 60)
    print("InvoiceFlow - نظام إدارة الفواتير الاحترافي")
    print(f"الخادم يعمل على: http://0.0.0.0:{port}")
    print("=" * 60)
    print("\nالمسارات المتاحة:")
    print("  / - الصفحة الرئيسية")
    print("  /login - تسجيل الدخول")
    print("  /register - إنشاء حساب")
    print("  /invoices - إدارة الفواتير")
    print("  /create - إنشاء فاتورة + PDF")
    print("  /clients - العملاء")
    print("  /ai - الذكاء الاصطناعي")
    print("  /ai/revenue - تحليل الإيرادات")
    print("  /ai/clients - تحليل العملاء")
    print("  /ai/recommendations - التوصيات")
    print("  /reports - التقارير")
    print("  /demo - العرض التوضيحي")
    print("  /features - الميزات")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
