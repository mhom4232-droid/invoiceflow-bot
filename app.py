import os
import sqlite3
import json
import time
import requests
import hashlib
import secrets
from datetime import datetime, timedelta
from threading import Thread, Lock
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, session, flash
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import io

# ================== تطبيق Flask ==================
app = Flask(__name__)
app.secret_key = 'invoiceflow_pro_secret_key_2024_advanced'

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - الإصدار المتقدم مع النظام الإداري")
print("🚀 واجهة سوداء عالمية + صلاحيات متقدمة")
print("👨💻 فريق البروفيسورات المتخصصين")
print("=" * 80)

# ================== نظام إدارة المستخدمين المتقدم ==================
class AdvancedUserManager:
    def __init__(self):
        self.db_path = 'invoices_pro.db'
        self.init_users_table()

    def init_users_table(self):
        """تهيئة جدول المستخدمين مع الصلاحيات المتقدمة"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    email TEXT,
                    full_name TEXT,
                    user_type TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')

            # 🔐 إضافة المدير الرئيسي (أنت) - كلمة سر قوية
            admin_password = self.hash_password("AdminMaster2024!")
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (username, password_hash, email, full_name, user_type) 
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_password, 'admin@invoiceflow.com', 'المدير الرئيسي', 'admin'))

            conn.commit()
            conn.close()
            print("✅ نظام المستخدمين المتقدم جاهز")
            print("🔐 بيانات المدير: admin / AdminMaster2024!")
        except Exception as e:
            print(f"🔧 خطأ في نظام المستخدمين: {e}")

    def hash_password(self, password):
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        """التحقق من المستخدم وتحديث آخر دخول"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash, user_type FROM users WHERE username = ? AND is_active = 1', (username,))
            result = cursor.fetchone()
            
            if result and result[0] == self.hash_password(password):
                # تحديث وقت آخر دخول
                cursor.execute('UPDATE users SET last_login = ? WHERE username = ?', 
                             (datetime.now(), username))
                conn.commit()
                conn.close()
                return True, result[1]  # إرجاع حالة النجاح ونوع المستخدم
            conn.close()
            return False, 'user'
        except Exception as e:
            print(f"🔧 خطأ في التحقق من المستخدم: {e}")
            return False, 'user'

    def create_user(self, username, password, email, full_name, user_type='user'):
        """إنشاء مستخدم جديد"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, user_type))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"🔧 خطأ في إنشاء المستخدم: {e}")
            return False

    def get_all_users(self):
        """جلب جميع المستخدمين (للمدير فقط)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, email, full_name, user_type, is_active, last_login
                FROM users ORDER BY created_at DESC
            ''')
            users = cursor.fetchall()
            conn.close()
            
            result = []
            for user in users:
                result.append({
                    'username': user[0],
                    'email': user[1],
                    'full_name': user[2],
                    'user_type': user[3],
                    'is_active': user[4],
                    'last_login': user[5]
                })
            return result
        except Exception as e:
            print(f"🔧 خطأ في جلب المستخدمين: {e}")
            return []

# ================== نظام PDF المحسن ==================
class ProfessionalPDFGenerator:
    """نظام إنشاء فواتير PDF احترافية - النسخة المحسنة"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """إعداد الأنماط المخصصة للعربية"""
        try:
            font_name = 'ArabicFont' if 'ArabicFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            
            self.arabic_title_style = ParagraphStyle(
                'ArabicTitle',
                parent=self.styles['Heading1'],
                fontName=font_name,
                fontSize=16,
                textColor=colors.darkblue,
                alignment=2,
                spaceAfter=12
            )
            
            self.arabic_normal_style = ParagraphStyle(
                'ArabicNormal',
                parent=self.styles['Normal'],
                fontName=font_name,
                fontSize=10,
                textColor=colors.black,
                alignment=2,
                spaceAfter=6
            )
            
            print(f"✅ تم إعداد أنماط PDF باستخدام الخط: {font_name}")
        except Exception as e:
            print(f"⚠️ استخدام الأنماط الافتراضية: {e}")
    
    def reshape_arabic_text(self, text):
        """إعادة تشكيل النص العربي"""
        if text:
            try:
                reshaped_text = arabic_reshaper.reshape(text)
                return get_display(reshaped_text)
            except:
                return text
        return text
    
    def create_professional_invoice(self, invoice_data):
        """إنشاء فاتورة PDF احترافية"""
        try:
            os.makedirs('invoices', exist_ok=True)
            safe_filename = f"{invoice_data['invoice_id']}_professional.pdf"
            file_path = f"invoices/{safe_filename}"
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            story = []
            
            # رأس الفاتورة
            header_data = [
                [self.reshape_arabic_text("فاتورة احترافية"), "", self.reshape_arabic_text("InvoiceFlow Pro")],
                [self.reshape_arabic_text("رقم الفاتورة: ") + invoice_data['invoice_id'], "", self.reshape_arabic_text("تاريخ الإصدار: ") + invoice_data['issue_date']],
            ]
            
            header_table = Table(header_data, colWidths=[60*mm, 30*mm, 60*mm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 15))
            
            # معلومات العميل
            client_info = f"""
            العميل: {invoice_data['client_name']}
            البريد: {invoice_data.get('client_email', 'غير محدد')}
            الهاتف: {invoice_data.get('client_phone', 'غير محدد')}
            """
            
            story.append(Paragraph(self.reshape_arabic_text(client_info), self.arabic_normal_style))
            story.append(Spacer(1, 20))
            
            # جدول الخدمات
            services_header = [
                self.reshape_arabic_text("الخدمة"),
                self.reshape_arabic_text("السعر"),
                self.reshape_arabic_text("المجموع")
            ]
            
            services_data = [services_header]
            total_amount = 0
            
            for service in invoice_data['services']:
                service_total = service['price'] * service.get('quantity', 1)
                total_amount += service_total
                
                services_data.append([
                    self.reshape_arabic_text(service['name']),
                    f"${service['price']:.2f}",
                    f"${service_total:.2f}"
                ])
            
            services_data.append([
                self.reshape_arabic_text("المجموع الإجمالي"),
                "",
                f"${total_amount:.2f}"
            ])
            
            services_table = Table(services_data, colWidths=[100*mm, 30*mm, 30*mm])
            services_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            story.append(services_table)
            
            # إنشاء PDF
            doc.build(story)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            with open(file_path, 'wb') as f:
                f.write(pdf_data)
            
            print(f"✅ تم إنشاء فاتورة PDF: {file_path}")
            return file_path, pdf_data
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF: {e}")
            return None, None

# ================== نظام قاعدة البيانات ==================
class DatabaseManager:
    def __init__(self):
        self.db_path = 'invoices_pro.db'
        self.init_database()

    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id TEXT UNIQUE,
                    user_id TEXT,
                    user_name TEXT,
                    company_name TEXT,
                    client_name TEXT,
                    client_email TEXT,
                    client_phone TEXT,
                    services_json TEXT,
                    total_amount REAL,
                    issue_date TEXT,
                    due_date TEXT,
                    pdf_path TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            print("✅ قاعدة البيانات المتطورة جاهزة")
        except Exception as e:
            print(f"🔧 خطأ في قاعدة البيانات: {e}")

    def save_invoice(self, invoice_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO invoices 
                (invoice_id, user_id, user_name, company_name, client_name, 
                 client_email, client_phone, services_json, total_amount, issue_date, due_date, pdf_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_id'],
                invoice_data.get('user_id', 'web_user'),
                invoice_data.get('user_name', 'مستخدم الويب'),
                invoice_data.get('company_name', 'شركتك'),
                invoice_data['client_name'],
                invoice_data.get('client_email', ''),
                invoice_data.get('client_phone', ''),
                json.dumps(invoice_data['services'], ensure_ascii=False),
                invoice_data['total_amount'],
                invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                invoice_data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
                invoice_data.get('pdf_path', '')
            ))

            conn.commit()
            conn.close()
            print(f"✅ تم حفظ الفاتورة: {invoice_data['invoice_id']}")
            return True
        except Exception as e:
            print(f"🔧 خطأ في حفظ الفاتورة: {e}")
            return False

    def get_all_invoices(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT invoice_id, client_name, total_amount, issue_date, services_json, pdf_path
                FROM invoices 
                ORDER BY created_at DESC
            ''')
            invoices = cursor.fetchall()
            conn.close()
            
            result = []
            for invoice in invoices:
                result.append({
                    'invoice_id': invoice[0],
                    'client_name': invoice[1],
                    'total_amount': invoice[2],
                    'issue_date': invoice[3],
                    'services': json.loads(invoice[4]) if invoice[4] else [],
                    'pdf_path': invoice[5]
                })
            return result
        except Exception as e:
            print(f"🔧 خطأ في جلب الفواتير: {e}")
            return []

    def get_user_invoices(self, username):
        """جلب فواتير مستخدم محدد"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT invoice_id, client_name, total_amount, issue_date, services_json, pdf_path
                FROM invoices 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (username,))
            invoices = cursor.fetchall()
            conn.close()
            
            result = []
            for invoice in invoices:
                result.append({
                    'invoice_id': invoice[0],
                    'client_name': invoice[1],
                    'total_amount': invoice[2],
                    'issue_date': invoice[3],
                    'services': json.loads(invoice[4]) if invoice[4] else [],
                    'pdf_path': invoice[5]
                })
            return result
        except Exception as e:
            print(f"🔧 خطأ في جلب فواتير المستخدم: {e}")
            return []

    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM invoices')
            total_invoices, total_revenue = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) FROM invoices WHERE date(created_at) = date("now")')
            today_invoices = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_invoices': total_invoices,
                'total_revenue': total_revenue,
                'today_invoices': today_invoices
            }
        except Exception as e:
            print(f"🔧 خطأ في جلب الإحصائيات: {e}")
            return {'total_invoices': 0, 'total_revenue': 0, 'today_invoices': 0}

# ================== إعداد الأنظمة ==================
db_manager = DatabaseManager()
pdf_generator = ProfessionalPDFGenerator()
user_manager = AdvancedUserManager()

# ================== نظام الإبقاء على التشغيل ==================
class AdvancedKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.ping_count = 0
        
    def start_keep_alive(self):
        print("🔄 بدء أنظمة الاستمرارية...")
        self.start_self_monitoring()
        print("✅ أنظمة الاستمرارية مفعلة!")
    
    def start_self_monitoring(self):
        def monitor():
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                if int(current_time) % 600 == 0:
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"📊 تقرير النظام: {hours}س {minutes}د - {self.ping_count} زيارات")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# بدء نظام الاستمرارية
keep_alive_system = AdvancedKeepAlive()
keep_alive_system.start_keep_alive()

# ================== ديكورات المصادقة والصلاحيات ==================
def login_required(f):
    """ديكور للتحقق من تسجيل الدخول"""
    def decorated_function(*args, **kwargs):
        if 'user_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    """ديكور للتحقق من صلاحيات المدير"""
    def decorated_function(*args, **kwargs):
        if 'user_logged_in' not in session or session.get('user_type') != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ================== القوالب - التصميم الأسود العالمي ==================
MODERN_BLACK_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #10b981;
            --accent: #f59e0b;
            --danger: #ef4444;
            
            /* Dark Theme */
            --bg-primary: #0f0f0f;
            --bg-secondary: #1a1a1a;
            --bg-card: #262626;
            --bg-hover: #333333;
            --text-primary: #ffffff;
            --text-secondary: #a3a3a3;
            --text-muted: #737373;
            --border: #404040;
            --shadow: rgba(0, 0, 0, 0.5);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }
        
        .glass-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid var(--border);
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px var(--shadow);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px var(--shadow);
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2em;
            color: var(--text-secondary);
        }
        
        .user-info {
            position: absolute;
            left: 20px;
            top: 20px;
            background: var(--bg-card);
            padding: 10px 20px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        
        .admin-badge {
            background: var(--accent);
            color: var(--bg-primary);
            padding: 2px 8px;
            border-radius: 5px;
            font-size: 0.8em;
            margin-right: 10px;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .nav-card {
            background: var(--bg-secondary);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: var(--text-primary);
            text-decoration: none;
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }
        
        .nav-card:hover {
            background: var(--bg-hover);
            transform: translateY(-3px);
            border-color: var(--primary);
        }
        
        .nav-card i {
            font-size: 2.5em;
            margin-bottom: 15px;
            display: block;
            color: var(--primary);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: var(--bg-card);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            border: 1px solid var(--border);
        }
        
        .stat-number {
            font-size: 2.8em;
            font-weight: bold;
            margin: 10px 0;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .invoice-grid {
            display: grid;
            gap: 20px;
        }
        
        .invoice-card {
            background: var(--bg-card);
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid var(--primary);
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }
        
        .invoice-card:hover {
            transform: translateX(5px);
            border-left-color: var(--secondary);
        }
        
        .btn {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
        }
        
        .btn-outline {
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--secondary), #059669);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, var(--danger), #dc2626);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-primary);
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .form-control {
            width: 100%;
            padding: 15px;
            border: 2px solid var(--border);
            border-radius: 10px;
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            background: var(--bg-card);
        }
        
        .form-control::placeholder {
            color: var(--text-muted);
        }
        
        .alert {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
            border: 1px solid;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.1);
            border-color: var(--secondary);
            color: var(--secondary);
        }
        
        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--danger);
            color: var(--danger);
        }
        
        .alert-info {
            background: rgba(99, 102, 241, 0.1);
            border-color: var(--primary);
            color: var(--primary);
        }
        
        .login-container {
            max-width: 400px;
            margin: 100px auto;
        }
        
        .user-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .user-table th,
        .user-table td {
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid var(--border);
        }
        
        .user-table th {
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-weight: 600;
        }
        
        .feature-list {
            list-style: none;
            margin: 20px 0;
        }
        
        .feature-list li {
            padding: 10px 0;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }
        
        .feature-list li:before {
            content: "✓";
            color: var(--secondary);
            font-weight: bold;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="glass-container">
        {% if session.user_logged_in %}
        <div class="user-info">
            {% if session.user_type == 'admin' %}
            <span class="admin-badge">👑 مدير</span>
            {% endif %}
            <i class="fas fa-user"></i> {{ session.username }} 
            | <a href="{{ url_for('logout') }}" style="color: var(--primary); margin-right: 15px;">تسجيل خروج</a>
        </div>
        {% endif %}
        
        <div class="header">
            <h1><i class="fas fa-file-invoice-dollar"></i> InvoiceFlow Pro</h1>
            <p>🚀 النظام الاحترافي لإدارة الفواتير - الإصدار المتقدم</p>
            <p>⏰ مدة التشغيل: {{ uptime }}</p>
        </div>
        
        {% if session.user_logged_in %}
        <div class="nav-grid">
            <a href="/" class="nav-card">
                <i class="fas fa-home"></i>
                <h3>الرئيسية</h3>
            </a>
            <a href="/invoices" class="nav-card">
                <i class="fas fa-file-invoice"></i>
                <h3>الفواتير</h3>
            </a>
            <a href="/create" class="nav-card">
                <i class="fas fa-plus-circle"></i>
                <h3>إنشاء فاتورة</h3>
            </a>
            {% if session.user_type == 'admin' %}
            <a href="/admin" class="nav-card">
                <i class="fas fa-crown"></i>
                <h3>لوحة التحكم</h3>
            </a>
            {% endif %}
            <a href="/stats" class="nav-card">
                <i class="fas fa-chart-bar"></i>
                <h3>الإحصائيات</h3>
            </a>
        </div>
        {% endif %}

        {{ content | safe }}
    </div>
</body>
</html>
"""

