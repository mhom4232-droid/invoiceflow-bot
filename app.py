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
from email_validator import validate_email, EmailNotValidError

# ================== تطبيق Flask المتقدم ==================
app = Flask(__name__)
app.secret_key = 'invoiceflow_elite_professional_2024_v3'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Elite - الإصدار النخبوي المتميز")
print("🚀 تصميم بيج/بني فاخر + واجهات قوية + ذكاء اصطناعي متقدم")
print("👑 فريق النخبة البروفيسوري المتكامل")
print("=" * 80)

# ================== نظام قاعدة البيانات المحسن ==================
class EliteDatabaseManager:
    def __init__(self):
        self.db_path = 'invoices_elite.db'
        self.init_elite_database()

    def init_elite_database(self):
        """تهيئة قاعدة البيانات النخبوية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # جدول الفواتير المحسن
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS elite_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id TEXT UNIQUE,
                    user_id TEXT,
                    user_name TEXT,
                    company_name TEXT,
                    client_name TEXT,
                    client_email TEXT,
                    client_phone TEXT,
                    client_address TEXT,
                    services_json TEXT,
                    subtotal REAL,
                    tax_rate REAL DEFAULT 0.0,
                    tax_amount REAL DEFAULT 0.0,
                    total_amount REAL,
                    issue_date TEXT,
                    due_date TEXT,
                    payment_terms TEXT DEFAULT '30 يوم',
                    notes TEXT,
                    pdf_path TEXT,
                    status TEXT DEFAULT 'معلقة',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # جدول العملاء
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    client_name TEXT,
                    client_email TEXT,
                    client_phone TEXT,
                    client_address TEXT,
                    company_name TEXT,
                    tax_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # جدول الخدمات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    service_name TEXT,
                    service_description TEXT,
                    service_price REAL,
                    category TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            print("✅ قاعدة البيانات النخبوية جاهزة")
        except Exception as e:
            print(f"🔧 خطأ في قاعدة البيانات: {e}")

    def save_elite_invoice(self, invoice_data):
        """حفظ فاتورة نخبوية مع بيانات إضافية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO elite_invoices 
                (invoice_id, user_id, user_name, company_name, client_name, 
                 client_email, client_phone, client_address, services_json, 
                 subtotal, tax_rate, tax_amount, total_amount, issue_date, 
                 due_date, payment_terms, notes, pdf_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_id'],
                invoice_data.get('user_id', 'web_user'),
                invoice_data.get('user_name', 'مستخدم النخبة'),
                invoice_data.get('company_name', 'شركة النخبة'),
                invoice_data['client_name'],
                invoice_data.get('client_email', ''),
                invoice_data.get('client_phone', ''),
                invoice_data.get('client_address', ''),
                json.dumps(invoice_data['services'], ensure_ascii=False),
                invoice_data.get('subtotal', 0),
                invoice_data.get('tax_rate', 0),
                invoice_data.get('tax_amount', 0),
                invoice_data['total_amount'],
                invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                invoice_data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')),
                invoice_data.get('payment_terms', '30 يوم'),
                invoice_data.get('notes', ''),
                invoice_data.get('pdf_path', ''),
                invoice_data.get('status', 'معلقة')
            ))

            conn.commit()
            conn.close()
            print(f"✅ تم حفظ الفاتورة النخبوية: {invoice_data['invoice_id']}")
            return True
        except Exception as e:
            print(f"🔧 خطأ في حفظ الفاتورة: {e}")
            return False

    def get_user_elite_invoices(self, username):
        """جلب فواتير مستخدم نخبوية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT invoice_id, client_name, total_amount, issue_date, due_date, 
                       status, services_json, pdf_path
                FROM elite_invoices 
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
                    'due_date': invoice[4],
                    'status': invoice[5],
                    'services': json.loads(invoice[6]) if invoice[6] else [],
                    'pdf_path': invoice[7]
                })
            return result
        except Exception as e:
            print(f"🔧 خطأ في جلب الفواتير: {e}")
            return []

    def get_elite_stats(self, username):
        """إحصائيات نخبوية للمستخدم"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إجمالي الفواتير
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM elite_invoices WHERE user_id = ?', (username,))
            total_invoices, total_revenue = cursor.fetchone()
            
            # الفواتير المعلقة
            cursor.execute('SELECT COUNT(*) FROM elite_invoices WHERE user_id = ? AND status = "معلقة"', (username,))
            pending_invoices = cursor.fetchone()[0]
            
            # فواتير اليوم
            cursor.execute('SELECT COUNT(*) FROM elite_invoices WHERE user_id = ? AND date(created_at) = date("now")', (username,))
            today_invoices = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_invoices': total_invoices or 0,
                'total_revenue': total_revenue or 0,
                'pending_invoices': pending_invoices or 0,
                'today_invoices': today_invoices or 0
            }
        except Exception as e:
            print(f"🔧 خطأ في جلب الإحصائيات: {e}")
            return {'total_invoices': 0, 'total_revenue': 0, 'pending_invoices': 0, 'today_invoices': 0}

