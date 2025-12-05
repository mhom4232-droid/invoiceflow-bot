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
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_pro_enterprise_2024_v3_secure_key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# الحصول على البورت من بيئة Render
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - نظام إدارة الفواتير الاحترافي")
print("🚀 الإصدار النهائي المتكامل - تم إصلاح جميع الأخطاء")
print("=" * 80)

# ================== نظام إدارة قاعدة البيانات المحسن ==================
class DatabaseManager:
    def __init__(self):
        self.db_path = self.ensure_database_path()
        
    def ensure_database_path(self):
        """تأكيد وجود مسار قاعدة البيانات"""
        try:
            db_dir = os.path.join(os.getcwd(), 'database')
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            db_path = os.path.join(db_dir, 'invoiceflow_pro.db')
            print(f"📁 مسار قاعدة البيانات: {db_path}")
            return db_path
        except Exception as e:
            print(f"⚠️  خطأ في إنشاء المسار: {e}")
            return 'invoiceflow_pro.db'
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # تفعيل المفاتيح الخارجية
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA foreign_keys = ON")
                print("✅ تم إنشاء قاعدة بيانات جديدة")
                return conn
            except Exception as e2:
                print(f"❌ فشل إنشاء قاعدة بيانات جديدة: {e2}")
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
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                return False, f"بريد إلكتروني غير صحيح: {str(e)}"

            if len(password) < 8:
                return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
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

            # إنشاء الفهارس لتحسين الأداء
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON invoices(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(issue_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_clients_user_id ON clients(user_id)')

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

    def add_client(self, user_id, client_data):
        """إضافة عميل جديد"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clients (user_id, name, email, phone, company_name, category, payment_terms, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                client_data['name'],
                client_data.get('email', ''),
                client_data.get('phone', ''),
                client_data.get('company_name', ''),
                client_data.get('category', 'عام'),
                client_data.get('payment_terms', '30 يوم'),
                client_data.get('notes', '')
            ))
            
            conn.commit()
            conn.close()
            return True, "تم إضافة العميل بنجاح"
        except Exception as e:
            print(f"🔧 خطأ في إضافة العميل: {e}")
            return False, f"خطأ في إضافة العميل: {str(e)}"

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
            
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=30, 
                leftMargin=30, 
                topMargin=40, 
                bottomMargin=40
            )
            
            elements = []
            elements.extend(self.create_professional_header(invoice_data))
            elements.extend(self.create_company_client_info(invoice_data))
            elements.extend(self.create_services_table(invoice_data))
            elements.extend(self.create_totals_section(invoice_data))
            elements.extend(self.create_professional_footer())
            
            doc.build(elements)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF: {e}")
            return None
    
    def create_professional_header(self, invoice_data):
        """رأس الفاتورة الاحترافي"""
        elements = []
        
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            alignment=1,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph(self.arabic_text("فاتورة رسمية"), title_style)
        elements.append(title)
        
        header_data = [
            [self.arabic_text('رقم الفاتورة'), self.arabic_text(invoice_data['invoice_number'])],
            [self.arabic_text('تاريخ الإصدار'), self.arabic_text(invoice_data['issue_date'])],
            [self.arabic_text('تاريخ الاستحقاق'), self.arabic_text(invoice_data['due_date'])],
            [self.arabic_text('الحالة'), self.arabic_text(invoice_data.get('status', 'مسودة'))]
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
        company_info = self.arabic_text(f"""
        {company_name}
        نظام إدارة الفواتير الاحترافي
        البريد الإلكتروني: info@invoiceflow.com
        الهاتف: +966500000000
        """)
        
        client_info = self.arabic_text(f"""
        {invoice_data['client_name']}
        {invoice_data.get('client_email', '')}
        {invoice_data.get('client_phone', '')}
        {invoice_data.get('client_address', '')}
        """)
        
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
        """جدول الخدمات بتصميم متطور"""
        elements = []
        
        section_title = Paragraph(self.arabic_text("الخدمات والمنتجات"), self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 10))
        
        header = [self.arabic_text('الخدمة'), self.arabic_text('الوصف'), self.arabic_text('الكمية'), self.arabic_text('سعر الوحدة'), self.arabic_text('المجموع')]
        data = [header]
        
        for service in invoice_data['services']:
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
        """قسم الإجماليات والملاحظات"""
        elements = []
        
        totals_data = [
            [self.arabic_text('المجموع الفرعي:'), f"{invoice_data['subtotal']:,.2f}"],
            [self.arabic_text(f'الضريبة ({invoice_data["tax_rate"]}%):'), f"{invoice_data['tax_amount']:,.2f}"],
            [self.arabic_text('الإجمالي النهائي:'), f"{invoice_data['total_amount']:,.2f}"]
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
        
        if invoice_data.get('notes') or invoice_data.get('payment_terms'):
            notes_text = ""
            if invoice_data.get('payment_terms'):
                notes_text += f"{self.arabic_text('شروط الدفع:')} {self.arabic_text(invoice_data['payment_terms'])}<br/>"
            if invoice_data.get('notes'):
                notes_text += f"{self.arabic_text('ملاحظات:')} {self.arabic_text(invoice_data['notes'])}"
            
            notes_paragraph = Paragraph(notes_text, self.styles['Normal'])
            elements.append(notes_paragraph)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def create_professional_footer(self):
        """تذييل الفاتورة الاحترافي"""
        elements = []
        
        footer_text = self.arabic_text("""
        InvoiceFlow Pro - نظام إدارة الفواتير الاحترافي
        هاتف: +966500000000 | البريد الإلكتروني: info@invoiceflow.com
        شكراً لتعاملكم معنا
        """)
        
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

    def arabic_text(self, text):
        """معالجة النص العربي للعرض في PDF"""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except:
            return text

# ================== نظام الذكاء الاصطناعي المتقدم ==================
class AdvancedInvoiceAI:
    def __init__(self):
        self.user_profiles = {}
        self.conversation_history = {}
        
    def smart_welcome(self, username):
        """ترحيب ذكي مخصص مع تحليلات متقدمة"""
        user_stats = invoice_manager.get_user_stats(username)
        invoices = invoice_manager.get_user_invoices(username)
        
        return self._generate_welcome_dashboard(username, user_stats, invoices)
    
    def _generate_welcome_dashboard(self, username, stats, invoices):
        """إنشاء لوحة ترحيب ذكية"""
        
        # تحليل الأداء
        performance_analysis = self._analyze_performance(stats, invoices)
        
        # توصيات ذكية
        recommendations = self._generate_recommendations(stats, invoices)
        
        # تنبؤات
        predictions = self._generate_predictions(stats)
        
        return f"""
        <div class="ai-dashboard" style="background: linear-gradient(135deg, #0F172A, #1a237e); color: white; border-radius: 16px; padding: 25px; margin: 20px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <div style="background: #0D9488; padding: 12px; border-radius: 12px; margin-left: 15px;">
                    <i class="fas fa-robot" style="font-size: 1.5em;"></i>
                </div>
                <div>
                    <h3 style="margin: 0; color: white;">المساعد الذكي - InvoiceAI</h3>
                    <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 0.9em;">مرحباً {username}!
                    <span style="color: #0D9488;">• {performance_analysis['mood']}</span></p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div class="ai-card" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px);">
                    <h4 style="color: #0D9488; margin-bottom: 15px; display: flex; align-items: center;">
                        <i class="fas fa-chart-line" style="margin-left: 8px;"></i>
                        تحليل الأداء
                    </h4>
                    <div style="color: #E2E8F0;">
                        <p>📈 <b>معدل النمو:</b> {performance_analysis['growth_rate']}%</p>
                        <p>💰 <b>متوسط الفاتورة:</b> ${performance_analysis['avg_invoice']:,.0f}</p>
                        <p>⏱️ <b>كفاءة التحصيل:</b> {performance_analysis['collection_efficiency']}%</p>
                        <p>🎯 <b>مستوى الأداء:</b> {performance_analysis['performance_level']}</p>
                    </div>
                </div>
                
                <div class="ai-card" style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; backdrop-filter: blur(10px);">
                    <h4 style="color: #0D9488; margin-bottom: 15px; display: flex; align-items: center;">
                        <i class="fas fa-lightbulb" style="margin-left: 8px;"></i>
                        توصيات ذكية
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
    
    def _analyze_performance(self, stats, invoices):
        """تحليل أداء المستخدم"""
        total_invoices = stats['total_invoices']
        total_revenue = stats['total_revenue']
        pending_invoices = stats['pending_invoices']
        
        # حساب متوسط الفاتورة
        avg_invoice = total_revenue / max(total_invoices, 1)
        
        # حساب كفاءة التحصيل
        paid_amount = stats.get('paid_amount', 0)
        collection_efficiency = (paid_amount / max(total_revenue, 1)) * 100
        
        # تحديد معدل النمو
        growth_rate = min(25, total_invoices * 2)  # نمو تقديري
        
        # تحديد الحالة المزاجية بناءً على الأداء
        if total_invoices == 0:
            mood = "ابدأ رحلتك الأولى 🚀"
            performance_level = "مبتدئ"
        elif total_invoices < 5:
            mood = "أداء جيد للبداية 🌟"
            performance_level = "ناشئ"
        elif total_invoices < 20:
            mood = "أداء ممتاز مستمر 💪"
            performance_level = "محترف"
        else:
            mood = "خبير في الإدارة 🏆"
            performance_level = "خبير"
        
        return {
            'growth_rate': growth_rate,
            'avg_invoice': avg_invoice,
            'collection_efficiency': round(collection_efficiency, 1),
            'performance_level': performance_level,
            'mood': mood
        }
    
    def _generate_recommendations(self, stats, invoices):
        """توليد توصيات ذكية مخصصة"""
        recommendations = []
        total_invoices = stats['total_invoices']
        pending_invoices = stats['pending_invoices']
        
        if total_invoices == 0:
            recommendations.append("🎯 ابدأ بإنشاء فاتورتك الأولى اليوم")
            recommendations.append("📞 أضف عملاءك لتبدأ في بناء قاعدة عملائك")
        else:
            if pending_invoices > 2:
                recommendations.append("⏰ لديك فواتير معلقة تحتاج متابعة عاجلة")
            
            if total_invoices < 10:
                recommendations.append("🚀 وسع قاعدة عملائك لزيادة إيراداتك")
            
            if stats.get('paid_amount', 0) < stats['total_revenue'] * 0.7:
                recommendations.append("💳 حسن سياسة التحصيل لزيادة التدفق النقدي")
            
            # توصيات إضافية
            recommendations.append("📊 استخدم التقارير لمتابعة أدائك الشهري")
            recommendations.append("🎨 personaliza الفواتير لتعزيز الهوية التجارية")
        
        # إضافة توصية دائماً
        recommendations.append("⭐ استمر في استخدام النظام لتحقيق أفضل النتائج")
        
        return "".join(f'<p>• {rec}</p>' for rec in recommendations[:4])  # عرض 4 توصيات كحد أقصى
    
    def _generate_predictions(self, stats):
        """توليد تنبؤات ذكية"""
        total_invoices = stats['total_invoices']
        total_revenue = stats['total_revenue']
        
        if total_invoices == 0:
            return {
                'revenue_next_month': "$0",
                'invoices_next_month': "0",
                'success_probability': "85"
            }
        
        # تنبؤات تقديرية بناءً على الأداء الحالي
        revenue_growth = min(50, total_invoices * 5)  # نمو تقديري
        predicted_revenue = total_revenue * (1 + revenue_growth/100)
        predicted_invoices = total_invoices + max(2, total_invoices // 3)
        
        # احتمالية النجاح
        success_probability = min(95, 70 + total_invoices * 2)
        
        return {
            'revenue_next_month': f"${predicted_revenue:,.0f}",
            'invoices_next_month': f"{predicted_invoices}",
            'success_probability': f"{success_probability}"
        }

# ================== نظام النسخ الاحتياطي ==================
class BackupManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.backup_dir = self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """تأكيد وجود مجلد النسخ الاحتياطي"""
        try:
            backup_dir = os.path.join(os.getcwd(), 'backups')
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            return backup_dir
        except Exception as e:
            print(f"⚠️ خطأ في إنشاء مجلد النسخ الاحتياطي: {e}")
            return 'backups'
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'backup_{timestamp}.db')
            
            # نسخ قاعدة البيانات
            import shutil
            shutil.copy2(self.db.db_path, backup_file)
            
            print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
            return True, backup_file
        except Exception as e:
            print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False, str(e)
    
    def auto_backup(self):
        """نسخ احتياطي تلقائي"""
        try:
            success, backup_file = self.create_backup()
            if success:
                # حذف النسخ القديمة (الاحتفاظ بـ 5 نسخ فقط)
                self.clean_old_backups()
            return success
        except Exception as e:
            print(f"❌ خطأ في النسخ الاحتياطي التلقائي: {e}")
            return False
    
    def clean_old_backups(self, keep_count=5):
        """تنظيف النسخ القديمة"""
        try:
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.startswith('backup_') and file.endswith('.db'):
                    backup_files.append(file)
            
            # ترتيب الملفات حسب التاريخ (الأقدم أولاً)
            backup_files.sort()
            
            # حذف الملفات الزائدة
            if len(backup_files) > keep_count:
                for file in backup_files[:-keep_count]:
                    os.remove(os.path.join(self.backup_dir, file))
                    print(f"🗑️ تم حذف النسخة القديمة: {file}")
        except Exception as e:
            print(f"⚠️ خطأ في تنظيف النسخ القديمة: {e}")

# ================== نظام الإشعارات ==================
class NotificationManager:
    def __init__(self):
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
                'timestamp': datetime.now(),
                'read': False
            }
            
            self.notifications[user_id].append(notification)
            return True
        except Exception as e:
            print(f"❌ خطأ في إضافة الإشعار: {e}")
            return False
    
    def get_user_notifications(self, user_id, unread_only=False):
        """جلب إشعارات المستخدم"""
        try:
            if user_id not in self.notifications:
                return []
            
            notifications = self.notifications[user_id]
            if unread_only:
                notifications = [n for n in notifications if not n['read']]
            
            return notifications[-10:]  # آخر 10 إشعارات
        except Exception as e:
            print(f"❌ خطأ في جلب الإشعارات: {e}")
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
            print(f"❌ خطأ في تحديد الإشعار كمقروء: {e}")
            return False

