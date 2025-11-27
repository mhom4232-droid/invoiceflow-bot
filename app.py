import os
import sqlite3
import json
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session, send_file
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

# ================== تطبيق Flask الاحترافي ==================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_pro_enterprise_2024_v3')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# الحصول على البورت من بيئة Render أو استخدام 10000 محلياً
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - نظام إدارة الفواتير الاحترافي")
print("🚀 تصميم شركات عالمي - أمان متقدم - واجهات متجاوبة")
print("💼 الإصدار النهائي المتكامل - قاعدة بيانات منظمة")
print("=" * 80)

# ================== نظام إدارة قاعدة البيانات المحسن ==================
class DatabaseManager:
    def __init__(self):
        self.db_path = self.ensure_database_path()
        
    def ensure_database_path(self):
        """تأكيد وجود مسار قاعدة البيانات"""
        if 'RENDER' in os.environ:
            # في Render، استخدم المسار المطلق
            db_dir = '/var/lib/render'
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            return os.path.join(db_dir, 'invoiceflow_pro.db')
        else:
            # محلياً، استخدم المسار الحالي
            db_dir = 'database'
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            return os.path.join(db_dir, 'invoiceflow_pro.db')
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            raise

# ================== نظام إدارة المستخدمين المتقدم ==================
class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    email_verified BOOLEAN DEFAULT 0,
                    verification_token TEXT,
                    reset_token TEXT,
                    profile_data TEXT DEFAULT '{}'
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
            print("✅ نظام المستخدمين المتقدم جاهز")
        except Exception as e:
            print(f"🔧 خطأ في نظام المستخدمين: {e}")

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

    def authenticate_user(self, identifier, password):
        """مصادقة المستخدم باستخدام اسم المستخدم أو البريد الإلكتروني"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT password_hash, user_role, email, full_name, company_name, plan_type, username
                FROM users WHERE (username = ? OR email = ?) AND is_active = 1
            ''', (identifier, identifier))
            
            result = cursor.fetchone()
            
            if result and self.verify_password(result[0], password):
                # تحديث آخر دخول
                cursor.execute('UPDATE users SET last_login = ? WHERE username = ?', 
                             (datetime.now(), result[6]))
                conn.commit()
                conn.close()
                return True, result[1], result[2], result[3], result[4], result[5], result[6]
            
            conn.close()
            return False, 'user', '', '', '', 'professional', ''
        except Exception as e:
            print(f"🔧 خطأ في المصادقة: {e}")
            return False, 'user', '', '', '', 'professional', ''

    def register_user(self, username, email, password, full_name, company_name='', phone=''):
        """تسجيل مستخدم جديد"""
        try:
            # التحقق من صحة البريد الإلكتروني
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                return False, f"بريد إلكتروني غير صحيح: {str(e)}"

            # التحقق من قوة كلمة المرور
            if len(password) < 8:
                return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # التحقق من عدم وجود المستخدم مسبقاً
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً"
            
            password_hash = self.hash_password(password)
            verification_token = secrets.token_urlsafe(32)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, company_name, phone, verification_token)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, company_name, phone, verification_token))
            
            conn.commit()
            conn.close()
            
            return True, "تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن."
        except Exception as e:
            print(f"🔧 خطأ في التسجيل: {e}")
            return False, f"خطأ في إنشاء الحساب: {str(e)}"

# ================== نظام إدارة الفواتير المتكامل ==================
class InvoiceManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.init_invoice_system()

    def init_invoice_system(self):
        """تهيئة نظام الفواتير المتكامل"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # جدول الفواتير المحسن
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

            # جدول العملاء المتكامل
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

            # جدول الخدمات والمنتجات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price DECIMAL(15,2) NOT NULL,
                    unit TEXT DEFAULT 'ساعة',
                    category TEXT DEFAULT 'عام',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            print("✅ نظام الفواتير المتكامل جاهز")
        except Exception as e:
            print(f"🔧 خطأ في نظام الفواتير: {e}")

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
            return True, invoice_number, "تم إنشاء الفاتورة بنجاح"
        except Exception as e:
            print(f"🔧 خطأ في إنشاء الفاتورة: {e}")
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
            print(f"🔧 خطأ في جلب الفواتير: {e}")
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
            print(f"🔧 خطأ في جلب الإحصائيات: {e}")
            return {'total_invoices': 0, 'total_revenue': 0, 'paid_amount': 0, 'pending_invoices': 0, 'tax_amount': 0}

    def get_user_clients(self, user_id):
        """جلب عملاء المستخدم"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, email, phone, company_name, category, created_at
                FROM clients WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC
            ''', (user_id,))
            
            clients = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return clients
        except Exception as e:
            print(f"🔧 خطأ في جلب العملاء: {e}")
            return []

# ================== نظام PDF الاحترافي العالمي ==================
class ProfessionalPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor('#2563EB')
        self.secondary_color = colors.HexColor('#1E293B')
        self.accent_color = colors.HexColor('#0D9488')
    
    def create_professional_invoice(self, invoice_data):
        """إنشاء فاتورة PDF احترافية بتصميم عالمي"""
        try:
            buffer = io.BytesIO()
            
            # إنشاء مستند بتصميم احترافي
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=30, 
                leftMargin=30, 
                topMargin=40, 
                bottomMargin=40
            )
            
            elements = []
            
            # 1. 🎨 رأس الفاتورة الاحترافي
            elements.extend(self.create_professional_header(invoice_data))
            
            # 2. 👥 معلومات البائع والعميل
            elements.extend(self.create_company_client_info(invoice_data))
            
            # 3. 📊 جدول الخدمات المتطور
            elements.extend(self.create_services_table(invoice_data))
            
            # 4. 💰 قسم الإجماليات والملاحظات
            elements.extend(self.create_totals_section(invoice_data))
            
            # 5. 🏆 تذييل الفاتورة الاحترافي
            elements.extend(self.create_professional_footer())
            
            # بناء المستند
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF: {e}")
            return None
    
    def create_professional_header(self, invoice_data):
        """رأس الفاتورة الاحترافي"""
        elements = []
        
        # العنوان الرئيسي
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            alignment=1,  # محاذاة وسط
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph(arabic_text("فاتورة رسمية"), title_style)
        elements.append(title)
        
        # معلومات الفاتورة
        header_data = [
            [arabic_text('رقم الفاتورة'), arabic_text(invoice_data['invoice_number'])],
            [arabic_text('تاريخ الإصدار'), arabic_text(invoice_data['issue_date'])],
            [arabic_text('تاريخ الاستحقاق'), arabic_text(invoice_data['due_date'])],
            [arabic_text('الحالة'), arabic_text(invoice_data.get('status', 'مسودة'))]
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
        """معلومات الشركة والعميل بتصميم احترافي"""
        elements = []
        
        company_name = invoice_data.get('company_name', 'InvoiceFlow Pro')
        company_info = arabic_text(f"""
        {company_name}
        نظام إدارة الفواتير الاحترافي
        البريد الإلكتروني: info@invoiceflow.com
        الهاتف: +966500000000
        """)
        
        client_info = arabic_text(f"""
        {invoice_data['client_name']}
        {invoice_data.get('client_email', '')}
        {invoice_data.get('client_phone', '')}
        {invoice_data.get('client_address', '')}
        """)
        
        info_data = [
            [arabic_text('معلومات البائع'), arabic_text('معلومات العميل')],
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
        """جدول الخدمات بتصميم متطور"""
        elements = []
        
        # عنوان الجدول
        section_title = Paragraph(arabic_text("الخدمات والمنتجات"), self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 10))
        
        # رأس الجدول
        header = [arabic_text('الخدمة'), arabic_text('الوصف'), arabic_text('الكمية'), arabic_text('سعر الوحدة'), arabic_text('المجموع')]
        data = [header]
        
        # بيانات الخدمات
        for service in invoice_data['services']:
            total = service['quantity'] * service['price']
            data.append([
                arabic_text(service['name']),
                arabic_text(service.get('description', '')),
                str(service['quantity']),
                f"{service['price']:,.2f}",
                f"{total:,.2f}"
            ])
        
        # إنشاء الجدول
        services_table = Table(data, colWidths=[120, 150, 60, 80, 80])
        services_table.setStyle(TableStyle([
            # رأس الجدول
            ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # بيانات الجدول
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
        """قسم الإجماليات والملاحظات"""
        elements = []
        
        # بيانات الإجماليات
        totals_data = [
            [arabic_text('المجموع الفرعي:'), f"{invoice_data['subtotal']:,.2f}"],
            [arabic_text(f'الضريبة ({invoice_data["tax_rate"]}%):'), f"{invoice_data['tax_amount']:,.2f}"],
            [arabic_text('الإجمالي النهائي:'), f"{invoice_data['total_amount']:,.2f}"]
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
        
        # الملاحظات وشروط الدفع
        if invoice_data.get('notes') or invoice_data.get('payment_terms'):
            notes_text = ""
            if invoice_data.get('payment_terms'):
                notes_text += f"{arabic_text('شروط الدفع:')} {arabic_text(invoice_data['payment_terms'])}<br/>"
            if invoice_data.get('notes'):
                notes_text += f"{arabic_text('ملاحظات:')} {arabic_text(invoice_data['notes'])}"
            
            notes_paragraph = Paragraph(notes_text, self.styles['Normal'])
            elements.append(notes_paragraph)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def create_professional_footer(self):
        """تذييل الفاتورة الاحترافي"""
        elements = []
        
        footer_text = arabic_text("""
        InvoiceFlow Pro - نظام إدارة الفواتير الاحترافي
        هاتف: +966500000000 | البريد الإلكتروني: info@invoiceflow.com
        شكراً لتعاملكم معنا
        """)
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#475569'),
            alignment=1,  # محاذاة وسط
            spaceBefore=20
        )
        
        footer = Paragraph(footer_text.replace('\n', '<br/>'), footer_style)
        elements.append(footer)
        
        return elements

# ================== نظام الذكاء الاصطناعي ==================
class InvoiceAI:
    def __init__(self):
        self.user_profiles = {}
        
    def smart_welcome(self, username):
        """ترحيب ذكي مخصص لكل مستخدم"""
        user_stats = invoice_manager.get_user_stats(username)
        return f"""
        <div class="content-section" style="background: linear-gradient(135deg, var(--primary-dark), #1a237e); color: white;">
            <h3 style="margin-bottom: 15px; color: white;">
                <i class="fas fa-brain"></i> المساعد الذكي - InvoiceAI
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h4 style="color: var(--accent-teal); margin-bottom: 10px;">🧠 ترحيب ذكي</h4>
                    <p>مرحباً <b>{username}</b>! 👋</p>
                    <p>• الإيرادات المتوقعة: <b>${user_stats['total_revenue'] * 1.15:,.0f}</b></p>
                    <p>• فواتير تحت المتابعة: <b>{user_stats['pending_invoices']}</b></p>
                </div>
                <div>
                    <h4 style="color: var(--accent-teal); margin-bottom: 10px;">💡 توصيات ذكية</h4>
                    {self.generate_smart_recommendations(username)}
                </div>
            </div>
        </div>
        """
    
    def generate_smart_recommendations(self, username):
        """توصيات ذكية مخصصة"""
        invoices = invoice_manager.get_user_invoices(username)
        recommendations = []
        
        if len(invoices) > 5:
            recommendations.append("🎯 لديك قاعدة عملاء جيدة، نوصي بعرض باقة خدمات متكاملة")
        
        pending_count = sum(1 for inv in invoices if inv['status'] == 'معلقة')
        if pending_count > 2:
            recommendations.append("⏰ لديك فواتير معلقة، نوصي بمتابعة فورية مع العملاء")
            
        if not recommendations:
            recommendations.append("✨ أداؤك ممتاز! استمر في هذا النجاح")
            
        return "".join(f'<p>• {rec}</p>' for rec in recommendations)

# ================== إعداد الأنظمة ==================
db_manager = DatabaseManager()
user_manager = UserManager()
invoice_manager = InvoiceManager()
pdf_generator = ProfessionalPDFGenerator()
invoice_ai = InvoiceAI()

class SystemMonitor:
    def __init__(self):
        self.uptime_start = time.time()
        
    def start_monitoring(self):
        print("🔄 بدء أنظمة InvoiceFlow Pro...")
        Thread(target=self._monitor, daemon=True).start()
        print("✅ أنظمة InvoiceFlow Pro مفعلة!")
    
    def _monitor(self):
        while True:
            time.sleep(60)
            uptime = time.time() - self.uptime_start
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            print(f"📊 تقرير النظام: {hours}س {minutes}د - نظام مستقر")

monitor = SystemMonitor()
monitor.start_monitoring()

# ================== التصميم المتجاوب الاحترافي ==================
PROFESSIONAL_DESIGN = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            /* نظام الألوان الاحترافي */
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
            
            /* تأثيرات التدرج */
            --blue-gradient: linear-gradient(135deg, var(--accent-blue), #1D4ED8);
            --teal-gradient: linear-gradient(135deg, var(--accent-teal), #0F766E);
            --dark-gradient: linear-gradient(135deg, var(--primary-dark), #020617);
            
            /* الظلال */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--light-gray);
            color: var(--primary-dark);
            min-height: 100vh;
            line-height: 1.7;
            width: 100%;
            height: 100%;
        }
        
        .professional-container {
            width: 100%;
            min-height: 100vh;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* ================== شاشة تسجيل الدخول المتجاوبة ================== */
        .auth-wrapper {
            min-height: 100vh;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--dark-gradient);
            position: relative;
            padding: 20px;
        }
        
        .auth-card {
            background: var(--pure-white);
            border-radius: 16px;
            padding: 40px 35px;
            width: 100%;
            max-width: 440px;
            box-shadow: var(--shadow-xl);
            border: 1px solid var(--border-light);
            animation: cardEntrance 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        @keyframes cardEntrance {
            0% {
                opacity: 0;
                transform: translateY(20px) scale(0.98);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        .brand-section {
            text-align: center;
            margin-bottom: 35px;
        }
        
        .brand-logo {
            font-size: 2.5em;
            color: var(--accent-blue);
            margin-bottom: 12px;
        }
        
        .brand-title {
            font-size: 2em;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 6px;
        }
        
        .brand-subtitle {
            color: var(--light-slate);
            font-size: 0.95em;
            font-weight: 400;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            color: var(--primary-dark);
            font-weight: 500;
            font-size: 0.92em;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .form-control {
            width: 100%;
            padding: 14px 16px;
            background: var(--pure-white);
            border: 2px solid var(--border-light);
            border-radius: 10px;
            color: var(--primary-dark);
            font-size: 1em;
            transition: all 0.2s ease;
            font-family: inherit;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .input-icon {
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-slate);
            font-size: 1.1em;
        }
        
        .btn {
            background: var(--blue-gradient);
            color: var(--pure-white);
            padding: 16px 32px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            font-family: inherit;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-secondary {
            background: transparent;
            border: 2px solid var(--accent-blue);
            color: var(--accent-blue);
        }
        
        .btn-secondary:hover {
            background: var(--accent-blue);
            color: var(--pure-white);
        }
        
        .auth-footer {
            text-align: center;
            margin-top: 28px;
            padding-top: 20px;
            border-top: 1px solid var(--border-light);
        }
        
        .footer-text {
            color: var(--light-slate);
            font-size: 0.88em;
            margin-bottom: 14px;
        }
        
        .security-indicator {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: var(--success);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.82em;
            font-weight: 500;
        }
        
        /* ================== لوحة التحكم الرئيسية ================== */
        .dashboard-header {
            background: var(--pure-white);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-light);
            position: relative;
            width: 100%;
        }
        
        .header-content h1 {
            font-size: 2.3em;
            font-weight: 700;
            color: var(--primary-dark);
            margin-bottom: 10px;
        }
        
        .header-content p {
            font-size: 1.05em;
            color: var(--light-slate);
            font-weight: 400;
        }
        
        .user-nav {
            position: absolute;
            left: 30px;
            top: 30px;
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            padding: 10px 18px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-sm);
        }
        
        .admin-badge {
            background: var(--accent-emerald);
            color: var(--pure-white);
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 0.75em;
            font-weight: 600;
        }
        
        .nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 35px;
            width: 100%;
        }
        
        .nav-card {
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
        }
        
        .nav-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--accent-blue);
        }
        
        .nav-card i {
            font-size: 2.5em;
            margin-bottom: 18px;
            color: var(--accent-blue);
        }
        
        .nav-card h3 {
            font-size: 1.3em;
            margin-bottom: 10px;
            color: var(--primary-dark);
            font-weight: 600;
        }
        
        .nav-card p {
            color: var(--light-slate);
            font-size: 0.92em;
            line-height: 1.6;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin: 30px 0;
            width: 100%;
        }
        
        .stat-card {
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            border-radius: 14px;
            padding: 25px;
            text-align: center;
            box-shadow: var(--shadow-sm);
            width: 100%;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: 700;
            margin: 12px 0;
            color: var(--primary-dark);
        }
        
        .stat-card p {
            font-size: 0.95em;
            color: var(--light-slate);
            font-weight: 500;
        }
        
        .alert {
            padding: 18px 22px;
            border-radius: 12px;
            margin: 18px 0;
            text-align: center;
            font-weight: 500;
            border: 1px solid;
            font-size: 0.95em;
            width: 100%;
        }
        
        .alert-success {
            background: rgba(16, 185, 129, 0.1);
            border-color: var(--success);
            color: var(--success);
        }
        
        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            border-color: var(--error);
            color: var(--error);
        }
        
        .alert-info {
            background: rgba(37, 99, 235, 0.1);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
        }
        
        .content-section {
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            border-radius: 14px;
            padding: 25px;
            margin: 22px 0;
            box-shadow: var(--shadow-sm);
            width: 100%;
        }
        
        /* ================== نماذج الفواتير ================== */
        .invoice-form {
            background: var(--pure-white);
            border-radius: 14px;
            padding: 30px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-light);
            width: 100%;
        }
        
        .form-section {
            margin-bottom: 30px;
            padding-bottom: 25px;
            border-bottom: 1px solid var(--border-light);
        }
        
        .form-section:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }
        
        .section-title {
            font-size: 1.25em;
            font-weight: 600;
            color: var(--primary-dark);
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .services-table {
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
        }
        
        .services-table th,
        .services-table td {
            padding: 10px 12px;
            text-align: right;
            border-bottom: 1px solid var(--border-light);
        }
        
        .services-table th {
            background: var(--light-gray);
            font-weight: 600;
            color: var(--primary-dark);
        }
        
        .service-row:hover {
            background: var(--light-gray);
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 22px;
            flex-wrap: wrap;
        }
        
        /* ================== التصميم المتجاوب ================== */
        @media (max-width: 1200px) {
            .professional-container {
                padding: 18px;
            }
        }
        
        @media (max-width: 768px) {
            .professional-container {
                padding: 15px;
            }
            
            .auth-card {
                padding: 30px 20px;
                margin: 10px;
            }
            
            .dashboard-header {
                padding: 20px;
            }
            
            .header-content h1 {
                font-size: 1.8em;
            }
            
            .user-nav {
                position: relative;
                left: auto;
                top: auto;
                margin-bottom: 15px;
                justify-content: center;
                width: 100%;
            }
            
            .nav-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .invoice-form {
                padding: 20px;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .nav-card, .stat-card {
                padding: 20px;
            }
            
            .content-section {
                padding: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .professional-container {
                padding: 10px;
            }
            
            .auth-card {
                padding: 25px 15px;
            }
            
            .brand-title {
                font-size: 1.7em;
            }
            
            .dashboard-header {
                padding: 15px;
            }
            
            .header-content h1 {
                font-size: 1.6em;
            }
            
            .nav-card h3 {
                font-size: 1.2em;
            }
            
            .stat-number {
                font-size: 2em;
            }
            
            .btn {
                padding: 14px 20px;
                font-size: 0.95em;
            }
        }
        
        /* أنماط إضافية للعملاء */
        .clients-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }
        
        .client-card {
            background: var(--pure-white);
            border: 1px solid var(--border-light);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
        }
        
        .client-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .client-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .client-header h3 {
            margin: 0;
            color: var(--primary-dark);
        }
        
        .client-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .client-badge.شركة { background: var(--accent-blue); color: white; }
        .client-badge.فرد { background: var(--accent-teal); color: white; }
        .client-badge.حكومي { background: var(--accent-emerald); color: white; }
        
        .client-info p {
            margin: 8px 0;
            color: var(--light-slate);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .client-actions {
            display: flex;
            gap: 8px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border-light);
        }
        
        .btn-action {
            padding: 8px 12px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: var(--light-gray);
            color: var(--primary-dark);
        }
        
        .btn-action:hover {
            background: var(--accent-blue);
            color: white;
        }
        
        .btn-action.delete:hover {
            background: var(--error);
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--light-slate);
            grid-column: 1 / -1;
        }
        
        .empty-state i {
            margin-bottom: 20px;
            color: var(--border-light);
        }
        
        /* أنماط المودال */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: var(--pure-white);
            margin: 5% auto;
            padding: 0;
            border-radius: 12px;
            width: 90%;
            max-width: 700px;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            padding: 20px 25px;
            border-bottom: 1px solid var(--border-light);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .modal-body {
            padding: 25px;
        }
        
        .modal-footer {
            padding: 20px 25px;
            border-top: 1px solid var(--border-light);
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        .close {
            color: var(--light-slate);
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: var(--primary-dark);
        }
    </style>
</head>
<body>
    {% if not is_auth_page %}
    <div class="professional-container">
        {% if session.user_logged_in %}
        <div class="user-nav">
            {% if session.user_type == 'admin' %}
            <span class="admin-badge">مدير النظام</span>
            {% endif %}
            <i class="fas fa-user-circle"></i> {{ session.username }}
            | <a href="/profile" style="color: var(--accent-blue); margin: 0 10px;">الملف الشخصي</a>
            | <a href="/logout" style="color: var(--light-slate);">تسجيل خروج</a>
        </div>
        {% endif %}
        
        <div class="dashboard-header">
            <div class="header-content">
                <h1><i class="fas fa-file-invoice"></i> InvoiceFlow Pro</h1>
                <p>نظام إدارة الفواتير الاحترافي - إصدار Enterprise</p>
                <p>⏰ وقت التشغيل: {{ uptime }}</p>
            </div>
        </div>
        
        {% if session.user_logged_in %}
        <div class="nav-grid">
            <a href="/" class="nav-card">
                <i class="fas fa-home"></i>
                <h3>لوحة التحكم</h3>
                <p>نظرة عامة على الإحصائيات والأداء</p>
            </a>
            <a href="/invoices" class="nav-card">
                <i class="fas fa-receipt"></i>
                <h3>الفواتير</h3>
                <p>إدارة وعرض وتحرير جميع الفواتير</p>
            </a>
            <a href="/invoices/create" class="nav-card">
                <i class="fas fa-plus-circle"></i>
                <h3>فاتورة جديدة</h3>
                <p>إنشاء فاتورة احترافية جديدة</p>
            </a>
            <a href="/clients" class="nav-card">
                <i class="fas fa-users"></i>
                <h3>العملاء</h3>
                <p>إدارة قاعدة بيانات العملاء</p>
            </a>
            {% if session.user_type == 'admin' %}
            <a href="/admin" class="nav-card">
                <i class="fas fa-cog"></i>
                <h3>الإدارة</h3>
                <p>إعدادات النظام المتقدمة</p>
            </a>
            {% endif %}
            <a href="/reports" class="nav-card">
                <i class="fas fa-chart-bar"></i>
                <h3>التقارير</h3>
                <p>تقارير وتحليلات مالية متقدمة</p>
            </a>
        </div>
        {% endif %}

        {{ content | safe }}
    </div>
    {% else %}
    <div class="auth-wrapper">
        {{ content | safe }}
    </div>
    {% endif %}

    <script>
        // تأثيرات الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            // تأثيرات الكروت
            const cards = document.querySelectorAll('.nav-card, .stat-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
            });
            
            // تأثيرات الأزرار
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-1px)';
                });
                btn.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>
</body>
</html>
"""

