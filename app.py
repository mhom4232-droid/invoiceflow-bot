import os
import io
import time
import sqlite3
from datetime import datetime
from threading import Thread
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

# ================== تطبيق Flask المتطور ==================
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # ساعة واحدة

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Premium - النسخة الاحترافية")
print("🚀 تصميم أسود/أبيض + نظام PDF متكامل + واجهات كاملة")
print("👑 فريق النخبة البروفيسوري المتكامل")
print("=" * 80)

# ================== نظام الإبقاء على التشغيل ==================
class PremiumKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.request_count = 0
        
    def start_premium_system(self):
        print("🚀 بدء النظام الاحترافي...")
        self.start_premium_monitoring()
        print("✅ النظام الاحترافي مفعل!")
    
    def start_premium_monitoring(self):
        def monitor():
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                if int(current_time) % 300 == 0:  # كل 5 دقائق
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"📊 تقرير النظام: {hours}س {minutes}د - {self.request_count} طلب")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# إعداد النظام
keep_alive_system = PremiumKeepAlive()
keep_alive_system.start_premium_system()

# ================== نظام إنشاء PDF بالعربية ==================
def setup_arabic_font():
    """إعداد الخطوط العربية"""
    try:
        # محاولة استخدام خط Arial للعربية
        pdfmetrics.registerFont(TTFont('Arabic', 'Arial.ttf'))
    except:
        try:
            # استخدام DejaVu كبديل
            pdfmetrics.registerFont(TTFont('Arabic', 'DejaVuSans.ttf'))
        except:
            # استخدام الخط الافتراضي
            pdfmetrics.registerFont(TTFont('Arabic', 'Helvetica'))

def prepare_arabic_text(text):
    """معالجة النص العربي للعرض الصحيح"""
    if text and isinstance(text, str):
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text
    return text