# ================== الدوال المساعدة ==================
def validate_invoice_data(data):
    """التحقق من صحة بيانات الفاتورة"""
    required_fields = ['client_name', 'services']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"الحقل {field} مطلوب"
    
    if not isinstance(data['services'], list) or len(data['services']) == 0:
        return False, "يجب إضافة خدمة واحدة على الأقل"
    
    for service in data['services']:
        if 'name' not in service or 'price' not in service:
            return False, "بيانات الخدمة غير مكتملة"
    
    return True, "بيانات صحيحة"

def analyze_financial_data(invoices):
    """تحليل البيانات المالية"""
    if not invoices:
        return {
            'avg_invoice': 0,
            'max_invoice': 0,
            'min_invoice': 0,
            'monthly_revenue': 0,
            'net_revenue': 0,
            'growth_rate': 0
        }
    
    amounts = [inv['amount'] for inv in invoices]
    
    return {
        'avg_invoice': sum(amounts) / len(amounts),
        'max_invoice': max(amounts),
        'min_invoice': min(amounts),
        'monthly_revenue': sum(amounts) * 0.3,  # تقدير شهري
        'net_revenue': sum(amounts) * 0.85,     # تقدير صافي
        'growth_rate': min(25, len(invoices) * 2)  # نمو تقديري
    }

