# ================== InvoiceFlow Pro - النظام المجاني المستمر ==================
# 🎯 الإصدار ULTIMATE FREE - Maximum Uptime Edition
# 👨💻 فريق البروفيسورات المتخصصين
# 🔧 نظام مجاني يعمل لأطول فترة ممكنة

import os
import sqlite3
import json
import time
import requests
from datetime import datetime, timedelta
from threading import Thread, Lock
import sys

print("=" * 80)
print("🎯 InvoiceFlow Pro - النظام المجاني المستمر")
print("🚀 الإصدار ULTIMATE FREE - Maximum Uptime Edition")
print("👨💻 فريق البروفيسورات المتخصصين")
print("🔧 نظام مجاني يعمل 24/7 بأقصى استمرارية ممكنة")
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
        
        # 1. تشغيل خادم ويب بسيط
        self.start_web_server()
        
        # 2. بدء نظام البينغ التلقائي
        self.start_auto_ping()
        
        # 3. نظام المراقبة الذاتية
        self.start_self_monitoring()
        
        print("✅ جميع أنظمة الاستمرارية مفعلة!")
    
    def start_web_server(self):
        """تشغيل خادم ويب بسيط باستخدام مكتبات مدمجة"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            class KeepAliveHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    
                    uptime = time.time() - self.server.uptime_start
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    
                    html_content = f"""
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
                                max-width: 600px;
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
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🎯 InvoiceFlow Pro</h1>
                            <div class="status">✅ النظام يعمل بنجاح!</div>
                            
                            <div class="uptime">
                                ⏰ مدة التشغيل: {hours} ساعة {minutes} دقيقة
                            </div>
                            
                            <div class="info">🤖 البوت نشط وجاهز لاستقبال الطلبات</div>
                            <div class="info">📊 عدد الزيارات: {self.server.ping_count}</div>
                            <div class="info">🔧 الإصدار: ULTIMATE FREE - Maximum Uptime</div>
                            <div class="info">👨💻 فريق البروفيسورات المتخصصين</div>
                            <div class="info">🕒 آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html_content.encode('utf-8'))
                
                def log_message(self, format, *args):
                    pass  # تعطيل التسجيل لتقليل الضوضاء
            
            class CustomHTTPServer(HTTPServer):
                def __init__(self, *args, **kwargs):
                    self.uptime_start = time.time()
                    self.ping_count = 0
                    super().__init__(*args, **kwargs)
            
            def run_server():
                server = CustomHTTPServer(('0.0.0.0', 8080), KeepAliveHandler)
                print("🌐 خادم الويب يعمل على port 8080")
                server.serve_forever()
            
            server_thread = Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()
            
        except Exception as e:
            print(f"⚠️ تعذر تشغيل خادم الويب: {e}")
            print("🔧 استخدام الطريقة البديلة...")
            self.start_backup_keep_alive()
    
    def start_backup_keep_alive(self):
        """طريقة بديلة للإبقاء على التشغيل"""
        def keep_alive_loop():
            while True:
                try:
                    # إنشاء نشاط بسيط كل دقيقة
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"🟢 النظام نشط - {current_time}")
                    time.sleep(60)
                except:
                    time.sleep(60)
        
        backup_thread = Thread(target=keep_alive_loop)
        backup_thread.daemon = True
        backup_thread.start()
    
    def start_auto_ping(self):
        """بدء نظام البينغ التلقائي"""
        def auto_ping():
            while True:
                try:
                    # محاولة الوصول للخادم نفسه
                    response = requests.get('http://localhost:8080', timeout=10)
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

# بدء نظام الاستمرارية فوراً
keep_alive_system = AdvancedKeepAlive()
keep_alive_system.start_keep_alive()

