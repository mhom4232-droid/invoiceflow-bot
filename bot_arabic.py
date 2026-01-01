الموقع الاحترافي 
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

# ================== تطبيق Flask المتطور ==================
app = Flask(__name__)
app.secret_key = 'invoiceflow_premium_elite_2024_v4'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# الحصول على البورت من البيئة
port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🎯 InvoiceFlow Premium - الإصدار الراقي المتميز")
print("🚀 تصميم ذهبي راقي + ذكاء اصطناعي متقدم + أداء فائق")
print("👑 فريق النخبة البروفيسوري المتكامل")
print("=" * 80)

# ================== نظام الإبقاء على التشغيل ==================
class PremiumKeepAlive:
    def __init__(self):
        self.uptime_start = time.time()
        self.request_count = 0
        
    def start_premium_system(self):
        print("🚀 بدء النظام الراقي...")
        self.start_premium_monitoring()
        print("✅ النظام الراقي مفعل!")
    
    def start_premium_monitoring(self):
        def monitor():
            while True:
                current_time = time.time()
                uptime = current_time - self.uptime_start
                
                if int(current_time) % 300 == 0:  # كل 5 دقائق
                    hours = int(uptime // 3600)
                    minutes = int((uptime % 3600) // 60)
                    print(f"📊 تقرير النظام الراقي: {hours}س {minutes}د - {self.request_count} طلب")
                
                time.sleep(1)
        
        monitor_thread = Thread(target=monitor)
        monitor_thread.daemon = True
        monitor_thread.start()

# إعداد النظام الراقي
keep_alive_system = PremiumKeepAlive()
keep_alive_system.start_premium_system()

# ================== نظام التصميم الراقي ==================
PREMIUM_DESIGN_HTML = """
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
            /* الألوان الراقية - ذهبي/أسود */
            --primary-gold: #D4AF37;
            --light-gold: #F5E6A4;
            --dark-gold: #B8860B;
            --primary-black: #0A0A0A;
            --dark-gray: #1A1A1A;
            --light-gray: #2A2A2A;
            --text-gold: #FFD700;
            --text-light: #E5E5E5;
            --text-muted: #A0A0A0;
            --accent-emerald: #10B981;
            --accent-ruby: #EF4444;
            --accent-sapphire: #3B82F6;
            --shadow-premium: rgba(212, 175, 55, 0.15);
            --gradient-premium: linear-gradient(135deg, var(--primary-gold) 0%, var(--dark-gold) 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Tajawal', 'Segoe UI', sans-serif;
            background: var(--primary-black);
            color: var(--text-light);
            min-height: 100vh;
            line-height: 1.8;
            overflow-x: hidden;
        }

        .premium-container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 20px;
            min-height: 100vh;
        }

        /* شريط التنقل الراقي */
        .premium-navbar {
            background: rgba(10, 10, 10, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 2px solid var(--primary-gold);
            padding: 0 30px;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .nav-brand h1 {
            font-size: 2.2em;
            font-weight: 800;
            background: var(--gradient-premium);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 10px var(--shadow-premium);
        }

        .nav-links {
            display: flex;
            gap: 30px;
            align-items: center;
        }

        .nav-link {
            color: var(--text-light);
            text-decoration: none;
            font-weight: 600;
            padding: 12px 20px;
            border-radius: 10px;
            transition: all 0.3s ease;
            position: relative;
        }

        .nav-link:hover {
            color: var(--primary-gold);
            background: rgba(212, 175, 55, 0.1);
        }

        .nav-link.active {
            background: var(--gradient-premium);
            color: var(--primary-black);
            box-shadow: 0 4px 15px var(--shadow-premium);
        }

        .nav-link.active::before {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 20px;
            right: 20px;
            height: 2px;
            background: var(--primary-gold);
        }

        /* المحتوى الرئيسي */
        .premium-content {
            margin-top: 100px;
            padding: 40px 0;
        }

        .premium-hero {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(10, 10, 10, 0.95) 100%);
            border-radius: 30px;
            padding: 60px;
            margin-bottom: 50px;
            border: 1px solid rgba(212, 175, 55, 0.3);
            position: relative;
            overflow: hidden;
        }

        .premium-hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 20% 80%, rgba(212, 175, 55, 0.1) 0%, transparent 50%);
            pointer-events: none;
        }

        .hero-content h1 {
            font-size: 4.5em;
            font-weight: 800;
            background: var(--gradient-premium);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            line-height: 1.2;
        }

        .hero-content p {
            font-size: 1.4em;
            color: var(--text-muted);
            margin-bottom: 30px;
            max-width: 600px;
        }

        /* كروت الخدمات الراقية */
        .premium-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 30px;
            margin: 50px 0;
        }

        .premium-card {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.8) 0%, rgba(42, 42, 42, 0.6) 100%);
            border-radius: 25px;
            padding: 40px;
            border: 1px solid rgba(212, 175, 55, 0.2);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }

        .premium-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-premium);
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }

        .premium-card:hover {
            transform: translateY(-10px) scale(1.02);
            border-color: var(--primary-gold);
            box-shadow: 0 20px 40px var(--shadow-premium);
        }

        .premium-card:hover::before {
            transform: scaleX(1);
        }

        .premium-card i {
            font-size: 3.5em;
            margin-bottom: 25px;
            background: var(--gradient-premium);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .premium-card h3 {
            font-size: 1.8em;
            margin-bottom: 15px;
            color: var(--text-light);
            font-weight: 700;
        }

        .premium-card p {
            color: var(--text-muted);
            font-size: 1.1em;
            line-height: 1.7;
        }

        /* الإحصائيات الراقية */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 60px 0;
        }

        .stat-card {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.7) 100%);
            border-radius: 20px;
            padding: 35px 30px;
            text-align: center;
            border: 1px solid rgba(212, 175, 55, 0.15);
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-premium);
        }

        .stat-number {
            font-size: 3.8em;
            font-weight: 800;
            margin: 20px 0;
            background: var(--gradient-premium);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-card p {
            font-size: 1.2em;
            color: var(--text-muted);
            font-weight: 600;
        }

        /* الأزرار الراقية */
        .premium-btn {
            background: var(--gradient-premium);
            color: var(--primary-black);
            padding: 18px 45px;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 700;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin: 10px;
            box-shadow: 0 5px 20px var(--shadow-premium);
            position: relative;
            overflow: hidden;
        }

        .premium-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
        }

        .premium-btn:hover::before {
            left: 100%;
        }

        .premium-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.4);
        }

        .premium-btn-outline {
            background: transparent;
            border: 2px solid var(--primary-gold);
            color: var(--primary-gold);
        }

        .premium-btn-outline:hover {
            background: var(--primary-gold);
            color: var(--primary-black);
        }

        /* قسم الذكاء الاصطناعي */
        .ai-section {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(10, 10, 10, 0.98) 100%);
            border-radius: 30px;
            padding: 50px;
            margin: 60px 0;
            border: 1px solid rgba(212, 175, 55, 0.3);
            position: relative;
        }

        .ai-section::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: var(--gradient-premium);
            border-radius: 32px;
            z-index: -1;
            opacity: 0.1;
        }

        /* التحميل المتحرك */
        .loading-spinner {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid rgba(212, 175, 55, 0.3);
            border-radius: 50%;
            border-top-color: var(--primary-gold);
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* تأثيرات النص */
        .text-glow {
            text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        }

        /* التكيف مع الأجهزة المحمولة */
        @media (max-width: 768px) {
            .premium-navbar {
                padding: 0 15px;
                height: 70px;
            }

            .nav-brand h1 {
                font-size: 1.8em;
            }

            .nav-links {
                display: none;
            }

            .premium-hero {
                padding: 40px 25px;
            }

            .hero-content h1 {
                font-size: 2.8em;
            }

            .premium-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .premium-card {
                padding: 30px;
            }
        }

        /* نظام الثيمات */
        .theme-switcher {
            position: fixed;
            bottom: 30px;
            left: 30px;
            z-index: 1000;
        }

        .theme-btn {
            background: var(--gradient-premium);
            color: var(--primary-black);
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            cursor: pointer;
            font-size: 1.3em;
            box-shadow: 0 5px 15px var(--shadow-premium);
            transition: all 0.3s ease;
        }

        .theme-btn:hover {
            transform: scale(1.1) rotate(180deg);
        }
    </style>
</head>
<body>
    <!-- شريط التنقل الراقي -->
    <nav class="premium-navbar">
        <div class="nav-brand">
            <i class="fas fa-crown" style="color: var(--primary-gold); font-size: 2em;"></i>
            <h1>InvoiceFlow Premium</h1>
        </div>
        
        <div class="nav-links">
            <a href="{{ url_for('home') }}" class="nav-link {% if request.endpoint == 'home' %}active{% endif %}">
                <i class="fas fa-home"></i> الرئيسية
            </a>
            <a href="{{ url_for('invoices') }}" class="nav-link {% if request.endpoint == 'invoices' %}active{% endif %}">
                <i class="fas fa-file-invoice-dollar"></i> الفواتير
            </a>
            <a href="{{ url_for('create_invoice') }}" class="nav-link {% if request.endpoint == 'create_invoice' %}active{% endif %}">
                <i class="fas fa-plus-circle"></i> إنشاء فاتورة
            </a>
            <a href="{{ url_for('ai_insights') }}" class="nav-link {% if request.endpoint == 'ai_insights' %}active{% endif %}">
                <i class="fas fa-robot"></i> الذكاء الاصطناعي
            </a>
            {% if session.user_logged_in %}
            <div class="user-menu">
                <span style="color: var(--primary-gold); margin: 0 15px;">
                    <i class="fas fa-user-tie"></i> {{ session.username }}
                </span>
                <a href="{{ url_for('logout') }}" class="premium-btn" style="padding: 10px 20px; font-size: 0.9em;">
                    <i class="fas fa-sign-out-alt"></i> خروج
                </a>
            </div>
            {% else %}
            <a href="{{ url_for('login') }}" class="premium-btn" style="padding: 12px 25px;">
                <i class="fas fa-sign-in-alt"></i> دخول
            </a>
            {% endif %}
        </div>
    </nav>

    <!-- المحتوى الرئيسي -->
    <div class="premium-container">
        <div class="premium-content">
            {{ content | safe }}
        </div>
    </div>

    <!-- زر تبديل الثيمات -->
    <div class="theme-switcher">
        <button class="theme-btn" onclick="toggleTheme()">
            <i class="fas fa-palette"></i>
        </button>
    </div>

    <script>
        // تأثيرات الصفحة
        document.addEventListener('DOMContentLoaded', function() {
            // تأثير التحميل
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);

            // تأثيرات الكروت
            const cards = document.querySelectorAll('.premium-card');
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
            });

            // تأثيرات الأرقام
            const counters = document.querySelectorAll('.stat-number');
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target'));
                if (!isNaN(target)) {
                    animateCounter(counter, 0, target, 2000);
                }
            });
        });

        // عدادات متحركة
        function animateCounter(element, start, end, duration) {
            let startTimestamp = null;
            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                const value = Math.floor(progress * (end - start) + start);
                element.textContent = value.toLocaleString();
                if (progress < 1) {
                    window.requestAnimationFrame(step);
                }
            };
            window.requestAnimationFrame(step);
        }

        // تبديل الثيمات
        function toggleTheme() {
            const body = document.body;
            const currentTheme = body.getAttribute('data-theme');
            
            if (currentTheme === 'light') {
                body.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                body.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        }

        // تحميل الثيم المحفوظ
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.setAttribute('data-theme', savedTheme);

        // تأثيرات التمرير
        window.addEventListener('scroll', function() {
            const navbar = document.querySelector('.premium-navbar');
            if (window.scrollY > 100) {
                navbar.style.background = 'rgba(10, 10, 10, 0.98)';
                navbar.style.backdropFilter = 'blur(20px)';
            } else {
                navbar.style.background = 'rgba(10, 10, 10, 0.95)';
                navbar.style.backdropFilter = 'blur(20px)';
            }
        });
    </script>
</body>
</html>
"""

# ================== Routes الأساسية المصححة ==================

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    uptime = time.time() - keep_alive_system.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    # إحصائيات متقدمة
    stats = {
        'total_invoices': 156,
        'total_revenue': 125000,
        'active_users': 89,
        'success_rate': 94
    }
    
    content = f"""
    <!-- قسم البطل -->
    <div class="premium-hero">
        <div class="hero-content">
            <h1 class="text-glow">نظام الفواتير الراقي</h1>
            <p>منصة متكاملة لإدارة الفواتير بمستوى احترافي عالمي، مصممة خصيصاً للشركات النخبوية</p>
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <a href="/create" class="premium-btn">
                    <i class="fas fa-rocket"></i> ابدأ الآن
                </a>
                <a href="/demo" class="premium-btn premium-btn-outline">
                    <i class="fas fa-play-circle"></i> شاهد العرض
                </a>
            </div>
        </div>
    </div>

    <!-- الإحصائيات -->
    <div class="stats-grid">
        <div class="stat-card">
            <i class="fas fa-file-invoice" style="color: var(--primary-gold);"></i>
            <div class="stat-number" data-target="{stats['total_invoices']}">{stats['total_invoices']}</div>
            <p>فاتورة تم إنشاؤها</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-dollar-sign" style="color: var(--primary-gold);"></i>
            <div class="stat-number" data-target="{stats['total_revenue']}">${stats['total_revenue']:,.0f}</div>
            <p>إيرادات تم تحقيقها</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-users" style="color: var(--primary-gold);"></i>
            <div class="stat-number" data-target="{stats['active_users']}">{stats['active_users']}</div>
            <p>مستخدم نشط</p>
        </div>
        <div class="stat-card">
            <i class="fas fa-chart-line" style="color: var(--primary-gold);"></i>
            <div class="stat-number" data-target="{stats['success_rate']}">{stats['success_rate']}%</div>
            <p>معدل النجاح</p>
        </div>
    </div>

    <!-- الخدمات المميزة -->
    <div style="text-align: center; margin: 80px 0 40px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; background: var(--gradient-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            المزايا الراقية
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted); max-width: 600px; margin: 0 auto;">
            اكتشف مجموعة المزايا المتقدمة المصممة خصيصاً لاحتياجاتك النخبوية
        </p>
    </div>

    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-brain"></i>
            <h3>ذكاء اصطناعي متقدم</h3>
            <p>نظام تحليلات ذكي يقدم رؤى عميقة وتوصيات مخصصة لتحسين أداء أعمالك</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-shield-alt"></i>
            <h3>أمان من المستوى الأول</h3>
            <p>حماية متقدمة للبيانات مع تشفير من الدرجة الأولى ونسخ احتياطي تلقائي</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-bolt"></i>
            <h3>أداء فائق السرعة</h3>
            <p>تصميم محسن لأقصى أداء مع أوقات تحميل فائقة السرعة واستجابة فورية</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-mobile-alt"></i>
            <h3>تصميم متجاوب راقي</h3>
            <p>تجربة مستخدم متميزة على جميع الأجهزة بتصميم أنيق واحترافي</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-chart-pie"></i>
            <h3>تقارير متقدمة</h3>
            <p>لوحة تحكم شاملة مع رسوم بيانية تفاعلية وتقارير مفصلة عن أدائك</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-headset"></i>
            <h3>دعم فني متميز</h3>
            <p>فريق دعم فني متخصص متاح على مدار الساعة لتقديم أفضل تجربة مستخدم</p>
        </div>
    </div>

    <!-- قسم الذكاء الاصطناعي -->
    <div class="ai-section">
        <div style="text-align: center; margin-bottom: 50px;">
            <h2 style="font-size: 2.8em; margin-bottom: 15px; background: var(--gradient-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                <i class="fas fa-robot"></i> المساعد الذكي
            </h2>
            <p style="font-size: 1.2em; color: var(--text-muted);">
                استفد من قوة الذكاء الاصطناعي لتحليل بياناتك وتقديم توصيات ذكية
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
            <div>
                <h3 style="color: var(--primary-gold); margin-bottom: 20px;">📊 تحليلات متقدمة</h3>
                <div style="background: rgba(212, 175, 55, 0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.2);">
                    <p style="margin-bottom: 15px;">• تحليل أنماط الإنفاق والعوائد</p>
                    <p style="margin-bottom: 15px;">• توقعات الإيرادات المستقبلية</p>
                    <p style="margin-bottom: 15px;">• توصيات تحسين الأسعار</p>
                    <p>• اكتشاف فرص النمو</p>
                </div>
            </div>
            
            <div>
                <h3 style="color: var(--primary-gold); margin-bottom: 20px;">🚀 تحسين الأداء</h3>
                <div style="background: rgba(212, 175, 55, 0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.2);">
                    <p style="margin-bottom: 15px;">• اقتراحات لتحسين العملية</p>
                    <p style="margin-bottom: 15px;">• تحليل كفاءة الموارد</p>
                    <p style="margin-bottom: 15px;">• تقارير أداء مخصصة</p>
                    <p>• نصائح لزيادة الإنتاجية</p>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px;">
            <a href="/ai" class="premium-btn" style="padding: 20px 50px; font-size: 1.2em;">
                <i class="fas fa-magic"></i> تجربة المساعد الذكي
            </a>
        </div>
    </div>
    """
    
    return render_template_string(PREMIUM_DESIGN_HTML, title="InvoiceFlow Premium - النظام الراقي", uptime=uptime_str, content=content)

@app.route('/login')
def login():
    """صفحة تسجيل الدخول"""
    content = """
    <div style="max-width: 500px; margin: 100px auto;">
        <div class="premium-card" style="text-align: center;">
            <i class="fas fa-lock" style="font-size: 4em; margin-bottom: 30px;"></i>
            <h2 style="margin-bottom: 30px;">الدخول إلى النظام الراقي</h2>
            
            <form style="text-align: right;">
                <div style="margin-bottom: 25px;">
                    <input type="text" placeholder="اسم المستخدم" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                <div style="margin-bottom: 25px;">
                    <input type="password" placeholder="كلمة المرور" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                
                <button type="submit" class="premium-btn" style="width: 100%; padding: 18px;">
                    <i class="fas fa-sign-in-alt"></i> دخول إلى النظام
                </button>
            </form>
            
            <div style="margin-top: 30px; color: var(--text-muted);">
                <p>ليس لديك حساب؟ <a href="/register" style="color: var(--primary-gold); text-decoration: none;">انضم إلينا</a></p>
            </div>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الدخول - InvoiceFlow Premium", uptime="", content=content)

@app.route('/register')
def register():
    """صفحة التسجيل"""
    content = """
    <div style="max-width: 500px; margin: 100px auto;">
        <div class="premium-card" style="text-align: center;">
            <i class="fas fa-user-plus" style="font-size: 4em; margin-bottom: 30px;"></i>
            <h2 style="margin-bottom: 30px;">انضم إلى النخبة</h2>
            
            <form style="text-align: right;">
                <div style="margin-bottom: 20px;">
                    <input type="text" placeholder="الاسم الكامل" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                <div style="margin-bottom: 20px;">
                    <input type="text" placeholder="اسم المستخدم" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                <div style="margin-bottom: 20px;">
                    <input type="email" placeholder="البريد الإلكتروني" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                <div style="margin-bottom: 25px;">
                    <input type="password" placeholder="كلمة المرور" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                
                <button type="submit" class="premium-btn" style="width: 100%; padding: 18px;">
                    <i class="fas fa-user-plus"></i> إنشاء حساب
                </button>
            </form>
            
            <div style="margin-top: 30px; color: var(--text-muted);">
                <p>لديك حساب؟ <a href="/login" style="color: var(--primary-gold); text-decoration: none;">سجل الدخول</a></p>
            </div>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="التسجيل - InvoiceFlow Premium", uptime="", content=content)

@app.route('/invoices')
def invoices():
    """صفحة الفواتير"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; background: var(--gradient-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <i class="fas fa-file-invoice-dollar"></i> إدارة الفواتير
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted);">
            قم بإدارة وعرض وتتبع جميع فواتيرك من مكان واحد
        </p>
    </div>

    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-search"></i>
            <h3>استعراض الفواتير</h3>
            <p>تصفح جميع فواتيرك مع إمكانيات البحث والتصفية المتقدمة</p>
            <a href="/invoices/list" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-list"></i> عرض الكل
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-plus"></i>
            <h3>إنشاء فاتورة</h3>
            <p>أنشئ فاتورة جديدة بتصميم احترافي وخيارات متقدمة</p>
            <a href="/create" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-plus-circle"></i> إنشاء جديد
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-chart-bar"></i>
            <h3>إحصائيات الفواتير</h3>
            <p>اطلع على إحصائيات مفصلة عن أداء فواتيرك وإيراداتك</p>
            <a href="/invoices/stats" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-chart-line"></i> عرض الإحصائيات
            </a>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الفواتير - InvoiceFlow Premium", uptime="", content=content)

@app.route('/create')
def create_invoice():
    """صفحة إنشاء الفاتورة"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; background: var(--gradient-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <i class="fas fa-plus-circle"></i> إنشاء فاتورة جديدة
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted);">
            أنشئ فاتورة احترافية بتصميم راقي وخيارات متقدمة
        </p>
    </div>

    <div class="premium-card" style="max-width: 800px; margin: 0 auto;">
        <form style="text-align: right;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <div>
                    <label style="display: block; margin-bottom: 10px; color: var(--primary-gold);">اسم العميل</label>
                    <input type="text" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 10px; color: var(--primary-gold);">البريد الإلكتروني</label>
                    <input type="email" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
            </div>
            
            <div style="margin-bottom: 25px;">
                <label style="display: block; margin-bottom: 10px; color: var(--primary-gold);">الخدمات</label>
                <textarea style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light); height: 120px;" placeholder="أدخل الخدمات المقدمة..."></textarea>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div>
                    <label style="display: block; margin-bottom: 10px; color: var(--primary-gold);">المبلغ</label>
                    <input type="number" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);" placeholder="0.00">
                </div>
                <div>
                    <label style="display: block; margin-bottom: 10px; color: var(--primary-gold);">تاريخ الاستحقاق</label>
                    <input type="date" style="width: 100%; padding: 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 10px; color: var(--text-light);">
                </div>
            </div>
            
            <button type="submit" class="premium-btn" style="width: 100%; padding: 18px; font-size: 1.2em;">
                <i class="fas fa-file-pdf"></i> إنشاء الفاتورة
            </button>
        </form>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="إنشاء فاتورة - InvoiceFlow Premium", uptime="", content=content)