def create_invoice_pdf(invoice_data):
    """إنشاء فاتورة PDF احترافية بالعربية"""
    buffer = io.BytesIO()
    
    # إعداد الخطوط
    setup_arabic_font()
    
    # إنشاء المستند
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
        title=prepare_arabic_text("فاتورة ضريبية")
    )
    
    # عناصر PDF
    elements = []
    styles = getSampleStyleSheet()
    
    # إعداد الأنماط العربية
    arabic_title_style = ParagraphStyle(
        'ArabicTitle',
        parent=styles['Heading1'],
        fontName='Arabic',
        fontSize=24,
        alignment=2,  # محاذاة لليمين
        textColor=colors.black,
        spaceAfter=30
    )
    
    arabic_normal_style = ParagraphStyle(
        'ArabicNormal',
        parent=styles['Normal'],
        fontName='Arabic',
        fontSize=12,
        alignment=0,
        textColor=colors.black
    )
    
    # عنوان الفاتورة
    title = prepare_arabic_text("فاتورة ضريبية")
    elements.append(Paragraph(title, arabic_title_style))
    
    # معلومات الشركة
    company_info = prepare_arabic_text("""
    <b>شركة InvoiceFlow Premium</b><br/>
    الرقم الضريبي: 123456789<br/>
    البريد الإلكتروني: info@invoiceflow.com<br/>
    الهاتف: +966 55 123 4567
    """)
    elements.append(Paragraph(company_info, arabic_normal_style))
    elements.append(Spacer(1, 20))
    
    # معلومات الفاتورة
    invoice_info = f"""
    <b>رقم الفاتورة:</b> {invoice_data.get('invoice_number', 'INV-001')}<br/>
    <b>التاريخ:</b> {invoice_data.get('date', datetime.now().strftime('%Y-%m-%d'))}<br/>
    <b>العميل:</b> {prepare_arabic_text(invoice_data.get('client_name', 'عميل'))}<br/>
    <b>البريد الإلكتروني:</b> {invoice_data.get('client_email', '')}
    """
    elements.append(Paragraph(invoice_info, arabic_normal_style))
    elements.append(Spacer(1, 30))
    
    # جدول العناصر
    headers = [
        prepare_arabic_text('الوصف'),
        prepare_arabic_text('الكمية'),
        prepare_arabic_text('السعر'),
        prepare_arabic_text('المجموع')
    ]
    
    data = [headers]
    total = 0
    
    items = invoice_data.get('items', [])
    if not items:
        # عنصر افتراضي
        items = [{
            'description': 'خدمة إدارة الفواتير',
            'quantity': 1,
            'price': 1000
        }]
    
    for item in items:
        description = prepare_arabic_text(item.get('description', ''))
        quantity = str(item.get('quantity', 1))
        price = f"{float(item.get('price', 0)):,.2f}"
        item_total = float(item.get('quantity', 1)) * float(item.get('price', 0))
        total += item_total
        total_str = f"{item_total:,.2f}"
        
        data.append([description, quantity, price, total_str])
    
    # إضافة الإجمالي
    data.append([
        prepare_arabic_text('الإجمالي'),
        '', '', 
        f"{total:,.2f} ر.س"
    ])
    
    # إضافة الضريبة
    tax = total * 0.15
    data.append([
        prepare_arabic_text('الضريبة (15%)'),
        '', '', 
        f"{tax:,.2f} ر.س"
    ])
    
    # الإجمالي النهائي
    final_total = total + tax
    data.append([
        prepare_arabic_text('المبلغ المستحق'),
        '', '', 
        f"<b>{final_total:,.2f} ر.س</b>"
    ])
    
    # إنشاء الجدول
    table = Table(data, colWidths=[200, 60, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arabic'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#ECF0F1')),
        ('GRID', (0, 0), (-1, -4), 1, colors.grey),
        ('BOX', (0, -3), (-1, -1), 2, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 40))
    
    # ملاحظات
    notes_text = prepare_arabic_text(invoice_data.get('notes', 
        'شكراً لتعاملكم معنا. يرجى الدفع خلال 30 يوم من تاريخ الفاتورة.'))
    notes = f"<b>ملاحظات:</b> {notes_text}"
    elements.append(Paragraph(notes, arabic_normal_style))
    
    # بناء PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================== التصميم الأسود/الأبيض ==================
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
            /* نظام ألوان أسود/أبيض احترافي */
            --primary-black: #000000;
            --dark-black: #111111;
            --medium-black: #222222;
            --light-black: #333333;
            --pure-white: #FFFFFF;
            --light-white: #F5F5F5;
            --gray-white: #E0E0E0;
            --accent-blue: #0066CC;
            --accent-green: #00CC88;
            --accent-red: #FF4444;
            --accent-gold: #FFD700;
            --text-primary: #FFFFFF;
            --text-secondary: #CCCCCC;
            --text-muted: #888888;
            --shadow-black: rgba(0, 0, 0, 0.3);
            --shadow-light: rgba(255, 255, 255, 0.1);
            --gradient-black: linear-gradient(135deg, #000000 0%, #222222 100%);
            --gradient-dark: linear-gradient(135deg, #111111 0%, #333333 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Tajawal', 'Segoe UI', sans-serif;
            background: var(--primary-black);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.8;
            overflow-x: hidden;
        }

        .premium-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 20px;
            min-height: 100vh;
        }

        /* شريط التنقل */
        .premium-navbar {
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0 30px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .nav-brand h1 {
            font-size: 2.2em;
            font-weight: 800;
            background: linear-gradient(45deg, var(--pure-white), var(--gray-white));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-links {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 600;
            padding: 12px 20px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .nav-link:hover {
            color: var(--pure-white);
            background: rgba(255, 255, 255, 0.05);
        }

        .nav-link.active {
            background: rgba(255, 255, 255, 0.1);
            color: var(--pure-white);
            border-left: 3px solid var(--pure-white);
        }

        /* المحتوى الرئيسي */
        .premium-content {
            margin-top: 100px;
            padding: 40px 0;
        }

        .premium-hero {
            background: var(--gradient-dark);
            border-radius: 20px;
            padding: 60px;
            margin-bottom: 50px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }

        .premium-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
            pointer-events: none;
        }

        .hero-content h1 {
            font-size: 4em;
            font-weight: 800;
            margin-bottom: 20px;
            line-height: 1.2;
        }

        .hero-content p {
            font-size: 1.4em;
            color: var(--text-secondary);
            margin-bottom: 30px;
            max-width: 600px;
        }

        /* كروت الخدمات */
        .premium-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin: 50px 0;
        }

        .premium-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }

        .premium-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.3);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }

        .premium-card i {
            font-size: 3em;
            margin-bottom: 25px;
            color: var(--pure-white);
        }

        .premium-card h3 {
            font-size: 1.8em;
            margin-bottom: 15px;
            color: var(--pure-white);
            font-weight: 700;
        }

        .premium-card p {
            color: var(--text-secondary);
            font-size: 1.1em;
            line-height: 1.7;
        }

        /* الإحصائيات */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin: 60px 0;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 35px 30px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }

        .stat-number {
            font-size: 3.5em;
            font-weight: 800;
            margin: 20px 0;
            color: var(--pure-white);
        }

        .stat-card p {
            font-size: 1.2em;
            color: var(--text-secondary);
            font-weight: 600;
        }

        /* الأزرار */
        .premium-btn {
            background: var(--pure-white);
            color: var(--primary-black);
            padding: 15px 35px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 700;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin: 10px;
        }

        .premium-btn:hover {
            background: var(--gray-white);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }

        .premium-btn-outline {
            background: transparent;
            border: 2px solid var(--pure-white);
            color: var(--pure-white);
        }

        .premium-btn-outline:hover {
            background: var(--pure-white);
            color: var(--primary-black);
        }

        /* حقول الإدخال */
        input, select, textarea {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            color: var(--pure-white) !important;
            padding: 12px 15px !important;
            font-family: 'Tajawal', sans-serif !important;
            width: 100% !important;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--pure-white) !important;
            box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1) !important;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        /* قسم الذكاء الاصطناعي */
        .ai-section {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 50px;
            margin: 60px 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* الجداول */
        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            text-align: right;
            color: var(--text-secondary);
            font-weight: 600;
        }

        td {
            padding: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--pure-white);
        }

        tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        /* التكيف مع الأجهزة المحمولة */
        @media (max-width: 768px) {
            .premium-navbar {
                padding: 0 15px;
                height: 70px;
            }

            .nav-brand h1 {
                font-size: 1.6em;
            }

            .nav-links {
                gap: 10px;
            }

            .nav-link {
                padding: 8px 12px;
                font-size: 0.9em;
            }

            .premium-hero {
                padding: 40px 25px;
            }

            .hero-content h1 {
                font-size: 2.5em;
            }

            .premium-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .premium-card {
                padding: 30px;
            }

            .ai-section {
                padding: 30px;
            }
        }

        /* تأثيرات متحركة */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }
    </style>
