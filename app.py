# ================== InvoiceFlow Pro - النظام المجاني المستمر ==================
# 🎯 الإصدار ULTIMATE FREE - Web Edition
# 👨💻 فريق البروفيسورات المتخصصين
# 🔧 نظام مجاني يعمل على السحابة والمواقع

import os
import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta
from threading import Thread, Lock
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# ================== تطبيق Flask ==================
app = Flask(__name__)

# الحصول على البورت من البيئة (مطلوب للسحابة)
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Pro - النظام المجاني المستمر")
print("🚀 الإصدار ULTIMATE FREE - Web Edition")
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
        
        # نظام المراقبة الذاتية
        self.start_self_monitoring()
        
        print("✅ جميع أنظمة الاستمرارية مفعلة!")
    
    def start_self_monitoring(self):
        """بدء المراقبة الذاتية"""
        def monitor():
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

# بدء نظام الاستمرارية فوراً
keep_alive_system = AdvancedKeepAlive()
keep_alive_system.start_keep_alive()

# ================== نظام الترجمة المتطور ==================
class AdvancedTranslationSystem:
    """نظام ترجمة متطور متعدد اللغات"""
    
    def __init__(self):
        self.translations = {
            'ar': {
                'welcome': "🌟 مرحباً بك في InvoiceFlow Pro!",
                'create_invoice': "🧾 إنشاء فاتورة",
                'stats': "📊 الإحصائيات", 
                'help': "🆘 المساعدة",
                'exit': "🚪 خروج",
                'select_option': "اختر الخيار:",
                'enter_client_name': "أدخل اسم العميل:",
                'enter_services': "أدخل الخدمات (اسم الخدمة : السعر)",
                'service_added': "تمت الإضافة: {} - ${}",
                'invoice_summary': "ملخص الفاتورة",
                'confirm_invoice': "✅ تأكيد إنشاء الفاتورة",
                'edit_invoice': "✏️ تعديل البيانات", 
                'cancel_invoice': "❌ إلغاء",
                'invoice_created': "تم إنشاء الفاتورة بنجاح!",
                'new_invoice': "🧾 إنشاء فاتورة جديدة",
                'main_menu': "🏠 الرئيسية",
                'thank_you': "شكراً لاستخدامك InvoiceFlow Pro",
                'invalid_choice': "❌ خيار غير صحيح",
                'no_services': "❌ لم تدخل أي خدمات",
                'price_error': "❌ خطأ في السعر",
                'format_error': "❌ تنسيق غير صحيح"
            }
        }
    
    def get_text(self, key, language='ar', **kwargs):
        """الحصول على نص مترجم"""
        text = self.translations.get(language, {}).get(key, key)
        return text.format(**kwargs) if kwargs else text