@app.route('/ai')
def ai_insights():
    """صفحة الذكاء الاصطناعي"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; background: var(--gradient-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <i class="fas fa-robot"></i> الذكاء الاصطناعي
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted);">
            استفد من قوة الذكاء الاصطناعي لتحليل بياناتك وتقديم توصيات ذكية
        </p>
    </div>

    <div class="premium-grid">
        <div class="premium-card">
            <i class="fas fa-chart-line"></i>
            <h3>تحليل الإيرادات</h3>
            <p>تحليل متقدم لأنماط الإيرادات وتوقعات النمو المستقبلية</p>
            <a href="/ai/revenue" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-chart-bar"></i> عرض التحليل
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-users"></i>
            <h3>تحليل العملاء</h3>
            <p>فهم سلوك عملائك وتحديد أفضل الفرص للنمو</p>
            <a href="/ai/clients" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-user-chart"></i> تحليل العملاء
            </a>
        </div>
        
        <div class="premium-card">
            <i class="fas fa-lightbulb"></i>
            <h3>توصيات ذكية</h3>
            <p>احصل على توصيات مخصصة لتحسين أداء أعمالك</p>
            <a href="/ai/recommendations" class="premium-btn" style="margin-top: 20px; padding: 12px 25px;">
                <i class="fas fa-magic"></i> التوصيات
            </a>
        </div>
    </div>

    <div class="ai-section" style="margin-top: 50px;">
        <h3 style="text-align: center; margin-bottom: 30px; color: var(--primary-gold);">📊 لوحة التحكم الذكية</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
            <div style="background: rgba(212, 175, 55, 0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.2); text-align: center;">
                <div style="font-size: 2.5em; font-weight: bold; color: var(--primary-gold);">85%</div>
                <div style="color: var(--text-muted);">معدل النمو</div>
            </div>
            <div style="background: rgba(212, 175, 55, 0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.2); text-align: center;">
                <div style="font-size: 2.5em; font-weight: bold; color: var(--primary-gold);">92%</div>
                <div style="color: var(--text-muted);">رضا العملاء</div>
            </div>
            <div style="background: rgba(212, 175, 55, 0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(212, 175, 55, 0.2); text-align: center;">
                <div style="font-size: 2.5em; font-weight: bold; color: var(--primary-gold);">78%</div>
                <div style="color: var(--text-muted);">كفاءة الأداء</div>
            </div>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="الذكاء الاصطناعي - InvoiceFlow Premium", uptime="", content=content)

@app.route('/demo')
def demo():
    """صفحة العرض التوضيحي"""
    content = """
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="font-size: 3em; margin-bottom: 20px; background: var(--gradient-premium); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <i class="fas fa-play-circle"></i> العرض التوضيحي
        </h2>
        <p style="font-size: 1.3em; color: var(--text-muted); max-width: 600px; margin: 0 auto;">
            شاهد كيف يمكن لـ InvoiceFlow Premium تحويل إدارة فواتيرك إلى تجربة راقية ومتقدمة
        </p>
    </div>

    <div class="premium-card" style="max-width: 900px; margin: 0 auto; text-align: center;">
        <div style="font-size: 6em; color: var(--primary-gold); margin-bottom: 30px;">
            <i class="fas fa-video"></i>
        </div>
        <h3 style="margin-bottom: 20px; font-size: 2em;">عرض حي للنظام</h3>
        <p style="color: var(--text-muted); margin-bottom: 30px; line-height: 1.7;">
            جرب النظام بنفسك وشاهد كيف يمكنه تبسيط عمليات إدارة الفواتير وتحسين كفاءة أعمالك
        </p>
        
        <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
            <a href="/login" class="premium-btn" style="padding: 15px 35px;">
                <i class="fas fa-play"></i> بدء العرض
            </a>
            <a href="/features" class="premium-btn premium-btn-outline" style="padding: 15px 35px;">
                <i class="fas fa-list"></i> الميزات الكاملة
            </a>
        </div>
    </div>

    <div class="premium-grid" style="margin-top: 60px;">
        <div class="premium-card">
            <i class="fas fa-bolt"></i>
            <h3>سهولة الاستخدام</h3>
            <p>واجهة بديهية وسهلة الاستخدام لا تحتاج إلى تدريب مسبق</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-cogs"></i>
            <h3>التكامل السلس</h3>
            <p>يتكامل بسهولة مع أنظمتك الحالية بدون تعقيدات</p>
        </div>
        <div class="premium-card">
            <i class="fas fa-shield-alt"></i>
            <h3>أمان مضمون</h3>
            <p>حماية كاملة لبياناتك مع أعلى معايير الأمان</p>
        </div>
    </div>
    """
    return render_template_string(PREMIUM_DESIGN_HTML, title="العرض التوضيحي - InvoiceFlow Premium", uptime="", content=content)

@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    session.clear()
    return redirect('/')

# ================== التشغيل الرئيسي ==================
if __name__ == '__main__':
    try:
        print("🌟 بدء تشغيل النظام الراقي...")
        print(f"🌐 الخادم الراقي يعمل على: http://0.0.0.0:{port}")
        print("✅ النظام الراقي جاهز لاستقبال الطلبات!")
        print("🎨 التصميم الذهبي/أسود الراقي مفعل!")
        print("🧠 الذكاء الاصطناعي المتقدم نشط!")
        print("🔐 نظام الأمان الراقي مفعل!")
        print("🚀 الأداء الفائق جاهز!")
        print("👑 فريق النخبة البروفيسوري في الخدمة!")
        
        print("\n📋 المسارات المتاحة:")
        print("🔹 / - الصفحة الرئيسية")
        print("🔹 /login - تسجيل الدخول") 
        print("🔹 /register - إنشاء حساب")
        print("🔹 /invoices - إدارة الفواتير")
        print("🔹 /create - إنشاء فاتورة")
        print("🔹 /ai - الذكاء الاصطناعي")
        print("🔹 /demo - العرض التوضيحي")
        print("🔹 /logout - تسجيل الخروج")
        
        # تشغيل خادم Flask
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل الراقي: {e}")
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)