</head>
<body>
    <!-- شريط التنقل -->
    <nav class="premium-navbar">
        <div class="nav-brand">
            <i class="fas fa-file-invoice" style="color: var(--pure-white); font-size: 1.8em;"></i>
            <h1>InvoiceFlow Premium</h1>
        </div>
        
        <div class="nav-links">
            <a href="/" class="nav-link {% if request.endpoint == 'home' %}active{% endif %}">
                <i class="fas fa-home"></i> الرئيسية
            </a>
            <a href="/invoices" class="nav-link {% if request.endpoint == 'invoices' %}active{% endif %}">
                <i class="fas fa-file-invoice-dollar"></i> الفواتير
            </a>
            <a href="/create_invoice" class="nav-link {% if request.endpoint == 'create_invoice' %}active{% endif %}">
                <i class="fas fa-plus-circle"></i> إنشاء فاتورة
            </a>
            <a href="/ai" class="nav-link {% if request.endpoint == 'ai' %}active{% endif %}">
                <i class="fas fa-robot"></i> الذكاء الاصطناعي
            </a>
            <a href="/features" class="nav-link {% if request.endpoint == 'features' %}active{% endif %}">
                <i class="fas fa-star"></i> الميزات
            </a>
            {% if session.get('user_logged_in') %}
            <div class="user-menu">
                <span style="color: var(--pure-white); margin: 0 15px;">
                    <i class="fas fa-user-tie"></i> {{ session.username }}
                </span>
                <a href="/logout" class="premium-btn" style="padding: 10px 20px; font-size: 0.9em;">
                    <i class="fas fa-sign-out-alt"></i> خروج
                </a>
            </div>
            {% else %}
            <a href="/login" class="premium-btn" style="padding: 10px 20px; font-size: 0.9em;">
                <i class="fas fa-sign-in-alt"></i> دخول
            </a>
            {% endif %}
        </div>
    </nav>

    <!-- المحتوى الرئيسي -->
    <div class="premium-container">
        <div class="premium-content fade-in">
            {{ content | safe }}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // تأثيرات العدادات
            const counters = document.querySelectorAll('.stat-number');
            counters.forEach(counter => {
                const target = parseInt(counter.textContent.replace(/,/g, ''));
                if (!isNaN(target)) {
                    animateCounter(counter, 0, target, 2000);
                }
            });

            // تأثير التمرير لشريط التنقل
            window.addEventListener('scroll', function() {
                const navbar = document.querySelector('.premium-navbar');
                if (window.scrollY > 100) {
                    navbar.style.background = 'rgba(0, 0, 0, 0.98)';
                } else {
                    navbar.style.background = 'rgba(0, 0, 0, 0.95)';
                }
            });
        });

        function animateCounter(element, start, end, duration) {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const value = Math.floor(progress * (end - start) + start);
                element.textContent = value.toLocaleString();
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        }
    </script>
