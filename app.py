import os
import sqlite3
import json
import time
import hashlib
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from email_validator import validate_email, EmailNotValidError

# ================== تطبيق Flask المتقدم ==================
app = Flask(__name__)
app.secret_key = 'invoiceflow_black_elite_2024_v1'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Elite - الإصدار الأسود الفاخر")
print("🚀 تصميم أسود مميز + ذهبي أنيق + حدّة تقنية")
print("👑 فريق النخبة البروفيسوري - المرحلة الأولى")
print("=" * 80)

# ================== نظام الألوان الأسود الفاخر ==================
BLACK_ELITE_DESIGN = """
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
            /* نظام الألوان الأسود الفاخر */
            --primary-black: #0A0A0A;
            --dark-black: #000000;
            --light-black: #1A1A1A;
            --charcoal: #2D2D2D;
            --elite-gold: #D4AF37;
            --light-gold: #F4D03F;
            --pure-white: #FFFFFF;
            --smoke-white: #F5F5F5;
            --accent-red: #E74C3C;
            --accent-green: #27AE60;
            --accent-blue: #3498DB;
            
            /* تأثيرات التدرج */
            --gold-gradient: linear-gradient(135deg, var(--elite-gold), var(--light-gold));
            --black-gradient: linear-gradient(135deg, var(--primary-black), var(--dark-black));
            --card-gradient: linear-gradient(145deg, #1A1A1A, #0F0F0F);
            
            /* الظلال */
            --shadow-elite: 0 20px 40px rgba(0, 0, 0, 0.5);
            --shadow-gold: 0 0 30px rgba(212, 175, 55, 0.3);
            --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--black-gradient);
            color: var(--pure-white);
            min-height: 100vh;
            line-height: 1.7;
            overflow-x: hidden;
        }
        
        .elite-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
        }
        
        /* ================== شاشة تسجيل الدخول الفاخرة ================== */
        .login-wrapper {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--black-gradient);
            position: relative;
            overflow: hidden;
        }
        
        .login-wrapper::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(212, 175, 55, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(212, 175, 55, 0.05) 0%, transparent 50%);
            animation: backgroundShift 10s ease-in-out infinite;
        }
        
        @keyframes backgroundShift {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        .login-card {
            background: var(--card-gradient);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 24px;
            padding: 60px 50px;
            width: 100%;
            max-width: 480px;
            position: relative;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-elite), var(--shadow-gold);
            animation: cardEntrance 0.8s cubic-bezier(0.4, 0, 0.2, 1);
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
        
        .login-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gold-gradient);
            border-radius: 24px 24px 0 0;
        }
        
        .logo-section {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .logo-icon {
            font-size: 3.5em;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            display: inline-block;
            animation: logoPulse 3s ease-in-out infinite;
        }
        
        @keyframes logoPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .logo-text {
            font-size: 2.8em;
            font-weight: 800;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .logo-subtitle {
            color: var(--smoke-white);
            font-size: 1.1em;
            font-weight: 300;
            opacity: 0.8;
        }
        
        .elite-form-group {
            margin-bottom: 30px;
            position: relative;
        }
        
        .form-label {
            display: block;
            margin-bottom: 12px;
            color: var(--pure-white);
            font-weight: 600;
            font-size: 1.1em;
            text-align: right;
        }
        
        .input-wrapper {
            position: relative;
        }
        
        .elite-form-control {
            width: 100%;
            padding: 20px 25px;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            color: var(--pure-white);
            font-size: 1.1em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(10px);
        }
        
        .elite-form-control:focus {
            outline: none;
            border-color: var(--elite-gold);
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.1);
            transform: translateY(-2px);
        }
        
        .input-icon {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--elite-gold);
            font-size: 1.2em;
        }
        
        .elite-btn {
            background: var(--gold-gradient);
            color: var(--dark-black);
            padding: 20px 40px;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 700;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .elite-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .elite-btn:hover::before {
            left: 100%;
        }
        
        .elite-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4);
        }
        
        .elite-btn:active {
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: transparent;
            border: 2px solid var(--elite-gold);
            color: var(--elite-gold);
        }
        
        .btn-secondary:hover {
            background: var(--elite-gold);
            color: var(--dark-black);
        }
        
        .login-footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .footer-text {
            color: var(--smoke-white);
            opacity: 0.7;
            font-size: 0.95em;
        }
        
        .security-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(39, 174, 96, 0.1);
            border: 1px solid rgba(39, 174, 96, 0.3);
            color: var(--accent-green);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            margin-top: 15px;
        }
        
        /* ================== لوحة التحكم ================== */
        .elite-header {
            background: var(--card-gradient);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }
        
        .elite-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gold-gradient);
        }
        
        .header-content h1 {
            font-size: 3.2em;
            font-weight: 800;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
        }
        
        .header-content p {
            font-size: 1.3em;
            color: var(--smoke-white);
            opacity: 0.8;
            font-weight: 300;
        }
        
        .elite-user-panel {
            position: absolute;
            left: 40px;
            top: 40px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            padding: 15px 25px;
            border-radius: 15px;
            border: 1px solid rgba(212, 175, 55, 0.3);
            color: var(--smoke-white);
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .elite-admin-badge {
            background: var(--gold-gradient);
            color: var(--dark-black);
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 700;
            border: 1px solid var(--elite-gold);
        }
        
        .elite-navigation {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .elite-nav-card {
            background: var(--card-gradient);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 35px 30px;
            text-align: center;
            color: var(--pure-white);
            text-decoration: none;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }
        
        .elite-nav-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gold-gradient);
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }
        
        .elite-nav-card:hover {
            transform: translateY(-8px);
            border-color: var(--elite-gold);
            box-shadow: var(--shadow-card), var(--shadow-gold);
        }
        
        .elite-nav-card:hover::before {
            transform: scaleX(1);
        }
        
        .elite-nav-card i {
            font-size: 3.2em;
            margin-bottom: 25px;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            transition: all 0.4s ease;
        }
        
        .elite-nav-card:hover i {
            transform: scale(1.1);
        }
        
        .elite-nav-card h3 {
            font-size: 1.5em;
            margin-bottom: 15px;
            color: var(--pure-white);
            font-weight: 700;
        }
        
        .elite-nav-card p {
            color: var(--smoke-white);
            font-size: 1em;
            line-height: 1.6;
            opacity: 0.8;
        }
        
        .elite-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }
        
        .elite-stat-card {
            background: var(--card-gradient);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 35px 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }
        
        .elite-stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gold-gradient);
        }
        
        .elite-stat-number {
            font-size: 3.5em;
            font-weight: 800;
            margin: 20px 0;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .elite-stat-card p {
            font-size: 1.2em;
            color: var(--smoke-white);
            font-weight: 600;
            opacity: 0.9;
        }
        
        .elite-alert {
            padding: 25px 30px;
            border-radius: 16px;
            margin: 25px 0;
            text-align: center;
            font-weight: 600;
            border: 1px solid;
            backdrop-filter: blur(10px);
            font-size: 1.1em;
        }
        
        .elite-alert-success {
            background: rgba(39, 174, 96, 0.1);
            border-color: var(--accent-green);
            color: var(--accent-green);
        }
        
        .elite-alert-error {
            background: rgba(231, 76, 60, 0.1);
            border-color: var(--accent-red);
            color: var(--accent-red);
        }
        
        .elite-profile-section {
            background: var(--card-gradient);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 35px;
            margin: 25px 0;
            box-shadow: var(--shadow-card);
        }
        
        /* تأثيرات الاستجابة */
        @media (max-width: 768px) {
            .elite-container {
                padding: 15px;
            }
            
            .login-card {
                padding: 40px 30px;
                margin: 20px;
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
                justify-content: center;
            }
            
            .elite-navigation {
                grid-template-columns: 1fr;
            }
            
            .elite-stats-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* تأثيرات تحميل إضافية */
        .loading-dots {
            display: inline-flex;
            gap: 4px;
        }
        
        .loading-dots span {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--elite-gold);
            animation: loadingDot 1.4s ease-in-out infinite both;
        }
        
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes loadingDot {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    {% if not is_login_page %}
    <div class="elite-container">
        {% if session.user_logged_in %}
        <div class="elite-user-panel">
            {% if session.user_type == 'admin' %}
            <span class="elite-admin-badge">👑 نخبة</span>
            {% endif %}
            <i class="fas fa-user-tie"></i> {{ session.username }}
            | <a href="/elite/profile" style="color: var(--elite-gold); margin: 0 15px;">الملف الشخصي</a>
            | <a href="/elite/logout" style="color: var(--smoke-white);">تسجيل خروج</a>
        </div>
        {% endif %}
        
        <div class="elite-header">
            <div class="header-content">
                <h1><i class="fas fa-crown"></i> InvoiceFlow Elite</h1>
                <p>🚀 النظام النخبوي الأسود - التميز في كل تفصيل</p>
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
    {% else %}
    <div class="login-wrapper">
        {{ content | safe }}
    </div>
    {% endif %}

    <script>
        // تأثيرات النخبة المتقدمة
        document.addEventListener('DOMContentLoaded', function() {
            // تأثيرات الكروت
            const cards = document.querySelectorAll('.elite-nav-card, .elite-stat-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
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
            
            // تأثيرات حقول الإدخال
            const inputs = document.querySelectorAll('.elite-form-control');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.style.transform = 'translateY(-2px)';
                });
                input.addEventListener('blur', function() {
                    this.parentElement.style.transform = 'translateY(0)';
                });
            });
            
            // تحميل متحرك للصفحة
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);
        });
        
        // تأثيرات العدادات المتحركة
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

# ================== نظام إدارة المستخدمين ==================
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

# ================== نظام قاعدة البيانات ==================
class EliteDatabaseManager:
    def __init__(self):
        self.db_path = 'invoices_elite.db'
        self.init_elite_database()

    def init_elite_database(self):
        """تهيئة قاعدة البيانات النخبوية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

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

            conn.commit()
            conn.close()
            print("✅ قاعدة البيانات النخبوية جاهزة")
        except Exception as e:
            print(f"🔧 خطأ في قاعدة البيانات: {e}")

    def get_elite_stats(self, username):
        """إحصائيات نخبوية للمستخدم"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # إجمالي الفواتير
            cursor.execute('SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM elite_invoices WHERE user_id = ?', (username,))
            result = cursor.fetchone()
            total_invoices = result[0] if result else 0
            total_revenue = result[1] if result else 0
            
            # الفواتير المعلقة
            cursor.execute('SELECT COUNT(*) FROM elite_invoices WHERE user_id = ? AND status = "معلقة"', (username,))
            pending_invoices = cursor.fetchone()[0] or 0
            
            # فواتير اليوم
            cursor.execute('SELECT COUNT(*) FROM elite_invoices WHERE user_id = ? AND date(created_at) = date("now")', (username,))
            today_invoices = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_invoices': total_invoices,
                'total_revenue': total_revenue,
                'pending_invoices': pending_invoices,
                'today_invoices': today_invoices
            }
        except Exception as e:
            print(f"🔧 خطأ في جلب الإحصائيات: {e}")
            return {'total_invoices': 0, 'total_revenue': 0, 'pending_invoices': 0, 'today_invoices': 0}

# ================== نظام الإبقاء على التشغيل ==================
class EliteKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.ping_count = 0
        
    def start_elite_keep_alive(self):
        print("🔄 بدء أنظمة النخبة السوداء...")
        self.start_elite_monitoring()
        print("✅ أنظمة النخبة السوداء مفعلة!")
    
    def start_elite_monitoring(self):
        def monitor():
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                if int(current_time) % 600 == 0:
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"📊 تقرير النخبة السوداء: {hours}س {minutes}د - {self.ping_count} زيارات نخبوية")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# ================== إعداد الأنظمة النخبوية ==================
elite_db = EliteDatabaseManager()
elite_users = EliteUserManager()
keep_alive_system = EliteKeepAlive()
keep_alive_system.start_elite_keep_alive()

# ================== Routes النخبوية ==================
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
    
    admin_button = ''
    if session.get('user_type') == 'admin':
        admin_button = '<a href="/elite/admin" class="elite-btn" style="margin-top: 20px;"><i class="fas fa-crown"></i> لوحة التحكم</a>'
    
    content = f"""
    <div class="elite-stats-grid">
        <div class="elite-stat-card">
            <i class="fas fa-file-invoice"></i>
            <div class="elite-stat-number" data-target="{stats['total_invoices']}">{stats['total_invoices']}</div>
            <p>إجمالي الفواتير</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-dollar-sign"></i>
            <div class="elite-stat-number" data-target="{int(stats['total_revenue'])}">${stats['total_revenue']:,.0f}</div>
            <p>إجمالي الإيرادات</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-clock"></i>
            <div class="elite-stat-number" data-target="{stats['pending_invoices']}">{stats['pending_invoices']}</div>
            <p>فواتير معلقة</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-chart-line"></i>
            <div class="elite-stat-number" data-target="{85}">85%</div>
            <p>كفاءة النظام</p>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 40px;">
        <div class="elite-profile-section">
            <h3 style="margin-bottom: 20px; color: var(--pure-white);">
                <i class="fas fa-bolt"></i> إجراءات سريعة
            </h3>
            <div style="display: flex; flex-direction: column; gap: 15px;">
                <a href="/elite/create" class="elite-btn">
                    <i class="fas fa-plus"></i> إنشاء فاتورة جديدة
                </a>
                <a href="/elite/invoices" class="elite-btn btn-secondary">
                    <i class="fas fa-list"></i> عرض جميع الفواتير
                </a>
                {admin_button}
            </div>
        </div>
        
        <div class="elite-profile-section">
            <h3 style="margin-bottom: 20px; color: var(--pure-white);">
                <i class="fas fa-star"></i> مزايا النخبة السوداء
            </h3>
            <div style="color: var(--smoke-white); line-height: 2;">
                <p>🎯 تصميم أسود فاخر بلمسات ذهبية</p>
                <p>⚡ واجهات مستخدم سريعة واستجابة</p>
                <p>🔐 نظام أمني متكامل وحماية بيانات</p>
                <p>📊 تحليلات ذكية وتقارير متقدمة</p>
                <p>🎨 تجربة مستخدم فريدة ومتميزة</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(BLACK_ELITE_DESIGN, title="InvoiceFlow Elite - النظام الأسود", uptime=uptime_str, content=content, is_login_page=False)

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
            login_content = """
            <div class="login-card">
                <div class="logo-section">
                    <div class="logo-icon">
                        <i class="fas fa-crown"></i>
                    </div>
                    <div class="logo-text">InvoiceFlow Elite</div>
                    <div class="logo-subtitle">النظام الأسود الفاخر لإدارة الفواتير</div>
                </div>
                
                <div class="elite-alert elite-alert-error">
                    <i class="fas fa-exclamation-triangle"></i> بيانات الدخول غير صحيحة
                </div>
                
                <form method="POST">
                    <div class="elite-form-group">
                        <label class="form-label">اسم المستخدم</label>
                        <div class="input-wrapper">
                            <input type="text" name="username" class="elite-form-control" placeholder="أدخل اسم المستخدم النخبوي" required>
                            <div class="input-icon">
                                <i class="fas fa-user"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="elite-form-group">
                        <label class="form-label">كلمة المرور</label>
                        <div class="input-wrapper">
                            <input type="password" name="password" class="elite-form-control" placeholder="أدخل كلمة المرور" required>
                            <div class="input-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="elite-btn">
                        <i class="fas fa-sign-in-alt"></i> دخول النخبة
                    </button>
                </form>
                
                <div class="login-footer">
                    <div class="footer-text">ليس لديك حساب؟ انضم إلى النخبة</div>
                    <a href="/elite/register" class="elite-btn btn-secondary" style="margin-top: 15px;">
                        <i class="fas fa-user-plus"></i> إنشاء حساب جديد
                    </a>
                    <div class="security-badge">
                        <i class="fas fa-shield-alt"></i>
                        نظام آمن ومشفر
                    </div>
                </div>
            </div>
            """
            return render_template_string(BLACK_ELITE_DESIGN, title="تسجيل الدخول - InvoiceFlow Elite", content=login_content, is_login_page=True)
    
    if 'user_logged_in' in session:
        return redirect(url_for('elite_home'))
    
    login_content = """
    <div class="login-card">
        <div class="logo-section">
            <div class="logo-icon">
                <i class="fas fa-crown"></i>
            </div>
            <div class="logo-text">InvoiceFlow Elite</div>
            <div class="logo-subtitle">النظام الأسود الفاخر لإدارة الفواتير</div>
        </div>
        
        <form method="POST">
            <div class="elite-form-group">
                <label class="form-label">اسم المستخدم</label>
                <div class="input-wrapper">
                    <input type="text" name="username" class="elite-form-control" placeholder="أدخل اسم المستخدم النخبوي" required>
                    <div class="input-icon">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            </div>
            
            <div class="elite-form-group">
                <label class="form-label">كلمة المرور</label>
                <div class="input-wrapper">
                    <input type="password" name="password" class="elite-form-control" placeholder="أدخل كلمة المرور" required>
                    <div class="input-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="elite-btn">
                <i class="fas fa-sign-in-alt"></i> دخول النخبة
            </button>
        </form>
        
        <div class="login-footer">
            <div class="footer-text">ليس لديك حساب؟ انضم إلى النخبة</div>
            <a href="/elite/register" class="elite-btn btn-secondary" style="margin-top: 15px;">
                <i class="fas fa-user-plus"></i> إنشاء حساب جديد
            </a>
            <div class="security-badge">
                <i class="fas fa-shield-alt"></i>
                نظام آمن ومشفر
            </div>
        </div>
    </div>
    """
    return render_template_string(BLACK_ELITE_DESIGN, title="تسجيل الدخول - InvoiceFlow Elite", content=login_content, is_login_page=True)

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
            register_content = f"""
            <div class="login-card">
                <div class="logo-section">
                    <div class="logo-icon">
                        <i class="fas fa-crown"></i>
                    </div>
                    <div class="logo-text">InvoiceFlow Elite</div>
                    <div class="logo-subtitle">انضم إلى النخبة</div>
                </div>
                
                <div class="elite-alert elite-alert-success">
                    <i class="fas fa-check-circle"></i> {message}
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/elite/login" class="elite-btn">
                        <i class="fas fa-sign-in-alt"></i> الانتقال لتسجيل الدخول
                    </a>
                </div>
            </div>
            """
            return render_template_string(BLACK_ELITE_DESIGN, title="تم الإنشاء - InvoiceFlow Elite", content=register_content, is_login_page=True)
        else:
            register_content = f"""
            <div class="login-card">
                <div class="logo-section">
                    <div class="logo-icon">
                        <i class="fas fa-crown"></i>
                    </div>
                    <div class="logo-text">InvoiceFlow Elite</div>
                    <div class="logo-subtitle">انضم إلى النخبة</div>
                </div>
                
                <div class="elite-alert elite-alert-error">
                    <i class="fas fa-exclamation-triangle"></i> {message}
                </div>
                
                <form method="POST">
                    <div class="elite-form-group">
                        <label class="form-label">اسم المستخدم</label>
                        <div class="input-wrapper">
                            <input type="text" name="username" class="elite-form-control" placeholder="اختر اسم مستخدم فريد" value="{username}" required>
                            <div class="input-icon">
                                <i class="fas fa-user"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="elite-form-group">
                        <label class="form-label">كلمة المرور</label>
                        <div class="input-wrapper">
                            <input type="password" name="password" class="elite-form-control" placeholder="كلمة مرور قوية" required>
                            <div class="input-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="elite-form-group">
                        <label class="form-label">البريد الإلكتروني</label>
                        <div class="input-wrapper">
                            <input type="email" name="email" class="elite-form-control" placeholder="example@elite.com" value="{email}" required>
                            <div class="input-icon">
                                <i class="fas fa-envelope"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="elite-form-group">
                        <label class="form-label">الاسم الكامل</label>
                        <div class="input-wrapper">
                            <input type="text" name="full_name" class="elite-form-control" placeholder="الاسم الثلاثي" value="{full_name}" required>
                            <div class="input-icon">
                                <i class="fas fa-id-card"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="elite-form-group">
                        <label class="form-label">اسم الشركة (اختياري)</label>
                        <div class="input-wrapper">
                            <input type="text" name="company_name" class="elite-form-control" placeholder="اسم شركتك" value="{company_name}">
                            <div class="input-icon">
                                <i class="fas fa-building"></i>
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit" class="elite-btn">
                        <i class="fas fa-user-plus"></i> انضم إلى النخبة
                    </button>
                </form>
                
                <div class="login-footer">
                    <a href="/elite/login" class="elite-btn btn-secondary">
                        <i class="fas fa-arrow-right"></i> لديك حساب؟ سجل الدخول
                    </a>
                </div>
            </div>
            """
            return render_template_string(BLACK_ELITE_DESIGN, title="التسجيل - InvoiceFlow Elite", content=register_content, is_login_page=True)
    
    register_content = """
    <div class="login-card">
        <div class="logo-section">
            <div class="logo-icon">
                <i class="fas fa-crown"></i>
            </div>
            <div class="logo-text">InvoiceFlow Elite</div>
            <div class="logo-subtitle">انضم إلى النخبة</div>
        </div>
        
        <form method="POST">
            <div class="elite-form-group">
                <label class="form-label">اسم المستخدم</label>
                <div class="input-wrapper">
                    <input type="text" name="username" class="elite-form-control" placeholder="اختر اسم مستخدم فريد" required>
                    <div class="input-icon">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            </div>
            
            <div class="elite-form-group">
                <label class="form-label">كلمة المرور</label>
                <div class="input-wrapper">
                    <input type="password" name="password" class="elite-form-control" placeholder="كلمة مرور قوية" required>
                    <div class="input-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                </div>
            </div>
            
            <div class="elite-form-group">
                <label class="form-label">البريد الإلكتروني</label>
                <div class="input-wrapper">
                    <input type="email" name="email" class="elite-form-control" placeholder="example@elite.com" required>
                    <div class="input-icon">
                        <i class="fas fa-envelope"></i>
                    </div>
                </div>
            </div>
            
            <div class="elite-form-group">
                <label class="form-label">الاسم الكامل</label>
                <div class="input-wrapper">
                    <input type="text" name="full_name" class="elite-form-control" placeholder="الاسم الثلاثي" required>
                    <div class="input-icon">
                        <i class="fas fa-id-card"></i>
                    </div>
                </div>
            </div>
            
            <div class="elite-form-group">
                <label class="form-label">اسم الشركة (اختياري)</label>
                <div class="input-wrapper">
                    <input type="text" name="company_name" class="elite-form-control" placeholder="اسم شركتك">
                    <div class="input-icon">
                        <i class="fas fa-building"></i>
                    </div>
                </div>
            </div>
            
            <button type="submit" class="elite-btn">
                <i class="fas fa-user-plus"></i> انضم إلى النخبة
            </button>
        </form>
        
        <div class="login-footer">
            <a href="/elite/login" class="elite-btn btn-secondary">
                <i class="fas fa-arrow-right"></i> لديك حساب؟ سجل الدخول
            </a>
        </div>
    </div>
    """
    return render_template_string(BLACK_ELITE_DESIGN, title="التسجيل - InvoiceFlow Elite", content=register_content, is_login_page=True)

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
    
    stats = elite_db.get_elite_stats(session['username'])
    
    content = f"""
    <div class="elite-header">
        <h2 style="margin-bottom: 20px; text-align: center;">
            <i class="fas fa-user-tie"></i> الملف الشخصي النخبوي
        </h2>
    </div>
    
    <div class="elite-stats-grid">
        <div class="elite-stat-card">
            <i class="fas fa-file-invoice"></i>
            <div class="elite-stat-number">{stats['total_invoices']}</div>
            <p>فواتيرك</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-dollar-sign"></i>
            <div class="elite-stat-number">${stats['total_revenue']:,.0f}</div>
            <p>إيراداتك</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-clock"></i>
            <div class="elite-stat-number">{stats['pending_invoices']}</div>
            <p>معلقة</p>
        </div>
        <div class="elite-stat-card">
            <i class="fas fa-crown"></i>
            <div class="elite-stat-number">{session.get('subscription_tier', 'basic').title()}</div>
            <p>مستواك</p>
        </div>
    </div>
    
    <div class="elite-profile-section">
        <h3 style="margin-bottom: 25px; color: var(--pure-white);">
            <i class="fas fa-id-card"></i> المعلومات الشخصية
        </h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
            <div style="color: var(--smoke-white);">
                <p style="margin-bottom: 15px;"><strong>اسم المستخدم:</strong> {session['username']}</p>
                <p style="margin-bottom: 15px;"><strong>البريد الإلكتروني:</strong> {session['email']}</p>
                <p style="margin-bottom: 15px;"><strong>الاسم الكامل:</strong> {session['full_name']}</p>
                <p style="margin-bottom: 15px;"><strong>الشركة:</strong> {session.get('company_name', 'غير محدد')}</p>
            </div>
            <div style="color: var(--smoke-white);">
                <p style="margin-bottom: 15px;"><strong>نوع الحساب:</strong> {session['user_type']}</p>
                <p style="margin-bottom: 15px;"><strong>مستوى الاشتراك:</strong> {session.get('subscription_tier', 'basic').title()}</p>
                <p style="margin-bottom: 15px;"><strong>حالة الحساب:</strong> <span style="color: var(--accent-green);">نشط</span></p>
                <p style="margin-bottom: 15px;"><strong>تاريخ الانضمام:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(BLACK_ELITE_DESIGN, title="الملف الشخصي - InvoiceFlow Elite", uptime=uptime_str, content=content, is_login_page=False)

# إضافة الروابط الأساسية
@app.route('/elite/invoices')
def elite_invoices():
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
        <p style="text-align: center; color: var(--smoke-white); opacity: 0.8;">قريباً... سيتم إضافة نظام الفواتير المتكامل</p>
    </div>
    """
    return render_template_string(BLACK_ELITE_DESIGN, title="الفواتير - InvoiceFlow Elite", uptime=uptime_str, content=content, is_login_page=False)