# ================== نظام PDF النخبوي ==================
class ElitePDFGenerator:
    def __init__(self):
        self.setup_elite_fonts()
    
    def setup_elite_fonts(self):
        """إعداد خطوط النخبة"""
        try:
            self.primary_font = 'Helvetica'
            self.bold_font = 'Helvetica-Bold'
            print("✅ خطوط النخبة جاهزة")
        except Exception as e:
            print(f"⚠️  استخدام الخطوط الافتراضية: {e}")

    def create_elite_invoice(self, invoice_data):
        """إنشاء فاتورة نخبوية فاخرة"""
        try:
            os.makedirs('elite_invoices', exist_ok=True)
            safe_filename = f"{invoice_data['invoice_id']}_elite.pdf"
            file_path = f"elite_invoices/{safe_filename}"
            
            # إنشاء PDF نخبوي
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=50,
                bottomMargin=50
            )
            
            elements = []
            styles = self.get_elite_styles()
            
            # الهيدر الفاخر
            header_data = [
                ['INVOICEFLOW ELITE', 'فاتورة رسمية'],
                ['نظام الفواتير النخبوي', f"رقم: {invoice_data['invoice_id']}"],
                ['', f"التاريخ: {invoice_data['issue_date']}"]
            ]
            
            header_table = Table(header_data, colWidths=[3*inch, 3*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8B7355')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), self.bold_font),
                ('FONTSIZE', (0,0), (-1,0), 16),
                ('BOTTOMPADDING', (0,0), (-1,0), 15),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F5F5DC')),
                ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#8B7355')),
                ('FONTNAME', (0,1), (-1,1), self.primary_font),
                ('FONTSIZE', (0,1), (-1,1), 10),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 25))
            
            # معلومات الشركة والعميل
            company_info = [
                ['معلومات الشركة', 'معلومات العميل'],
                [invoice_data.get('company_name', 'شركة النخبة'), invoice_data['client_name']],
                ['السجل التجاري: 1234567890', invoice_data.get('client_email', '')],
                ['الهاتف: +966500000000', invoice_data.get('client_phone', '')],
                ['البريد: info@elite.com', invoice_data.get('client_address', '')]
            ]
            
            company_table = Table(company_info, colWidths=[3*inch, 3*inch])
            company_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D2B48C')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), self.bold_font),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#8B7355')),
                ('FONTSIZE', (0,0), (-1,-1), 10),
            ]))
            elements.append(company_table)
            elements.append(Spacer(1, 20))
            
            # جدول الخدمات النخبوي
            service_data = [['الخدمة', 'الوصف', 'الكمية', 'السعر', 'المجموع']]
            subtotal = 0
            
            for service in invoice_data['services']:
                quantity = service.get('quantity', 1)
                price = service['price']
                total = quantity * price
                subtotal += total
                
                service_data.append([
                    service['name'],
                    service.get('description', ''),
                    str(quantity),
                    f"${price:.2f}",
                    f"${total:.2f}"
                ])
            
            # الحسابات النهائية
            tax_rate = invoice_data.get('tax_rate', 0)
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            service_data.append(['', '', '', 'المجموع الفرعي:', f"${subtotal:.2f}"])
            service_data.append(['', '', '', f'الضريبة ({tax_rate}%):', f"${tax_amount:.2f}"])
            service_data.append(['', '', '', 'الإجمالي النهائي:', f"${total_amount:.2f}"])
            
            service_table = Table(service_data, colWidths=[1.5*inch, 2*inch, 0.7*inch, 0.9*inch, 1*inch])
            service_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8B7355')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), self.bold_font),
                ('FONTSIZE', (0,0), (-1,0), 11),
                ('BACKGROUND', (0,1), (-1,-4), colors.HexColor('#FAF0E6')),
                ('BACKGROUND', (0,-3), (-1,-1), colors.HexColor('#F5F5DC')),
                ('FONTNAME', (0,-3), (-1,-1), self.bold_font),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#D2B48C')),
            ]))
            elements.append(service_table)
            elements.append(Spacer(1, 25))
            
            # التذييل النخبوي
            footer_data = [
                ['شروط الدفع', 'ملاحظات إضافية'],
                [invoice_data.get('payment_terms', '30 يوم'), invoice_data.get('notes', 'شكراً لتعاملكم معنا')],
                ['خصم 5% للدفع خلال 15 يوم', 'للاستفسارات: support@elite.com'],
                ['', f"تاريخ الاستحقاق: {invoice_data.get('due_date', '')}"]
            ]
            
            footer_table = Table(footer_data, colWidths=[3*inch, 3*inch])
            footer_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#D2B48C')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), self.bold_font),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#8B7355')),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            elements.append(footer_table)
            
            # بناء PDF
            doc.build(elements)
            print(f"✅ تم إنشاء فاتورة نخبوية: {file_path}")
            return file_path, None
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF نخبوي: {e}")
            return None, str(e)

    def get_elite_styles(self):
        """الحصول على أنماط النخبة"""
        styles = getSampleStyleSheet()
        return styles

