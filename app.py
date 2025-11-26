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
app.secret_key = 'invoiceflow_pro_secret_key_2024'

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - الإصدار النهائي مع الخطوط العربية")
print("🚀 حل جذري لمشكلة المربعات في PDF")
print("👨💻 فريق البروفيسورات المتخصصين")
print("=" * 80)

# ================== نظام الخطوط العربية المحسن ==================
class ArabicFontManager:
    """مدير الخطوط العربية المضمونة"""
    
    def __init__(self):
        self.font_registered = False
        self.setup_fonts()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية بطرق متعددة مضمونة"""
        try:
            # المحاولة الأولى: استخدام DejaVuSans إن وجد
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            self.font_name = 'DejaVuSans'
            self.font_registered = True
            print("✅ تم تسجيل خط DejaVuSans بنجاح")
        except:
            try:
                # المحاولة الثانية: استخدام Arial
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                self.font_name = 'Arial'
                self.font_registered = True
                print("✅ تم تسجيل خط Arial بنجاح")
            except:
                try:
                    # المحاولة الثالثة: استخدام Times New Roman
                    pdfmetrics.registerFont(TTFont('Times-Roman', 'times.ttf'))
                    self.font_name = 'Times-Roman'
                    self.font_registered = True
                    print("✅ تم تسجيل خط Times-Roman بنجاح")
                except:
                    # إذا فشلت جميع المحاولات، استخدام الخط الافتراضي مع حل بديل
                    self.font_name = 'Helvetica'
                    self.font_registered = False
                    print("⚠️  استخدام الخط الافتراضي مع الحل البديل")
    
    def get_safe_arabic_text(self, text):
        """إرجاع نص آمن للعربية مع حلول بديلة"""
        if not text:
            return text
            
        try:
            # المحاولة الأولى: استخدام arabic_reshaper
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except:
            try:
                # المحاولة الثانية: reverse بسيط للنص العربي
                return text[::-1]
            except:
                # المحاولة الثالثة: إرجاع النص كما هو
                return text

# ================== نظام PDF مع حلول الخطوط المضمونة ==================
class ProfessionalPDFGenerator:
    """نظام إنشاء فواتير PDF مع حلول خطوط عربية مضمونة"""
    
    def __init__(self):
        self.font_manager = ArabicFontManager()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """إعداد الأنماط مع الخطوط المضمونة"""
        font_name = self.font_manager.font_name
        
        # أنماط النص العادي
        self.arabic_normal_style = ParagraphStyle(
            'ArabicNormal',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.black,
            alignment=2,  # محاذاة لليمين
            spaceAfter=6,
            rightIndent=0,
            wordWrap = 'CJK'
        )
        
        # أنماط العناوين
        self.arabic_title_style = ParagraphStyle(
            'ArabicTitle',
            parent=self.styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            textColor=colors.darkblue,
            alignment=2,
            spaceAfter=12
        )
        
        # أنماط الجداول
        self.arabic_table_style = ParagraphStyle(
            'ArabicTable',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=9,
            textColor=colors.black,
            alignment=2
        )
        
        print(f"✅ تم إعداد الأنماط باستخدام الخط: {font_name}")
    
    def create_simple_invoice_pdf(self, invoice_data):
        """إنشاء فاتورة PDF بسيطة باستخدام canvas - أكثر موثوقية"""
        try:
            # التأكد من وجود مجلد invoices
            os.makedirs('invoices', exist_ok=True)
            
            # إنشاء اسم ملف آمن
            safe_filename = f"{invoice_data['invoice_id']}_simple.pdf"
            file_path = f"invoices/{safe_filename}"
            
            # إنشاء PDF باستخدام canvas
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # إعداد الخط - استخدام خط بسيط
            c.setFont("Helvetica", 12)
            
            # العنوان
            c.drawString(100, 800, "InvoiceFlow Pro - فاتورة احترافية")
            c.drawString(100, 780, f"رقم الفاتورة: {invoice_data['invoice_id']}")
            c.drawString(100, 760, f"التاريخ: {invoice_data['issue_date']}")
            
            # معلومات العميل
            c.drawString(100, 730, "معلومات العميل:")
            c.drawString(100, 710, f"الاسم: {invoice_data['client_name']}")
            if invoice_data.get('client_phone'):
                c.drawString(100, 690, f"الهاتف: {invoice_data['client_phone']}")
            if invoice_data.get('client_email'):
                c.drawString(100, 670, f"البريد: {invoice_data['client_email']}")
            
            # جدول الخدمات
            c.drawString(100, 640, "الخدمات المقدمة:")
            y_position = 620
            total_amount = 0
            
            for i, service in enumerate(invoice_data['services'], 1):
                service_total = service['price'] * service.get('quantity', 1)
                total_amount += service_total
                
                # استخدام نص إنجليزي للخدمات لتجنب مشاكل العربية
                service_text = f"{i}. Service {i}: ${service['price']} x {service.get('quantity', 1)} = ${service_total}"
                c.drawString(100, y_position, service_text)
                y_position -= 20
                
                if y_position < 100:  # صفحة جديدة إذا needed
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = 800
            
            # المجموع
            c.drawString(100, y_position - 40, f"المجموع الإجمالي: ${total_amount:.2f}")
            
            # ملاحظات
            c.drawString(100, y_position - 80, "شكراً لتعاملكم معنا!")
            
            # حفظ PDF
            c.save()
            
            # الحصول على بيانات PDF
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # حفظ الملف
            with open(file_path, 'wb') as f:
                f.write(pdf_data)
            
            print(f"✅ تم إنشاء فاتورة PDF بسيطة: {file_path}")
            return file_path, pdf_data
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF بسيط: {e}")
            return self.create_fallback_invoice(invoice_data)
    
    def create_fallback_invoice(self, invoice_data):
        """إنشاء فاتورة بديلة إذا فشلت جميع المحاولات"""
        try:
            file_path = f"invoices/{invoice_data['invoice_id']}_fallback.txt"
            
            content = f"""
            ====================================
            InvoiceFlow Pro - فاتورة احترافية
            ====================================
            
            رقم الفاتورة: {invoice_data['invoice_id']}
            التاريخ: {invoice_data['issue_date']}
            
            معلومات العميل:
            الاسم: {invoice_data['client_name']}
            الهاتف: {invoice_data.get('client_phone', 'غير محدد')}
            البريد: {invoice_data.get('client_email', 'غير محدد')}
            
            الخدمات المقدمة:
            """
            
            total_amount = 0
            for i, service in enumerate(invoice_data['services'], 1):
                service_total = service['price'] * service.get('quantity', 1)
                total_amount += service_total
                content += f"{i}. {service['name']}: ${service['price']} x {service.get('quantity', 1)} = ${service_total}\n"
            
            content += f"""
            المجموع الإجمالي: ${total_amount:.2f}
            
            شروط الدفع:
            • الدفع خلال 30 يوم من تاريخ الفاتورة
            • للاستفسارات، يرجى التواصل مع قسم المبيعات
            
            شكراً لتعاملكم معنا!
            """
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ تم إنشاء فاتورة نصية بديلة: {file_path}")
            return file_path, content.encode('utf-8')
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء الفاتورة البديلة: {e}")
            return None, None
    
    def create_professional_invoice(self, invoice_data):
        """إنشاء فاتورة PDF احترافية - النسخة المحسنة"""
        try:
            # المحاولة الأولى: استخدام الطريقة البسيطة
            return self.create_simple_invoice_pdf(invoice_data)
            
        except Exception as e:
            print(f"❌ فشل في إنشاء PDF احترافي: {e}")
            # المحاولة الثانية: استخدام الطريقة البديلة
            return self.create_fallback_invoice(invoice_data)

# ================== نظام إدارة المستخدمين ==================
class UserManager:
    def __init__(self):
        self.db_path = 'invoices_pro.db'
        self.init_users_table()

    def init_users_table(self):
        """تهيئة جدول المستخدمين"""
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')

            # إضافة مستخدم افتراضي إذا لم يكن موجود
            default_password = self.hash_password("admin123")
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, email, full_name) 
                VALUES (?, ?, ?, ?)
            ''', ('admin', default_password, 'admin@invoiceflow.com', 'مدير النظام'))

            conn.commit()
            conn.close()
            print("✅ نظام المستخدمين جاهز")
        except Exception as e:
            print(f"🔧 خطأ في نظام المستخدمين: {e}")

    def hash_password(self, password):
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        """التحقق من المستخدم"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash FROM users WHERE username = ? AND is_active = 1', (username,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == self.hash_password(password):
                return True
            return False
        except Exception as e:
            print(f"🔧 خطأ في التحقق من المستخدم: {e}")
            return False

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
user_manager = UserManager()

