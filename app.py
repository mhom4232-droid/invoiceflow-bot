# ================== InvoiceFlow Pro - النظام المجاني المستمر ==================
# 🎯 الإصدار ULTIMATE FREE - Cloud Edition
# 👨💻 فريق البروفيسورات المتخصصين
# 🔧 نظام مجاني يعمل على السحابة والسيرفرات

import os
import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta
from threading import Thread, Lock
import sys
from flask import Flask, jsonify, request

# ================== تطبيق Flask للويب ==================
app = Flask(__name__)

# الحصول على البورت من البيئة (مطلوب للسحابة)
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - النظام المجاني المستمر")
print("🚀 الإصدار ULTIMATE FREE - Cloud Edition")
print("👨💻 فريق البروفيسورات المتخصصين")
print("🔧 نظام مجاني يعمل 24/7 على السحابة")
print("=" * 80)

# ================== نظام الإبقاء على التشغيل المتقدم ==================
class AdvancedKeepAlive:
    """نظام متقدم للإبقاء على التشغيل مجاناً"""
    
    def __init__(self):
        self.uptime_start = time.time()
        self.ping_count = 0
        
    def start_keep_alive(self):
        """بدء جميع أنظمة الإبقاء على التشغيل"""
        print("🔄 بدء أنظمة الاستمرارية المجانية...")
        
        # 1. نظام البينغ التلقائي
        self.start_auto_ping()
        
        # 2. نظام المراقبة الذاتية
        self.start_self_monitoring()
        
        print("✅ جميع أنظمة الاستمرارية مفعلة!")
    
    def start_auto_ping(self):
        """بدء نظام البينغ التلقائي"""
        def auto_ping():
            while True:
                try:
                    # محاولة الوصول للخادم نفسه
                    response = requests.get(f'http://localhost:{port}', timeout=10)
                    self.ping_count += 1
                    print(f"📡 بينغ ناجح #{self.ping_count}")
                except:
                    print("🔴 فشل البينغ - الخادم قد يكون متوقفاً")
                
                time.sleep(300)  # كل 5 دقائق
        
        ping_thread = Thread(target=auto_ping)
        ping_thread.daemon = True
        ping_thread.start()
    
    def start_self_monitoring(self):
        """بدء المراقبة الذاتية"""
        def monitor():
            last_activity = time.time()
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                # عرض تقرير كل 10 دقائق
                if int(current_time) % 600 == 0:
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"📊 تقرير النظام: {hours}س {minutes}د - {self.ping_count} زيارات")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# ================== واجهات ويب بدلاً من Console ==================
@app.route('/')
def home():
    """الصفحة الرئيسية"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    return f'''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>InvoiceFlow Pro - النظام النشط</title>
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                max-width: 800px;
                margin: 0 auto;
            }}
            .status {{
                font-size: 28px;
                margin: 20px 0;
                color: #00ff88;
            }}
            .info {{
                margin: 15px 0;
                font-size: 18px;
            }}
            .uptime {{
                background: rgba(0,255,136,0.2);
                padding: 10px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .menu {{
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 30px 0;
                flex-wrap: wrap;
            }}
            .menu-btn {{
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                text-decoration: none;
                font-size: 16px;
                transition: all 0.3s;
            }}
            .menu-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 InvoiceFlow Pro</h1>
            <div class="status">✅ النظام يعمل بنجاح!</div>
            
            <div class="uptime">
                ⏰ مدة التشغيل: {hours} ساعة {minutes} دقيقة
            </div>
            
            <div class="info">🤖 النظام نشط وجاهز لاستقبال الطلبات</div>
            <div class="info">📊 عدد الزيارات: {keep_alive_system.ping_count}</div>
            <div class="info">🔧 الإصدار: ULTIMATE FREE - Cloud Edition</div>
            <div class="info">👨💻 فريق البروفيسورات المتخصصين</div>
            <div class="info">🕒 آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
            
            <div class="menu">
                <a href="/invoices" class="menu-btn">📋 عرض الفواتير</a>
                <a href="/stats" class="menu-btn">📊 الإحصائيات</a>
                <a href="/health" class="menu-btn">❤️ حالة النظام</a>
                <a href="/create" class="menu-btn">🧾 إنشاء فاتورة</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """فحص صحة النظام"""
    return jsonify({
        "status": "healthy",
        "service": "InvoiceFlow Pro",
        "uptime": time.time() - keep_alive_system.uptime_start,
        "version": "ULTIMATE FREE - Cloud Edition",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/invoices')
def get_invoices():
    """الحصول على الفواتير"""
    try:
        conn = sqlite3.connect('invoices_pro.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invoices ORDER BY created_at DESC LIMIT 10')
        invoices = cursor.fetchall()
        conn.close()
        
        invoices_list = []
        for invoice in invoices:
            invoices_list.append({
                'id': invoice[0],
                'invoice_id': invoice[1],
                'client_name': invoice[5],
                'total_amount': invoice[9],
                'issue_date': invoice[10]
            })
        
        return jsonify({"invoices": invoices_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def get_stats():
    """الإحصائيات"""
    try:
        conn = sqlite3.connect('invoices_pro.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM invoices')
        total_invoices, total_revenue = cursor.fetchone()
        
        cursor.execute('SELECT invoice_id, client_name, total_amount FROM invoices ORDER BY created_at DESC LIMIT 5')
        recent_invoices = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "total_invoices": total_invoices,
            "total_revenue": total_revenue,
            "recent_invoices": recent_invoices
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة"""
    if request.method == 'GET':
        return '''
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>إنشاء فاتورة جديدة</title>
            <style>
                body { font-family: Arial; padding: 20px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🧾 إنشاء فاتورة جديدة</h2>
                <form method="POST">
                    <input type="text" name="client_name" placeholder="اسم العميل" required>
                    <input type="email" name="client_email" placeholder="البريد الإلكتروني (اختياري)">
                    <input type="text" name="client_phone" placeholder="رقم الهاتف (اختياري)">
                    <textarea name="services" placeholder="الخدمات (اسم الخدمة : السعر)" rows="5" required></textarea>
                    <button type="submit">إنشاء الفاتورة</button>
                </form>
                <p>💡 مثال للخدمات:<br>تصميم موقع : 1500<br>استضافة : 500<br>صيانة : 300</p>
            </div>
        </body>
        </html>
        '''
    
    else:  # POST
        try:
            client_name = request.form['client_name']
            client_email = request.form.get('client_email', '')
            client_phone = request.form.get('client_phone', '')
            services_text = request.form['services']
            
            # معالجة الخدمات
            services = []
            for line in services_text.split('\n'):
                if ':' in line:
                    name, price = line.split(':', 1)
                    services.append({
                        'name': name.strip(),
                        'price': float(price.strip()),
                        'quantity': 1
                    })
            
            if not services:
                return jsonify({"error": "لم تدخل أي خدمات"}), 400
            
            total_amount = sum(s['price'] for s in services)
            
            # حفظ الفاتورة
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
            
            # استخدام نظام قاعدة البيانات الموجود
            db_manager = DatabaseManager()
            success = db_manager.save_invoice(invoice_data)
            
            if success:
                return jsonify({
                    "success": True,
                    "invoice_id": invoice_data['invoice_id'],
                    "client_name": client_name,
                    "total_amount": total_amount,
                    "message": "تم إنشاء الفاتورة بنجاح"
                })
            else:
                return jsonify({"error": "فشل في حفظ الفاتورة"}), 500
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# ================== الأنظمة الأساسية (بدون تغيير) ==================
class AdvancedTranslationSystem:
    """نظام ترجمة متطور متعدد اللغات"""
    def __init__(self):
        self.translations = {
            'ar': {
                'welcome': "🌟 **مرحباً بك في InvoiceFlow Pro!** 🌟",
                # ... باقي النصوص كما هي
            }
        }

class DatabaseManager:
    """مدير قاعدة بيانات متطور"""
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
                 client_email, client_phone, services_json, total_amount, issue_date, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_data['invoice_id'],
                invoice_data.get('user_id', 'web_user'),
                invoice_data.get('user_name', 'مستخدم الويب'),
                invoice_data.get('company_name', 'شركتي'),
                invoice_data['client_name'],
                invoice_data.get('client_email', ''),
                invoice_data.get('client_phone', ''),
                json.dumps(invoice_data['services'], ensure_ascii=False),
                invoice_data['total_amount'],
                invoice_data.get('issue_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                invoice_data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
            ))
            conn.commit()
            conn.close()
            print(f"✅ تم حفظ الفاتورة: {invoice_data['invoice_id']}")
            return True
        except Exception as e:
            print(f"🔧 خطأ في حفظ الفاتورة: {e}")
            return False

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        # بدء نظام الاستمرارية
        keep_alive_system = AdvancedKeepAlive()
        keep_alive_system.start_keep_alive()
        
        # بدء قاعدة البيانات
        db_manager = DatabaseManager()
        
        print("🌟 بدء تشغيل النظام على السحابة...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة...")
        time.sleep(5)