# ================== نظام الذكاء الاصطناعي النخبوي ==================
class EliteAIAssistant:
    def __init__(self):
        self.analysis_models = {}
        
    def comprehensive_analysis(self, user_invoices, user_stats):
        """تحليل شامل متقدم"""
        if not user_invoices:
            return self.get_empty_analysis()
        
        analysis = {
            'performance_score': self.calculate_performance_score(user_stats),
            'revenue_trend': self.analyze_revenue_trend(user_invoices),
            'client_insights': self.analyze_clients(user_invoices),
            'service_recommendations': self.generate_service_recommendations(user_invoices),
            'growth_opportunities': self.identify_growth_opportunities(user_stats)
        }
        
        return analysis
    
    def calculate_performance_score(self, stats):
        """حساب درجة الأداء"""
        score = 0
        if stats['total_invoices'] > 10:
            score += 30
        if stats['total_revenue'] > 1000:
            score += 40
        if stats['pending_invoices'] < 3:
            score += 30
        
        return min(score, 100)
    
    def analyze_revenue_trend(self, invoices):
        """تحليل اتجاهات الإيرادات"""
        if len(invoices) < 2:
            return "ثابت"
        
        recent_avg = sum(inv['total_amount'] for inv in invoices[:3]) / 3
        older_avg = sum(inv['total_amount'] for inv in invoices[-3:]) / 3
        
        if recent_avg > older_avg * 1.1:
            return "تصاعدي 📈"
        elif recent_avg < older_avg * 0.9:
            return "تنازلي 📉"
        else:
            return "مستقر ↔️"
    
    def analyze_clients(self, invoices):
        """تحليل قاعدة العملاء"""
        clients = {}
        for invoice in invoices:
            client = invoice['client_name']
            if client in clients:
                clients[client] += 1
            else:
                clients[client] = 1
        
        if not clients:
            return "لا توجد بيانات كافية"
        
        top_client = max(clients, key=clients.get)
        return f"أفضل عملائك: {top_client} ({clients[top_client]} معاملة)"
    
    def generate_service_recommendations(self, invoices):
        """توليد توصيات خدمات مخصصة"""
        service_categories = {}
        for invoice in invoices:
            for service in invoice.get('services', []):
                category = self.categorize_service(service['name'])
                if category in service_categories:
                    service_categories[category] += 1
                else:
                    service_categories[category] = 1
        
        if not service_categories:
            return ["تطوير مواقع ويب", "استشارات تقنية", "تصميم جرافيك"]
        
        top_category = max(service_categories, key=service_categories.get)
        return self.get_category_recommendations(top_category)
    
    def categorize_service(self, service_name):
        """تصنيف الخدمات"""
        tech_keywords = ['موقع', 'ويب', 'برمجة', 'تطبيق', 'سوفتوير']
        design_keywords = ['تصميم', 'شعار', 'جرافيك', 'هوية']
        
        if any(keyword in service_name for keyword in tech_keywords):
            return 'تكنولوجيا'
        elif any(keyword in service_name for keyword in design_keywords):
            return 'تصميم'
        else:
            return 'استشارات'
    
    def get_category_recommendations(self, category):
        """الحصول على توصيات حسب التصنيف"""
        recommendations = {
            'تكنولوجيا': ['تطبيقات جوال متقدمة', 'أنظمة إدارة محتوى', 'حلول سحابية'],
            'تصميم': ['هوية بصرية متكاملة', 'تصميم واجهات مستخدم', 'مواد تسويقية'],
            'استشارات': ['دراسات جدوى متقدمة', 'خطط عمل استراتيجية', 'تحليل أسواق']
        }
        return recommendations.get(category, ['خدمات متخصصة', 'حلول مخصصة'])
    
    def identify_growth_opportunities(self, stats):
        """تحديد فرص النمو"""
        opportunities = []
        
        if stats['total_invoices'] < 5:
            opportunities.append("تنويع قاعدة العملاء")
        if stats['total_revenue'] / max(stats['total_invoices'], 1) < 200:
            opportunities.append("رفع قيمة الخدمات المقدمة")
        if stats['pending_invoices'] > 2:
            opportunities.append("تحسين متابعة المدفوعات")
        
        return opportunities if opportunities else ["الحفاظ على الأداء المتميز"]
    
    def get_empty_analysis(self):
        """تحليل للبيانات الفارغة"""
        return {
            'performance_score': 0,
            'revenue_trend': "غير محدد",
            'client_insights': "ابدأ بإنشاء فاتورتك الأولى",
            'service_recommendations': ["تطوير مواقع ويب", "استشارات تقنية", "تصميم جرافيك"],
            'growth_opportunities': ["إنشاء فواتير جديدة", "جذب عملاء جدد"]
        }

# ================== نظام إدارة المستخدمين النخبوي ==================
class EliteUserManager:
    def __init__(self):
        self.db_path = 'invoices_elite.db'
        self.init_elite_users_table()

    def init_elite_users_table(self):
        """تهيئة جدول المستخدمين النخبوي"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS elite_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    email TEXT UNIQUE,
                    full_name TEXT,
                    company_name TEXT,
                    phone TEXT,
                    user_type TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    subscription_tier TEXT DEFAULT 'basic',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    profile_data TEXT DEFAULT '{}'
                )
            ''')

            # 🔐 إضافة المدير النخبوي
            admin_password = self.hash_password("EliteMaster2024!@#")
            cursor.execute('''
                INSERT OR IGNORE INTO elite_users 
                (username, password_hash, email, full_name, company_name, user_type, subscription_tier) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_password, 'admin@elite.com', 'المدير النخبوي', 'شركة النخبة', 'admin', 'premium'))

            conn.commit()
            conn.close()
            print("✅ نظام المستخدمين النخبوي جاهز")
        except Exception as e:
            print(f"🔧 خطأ في نظام المستخدمين: {e}")

    def hash_password(self, password):
        """تشفير كلمة المرور النخبوي"""
        salt = "elite_invoice_system_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def verify_elite_user(self, username, password):
        """التحقق من المستخدم النخبوي"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT password_hash, user_type, email, full_name, company_name, subscription_tier
                FROM elite_users WHERE username = ? AND is_active = 1
            ''', (username,))
            result = cursor.fetchone()
            
            if result and result[0] == self.hash_password(password):
                # تحديث آخر دخول
                cursor.execute('UPDATE elite_users SET last_login = ? WHERE username = ?', 
                             (datetime.now(), username))
                conn.commit()
                conn.close()
                return True, result[1], result[2], result[3], result[4], result[5]
            conn.close()
            return False, 'user', '', '', '', 'basic'
        except Exception as e:
            print(f"🔧 خطأ في التحقق من المستخدم: {e}")
            return False, 'user', '', '', '', 'basic'

    def create_elite_user(self, username, password, email, full_name, company_name='', phone=''):
        """إنشاء مستخدم نخبوي جديد"""
        try:
            # التحقق من البريد الإلكتروني
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                return False, f"بريد إلكتروني غير صحيح: {str(e)}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO elite_users (username, password_hash, email, full_name, company_name, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, company_name, phone))
            
            conn.commit()
            conn.close()
            return True, "تم إنشاء الحساب النخبوي بنجاح"
        except sqlite3.IntegrityError:
            return False, "اسم المستخدم أو البريد الإلكتروني موجود مسبقاً"
        except Exception as e:
            print(f"🔧 خطأ في إنشاء المستخدم: {e}")
            return False, f"خطأ في إنشاء الحساب: {str(e)}"

    def get_elite_profile(self, username):
        """جلب الملف الشخصي النخبوي"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, email, full_name, company_name, phone, 
                       user_type, subscription_tier, created_at, last_login, profile_data
                FROM elite_users WHERE username = ?
            ''', (username,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'username': result[0],
                    'email': result[1],
                    'full_name': result[2],
                    'company_name': result[3],
                    'phone': result[4],
                    'user_type': result[5],
                    'subscription_tier': result[6],
                    'created_at': result[7],
                    'last_login': result[8],
                    'profile_data': json.loads(result[9]) if result[9] else {}
                }
            return None
        except Exception as e:
            print(f"🔧 خطأ في جلب الملف الشخصي: {e}")
            return None

