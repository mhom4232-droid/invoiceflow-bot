import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import logging

# مكتبات PDF الجديدة
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# حالة المحادثة
CLIENT_NAME, SERVICE_NAME, SERVICE_PRICE, ADD_MORE = range(4)

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            invoice_number TEXT,
            client_name TEXT,
            services TEXT,
            total REAL,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 🔥 **الإصلاح: دالة جديدة لمعالجة النص العربي بشكل صحيح**
def arabic_text(text):
    """
    دالة لمعالجة النص العربي للعرض في التليجرام وPDF
    """
    try:
        # إصلاح النص العربي للعرض الصحيح
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except Exception as e:
        logger.error(f"Error in arabic_text: {e}")
        return str(text)

def simple_text(text):
    """
    دالة مبسطة للنصوص الأساسية بدون تعقيد
    """
    return str(text)

# 🔥 **الإصلاح: دالة PDF جديدة ومبسطة**
def create_simple_invoice_pdf(invoice_data):
    filename = f"invoice_{invoice_data['invoice_number']}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    
    # العناصر التي ستظهر في PDF
    elements = []
    
    # إعداد الأنماط
    styles = getSampleStyleSheet()
    
    # عنوان الفاتورة
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # مركز
    )
    
    title_text = arabic_text("فاتورة احترافية")
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 20))
    
    # معلومات الفاتورة
    info_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12
    )
    
    # رقم الفاتورة
    invoice_no = arabic_text(f"رقم الفاتورة: {invoice_data['invoice_number']}")
    elements.append(Paragraph(invoice_no, info_style))
    
    # التاريخ
    date_text = arabic_text(f"التاريخ: {invoice_data['date']}")
    elements.append(Paragraph(date_text, info_style))
    
    # اسم العميل
    client_text = arabic_text(f"اسم العميل: {invoice_data['client_name']}")
    elements.append(Paragraph(client_text, info_style))
    
    elements.append(Spacer(1, 30))
    
    # عنوان الخدمات
    services_title = arabic_text("الخدمات المقدمة")
    elements.append(Paragraph(services_title, styles['Heading2']))
    elements.append(Spacer(1, 15))
    
    # جدول الخدمات
    service_data = [['#', 'الخدمة', 'السعر']]
    
    for i, service in enumerate(invoice_data['services'], 1):
        service_name = arabic_text(service['name'])
        service_price = f"${service['price']:,.2f}"
        service_data.append([str(i), service_name, service_price])
    
    # إنشاء الجدول
    service_table = Table(service_data, colWidths=[0.5*inch, 3*inch, 1.5*inch])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(service_table)
    elements.append(Spacer(1, 20))
    
    # المجموع الكلي
    total_style = ParagraphStyle(
        'CustomTotal',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        textColor=colors.darkred
    )
    
    total_text = arabic_text(f"المجموع الكلي: ${invoice_data['total']:,.2f}")
    elements.append(Paragraph(total_text, total_style))
    elements.append(Spacer(1, 30))
    
    # تذييل الفاتورة
    footer_style = ParagraphStyle(
        'CustomFooter',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=1  # مركز
    )
    
    footer1 = arabic_text("شكراً لتعاملكم معنا")
    footer2 = arabic_text("InvoiceFlow - للاستفسارات: support@invoiceflow.com")
    
    elements.append(Paragraph(footer1, footer_style))
    elements.append(Paragraph(footer2, footer_style))
    
    # بناء PDF
    doc.build(elements)
    return filename

# توليد رقم فاتورة فريد
def generate_invoice_number():
    now = datetime.now()
    return f"INV-{now.strftime('%Y%m%d%H%M%S')}"