# ================== نظام الترجمة المتطور ==================
class AdvancedTranslationSystem:
    """نظام ترجمة متطور متعدد اللغات"""
    
    def __init__(self):
        self.translations = {
            'ar': {
                'welcome': "🌟 **مرحباً بك في InvoiceFlow Pro!** 🌟\n\n🎯 النظام الذكي لإدارة الفواتير\n\n🚀 **اختر الإجراء المناسب:**",
                'create_invoice': "🧾 إنشاء فاتورة",
                'stats': "📊 الإحصائيات", 
                'help': "🆘 المساعدة",
                'exit': "🚪 خروج",
                'select_option': "👉 اختر رقم الخيار:",
                'enter_client_name': "👤 **أدخل اسم العميل:**",
                'enter_services': "💰 **أدخل الخدمات:**\n\n📝 استخدم التنسيق: `اسم الخدمة : السعر`\n\n💡 **أمثلة:**\n• تصميم موقع : 1500\n• استضافة : 500\n• صيانة : 300\n\n🚀 **اكتب 'تم' عند الانتهاء**",
                'service_added': "✅ **تمت الإضافة:** {} - ${}\n\n💰 **المجموع الحالي:** ${}\n\n💡 **استمر في الإضافة أو اكتب 'تم'**",
                'invoice_summary': "🧾 **ملخص الفاتورة**\n\n👤 **العميل:** {}\n\n💰 **الخدمات:**\n{}\n\n💵 **المجموع النهائي:** ${}\n\n🎯 **اختر الإجراء:**",
                'confirm_invoice': "✅ تأكيد إنشاء الفاتورة",
                'edit_invoice': "✏️ تعديل البيانات", 
                'cancel_invoice': "❌ إلغاء",
                'invoice_created': "🎉 **تم إنشاء الفاتورة بنجاح!**\n\n📋 **تفاصيل الفاتورة:**\n• 📄 رقم الفاتورة: `{}`\n• 💰 المبلغ الإجمالي: `${}`\n• 👤 اسم العميل: {}\n• 📅 تاريخ الإنشاء: {}\n\n✅ **الحالة:** \n• 💾 تم حفظ الفاتورة في النظام\n• 📊 تم تحديث الإحصائيات\n• 📁 تم إنشاء ملف الفاتورة",
                'new_invoice': "🧾 إنشاء فاتورة جديدة",
                'main_menu': "🏠 الرئيسية",
                'thank_you': "شكراً لاستخدامك InvoiceFlow Pro",
                'press_enter': "اضغط Enter للمتابعة...",
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

# ================== نظام واجهة المستخدم المتطور ==================
class ConsoleInterface:
    """نظام واجهة مستخدم Console متطورة"""
    
    def __init__(self, translation_system):
        self.translation = translation_system
        
    def clear_screen(self):
        """مسح الشاشة"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_header(self, title, language='ar'):
        """عرض عنوان الشاشة"""
        self.clear_screen()
        print("=" * 60)
        print(f"🎯 {title}")
        print("=" * 60)
        print()
        
    def show_menu(self, options, language='ar'):
        """عرض قائمة خيارات"""
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print()
        
    def get_choice(self, prompt, language='ar'):
        """الحصول على اختيار المستخدم"""
        try:
            choice = input(f"👉 {prompt} ")
            return choice.strip()
        except KeyboardInterrupt:
            return 'exit'
        except:
            return ''
            
    def show_message(self, message, language='ar'):
        """عرض رسالة"""
        print(f"\n{message}\n")
        
    def wait_for_enter(self, language='ar'):
        """انتظار ضغط Enter"""
        input(self.translation.get_text('press_enter', language))

# ================== نظام إدارة الجلسات المتطور ==================
class SessionManager:
    """نظام إدارة جلسات متطور"""

    def __init__(self):
        self.sessions = {}
        self.lock = Lock()
        self.session_timeout = 1800

    def create_session(self, user_id="console", session_type="invoice"):
        with self.lock:
            self.sessions[user_id] = {
                'type': session_type,
                'step': 'start',
                'data': {},
                'created_at': time.time(),
                'last_activity': time.time(),
                'is_active': True
            }
            return True

    def get_session(self, user_id="console"):
        with self.lock:
            session = self.sessions.get(user_id)
            if session and self._is_session_valid(session):
                session['last_activity'] = time.time()
                return session
            elif session:
                del self.sessions[user_id]
            return None

    def update_session(self, user_id="console", step=None, data=None):
        with self.lock:
            if user_id in self.sessions:
                if step:
                    self.sessions[user_id]['step'] = step
                if data:
                    self.sessions[user_id]['data'].update(data)
                self.sessions[user_id]['last_activity'] = time.time()
                return True
            return False

    def end_session(self, user_id="console"):
        with self.lock:
            if user_id in self.sessions:
                del self.sessions[user_id]
                return True
            return False

    def _is_session_valid(self, session):
        if not session.get('is_active', True):
            return False
        time_diff = time.time() - session.get('last_activity', 0)
        return time_diff < self.session_timeout

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
                invoice_data.get('user_id', 'console'),
                invoice_data.get('user_name', 'مستخدم'),
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
                invoice_data.get('user_id', 'console'),
                invoice_data.get('user_name', 'مستخدم'),
                invoice_data.get('user_id', 'console'),
                invoice_data.get('user_id', 'console'),
                invoice_data['total_amount']
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"🔧 خطأ في تحديث الإحصائيات: {e}")

# ================== نظام إنشاء الفواتير المتطور ==================
class InvoiceGenerator:
    """نظام إنشاء الفواتير المتطور"""
    
    def __init__(self, translation_system):
        self.translation = translation_system
        
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

# ================== نظام إدارة الفواتير المتطور ==================
class InvoiceManager:
    """نظام إدارة الفواتير المتطور"""

    def __init__(self, session_manager, db_manager, translation_system, interface, invoice_generator):
        self.session_manager = session_manager
        self.db_manager = db_manager
        self.translation = translation_system
        self.interface = interface
        self.invoice_generator = invoice_generator
        self.current_language = 'ar'

    def start_invoice_creation(self):
        self.session_manager.create_session(language=self.current_language)
        return self._get_client_info()

    def _get_client_info(self):
        self.interface.show_header(self.translation.get_text('create_invoice', self.current_language), self.current_language)
        
        client_name = self.interface.get_choice(self.translation.get_text('enter_client_name', self.current_language), self.current_language)
        
        if client_name.lower() in ['exit', 'خروج']:
            return False
            
        email = self.interface.get_choice("📧 أدخل البريد الإلكتروني (اختياري):", self.current_language)
        if email.lower() in ['exit', 'خروج']:
            return False
            
        phone = self.interface.get_choice("📞 أدخل رقم الهاتف (اختياري):", self.current_language)
        if phone.lower() in ['exit', 'خروج']:
            return False

        self.session_manager.update_session(
            data={
                'client_name': client_name,
                'client_email': email if email else '',
                'client_phone': phone if phone else ''
            }, 
            step='services'
        )
        return self._get_services()

    def _get_services(self):
        services = []
        
        while True:
            self.interface.show_header(self.translation.get_text('create_invoice', self.current_language), self.current_language)
            
            if services:
                total = sum(s['price'] for s in services)
                print(f"💰 **المجموع الحالي:** ${total:.2f}")
                print()
                
            service_input = self.interface.get_choice(self.translation.get_text('enter_services', self.current_language), self.current_language)
            
            if service_input.lower() in ['تم', 'done', 'exit', 'خروج']:
                if not services:
                    self.interface.show_message(self.translation.get_text('no_services', self.current_language), self.current_language)
                    self.interface.wait_for_enter(self.current_language)
                    continue
                break
                
            if ':' in service_input:
                parts = service_input.split(':', 1)
                service_name = parts[0].strip()
                try:
                    service_price = float(parts[1].strip())
                    services.append({
                        'name': service_name,
                        'price': service_price,
                        'quantity': 1
                    })
                    
                    total = sum(s['price'] for s in services)
                    self.interface.show_message(
                        self.translation.get_text('service_added', self.current_language, service_name, service_price, total),
                        self.current_language
                    )
                    self.interface.wait_for_enter(self.current_language)
                    
                except ValueError:
                    self.interface.show_message(self.translation.get_text('price_error', self.current_language), self.current_language)
                    self.interface.wait_for_enter(self.current_language)
            else:
                self.interface.show_message(self.translation.get_text('format_error', self.current_language), self.current_language)
                self.interface.wait_for_enter(self.current_language)
                
        self.session_manager.update_session(data={'services': services})
        return self._show_invoice_summary()

    def _show_invoice_summary(self):
        session = self.session_manager.get_session()
        client_name = session['data'].get('client_name', '')
        services = session['data'].get('services', [])
        total = sum(s['price'] for s in services)
        
        invoice_data = {
            'client_name': client_name,
            'services': services,
            'total_amount': total
        }
        
        self.interface.show_invoice_summary(invoice_data, self.current_language)
        
        options = [
            self.translation.get_text('confirm_invoice', self.current_language),
            self.translation.get_text('edit_invoice', self.current_language),
            self.translation.get_text('cancel_invoice', self.current_language)
        ]
        
        self.interface.show_menu(options, self.current_language)
        choice = self.interface.get_choice(self.translation.get_text('select_option', self.current_language), self.current_language)
        
        if choice == '1':
            return self._confirm_invoice()
        elif choice == '2':
            return self._get_services()
        elif choice == '3':
            self.session_manager.end_session()
            return True
        else:
            self.interface.show_message(self.translation.get_text('invalid_choice', self.current_language), self.current_language)
            self.interface.wait_for_enter(self.current_language)
            return self._show_invoice_summary()

    def _confirm_invoice(self):
        session = self.session_manager.get_session()
        client_name = session['data'].get('client_name', '')
        client_email = session['data'].get('client_email', '')
        client_phone = session['data'].get('client_phone', '')
        services = session['data'].get('services', [])
        total = sum(s['price'] for s in services)
        
        invoice_data = {
            'invoice_id': f"INV-{int(time.time())}",
            'user_id': 'console',
            'user_name': 'مستخدم',
            'client_name': client_name,
            'client_email': client_email,
            'client_phone': client_phone,
            'services': services,
            'total_amount': total,
            'issue_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
        
        success = self.db_manager.save_invoice(invoice_data)
        
        if success:
            file_path = self.invoice_generator.create_text_invoice(invoice_data, self.current_language)
            
            self.interface.show_header(self.translation.get_text('invoice_created', self.current_language), self.current_language)
            print(self.translation.get_text('invoice_details', self.current_language))
            print(self.translation.get_text('invoice_id', self.current_language, invoice_data['invoice_id']))
            print(self.translation.get_text('client', self.current_language, client_name))
            print(f"📧 البريد الإلكتروني: {client_email}" if client_email else "")
            print(f"📞 الهاتف: {client_phone}" if client_phone else "")
            print(self.translation.get_text('total_amount', self.current_language, total))
            
            if file_path:
                print(f"📁 تم إنشاء ملف الفاتورة: {file_path}")
                
            print()
            self.interface.show_message(self.translation.get_text('thank_you', self.current_language), self.current_language)
            
        else:
            self.interface.show_message("❌ فشل في حفظ الفاتورة", self.current_language)
            
        self.session_manager.end_session()
        self.interface.wait_for_enter(self.current_language)
        return True

    def show_stats(self):
        self.interface.show_header(self.translation.get_text('stats', self.current_language), self.current_language)
        
        try:
            conn = sqlite3.connect('invoices_pro.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM invoices')
            total_invoices, total_revenue = cursor.fetchone()
            
            print(f"📊 الإحصائيات العامة:")
            print(f"   • عدد الفواتير: {total_invoices}")
            print(f"   • إجمالي الإيرادات: ${total_revenue:.2f}")
            print()
            
            cursor.execute('''
                SELECT invoice_id, client_name, total_amount, issue_date 
                FROM invoices 
                ORDER BY created_at DESC 
                LIMIT 5
            ''')
            
            recent_invoices = cursor.fetchall()
            
            if recent_invoices:
                print("📋 آخر الفواتير:")
                for invoice in recent_invoices:
                    print(f"   • {invoice[0]} - {invoice[1]} - ${invoice[2]:.2f}")
            
            conn.close()
            
        except Exception as e:
            print(f"🔧 خطأ في عرض الإحصائيات: {e}")
            
        print()
        self.interface.wait_for_enter(self.current_language)

    def show_help(self):
        self.interface.show_header(self.translation.get_text('help', self.current_language), self.current_language)
        
        help_text = """
📖 دليل استخدام النظام:

1. إنشاء فاتورة:
   • اختر "إنشاء فاتورة" من القائمة الرئيسية
   • أدخل اسم العميل
   • أدخل البريد الإلكتروني والهاتف (اختياري)
   • أدخل الخدمات بالشكل: "اسم الخدمة : السعر"
   • اكتب "تم" عند الانتهاء من إدخال الخدمات
   • تأكيد إنشاء الفاتورة

2. تنسيق إدخال الخدمات:
   • استخدم النقطتين (:) لفصل اسم الخدمة عن السعر
   • أمثلة:
        تصميم موقع : 1500
        استضافة : 500
        صيانة : 300

3. المميزات:
   • نظام متعدد اللغات (عربي/إنجليزي)
   • حفظ تلقائي للفواتير في قاعدة البيانات
   • إنشاء ملفات نصية للفواتير
   • إحصائيات مفصلة
   • إدارة جلسات متقدمة
"""
        
        print(help_text)
        self.interface.wait_for_enter(self.current_language)

    def change_language(self):
        self.interface.show_header("تغيير اللغة / Change Language", self.current_language)
        
        options = ["العربية / Arabic", "English / الإنجليزية"]
        self.interface.show_menu(options, self.current_language)
        
        choice = self.interface.get_choice("اختر اللغة / Select language", self.current_language)
        
        if choice == '1':
            self.current_language = 'ar'
            self.interface.show_message("✅ تم تغيير اللغة إلى العربية", 'ar')
        elif choice == '2':
            self.current_language = 'en'
            self.interface.show_message("✅ Language changed to English", 'en')
        else:
            self.interface.show_message(self.translation.get_text('invalid_choice', self.current_language), self.current_language)
            
        self.interface.wait_for_enter(self.current_language)

# ================== النظام الرئيسي المتكامل ==================
class UltimateInvoiceSystem:
    """النظام الرئيسي المتكامل"""

    def __init__(self):
        self.translation_system = AdvancedTranslationSystem()
        self.interface = ConsoleInterface(self.translation_system)
        self.session_manager = SessionManager()
        self.db_manager = DatabaseManager()
        self.invoice_generator = InvoiceGenerator(self.translation_system)
        self.invoice_manager = InvoiceManager(
            self.session_manager,
            self.db_manager,
            self.translation_system,
            self.interface,
            self.invoice_generator
        )

    def run(self):
        print("\n🚀 بدء تشغيل InvoiceFlow Pro...")
        print("✅ النظام جاهز للعمل!")
        print("🔧 نظام مجاني مع أقصى استمرارية ممكنة")
        print("=" * 60)
        
        self.interface.wait_for_enter('ar')
        self.show_main_menu()

    def show_main_menu(self):
        while True:
            self.interface.show_header(self.translation_system.get_text('welcome', self.invoice_manager.current_language), self.invoice_manager.current_language)
            
            options = [
                self.translation_system.get_text('create_invoice', self.invoice_manager.current_language),
                self.translation_system.get_text('stats', self.invoice_manager.current_language),
                self.translation_system.get_text('help', self.invoice_manager.current_language),
                "🌍 تغيير اللغة / Change Language",
                self.translation_system.get_text('exit', self.invoice_manager.current_language)
            ]
            
            self.interface.show_menu(options, self.invoice_manager.current_language)
            
            choice = self.interface.get_choice(self.translation_system.get_text('select_option', self.invoice_manager.current_language), self.invoice_manager.current_language)
            
            if choice == '1':
                self.invoice_manager.start_invoice_creation()
            elif choice == '2':
                self.invoice_manager.show_stats()
            elif choice == '3':
                self.invoice_manager.show_help()
            elif choice == '4':
                self.invoice_manager.change_language()
            elif choice == '5' or choice.lower() in ['exit', 'خروج']:
                print("\n🎉 شكراً لاستخدامك InvoiceFlow Pro!")
                print("👋 إلى اللقاء!")
                break
            else:
                self.interface.show_message(self.translation_system.get_text('invalid_choice', self.invoice_manager.current_language), self.invoice_manager.current_language)
                self.interface.wait_for_enter(self.invoice_manager.current_language)

# ================== التشغيل الرئيسي مع الاستمرارية ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام المجاني المستمر...")
        system = UltimateInvoiceSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n👋 تم إيقاف النظام بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
        print("🔄 جاري إعادة التشغيل التلقائي...")
        time.sleep(5)
        
        # إعادة التشغيل التلقائي
        try:
            system = UltimateInvoiceSystem()
            system.run()
        except:
            print("❌ فشل في إعادة التشغيل، يرجى تحديث الصفحة")