# ================== إعداد الأنظمة النخبوية ==================
elite_db = EliteDatabaseManager()
elite_pdf = ElitePDFGenerator()
elite_ai = EliteAIAssistant()
elite_users = EliteUserManager()

# ================== نظام الإبقاء على التشغيل ==================
class EliteKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.ping_count = 0
        
    def start_elite_keep_alive(self):
        print("🔄 بدء أنظمة النخبة...")
        self.start_elite_monitoring()
        print("✅ أنظمة النخبة مفعلة!")
    
    def start_elite_monitoring(self):
        def monitor():
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                if int(current_time) % 600 == 0:
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"📊 تقرير النخبة: {hours}س {minutes}د - {self.ping_count} زيارات نخبوية")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# إعداد نظام النخبة
keep_alive_system = EliteKeepAlive()
keep_alive_system.start_elite_keep_alive()

# ================== التصميم النخبوي (بيج/بني) ==================
ELITE_DESIGN_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            /* الألوان النخبوية - بيج/بني */
            --primary-beige: #F5F5DC;
            --light-beige: #FAF0E6;
            --dark-beige: #F5E6D3;
            --primary-brown: #8B7355;
            --dark-brown: #654321;
            --light-brown: #A0522D;
            --accent-gold: #D4AF37;
            --text-dark: #2C1810;
            --text-light: #5D4037;
            --success: #27AE60;
            --warning: #F39C12;
            --danger: #E74C3C;
            --shadow: rgba(139, 115, 85, 0.2);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
            background: linear-gradient(135deg, var(--primary-beige) 0%, var(--light-beige) 100%);
            color: var(--text-dark);
            min-height: 100vh;
            line-height: 1.7;
        }
        
        .elite-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
        }
        
        .elite-header {
            background: linear-gradient(135deg, var(--primary-brown) 0%, var(--dark-brown) 100%);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            border: 2px solid var(--accent-gold);
            box-shadow: 0 15px 35px var(--shadow);
            position: relative;
            overflow: hidden;
        }
        
        .elite-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-gold), var(--primary-brown));
        }
        
        .header-content h1 {
            font-size: 3.8em;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-gold), var(--light-beige));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-content p {
            font-size: 1.4em;
            color: var(--light-beige);
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .elite-user-panel {
            position: absolute;
            left: 40px;
            top: 40px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 15px 25px;
            border-radius: 15px;
            border: 1px solid var(--accent-gold);
            color: var(--light-beige);
        }
        
        .elite-admin-badge {
            background: linear-gradient(135deg, var(--accent-gold), var(--primary-brown));
            color: var(--text-dark);
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 700;
            margin-left: 10px;
            border: 1px solid var(--accent-gold);
        }
        
        .elite-navigation {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .elite-nav-card {
            background: linear-gradient(135deg, var(--light-beige) 0%, var(--dark-beige) 100%);
            border-radius: 20px;
            padding: 35px 30px;
            text-align: center;
            color: var(--text-dark);
            text-decoration: none;
            transition: all 0.4s ease;
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 25px var(--shadow);
        }
        
        .elite-nav-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-brown), var(--accent-gold));
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }
        
        .elite-nav-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px var(--shadow);
            border-color: var(--primary-brown);
        }
        
        .elite-nav-card:hover::before {
            transform: scaleX(1);
        }
        
        .elite-nav-card i {
            font-size: 3.5em;
            margin-bottom: 25px;
            background: linear-gradient(135deg, var(--primary-brown), var(--dark-brown));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            transition: all 0.4s ease;
        }
        
        .elite-nav-card:hover i {
            transform: scale(1.1);
        }
        
        .elite-nav-card h3 {
            font-size: 1.6em;
            margin-bottom: 15px;
            color: var(--dark-brown);
            font-weight: 700;
        }
        
        .elite-nav-card p {
            color: var(--text-light);
            font-size: 1.1em;
            line-height: 1.6;
        }
        
        .elite-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }
        
        .elite-stat-card {
            background: linear-gradient(135deg, var(--light-beige) 0%, var(--primary-beige) 100%);
            border-radius: 20px;
            padding: 35px 30px;
            text-align: center;
            border: 2px solid var(--dark-beige);
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 25px var(--shadow);
        }
        
        .elite-stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-brown), var(--accent-gold));
        }
        
        .elite-stat-number {
            font-size: 4em;
            font-weight: 800;
            margin: 20px 0;
            background: linear-gradient(135deg, var(--dark-brown), var(--primary-brown));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .elite-stat-card p {
            font-size: 1.3em;
            color: var(--text-light);
            font-weight: 600;
        }
        
        .elite-ai-section {
            background: linear-gradient(135deg, var(--light-beige) 0%, var(--dark-beige) 100%);
            border-radius: 20px;
            padding: 35px;
            margin: 30px 0;
            border: 2px solid var(--primary-brown);
            box-shadow: 0 10px 30px var(--shadow);
        }
        
        .elite-btn {
            background: linear-gradient(135deg, var(--primary-brown), var(--dark-brown));
            color: var(--light-beige);
            padding: 18px 40px;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin: 8px;
            box-shadow: 0 5px 15px var(--shadow);
        }
        
        .elite-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(139, 115, 85, 0.4);
            background: linear-gradient(135deg, var(--dark-brown), var(--primary-brown));
        }
        
        .elite-btn-secondary {
            background: transparent;
            border: 2px solid var(--primary-brown);
            color: var(--primary-brown);
        }
        
        .elite-btn-secondary:hover {
            background: var(--primary-brown);
            color: var(--light-beige);
        }
        
        .elite-form-group {
            margin-bottom: 30px;
        }
        
        .elite-form-group label {
            display: block;
            margin-bottom: 12px;
            color: var(--dark-brown);
            font-weight: 700;
            font-size: 1.2em;
        }
        
        .elite-form-control {
            width: 100%;
            padding: 18px 25px;
            border: 2px solid var(--dark-beige);
            border-radius: 15px;
            background: var(--light-beige);
            color: var(--text-dark);
            font-size: 1.1em;
            transition: all 0.3s ease;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .elite-form-control:focus {
            outline: none;
            border-color: var(--primary-brown);
            background: var(--primary-beige);
            box-shadow: 0 0 0 3px rgba(139, 115, 85, 0.2);
        }
        
        .elite-alert {
            padding: 25px 30px;
            border-radius: 15px;
            margin: 25px 0;
            text-align: center;
            font-weight: 600;
            border: 2px solid;
            backdrop-filter: blur(10px);
            font-size: 1.1em;
        }
        
        .elite-alert-success {
            background: rgba(39, 174, 96, 0.1);
            border-color: var(--success);
            color: var(--success);
        }
        
        .elite-alert-error {
            background: rgba(231, 76, 60, 0.1);
            border-color: var(--danger);
            color: var(--danger);
        }
        
        .elite-alert-warning {
            background: rgba(243, 156, 18, 0.1);
            border-color: var(--warning);
            color: var(--warning);
        }
        
        .elite-login-container {
            max-width: 480px;
            margin: 80px auto;
        }
        
        .elite-profile-section {
            background: linear-gradient(135deg, var(--light-beige) 0%, var(--primary-beige) 100%);
            border-radius: 20px;
            padding: 35px;
            margin: 25px 0;
            border: 2px solid var(--dark-beige);
            box-shadow: 0 8px 25px var(--shadow);
        }
        
        .elite-feature-list {
            list-style: none;
            margin: 25px 0;
        }
        
        .elite-feature-list li {
            padding: 15px 0;
            border-bottom: 1px solid var(--dark-beige);
            color: var(--text-dark);
            font-size: 1.1em;
            position: relative;
            padding-right: 40px;
        }
        
        .elite-feature-list li:before {
            content: '✓';
            position: absolute;
            right: 0;
            color: var(--success);
            font-weight: bold;
            font-size: 1.3em;
        }
        
        .elite-service-item {
            background: var(--light-beige);
            border: 2px solid var(--dark-beige);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .elite-service-item:hover {
            border-color: var(--primary-brown);
            transform: translateX(-5px);
        }
        
        @media (max-width: 768px) {
            .elite-container {
                padding: 15px;
            }
            
            .elite-header {
                padding: 25px;
            }
            
            .header-content h1 {
                font-size: 2.5em;
            }
            
            .elite-user-panel {
                position: relative;
                left: auto;
                top: auto;
                margin-bottom: 20px;
                text-align: center;
            }
            
            .elite-navigation {
                grid-template-columns: 1fr;
            }
            
            .elite-stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="elite-container">
        {% if session.user_logged_in %}
        <div class="elite-user-panel">
            {% if session.user_type == 'admin' %}
            <span class="elite-admin-badge">👑 نخبة</span>
            {% endif %}
            <i class="fas fa-user-tie"></i> {{ session.username }}
            | <a href="/elite/profile" style="color: var(--accent-gold); margin: 0 15px;">الملف الشخصي</a>
            | <a href="/elite/logout" style="color: var(--light-beige);">تسجيل خروج</a>
        </div>
        {% endif %}
        
        <div class="elite-header">
            <div class="header-content">
                <h1><i class="fas fa-crown"></i> InvoiceFlow Elite</h1>
                <p>🚀 النظام النخبوي لإدارة الفواتير - التميز في كل تفصيل</p>
                <p>⏰ مدة التشغيل: {{ uptime }}</p>
            </div>
        </div>
        
        {% if session.user_logged_in %}
        <div class="elite-navigation">
            <a href="/" class="elite-nav-card">
                <i class="fas fa-home"></i>
                <h3>الرئيسية</h3>
                <p>لوحة التحكم الشاملة والإحصائيات المتقدمة</p>
            </a>
            <a href="/elite/invoices" class="elite-nav-card">
                <i class="fas fa-file-invoice-dollar"></i>
                <h3>الفواتير</h3>
                <p>إدارة وعرض وتتبع الفواتير النخبوية</p>
            </a>
            <a href="/elite/create" class="elite-nav-card">
                <i class="fas fa-plus-circle"></i>
                <h3>إنشاء فاتورة</h3>
                <p>إنشاء فاتورة نخبوية جديدة بتصميم فاخر</p>
            </a>
            {% if session.user_type == 'admin' %}
            <a href="/elite/admin" class="elite-nav-card">
                <i class="fas fa-crown"></i>
                <h3>لوحة التحكم</h3>
                <p>الإدارة المتقدمة والنخبوية للنظام</p>
            </a>
            {% endif %}
            <a href="/elite/profile" class="elite-nav-card">
                <i class="fas fa-user-cog"></i>
                <h3>الملف الشخصي</h3>
                <p>بياناتك الشخصية وإعدادات الحساب</p>
            </a>
            <a href="/elite/ai" class="elite-nav-card">
                <i class="fas fa-robot"></i>
                <h3>الذكاء الاصطناعي</h3>
                <p>تحليلات متقدمة وتوصيات ذكية مخصصة</p>
            </a>
        </div>
        {% endif %}

        {{ content | safe }}
    </div>

    <script>
        // تأثيرات النخبة
        document.addEventListener('DOMContentLoaded', function() {
            // تأثيرات الكروت
            const cards = document.querySelectorAll('.elite-nav-card, .elite-stat-card');
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px) scale(1.02)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
            
            // تأثيرات الأزرار
            const buttons = document.querySelectorAll('.elite-btn');
            buttons.forEach(btn => {
                btn.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-3px)';
                });
                btn.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
            
            // تحميل متحرك للصفحة
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
        });
        
        // تأثيرات إضافية للواجهات
        function animateValue(element, start, end, duration) {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                element.innerHTML = Math.floor(progress * (end - start) + start);
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        }
        
        // تفعيل العدادات المتحركة
        document.addEventListener('DOMContentLoaded', function() {
            const counters = document.querySelectorAll('.elite-stat-number');
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target'));
                if (!isNaN(target)) {
                    animateValue(counter, 0, target, 2000);
                }
            });
        });
    </script>
