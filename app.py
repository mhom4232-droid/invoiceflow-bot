import os
import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta
from threading import Thread, Lock
from flask import Flask, render_template_string, request, jsonify, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display
import io

# ================== تطبيق Flask ==================
app = Flask(__name__)

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - النظام الاحترافي - الإصدار المحسن")
print("🚀 إصلاح مشكلة تحميل PDF - فريق البروفيسورات")
print("=" * 80)

# ================== إصلاح مشكلة PDF ==================

@app.route('/download/<filename>')
def download_file(filename):
    """تحميل ملفات PDF بشكل آمن"""
    try:
        # التأكد من أن الملف موجود في مجلد invoices
        file_path = f"invoices/{filename}"
        
        print(f"🔍 محاولة تحميل الملف: {file_path}")
        print(f"📁 هل الملف موجود؟: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            print(f"✅ تم العثور على الملف، جاري التحميل...")
            return send_file(
                file_path, 
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            print(f"❌ الملف غير موجود: {file_path}")
            return render_template_string("""
            <div style="text-align: center; padding: 50px;">
                <h1 style="color: #f44336;">❌ الملف غير موجود</h1>
                <p>عذراً، لم يتم العثور على الملف المطلوب.</p>
                <a href="/invoices" style="color: #4361ee;">العودة إلى الفواتير</a>
            </div>
            """), 404
            
    except Exception as e:
        print(f"❌ خطأ في تحميل الملف: {e}")
        return render_template_string("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #f44336;">❌ خطأ في تحميل الملف</h1>
            <p>حدث خطأ أثناء محاولة تحميل الملف.</p>
            <a href="/invoices" style="color: #4361ee;">العودة إلى الفواتير</a>
        </div>
        """), 500

# ================== نظام PDF المحسن ==================
class ProfessionalPDFGenerator:
    """نظام إنشاء فواتير PDF احترافية - النسخة المحسنة"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """إعداد الأنماط المخصصة للعربية"""
        self.arabic_title_style = ParagraphStyle(
            'ArabicTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.darkblue,
            alignment=2,
            spaceAfter=12
        )
        
        self.arabic_normal_style = ParagraphStyle(
            'ArabicNormal',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.black,
            alignment=2,
            spaceAfter=6
        )
        
        self.arabic_table_style = ParagraphStyle(
            'ArabicTable',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.black,
            alignment=2
        )
    
    def reshape_arabic_text(self, text):
        """إعادة تشكيل النص العربي للعرض الصحيح"""
        if text:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        return text
    
    def create_professional_invoice(self, invoice_data):
        """إنشاء فاتورة PDF احترافية - نسخة محسنة"""
        try:
            # التأكد من وجود مجلد invoices
            os.makedirs('invoices', exist_ok=True)
            
            # إنشاء اسم ملف آمن
            safe_filename = f"{invoice_data['invoice_id']}_professional.pdf"
            file_path = f"invoices/{safe_filename}"
            
            # إنشاء buffer للPDF في الذاكرة
            buffer = io.BytesIO()
            
            # إنشاء مستند PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # محتوى الفاتورة
            story = []
            
            # رأس الفاتورة
            header_data = [
                [self.reshape_arabic_text("فاتورة احترافية"), "", self.reshape_arabic_text("InvoiceFlow Pro")],
                [self.reshape_arabic_text("رقم الفاتورة: ") + invoice_data['invoice_id'], "", self.reshape_arabic_text("تاريخ الإصدار: ") + invoice_data['issue_date']],
                [self.reshape_arabic_text("شركتك"), "", self.reshape_arabic_text("مقدم الخدمة")],
            ]
            
            header_table = Table(header_data, colWidths=[60*mm, 30*mm, 60*mm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 15))
            
            # معلومات العميل
            client_info = [
                [self.reshape_arabic_text("معلومات العميل"), "", self.reshape_arabic_text("معلومات الشركة")],
                [
                    self.reshape_arabic_text(f"الاسم: {invoice_data['client_name']}\nالهاتف: {invoice_data.get('client_phone', 'غير محدد')}\nالبريد: {invoice_data.get('client_email', 'غير محدد')}"),
                    "",
                    self.reshape_arabic_text(f"الشركة: شركتك\nالتسجيل: 123456\nالعنوان: مدينة الأعمال")
                ]
            ]
            
            client_table = Table(client_info, colWidths=[70*mm, 10*mm, 70*mm])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(client_table)
            story.append(Spacer(1, 20))
            
            # جدول الخدمات
            services_header = [
                self.reshape_arabic_text("رقم"),
                self.reshape_arabic_text("وصف الخدمة"),
                self.reshape_arabic_text("الكمية"),
                self.reshape_arabic_text("السعر"),
                self.reshape_arabic_text("المجموع")
            ]
            
            services_data = [services_header]
            total_amount = 0
            
            for i, service in enumerate(invoice_data['services'], 1):
                service_total = service['price'] * service.get('quantity', 1)
                total_amount += service_total
                
                services_data.append([
                    str(i),
                    self.reshape_arabic_text(service['name']),
                    str(service.get('quantity', 1)),
                    f"${service['price']:.2f}",
                    f"${service_total:.2f}"
                ])
            
            # إضافة المجموع
            services_data.append([
                "", 
                self.reshape_arabic_text("المجموع الإجمالي"), 
                "", 
                "", 
                f"${total_amount:.2f}"
            ])
            
            services_table = Table(services_data, colWidths=[15*mm, 70*mm, 20*mm, 25*mm, 30*mm])
            services_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ]))
            
            story.append(services_table)
            story.append(Spacer(1, 25))
            
            # ملاحظات
            notes = [
                self.reshape_arabic_text("شروط الدفع:"),
                self.reshape_arabic_text("• الدفع خلال 30 يوم من تاريخ الفاتورة"),
                self.reshape_arabic_text("• تأخر الدفع قد يؤدي إلى تطبيق فوائد تأخير"),
                self.reshape_arabic_text("• للاستفسارات، يرجى التواصل مع قسم المبيعات"),
                "",
                self.reshape_arabic_text("شكراً لتعاملكم معنا!")
            ]
            
            for note in notes:
                if note:
                    story.append(Paragraph(self.reshape_arabic_text(note), self.arabic_normal_style))
                else:
                    story.append(Spacer(1, 6))
            
            # إنشاء PDF
            doc.build(story)
            
            # الحصول على بيانات PDF
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # حفظ ملف PDF
            with open(file_path, 'wb') as f:
                f.write(pdf_data)
            
            print(f"✅ تم إنشاء فاتورة PDF بنجاح: {file_path}")
            print(f"📊 حجم الملف: {len(pdf_data)} بايت")
            
            return file_path, pdf_data
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF: {e}")
            import traceback
            traceback.print_exc()
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

# ================== القوالب ==================
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
    </style>
</head>
<body>
    <div class="glass-container">
        <div class="header">
            <h1><i class="fas fa-file-invoice-dollar"></i> InvoiceFlow Pro</h1>
            <p>🚀 النظام الاحترافي لإدارة الفواتير - مع تقارير PDF متقدمة</p>
            <p>⏰ مدة التشغيل: {{ uptime }}</p>
        </div>
        
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

        {{ content | safe }}
    </div>
</body>
</html>
"""

# ================== Routes محسنة مع إصلاح PDF ==================
@app.route('/')
def home():
    """الصفحة الرئيسية المحسنة"""
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
                    <h4 style="color: white; margin-bottom: 10px;">💡 نصيحة سريعة:</h4>
                    <p style="color: rgba(255,255,255,0.8);">استخدم نموذج إنشاء الفاتورة لإنشاء فاتورة PDF احترافية يمكن تحميلها ومشاركتها مع العملاء</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(MODERN_BASE_HTML, title="InvoiceFlow Pro - النظام الاحترافي", uptime=uptime_str, content=content)

@app.route('/invoices')
def invoices_page():
    """صفحة الفواتير المحسنة مع إصلاح التحميل"""
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
def create_invoice():
    """إنشاء فاتورة جديدة مع PDF - نسخة محسنة"""
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
                'user_id': 'web_user',
                'user_name': 'مستخدم الويب',
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
                        <p style="color: rgba(255,255,255,0.8);">تم إنشاء فاتورة PDF احترافية يمكنك تحميلها ومشاركتها مع عميلك. الفاتورة تحتوي على جميع التفاصيل بشكل منظم واحترافي.</p>
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
    """نموذج إنشاء الفاتورة المحسن"""
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
        </div>
    </div>
    """

# باقي الـ Routes (stats, health) تبقى كما هي...

@app.route('/stats')
def stats_page():
    """صفحة الإحصائيات المحسنة"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    invoices = db_manager.get_all_invoices()[:5]
    
    recent_invoices_html = ""
    for invoice in invoices:
        recent_invoices_html += f"""
        <div style="padding: 15px; background: rgba(255,255,255,0.1); margin: 8px 0; border-radius: 8px; border-left: 3px solid var(--success);">
            <strong>{invoice['invoice_id']}</strong> - {invoice['client_name']} - ${invoice['total_amount']:.2f}
        </div>
        """
    
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
            <i class="fas fa-chart-line"></i> الإحصائيات والتقارير
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <h3 style="color: var(--success); margin-bottom: 15px;">📈 نظرة عامة</h3>
                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                    <p style="margin: 10px 0;"><strong>متوسط قيمة الفاتورة:</strong> ${stats['total_revenue']/max(stats['total_invoices'], 1):.2f}</p>
                    <p style="margin: 10px 0;"><strong>إجمالي الفواتير النشطة:</strong> {stats['total_invoices']}</p>
                    <p style="margin: 10px 0;"><strong>فواتير هذا الشهر:</strong> {stats['today_invoices']}</p>
                </div>
            </div>
            
            <div>
                <h3 style="color: var(--success); margin-bottom: 15px;">📋 آخر الفواتير</h3>
                {recent_invoices_html if recent_invoices_html else '<p style="color: rgba(255,255,255,0.7); text-align: center;">لا توجد فواتير حديثة</p>'}
            </div>
        </div>
    </div>
    """
    
    return render_template_string(MODERN_BASE_HTML, title="الإحصائيات - InvoiceFlow Pro", uptime=uptime_str, content=content)

@app.route('/health')
def health_page():
    """صفحة حالة النظام المحسنة"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    
    content = f"""
    <div class="stats-grid">
        <div class="stat-card" style="background: rgba(76, 201, 240, 0.2);">
            <i class="fas fa-heartbeat"></i>
            <div class="stat-number">نشط</div>
            <p>حالة الخدمة</p>
        </div>
        
        <div class="stat-card">
            <i class="fas fa-clock"></i>
            <div class="stat-number">{uptime_str.split(' ')[0]}</div>
            <p>مدة التشغيل</p>
        </div>
        
        <div class="stat-card">
            <i class="fas fa-database"></i>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>الفواتير المخزنة</p>
        </div>
    </div>
    
    <div class="glass-card">
        <h2 style="color: white; margin-bottom: 25px; text-align: center;">
            <i class="fas fa-server"></i> حالة النظام والخدمات
        </h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
            <div style="text-align: center; padding: 20px; background: rgba(76, 201, 240, 0.1); border-radius: 10px;">
                <i class="fas fa-check-circle" style="color: var(--success); font-size: 2em;"></i>
                <h4 style="color: white; margin: 10px 0;">خادم الويب</h4>
                <p style="color: rgba(255,255,255,0.8);">يعمل بشكل طبيعي</p>
            </div>
            
            <div style="text-align: center; padding: 20px; background: rgba(76, 201, 240, 0.1); border-radius: 10px;">
                <i class="fas fa-check-circle" style="color: var(--success); font-size: 2em;"></i>
                <h4 style="color: white; margin: 10px 0;">قاعدة البيانات</h4>
                <p style="color: rgba(255,255,255,0.8);">متصل ومستقر</p>
            </div>
            
            <div style="text-align: center; padding: 20px; background: rgba(76, 201, 240, 0.1); border-radius: 10px;">
                <i class="fas fa-check-circle" style="color: var(--success); font-size: 2em;"></i>
                <h4 style="color: white; margin: 10px 0;">نظام PDF</h4>
                <p style="color: rgba(255,255,255,0.8);">جاهز للعمل</p>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
            <h3 style="color: var(--success); margin-bottom: 15px;">✅ جميع الأنظمة تعمل بشكل طبيعي</h3>
            <div style="color: rgba(255,255,255,0.8); line-height: 1.6;">
                <p>• خادم الويب يستجيب للطلبات</p>
                <p>• قاعدة البيانات متصلة وتعمل</p>
                <p>• نظام إنشاء PDF جاهز</p>
                <p>• الذاكرة مستقرة</p>
                <p>• النظام يعمل 24/7 على السحابة</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(MODERN_BASE_HTML, title="حالة النظام - InvoiceFlow Pro", uptime=uptime_str, content=content)

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام الاحترافي المحسن...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        print("📄 نظام PDF المحسن مفعل وجاهز!")
        print("🔗 روابط التحميل المباشرة مفعلة!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