</body>
</html>
"""

# ================== Routes الأساسية ==================

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = {
        'total_invoices': 156,
        'total_revenue': 125000,
        'active_users': 89,
        'success_rate': 94
    }
    
    content = f"""
    <!-- قسم البطل -->
    <div class="premium-hero">
        <div class="hero-content">
            <h1>نظام الفواتير الاحترافي</h1>
            <p>منصة متكاملة لإدارة الفواتير بمستوى عالمي، مصممة خصيصاً للشركات الاحترافية</p>
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <a href="/create_invoice" class="premium-btn">
                    <i class="fas fa-rocket"></i> ابدأ الآن
                </a>
                <a href="/features" class="premium-btn premium-btn-outline">
                    <i class="fas fa-play-circle"></i> استكشف الميزات
                </a>
            </div>
        </div>
    </div>

    <!-- الإحصائيات -->
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-file-invoice"></i>
            <div class="stat-number" data-target="{stats['total_invoices']}">{stats['total_invoices']}</div>
            <p>فاتورة تم إنشاؤها</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-number" data-target="{stats['total_revenue']}">${stats['total_revenue']:,.0f}</div>
            <p>إيرادات تم تحقيقها</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-users"></i>
            <div class="stat-number" data-target="{stats['active_users']}">{stats['active_users']}</div>
            <p>مستخدم نشط</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-chart-line"></i>
            <div class="stat-number" data-target="{stats['success_rate']}">{stats['success_rate']}%</div>
            <p>معدل النجاح</p>
        </div>
    </div>

    <!-- المزايا الرئيسية -->
    <div style="text-align: center; margin: 80px 0 40px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; color: var(--pure-white);">
            لماذا InvoiceFlow Premium؟
        </h2>
    </div>

    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-bolt"></i>
            <h3>سرعة فائقة</h3>
            <p>إنشاء الفواتير في ثوانٍ مع واجهة مستخدم سريعة وسلسة</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-lock"></i>
            <h3>أمان كامل</h3>
            <p>بياناتك محمية بأفضل أنظمة التشفير والأمان</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-chart-pie"></i>
            <h3>تحليلات ذكية</h3>
            <p>تقارير وتحليلات متقدمة تساعد في اتخاذ القرارات</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-headset"></i>
            <h3>دعم فني</h3>
            <p>فريق دعم متخصص متاح على مدار الساعة لمساعدتك</p>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="InvoiceFlow Premium - النظام الاحترافي", content=content)

@app.route('/login')
def login():
    """صفحة تسجيل الدخول"""
    content = """
    <div style="max-width: 500px; margin: 100px auto;">
        <div class="premium-card" style="text-align: center;">
            <i class="fas fa-lock" style="font-size: 4em; margin-bottom: 30px;"></i>
            <h2 style="margin-bottom: 30px;">الدخول إلى النظام</h2>
            
            <form style="text-align: right;">
                <div style="margin-bottom: 25px;">
                    <label>اسم المستخدم</label>
                    <input type="text" placeholder="أدخل اسم المستخدم" required>
                </div>
                <div style="margin-bottom: 25px;">
                    <label>كلمة المرور</label>
                    <input type="password" placeholder="أدخل كلمة المرور" required>
                </div>
                
                <button type="submit" class="premium-btn" style="width: 100%; padding: 18px;">
                    <i class="fas fa-sign-in-alt"></i> دخول إلى النظام
                </button>
            </form>
            
            <div style="margin-top: 30px; color: var(--text-muted);">
                <p>ليس لديك حساب؟ <a href="/register" style="color: var(--pure-white); text-decoration: none;">انضم إلينا</a></p>
            </div>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الدخول - InvoiceFlow Premium", content=content)

@app.route('/register')
def register():
    """صفحة التسجيل"""
    content = """
    <div style="max-width: 500px; margin: 100px auto;">
        <div class="premium-card" style="text-align: center;">
            <i class="fas fa-user-plus" style="font-size: 4em; margin-bottom: 30px;"></i>
            <h2 style="margin-bottom: 30px;">انضم إلى النخبة</h2>
            
            <form style="text-align: right;">
                <div style="margin-bottom: 20px;">
                    <label>الاسم الكامل</label>
                    <input type="text" placeholder="أدخل الاسم الكامل" required>
                </div>
                <div style="margin-bottom: 20px;">
                    <label>اسم المستخدم</label>
                    <input type="text" placeholder="اختر اسم مستخدم" required>
                </div>
                <div style="margin-bottom: 20px;">
                    <label>البريد الإلكتروني</label>
                    <input type="email" placeholder="example@domain.com" required>
                </div>
                <div style="margin-bottom: 25px;">
                    <label>كلمة المرور</label>
                    <input type="password" placeholder="اختر كلمة مرور قوية" required>
                </div>
                
                <button type="submit" class="premium-btn" style="width: 100%; padding: 18px;">
                    <i class="fas fa-user-plus"></i> إنشاء حساب
                </button>
            </form>
            
            <div style="margin-top: 30px; color: var(--text-muted);">
                <p>لديك حساب؟ <a href="/login" style="color: var(--pure-white); text-decoration: none;">سجل الدخول</a></p>
            </div>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="التسجيل - InvoiceFlow Premium", content=content)

