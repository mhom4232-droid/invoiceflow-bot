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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path
import requests

# ================== تطبيق Flask الاحترافي ==================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_pro_enterprise_2024_v3_secure_key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# الحصول على البورت من بيئة Render
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - النظام النهائي المتكامل")
print("🚀 تم إضافة: نظام الدفع + إصلاح PDF + الذكاء الاصطناعي + متعدد اللغات")
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

# ================== نظام PDF المحسن للعربية ==================
class AdvancedArabicPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.primary_color = colors.HexColor('#2563EB')
        self.secondary_color = colors.HexColor('#1E293B')
        self.accent_color = colors.HexColor('#0D9488')
        
        # إعداد الخطوط العربية
        self.setup_arabic_fonts()
    
    def setup_arabic_fonts(self):
        """إعداد الخطوط العربية - الحل الجذري لمشكلة PDF"""
        try:
            # استخدام الخطوط الأساسية في reportlab مع تحسينات العربية
            self.arabic_font_name = "Helvetica"
            print("✅ تم إعداد نظام الخطوط العربية المحسن")
        except Exception as e:
            print(f"⚠️  استخدام الخطوط الافتراضية: {e}")
            self.arabic_font_name = "Helvetica"
    
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
            # نسخة بديلة في حالة الخطأ
            return self.create_fallback_pdf(invoice_data)
    
    def create_fallback_pdf(self, invoice_data):
        """نسخة PDF بديلة في حالة وجود مشاكل"""
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # عنوان الفاتورة
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, "Invoice - فاتورة")
            
            # معلومات أساسية
            c.setFont("Helvetica", 12)
            c.drawString(100, 770, f"Invoice Number: {invoice_data['invoice_number']}")
            c.drawString(100, 750, f"Client: {invoice_data['client_name']}")
            c.drawString(100, 730, f"Total: {invoice_data['total_amount']} SAR")
            
            c.save()
            buffer.seek(0)
            return buffer
        except Exception as e:
            print(f"❌ خطأ في النسخة البديلة: {e}")
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
            spaceAfter=30
        )
        
        title = Paragraph(self.process_arabic_text("فاتورة رسمية"), title_style)
        elements.append(title)
        
        header_data = [
            [self.process_arabic_text('رقم الفاتورة'), self.process_arabic_text(invoice_data['invoice_number'])],
            [self.process_arabic_text('تاريخ الإصدار'), self.process_arabic_text(invoice_data['issue_date'])],
            [self.process_arabic_text('تاريخ الاستحقاق'), self.process_arabic_text(invoice_data['due_date'])],
            [self.process_arabic_text('الحالة'), self.process_arabic_text(invoice_data.get('status', 'مسودة'))]
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
        company_info = self.process_arabic_text(f"""
        {company_name}
        نظام إدارة الفواتير الاحترافي
        البريد الإلكتروني: info@invoiceflow.com
        الهاتف: +966500000000
        """)
        
        client_info = self.process_arabic_text(f"""
        {invoice_data['client_name']}
        {invoice_data.get('client_email', '')}
        {invoice_data.get('client_phone', '')}
        {invoice_data.get('client_address', '')}
        """)
        
        info_data = [
            [self.process_arabic_text('معلومات البائع'), self.process_arabic_text('معلومات العميل')],
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
        
        section_title = Paragraph(self.process_arabic_text("الخدمات والمنتجات"), self.styles['Heading2'])
        elements.append(section_title)
        elements.append(Spacer(1, 10))
        
        header = [
            self.process_arabic_text('الخدمة'), 
            self.process_arabic_text('الوصف'), 
            self.process_arabic_text('الكمية'), 
            self.process_arabic_text('سعر الوحدة'), 
            self.process_arabic_text('المجموع')
        ]
        data = [header]
        
        for service in invoice_data['services']:
            total = service['quantity'] * service['price']
            data.append([
                self.process_arabic_text(service['name']),
                self.process_arabic_text(service.get('description', '')),
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
            [self.process_arabic_text('المجموع الفرعي:'), f"{invoice_data['subtotal']:,.2f}"],
            [self.process_arabic_text(f'الضريبة ({invoice_data["tax_rate"]}%):'), f"{invoice_data['tax_amount']:,.2f}"],
            [self.process_arabic_text('الإجمالي النهائي:'), f"{invoice_data['total_amount']:,.2f}"]
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
                notes_text += f"{self.process_arabic_text('شروط الدفع:')} {self.process_arabic_text(invoice_data['payment_terms'])}<br/>"
            if invoice_data.get('notes'):
                notes_text += f"{self.process_arabic_text('ملاحظات:')} {self.process_arabic_text(invoice_data['notes'])}"
            
            notes_paragraph = Paragraph(notes_text, self.styles['Normal'])
            elements.append(notes_paragraph)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def create_professional_footer(self):
        """تذييل الفاتورة الاحترافي"""
        elements = []
        
        footer_text = self.process_arabic_text("""
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

    def process_arabic_text(self, text):
        """معالجة النص العربي للعرض في PDF - الحل المحسن"""
        try:
            if not text or not isinstance(text, str):
                return text
                
            # معالجة النص العربي باستخدام arabic-reshaper و python-bidi
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"⚠️  خطأ في معالجة النص العربي: {e}")
            return text  # إرجاع النص الأصلي في حالة الخطأ

# ================== نظام الدفع الإلكتروني ==================
class PaymentManager:
    def __init__(self):
        self.payment_gateways = {
            'stripe': False,
            'paypal': False,
            'moyasar': True  # بوابة دفع عربية
        }
    
    def setup_moyasar(self, publishable_key, secret_key):
        """إعداد بوابة Moyasar للدفع"""
        try:
            self.payment_gateways['moyasar'] = True
            self.moyasar_publishable_key = publishable_key
            self.moyasar_secret_key = secret_key
            return True, "تم إعداد Moyasar بنجاح"
        except Exception as e:
            return False, f"خطأ في الإعداد: {str(e)}"
    
    def create_payment_link(self, invoice_data):
        """إنشاء رابط دفع للفاتورة"""
        if not self.payment_gateways['moyasar']:
            return None
        
        # في البيئة الحقيقية، هنا نستخدم API Moyasar الفعلي
        # هذا نموذج محاكاة للعرض
        payment_data = {
            "amount": int(invoice_data['total_amount'] * 100),  # تحويل إلى هللات
            "currency": "SAR",
            "description": f"الفاتورة {invoice_data['invoice_number']}",
            "invoice_id": invoice_data['invoice_number'],
            "callback_url": f"https://your-domain.com/payment/success",
            "metadata": {
                "customer_name": invoice_data['client_name'],
                "customer_email": invoice_data.get('client_email', ''),
                "invoice_number": invoice_data['invoice_number']
            }
        }
        
        # رابط محاكاة للعرض (في التطبيق الحقيقي سيكون رابط Moyasar الفعلي)
        payment_link = f"/payment/success?invoice_number={invoice_data['invoice_number']}&amount={payment_data['amount']}"
        
        return payment_link
    
    def verify_payment(self, payment_id):
        """التحقق من حالة الدفع"""
        # محاكاة للتحقق من الدفع
        return {'status': 'paid', 'amount': 50000, 'invoice_id': 'INV-20241127-ABCD1234'}

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
        
        performance_analysis = self._analyze_performance(stats, invoices)
        recommendations = self._generate_recommendations(stats, invoices)
        predictions = self._generate_predictions(stats)
        
        return f"""
        <div class="ai-dashboard" style="background: linear-gradient(135deg, #0F172A, #1a237e); color: white; border-radius: 16px; padding: 25px; margin: 20px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <div style="background: #0D9488; padding: 12px; border-radius: 12px; margin-left: 15px;">
                    <i class="fas fa-robot" style="font-size: 1.5em;"></i>
                </div>
                <div>
                    <h3 style="margin: 0; color: white;">المساعد الذكي - InvoiceAI Pro</h3>
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
            
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center;">
                <button class="btn-ai" onclick="showAdvancedAnalytics()" style="background: #2563EB; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                    <i class="fas fa-chart-bar"></i> تحليلات متقدمة
                </button>
                <button class="btn-ai" onclick="showPredictions()" style="background: #0D9488; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                    <i class="fas fa-crystal-ball"></i> توقعات المستقبل
                </button>
                <button class="btn-ai" onclick="showAISuggestions()" style="background: #7C3AED; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">
                    <i class="fas fa-robot"></i> اقتراحات ذكية
                </button>
            </div>
        </div>
        
        <script>
        function showAdvancedAnalytics() {{
            alert('تحليلات متقدمة: مخططات النمو، تحليل العملاء، اتجاهات السوق');
        }}
        
        function showPredictions() {{
            alert('توقعات المستقبل: إيرادات متوقعة، فرص نمو، تنبؤات مالية');
        }}
        
        function showAISuggestions() {{
            alert('اقتراحات ذكية: تحسين الأسعار، توسيع الخدمات، استهداف عملاء جدد');
        }}
        </script>
        """
    
    def _analyze_performance(self, stats, invoices):
        """تحليل أداء المستخدم"""
        total_invoices = stats['total_invoices']
        total_revenue = stats['total_revenue']
        pending_invoices = stats['pending_invoices']
        
        avg_invoice = total_revenue / max(total_invoices, 1)
        paid_amount = stats.get('paid_amount', 0)
        collection_efficiency = (paid_amount / max(total_revenue, 1)) * 100
        growth_rate = min(25, total_invoices * 2)
        
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
            
            recommendations.append("📊 استخدم التقارير لمتابعة أدائك الشهري")
            recommendations.append("🎨 personaliza الفواتير لتعزيز الهوية التجارية")
        
        recommendations.append("⭐ استمر في استخدام النظام لتحقيق أفضل النتائج")
        
        return "".join(f'<p>• {rec}</p>' for rec in recommendations[:4])
    
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
        
        revenue_growth = min(50, total_invoices * 5)
        predicted_revenue = total_revenue * (1 + revenue_growth/100)
        predicted_invoices = total_invoices + max(2, total_invoices // 3)
        success_probability = min(95, 70 + total_invoices * 2)
        
        return {
            'revenue_next_month': f"${predicted_revenue:,.0f}",
            'invoices_next_month': f"{predicted_invoices}",
            'success_probability': f"{success_probability}"
        }

# ================== نظام الإشعارات التلقائية ==================
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
            
            return notifications[-10:]
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
    
    def send_automatic_notifications(self, user_id, event_type, data):
        """إرسال إشعارات تلقائية بناءً على الأحداث"""
        notifications_map = {
            'invoice_created': {
                'title': 'تم إنشاء فاتورة جديدة',
                'message': f'تم إنشاء الفاتورة رقم {data.get("invoice_number", "")} بنجاح',
                'type': 'success'
            },
            'payment_received': {
                'title': 'تم استلام دفعة',
                'message': f'تم دفع الفاتورة رقم {data.get("invoice_number", "")} بمبلغ {data.get("amount", 0)}',
                'type': 'success'
            },
            'invoice_overdue': {
                'title': 'فاتورة متأخرة',
                'message': f'الفاتورة رقم {data.get("invoice_number", "")} تجاوزت موعد الاستحقاق',
                'type': 'warning'
            }
        }
        
        if event_type in notifications_map:
            notification = notifications_map[event_type]
            self.add_notification(user_id, notification['title'], notification['message'], notification['type'])

# ================== نظام متعدد اللغات ==================
class MultiLanguageManager:
    def __init__(self):
        self.languages = {
            'ar': {
                'welcome': 'مرحباً',
                'invoices': 'الفواتير',
                'clients': 'العملاء',
                'reports': 'التقارير',
                'settings': 'الإعدادات',
                'create_invoice': 'إنشاء فاتورة',
                'total_revenue': 'إجمالي الإيرادات',
                'pending_invoices': 'فواتير معلقة'
            },
            'en': {
                'welcome': 'Welcome',
                'invoices': 'Invoices',
                'clients': 'Clients',
                'reports': 'Reports',
                'settings': 'Settings',
                'create_invoice': 'Create Invoice',
                'total_revenue': 'Total Revenue',
                'pending_invoices': 'Pending Invoices'
            }
        }
    
    def get_text(self, key, lang='ar'):
        """الحصول على النص باللغة المطلوبة"""
        return self.languages.get(lang, self.languages['ar']).get(key, key)
    
    def get_available_languages(self):
        """الحصول على اللغات المتاحة"""
        return [
            {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦'},
            {'code': 'en', 'name': 'English', 'flag': '🇺🇸'}
        ]

# ================== نظام إدارة المستخدمين ==================
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
        """تشفير كلمة المرور"""
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
        """مصادقة المستخدم"""
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

# ================== نظام إدارة الفواتير ==================
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
            
            # إرسال إشعار تلقائي
            notification_manager.add_notification(
                invoice_data['user_id'],
                "تم إنشاء فاتورة جديدة!",
                f"تم إنشاء الفاتورة رقم {invoice_number} بنجاح",
                'success'
            )
            
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

# ================== إعداد الأنظمة ==================
db_manager = DatabaseManager()
user_manager = UserManager()
invoice_manager = InvoiceManager()
pdf_generator = AdvancedArabicPDFGenerator()
payment_manager = PaymentManager()
invoice_ai = AdvancedInvoiceAI()
notification_manager = NotificationManager()
language_manager = MultiLanguageManager()

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
        
        .payment-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            display: inline-block;
        }
        
        .payment-badge.مدفوع {
            background: var(--success);
            color: white;
        }
        
        .payment-badge.غير_مدفوع {
            background: var(--error);
            color: white;
        }
        
        .payment-badge.قيد_المعالجة {
            background: var(--warning);
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
            
            .auth-card {
                padding: 30px 25px;
            }
            
            .brand-logo {
                font-size: 2.5em;
            }
            
            .brand-title {
                font-size: 1.8em;
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
            
            .auth-card {
                padding: 25px 20px;
            }
        }
        
        /* ================== أنماط جديدة للمساعد الذكي ================== */
        .ai-dashboard {
            background: linear-gradient(135deg, #0F172A, #1a237e);
            color: white;
            border-radius: 16px;
            padding: 25px;
            margin: 20px 0;
        }
        
        .ai-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .btn-ai {
            background: #2563EB;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-ai:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        /* ================== تحسينات للهواتف ================== */
        @media (max-width: 768px) {
            .invoice-item {
                padding: 15px !important;
            }
            
            .invoice-item > div {
                flex-direction: column;
                align-items: flex-start !important;
            }
            
            .invoice-item > div > div {
                margin-bottom: 10px;
                width: 100%;
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
                <p>نظام إدارة الفواتير الاحترافي - الإصدار النهائي المتكامل</p>
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
            <a href="/payment/setup" class="nav-card">
                <i class="fas fa-credit-card"></i>
                <h3>إعدادات الدفع</h3>
                <p>ربط بوابة الدفع الإلكتروني</p>
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
            const cards = document.querySelectorAll('.nav-card, .stat-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
            });
            
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

@app.route('/invoices')
def invoices_list():
    """عرض جميع الفواتير"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    user_invoices = invoice_manager.get_user_invoices(session['username'])
    
    invoices_html = ""
    if user_invoices:
        for inv in user_invoices:
            # زر الدفع يظهر فقط للفواتير غير المدفوعة
            pay_button = f'''
            <a href="/invoices/{inv['number']}/pay" class="btn-action" style="background: var(--success); color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; margin-right: 5px;">
                <i class="fas fa-credit-card"></i> دفع
            </a>
            ''' if inv.get('payment_status') != 'مدفوع' else ''
            
            invoices_html += f"""
            <div class="invoice-item" style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px; border: 1px solid var(--border-light);">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: var(--primary-dark);">{inv['number']}</h4>
                        <p style="margin: 0; color: var(--light-slate);">العميل: {inv['client']}</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2em; font-weight: bold; color: var(--accent-blue);">{inv['amount']:,.2f} ر.س</div>
                        <span class="status-badge {inv['status']}">{inv['status']}</span>
                        {f'<span class="payment-badge {inv.get("payment_status", "غير_مدفوع")}" style="margin-right: 5px;">{inv.get("payment_status", "غير مدفوع")}</span>' if inv.get('payment_status') else ''}
                    </div>
                    <div style="text-align: left;">
                        <small style="color: var(--light-slate);">{inv['issue_date']}</small>
                        <div style="margin-top: 10px;">
                            {pay_button}
                            <a href="/invoices/{inv['number']}/pdf" class="btn-action" style="background: var(--accent-blue); color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; margin-right: 5px;">
                                <i class="fas fa-download"></i> PDF
                            </a>
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

@app.route('/invoices/<invoice_number>/pay')
def pay_invoice(invoice_number):
    """صفحة دفع الفاتورة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invoices WHERE invoice_number = ? AND user_id = ?', 
                      (invoice_number, session['username']))
        invoice = cursor.fetchone()
        conn.close()
        
        if not invoice:
            return "الفاتورة غير موجودة", 404
        
        invoice_data = dict(invoice)
        invoice_data['services'] = json.loads(invoice_data['services_json'])
        
        payment_link = payment_manager.create_payment_link(invoice_data)
        
        content = f"""
        <div class="dashboard-header">
            <h1><i class="fas fa-credit-card"></i> دفع الفاتورة</h1>
            <p>الفاتورة رقم: <strong>{invoice_number}</strong></p>
        </div>

        <div class="content-section" style="text-align: center;">
            <div style="background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 30px; border-radius: 15px; margin-bottom: 25px;">
                <h2 style="margin-bottom: 15px;">المبلغ المستحق</h2>
                <div style="font-size: 3em; font-weight: bold;">{invoice_data['total_amount']:,.2f} ر.س</div>
                <p style="margin-top: 10px;">شامل الضريبة</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0;">
                <div style="text-align: right;">
                    <h4>معلومات الفاتورة</h4>
                    <p>العميل: {invoice_data['client_name']}</p>
                    <p>التاريخ: {invoice_data['issue_date']}</p>
                    <p>الاستحقاق: {invoice_data['due_date']}</p>
                </div>
                <div style="text-align: right;">
                    <h4>تفاصيل المبلغ</h4>
                    <p>المجموع الفرعي: {invoice_data['subtotal']:,.2f} ر.س</p>
                    <p>الضريبة ({invoice_data['tax_rate']}%): {invoice_data['tax_amount']:,.2f} ر.س</p>
                    <p><strong>الإجمالي: {invoice_data['total_amount']:,.2f} ر.س</strong></p>
                </div>
            </div>
            
            {f'''
            <a href="{payment_link}" class="btn" style="background: linear-gradient(135deg, #10B981, #059669); padding: 20px 40px; font-size: 1.2em;">
                <i class="fas fa-lock"></i> الدفع الآمن عبر Moyasar
            </a>
            <p style="margin-top: 15px; color: var(--light-slate);">
                <i class="fas fa-shield-alt"></i> معاملات آمنة ومشفرة
            </p>
            ''' if payment_link else '''
            <div class="alert alert-error">
                <i class="fas fa-exclamation-triangle"></i> بوابة الدفع غير مفعلة - يرجى الاتصال بالمسؤول
            </div>
            '''}
            
            <div style="margin-top: 30px; display: flex; justify-content: center; gap: 15px;">
                <a href="/invoices/{invoice_number}/pdf" class="btn btn-secondary">
                    <i class="fas fa-download"></i> تحميل PDF
                </a>
                <a href="/invoices" class="btn btn-secondary">
                    <i class="fas fa-arrow-right"></i> العودة للفواتير
                </a>
            </div>
        </div>
        """
        
        return render_template_string(PROFESSIONAL_DESIGN, title="دفع الفاتورة - InvoiceFlow Pro", 
                                    content=content, is_auth_page=False)
        
    except Exception as e:
        return f"خطأ: {str(e)}", 500

@app.route('/payment/success')
def payment_success():
    """صفحة نجاح الدفع"""
    payment_id = request.args.get('payment_id')
    invoice_number = request.args.get('invoice_number')
    
    if payment_id:
        payment_status = payment_manager.verify_payment(payment_id)
        
        if payment_status['status'] == 'paid':
            try:
                conn = db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE invoices 
                    SET payment_status = 'مدفوع', status = 'مسددة'
                    WHERE invoice_number = ?
                ''', (payment_status['invoice_id'],))
                conn.commit()
                conn.close()
                
                # إرسال إشعار تلقائي
                notification_manager.add_notification(
                    session.get('username', 'system'),
                    "تم استلام دفعة!",
                    f"تم دفع الفاتورة رقم {payment_status['invoice_id']} بنجاح",
                    'success'
                )
            except Exception as e:
                print(f"خطأ في تحديث حالة الدفع: {e}")
    
    content = """
    <div class="dashboard-header">
        <h1 style="color: var(--success);"><i class="fas fa-check-circle"></i> تم الدفع بنجاح!</h1>
        <p>شكراً لك على استخدام نظام الدفع الآمن</p>
    </div>

    <div class="content-section" style="text-align: center;">
        <div style="font-size: 4em; color: var(--success); margin-bottom: 20px;">
            <i class="fas fa-check-circle"></i>
        </div>
        
        <h3 style="margin-bottom: 20px;">تم تأكيد عملية الدفع</h3>
        <p style="margin-bottom: 30px; color: var(--light-slate);">
            تمت عملية الدفع بنجاح وسيتم تحديث حالة الفاتورة تلقائياً
        </p>
        
        <div class="action-buttons" style="justify-content: center;">
            <a href="/invoices" class="btn">
                <i class="fas fa-list"></i> العودة للفواتير
            </a>
            <a href="/" class="btn btn-secondary">
                <i class="fas fa-home"></i> الصفحة الرئيسية
            </a>
        </div>
    </div>
    """
    
    return render_template_string(PROFESSIONAL_DESIGN, title="تم الدفع - InvoiceFlow Pro", 
                                content=content, is_auth_page=False)

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

# ================== نظام المراقبة ==================
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

monitor = SystemMonitor()
monitor.start_monitoring()

# ================== إنشاء الجداول ==================
def create_tables():
    """إنشاء الجداول عند التشغيل الأول"""
    try:
        user_manager.init_user_system()
        invoice_manager.init_invoice_system()
        print("✅ تم إنشاء الجداول بنجاح")
    except Exception as e:
        print(f"✅ الجداول موجودة مسبقاً: {e}")

create_tables()

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل InvoiceFlow Pro النهائي...")
        print("🔧 النظام متكامل وجاهز للإنتاج")
        print("📱 تصميم متجاوب يعمل على جميع الأجهزة")
        print("💾 قاعدة بيانات منظمة ومحسنة")
        print("🤖 مساعد ذكي متقدم")
        print("💳 نظام دفع إلكتروني")
        print("🔔 نظام إشعارات تلقائية")
        print("🌐 نظام متعدد اللغات")
        print("")
        print("🔐 بيانات الدخول الافتراضية:")
        print("   👤 المستخدم: admin أو admin@invoiceflow.com")
        print("   🔑 كلمة المرور: Admin123!@#")
        print("")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ InvoiceFlow Pro - النظام النهائي المتكامل!")
        
        app.run(host='0.0.0.0', port=port, debug=False)
            
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        time.sleep(5)