# ================== Routes نظام تسجيل الدخول ==================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        is_valid, user_type = user_manager.verify_user(username, password)
        
        if is_valid:
            session['user_logged_in'] = True
            session['username'] = username
            session['user_type'] = user_type
            return redirect(url_for('home'))
        else:
            content = """
            <div class="login-container">
                <div class="glass-card">
                    <h2 style="margin-bottom: 30px; text-align: center;">تسجيل الدخول</h2>
                    <div class="alert alert-error">
                        ❌ اسم المستخدم أو كلمة المرور غير صحيحة
                    </div>
                    <form method="POST">
                        <div class="form-group">
                            <input type="text" name="username" class="form-control" placeholder="اسم المستخدم" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="password" class="form-control" placeholder="كلمة المرور" required>
                        </div>
                        <button type="submit" class="btn" style="width: 100%;">تسجيل الدخول</button>
                    </form>
                    <div style="margin-top: 20px; color: var(--text-secondary); text-align: center;">
                        <p>بيانات الدخول الافتراضية للمدير:</p>
                        <p>اسم المستخدم: <strong>admin</strong></p>
                        <p>كلمة المرور: <strong>AdminMaster2024!</strong></p>
                    </div>
                </div>
            </div>
            """
            return render_template_string(MODERN_BLACK_HTML, title="تسجيل الدخول - InvoiceFlow Pro", uptime="", content=content)
    
    if 'user_logged_in' in session:
        return redirect(url_for('home'))
    
    content = """
    <div class="login-container">
        <div class="glass-card">
            <h2 style="margin-bottom: 30px; text-align: center;">تسجيل الدخول</h2>
            <form method="POST">
                <div class="form-group">
                    <input type="text" name="username" class="form-control" placeholder="اسم المستخدم" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" class="form-control" placeholder="كلمة المرور" required>
                </div>
                <button type="submit" class="btn" style="width: 100%;">تسجيل الدخول</button>
            </form>
            <div style="margin-top: 20px; color: var(--text-secondary); text-align: center;">
                <p>بيانات الدخول الافتراضية للمدير:</p>
                <p>اسم المستخدم: <strong>admin</strong></p>
                <p>كلمة المرور: <strong>AdminMaster2024!</strong></p>
            </div>
        </div>
    </div>
    """
    return render_template_string(MODERN_BLACK_HTML, title="تسجيل الدخول - InvoiceFlow Pro", uptime="", content=content)

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