</body>
</html>
"""

# ================== Routes النخبوية المصححة ==================
@app.route('/')
def elite_home():
    """الصفحة الرئيسية النخبوية"""
    if 'user_logged_in' not in session:
        return redirect(url_for('elite_login'))
    
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    # جلب الإحصائيات النخبوية
    stats = elite_db.get_elite_stats(session['username'])
    user_invoices = elite_db.get_user_elite_invoices(session['username'])
    ai_analysis = elite_ai.comprehensive_analysis(user_invoices, stats)
    
    # إصلاح الخطأ: استخدام علامات اقتباس مختلفة
    admin_button = ''
    if session.get('user_type') == 'admin':
        admin_button = '<a href="/elite/admin" class="elite-btn" style="background: linear-gradient(135deg, var(--accent-gold), var(--primary-brown));"><i class="fas fa-crown"></i> لوحة التحكم</a>'
    
    content = f"""
    <div class="elite-stats-grid">
        <div class="elite-stat-card">
            <i class="fas fa-file-invoice" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number" data-target="{stats['total_invoices']}">{stats['total_invoices']}</div>
            <p>إجمالي الفواتير</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-dollar-sign" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number" data-target="{int(stats['total_revenue'])}">${stats['total_revenue']:,.0f}</div>
            <p>إجمالي الإيرادات</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-clock" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number" data-target="{stats['pending_invoices']}">{stats['pending_invoices']}</div>
            <p>فواتير معلقة</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-chart-line" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number" data-target="{int(ai_analysis['performance_score'])}">{ai_analysis['performance_score']}%</div>
            <p>درجة الأداء</p>
        </div>
    </div>
    
    <div class="elite-ai-section">
        <h2 style="margin-bottom: 25px; text-align: center; color: var(--dark-brown);">
            <i class="fas fa-robot"></i> لوحة التحليل الذكي
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
            <div>
                <h3 style="color: var(--primary-brown); margin-bottom: 15px;">📊 أداؤك</h3>
                <div style="background: var(--primary-beige); padding: 20px; border-radius: 15px; border: 2px solid var(--dark-beige);">
                    <p><strong>اتجاه الإيرادات:</strong> {ai_analysis['revenue_trend']}</p>
                    <p><strong>رؤى العملاء:</strong> {ai_analysis['client_insights']}</p>
                    <p><strong>درجة الأداء:</strong> {ai_analysis['performance_score']}%</p>
                </div>
            </div>
            
            <div>
                <h3 style="color: var(--primary-brown); margin-bottom: 15px;">💡 فرص النمو</h3>
                <div style="background: var(--primary-beige); padding: 20px; border-radius: 15px; border: 2px solid var(--dark-beige);">
                    {''.join([f'<p>• {opportunity}</p>' for opportunity in ai_analysis['growth_opportunities']])}
                </div>
            </div>
        </div>
        
        <div>
            <h3 style="color: var(--primary-brown); margin-bottom: 15px;">🎯 توصيات الخدمات</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                {''.join([f'<div class="elite-service-item">{service}</div>' for service in ai_analysis['service_recommendations']])}
            </div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 40px;">
        <div class="elite-profile-section">
            <h3 style="margin-bottom: 20px; color: var(--dark-brown);">
                <i class="fas fa-bolt"></i> إجراءات سريعة
            </h3>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <a href="/elite/create" class="elite-btn">
                    <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
                </a>
                <a href="/elite/invoices" class="elite-btn elite-btn-secondary">
                    <i class="fas fa-list"></i> عرض جميع الفواتير
                </a>
                {admin_button}
            </div>
        </div>
        
        <div class="elite-profile-section">
            <h3 style="margin-bottom: 20px; color: var(--dark-brown);">
                <i class="fas fa-star"></i> مزايا النخبة
            </h3>
            <ul class="elite-feature-list">
                <li>فواتير PDF نخبوية فاخرة</li>
                <li>تحليلات ذكاء اصطناعي متقدمة</li>
                <li>تصميم بيج/بني فاخر</li>
                <li>نظام أمني متكامل</li>
                <li>واجهات مستخدم قوية</li>
            </ul>
        </div>
    </div>
    """
    
    return render_template_string(ELITE_DESIGN_HTML, title="InvoiceFlow Elite - النظام النخبوي", uptime=uptime_str, content=content)

@app.route('/elite/login', methods=['GET', 'POST'])
def elite_login():
    """صفحة تسجيل الدخول النخبوية"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        is_valid, user_type, email, full_name, company_name, subscription_tier = elite_users.verify_elite_user(username, password)
        
        if is_valid:
            session['user_logged_in'] = True
            session['username'] = username
            session['user_type'] = user_type
            session['email'] = email
            session['full_name'] = full_name
            session['company_name'] = company_name
            session['subscription_tier'] = subscription_tier
            session.permanent = True
            
            return redirect(url_for('elite_home'))
        else:
            content = """
            <div class="elite-login-container">
                <div class="elite-header">
                    <h2 style="margin-bottom: 30px; text-align: center;">تسجيل الدخول النخبوي</h2>
                    <div class="elite-alert elite-alert-error">
                        <i class="fas fa-exclamation-triangle"></i> بيانات الدخول غير صحيحة
                    </div>
                    <form method="POST">
                        <div class="elite-form-group">
                            <input type="text" name="username" class="elite-form-control" placeholder="اسم المستخدم النخبوي" required>
                        </div>
                        <div class="elite-form-group">
                            <input type="password" name="password" class="elite-form-control" placeholder="كلمة المرور" required>
                        </div>
                        <button type="submit" class="elite-btn" style="width: 100%;">
                            <i class="fas fa-sign-in-alt"></i> دخول النخبة
                        </button>
                    </form>
                    <div style="margin-top: 25px; text-align: center;">
                        <a href="/elite/register" class="elite-btn elite-btn-secondary" style="width: 100%;">
                            <i class="fas fa-user-plus"></i> انضم إلى النخبة
                        </a>
                    </div>
                </div>
            </div>
            """
            return render_template_string(ELITE_DESIGN_HTML, title="تسجيل الدخول - InvoiceFlow Elite", uptime="", content=content)
    
    if 'user_logged_in' in session:
        return redirect(url_for('elite_home'))
    
    content = """
    <div class="elite-login-container">
        <div class="elite-header">
            <h2 style="margin-bottom: 30px; text-align: center;">تسجيل الدخول النخبوي</h2>
            <form method="POST">
                <div class="elite-form-group">
                    <input type="text" name="username" class="elite-form-control" placeholder="اسم المستخدم النخبوي" required>
                </div>
                <div class="elite-form-group">
                    <input type="password" name="password" class="elite-form-control" placeholder="كلمة المرور" required>
                </div>
                <button type="submit" class="elite-btn" style="width: 100%;">
                    <i class="fas fa-sign-in-alt"></i> دخول النخبة
                </button>
            </form>
            <div style="margin-top: 25px; text-align: center;">
                <a href="/elite/register" class="elite-btn elite-btn-secondary" style="width: 100%;">
                    <i class="fas fa-user-plus"></i> انضم إلى النخبة
                </a>
            </div>
        </div>
    </div>
    """
    return render_template_string(ELITE_DESIGN_HTML, title="تسجيل الدخول - InvoiceFlow Elite", uptime="", content=content)