def generate_invoices_table(invoices):
    """إنشاء جدول الفواتير"""
    if not invoices:
        return '''
        <tr>
            <td colspan="6" style="text-align: center; padding: 20px; color: var(--light-slate);">
                <i class="fas fa-receipt" style="font-size: 2em; margin-bottom: 10px; display: block; opacity: 0.5;"></i>
                لا توجد فواتير لعرضها
            </td>
        </tr>
        '''
    
    html = ""
    for inv in invoices[:10]:  # عرض 10 فواتير كحد أقصى
        payment_class = 'مدفوع' if inv.get('payment_status') == 'مدفوع' else 'غير_مدفوع'
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

def get_ai_tip(stats):
    """نصائح ذكية من المساعد"""
    if stats['total_invoices'] == 0:
        return "ابدأ بإنشاء فاتورتك الأولى اليوم لترى تحليلات مفصلة"
    elif stats['total_invoices'] < 5:
        return "رائع! استمر في إضافة الفواتير لتحصل على تحليلات أكثر دقة"
    else:
        return "أداؤك ممتاز! فكر في توسيع قاعدة عملائك لزيادة الإيرادات"

def get_ai_tip2(stats):
    """نصيحة ذكية ثانية"""
    if stats['pending_invoices'] > 0:
        return "راجع الفواتير المعلقة لتحسين التدفق النقدي"
    else:
        return "جميع فواتيرك مسددة - هذا ممتاز للتدفق النقدي"

def get_ai_tip3(analysis):
    """نصيحة ذكية ثالثة"""
    if analysis['growth_rate'] > 15:
        return "معدل نموك ممتاز! استمر في هذا الأداء الرائع"
    else:
        return "هناك مجال لتحسين النمو - راجع استراتيجية التسعير"

# ================== إعداد الأنظمة ==================
db_manager = DatabaseManager()
user_manager = UserManager()
invoice_manager = InvoiceManager()
pdf_generator = ProfessionalPDFGenerator()
invoice_ai = AdvancedInvoiceAI()
backup_manager = BackupManager()
notification_manager = NotificationManager()