# ================== Routes محمية ==================
@app.route('/')
@login_required
def home():
    """الصفحة الرئيسية"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    
    # جلب الفواتير حسب نوع المستخدم
    if session.get('user_type') == 'admin':
        invoices = db_manager.get_all_invoices()
    else:
        invoices = db_manager.get_user_invoices(session.get('username', ''))
    
    user_invoices_count = len(invoices)
    user_revenue = sum(inv['total_amount'] for inv in invoices)
    
    content = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-file-invoice"></i>
            <div class="stat-number">{user_invoices_count}</div>
            <p>فواتيرك</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-number">${user_revenue:,.0f}</div>
            <p>إيراداتك</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-calendar-day"></i>
            <div class="stat-number">{stats['today_invoices']}</div>
            <p>فواتير اليوم</p>
        </div>
    </div>
    
    <div class="glass-card">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-rocket"></i> مرحباً بك في InvoiceFlow Pro
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px;">
            <div>
                <h3 style="color: var(--secondary); margin-bottom: 15px;">🚀 المميزات:</h3>
                <ul class="feature-list">
                    <li>فواتير PDF احترافية</li>
                    <li>واجهة سوداء عالمية</li>
                    <li>نظام أمان متقدم</li>
                    <li>إحصائيات مفصلة</li>
                    <li>دعم كامل للعربية</li>
                    {'<li>صلاحيات إدارية متقدمة</li>' if session.get('user_type') == 'admin' else ''}
                </ul>
            </div>
            
            <div>
                <h3 style="color: var(--secondary); margin-bottom: 15px;">📊 إجراءات سريعة:</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <a href="/create" class="btn" style="text-align: center;">
                        <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
                    </a>
                    <a href="/invoices" class="btn btn-outline" style="text-align: center;">
                        <i class="fas fa-list"></i> عرض الفواتير
                    </a>
                    {'<a href="/admin" class="btn btn-success" style="text-align: center;">
                        <i class="fas fa-crown"></i> لوحة التحكم
                    </a>' if session.get('user_type') == 'admin' else ''}
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(MODERN_BLACK_HTML, title="InvoiceFlow Pro - النظام المتقدم", uptime=uptime_str, content=content)

@app.route('/admin')
@admin_required
def admin_panel():
    """لوحة تحكم المدير"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    users = user_manager.get_all_users()
    stats = db_manager.get_stats()
    
    users_html = ""
    for user in users:
        user_type_badge = '<span class="admin-badge">👑 مدير</span>' if user['user_type'] == 'admin' else '<span style="color: var(--text-secondary);">👤 مستخدم</span>'
        status_badge = '<span style="color: var(--secondary);">✅ نشط</span>' if user['is_active'] else '<span style="color: var(--danger);">❌ غير نشط</span>'
        
        users_html += f"""
        <tr>
            <td>{user_type_badge} {user['username']}</td>
            <td>{user['full_name']}</td>
            <td>{user['email']}</td>
            <td>{status_badge}</td>
            <td>{user['last_login'] or 'لم يسجل دخول'}</td>
        </tr>
        """
    
    content = f"""
    <div class="glass-card">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-crown"></i> لوحة تحكم المدير
        </h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <i class="fas fa-users"></i>
                <div class="stat-number">{len(users)}</div>
                <p>إجمالي المستخدمين</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-file-invoice"></i>
                <div class="stat-number">{stats['total_invoices']}</div>
                <p>إجمالي الفواتير</p>
            </div>
            <div class="stat-card">
                <i class="fas fa-dollar-sign"></i>
                <div class="stat-number">${stats['total_revenue']:,.0f}</div>
                <p>إجمالي الإيرادات</p>
            </div>
        </div>
    </div>
    
    <div class="glass-card">
        <h3 style="margin-bottom: 20px; color: var(--accent);">
            <i class="fas fa-users-cog"></i> إدارة المستخدمين
        </h3>
        
        <table class="user-table">
            <thead>
                <tr>
                    <th>اسم المستخدم</th>
                    <th>الاسم الكامل</th>
                    <th>البريد الإلكتروني</th>
                    <th>الحالة</th>
                    <th>آخر دخول</th>
                </tr>
            </thead>
            <tbody>
                {users_html}
            </tbody>
        </table>
    </div>
    
    <div class="glass-card">
        <h3 style="margin-bottom: 15px; color: var(--accent);">🔧 أدوات المدير</h3>
        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
            <button class="btn" onclick="alert('سيتم تطوير هذه الميزة قريباً')">
                <i class="fas fa-plus"></i> إضافة مستخدم
            </button>
            <button class="btn btn-outline" onclick="alert('سيتم تطوير هذه الميزة قريباً')">
                <i class="fas fa-download"></i> تصدير البيانات
            </button>
            <button class="btn btn-danger" onclick="alert('سيتم تطوير هذه الميزة قريباً')">
                <i class="fas fa-trash"></i> حذف مستخدم
            </button>
        </div>
    </div>
    """
    
    return render_template_string(MODERN_BLACK_HTML, title="لوحة التحكم - InvoiceFlow Pro", uptime=uptime_str, content=content)