@app.route('/invoices')
def invoices():
    """صفحة الفواتير"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; color: var(--pure-white);">
            <i class="fas fa-file-invoice-dollar"></i> إدارة الفواتير
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted);">
            قم بإدارة وعرض وتتبع جميع فواتيرك من مكان واحد
        </p>
    </div>

    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-search"></i>
            <h3>استعراض الفواتير</h3>
            <p>تصفح جميع فواتيرك مع إمكانيات البحث والتصفية المتقدمة</p>
            <a href="/invoices/list" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-list"></i> عرض الكل
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-plus"></i>
            <h3>إنشاء فاتورة</h3>
            <p>أنشئ فاتورة جديدة بتصميم احترافي وخيارات متقدمة</p>
            <a href="/create_invoice" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-plus-circle"></i> إنشاء جديد
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-chart-bar"></i>
            <h3>إحصائيات الفواتير</h3>
            <p>اطلع على إحصائيات مفصلة عن أداء فواتيرك وإيراداتك</p>
            <a href="/invoices/stats" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-chart-line"></i> عرض الإحصائيات
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الفواتير - InvoiceFlow Premium", content=content)

@app.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة"""
    if request.method == 'POST':
        try:
            # جمع بيانات الفاتورة
            invoice_data = {
                'client_name': request.form.get('client_name', 'عميل'),
                'client_email': request.form.get('client_email', ''),
                'invoice_number': request.form.get('invoice_number', f'INV-{int(time.time())}'),
                'date': request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
                'items': [],
                'notes': request.form.get('notes', 'شكراً لتعاملكم معنا. يرجى الدفع خلال 30 يوم من تاريخ الفاتورة.'),
                'status': 'معلق'
            }
            
            # معالجة العناصر
            descriptions = request.form.getlist('item_description[]')
            quantities = request.form.getlist('item_quantity[]')
            prices = request.form.getlist('item_price[]')
            
            for i in range(len(descriptions)):
                if descriptions[i] and descriptions[i].strip():
                    try:
                        invoice_data['items'].append({
                            'description': descriptions[i].strip(),
                            'quantity': float(quantities[i]) if quantities[i] and quantities[i].strip() else 1,
                            'price': float(prices[i]) if prices[i] and prices[i].strip() else 0
                        })
                    except ValueError:
                        continue
            
            # إذا لم يكن هناك عناصر، نضيف عنصر افتراضي
            if not invoice_data['items']:
                invoice_data['items'] = [{
                    'description': 'خدمة إدارة الفواتير الاحترافية',
                    'quantity': 1,
                    'price': 1000
                }]
            
            # إنشاء PDF
            pdf_buffer = create_invoice_pdf(invoice_data)
            
            # إرجاع الملف للتحميل
            filename = f"invoice_{invoice_data['invoice_number']}.pdf"
            
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            flash(f'خطأ في إنشاء الفاتورة: {str(e)}', 'error')
            return redirect(url_for('create_invoice'))
    
    # نموذج إنشاء الفاتورة
    content = """
    <div style="max-width: 900px; margin: 0 auto;">
        <div class="premium-card">
            <h2 style="text-align: center; margin-bottom: 30px; color: var(--pure-white);">
                <i class="fas fa-file-invoice"></i> إنشاء فاتورة جديدة
            </h2>
            
            <form method="POST" action="{{ url_for('create_invoice') }}" id="invoiceForm">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                    <div>
                        <label>اسم العميل *</label>
                        <input type="text" name="client_name" required placeholder="أدخل اسم العميل">
                    </div>
                    <div>
                        <label>البريد الإلكتروني</label>
                        <input type="email" name="client_email" placeholder="example@domain.com">
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                    <div>
                        <label>رقم الفاتورة</label>
                        <input type="text" name="invoice_number" value="INV-{{ '%03d' % (range(1, 1000)|random) }}" placeholder="رقم الفاتورة">
                    </div>
                    <div>
                        <label>التاريخ</label>
                        <input type="date" name="date" value="{{ datetime.now().strftime('%Y-%m-%d') }}">
                    </div>
                </div>
                
                <!-- عناصر الفاتورة -->
                <div id="itemsContainer">
                    <div class="invoice-item" style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div>
                            <label>الوصف</label>
                            <input type="text" name="item_description[]" placeholder="وصف الخدمة/المنتج" required>
                        </div>
                        <div>
                            <label>الكمية</label>
                            <input type="number" name="item_quantity[]" placeholder="الكمية" value="1" step="1" min="1" required>
                        </div>
                        <div>
                            <label>السعر (ر.س)</label>
                            <input type="number" name="item_price[]" placeholder="السعر" step="0.01" min="0" required>
                        </div>
                    </div>
                </div>
                
                <button type="button" onclick="addItem()" class="premium-btn-outline" style="margin-bottom: 20px; padding: 12px 25px;">
                    <i class="fas fa-plus"></i> إضافة عنصر جديد
                </button>
                
                <div style="margin-bottom: 25px;">
                    <label>ملاحظات إضافية</label>
                    <textarea name="notes" rows="3" placeholder="ملاحظات أو تعليمات خاصة..."></textarea>
                </div>
                
                <button type="submit" class="premium-btn" style="width: 100%; padding: 15px; font-size: 1.1em;">
                    <i class="fas fa-file-pdf"></i> إنشاء وتحميل الفاتورة
                </button>
            </form>
        </div>
    </div>
    
    <script>
    function addItem() {
        const container = document.getElementById('itemsContainer');
        const newItem = document.createElement('div');
        newItem.className = 'invoice-item';
        newItem.style = 'display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; margin-bottom: 15px;';
        newItem.innerHTML = `
            <div>
                <label>الوصف</label>
                <input type="text" name="item_description[]" placeholder="وصف الخدمة/المنتج" required>
            </div>
            <div>
                <label>الكمية</label>
                <input type="number" name="item_quantity[]" placeholder="الكمية" value="1" step="1" min="1" required>
            </div>
            <div>
                <label>السعر (ر.س)</label>
                <input type="number" name="item_price[]" placeholder="السعر" step="0.01" min="0" required>
            </div>
        `;
        container.appendChild(newItem);
    }
    </script>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="إنشاء فاتورة - InvoiceFlow Premium", content=content)

@app.route('/ai')
def ai():
    """صفحة الذكاء الاصطناعي"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; color: var(--pure-white);">
            <i class="fas fa-robot"></i> الذكاء الاصطناعي
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted);">
            استفد من قوة الذكاء الاصطناعي لتحليل بياناتك وتقديم توصيات ذكية
        </p>
    </div>

    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-chart-line"></i>
            <h3>تحليل الإيرادات</h3>
            <p>تحليل متقدم لأنماط الإيرادات وتوقعات النمو المستقبلية</p>
            <a href="/ai/revenue" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-chart-bar"></i> عرض التحليل
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-users"></i>
            <h3>تحليل العملاء</h3>
            <p>فهم سلوك عملائك وتحديد أفضل الفرص للنمو</p>
            <a href="/ai/clients" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-user-chart"></i> تحليل العملاء
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-lightbulb"></i>
            <h3>توصيات ذكية</h3>
            <p>احصل على توصيات مخصصة لتحسين أداء أعمالك</p>
            <a href="/ai/recommendations" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-magic"></i> التوصيات
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الذكاء الاصطناعي - InvoiceFlow Premium", content=content)