# ================== Routes الاحترافية ==================
@app.route('/')
def dashboard():
    """لوحة التحكم الرئيسية"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = invoice_manager.get_user_stats(session['username'])
    
    # الذكاء الاصطناعي - الترحيب الذكي
    ai_welcome = invoice_ai.smart_welcome(session['username'])
    
    # ✅ الإصلاح: فصل المنطق الشرطي عن f-string
    admin_button = ''
    if session.get('user_type') == 'admin':
        admin_button = '''
        <a href="/admin" class="btn" style="background: var(--accent-teal);">
            <i class="fas fa-cog"></i> لوحة الإدارة
        </a>
        '''
    
    content = f"""
    {ai_welcome}
    
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-receipt" style="color: var(--accent-blue);"></i>
            <div class="stat-number" data-target="{stats['total_invoices']}">{stats['total_invoices']}</div>
            <p>إجمالي الفواتير</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign" style="color: var(--accent-emerald);"></i>
            <div class="stat-number" data-target="{int(stats['total_revenue'])}">${stats['total_revenue']:,.0f}</div>
            <p>إجمالي الإيرادات</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-clock" style="color: var(--warning);"></i>
            <div class="stat-number" data-target="{stats['pending_invoices']}">{stats['pending_invoices']}</div>
            <p>فواتير معلقة</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-check-circle" style="color: var(--success);"></i>
            <div class="stat-number" data-target="{int(stats['paid_amount'])}">${stats['paid_amount']:,.0f}</div>
            <p>المسدد</p>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-top: 35px;">
        <div class="content-section">
            <h3 style="margin-bottom: 18px; color: var(--primary-dark);">
                <i class="fas fa-bolt"></i> إجراءات سريعة
            </h3>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <a href="/invoices/create" class="btn">
                    <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
                </a>
                <a href="/invoices" class="btn btn-secondary">
                    <i class="fas fa-list"></i> عرض جميع الفواتير
                </a>
                {admin_button}
            </div>
        </div>
        
        <div class="content-section">
            <h3 style="margin-bottom: 18px; color: var(--primary-dark);">
                <i class="fas fa-chart-line"></i> نظرة سريعة
            </h3>
            <div style="color: var(--light-slate); line-height: 2;">
                <p>📈 {stats['total_invoices']} فاتورة تم إنشاؤها</p>
                <p>💰 ${stats['total_revenue']:,.2f} إجمالي الإيرادات</p>
                <p>⏳ {stats['pending_invoices']} فاتورة قيد المعالجة</p>
                <p>✅ ${stats['paid_amount']:,.2f} تم تحصيلها</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(PROFESSIONAL_DESIGN, title="InvoiceFlow Pro - لوحة التحكم", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        is_valid, user_role, email, full_name, company_name, plan_type, username = user_manager.authenticate_user(identifier, password)
        
        if is_valid:
            session['user_logged_in'] = True
            session['username'] = username
            session['user_type'] = user_role
            session['email'] = email
            session['full_name'] = full_name
            session['company_name'] = company_name
            session['plan_type'] = plan_type
            session.permanent = True
            
            return redirect(url_for('dashboard'))
        else:
            auth_content = """
            <div class="auth-card">
                <div class="brand-section">
                    <div class="brand-logo">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <div class="brand-title">InvoiceFlow Pro</div>
                    <div class="brand-subtitle">نظام إدارة الفواتير الاحترافي</div>
                </div>
                
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i> بيانات الدخول غير صحيحة
                </div>
                
                <form method="POST">
                    <div class="form-group">
                        <label class="form-label">اسم المستخدم أو البريد الإلكتروني</label>
                        <div class="input-wrapper">
                            <input type="text" name="identifier" class="form-control" placeholder="أدخل اسم المستخدم أو البريد الإلكتروني" required>
                            <div class="input-icon">
                                <i class="fas fa-user"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">كلمة المرور</label>
                        <div class="input-wrapper">
                            <input type="password" name="password" class="form-control" placeholder="أدخل كلمة المرور" required>
                            <div class="input-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">
                        <i class="fas fa-sign-in-alt"></i> تسجيل الدخول
                    </button>
                </form>
                
                <div class="auth-footer">
                    <div class="footer-text">ليس لديك حساب؟ سجل الآن</div>
                    <a href="/register" class="btn btn-secondary">
                        <i class="fas fa-user-plus"></i> إنشاء حساب جديد
                    </a>
                    <div class="security-indicator">
                        <i class="fas fa-shield-alt"></i>
                        اتصال آمن ومشفر
                    </div>
                </div>
            </div>
            """
            return render_template_string(PROFESSIONAL_DESIGN, title="تسجيل الدخول - InvoiceFlow Pro", 
                                        content=auth_content, is_auth_page=True)
    
    if 'user_logged_in' in session:
        return redirect(url_for('dashboard'))
    
    auth_content = """
    <div class="auth-card">
        <div class="brand-section">
            <div class="brand-logo">
                <i class="fas fa-file-invoice"></i>
            </div>
            <div class="brand-title">InvoiceFlow Pro</div>
            <div class="brand-subtitle">نظام إدارة الفواتير الاحترافي</div>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">اسم المستخدم أو البريد الإلكتروني</label>
                <div class="input-wrapper">
                    <input type="text" name="identifier" class="form-control" placeholder="أدخل اسم المستخدم أو البريد الإلكتروني" required>
                    <div class="input-icon">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">كلمة المرور</label>
                <div class="input-wrapper">
                    <input type="password" name="password" class="form-control" placeholder="أدخل كلمة المرور" required>
                    <div class="input-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-sign-in-alt"></i> تسجيل الدخول
            </button>
        </form>
        
        <div class="auth-footer">
            <div class="footer-text">ليس لديك حساب؟ سجل الآن</div>
            <a href="/register" class="btn btn-secondary">
                <i class="fas fa-user-plus"></i> إنشاء حساب جديد
            </a>
            <div class="security-indicator">
                <i class="fas fa-shield-alt"></i>
                اتصال آمن ومشفر
            </div>
        </div>
    </div>
    """
    return render_template_string(PROFESSIONAL_DESIGN, title="تسجيل الدخول - InvoiceFlow Pro", 
                                content=auth_content, is_auth_page=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['full_name']
        company_name = request.form.get('company_name', '')
        phone = request.form.get('phone', '')
        
        if password != confirm_password:
            auth_content = """
            <div class="auth-card">
                <div class="brand-section">
                    <div class="brand-logo">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <div class="brand-title">InvoiceFlow Pro</div>
                    <div class="brand-subtitle">انضم إلينا اليوم</div>
                </div>
                
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i> كلمات المرور غير متطابقة
                </div>
                
                <form method="POST">
                    <div class="form-group">
                        <label class="form-label">اسم المستخدم</label>
                        <input type="text" name="username" class="form-control" placeholder="اختر اسم مستخدم فريد" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">البريد الإلكتروني</label>
                        <input type="email" name="email" class="form-control" placeholder="example@company.com" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">كلمة المرور</label>
                        <input type="password" name="password" class="form-control" placeholder="كلمة مرور قوية (8 أحرف على الأقل)" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">تأكيد كلمة المرور</label>
                        <input type="password" name="confirm_password" class="form-control" placeholder="أعد إدخال كلمة المرور" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">الاسم الكامل</label>
                        <input type="text" name="full_name" class="form-control" placeholder="الاسم الثلاثي" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">اسم الشركة (اختياري)</label>
                        <input type="text" name="company_name" class="form-control" placeholder="اسم شركتك">
                    </div>
                    
                    <button type="submit" class="btn">
                        <i class="fas fa-user-plus"></i> إنشاء حساب
                    </button>
                </form>
                
                <div class="auth-footer">
                    <a href="/login" class="btn btn-secondary">
                        <i class="fas fa-arrow-right"></i> لديك حساب؟ سجل الدخول
                    </a>
                </div>
            </div>
            """
            return render_template_string(PROFESSIONAL_DESIGN, title="التسجيل - InvoiceFlow Pro", 
                                        content=auth_content, is_auth_page=True)
        
        success, message = user_manager.register_user(username, email, password, full_name, company_name, phone)
        
        if success:
            auth_content = f"""
            <div class="auth-card">
                <div class="brand-section">
                    <div class="brand-logo">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <div class="brand-title">InvoiceFlow Pro</div>
                    <div class="brand-subtitle">انضم إلينا اليوم</div>
                </div>
                
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> {message}
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/login" class="btn">
                        <i class="fas fa-sign-in-alt"></i> الانتقال لتسجيل الدخول
                    </a>
                </div>
            </div>
            """
            return render_template_string(PROFESSIONAL_DESIGN, title="تم التسجيل - InvoiceFlow Pro", 
                                        content=auth_content, is_auth_page=True)
        else:
            auth_content = f"""
            <div class="auth-card">
                <div class="brand-section">
                    <div class="brand-logo">
                        <i class="fas fa-file-invoice"></i>
                    </div>
                    <div class="brand-title">InvoiceFlow Pro</div>
                    <div class="brand-subtitle">انضم إلينا اليوم</div>
                </div>
                
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i> {message}
                </div>
                
                <form method="POST">
                    <div class="form-group">
                        <label class="form-label">اسم المستخدم</label>
                        <input type="text" name="username" class="form-control" placeholder="اختر اسم مستخدم فريد" value="{username}" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">البريد الإلكتروني</label>
                        <input type="email" name="email" class="form-control" placeholder="example@company.com" value="{email}" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">كلمة المرور</label>
                        <input type="password" name="password" class="form-control" placeholder="كلمة مرور قوية (8 أحرف على الأقل)" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">تأكيد كلمة المرور</label>
                        <input type="password" name="confirm_password" class="form-control" placeholder="أعد إدخال كلمة المرور" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">الاسم الكامل</label>
                        <input type="text" name="full_name" class="form-control" placeholder="الاسم الثلاثي" value="{full_name}" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">اسم الشركة (اختياري)</label>
                        <input type="text" name="company_name" class="form-control" placeholder="اسم شركتك" value="{company_name}">
                    </div>
                    
                    <button type="submit" class="btn">
                        <i class="fas fa-user-plus"></i> إنشاء حساب
                    </button>
                </form>
                
                <div class="auth-footer">
                    <a href="/login" class="btn btn-secondary">
                        <i class="fas fa-arrow-right"></i> لديك حساب؟ سجل الدخول
                    </a>
                </div>
            </div>
            """
            return render_template_string(PROFESSIONAL_DESIGN, title="التسجيل - InvoiceFlow Pro", 
                                        content=auth_content, is_auth_page=True)
    
    auth_content = """
    <div class="auth-card">
        <div class="brand-section">
            <div class="brand-logo">
                <i class="fas fa-file-invoice"></i>
            </div>
            <div class="brand-title">InvoiceFlow Pro</div>
            <div class="brand-subtitle">انضم إلينا اليوم</div>
        </div>
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">اسم المستخدم</label>
                <input type="text" name="username" class="form-control" placeholder="اختر اسم مستخدم فريد" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">البريد الإلكتروني</label>
                <input type="email" name="email" class="form-control" placeholder="example@company.com" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">كلمة المرور</label>
                <input type="password" name="password" class="form-control" placeholder="كلمة مرور قوية (8 أحرف على الأقل)" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">تأكيد كلمة المرور</label>
                <input type="password" name="confirm_password" class="form-control" placeholder="أعد إدخال كلمة المرور" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">الاسم الكامل</label>
                <input type="text" name="full_name" class="form-control" placeholder="الاسم الثلاثي" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">اسم الشركة (اختياري)</label>
                <input type="text" name="company_name" class="form-control" placeholder="اسم شركتك">
            </div>
            
            <button type="submit" class="btn">
                <i class="fas fa-user-plus"></i> إنشاء حساب
            </button>
        </form>
        
        <div class="auth-footer">
            <a href="/login" class="btn btn-secondary">
                <i class="fas fa-arrow-right"></i> لديك حساب؟ سجل الدخول
            </a>
        </div>
    </div>
    """
    return render_template_string(PROFESSIONAL_DESIGN, title="التسجيل - InvoiceFlow Pro", 
                                content=auth_content, is_auth_page=True)

@app.route('/invoices/create', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة مع التصميم المحسن"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # معالجة بيانات الفاتورة
        client_name = request.form['client_name']
        client_email = request.form.get('client_email', '')
        client_phone = request.form.get('client_phone', '')
        client_address = request.form.get('client_address', '')
        issue_date = request.form.get('issue_date', datetime.now().strftime('%Y-%m-%d'))
        due_date = request.form.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        tax_rate = float(request.form.get('tax_rate', 15))
        payment_terms = request.form.get('payment_terms', '30 يوم')
        notes = request.form.get('notes', '')
        
        # معالجة الخدمات
        services = []
        subtotal = 0
        
        service_names = request.form.getlist('service_name')
        service_descs = request.form.getlist('service_desc')
        service_qtys = request.form.getlist('service_qty')
        service_prices = request.form.getlist('service_price')
        
        for i in range(len(service_names)):
            if service_names[i].strip():
                quantity = float(service_qtys[i]) if service_qtys[i] else 1
                price = float(service_prices[i]) if service_prices[i] else 0
                total = quantity * price
                subtotal += total
                
                services.append({
                    'name': service_names[i],
                    'description': service_descs[i] if i < len(service_descs) else '',
                    'quantity': quantity,
                    'price': price,
                    'total': total
                })
        
        tax_amount = subtotal * (tax_rate / 100)
        total_amount = subtotal + tax_amount
        
        invoice_data = {
            'user_id': session['username'],
            'client_name': client_name,
            'client_email': client_email,
            'client_phone': client_phone,
            'client_address': client_address,
            'issue_date': issue_date,
            'due_date': due_date,
            'services': services,
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'payment_terms': payment_terms,
            'notes': notes,
            'status': 'مسودة',
            'company_name': session.get('company_name', 'InvoiceFlow Pro')
        }
        
        success, invoice_number, message = invoice_manager.create_invoice(invoice_data)
        
        if success:
            # 🎨 إنشاء PDF احترافي
            invoice_data['invoice_number'] = invoice_number
            pdf_buffer = pdf_generator.create_professional_invoice(invoice_data)
            
            if pdf_buffer:
                return send_file(
                    pdf_buffer, 
                    as_attachment=True, 
                    download_name=f'Invoice_{invoice_number}.pdf',
                    mimetype='application/pdf'
                )
            else:
                # عرض رسالة نجاح إذا لم يتم إنشاء PDF
                content = f"""
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> {message}
                </div>
                <div class="alert alert-info">
                    <i class="fas fa-file-pdf"></i> تم إنشاء الفاتورة بنجاح! رقم الفاتورة: {invoice_number}
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="/invoices" class="btn">عرض جميع الفواتير</a>
                    <a href="/invoices/create" class="btn btn-secondary">فاتورة جديدة</a>
                    <a href="/invoices/download/{invoice_number}" class="btn" style="background: var(--accent-teal);">
                        <i class="fas fa-download"></i> تحميل PDF
                    </a>
                </div>
                """
        else:
            content = f"""
            <div class="alert alert-error">
                <i class="fas fa-exclamation-circle"></i> {message}
            </div>
            """
            
        uptime = time.time() - monitor.uptime_start
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        uptime_str = f"{hours} ساعة {minutes} دقيقة"
        
        return render_template_string(PROFESSIONAL_DESIGN, title="إنشاء فاتورة - InvoiceFlow Pro", 
                                    uptime=uptime_str, content=content, is_auth_page=False)
    
    else:
        # عرض نموذج إنشاء الفاتورة
        content = """
        <div class="invoice-form">
            <h2 style="margin-bottom: 25px; color: var(--primary-dark);">
                <i class="fas fa-plus-circle"></i> إنشاء فاتورة جديدة
            </h2>
            
            <form method="POST" id="invoiceForm">
                <div class="form-section">
                    <div class="section-title">
                        <i class="fas fa-user"></i> معلومات العميل
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div class="form-group">
                            <label class="form-label">اسم العميل *</label>
                            <input type="text" name="client_name" class="form-control" placeholder="اسم العميل الكامل" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">البريد الإلكتروني</label>
                            <input type="email" name="client_email" class="form-control" placeholder="email@example.com">
                        </div>
                        <div class="form-group">
                            <label class="form-label">رقم الهاتف</label>
                            <input type="tel" name="client_phone" class="form-control" placeholder="+966500000000">
                        </div>
                        <div class="form-group">
                            <label class="form-label">العنوان</label>
                            <textarea name="client_address" class="form-control" placeholder="عنوان العميل" rows="2"></textarea>
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <div class="section-title">
                        <i class="fas fa-calendar"></i> تفاصيل الفاتورة
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
                        <div class="form-group">
                            <label class="form-label">تاريخ الإصدار</label>
                            <input type="date" name="issue_date" class="form-control" value="{{ today }}">
                        </div>
                        <div class="form-group">
                            <label class="form-label">تاريخ الاستحقاق</label>
                            <input type="date" name="due_date" class="form-control" value="{{ due_date }}">
                        </div>
                        <div class="form-group">
                            <label class="form-label">نسبة الضريبة (%)</label>
                            <input type="number" name="tax_rate" class="form-control" value="15" step="0.1" min="0" max="100" onchange="calculateTotal()">
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <div class="section-title">
                        <i class="fas fa-list"></i> الخدمات والمنتجات
                        <button type="button" class="btn" onclick="addService()" style="padding: 8px 16px; font-size: 0.9em;">
                            <i class="fas fa-plus"></i> إضافة خدمة
                        </button>
                    </div>
                    
                    <div style="overflow-x: auto;">
                        <table class="services-table">
                            <thead>
                                <tr>
                                    <th>الخدمة</th>
                                    <th>الوصف</th>
                                    <th>الكمية</th>
                                    <th>السعر</th>
                                    <th>المجموع</th>
                                    <th>إجراءات</th>
                                </tr>
                            </thead>
                            <tbody id="servicesBody">
                                <tr class="service-row">
                                    <td><input type="text" class="form-control" name="service_name" placeholder="اسم الخدمة" required onchange="calculateTotal()"></td>
                                    <td><textarea class="form-control" name="service_desc" placeholder="وصف الخدمة" rows="2"></textarea></td>
                                    <td><input type="number" class="form-control" name="service_qty" value="1" min="1" required onchange="calculateTotal()"></td>
                                    <td><input type="number" class="form-control" name="service_price" placeholder="0.00" step="0.01" required onchange="calculateTotal()"></td>
                                    <td><span class="service-total">0.00</span></td>
                                    <td><button type="button" class="btn" onclick="removeService(this)" style="background: var(--error); padding: 8px 12px;"><i class="fas fa-trash"></i></button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="form-section">
                    <div class="section-title">
                        <i class="fas fa-calculator"></i> الإجماليات
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; max-width: 400px; margin: 0 auto; background: var(--light-gray); padding: 20px; border-radius: 10px;">
                        <div style="text-align: left; font-weight: 500;">المجموع الفرعي:</div>
                        <div style="text-align: right; font-weight: 600;" id="subtotal">0.00</div>
                        
                        <div style="text-align: left; font-weight: 500;">الضريبة:</div>
                        <div style="text-align: right; font-weight: 600;" id="tax_amount">0.00</div>
                        
                        <div style="text-align: left; font-size: 1.1em; font-weight: 600;">الإجمالي النهائي:</div>
                        <div style="text-align: right; font-size: 1.1em; font-weight: 700; color: var(--accent-blue);" id="total_amount">0.00</div>
                    </div>
                </div>
                
                <div class="form-section">
                    <div class="section-title">
                        <i class="fas fa-file-alt"></i> ملاحظات إضافية
                    </div>
                    <div class="form-group">
                        <label class="form-label">شروط الدفع</label>
                        <input type="text" name="payment_terms" class="form-control" value="30 يوم" placeholder="شروط الدفع">
                    </div>
                    <div class="form-group">
                        <label class="form-label">ملاحظات</label>
                        <textarea name="notes" class="form-control" placeholder="ملاحظات إضافية للفاتورة" rows="3"></textarea>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button type="submit" class="btn">
                        <i class="fas fa-save"></i> حفظ وإنشاء الفاتورة
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="addService()">
                        <i class="fas fa-plus"></i> إضافة خدمة أخرى
                    </button>
                    <button type="reset" class="btn" style="background: var(--light-slate);">
                        <i class="fas fa-redo"></i> إعادة تعيين
                    </button>
                </div>
            </form>
        </div>
        
        <script>
            let serviceCounter = 1;
            
            function addService() {
                serviceCounter++;
                const tbody = document.getElementById('servicesBody');
                const newRow = document.createElement('tr');
                newRow.className = 'service-row';
                newRow.innerHTML = `
                    <td><input type="text" class="form-control" name="service_name" placeholder="اسم الخدمة" onchange="calculateTotal()"></td>
                    <td><textarea class="form-control" name="service_desc" placeholder="وصف الخدمة" rows="2"></textarea></td>
                    <td><input type="number" class="form-control" name="service_qty" value="1" min="1" onchange="calculateTotal()"></td>
                    <td><input type="number" class="form-control" name="service_price" placeholder="0.00" step="0.01" onchange="calculateTotal()"></td>
                    <td><span class="service-total">0.00</span></td>
                    <td><button type="button" class="btn" onclick="removeService(this)" style="background: var(--error); padding: 8px 12px;"><i class="fas fa-trash"></i></button></td>
                `;
                tbody.appendChild(newRow);
            }
            
            function removeService(button) {
                if (document.querySelectorAll('.service-row').length > 1) {
                    button.closest('tr').remove();
                    calculateTotal();
                } else {
                    alert('يجب أن تحتوي الفاتورة على خدمة واحدة على الأقل');
                }
            }
            
            function calculateTotal() {
                let subtotal = 0;
                
                document.querySelectorAll('.service-row').forEach((row, index) => {
                    const qtyInput = row.querySelector('[name="service_qty"]');
                    const priceInput = row.querySelector('[name="service_price"]');
                    const totalSpan = row.querySelector('.service-total');
                    
                    const qty = parseFloat(qtyInput.value) || 0;
                    const price = parseFloat(priceInput.value) || 0;
                    const total = qty * price;
                    
                    totalSpan.textContent = total.toFixed(2);
                    subtotal += total;
                });
                
                const taxRate = parseFloat(document.querySelector('[name="tax_rate"]').value) || 0;
                const taxAmount = subtotal * (taxRate / 100);
                const total = subtotal + taxAmount;
                
                document.getElementById('subtotal').textContent = subtotal.toFixed(2);
                document.getElementById('tax_amount').textContent = taxAmount.toFixed(2);
                document.getElementById('total_amount').textContent = total.toFixed(2);
            }
            
            // حساب أولي عند التحميل
            document.addEventListener('DOMContentLoaded', function() {
                calculateTotal();
                
                // تحديث الحساب عند أي تغيير
                document.querySelectorAll('input, textarea').forEach(element => {
                    element.addEventListener('input', calculateTotal);
                });
            });
        </script>
        """.replace("{{ today }}", datetime.now().strftime('%Y-%m-%d')).replace("{{ due_date }}", (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="إنشاء فاتورة - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/invoices')
def list_invoices():
    """عرض جميع الفواتير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    invoices = invoice_manager.get_user_invoices(session['username'])
    
    invoices_html = ""
    for invoice in invoices:
        status_color = 'var(--success)' if invoice['status'] == 'مسددة' else 'var(--warning)' if invoice['status'] == 'معلقة' else 'var(--light-slate)'
        payment_color = 'var(--success)' if invoice['payment_status'] == 'مدفوع' else 'var(--error)'
        invoices_html += f"""
        <div class="content-section" style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin-bottom: 5px;">فاتورة {invoice['number']}</h4>
                    <p style="color: var(--light-slate); margin: 0;">العميل: {invoice['client']}</p>
                </div>
                <div style="text-align: left;">
                    <div style="font-weight: 600; color: var(--accent-blue);">${invoice['amount']:,.2f}</div>
                    <div style="color: {status_color}; font-size: 0.9em;">{invoice['status']}</div>
                    <div style="color: {payment_color}; font-size: 0.8em;">{invoice['payment_status']}</div>
                    <div style="color: var(--light-slate); font-size: 0.8em;">{invoice['issue_date']}</div>
                </div>
            </div>
            <div style="margin-top: 10px; display: flex; gap: 10px;">
                <a href="/invoices/download/{invoice['number']}" class="btn" style="padding: 8px 12px; font-size: 0.8em;">
                    <i class="fas fa-download"></i> تحميل PDF
                </a>
            </div>
        </div>
        """
    
    content = f"""
    <div class="dashboard-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-receipt"></i> إدارة الفواتير
        </h2>
    </div>
    
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
        <h3 style="color: var(--primary-dark);">الفواتير ({len(invoices)})</h3>
        <a href="/invoices/create" class="btn">
            <i class="fas fa-plus"></i> فاتورة جديدة
        </a>
    </div>
    
    {invoices_html if invoices else '<div class="alert">لا توجد فواتير حتى الآن</div>'}
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="الفواتير - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/invoices/download/<invoice_number>')
def download_invoice(invoice_number):
    """تحميل فاتورة PDF"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM invoices WHERE invoice_number = ? AND user_id = ?
        ''', (invoice_number, session['username']))
        
        result = cursor.fetchone()
        if result:
            # إعادة إنشاء بيانات الفاتورة
            invoice_data = {
                'invoice_number': result['invoice_number'],
                'client_name': result['client_name'],
                'client_email': result['client_email'],
                'client_phone': result['client_phone'],
                'client_address': result['client_address'],
                'issue_date': result['issue_date'],
                'due_date': result['due_date'],
                'services': json.loads(result['services_json']),
                'subtotal': result['subtotal'],
                'tax_rate': result['tax_rate'],
                'tax_amount': result['tax_amount'],
                'total_amount': result['total_amount'],
                'payment_terms': result['payment_terms'],
                'notes': result['notes'],
                'status': result['status'],
                'company_name': result['company_name'] or session.get('company_name', 'InvoiceFlow Pro')
            }
            
            pdf_buffer = pdf_generator.create_professional_invoice(invoice_data)
            
            if pdf_buffer:
                return send_file(
                    pdf_buffer,
                    as_attachment=True,
                    download_name=f'Invoice_{invoice_number}.pdf',
                    mimetype='application/pdf'
                )
        
        conn.close()
        return "الفاتورة غير موجودة", 404
        
    except Exception as e:
        print(f"❌ خطأ في تحميل الفاتورة: {e}")
        return "خطأ في تحميل الفاتورة", 500

@app.route('/clients', methods=['GET', 'POST'])
def clients_management():
    """نظام إدارة العملاء المتكامل"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # إضافة عميل جديد
        name = request.form['name']
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        company_name = request.form.get('company_name', '')
        tax_number = request.form.get('tax_number', '')
        category = request.form.get('category', 'عام')
        payment_terms = request.form.get('payment_terms', '30 يوم')
        notes = request.form.get('notes', '')
        
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clients 
                (user_id, name, email, phone, address, company_name, tax_number, category, payment_terms, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['username'], name, email, phone, address, company_name, tax_number, category, payment_terms, notes))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'تم إضافة العميل بنجاح'})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'خطأ في إضافة العميل: {str(e)}'})
    
    # جلب العملاء
    clients = invoice_manager.get_user_clients(session['username'])
    
    # واجهة إدارة العملاء
    content = f"""
    <div class="dashboard-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1><i class="fas fa-users"></i> إدارة العملاء</h1>
                <p>إدارة قاعدة عملائك بكل سهولة واحترافية</p>
            </div>
            <button class="btn" onclick="showAddClientModal()">
                <i class="fas fa-plus"></i> إضافة عميل جديد
            </button>
        </div>
    </div>

    <div class="content-section">
        <div style="display: flex; gap: 15px; margin-bottom: 20px;">
            <input type="text" id="searchClients" class="form-control" placeholder="🔍 بحث في العملاء..." style="flex: 1;">
            <select id="filterCategory" class="form-control" style="width: 200px;">
                <option value="">جميع الفئات</option>
                <option value="شركة">شركة</option>
                <option value="فرد">فرد</option>
                <option value="حكومي">حكومي</option>
            </select>
        </div>

        <div class="clients-grid" id="clientsContainer">
            {"".join([f"""
            <div class="client-card" data-category="{client['category']}">
                <div class="client-header">
                    <h3>{client['name']}</h3>
                    <span class="client-badge {client['category']}">{client['category']}</span>
                </div>
                <div class="client-info">
                    <p><i class="fas fa-building"></i> {client['company_name'] or 'غير محدد'}</p>
                    <p><i class="fas fa-envelope"></i> {client['email'] or 'غير محدد'}</p>
                    <p><i class="fas fa-phone"></i> {client['phone'] or 'غير محدد'}</p>
                    <p><i class="fas fa-map-marker-alt"></i> {client['address'] or 'غير محدد'}</p>
                </div>
                <div class="client-actions">
                    <button class="btn-action" onclick="editClient({client['id']})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-action" onclick="createInvoiceForClient({client['id']})">
                        <i class="fas fa-file-invoice"></i>
                    </button>
                    <button class="btn-action delete" onclick="deleteClient({client['id']})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            """ for client in clients]) if clients else '''
            <div class="empty-state">
                <i class="fas fa-users fa-3x"></i>
                <h3>لا يوجد عملاء</h3>
                <p>ابدأ بإضافة عميلك الأول</p>
                <button class="btn" onclick="showAddClientModal()">
                    <i class="fas fa-plus"></i> إضافة عميل جديد
                </button>
            </div>
            '''}
        </div>
    </div>

    <!-- نموذج إضافة عميل -->
    <div id="addClientModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-user-plus"></i> إضافة عميل جديد</h3>
                <span class="close" onclick="closeAddClientModal()">&times;</span>
            </div>
            <form id="addClientForm" onsubmit="addClient(event)">
                <div class="modal-body">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div class="form-group">
                            <label class="form-label">اسم العميل *</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">البريد الإلكتروني</label>
                            <input type="email" name="email" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="form-label">رقم الهاتف</label>
                            <input type="tel" name="phone" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="form-label">اسم الشركة</label>
                            <input type="text" name="company_name" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="form-label">رقم الضريبي</label>
                            <input type="text" name="tax_number" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="form-label">الفئة</label>
                            <select name="category" class="form-control">
                                <option value="عام">عام</option>
                                <option value="شركة">شركة</option>
                                <option value="فرد">فرد</option>
                                <option value="حكومي">حكومي</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">العنوان</label>
                        <textarea name="address" class="form-control" rows="2"></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label">شروط الدفع</label>
                        <input type="text" name="payment_terms" class="form-control" value="30 يوم">
                    </div>
                    <div class="form-group">
                        <label class="form-label">ملاحظات</label>
                        <textarea name="notes" class="form-control" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeAddClientModal()">إلغاء</button>
                    <button type="submit" class="btn">حفظ العميل</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function showAddClientModal() {{
            document.getElementById('addClientModal').style.display = 'block';
        }}
        
        function closeAddClientModal() {{
            document.getElementById('addClientModal').style.display = 'none';
        }}
        
        async function addClient(event) {{
            event.preventDefault();
            const formData = new FormData(event.target);
            
            try {{
                const response = await fetch('/clients', {{
                    method: 'POST',
                    body: formData
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    closeAddClientModal();
                    alert(result.message);
                    setTimeout(() => location.reload(), 1000);
                }} else {{
                    alert(result.message);
                }}
            }} catch (error) {{
                alert('خطأ في الإتصال');
            }}
        }}
        
        // البحث والتصفية
        document.getElementById('searchClients').addEventListener('input', filterClients);
        document.getElementById('filterCategory').addEventListener('change', filterClients);
        
        function filterClients() {{
            const searchTerm = document.getElementById('searchClients').value.toLowerCase();
            const categoryFilter = document.getElementById('filterCategory').value;
            
            document.querySelectorAll('.client-card').forEach(card => {{
                const name = card.querySelector('h3').textContent.toLowerCase();
                const category = card.getAttribute('data-category');
                
                const matchesSearch = name.includes(searchTerm);
                const matchesCategory = !categoryFilter || category === categoryFilter;
                
                card.style.display = (matchesSearch && matchesCategory) ? 'block' : 'none';
            }});
        }}
        
        function editClient(clientId) {{
            alert('سيتم تنفيذ تعديل العميل في الإصدار القادم - العميل: ' + clientId);
        }}
        
        function createInvoiceForClient(clientId) {{
            alert('سيتم إنشاء فاتورة للعميل في الإصدار القادم - العميل: ' + clientId);
        }}
        
        function deleteClient(clientId) {{
            if (confirm('هل أنت متأكد من حذف هذا العميل؟')) {{
                alert('سيتم حذف العميل في الإصدار القادم - العميل: ' + clientId);
            }}
        }}
    </script>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="إدارة العملاء - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

# إضافة الروابط الأساسية المتبقية
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = invoice_manager.get_user_stats(session['username'])
    
    content = f"""
    <div class="dashboard-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-user-circle"></i> الملف الشخصي
        </h2>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-receipt"></i>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>الفواتير</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p>الإيرادات</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-clock"></i>
            <div class="stat-number">{stats['pending_invoices']}</div>
            <p>قيد المعالجة</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-crown"></i>
            <div class="stat-number">{session.get('plan_type', 'professional').title()}</div>
            <p>الخطة</p>
        </div>
    </div>
    
    <div class="content-section">
        <h3 style="margin-bottom: 25px; color: var(--primary-dark);">
            <i class="fas fa-id-card"></i> المعلومات الشخصية
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <p><strong>اسم المستخدم:</strong> {session['username']}</p>
                <p><strong>البريد الإلكتروني:</strong> {session['email']}</p>
                <p><strong>الاسم الكامل:</strong> {session['full_name']}</p>
                <p><strong>الشركة:</strong> {session.get('company_name', 'غير محدد')}</p>
            </div>
            <div>
                <p><strong>نوع الحساب:</strong> {session['user_type']}</p>
                <p><strong>الخطة:</strong> {session.get('plan_type', 'professional').title()}</p>
                <p><strong>حالة الحساب:</strong> <span style="color: var(--success);">نشط</span></p>
                <p><strong>تاريخ التسجيل:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(PROFESSIONAL_DESIGN, title="الملف الشخصي - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/admin')
def admin():
    if 'user_logged_in' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('dashboard'))
    
    content = """
    <div class="dashboard-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-cog"></i> لوحة الإدارة
        </h2>
        <p style="text-align: center; color: var(--light-slate);">قريباً... سيتم إضافة لوحة الإدارة المتكاملة</p>
    </div>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="الإدارة - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/reports')
def reports():
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    stats = invoice_manager.get_user_stats(session['username'])
    
    content = f"""
    <div class="dashboard-header">
        <h1><i class="fas fa-chart-bar"></i> التقارير والتحليلات</h1>
        <p>تحليلات متقدمة وإحصائيات مفصلة عن أدائك</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-receipt"></i>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>إجمالي الفواتير</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p>إجمالي الإيرادات</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-percentage"></i>
            <div class="stat-number">${stats['tax_amount']:,.0f}</div>
            <p>إجمالي الضرائب</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-trend-up"></i>
            <div class="stat-number">+15%</div>
            <p>نمو الإيرادات</p>
        </div>
    </div>

    <div class="content-section" style="margin-top: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3><i class="fas fa-table"></i> أحدث الفواتير</h3>
            <button class="btn" onclick="exportToExcel()">
                <i class="fas fa-download"></i> تصدير إلى Excel
            </button>
        </div>
        
        <div style="overflow-x: auto;">
            <table class="services-table">
                <thead>
                    <tr>
                        <th>رقم الفاتورة</th>
                        <th>العميل</th>
                        <th>التاريخ</th>
                        <th>المبلغ</th>
                        <th>الحالة</th>
                        <th>الحالة المالية</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f"""
                    <tr>
                        <td>{inv['number']}</td>
                        <td>{inv['client']}</td>
                        <td>{inv['issue_date']}</td>
                        <td>${inv['amount']:,.2f}</td>
                        <td><span class="status-badge {inv['status']}">{inv['status']}</span></td>
                        <td><span class="payment-badge {'مدفوع' if inv['payment_status'] == 'مدفوع' else 'غير مدفوع'}">{inv['payment_status']}</span></td>
                    </tr>
                    """ for inv in invoice_manager.get_user_invoices(session['username'])[:10]]) if invoice_manager.get_user_invoices(session['username']) else '''
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 20px;">لا توجد فواتير لعرضها</td>
                    </tr>
                    '''}
                </tbody>
            </table>
        </div>
    </div>

    <style>
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        
        .status-badge.مسددة {{ background: var(--success); color: white; }}
        .status-badge.معلقة {{ background: var(--warning); color: white; }}
        .status-badge.مسودة {{ background: var(--light-slate); color: white; }}
        
        .payment-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        
        .payment-badge.مدفوع {{ background: var(--success); color: white; }}
        .payment-badge.غير_مدفوع {{ background: var(--error); color: white; }}
    </style>

    <script>
        function exportToExcel() {{
            alert('سيتم تنفيذ تصدير Excel في الإصدار القادم');
        }}
    </script>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="التقارير - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

# ================== إعدادات التشغيل لـ Render ==================
def create_tables():
    """إنشاء الجداول عند التشغيل الأول"""
    try:
        user_manager.init_user_system()
        invoice_manager.init_invoice_system()
        print("✅ تم إنشاء الجداول بنجاح")
    except Exception as e:
        print(f"✅ الجداول موجودة مسبقاً: {e}")

# استدعاء إنشاء الجداول عند التشغيل
create_tables()

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل InvoiceFlow Pro المحسن...")
        print("🔧 تم إصلاح جميع المشاكل السابقة")
        print("📱 تصميم متجاوب يعمل على جميع الأجهزة")
        print("💾 قاعدة بيانات منظمة ومحسنة")
        print("🎯 النظام جاهز للتشغيل الكامل")
        print("")
        print("🔐 بيانات الدخول الافتراضية:")
        print("   👤 المستخدم: admin أو admin@invoiceflow.com")
        print("   🔑 كلمة المرور: Admin123!@#")
        print("")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ InvoiceFlow Pro - النظام النهائي المتكامل!")
        
        # التأكد من إنشاء الجداول
        create_tables()
        
        if 'RENDER' in os.environ:
            app.run(host='0.0.0.0', port=port, debug=False)
        else:
            app.run(host='0.0.0.0', port=port, debug=True)
            
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        time.sleep(5)