@app.route('/elite/register', methods=['GET', 'POST'])
def elite_register():
    """صفحة التسجيل النخبوية"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        company_name = request.form.get('company_name', '')
        phone = request.form.get('phone', '')
        
        success, message = elite_users.create_elite_user(username, password, email, full_name, company_name, phone)
        
        if success:
            content = f"""
            <div class="elite-login-container">
                <div class="elite-header">
                    <div class="elite-alert elite-alert-success">
                        <i class="fas fa-check-circle"></i> {message}
                    </div>
                    <div style="text-align: center; margin-top: 25px;">
                        <a href="/elite/login" class="elite-btn">
                            <i class="fas fa-sign-in-alt"></i> الانتقال لتسجيل الدخول
                        </a>
                    </div>
                </div>
            </div>
            """
            return render_template_string(ELITE_DESIGN_HTML, title="تم الإنشاء - InvoiceFlow Elite", uptime="", content=content)
        else:
            content = f"""
            <div class="elite-login-container">
                <div class="elite-header">
                    <div class="elite-alert elite-alert-error">
                        <i class="fas fa-exclamation-triangle"></i> {message}
                    </div>
                    <form method="POST">
                        <div class="elite-form-group">
                            <input type="text" name="username" class="elite-form-control" placeholder="اسم المستخدم" value="{username}" required>
                        </div>
                        <div class="elite-form-group">
                            <input type="password" name="password" class="elite-form-control" placeholder="كلمة المرور" required>
                        </div>
                        <div class="elite-form-group">
                            <input type="email" name="email" class="elite-form-control" placeholder="البريد الإلكتروني" value="{email}" required>
                        </div>
                        <div class="elite-form-group">
                            <input type="text" name="full_name" class="elite-form-control" placeholder="الاسم الكامل" value="{full_name}" required>
                        </div>
                        <div class="elite-form-group">
                            <input type="text" name="company_name" class="elite-form-control" placeholder="اسم الشركة (اختياري)" value="{company_name}">
                        </div>
                        <div class="elite-form-group">
                            <input type="text" name="phone" class="elite-form-control" placeholder="رقم الهاتف (اختياري)" value="{phone}">
                        </div>
                        <button type="submit" class="elite-btn" style="width: 100%;">
                            <i class="fas fa-user-plus"></i> انضم إلى النخبة
                        </button>
                    </form>
                </div>
            </div>
            """
            return render_template_string(ELITE_DESIGN_HTML, title="التسجيل - InvoiceFlow Elite", uptime="", content=content)
    
    content = """
    <div class="elite-login-container">
        <div class="elite-header">
            <h2 style="margin-bottom: 30px; text-align: center;">انضم إلى النخبة</h2>
            <form method="POST">
                <div class="elite-form-group">
                    <input type="text" name="username" class="elite-form-control" placeholder="اسم المستخدم" required>
                </div>
                <div class="elite-form-group">
                    <input type="password" name="password" class="elite-form-control" placeholder="كلمة المرور" required>
                </div>
                <div class="elite-form-group">
                    <input type="email" name="email" class="elite-form-control" placeholder="البريد الإلكتروني" required>
                </div>
                <div class="elite-form-group">
                    <input type="text" name="full_name" class="elite-form-control" placeholder="الاسم الكامل" required>
                </div>
                <div class="elite-form-group">
                    <input type="text" name="company_name" class="elite-form-control" placeholder="اسم الشركة (اختياري)">
                </div>
                <div class="elite-form-group">
                    <input type="text" name="phone" class="elite-form-control" placeholder="رقم الهاتف (اختياري)">
                </div>
                <button type="submit" class="elite-btn" style="width: 100%;">
                    <i class="fas fa-user-plus"></i> انضم إلى النخبة
                </button>
            </form>
            <div style="margin-top: 25px; text-align: center;">
                <a href="/elite/login" class="elite-btn elite-btn-secondary" style="width: 100%;">
                    <i class="fas fa-sign-in-alt"></i> لديك حساب؟ سجل الدخول
                </a>
            </div>
        </div>
    </div>
    """
    return render_template_string(ELITE_DESIGN_HTML, title="التسجيل - InvoiceFlow Elite", uptime="", content=content)

@app.route('/elite/logout')
def elite_logout():
    """تسجيل الخروج النخبوي"""
    session.clear()
    return redirect(url_for('elite_login'))

@app.route('/elite/profile')
def elite_profile():
    """الصفحة الشخصية النخبوية"""
    if 'user_logged_in' not in session:
        return redirect(url_for('elite_login'))
    
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    user_profile = elite_users.get_elite_profile(session['username'])
    stats = elite_db.get_elite_stats(session['username'])
    
    content = f"""
    <div class="elite-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-user-tie"></i> الملف الشخصي النخبوي
        </h2>
    </div>
    
    <div class="elite-stats-grid">
        <div class="elite-stat-card">
            <i class="fas fa-file-invoice" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number">{stats['total_invoices']}</div>
            <p>فواتيرك</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-dollar-sign" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number">${stats['total_revenue']:,.0f}</div>
            <p>إيراداتك</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-clock" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number">{stats['pending_invoices']}</div>
            <p>معلقة</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-crown" style="color: var(--primary-brown);"></i>
            <div class="elite-stat-number">{user_profile.get('subscription_tier', 'basic').title()}</div>
            <p>مستواك</p>
        </div>
    </div>
    
    <div class="elite-profile-section">
        <h3 style="margin-bottom: 25px; color: var(--dark-brown);">
            <i class="fas fa-id-card"></i> المعلومات الشخصية
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div>
                <p><strong>اسم المستخدم:</strong> {user_profile['username']}</p>
                <p><strong>البريد الإلكتروني:</strong> {user_profile['email']}</p>
                <p><strong>الاسم الكامل:</strong> {user_profile['full_name']}</p>
                <p><strong>الشركة:</strong> {user_profile.get('company_name', 'غير محدد')}</p>
            </div>
            <div>
                <p><strong>نوع الحساب:</strong> {user_profile['user_type']}</p>
                <p><strong>مستوى الاشتراك:</strong> {user_profile.get('subscription_tier', 'basic').title()}</p>
                <p><strong>آخر دخول:</strong> {user_profile['last_login'] or 'لم يسجل'}</p>
                <p><strong>تاريخ الانضمام:</strong> {user_profile['created_at'][:10] if user_profile['created_at'] else 'غير محدد'}</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(ELITE_DESIGN_HTML, title="الملف الشخصي - InvoiceFlow Elite", uptime=uptime_str, content=content)