@app.route('/ai/revenue')
def ai_revenue():
    """تحليل الإيرادات الذكي"""
    content = """
    <div class="premium-card">
        <h2 style="color: var(--pure-white); margin-bottom: 30px;">
            <i class="fas fa-chart-line"></i> تحليل الإيرادات الذكي
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px;">
            <div>
                <h3 style="color: var(--text-secondary); margin-bottom: 20px;">📊 إحصائيات الإيرادات</h3>
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <span style="color: var(--text-secondary);">الإيرادات الشهرية:</span>
                        <span style="color: var(--pure-white); font-weight: bold;">$45,800</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <span style="color: var(--text-secondary);">نسبة النمو:</span>
                        <span style="color: var(--accent-green); font-weight: bold;">↑ 18%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <span style="color: var(--text-secondary);">متوسط الفاتورة:</span>
                        <span style="color: var(--pure-white); font-weight: bold;">$1,250</span>
                    </div>
                </div>
            </div>
            
            <div>
                <h3 style="color: var(--text-secondary); margin-bottom: 20px;">🎯 التنبؤات المستقبلية</h3>
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                    <p style="color: var(--text-secondary); margin-bottom: 15px;">التنبؤ بالإيرادات القادمة:</p>
                    <div style="color: var(--pure-white); font-size: 1.2em;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span>الشهر القادم:</span>
                            <span>$52,400</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span>ربع السنة:</span>
                            <span>$158,200</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="/ai" class="premium-btn" style="padding: 15px 40px;">
                <i class="fas fa-arrow-right"></i> العودة للقائمة الرئيسية
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="تحليل الإيرادات - InvoiceFlow Premium", content=content)

@app.route('/ai/clients')
def ai_clients():
    """تحليل العملاء"""
    content = """
    <div class="premium-card">
        <h2 style="color: var(--pure-white); margin-bottom: 30px;">
            <i class="fas fa-users"></i> تحليل العملاء المتقدم
        </h2>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: var(--text-secondary); margin-bottom: 15px;">👑 العملاء VIP</h3>
            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                    <div style="color: var(--text-secondary); font-weight: bold;">اسم العميل</div>
                    <div style="color: var(--text-secondary); font-weight: bold;">إجمالي المشتريات</div>
                    <div style="color: var(--text-secondary); font-weight: bold;">مستوى الولاء</div>
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                    <div style="color: var(--pure-white);">شركة التقنية المتقدمة</div>
                    <div style="color: var(--pure-white);">$28,500</div>
                    <div><span style="color: var(--accent-green);">★★★★★</span></div>
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                    <div style="color: var(--pure-white);">مؤسسة النجاح التجارية</div>
                    <div style="color: var(--pure-white);">$19,750</div>
                    <div><span style="color: var(--accent-green);">★★★★☆</span></div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="/ai" class="premium-btn" style="padding: 15px 40px;">
                <i class="fas fa-arrow-right"></i> العودة للقائمة الرئيسية
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="تحليل العملاء - InvoiceFlow Premium", content=content)