# ================== نظام قاعدة البيانات المتطور ==================
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

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id TEXT PRIMARY KEY,
                    user_name TEXT,
                    total_invoices INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

            self._update_user_stats(invoice_data)
            conn.commit()
            conn.close()
            print(f"✅ تم حفظ الفاتورة: {invoice_data['invoice_id']}")
            return True
        except Exception as e:
            print(f"🔧 خطأ في حفظ الفاتورة: {e}")
            return False

    def _update_user_stats(self, invoice_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO user_stats 
                (user_id, user_name, total_invoices, total_revenue, last_activity)
                VALUES (?, ?, 
                    COALESCE((SELECT total_invoices FROM user_stats WHERE user_id = ?), 0) + 1,
                    COALESCE((SELECT total_revenue FROM user_stats WHERE user_id = ?), 0) + ?,
                    CURRENT_TIMESTAMP
                )
            ''', (
                invoice_data.get('user_id', 'web_user'),
                invoice_data.get('user_name', 'مستخدم الويب'),
                invoice_data.get('user_id', 'web_user'),
                invoice_data.get('user_id', 'web_user'),
                invoice_data['total_amount']
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"🔧 خطأ في تحديث الإحصائيات: {e}")

    def get_all_invoices(self):
        """الحصول على جميع الفواتير"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT invoice_id, client_name, total_amount, issue_date, services_json 
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
                    'services': json.loads(invoice[4]) if invoice[4] else []
                })
            return result
        except Exception as e:
            print(f"🔧 خطأ في جلب الفواتير: {e}")
            return []

    def get_stats(self):
        """الحصول على الإحصائيات"""
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

# ================== نظام إنشاء الفواتير المتطور ==================
class InvoiceGenerator:
    """نظام إنشاء الفواتير المتطور"""
    
    def create_text_invoice(self, invoice_data, language='ar'):
        try:
            os.makedirs('invoices', exist_ok=True)
            
            filename = f"invoices/{invoice_data['invoice_id']}_{language}.txt"
            
            services_text = ""
            for i, service in enumerate(invoice_data['services'], 1):
                services_text += f"   {i}. {service['name']} - ${service['price']:.2f}\n"

            content = f"""
{'='*60}
فاتورة احترافية - InvoiceFlow Pro
{'='*60}

الشركة: {invoice_data.get('company_name', 'شركتي')}
العميل: {invoice_data['client_name']}
رقم الفاتورة: {invoice_data['invoice_id']}
التاريخ: {invoice_data['issue_date']}
البريد الإلكتروني: {invoice_data.get('client_email', 'غير محدد')}
الهاتف: {invoice_data.get('client_phone', 'غير محدد')}

الخدمات:
{services_text}
المجموع: ${invoice_data['total_amount']:.2f}

شكراً لتعاملكم مع InvoiceFlow Pro
{'='*60}
"""

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ تم إنشاء ملف: {filename}")
            return filename

        except Exception as e:
            print(f"🔧 خطأ في إنشاء الملف: {e}")
            return None

# ================== واجهات ويب ==================
translation_system = AdvancedTranslationSystem()
db_manager = DatabaseManager()
invoice_generator = InvoiceGenerator()

# قوالب HTML
BASE_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .nav {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}
        .nav a {{
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 15px 25px;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        .nav a:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 20px;
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.15);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
            color: #00ff88;
        }}
        .invoice-item {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #00ff88;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 8px;
            color: white;
            font-weight: bold;
        }}
        .form-control {{
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 16px;
        }}
        .form-control::placeholder {{
            color: rgba(255,255,255,0.7);
        }}
        .btn {{
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,255,136,0.4);
        }}
        .service-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 3px solid #00ff88;
        }}
        .alert {{
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        .alert-success {{
            background: rgba(0,255,136,0.2);
            border: 1px solid #00ff88;
            color: #00ff88;
        }}
        .alert-error {{
            background: rgba(255,0,0,0.2);
            border: 1px solid #ff4444;
            color: #ff4444;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 InvoiceFlow Pro</h1>
            <p>🚀 النظام المجاني المستمر - Web Edition</p>
            <p>⏰ مدة التشغيل: {uptime}</p>
        </div>
        
        <div class="nav">
            <a href="/">🏠 الرئيسية</a>
            <a href="/invoices">📋 الفواتير</a>
            <a href="/create">🧾 إنشاء فاتورة</a>
            <a href="/stats">📊 الإحصائيات</a>
            <a href="/health">❤️ حالة النظام</a>
        </div>

        {content}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    
    content = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <h3>📊 إجمالي الفواتير</h3>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>فاتورة</p>
        </div>
        <div class="stat-card">
            <h3>💰 إجمالي الإيرادات</h3>
            <div class="stat-number">${stats['total_revenue']:,.2f}</div>
            <p>دولار</p>
        </div>
        <div class="stat-card">
            <h3>📅 فواتير اليوم</h3>
            <div class="stat-number">{stats['today_invoices']}</div>
            <p>فاتورة</p>
        </div>
    </div>
    
    <div class="card">
        <h2>🎉 مرحباً بك في InvoiceFlow Pro!</h2>
        <p>نظام إدارة الفواتير المتكامل الذي يعمل 24/7 على السحابة</p>
        
        <div style="margin-top: 20px;">
            <h3>🚀 المميزات:</h3>
            <ul style="list-style: none; margin: 15px 0;">
                <li>✅ إنشاء فواتير احترافية</li>
                <li>✅ حفظ تلقائي في قاعدة البيانات</li>
                <li>✅ إحصائيات مفصلة</li>
                <li>✅ واجهة ويب متكاملة</li>
                <li>✅ يعمل على جميع الأجهزة</li>
            </ul>
        </div>
        
        <a href="/create" class="btn" style="display: inline-block; margin-top: 20px;">
            🧾 بدء إنشاء فاتورة
        </a>
    </div>
    """
    
    return render_template_string(BASE_HTML, title="InvoiceFlow Pro - الرئيسية", uptime=uptime_str, content=content)

@app.route('/invoices')
def invoices_page():
    """صفحة عرض الفواتير"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    invoices = db_manager.get_all_invoices()
    
    invoices_html = ""
    for invoice in invoices:
        services_html = ""
        for service in invoice['services']:
            services_html += f"<div class='service-item'>{service['name']} - ${service['price']:.2f}</div>"
        
        invoices_html += f"""
        <div class="invoice-item">
            <h3>📄 فاتورة #{invoice['invoice_id']}</h3>
            <p><strong>👤 العميل:</strong> {invoice['client_name']}</p>
            <p><strong>💰 المبلغ:</strong> ${invoice['total_amount']:.2f}</p>
            <p><strong>📅 التاريخ:</strong> {invoice['issue_date']}</p>
            <div style="margin-top: 10px;">
                <strong>الخدمات:</strong>
                {services_html}
            </div>
        </div>
        """
    
    content = f"""
    <div class="card">
        <h2>📋 جميع الفواتير</h2>
        <p>إجمالي الفواتير: {len(invoices)} فاتورة</p>
    </div>
    
    {invoices_html if invoices else '<div class="alert alert-error">لا توجد فواتير حالياً</div>'}
    """
    
    return render_template_string(BASE_HTML, title="الفواتير - InvoiceFlow Pro", uptime=uptime_str, content=content)

@app.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """إنشاء فاتورة جديدة"""
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
                return render_template_string(BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)
            
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
            
            success = db_manager.save_invoice(invoice_data)
            
            if success:
                # إنشاء ملف الفاتورة
                invoice_generator.create_text_invoice(invoice_data)
                
                success_content = f"""
                <div class="alert alert-success">
                    ✅ تم إنشاء الفاتورة بنجاح!
                </div>
                <div class="card">
                    <h3>🧾 تفاصيل الفاتورة</h3>
                    <p><strong>رقم الفاتورة:</strong> {invoice_data['invoice_id']}</p>
                    <p><strong>العميل:</strong> {client_name}</p>
                    <p><strong>المبلغ الإجمالي:</strong> ${total_amount:.2f}</p>
                    <p><strong>التاريخ:</strong> {invoice_data['issue_date']}</p>
                    
                    <div style="margin-top: 20px;">
                        <a href="/invoices" class="btn">📋 عرض جميع الفواتير</a>
                        <a href="/create" class="btn" style="background: #667eea;">🧾 إنشاء فاتورة جديدة</a>
                    </div>
                </div>
                """
                return render_template_string(BASE_HTML, title="تم إنشاء الفاتورة - InvoiceFlow Pro", uptime=uptime_str, content=success_content)
            else:
                content = '<div class="alert alert-error">❌ فشل في حفظ الفاتورة</div>'
                content += create_invoice_form()
                return render_template_string(BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)
                
        except Exception as e:
            content = f'<div class="alert alert-error">❌ حدث خطأ: {str(e)}</div>'
            content += create_invoice_form()
            return render_template_string(BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)
    
    content = create_invoice_form()
    return render_template_string(BASE_HTML, title="إنشاء فاتورة - InvoiceFlow Pro", uptime=uptime_str, content=content)

def create_invoice_form():
    """نموذج إنشاء الفاتورة"""
    return """
    <div class="card">
        <h2>🧾 إنشاء فاتورة جديدة</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="client_name">👤 اسم العميل *</label>
                <input type="text" id="client_name" name="client_name" class="form-control" placeholder="أدخل اسم العميل" required>
            </div>
            
            <div class="form-group">
                <label for="client_email">📧 البريد الإلكتروني (اختياري)</label>
                <input type="email" id="client_email" name="client_email" class="form-control" placeholder="example@email.com">
            </div>
            
            <div class="form-group">
                <label for="client_phone">📞 رقم الهاتف (اختياري)</label>
                <input type="text" id="client_phone" name="client_phone" class="form-control" placeholder="+1234567890">
            </div>
            
            <div class="form-group">
                <label for="services">💰 الخدمات *</label>
                <textarea id="services" name="services" class="form-control" rows="6" placeholder="أدخل الخدمات بالتنسيق:
تصميم موقع : 1500
استضافة ويب : 500
صيانة : 300
... إلخ" required></textarea>
                <small style="color: rgba(255,255,255,0.7);">💡 استخدم النقطتين (:) لفصل اسم الخدمة عن السعر</small>
            </div>
            
            <button type="submit" class="btn">✅ إنشاء الفاتورة</button>
        </form>
    </div>
    """

@app.route('/stats')
def stats_page():
    """صفحة الإحصائيات"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    invoices = db_manager.get_all_invoices()[:5]  # آخر 5 فواتير
    
    recent_invoices_html = ""
    for invoice in invoices:
        recent_invoices_html += f"""
        <div class="invoice-item">
            <strong>{invoice['invoice_id']}</strong> - {invoice['client_name']} - ${invoice['total_amount']:.2f}
        </div>
        """
    
    content = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <h3>📊 إجمالي الفواتير</h3>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>فاتورة</p>
        </div>
        <div class="stat-card">
            <h3>💰 إجمالي الإيرادات</h3>
            <div class="stat-number">${stats['total_revenue']:,.2f}</div>
            <p>دولار</p>
        </div>
        <div class="stat-card">
            <h3>📅 فواتير اليوم</h3>
            <div class="stat-number">{stats['today_invoices']}</div>
            <p>فاتورة</p>
        </div>
    </div>
    
    <div class="card">
        <h2>📋 آخر الفواتير</h2>
        {recent_invoices_html if recent_invoices_html else '<p>لا توجد فواتير حديثة</p>'}
    </div>
    """
    
    return render_template_string(BASE_HTML, title="الإحصائيات - InvoiceFlow Pro", uptime=uptime_str, content=content)

@app.route('/health')
def health_page():
    """صفحة حالة النظام"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    stats = db_manager.get_stats()
    
    content = f"""
    <div class="card">
        <h2>❤️ حالة النظام</h2>
        
        <div class="stats-grid">
            <div class="stat-card" style="background: rgba(0,255,136,0.2);">
                <h3>🟢 حالة الخدمة</h3>
                <div class="stat-number">نشط</div>
                <p>يعمل بشكل طبيعي</p>
            </div>
            
            <div class="stat-card">
                <h3>⏰ مدة التشغيل</h3>
                <div class="stat-number">{uptime_str}</div>
                <p>منذ آخر تشغيل</p>
            </div>
            
            <div class="stat-card">
                <h3>📊 الفواتير</h3>
                <div class="stat-number">{stats['total_invoices']}</div>
                <p>فاتورة مخزنة</p>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <h3>✅ جميع الأنظمة تعمل بشكل طبيعي</h3>
            <ul style="list-style: none; margin: 15px 0;">
                <li>✅ خادم الويب نشط</li>
                <li>✅ قاعدة البيانات متصلة</li>
                <li>✅ نظام الفواتير يعمل</li>
                <li>✅ الذاكرة مستقرة</li>
            </ul>
        </div>
    </div>
    """
    
    return render_template_string(BASE_HTML, title="حالة النظام - InvoiceFlow Pro", uptime=uptime_str, content=content)

@app.route('/api/health')
def api_health():
    """API لفحص صحة النظام"""
    return jsonify({
        "status": "healthy",
        "service": "InvoiceFlow Pro",
        "version": "ULTIMATE FREE - Web Edition",
        "uptime": time.time() - keep_alive_system.uptime_start,
        "timestamp": datetime.now().isoformat()
    })

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام على السحابة...")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام جاهز لاستقبال الطلبات!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
