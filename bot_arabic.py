import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import logging

# مكتبات PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import arabic_reshaper
from bidi.algorithm import get_display

# 🔥 الآمن: التوكن من environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

# إعداد التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# حالة المحادثة
CLIENT_NAME, SERVICE_NAME, SERVICE_PRICE, ADD_MORE = range(4)

def init_db():
    conn = sqlite3.connect('invoices.db', check_same_thread=False)
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

def arabic_text(text):
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except Exception as e:
        return str(text)

def create_simple_invoice_pdf(invoice_data):
    filename = f"invoice_{invoice_data['invoice_number']}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, alignment=1)
    elements.append(Paragraph(arabic_text("فاتورة احترافية"), title_style))
    elements.append(Spacer(1, 20))
    
    info_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=12)
    elements.append(Paragraph(arabic_text(f"رقم الفاتورة: {invoice_data['invoice_number']}"), info_style))
    elements.append(Paragraph(arabic_text(f"التاريخ: {invoice_data['date']}"), info_style))
    elements.append(Paragraph(arabic_text(f"اسم العميل: {invoice_data['client_name']}"), info_style))
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph(arabic_text("الخدمات المقدمة"), styles['Heading2']))
    elements.append(Spacer(1, 15))
    
    service_data = [['#', 'الخدمة', 'السعر']]
    for i, service in enumerate(invoice_data['services'], 1):
        service_name = arabic_text(service['name'])
        service_price = f"${service['price']:,.2f}"
        service_data.append([str(i), service_name, service_price])
    
    service_table = Table(service_data, colWidths=[0.5*inch, 3*inch, 1.5*inch])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(service_table)
    elements.append(Spacer(1, 20))
    
    total_style = ParagraphStyle('CustomTotal', parent=styles['Heading2'], fontSize=14, textColor=colors.darkred)
    total_text = arabic_text(f"المجموع الكلي: ${invoice_data['total']:,.2f}")
    elements.append(Paragraph(total_text, total_style))
    
    doc.build(elements)
    return filename

def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("إنشاء فاتورة جديدة", callback_data="create_invoice")],
        [InlineKeyboardButton("إحصائياتي", callback_data="my_stats")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """🚀 **مرحباً بك في InvoiceFlow Bot!**
أنشئ فواتير PDF احترافية في 30 ثانية!"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "create_invoice":
        await query.edit_message_text("📝 **أدخل اسم العميل:**")
        return CLIENT_NAME
    elif query.data == "my_stats":
        # دالة بسيطة للإحصائيات
        stats_text = "📊 **إحصائياتك:**\n• عدد الفواتير: 0\n• إجمالي المبيعات: $0"
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
            [InlineKeyboardButton("➕ إضافة خدمة أخرى", callback_data="add_more")],
            [InlineKeyboardButton("✅ إنهاء وإنشاء الفاتورة", callback_data="finish")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("✅ **تم إضافة الخدمة!**", reply_markup=reply_markup)
        return ADD_MORE
        
    except ValueError:
        await update.message.reply_text("❌ **يرجى إدخال سعر صحيح!**")
        return SERVICE_PRICE

async def handle_add_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_more":
        await query.edit_message_text("📋 **أدخل اسم الخدمة التالية:**")
        return SERVICE_NAME
    else:
        await query.edit_message_text("🔄 **جاري إنشاء الفاتورة...**")
        return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not found!")
        return
        
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()
    
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
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    print("✅ البوت جاهز للتشغيل!")
    application.run_polling()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ **تم الإلغاء.**")
    return ConversationHandler.END

if __name__ == '__main__':
    main()