@app.route('/elite/create')
def elite_create_invoice():
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
        <p style="text-align: center; color: var(--smoke-white); opacity: 0.8;">قريباً... سيتم إضافة نظام إنشاء الفواتير المتكامل</p>
    </div>
    """
    return render_template_string(BLACK_ELITE_DESIGN, title="إنشاء فاتورة - InvoiceFlow Elite", uptime=uptime_str, content=content, is_login_page=False)

@app.route('/elite/admin')
def elite_admin():
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
        <p style="text-align: center; color: var(--smoke-white); opacity: 0.8;">قريباً... سيتم إضافة لوحة التحكم المتكاملة</p>
    </div>
    """
    return render_template_string(BLACK_ELITE_DESIGN, title="لوحة التحكم - InvoiceFlow Elite", uptime=uptime_str, content=content, is_login_page=False)

@app.route('/elite/ai')
def elite_ai_insights():
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
        <p style="text-align: center; color: var(--smoke-white); opacity: 0.8;">قريباً... سيتم إضافة نظام الذكاء الاصطناعي المتكامل</p>
    </div>
    """
    return render_template_string(BLACK_ELITE_DESIGN, title="الذكاء الاصطناعي - InvoiceFlow Elite", uptime=uptime_str, content=content, is_login_page=False)

# ================== التشغيل الرئيسي للنخبة ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام النخبوي الأسود...")
        print(f"🌐 الخادم النخبوي يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام النخبوي الأسود جاهز لاستقبال الطلبات!")
        print("🎨 التصميم الأسود الفاخر مفعل!")
        print("👑 فريق النخبة البروفيسوري في الخدمة!")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل النخبوي: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