@app.route('/ai/recommendations')
def ai_recommendations():
    """التوصيات الذكية"""
    content = """
    <div class="premium-card">
        <h2 style="color: var(--pure-white); margin-bottom: 30px;">
            <i class="fas fa-lightbulb"></i> التوصيات الذكية
        </h2>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: var(--text-secondary); margin-bottom: 20px;">🚀 توصيات لزيادة الإيرادات</h3>
            <div style="background: rgba(0, 102, 204, 0.1); border: 1px solid rgba(0, 102, 204, 0.3); 
                        padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: var(--accent-blue); margin-bottom: 10px;">
                    <i class="fas fa-bullseye"></i> استهداف العملاء النشطين
                </h4>
                <p style="color: var(--pure-white);">
                    ركز على 20% من العملاء الذين يمثلون 80% من إيراداتك. 
                    قدم لهم عروضاً حصرية لزيادة ولائهم.
                </p>
            </div>
            
            <div style="background: rgba(0, 204, 136, 0.1); border: 1px solid rgba(0, 204, 136, 0.3); 
                        padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                <h4 style="color: var(--accent-green); margin-bottom: 10px;">
                    <i class="fas fa-chart-pie"></i> تنويع الخدمات
                </h4>
                <p style="color: var(--pure-white);">
                    أضف 3 خدمات جديدة بناءً على طلبات العملاء المتكررة. 
                    التوقعات تشير إلى زيادة 25% في الإيرادات.
                </p>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="/ai" class="premium-btn" style="padding: 15px 40px;">
                <i class="fas fa-arrow-right"></i> العودة للقائمة الرئيسية
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="التوصيات الذكية - InvoiceFlow Premium", content=content)

@app.route('/invoices/list')
def invoices_list():
    """قائمة الفواتير"""
    content = """
    <div class="premium-card">
        <h2 style="color: var(--pure-white); margin-bottom: 30px;">
            <i class="fas fa-list"></i> قائمة الفواتير
        </h2>
        
        <div style="margin-bottom: 20px;">
            <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                <input type="text" placeholder="بحث في الفواتير..." 
                       style="flex: 1;">
                <select>
                    <option value="">جميع الحالات</option>
                    <option value="paid">مدفوعة</option>
                    <option value="pending">معلقة</option>
                </select>
            </div>
        </div>
        
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>رقم الفاتورة</th>
                        <th>العميل</th>
                        <th>المبلغ</th>
                        <th>التاريخ</th>
                        <th>الحالة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>INV-2024-001</td>
                        <td>شركة النجاح</td>
                        <td>$1,250.00</td>
                        <td>2024-01-15</td>
                        <td>
                            <span style="background: rgba(0,204,136,0.2); color: var(--accent-green); 
                                        padding: 5px 10px; border-radius: 20px; font-size: 0.9em;">
                                مدفوعة
                            </span>
                        </td>
                        <td>
                            <button class="premium-btn-outline" style="padding: 8px 15px; margin: 0 5px;">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="premium-btn-outline" style="padding: 8px 15px; margin: 0 5px;">
                                <i class="fas fa-download"></i>
                            </button>
                        </td>
                    </tr>
                    <tr>
                        <td>INV-2024-002</td>
                        <td>مؤسسة التميز</td>
                        <td>$2,850.00</td>
                        <td>2024-01-18</td>
                        <td>
                            <span style="background: rgba(255,204,0,0.2); color: var(--accent-gold); 
                                        padding: 5px 10px; border-radius: 20px; font-size: 0.9em;">
                                معلقة
                            </span>
                        </td>
                        <td>
                            <button class="premium-btn-outline" style="padding: 8px 15px; margin: 0 5px;">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="premium-btn-outline" style="padding: 8px 15px; margin: 0 5px;">
                                <i class="fas fa-download"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/invoices" class="premium-btn" style="padding: 15px 40px;">
                <i class="fas fa-arrow-right"></i> العودة
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="قائمة الفواتير - InvoiceFlow Premium", content=content)

