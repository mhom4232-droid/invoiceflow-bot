import os
import sqlite3
from flask import Flask, jsonify, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

app = Flask(__name__)

# الحصول على BOT_TOKEN من متغيرات البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN')

class InvoiceBot:
    def __init__(self):
        self.init_database()
        self.setup_bot()
    
    def init_database(self):
        self.conn = sqlite3.connect('invoices.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                amount REAL,
                date TEXT,
                description TEXT
            )
        ''')
        self.conn.commit()
    
    def setup_bot(self):
        if BOT_TOKEN:
            self.application = Application.builder().token(BOT_TOKEN).build()
            self.setup_handlers()
    
    def setup_handlers(self):
        # handler for /start command
        self.application.add_handler(CommandHandler("start", self.start_command))
        # handler for creating invoices
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🎉 مرحباً بك في InvoiceFlow Pro!\n\n"
            "أرسل لي بيانات الفاتورة بالتنسيق:\n"
            "العميل: الاسم\n"
            "المبلغ: 100\n"
            "الوصف: الخدمة المقدمة"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            text = update.message.text
            lines = text.split('\n')
            
            invoice_data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    invoice_data[key.strip()] = value.strip()
            
            if 'العميل' in invoice_data and 'المبلغ' in invoice_data:
                self.cursor.execute('''
                    INSERT INTO invoices (customer_name, amount, date, description)
                    VALUES (?, ?, datetime('now'), ?)
                ''', (invoice_data['العميل'], float(invoice_data['المبلغ']), 
                      invoice_data.get('الوصف', 'لا يوجد وصف')))
                self.conn.commit()
                
                await update.message.reply_text(
                    f"✅ تم إنشاء الفاتورة بنجاح!\n"
                    f"👤 العميل: {invoice_data['العميل']}\n"
                    f"💰 المبلغ: {invoice_data['المبلغ']}\n"
                    f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}"
                )
            else:
                await update.message.reply_text(
                    "❌ يرجى إرسال البيانات بالتنسيق الصحيح:\n"
                    "العميل: اسم العميل\n"
                    "المبلغ: 100\n"
                    "الوصف: وصف الخدمة"
                )
                
        except Exception as e:
            await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    
    def start_polling(self):
        if BOT_TOKEN:
            print("🤖 بدء تشغيل البوت...")
            self.application.run_polling()
        else:
            print("❌ BOT_TOKEN غير موجود!")

# إنشاء البوت
bot = InvoiceBot()

# Routes للويب
@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>InvoiceFlow Pro</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status { background: #4CAF50; color: white; padding: 10px; border-radius: 5px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 InvoiceFlow Pro يعمل بنجاح!</h1>
                <div class="status">
                    ✅ النظام يعمل 24/7 على السحابة
                </div>
                <p>🤖 البوت جاهز لاستقبال الرسائل على Telegram</p>
                <p>🔗 الرابط: https://t.me/your_bot_username</p>
                <p>📊 لإضافة فاتورة، أرسل للبوت:</p>
                <pre>
العميل: محمد أحمد
المبلغ: 150
الوصف: تصميم موقع ويب
                </pre>
            </div>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "InvoiceFlow Pro"})

@app.route('/invoices')
def get_invoices():
    bot.cursor.execute('SELECT * FROM invoices ORDER BY id DESC LIMIT 10')
    invoices = bot.cursor.fetchall()
    return jsonify({"invoices": invoices})

def run_bot():
    bot.start_polling()

if __name__ == '__main__':
    import threading
    
    # تشغيل البوت في thread منفصل
    if BOT_TOKEN:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("✅ بدء تشغيل البوت في الخلفية...")
    
    # تشغيل خادم الويب
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 بدء تشغيل خادم الويب على المنفذ {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