# ================== إضافة الروابط المفقودة ==================
@app.route('/elite/invoices')
def elite_invoices():
    """صفحة الفواتير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('elite_login'))
    
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    content = """
    <div class="elite-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-file-invoice-dollar"></i> إدارة الفواتير
        </h2>
        <p style="text-align: center; color: var(--light-beige);">قريباً... سيتم إضافة نظام الفواتير المتكامل</p>
    </div>
    """
    return render_template_string(ELITE_DESIGN_HTML, title="الفواتير - InvoiceFlow Elite", uptime=uptime_str, content=content)

@app.route('/elite/create')
def elite_create_invoice():
    """صفحة إنشاء الفواتير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('elite_login'))
    
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    content = """
    <div class="elite-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-plus-circle"></i> إنشاء فاتورة جديدة
        </h2>
        <p style="text-align: center; color: var(--light-beige);">قريباً... سيتم إضافة نظام إنشاء الفواتير المتكامل</p>
    </div>
    """
    return render_template_string(ELITE_DESIGN_HTML, title="إنشاء فاتورة - InvoiceFlow Elite", uptime=uptime_str, content=content)

@app.route('/elite/admin')
def elite_admin():
    """لوحة التحكم الإدارية"""
    if 'user_logged_in' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('elite_home'))
    
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    content = """
    <div class="elite-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-crown"></i> لوحة التحكم الإدارية
        </h2>
        <p style="text-align: center; color: var(--light-beige);">قريباً... سيتم إضافة لوحة التحكم المتكاملة</p>
    </div>
    """
    return render_template_string(ELITE_DESIGN_HTML, title="لوحة التحكم - InvoiceFlow Elite", uptime=uptime_str, content=content)

@app.route('/elite/ai')
def elite_ai_insights():
    """صفحة الذكاء الاصطناعي"""
    if 'user_logged_in' not in session:
        return redirect(url_for('elite_login'))
    
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    content = """
    <div class="elite-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-robot"></i> الذكاء الاصطناعي والتحليلات
        </h2>
        <p style="text-align: center; color: var(--light-beige);">قريباً... سيتم إضافة نظام الذكاء الاصطناعي المتكامل</p>
    </div>
    """
    return render_template_string(ELITE_DESIGN_HTML, title="الذكاء الاصطناعي - InvoiceFlow Elite", uptime=uptime_str, content=content)

# ================== التشغيل الرئيسي للنخبة ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام النخبوي...")
        print(f"🌐 الخادم النخبوي يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام النخبوي جاهز لاستقبال الطلبات!")
        print("🎨 التصميم البيج/بني الفاخر مفعل!")
        print("🧠 الذكاء الاصطناعي النخبوي نشط!")
        print("🔐 نظام الأمان النخبوي مفعل!")
        print("📄 نظام PDF النخبوي جاهز!")
        print("👑 فريق النخبة البروفيسوري في الخدمة!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل النخبوي: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