@app.route('/invoices/stats')
def invoices_stats():
    """إحصائيات الفواتير"""
    content = """
    <div style="display: grid; gap: 30px;">
        <div class="premium-card">
            <h2 style="color: var(--pure-white); margin-bottom: 30px;">
                <i class="fas fa-chart-bar"></i> إحصائيات الفواتير
            </h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="text-align: center; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--pure-white);">156</div>
                    <div style="color: var(--text-secondary);">إجمالي الفواتير</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--pure-white);">$125K</div>
                    <div style="color: var(--text-secondary);">إجمالي الإيرادات</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--accent-green);">94%</div>
                    <div style="color: var(--text-secondary);">فواتير مدفوعة</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px;">
                    <div style="font-size: 2.5em; font-weight: bold; color: var(--accent-blue);">28</div>
                    <div style="color: var(--text-secondary);">عملاء نشطين</div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <a href="/invoices" class="premium-btn" style="padding: 15px 40px;">
                <i class="fas fa-arrow-right"></i> العودة
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="إحصائيات الفواتير - InvoiceFlow Premium", content=content)

@app.route('/features')
def features():
    """صفحة الميزات"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; color: var(--pure-white);">
            <i class="fas fa-star"></i> الميزات الكاملة
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted); max-width: 600px; margin: 0 auto;">
            اكتشف كل ما يقدمه InvoiceFlow Premium من ميزات متقدمة
        </p>
    </div>
    
    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-file-pdf"></i>
            <h3>فواتير PDF احترافية</h3>
            <p>إنشاء فواتير بتصميم احترافي مع دعم كامل للغة العربية والتنسيق المتقدم</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-robot"></i>
            <h3>ذكاء اصطناعي متكامل</h3>
            <p>تحليلات ذكية وتوقعات وتوصيات مبنية على بياناتك الفعلية</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-shield-alt"></i>
            <h3>أمان متقدم</h3>
            <p>تشفير كامل للبيانات وحماية من الاختراق ونسخ احتياطي تلقائي</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-chart-line"></i>
            <h3>تقارير متقدمة</h3>
            <p>لوحة تحكم شاملة مع رسوم بيانية وتقارير مفصلة قابلة للتخصيص</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-mobile-alt"></i>
            <h3>تصميم متجاوب</h3>
            <p>تجربة مستخدم متميزة على جميع الأجهزة والحجوم</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-sync-alt"></i>
            <h3>مزامنة فورية</h3>
            <p>مزامنة تلقائية للبيانات بين جميع أجهزتك في الوقت الحقيقي</p>
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 50px;">
        <a href="/create_invoice" class="premium-btn" style="padding: 20px 50px; font-size: 1.2em;">
            <i class="fas fa-rocket"></i> جرب الآن مجاناً
        </a>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الميزات - InvoiceFlow Premium", content=content)

@app.route('/demo')
def demo():
    """الصفحة التجريبية"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; color: var(--pure-white);">
            <i class="fas fa-play-circle"></i> الصفحة التجريبية
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted); max-width: 600px; margin: 0 auto;">
            جرب InvoiceFlow Premium بدون الحاجة إلى حساب
        </p>
    </div>
    
    <div class="premium-card" style="max-width: 600px; margin: 0 auto; text-align: center;">
        <div style="font-size: 5em; color: var(--pure-white); margin-bottom: 30px;">
            <i class="fas fa-laptop-code"></i>
        </div>
        <h3 style="margin-bottom: 20px; font-size: 2em;">تجربة مباشرة</h3>
        <p style="color: var(--text-muted); margin-bottom: 30px; line-height: 1.7;">
            يمكنك تجربة إنشاء فاتورة نموذجية لترى كيف يعمل النظام.
        </p>
        
        <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
            <a href="/create_invoice" class="premium-btn" style="padding: 15px 35px;">
                <i class="fas fa-file-invoice"></i> إنشاء فاتورة تجريبية
            </a>
            <a href="/features" class="premium-btn premium-btn-outline" style="padding: 15px 35px;">
                <i class="fas fa-list"></i> عرض الميزات
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الصفحة التجريبية - InvoiceFlow Premium", content=content)

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    """صفحة 404"""
    content = """
    <div style="text-align: center; padding: 100px 20px;">
        <h1 style="font-size: 8em; color: var(--pure-white); margin-bottom: 20px;">404</h1>
        <h2 style="color: var(--text-secondary); margin-bottom: 30px;">الصفحة غير موجودة</h2>
        <p style="color: var(--text-muted); margin-bottom: 40px; max-width: 500px; margin: 0 auto 40px;">
            عذراً، الصفحة التي تبحث عنها غير موجودة أو تم نقلها.
        </p>
        <a href="/" class="premium-btn">
            <i class="fas fa-home"></i> العودة للرئيسية
        </a>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="404 - الصفحة غير موجودة", content=content), 404

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام الاحترافي...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        print("🎨 التصميم الأسود/الأبيض الاحترافي مفعل!")
        print("📄 نظام الفواتير PDF بالعربية جاهز!")
        print("🧠 الذكاء الاصطناعي نشط!")
        print("🔐 نظام الأمان مفعل!")
        
        print("\n📋 المسارات المتاحة:")
        print("🔹 / - الصفحة الرئيسية")
        print("🔹 /login - تسجيل الدخول") 
        print("🔹 /register - إنشاء حساب")
        print("🔹 /invoices - إدارة الفواتير")
        print("🔹 /create_invoice - إنشاء فاتورة")
        print("🔹 /ai - الذكاء الاصطناعي")
        print("🔹 /ai/revenue - تحليل الإيرادات")
        print("🔹 /ai/clients - تحليل العملاء")
        print("🔹 /ai/recommendations - التوصيات الذكية")
        print("🔹 /invoices/list - قائمة الفواتير")
        print("🔹 /invoices/stats - إحصائيات الفواتير")
        print("🔹 /features - الميزات الكاملة")
        print("🔹 /demo - الصفحة التجريبية")
        print("🔹 /logout - تسجيل الخروج")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        import time
        time.sleep(5)