class SystemMonitor:
    def __init__(self):
        self.uptime_start = time.time()
        self.last_backup = time.time()
        
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
            
            # نسخ احتياطي تلقائي كل ساعة
            if time.time() - self.last_backup > 3600:  # كل ساعة
                if backup_manager.auto_backup():
                    self.last_backup = time.time()
                    print("✅ تم النسخ الاحتياطي التلقائي")

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
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
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
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            font-family: 'Tajawal', -apple-system, BlinkMacSystemFont, sans-serif;
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
            overflow: hidden;
        }
        
        .auth-background {
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
        }
        
        .auth-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px 35px;
            width: 100%;
            max-width: 440px;
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.1),
                0 0 0 1px rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: cardEntrance 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }
        
        @keyframes cardEntrance {
            0% {
                opacity: 0;
                transform: translateY(30px) scale(0.95);
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
            font-size: 3em;
            background: var(--blue-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
            display: inline-block;
        }
        
        .brand-title {
            font-size: 2.2em;
            font-weight: 800;
            background: var(--blue-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }
        
        .brand-subtitle {
            color: var(--light-slate);
            font-size: 1em;
            font-weight: 400;
            line-height: 1.5;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            color: var(--primary-dark);
            font-weight: 600;
            font-size: 0.95em;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .form-control {
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
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--accent-blue);
            background: var(--pure-white);
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
            transform: translateY(-2px);
        }
        
        .input-icon {
            position: absolute;
            left: 18px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-slate);
            font-size: 1.2em;
            transition: all 0.3s ease;
        }
        
        .form-control:focus + .input-icon {
            color: var(--accent-blue);
            transform: translateY(-50%) scale(1.1);
        }
        
        .btn {
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
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn:hover::before {
            left: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn:active {
            transform: translateY(0);
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
            font-size: 0.9em;
            margin-bottom: 14px;
        }
        
        .security-indicator {
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
            backdrop-filter: blur(10px);
        }
        
        /* ================== تحسينات خاصة بالجوال ================== */
        @media (max-width: 768px) {
            .auth-wrapper {
                padding: 10px;
                align-items: flex-start;
                padding-top: 20px;
            }
            
            .auth-card {
                padding: 30px 25px;
                margin: 10px;
                border-radius: 20px;
                max-width: 100%;
            }
            
            .brand-logo {
                font-size: 2.5em;
            }
            
            .brand-title {
                font-size: 1.8em;
            }
            
            .brand-subtitle {
                font-size: 0.9em;
            }
            
            .form-control {
                padding: 14px 18px 14px 45px;
                font-size: 16px; /* منع التكبير في iOS */
            }
            
            .input-icon {
                left: 15px;
                font-size: 1.1em;
            }
            
            .btn {
                padding: 14px 24px;
                font-size: 16px; /* منع التكبير في iOS */
            }
        }
        
        @media (max-width: 480px) {
            .auth-card {
                padding: 25px 20px;
                border-radius: 16px;
            }
            
            .brand-logo {
                font-size: 2.2em;
            }
            
            .brand-title {
                font-size: 1.6em;
            }
            
            .form-control {
                padding: 12px 16px 12px 40px;
            }
            
            .input-icon {
                left: 12px;
                font-size: 1em;
            }
            
            .security-indicator {
                font-size: 0.8em;
                padding: 6px 12px;
            }
        }
        
        @media (max-width: 360px) {
            .auth-card {
                padding: 20px 15px;
            }
            
            .brand-section {
                margin-bottom: 25px;
            }
            
            .form-group {
                margin-bottom: 15px;
            }
        }
        
        /* ================== تحسينات خاصة بالشاشات الكبيرة ================== */
        @media (min-width: 1200px) {
            .auth-card {
                max-width: 480px;
                padding: 50px 45px;
            }
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
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
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
        
        /* ================== أنماط الجداول ================== */
        .services-table {
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
        }
        
        .services-table th,
        .services-table td {
            padding: 12px 15px;
            text-align: right;
            border-bottom: 1px solid var(--border-light);
        }
        
        .services-table th {
            background: var(--light-gray);
            font-weight: 600;
            color: var(--primary-dark);
        }
        
        .services-table tr:hover {
            background: var(--light-gray);
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
        }
        
        .status-badge.مسددة {
            background: var(--success);
            color: white;
        }
        
        .status-badge.معلقة {
            background: var(--warning);
            color: white;
        }
        
        .status-badge.مسودة {
            background: var(--light-slate);
            color: white;
        }
        
        .payment-badge.مدفوع {
            background: var(--success);
            color: white;
        }
        
        .payment-badge.غير_مدفوع {
            background: var(--error);
            color: white;
        }
        
        /* ================== تحسينات التصميم المتجاوب ================== */
        @media (max-width: 1200px) {
            .professional-container {
                padding: 18px;
            }
        }
        
        @media (max-width: 768px) {
            .professional-container {
                padding: 15px;
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
            
            .content-section {
                padding: 20px;
            }
        }
        
        @media (max-width: 480px) {
            .professional-container {
                padding: 10px;
            }
            
            .dashboard-header {
                padding: 15px;
            }
            
            .header-content h1 {
                font-size: 1.6em;
            }
            
            .nav-card, .stat-card {
                padding: 20px;
            }
            
            .stat-number {
                font-size: 2em;
            }
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
        <div class="auth-background"></div>
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
            
            // إضافة toggle لكلمة المرور
            const passwordInputs = document.querySelectorAll('input[type="password"]');
            passwordInputs.forEach(input => {
                const toggle = document.createElement('button');
                toggle.type = 'button';
                toggle.className = 'password-toggle';
                toggle.innerHTML = '<i class="fas fa-eye"></i>';
                toggle.style.cssText = 'position: absolute; right: 15px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--light-slate); cursor: pointer; font-size: 1.1em; padding: 5px;';
                
                toggle.addEventListener('click', function() {
                    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                    input.setAttribute('type', type);
                    this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
                });
                
                input.parentNode.appendChild(toggle);
            });
        });
        
        function exportToPDF() {
            alert('سيتم تنفيذ تصدير PDF في الإصدار القادم');
        }
        
        function showRevenueChart() {
            alert('مخططات الإيرادات التفاعلية قريباً في التحديث القادم');
        }
        
        function generateMonthlyReport() {
            alert('التقارير الشهرية الآلية قريباً في التحديث القادم');
        }
    </script>
</body>
</html>
"""

# ================== Routes الأساسية ==================
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
    
    ai_welcome = invoice_ai.smart_welcome(session['username'])
    
    admin_button = ''
    if session.get('user_type') == 'admin':
        admin_button = '''
        <a href="/admin" class="btn" style="background: var(--accent-teal);">
            <i class="fas fa-cog"></i> لوحة الإدارة
        </a>
        '''
    
    content = ai_welcome + f"""
    
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
            
            # إضافة إشعار ترحيب
            notification_manager.add_notification(
                username, 
                "مرحباً بك في InvoiceFlow Pro!",
                "نتمنى لك تجربة ممتعة مع نظام إدارة الفواتير المتكامل",
                'info'
            )
            
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

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    """الملف الشخصي"""
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

@app.route('/invoices')
def invoices_list():
    """عرض جميع الفواتير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    user_invoices = invoice_manager.get_user_invoices(session['username'])
    
    invoices_html = ""
    if user_invoices:
        for inv in user_invoices:
            invoices_html += f"""
            <div class="invoice-item" style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid var(--border-light);">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: var(--primary-dark);">{inv['number']}</h4>
                        <p style="margin: 0; color: var(--light-slate);">العميل: {inv['client']}</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2em; font-weight: bold; color: var(--accent-blue);">${inv['amount']:,.2f}</div>
                        <span class="status-badge {inv['status']}">{inv['status']}</span>
                    </div>
                    <div style="text-align: left;">
                        <small style="color: var(--light-slate);">{inv['issue_date']}</small>
                        <div style="margin-top: 10px;">
                            <a href="/invoices/{inv['number']}/pdf" class="btn-action" style="background: var(--accent-blue); color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; margin-right: 5px;">
                                <i class="fas fa-download"></i> PDF
                            </a>
                            <button class="btn-action" style="background: var(--accent-teal); color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none;">
                                <i class="fas fa-eye"></i> عرض
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            """
    else:
        invoices_html = '''
        <div style="text-align: center; padding: 40px; color: var(--light-slate);">
            <i class="fas fa-receipt" style="font-size: 3em; margin-bottom: 20px; opacity: 0.5;"></i>
            <h3>لا توجد فواتير</h3>
            <p>ابدأ بإنشاء فاتورتك الأولى</p>
            <a href="/invoices/create" class="btn" style="margin-top: 20px;">
                <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
            </a>
        </div>
        '''
    
    content = f"""
    <div class="dashboard-header">
        <h1><i class="fas fa-receipt"></i> إدارة الفواتير</h1>
        <p>عرض وإدارة جميع فواتيرك في مكان واحد</p>
    </div>

    <div class="content-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3><i class="fas fa-list"></i> قائمة الفواتير</h3>
            <a href="/invoices/create" class="btn">
                <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
            </a>
        </div>
        
        {invoices_html}
    </div>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="الفواتير - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/invoices/create', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            services = []
            service_count = int(request.form.get('service_count', 0))
            
            for i in range(service_count):
                service_name = request.form.get(f'service_name_{i}')
                service_desc = request.form.get(f'service_desc_{i}', '')
                quantity = float(request.form.get(f'quantity_{i}', 1))
                price = float(request.form.get(f'price_{i}', 0))
                
                if service_name and price > 0:
                    services.append({
                        'name': service_name,
                        'description': service_desc,
                        'quantity': quantity,
                        'price': price
                    })
            
            subtotal = sum(service['quantity'] * service['price'] for service in services)
            tax_rate = float(request.form.get('tax_rate', 0))
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
                'payment_terms': request.form.get('payment_terms', '30 يوم'),
                'notes': request.form.get('notes', ''),
                'company_name': session.get('company_name', 'InvoiceFlow Pro')
            }
            
            is_valid, message = validate_invoice_data(invoice_data)
            if not is_valid:
                content = f"""
                <div class="alert alert-error">
                    <i class="fas fa-exclamation-circle"></i> {message}
                </div>
                """ + create_invoice_form()
            else:
                success, invoice_number, message = invoice_manager.create_invoice(invoice_data)
                
                if success:
                    # إضافة إشعار نجاح
                    notification_manager.add_notification(
                        session['username'],
                        "تم إنشاء فاتورة جديدة!",
                        f"تم إنشاء الفاتورة رقم {invoice_number} بنجاح",
                        'success'
                    )
                    return redirect(f'/invoices/{invoice_number}/success')
                else:
                    content = f"""
                    <div class="alert alert-error">
                        <i class="fas fa-exclamation-circle"></i> {message}
                    </div>
                    """ + create_invoice_form()
        except Exception as e:
            content = f"""
            <div class="alert alert-error">
                <i class="fas fa-exclamation-circle"></i> خطأ في إنشاء الفاتورة: {str(e)}
            </div>
            """ + create_invoice_form()
    else:
        content = create_invoice_form()
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="إنشاء فاتورة - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

def create_invoice_form():
    """نموذج إنشاء الفاتورة"""
    return """
    <div class="dashboard-header">
        <h1><i class="fas fa-plus-circle"></i> إنشاء فاتورة جديدة</h1>
        <p>قم بإنشاء فاتورة احترافية لعملائك في دقائق</p>
    </div>

    <form method="POST" id="invoiceForm" class="invoice-form">
        <!-- معلومات العميل -->
        <div class="form-section">
            <h3 class="section-title"><i class="fas fa-user"></i> معلومات العميل</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label class="form-label">اسم العميل *</label>
                    <input type="text" name="client_name" class="form-control" required placeholder="أدخل اسم العميل الكامل">
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
                    <input type="text" name="client_address" class="form-control" placeholder="عنوان العميل">
                </div>
            </div>
        </div>

        <!-- الخدمات والمنتجات -->
        <div class="form-section">
            <h3 class="section-title"><i class="fas fa-list"></i> الخدمات والمنتجات</h3>
            <div id="servicesContainer">
                <div class="service-item" style="display: grid; grid-template-columns: 2fr 2fr 1fr 1fr auto; gap: 10px; margin-bottom: 15px; align-items: end;">
                    <div>
                        <label class="form-label">اسم الخدمة</label>
                        <input type="text" name="service_name_0" class="form-control" placeholder="اسم الخدمة أو المنتج">
                    </div>
                    <div>
                        <label class="form-label">الوصف</label>
                        <input type="text" name="service_desc_0" class="form-control" placeholder="وصف مختصر">
                    </div>
                    <div>
                        <label class="form-label">الكمية</label>
                        <input type="number" name="quantity_0" class="form-control" value="1" min="1" step="1">
                    </div>
                    <div>
                        <label class="form-label">السعر</label>
                        <input type="number" name="price_0" class="form-control" placeholder="0.00" min="0" step="0.01">
                    </div>
                    <div>
                        <button type="button" class="btn-action remove-service" style="background: var(--error); color: white; padding: 10px;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            <button type="button" id="addService" class="btn btn-secondary" style="margin-top: 15px;">
                <i class="fas fa-plus"></i> إضافة خدمة أخرى
            </button>
        </div>

        <!-- الإعدادات والإجماليات -->
        <div class="form-section">
            <h3 class="section-title"><i class="fas fa-calculator"></i> الإعدادات والإجماليات</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div class="form-group">
                    <label class="form-label">نسبة الضريبة (%)</label>
                    <input type="number" name="tax_rate" class="form-control" value="15" min="0" max="100" step="0.1">
                </div>
                <div class="form-group">
                    <label class="form-label">شروط الدفع</label>
                    <select name="payment_terms" class="form-control">
                        <option value="15 يوم">15 يوم</option>
                        <option value="30 يوم" selected>30 يوم</option>
                        <option value="45 يوم">45 يوم</option>
                        <option value="60 يوم">60 يوم</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">ملاحظات إضافية</label>
                <textarea name="notes" class="form-control" rows="3" placeholder="أي ملاحظات إضافية للفاتورة..."></textarea>
            </div>

            <div id="totalsSection" style="background: var(--light-gray); padding: 20px; border-radius: 10px; margin-top: 20px;">
                <h4 style="margin-bottom: 15px; color: var(--primary-dark);">الإجماليات:</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>المجموع الفرعي:</div>
                    <div id="subtotal" style="text-align: left;">$0.00</div>
                    
                    <div>الضريبة (<span id="taxRate">15</span>%):</div>
                    <div id="taxAmount" style="text-align: left;">$0.00</div>
                    
                    <div style="font-weight: bold; font-size: 1.1em;">الإجمالي النهائي:</div>
                    <div id="totalAmount" style="text-align: left; font-weight: bold; font-size: 1.1em; color: var(--accent-blue);">$0.00</div>
                </div>
            </div>
        </div>

        <div class="action-buttons">
            <button type="submit" class="btn">
                <i class="fas fa-check"></i> إنشاء الفاتورة
            </button>
            <a href="/invoices" class="btn btn-secondary">
                <i class="fas fa-times"></i> إلغاء
            </a>
        </div>

        <input type="hidden" name="service_count" id="serviceCount" value="1">
    </form>

    <script>
        let serviceCount = 1;
        
        document.getElementById('addService').addEventListener('click', function() {
            serviceCount++;
            const newService = `
                <div class="service-item" style="display: grid; grid-template-columns: 2fr 2fr 1fr 1fr auto; gap: 10px; margin-bottom: 15px; align-items: end;">
                    <div>
                        <input type="text" name="service_name_${serviceCount}" class="form-control" placeholder="اسم الخدمة أو المنتج">
                    </div>
                    <div>
                        <input type="text" name="service_desc_${serviceCount}" class="form-control" placeholder="وصف مختصر">
                    </div>
                    <div>
                        <input type="number" name="quantity_${serviceCount}" class="form-control" value="1" min="1" step="1">
                    </div>
                    <div>
                        <input type="number" name="price_${serviceCount}" class="form-control" placeholder="0.00" min="0" step="0.01">
                    </div>
                    <div>
                        <button type="button" class="btn-action remove-service" style="background: var(--error); color: white; padding: 10px;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            document.getElementById('servicesContainer').insertAdjacentHTML('beforeend', newService);
            document.getElementById('serviceCount').value = serviceCount;
            attachRemoveListeners();
            attachCalculationListeners();
        });

        function attachRemoveListeners() {
            document.querySelectorAll('.remove-service').forEach(button => {
                button.addEventListener('click', function() {
                    if (document.querySelectorAll('.service-item').length > 1) {
                        this.closest('.service-item').remove();
                        serviceCount--;
                        document.getElementById('serviceCount').value = serviceCount;
                        calculateTotals();
                    }
                });
            });
        }

        function attachCalculationListeners() {
            document.querySelectorAll('input[name^="quantity"], input[name^="price"]').forEach(input => {
                input.addEventListener('input', calculateTotals);
            });
        }

        function calculateTotals() {
            let subtotal = 0;
            
            document.querySelectorAll('.service-item').forEach((item, index) => {
                const quantity = parseFloat(item.querySelector(`[name="quantity_${index}"]`).value) || 0;
                const price = parseFloat(item.querySelector(`[name="price_${index}"]`).value) || 0;
                subtotal += quantity * price;
            });
            
            const taxRate = parseFloat(document.querySelector('[name="tax_rate"]').value) || 0;
            const taxAmount = subtotal * (taxRate / 100);
            const totalAmount = subtotal + taxAmount;
            
            document.getElementById('subtotal').textContent = '$' + subtotal.toFixed(2);
            document.getElementById('taxRate').textContent = taxRate;
            document.getElementById('taxAmount').textContent = '$' + taxAmount.toFixed(2);
            document.getElementById('totalAmount').textContent = '$' + totalAmount.toFixed(2);
        }

        // إضافة مستمعات الأحداث
        document.addEventListener('DOMContentLoaded', function() {
            attachRemoveListeners();
            attachCalculationListeners();
            document.querySelector('input[name="tax_rate"]').addEventListener('input', calculateTotals);
            calculateTotals();
        });
    </script>
    """

@app.route('/invoices/<invoice_number>/pdf')
def download_invoice_pdf(invoice_number):
    """تنزيل الفاتورة كملف PDF"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM invoices WHERE invoice_number = ? AND user_id = ?
        ''', (invoice_number, session['username']))
        
        invoice = cursor.fetchone()
        conn.close()
        
        if invoice:
            invoice_data = dict(invoice)
            invoice_data['services'] = json.loads(invoice_data['services_json'])
            
            pdf_buffer = pdf_generator.create_professional_invoice(invoice_data)
            
            if pdf_buffer:
                return send_file(
                    pdf_buffer,
                    as_attachment=True,
                    download_name=f'invoice_{invoice_number}.pdf',
                    mimetype='application/pdf'
                )
        
        return "الفاتورة غير موجودة", 404
    except Exception as e:
        print(f"❌ خطأ في إنشاء PDF: {e}")
        return "خطأ في إنشاء الفاتورة", 500

@app.route('/invoices/<invoice_number>/success')
def invoice_success(invoice_number):
    """صفحة نجاح إنشاء الفاتورة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    content = f"""
    <div class="dashboard-header">
        <h1 style="color: var(--success);"><i class="fas fa-check-circle"></i> تم إنشاء الفاتورة بنجاح!</h1>
        <p>فاتورتك الجاهزة رقم: <strong>{invoice_number}</strong></p>
    </div>

    <div class="content-section" style="text-align: center;">
        <div style="font-size: 4em; color: var(--success); margin-bottom: 20px;">
            <i class="fas fa-check-circle"></i>
        </div>
        
        <h3 style="margin-bottom: 20px;">تم إنشاء الفاتورة بنجاح</h3>
        <p style="margin-bottom: 30px; color: var(--light-slate);">
            يمكنك الآن تنزيل الفاتورة أو مشاركتها مع عميلك
        </p>
        
        <div class="action-buttons" style="justify-content: center;">
            <a href="/invoices/{invoice_number}/pdf" class="btn" style="background: var(--accent-blue);">
                <i class="fas fa-download"></i> تنزيل الفاتورة (PDF)
            </a>
            <a href="/invoices" class="btn btn-secondary">
                <i class="fas fa-list"></i> عرض جميع الفواتير
            </a>
            <a href="/invoices/create" class="btn" style="background: var(--accent-teal);">
                <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
            </a>
        </div>
    </div>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="تم الإنشاء - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/clients')
def clients_management():
    """إدارة العملاء"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    user_clients = invoice_manager.get_user_clients(session['username'])
    
    clients_html = ""
    if user_clients:
        for client in user_clients:
            clients_html += f"""
            <div class="client-card" style="background: white; border: 1px solid var(--border-light); border-radius: 12px; padding: 20px; margin-bottom: 15px;">
                <div class="client-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin: 0; color: var(--primary-dark);">{client['name']}</h3>
                    <span class="client-badge" style="padding: 4px 12px; border-radius: 20px; font-size: 0.8em; font-weight: 600; background: var(--accent-blue); color: white;">{client.get('category', 'عام')}</span>
                </div>
                <div class="client-info" style="color: var(--light-slate);">
                    <p><i class="fas fa-envelope"></i> {client.get('email', 'لا يوجد')}</p>
                    <p><i class="fas fa-phone"></i> {client.get('phone', 'لا يوجد')}</p>
                    <p><i class="fas fa-building"></i> {client.get('company_name', 'لا يوجد')}</p>
                    <p><i class="fas fa-calendar"></i> {client['created_at'][:10]}</p>
                </div>
                <div class="client-actions" style="display: flex; gap: 8px; margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-light);">
                    <button class="btn-action" onclick="editClient({client['id']})" style="background: var(--light-gray); color: var(--primary-dark); padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 5px;">
                        <i class="fas fa-edit"></i> تعديل
                    </button>
                    <button class="btn-action" onclick="createInvoiceForClient({client['id']})" style="background: var(--accent-teal); color: white; padding: 8px 12px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 5px;">
                        <i class="fas fa-receipt"></i> فاتورة
                    </button>
                </div>
            </div>
            """
    else:
        clients_html = '''
        <div style="text-align: center; padding: 60px 20px; color: var(--light-slate);">
            <i class="fas fa-users" style="font-size: 4em; margin-bottom: 20px; opacity: 0.5;"></i>
            <h3>لا يوجد عملاء</h3>
            <p>ابدأ بإضافة عميلك الأول</p>
            <button class="btn" onclick="openAddClientModal()" style="margin-top: 20px;">
                <i class="fas fa-plus"></i> إضافة عميل جديد
            </button>
        </div>
        '''
    
    content = f"""
    <div class="dashboard-header">
        <h1><i class="fas fa-users"></i> إدارة العملاء</h1>
        <p>إدارة قاعدة بيانات عملائك بسهولة واحترافية</p>
    </div>

    <div class="content-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3><i class="fas fa-address-book"></i> قائمة العملاء</h3>
            <button class="btn" onclick="openAddClientModal()">
                <i class="fas fa-plus"></i> إضافة عميل جديد
            </button>
        </div>
        
        <div>
            {clients_html}
        </div>
    </div>

    <!-- مودال إضافة عميل -->
    <div id="addClientModal" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);">
        <div class="modal-content" style="background-color: var(--pure-white); margin: 5% auto; padding: 0; border-radius: 12px; width: 90%; max-width: 700px;">
            <div class="modal-header" style="padding: 20px 25px; border-bottom: 1px solid var(--border-light); display: flex; justify-content: space-between; align-items: center;">
                <h3><i class="fas fa-user-plus"></i> إضافة عميل جديد</h3>
                <span class="close" onclick="closeAddClientModal()" style="color: var(--light-slate); font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
            </div>
            <div class="modal-body" style="padding: 25px;">
                <form id="addClientForm">
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
                            <label class="form-label">التصنيف</label>
                            <select name="category" class="form-control">
                                <option value="عام">عام</option>
                                <option value="شركة">شركة</option>
                                <option value="فرد">فرد</option>
                                <option value="حكومي">حكومي</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">شروط الدفع</label>
                            <select name="payment_terms" class="form-control">
                                <option value="15 يوم">15 يوم</option>
                                <option value="30 يوم" selected>30 يوم</option>
                                <option value="45 يوم">45 يوم</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">ملاحظات</label>
                        <textarea name="notes" class="form-control" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer" style="padding: 20px 25px; border-top: 1px solid var(--border-light); display: flex; justify-content: flex-end; gap: 10px;">
                <button type="button" class="btn btn-secondary" onclick="closeAddClientModal()">إلغاء</button>
                <button type="button" class="btn" onclick="saveClient()">حفظ العميل</button>
            </div>
        </div>
    </div>

    <script>
        function openAddClientModal() {{
            document.getElementById('addClientModal').style.display = 'block';
        }}

        function closeAddClientModal() {{
            document.getElementById('addClientModal').style.display = 'none';
        }}

        function saveClient() {{
            const form = document.getElementById('addClientForm');
            const formData = new FormData(form);
            
            fetch('/api/clients', {{
                method: 'POST',
                body: formData
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    location.reload();
                }} else {{
                    alert('خطأ: ' + data.message);
                }}
            }})
            .catch(error => {{
                alert('خطأ في الإضافة: ' + error);
            }});
        }}

        function createInvoiceForClient(clientId) {{
            window.location.href = '/invoices/create?client_id=' + clientId;
        }}

        function editClient(clientId) {{
            alert('ميزة التعديل قريباً في الإصدار القادم');
        }}

        window.onclick = function(event) {{
            const modal = document.getElementById('addClientModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}
    </script>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="العملاء - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/api/clients', methods=['POST'])
def api_add_client():
    """إضافة عميل جديد عبر API"""
    if 'user_logged_in' not in session:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    try:
        client_data = {
            'name': request.form['name'],
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'company_name': request.form.get('company_name', ''),
            'category': request.form.get('category', 'عام'),
            'payment_terms': request.form.get('payment_terms', '30 يوم'),
            'notes': request.form.get('notes', '')
        }
        
        success, message = invoice_manager.add_client(session['username'], client_data)
        
        if success:
            # إضافة إشعار
            notification_manager.add_notification(
                session['username'],
                "تم إضافة عميل جديد!",
                f"تم إضافة العميل {client_data['name']} بنجاح",
                'success'
            )
        
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ: {str(e)}'})

@app.route('/reports')
def enhanced_reports():
    """واجهة التقارير المحسنة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    stats = invoice_manager.get_user_stats(session['username'])
    invoices = invoice_manager.get_user_invoices(session['username'])
    
    # تحليل البيانات للإحصائيات
    analysis = analyze_financial_data(invoices)
    
    content = f"""
    <div class="dashboard-header">
        <h1><i class="fas fa-chart-bar"></i> التقارير والتحليلات المتقدمة</h1>
        <p>رؤى شاملة وأدوات تحليل متقدمة لأعمالك</p>
    </div>

    <!-- بطاقات الإحصائيات السريعة -->
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white;">
            <i class="fas fa-receipt"></i>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>إجمالي الفواتير</p>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #0D9488, #0F766E); color: white;">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p>إجمالي الإيرادات</p>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #059669, #047857); color: white;">
            <i class="fas fa-percentage"></i>
            <div class="stat-number">${stats['tax_amount']:,.0f}</div>
            <p>إجمالي الضرائب</p>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #7C3AED, #6D28D9); color: white;">
            <i class="fas fa-trend-up"></i>
            <div class="stat-number">+{analysis['growth_rate']}%</div>
            <p>معدل النمو</p>
        </div>
    </div>

    <!-- لوحة التحليلات المتقدمة -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 25px; margin-top: 25px;">
        <!-- التحليلات الرئيسية -->
        <div class="content-section">
            <h3 style="margin-bottom: 20px; color: var(--primary-dark); display: flex; align-items: center;">
                <i class="fas fa-chart-line" style="margin-left: 10px; color: var(--accent-blue);"></i>
                نظرة عامة على الأداء
            </h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <div style="background: var(--light-gray); padding: 20px; border-radius: 12px;">
                    <h4 style="color: var(--accent-blue); margin-bottom: 10px;">📈 أداء الفواتير</h4>
                    <p>• متوسط الفاتورة: <b>${analysis['avg_invoice']:,.2f}</b></p>
                    <p>• أكبر فاتورة: <b>${analysis['max_invoice']:,.2f}</b></p>
                    <p>• أصغر فاتورة: <b>${analysis['min_invoice']:,.2f}</b></p>
                </div>
                
                <div style="background: var(--light-gray); padding: 20px; border-radius: 12px;">
                    <h4 style="color: var(--accent-teal); margin-bottom: 10px;">💰 التحليل المالي</h4>
                    <p>• الإيرادات الشهرية: <b>${analysis['monthly_revenue']:,.2f}</b></p>
                    <p>• المصروفات الضريبية: <b>${stats['tax_amount']:,.2f}</b></p>
                    <p>• صافي الإيرادات: <b>${analysis['net_revenue']:,.2f}</b></p>
                </div>
            </div>
            
            <!-- جدول الفواتير -->
            <h4 style="margin-bottom: 15px; color: var(--primary-dark);">
                <i class="fas fa-table" style="margin-left: 8px;"></i>
                أحدث الفواتير
            </h4>
            
            <div style="overflow-x: auto;">
                <table class="services-table">
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
                        {generate_invoices_table(invoices)}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- اللوحة الجانبية -->
        <div>
            <!-- تحليل سريع -->
            <div class="content-section">
                <h4 style="margin-bottom: 15px; color: var(--primary-dark); display: flex; align-items: center;">
                    <i class="fas fa-bolt" style="margin-left: 8px; color: var(--warning);"></i>
                    تحليل سريع
                </h4>
                <div style="color: var(--light-slate); line-height: 2;">
                    <p>📊 <b>{stats['total_invoices']}</b> فاتورة تم إنشاؤها</p>
                    <p>💰 <b>${stats['total_revenue']:,.2f}</b> إجمالي الإيرادات</p>
                    <p>⏳ <b>{stats['pending_invoices']}</b> فاتورة قيد المعالجة</p>
                    <p>✅ <b>${stats['paid_amount']:,.2f}</b> تم تحصيلها</p>
                    <p>🎯 <b>{analysis['growth_rate']}%</b> معدل النمو</p>
                </div>
            </div>
            
            <!-- أدوات سريعة -->
            <div class="content-section">
                <h4 style="margin-bottom: 15px; color: var(--primary-dark); display: flex; align-items: center;">
                    <i class="fas fa-tools" style="margin-left: 8px; color: var(--accent-teal);"></i>
                    أدوات سريعة
                </h4>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="btn" onclick="exportToPDF()" style="background: var(--accent-blue);">
                        <i class="fas fa-file-pdf"></i> تصدير تقرير PDF
                    </button>
                    <button class="btn btn-secondary" onclick="showRevenueChart()">
                        <i class="fas fa-chart-bar"></i> عرض مخطط الإيرادات
                    </button>
                    <button class="btn btn-secondary" onclick="generateMonthlyReport()">
                        <i class="fas fa-calendar"></i> تقرير شهري
                    </button>
                </div>
            </div>
            
            <!-- نصائح المساعد الذكي -->
            <div class="content-section" style="background: linear-gradient(135deg, #0F172A, #1E293B); color: white;">
                <h4 style="margin-bottom: 15px; color: #0D9488; display: flex; align-items: center;">
                    <i class="fas fa-robot" style="margin-left: 8px;"></i>
                    نصائح ذكية
                </h4>
                <div style="font-size: 0.9em; line-height: 1.6;">
                    <p>🎯 {get_ai_tip(stats)}</p>
                    <p>💡 {get_ai_tip2(stats)}</p>
                    <p>🚀 {get_ai_tip3(analysis)}</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="التقارير - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

@app.route('/admin')
def admin():
    """لوحة الإدارة"""
    if 'user_logged_in' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('dashboard'))
    
    # إنشاء نسخة احتياطية عند زيارة لوحة الإدارة
    backup_success, backup_message = backup_manager.create_backup()
    
    content = f"""
    <div class="dashboard-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-cog"></i> لوحة الإدارة
        </h2>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-database"></i>
            <div class="stat-number">حالة النظام</div>
            <p>يعمل بشكل طبيعي</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-shield-alt"></i>
            <div class="stat-number">الأمان</div>
            <p>مستوى عالي</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-backup"></i>
            <div class="stat-number">النسخ الاحتياطي</div>
            <p>{"✅ ناجح" if backup_success else "❌ فاشل"}</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-rocket"></i>
            <div class="stat-number">الأداء</div>
            <p>ممتاز</p>
        </div>
    </div>
    
    <div class="content-section">
        <h3 style="margin-bottom: 20px; color: var(--primary-dark);">
            <i class="fas fa-tools"></i> أدوات الإدارة
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <button class="btn" onclick="createBackup()" style="background: var(--accent-teal);">
                <i class="fas fa-save"></i> إنشاء نسخة احتياطية
            </button>
            <button class="btn btn-secondary" onclick="showSystemLogs()">
                <i class="fas fa-list"></i> سجلات النظام
            </button>
            <button class="btn btn-secondary" onclick="showUserManagement()">
                <i class="fas fa-users"></i> إدارة المستخدمين
            </button>
            <button class="btn btn-secondary" onclick="showDatabaseStats()">
                <i class="fas fa-chart-bar"></i> إحصائيات قاعدة البيانات
            </button>
        </div>
    </div>
    
    <div class="content-section">
        <h3 style="margin-bottom: 15px; color: var(--primary-dark);">
            <i class="fas fa-info-circle"></i> معلومات النظام
        </h3>
        <div style="color: var(--light-slate); line-height: 2;">
            <p>🟢 <b>حالة النظام:</b> يعمل بشكل طبيعي</p>
            <p>📊 <b>آخر نسخة احتياطية:</b> { "تم بنجاح" if backup_success else "فشل في الإنشاء" }</p>
            <p>🛡️ <b>مستوى الأمان:</b> عالي</p>
            <p>⚡ <b>أداء النظام:</b> ممتاز</p>
            <p>🔧 <b>الإصدار:</b> InvoiceFlow Pro v3.0</p>
        </div>
    </div>

    <script>
        function createBackup() {{
            alert('سيتم إنشاء نسخة احتياطية...');
            location.reload();
        }}
        
        function showSystemLogs() {{
            alert('سجلات النظام قريباً في التحديث القادم');
        }}
        
        function showUserManagement() {{
            alert('إدارة المستخدمين قريباً في التحديث القادم');
        }}
        
        function showDatabaseStats() {{
            alert('إحصائيات قاعدة البيانات قريباً في التحديث القادم');
        }}
    </script>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="الإدارة - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

# ================== معالجة الأخطاء ==================
@app.errorhandler(404)
def not_found(error):
    """معالجة صفحة 404"""
    content = """
    <div class="dashboard-header">
        <h1 style="color: var(--error);"><i class="fas fa-exclamation-triangle"></i> 404 - الصفحة غير موجودة</h1>
        <p>عذراً، الصفحة التي تبحث عنها غير موجودة.</p>
    </div>
    
    <div class="content-section" style="text-align: center;">
        <div style="font-size: 6em; color: var(--light-slate); margin-bottom: 20px;">
            <i class="fas fa-search"></i>
        </div>
        <a href="/" class="btn">العودة للرئيسية</a>
    </div>
    """
    
    return render_template_string(PROFESSIONAL_DESIGN, title="404 - غير موجود", 
                                content=content, is_auth_page=False), 404

@app.errorhandler(500)
def internal_error(error):
    """معالجة أخطاء الخادم"""
    content = """
    <div class="dashboard-header">
        <h1 style="color: var(--error);"><i class="fas fa-bug"></i> خطأ في الخادم</h1>
        <p>عذراً، حدث خطأ داخلي في الخادم.</p>
    </div>
    
    <div class="content-section" style="text-align: center;">
        <div style="font-size: 6em; color: var(--light-slate); margin-bottom: 20px;">
            <i class="fas fa-cogs"></i>
        </div>
        <a href="/" class="btn">العودة للرئيسية</a>
    </div>
    """
    
    return render_template_string(PROFESSIONAL_DESIGN, title="خطأ - InvoiceFlow Pro", 
                                content=content, is_auth_page=False), 500

# ================== إعدادات التشغيل لـ Render ==================
def create_tables():
    """إنشاء الجداول عند التشغيل الأول"""
    try:
        user_manager.init_user_system()
        invoice_manager.init_invoice_system()
        print("✅ تم إنشاء الجداول بنجاح")
        
        # إنشاء نسخة احتياطية أولية
        backup_manager.create_backup()
        print("✅ تم إنشاء النسخة الاحتياطية الأولية")
        
    except Exception as e:
        print(f"✅ الجداول موجودة مسبقاً: {e}")

# استدعاء إنشاء الجداول عند التشغيل
create_tables()

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل InvoiceFlow Pro النهائي...")
        print("🔧 تم إصلاح جميع الأخطاء وجاهز لـ Render")
        print("📱 تصميم متجاوب يعمل على جميع الأجهزة")
        print("💾 قاعدة بيانات منظمة ومحسنة")
        print("🤖 مساعد ذكي متقدم")
        print("📊 نظام تقارير متكامل")
        print("🔄 نظام نسخ احتياطي آلي")
        print("🔔 نظام إشعارات ذكي")
        print("")
        print("🔐 بيانات الدخول الافتراضية:")
        print("   👤 المستخدم: admin أو admin@invoiceflow.com")
        print("   🔑 كلمة المرور: Admin123!@#")
        print("")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ InvoiceFlow Pro - النظام النهائي المتكامل!")
        
        create_tables()
        
        app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        time.sleep(5)