# 🔥 **الإصلاح: أوامر البوت مع نصوص مبسطة**
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [InlineKeyboardButton("إنشاء فاتورة جديدة", callback_data="create_invoice")],
        [InlineKeyboardButton("إحصائياتي", callback_data="my_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # استخدام نصوص إنجليزية مع بعض العربية البسيطة
    welcome_text = """🚀 **مرحباً بك في InvoiceFlow Bot!**

أنشئ فواتير PDF احترافية في 30 ثانية!

**الخيارات:**
- إنشاء فاتورة جديدة
- عرض الإحصائيات"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_invoice":
        # استخدام نص إنجليزي مع كلمات عربية بسيطة
        await query.edit_message_text("📝 **أدخل اسم العميل:**")
        return CLIENT_NAME
    elif query.data == "my_stats":
        user_id = query.from_user.id
        stats = get_user_stats(user_id)
        stats_text = f"""
📊 **إحصائياتك:**

• عدد الفواتير: {stats['total_invoices']}
• إجمالي المبيعات: ${stats['total_sales']:,.2f}
• آخر فاتورة: {stats['last_invoice']}
        """
        await query.edit_message_text(stats_text)

async def get_client_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['client_name'] = update.message.text
    await update.message.reply_text("📋 **أدخل اسم الخدمة الأولى:**")
    return SERVICE_NAME

async def get_service_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_service'] = {'name': update.message.text}
    await update.message.reply_text("💰 **أدخل سعر الخدمة:**")
    return SERVICE_PRICE

async def get_service_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
        context.user_data['current_service']['price'] = price
        
        if 'services' not in context.user_data:
            context.user_data['services'] = []
        
        context.user_data['services'].append(context.user_data['current_service'])
        
        keyboard = [
            [
                InlineKeyboardButton("➕ إضافة خدمة أخرى", callback_data="add_more"),
                InlineKeyboardButton("✅ إنهاء وإنشاء الفاتورة", callback_data="finish")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ **تم إضافة الخدمة!**\nاختر الخطوة التالية:",
            reply_markup=reply_markup
        )
        return ADD_MORE
        
    except ValueError:
        await update.message.reply_text("❌ **يرجى إدخال سعر صحيح!**\nأدخل سعر الخدمة:")
        return SERVICE_PRICE

async def handle_add_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_more":
        await query.edit_message_text("📋 **أدخل اسم الخدمة التالية:**")
        return SERVICE_NAME
    else:  # finish
        await create_final_invoice(update, context)
        return ConversationHandler.END

async def create_final_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data
    
    # حساب المجموع
    total = sum(service['price'] for service in user_data['services'])
    
    # إنشاء بيانات الفاتورة
    invoice_data = {
        'invoice_number': generate_invoice_number(),
        'client_name': user_data['client_name'],
        'services': user_data['services'],
        'total': total,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    # حفظ في قاعدة البيانات
    save_invoice(update.effective_user.id, invoice_data)
    
    # إنشاء PDF
    await query.edit_message_text("🔄 **جاري إنشاء الفاتورة...**")
    
    try:
        pdf_file = create_simple_invoice_pdf(invoice_data)
        
        # إرسال الفاتورة
        with open(pdf_file, 'rb') as file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=file,
                caption=f"""✅ **تم إنشاء الفاتورة بنجاح!**

• العميل: {user_data['client_name']}
• رقم الفاتورة: {invoice_data['invoice_number']}
• المجموع: ${total:,.2f}

شكراً لاستخدامك InvoiceFlow! 🚀"""
            )
        
        # تنظيف البيانات المؤقتة
        context.user_data.clear()
        
        # عرض زر جديد
        keyboard = [[InlineKeyboardButton("🔄 إنشاء فاتورة جديدة", callback_data="create_invoice")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="هل تريد إنشاء فاتورة جديدة؟",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        await query.edit_message_text("❌ **حدث خطأ في إنشاء الفاتورة!**\nيرجى المحاولة مرة أخرى.")

def save_invoice(user_id, invoice_data):
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO invoices (user_id, invoice_number, client_name, services, total, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        invoice_data['invoice_number'],
        invoice_data['client_name'],
        str(invoice_data['services']),
        invoice_data['total'],
        invoice_data['date']
    ))
    
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('invoices.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*), SUM(total) FROM invoices WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    
    c.execute('SELECT invoice_number FROM invoices WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    last_invoice = c.fetchone()
    
    conn.close()
    
    return {
        'total_invoices': result[0] or 0,
        'total_sales': result[1] or 0,
        'last_invoice': last_invoice[0] if last_invoice else "لا توجد فواتير"
    }

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ **تم إلغاء العملية.**")
    return ConversationHandler.END

def main():
    # استخدام التوكن
    BOT_TOKEN = '8346505913:AAEQ-8l9k9p7qtNUZepeT2PXwdjZajolNn0'
    
    # تهيئة قاعدة البيانات
    init_db()
    
    # إنشاء التطبيق
    application = Application.builder().token(BOT_TOKEN).build()
    
    # محادثة إنشاء الفاتورة
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_button_click, pattern='^(create_invoice|my_stats)$')],
        states={
            CLIENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_client_name)],
            SERVICE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service_name)],
            SERVICE_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service_price)],
            ADD_MORE: [CallbackQueryHandler(handle_add_more, pattern='^(add_more|finish)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    # بدء البوت
    print("✅ البوت يعمل...")
    application.run_polling()

if __name__ == '__main__':
    main()