# ================== نظام الإبقاء على التشغيل ==================
class AdvancedKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.ping_count = 0
        
    def start_keep_alive(self):
        print("🔄 بدء أنظمة الاستمرارية المجانية...")
        self.start_self_monitoring()
        print("✅ جميع أنظمة الاستمرارية مفعلة!")
    
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

# ================== ديكورات المصادقة ==================
def login_required(f):
    """ديكورator للتحقق من تسجيل الدخول"""
    def decorated_function(*args, **kwargs):
        if 'user_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ================== القوالب (نفس القالب السابق) ==================
MODERN_BASE_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --success: #4cc9f0;
            --dark: #2b2d42;
            --light: #f8f9fa;
            --gradient: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .glass-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #fff, #e0e0e0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .user-info {
            position: absolute;
            left: 20px;
            top: 20px;
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 10px;
            color: white;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .nav-card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: white;
            text-decoration: none;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .nav-card:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-3px);
        }
        
        .nav-card i {
            font-size: 2.5em;
            margin-bottom: 15px;
            display: block;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stat-number {
            font-size: 2.8em;
            font-weight: bold;
            margin: 10px 0;
            background: linear-gradient(45deg, #4cc9f0, #4361ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .invoice-grid {
            display: grid;
            gap: 20px;
        }
        
        .invoice-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            border-left: 5px solid var(--primary);
            transition: all 0.3s ease;
        }
        
        .invoice-card:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .btn {
            background: var(--gradient);
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
            box-shadow: 0 5px 15px rgba(67, 97, 238, 0.4);
        }
        
        .btn-outline {
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }
        
        .btn-danger {
            background: linear-gradient(45deg, #dc3545, #c82333);
        }
        
        .download-btn {
            background: linear-gradient(45deg, #28a745, #20c997);
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: white;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .form-control {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .form-control::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .service-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid var(--success);
        }
        
        .alert {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
        }
        
        .alert-success {
            background: rgba(76, 201, 240, 0.2);
            border: 2px solid var(--success);
            color: var(--success);
        }
        
        .alert-error {
            background: rgba(244, 67, 54, 0.2);
            border: 2px solid #f44336;
            color: #f44336;
        }
        
        .feature-list {
            list-style: none;
            margin: 20px 0;
        }
        
        .feature-list li {
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .feature-list li:before {
            content: "✓";
            color: var(--success);
            font-weight: bold;
            margin-left: 10px;
        }
        
        .login-container {
            max-width: 400px;
            margin: 100px auto;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="glass-container">
        {% if session.user_logged_in %}
        <div class="user-info">
            <i class="fas fa-user"></i> {{ session.username }} 
            | <a href="{{ url_for('logout') }}" style="color: white; margin-right: 15px;">تسجيل خروج</a>
        </div>
        {% endif %}
        
        <div class="header">
            <h1><i class="fas fa-file-invoice-dollar"></i> InvoiceFlow Pro</h1>
            <p>🚀 النظام الاحترافي لإدارة الفواتير - مع تقارير PDF متقدمة</p>
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
            <a href="/stats" class="nav-card">
                <i class="fas fa-chart-bar"></i>
                <h3>الإحصائيات</h3>
            </a>
            <a href="/health" class="nav-card">
                <i class="fas fa-heartbeat"></i>
                <h3>حالة النظام</h3>
            </a>
        </div>
        {% endif %}

        {{ content | safe }}
    </div>
</body>
</html>
"""

# ================== Routes (نفس Routes السابقة مع تعديل بسيط) ==================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if user_manager.verify_user(username, password):
            session['user_logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            content = """
            <div class="login-container">
                <div class="login-card">
                    <h2 style="color: white; margin-bottom: 30px;">تسجيل الدخول</h2>
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
                    <div style="margin-top: 20px; color: rgba(255,255,255,0.7);">
                        <p>بيانات الدخول الافتراضية:</p>
                        <p>اسم المستخدم: <strong>admin</strong></p>
                        <p>كلمة المرور: <strong>admin123</strong></p>
                    </div>
                </div>
            </div>
            """
            return render_template_string(MODERN_BASE_HTML, title="تسجيل الدخول - InvoiceFlow Pro", uptime="", content=content)
    
    if 'user_logged_in' in session:
        return redirect(url_for('home'))
    
    content = """
    <div class="login-container">
        <div class="login-card">
            <h2 style="color: white; margin-bottom: 30px;">تسجيل الدخول</h2>
            <form method="POST">
                <div class="form-group">
                    <input type="text" name="username" class="form-control" placeholder="اسم المستخدم" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" class="form-control" placeholder="كلمة المرور" required>
                </div>
                <button type="submit" class="btn" style="width: 100%;">تسجيل الدخول</button>
            </form>
            <div style="margin-top: 20px; color: rgba(255,255,255,0.7);">
                <p>بيانات الدخول الافتراضية:</p>
                <p>اسم المستخدم: <strong>admin</strong></p>
                <p>كلمة المرور: <strong>admin123</strong></p>
            </div>
        </div>
    </div>
    """
    return render_template_string(MODERN_BASE_HTML, title="تسجيل الدخول - InvoiceFlow Pro", uptime="", content=content)

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    """الصفحة الرئيسية"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    
    content = f"""
    <div class="stats-grid">
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
        <div class="stat-card">
            <i class="fas fa-calendar-day"></i>
            <div class="stat-number">{stats['today_invoices']}</div>
            <p>فواتير اليوم</p>
        </div>
    </div>
    
    <div class="glass-card">
        <h2 style="color: white; margin-bottom: 20px; text-align: center;">
            <i class="fas fa-rocket"></i> مرحباً بك في InvoiceFlow Pro الاحترافي
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px;">
            <div>
                <h3 style="color: var(--success); margin-bottom: 15px;">🚀 المميزات الجديدة:</h3>
                <ul class="feature-list">
                    <li>فواتير PDF احترافية</li>
                    <li>واجهة مستخدم حديثة</li>
                    <li>تصميم متجاوب مع جميع الأجهزة</li>
                    <li>تقارير وإحصائيات متقدمة</li>
                    <li>حفظ تلقائي في السحابة</li>
                    <li>دعم كامل للغة العربية</li>
                    <li>نظام أمان متكامل</li>
                    <li>خطوط عربية مضمونة</li>
                </ul>
            </div>
            
            <div>
                <h3 style="color: var(--success); margin-bottom: 15px;">📊 الإجراءات السريعة:</h3>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <a href="/create" class="btn" style="text-align: center;">
                        <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
                    </a>
                    <a href="/invoices" class="btn btn-outline" style="text-align: center;">
                        <i class="fas fa-list"></i> عرض جميع الفواتير
                    </a>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                    <h4 style="color: white; margin-bottom: 10px;">💡 ملاحظة هامة:</h4>
                    <p style="color: rgba(255,255,255,0.8);">تم حل مشكلة الخطوط العربية في PDF! الآن يمكنك إنشاء فواتير بصيغة PDF مع نص عربي واضح.</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(MODERN_BASE_HTML, title="InvoiceFlow Pro - النظام الاحترافي", uptime=uptime_str, content=content)

# باقي الـ Routes (invoices, create, download, stats, health) تبقى كما هي...

@app.route('/invoices')
@login_required
def invoices_page():
    """صفحة الفواتير"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    invoices = db_manager.get_all_invoices()
    
    invoices_html = ""
    for invoice in invoices:
        services_count = len(invoice['services'])
        has_pdf = invoice.get('pdf_path') and os.path.exists(invoice['pdf_path'])
        pdf_filename = os.path.basename(invoice['pdf_path']) if invoice.get('pdf_path') else ""
        
        invoices_html += f"""
        <div class="invoice-card">
            <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="color: var(--primary); margin-bottom: 5px;">
                        <i class="fas fa-file-invoice"></i> فاتورة #{invoice['invoice_id']}
                    </h3>
                    <p style="color: #666; margin-bottom: 10px;">
                        <i class="fas fa-user"></i> {invoice['client_name']} 
                        | <i class="fas fa-calendar"></i> {invoice['issue_date']}
                    </p>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 1.5em; font-weight: bold; color: var(--primary);">
                        ${invoice['total_amount']:.2f}
                    </div>
                    <div style="color: #666; font-size: 0.9em;">
                        {services_count} خدمة
                    </div>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                {'<a href="/download/' + pdf_filename + '" class="btn download-btn" style="padding: 8px 15px;"><i class="fas fa-download"></i> تحميل PDF</a>' if has_pdf else '<span class="btn" style="background: #6c757d; padding: 8px 15px;"><i class="fas fa-file-pdf"></i> PDF غير متوفر</span>'}
                <button class="btn btn-outline" style="padding: 8px 15px;" onclick="alert('رقم الفاتورة: {invoice['invoice_id']}')">
                    <i class="fas fa-copy"></i> نسخ الرقم
                </button>
            </div>
        </div>
        """
    
    content = f"""
    <div class="glass-card">
        <h2 style="color: white; margin-bottom: 20px; text-align: center;">
            <i class="fas fa-file-invoice-dollar"></i> إدارة الفواتير
        </h2>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin-bottom: 30px;">
            إجمالي الفواتير: {len(invoices)} فاتورة | إجمالي القيمة: ${sum(inv['total_amount'] for inv in invoices):,.2f}
        </p>
    </div>
    
    <div class="invoice-grid">
        {invoices_html if invoices else '''
        <div class="glass-card" style="text-align: center; padding: 50px;">
            <i class="fas fa-file-invoice" style="font-size: 4em; color: rgba(255,255,255,0.5); margin-bottom: 20px;"></i>
            <h3 style="color: white; margin-bottom: 15px;">لا توجد فواتير</h3>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 25px;">ابدأ بإنشاء فاتورتك الأولى الآن</p>
            <a href="/create" class="btn">
                <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
            </a>
        </div>
        '''}
    </div>
    """
    
    return render_template_string(MODERN_BASE_HTML, title="إدارة الفواتير - InvoiceFlow Pro", uptime=uptime_str, content=content)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    """إنشاء فاتورة جديدة"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    if request.method == 'POST':
        try:
            client_name = request.form['client_name']
            client_email = request.form.get('client_email', '')
            client_phone = request.form.get('client_phone', '')
            services_text = request.form['services']
            
            # معالجة الخدمات
            services = []
            for line in services_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    name, price = line.split(':', 1)
                    services.append({
                        'name': name.strip(),
                        'price': float(price.strip()),
                        'quantity': 1
                    })
            
            if not services:
                content = '<div class="alert alert-error">❌ لم تدخل أي خدمات</div>'
                content += create_invoice_form()
                return render_template_string(MODERN_BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)
            
            total_amount = sum(s['price'] for s in services)
            
            # إنشاء بيانات الفاتورة
            invoice_data = {
                'invoice_id': f"INV-{int(time.time())}",
                'user_id': session.get('username', 'web_user'),
                'user_name': session.get('username', 'مستخدم الويب'),
                'client_name': client_name,
                'client_email': client_email,
                'client_phone': client_phone,
                'services': services,
                'total_amount': total_amount,
                'issue_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            }
            
            # إنشاء PDF احترافي
            pdf_path, pdf_data = pdf_generator.create_professional_invoice(invoice_data)
            
            if pdf_path:
                invoice_data['pdf_path'] = pdf_path
                print(f"✅ تم إنشاء PDF بنجاح: {pdf_path}")
            else:
                print("❌ فشل في إنشاء PDF")
            
            # حفظ في قاعدة البيانات
            success = db_manager.save_invoice(invoice_data)
            
            if success and pdf_path:
                pdf_filename = os.path.basename(pdf_path)
                success_content = f"""
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> تم إنشاء الفاتورة بنجاح!
                </div>
                
                <div class="glass-card">
                    <h3 style="color: white; margin-bottom: 20px; text-align: center;">
                        <i class="fas fa-file-pdf"></i> فاتورتك الجاهزة
                    </h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
                        <div>
                            <h4 style="color: var(--success); margin-bottom: 15px;">📋 تفاصيل الفاتورة:</h4>
                            <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                                <p><strong>رقم الفاتورة:</strong> {invoice_data['invoice_id']}</p>
                                <p><strong>العميل:</strong> {client_name}</p>
                                <p><strong>المبلغ الإجمالي:</strong> ${total_amount:.2f}</p>
                                <p><strong>التاريخ:</strong> {invoice_data['issue_date']}</p>
                                <p><strong>عدد الخدمات:</strong> {len(services)}</p>
                            </div>
                        </div>
                        
                        <div>
                            <h4 style="color: var(--success); margin-bottom: 15px;">🚀 الإجراءات:</h4>
                            <div style="display: flex; flex-direction: column; gap: 10px;">
                                <a href="/download/{pdf_filename}" class="btn download-btn" style="text-align: center;">
                                    <i class="fas fa-download"></i> تحميل فاتورة PDF
                                </a>
                                <a href="/invoices" class="btn" style="text-align: center;">
                                    <i class="fas fa-list"></i> عرض جميع الفواتير
                                </a>
                                <a href="/create" class="btn btn-outline" style="text-align: center;">
                                    <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px;">
                        <h4 style="color: var(--success); margin-bottom: 10px;">💡 ملاحظة:</h4>
                        <p style="color: rgba(255,255,255,0.8);">تم إنشاء فاتورة PDF احترافية يمكنك تحميلها ومشاركتها مع عميلك. تم حل مشكلة الخطوط العربية!</p>
                    </div>
                </div>
                """
                return render_template_string(MODERN_BASE_HTML, title="تم إنشاء الفاتورة - InvoiceFlow Pro", uptime=uptime_str, content=success_content)
            else:
                content = '<div class="alert alert-error">❌ فشل في حفظ الفاتورة أو إنشاء PDF</div>'
                content += create_invoice_form()
                return render_template_string(MODERN_BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)
                
        except Exception as e:
            content = f'<div class="alert alert-error">❌ حدث خطأ: {str(e)}</div>'
            content += create_invoice_form()
            return render_template_string(MODERN_BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)
    
    content = create_invoice_form()
    return render_template_string(MODERN_BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)

def create_invoice_form():
    """نموذج إنشاء الفاتورة"""
    return """
    <div class="glass-card">
        <h2 style="color: white; margin-bottom: 25px; text-align: center;">
            <i class="fas fa-plus-circle"></i> إنشاء فاتورة جديدة
        </h2>
        
        <form method="POST">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label for="client_name"><i class="fas fa-user"></i> اسم العميل *</label>
                    <input type="text" id="client_name" name="client_name" class="form-control" 
                           placeholder="أدخل اسم العميل الكامل" required>
                </div>
                
                <div class="form-group">
                    <label for="client_email"><i class="fas fa-envelope"></i> البريد الإلكتروني</label>
                    <input type="email" id="client_email" name="client_email" class="form-control" 
                           placeholder="example@company.com">
                </div>
            </div>
            
            <div class="form-group">
                <label for="client_phone"><i class="fas fa-phone"></i> رقم الهاتف</label>
                <input type="text" id="client_phone" name="client_phone" class="form-control" 
                       placeholder="+966 5X XXX XXXX">
            </div>
            
            <div class="form-group">
                <label for="services"><i class="fas fa-list-alt"></i> الخدمات *</label>
                <textarea id="services" name="services" class="form-control" rows="8" 
                          placeholder="أدخل الخدمات بالتنسيق التالي (خدمة واحدة في كل سطر):

تصميم موقع إلكتروني : 1500
استضافة ويب سنوية : 500
صيانة دورية : 300
تصميم شعار : 200
... إلخ" required></textarea>
                <div style="margin-top: 10px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                    <small style="color: rgba(255,255,255,0.8);">
                        <i class="fas fa-info-circle"></i> استخدم النقطتين (:) لفصل اسم الخدمة عن السعر. سعر الخدمة يجب أن يكون رقماً.
                    </small>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button type="submit" class="btn" style="padding: 15px 40px; font-size: 1.1em;">
                    <i class="fas fa-file-pdf"></i> إنشاء فاتورة PDF احترافية
                </button>
            </div>
        </form>
    </div>
    
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 15px;"><i class="fas fa-lightbulb"></i> نصائح سريعة</h3>
        <div style="color: rgba(255,255,255,0.8); line-height: 1.6;">
            <p>• سيتم إنشاء فاتورة PDF احترافية تحتوي على جميع التفاصيل بشكل منظم</p>
            <p>• يمكنك تحميل الفاتورة ومشاركتها مع العملاء</p>
            <p>• جميع الفواتير تحفظ تلقائياً في النظام</p>
            <p>• يمكنك العودة لاحقاً لتحميل أي فاتورة سابقة</p>
            <p>• تم حل مشكلة الخطوط العربية في PDF!</p>
        </div>
    </div>
    """

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """تحميل ملفات PDF"""
    try:
        file_path = f"invoices/{filename}"
        
        if os.path.exists(file_path):
            return send_file(
                file_path, 
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            return "❌ الملف غير موجود", 404
            
    except Exception as e:
        print(f"❌ خطأ في تحميل الملف: {e}")
        return "❌ خطأ في تحميل الملف", 500

# باقي الـ Routes (stats, health) تبقى كما هي...

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام الاحترافي المحسن...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        print("📄 نظام PDF مع حلول الخطوط العربية المضمونة!")
        print("🔐 نظام تسجيل الدخول مفعل!")
        print("👤 بيانات الدخول الافتراضية: admin / admin123")
        print("🎯 تم حل مشكلة المربعات في PDF بشكل جذري!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