# ... باقي الـ Routes (invoices, create, stats, health, download) تبقى كما هي مع إضافة @login_required

@app.route('/invoices')
@login_required
def invoices_page():
    """صفحة الفواتير"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    # جلب الفواتير حسب نوع المستخدم
    if session.get('user_type') == 'admin':
        invoices = db_manager.get_all_invoices()
    else:
        invoices = db_manager.get_user_invoices(session.get('username', ''))
    
    invoices_html = ""
    for invoice in invoices:
        services_count = len(invoice['services'])
        has_pdf = invoice.get('pdf_path') and os.path.exists(invoice['pdf_path'])
        pdf_filename = os.path.basename(invoice['pdf_path']) if invoice.get('pdf_path') else ""
        
        invoices_html += f"""
        <div class="invoice-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="color: var(--primary); margin-bottom: 5px;">
                        <i class="fas fa-file-invoice"></i> فاتورة #{invoice['invoice_id']}
                    </h3>
                    <p style="color: var(--text-secondary); margin-bottom: 10px;">
                        <i class="fas fa-user"></i> {invoice['client_name']} 
                        | <i class="fas fa-calendar"></i> {invoice['issue_date']}
                    </p>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 1.5em; font-weight: bold; color: var(--primary);">
                        ${invoice['total_amount']:.2f}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.9em;">
                        {services_count} خدمة
                    </div>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                {'<a href="/download/' + pdf_filename + '" class="btn btn-success" style="padding: 8px 15px;"><i class="fas fa-download"></i> تحميل PDF</a>' if has_pdf else '<span class="btn" style="background: var(--text-muted); padding: 8px 15px;"><i class="fas fa-file-pdf"></i> PDF غير متوفر</span>'}
            </div>
        </div>
        """
    
    content = f"""
    <div class="glass-card">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-file-invoice-dollar"></i> إدارة الفواتير
        </h2>
        <p style="color: var(--text-secondary); text-align: center; margin-bottom: 30px;">
            {'إجمالي الفواتير: ' + str(len(invoices)) + ' فاتورة | إجمالي القيمة: $' + f"{sum(inv['total_amount'] for inv in invoices):,.2f}" if invoices else 'لا توجد فواتير'}
        </p>
    </div>
    
    <div class="invoice-grid">
        {invoices_html if invoices else '''
        <div class="glass-card" style="text-align: center; padding: 50px;">
            <i class="fas fa-file-invoice" style="font-size: 4em; color: var(--text-muted); margin-bottom: 20px;"></i>
            <h3 style="margin-bottom: 15px;">لا توجد فواتير</h3>
            <p style="color: var(--text-secondary); margin-bottom: 25px;">ابدأ بإنشاء فاتورتك الأولى الآن</p>
            <a href="/create" class="btn">
                <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
            </a>
        </div>
        '''}
    </div>
    """
    
    return render_template_string(MODERN_BLACK_HTML, title="إدارة الفواتير - InvoiceFlow Pro", uptime=uptime_str, content=content)

# ... باقي الـ Routes تبقى كما هي مع التعديلات المناسبة

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام المتقدم...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        print("🎨 الواجهة السوداء العالمية مفعلة!")
        print("👑 نظام الصلاحيات المتقدم مفعل!")
        print("🔐 بيانات المدير: admin / AdminMaster2024!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
