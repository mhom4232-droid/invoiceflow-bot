import os
import sqlite3
import json
import time
import hashlib
import secrets
import re
import io
import base64
import random
import uuid
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from threading import Thread, Lock
from functools import wraps
from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from reportlab.lib.units import inch, mm
import qrcode
from PIL import Image as PILImage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import warnings
warnings.filterwarnings('ignore')

# ================== تهيئة التطبيق ==================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'invoiceflow_pro_secure_key_2024_v2')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['DATABASE_PATH'] = 'database/invoiceflow_pro.db'
app.config['LANGUAGES'] = {'ar': 'العربية', 'en': 'English'}
app.config['SUPPORTED_CURRENCIES'] = {
    'USD': '$', 'SAR': 'ر.س', 'AED': 'د.إ', 'EUR': '€', 'GBP': '£'
}

# إعدادات الأمان
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# إنشاء المجلدات
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)
os.makedirs('static/invoices', exist_ok=True)
os.makedirs('static/qrcodes', exist_ok=True)
os.makedirs('static/logos', exist_ok=True)
os.makedirs('static/fonts', exist_ok=True)

port = int(os.environ.get("PORT", 10000))

print("=" * 80)
print("🚀 InvoiceFlow Pro - النظام الاحترافي المتكامل")
print("🎨 نظام متعدد اللغات • ذكاء اصطناعي متطور • فواتير PDF احترافية")
print("👑 فريق العمل المحترف - النسخة المتطورة")
print("=" * 80)

# ================== نظام اللغات المتعددة ==================
class MultiLanguage:
    def __init__(self):
        self.translations = {
            'ar': {
                'dashboard': 'لوحة التحكم',
                'invoices': 'الفواتير',
                'clients': 'العملاء',
                'products': 'المنتجات',
                'reports': 'التقارير',
                'ai_insights': 'الذكاء الاصطناعي',
                'profile': 'الملف الشخصي',
                'settings': 'الإعدادات',
                'logout': 'تسجيل الخروج',
                'welcome': 'مرحباً',
                'total_invoices': 'إجمالي الفواتير',
                'total_revenue': 'إجمالي الإيرادات',
                'pending_invoices': 'فواتير معلقة',
                'total_clients': 'إجمالي العملاء',
                'create_invoice': 'إنشاء فاتورة',
                'view_all': 'عرض الكل',
                'recent_invoices': 'الفواتير الأخيرة',
                'quick_actions': 'إجراءات سريعة',
                'performance_summary': 'ملخص الأداء',
                'recent_activity': 'نشاطات حديثة',
                'paid': 'مدفوعة',
                'pending': 'معلقة',
                'overdue': 'متأخرة',
                'cancelled': 'ملغاة',
                'view': 'عرض',
                'download': 'تحميل',
                'edit': 'تعديل',
                'delete': 'حذف',
                'save': 'حفظ',
                'cancel': 'إلغاء',
                'search': 'بحث',
                'filter': 'تصفية',
                'export': 'تصدير',
                'import': 'استيراد',
                'print': 'طباعة',
                'send': 'إرسال',
                'status': 'الحالة',
                'amount': 'المبلغ',
                'date': 'التاريخ',
                'actions': 'الإجراءات',
                'client': 'العميل',
                'invoice_number': 'رقم الفاتورة',
                'issue_date': 'تاريخ الإصدار',
                'due_date': 'تاريخ الاستحقاق',
                'payment_method': 'طريقة الدفع',
                'notes': 'ملاحظات',
                'subtotal': 'المجموع الفرعي',
                'tax': 'الضريبة',
                'discount': 'الخصم',
                'total': 'الإجمالي',
                'item': 'العنصر',
                'quantity': 'الكمية',
                'price': 'السعر',
                'unit': 'الوحدة',
                'description': 'الوصف',
                'category': 'الفئة',
                'active': 'نشط',
                'inactive': 'غير نشط',
                'company': 'الشركة',
                'phone': 'الهاتف',
                'email': 'البريد الإلكتروني',
                'address': 'العنوان',
                'website': 'الموقع الإلكتروني',
                'tax_number': 'الرقم الضريبي',
                'created_at': 'تاريخ الإنشاء',
                'last_login': 'آخر دخول',
                'language': 'اللغة',
                'currency': 'العملة',
                'timezone': 'المنطقة الزمنية',
                'notifications': 'الإشعارات',
                'security': 'الأمان',
                'preferences': 'التفضيلات',
                'help': 'مساعدة',
                'support': 'الدعم الفني',
                'documentation': 'التوثيق',
                'feedback': 'ملاحظات',
                'version': 'الإصدار',
                'copyright': 'حقوق النشر',
                'all_rights_reserved': 'جميع الحقوق محفوظة',
                'login': 'تسجيل الدخول',
                'register': 'إنشاء حساب',
                'username': 'اسم المستخدم',
                'password': 'كلمة المرور',
                'confirm_password': 'تأكيد كلمة المرور',
                'remember_me': 'تذكرني',
                'forgot_password': 'نسيت كلمة المرور؟',
                'dont_have_account': 'ليس لديك حساب؟',
                'already_have_account': 'لديك حساب بالفعل؟',
                'sign_up': 'اشتراك',
                'sign_in': 'دخول',
                'full_name': 'الاسم الكامل',
                'company_name': 'اسم الشركة',
                'phone_number': 'رقم الهاتف',
                'success': 'نجاح',
                'error': 'خطأ',
                'warning': 'تحذير',
                'info': 'معلومات',
                'loading': 'جاري التحميل...',
                'processing': 'جاري المعالجة...',
                'saving': 'جاري الحفظ...',
                'deleting': 'جاري الحذف...',
                'updating': 'جاري التحديث...',
                'sending': 'جاري الإرسال...',
                'please_wait': 'يرجى الانتظار...',
                'operation_successful': 'تمت العملية بنجاح',
                'operation_failed': 'فشلت العملية',
                'data_saved': 'تم حفظ البيانات',
                'data_deleted': 'تم حذف البيانات',
                'data_updated': 'تم تحديث البيانات',
                'invalid_input': 'إدخال غير صحيح',
                'required_field': 'هذا الحقل مطلوب',
                'invalid_email': 'بريد إلكتروني غير صالح',
                'password_too_short': 'كلمة المرور قصيرة جداً',
                'passwords_dont_match': 'كلمات المرور غير متطابقة',
                'user_exists': 'المستخدم موجود بالفعل',
                'user_not_found': 'المستخدم غير موجود',
                'incorrect_password': 'كلمة المرور غير صحيحة',
                'account_locked': 'الحساب مغلق',
                'session_expired': 'انتهت الجلسة',
                'access_denied': 'تم رفض الوصول',
                'permission_denied': 'تم رفض الإذن',
                'not_authorized': 'غير مصرح',
                'maintenance': 'الصيانة',
                'under_maintenance': 'تحت الصيانة',
                'coming_soon': 'قريباً',
                'new': 'جديد',
                'old': 'قديم',
                'today': 'اليوم',
                'yesterday': 'أمس',
                'tomorrow': 'غداً',
                'this_week': 'هذا الأسبوع',
                'this_month': 'هذا الشهر',
                'this_year': 'هذه السنة',
                'last_week': 'الأسبوع الماضي',
                'last_month': 'الشهر الماضي',
                'last_year': 'السنة الماضية',
                'next_week': 'الأسبوع القادم',
                'next_month': 'الشهر القادم',
                'next_year': 'السنة القادمة',
                'january': 'يناير',
                'february': 'فبراير',
                'march': 'مارس',
                'april': 'أبريل',
                'may': 'مايو',
                'june': 'يونيو',
                'july': 'يوليو',
                'august': 'أغسطس',
                'september': 'سبتمبر',
                'october': 'أكتوبر',
                'november': 'نوفمبر',
                'december': 'ديسمبر',
                'sunday': 'الأحد',
                'monday': 'الإثنين',
                'tuesday': 'الثلاثاء',
                'wednesday': 'الأربعاء',
                'thursday': 'الخميس',
                'friday': 'الجمعة',
                'saturday': 'السبت',
                'am': 'ص',
                'pm': 'م',
                'morning': 'صباحاً',
                'afternoon': 'ظهراً',
                'evening': 'مساءً',
                'night': 'ليلاً',
                'seconds': 'ثواني',
                'minutes': 'دقائق',
                'hours': 'ساعات',
                'days': 'أيام',
                'weeks': 'أسابيع',
                'months': 'أشهر',
                'years': 'سنوات',
                'now': 'الآن',
                'soon': 'قريباً',
                'later': 'لاحقاً',
                'never': 'أبداً',
                'always': 'دائماً',
                'sometimes': 'أحياناً',
                'rarely': 'نادراً',
                'often': 'غالباً',
                'very_often': 'كثيراً',
                'almost_never': 'بالكاد',
                'almost_always': 'دائماً تقريباً',
                'yes': 'نعم',
                'no': 'لا',
                'ok': 'موافق',
                'apply': 'تطبيق',
                'reset': 'إعادة تعيين',
                'close': 'إغلاق',
                'back': 'رجوع',
                'next': 'التالي',
                'previous': 'السابق',
                'first': 'الأول',
                'last': 'الأخير',
                'more': 'المزيد',
                'less': 'أقل',
                'all': 'الكل',
                'none': 'لا شيء',
                'some': 'بعض',
                'many': 'كثير',
                'few': 'قليل',
                'several': 'عدة',
                'any': 'أي',
                'each': 'كل',
                'every': 'كل',
                'other': 'آخر',
                'another': 'آخر',
                'same': 'نفس',
                'different': 'مختلف',
                'similar': 'مشابه',
                'opposite': 'معاكس',
                'better': 'أفضل',
                'worse': 'أسوأ',
                'best': 'الأفضل',
                'worst': 'الأسوأ',
                'good': 'جيد',
                'bad': 'سيئ',
                'excellent': 'ممتاز',
                'poor': 'ضعيف',
                'average': 'متوسط',
                'high': 'عالٍ',
                'low': 'منخفض',
                'medium': 'متوسط',
                'large': 'كبير',
                'small': 'صغير',
                'big': 'كبير',
                'tiny': 'صغير جداً',
                'huge': 'ضخم',
                'enormous': 'هائل',
                'giant': 'عملاق',
                'microscopic': 'مجهري',
                'short': 'قصير',
                'long': 'طويل',
                'tall': 'طويل',
                'wide': 'واسع',
                'narrow': 'ضيق',
                'deep': 'عميق',
                'shallow': 'سطحى',
                'heavy': 'ثقيل',
                'light': 'خفيف',
                'strong': 'قوي',
                'weak': 'ضعيف',
                'hard': 'صلب',
                'soft': 'ناعم',
                'smooth': 'ناعم',
                'rough': 'خشن',
                'sharp': 'حاد',
                'dull': 'باهت',
                'bright': 'ساطع',
                'dark': 'مظلم',
                'light': 'فاتح',
                'colorful': 'ملون',
                'colorless': 'عديم اللون',
                'transparent': 'شفاف',
                'opaque': 'معتم',
                'shiny': 'لامع',
                'matte': 'غير لامع',
                'wet': 'رطب',
                'dry': 'جاف',
                'hot': 'ساخن',
                'cold': 'بارد',
                'warm': 'دافئ',
                'cool': 'بارد',
                'freezing': 'تجمد',
                'boiling': 'غليان',
                'clean': 'نظيف',
                'dirty': 'وسخ',
                'tidy': 'مرتب',
                'messy': 'فوضوي',
                'organized': 'منظم',
                'disorganized': 'غير منظم',
                'neat': 'أنيق',
                'sloppy': 'غير أنيق',
                'elegant': 'أنيق',
                'clumsy': 'أخرق',
                'graceful': 'رشيق',
                'awkward': 'غريب',
                'beautiful': 'جميل',
                'ugly': 'قبيح',
                'handsome': 'وسيم',
                'pretty': 'جميل',
                'cute': 'لطيف',
                'attractive': 'جذاب',
                'unattractive': 'غير جذاب',
                'charming': 'ساحر',
                'repulsive': 'منفر',
                'friendly': 'ودود',
                'unfriendly': 'غير ودود',
                'kind': 'لطيف',
                'mean': 'قاسي',
                'nice': 'لطيف',
                'rude': 'وقح',
                'polite': 'مهذب',
                'impolite': 'غير مهذب',
                'respectful': 'محترم',
                'disrespectful': 'غير محترم',
                'honest': 'صادق',
                'dishonest': 'غير صادق',
                'trustworthy': 'جدير بالثقة',
                'untrustworthy': 'غير جدير بالثقة',
                'reliable': 'موثوق',
                'unreliable': 'غير موثوق',
                'responsible': 'مسؤول',
                'irresponsible': 'غير مسؤول',
                'mature': 'ناضج',
                'immature': 'غير ناضج',
                'wise': 'حكيم',
                'foolish': 'أحمق',
                'intelligent': 'ذكي',
                'stupid': 'غبي',
                'smart': 'ذكي',
                'dumb': 'غبي',
                'clever': 'ذكي',
                'naive': 'ساذج',
                'experienced': 'خبير',
                'inexperienced': 'غير خبير',
                'skilled': 'ماهر',
                'unskilled': 'غير ماهر',
                'talented': 'موهوب',
                'untalented': 'غير موهوب',
                'creative': 'خلاق',
                'uncreative': 'غير خلاَّق',
                'innovative': 'مبتكر',
                'traditional': 'تقليدي',
                'modern': 'حديث',
                'ancient': 'قديم',
                'contemporary': 'معاصر',
                'future': 'مستقبلي',
                'past': 'ماضٍ',
                'present': 'حاضر',
                'temporary': 'مؤقت',
                'permanent': 'دائم',
                'eternal': 'أبدي',
                'finite': 'محدود',
                'infinite': 'لا نهائي',
                'limited': 'محدود',
                'unlimited': 'غير محدود',
                'enough': 'كافٍ',
                'insufficient': 'غير كافٍ',
                'adequate': 'مناسب',
                'inadequate': 'غير مناسب',
                'satisfactory': 'مرضٍ',
                'unsatisfactory': 'غير مرضٍ',
                'acceptable': 'مقبول',
                'unacceptable': 'غير مقبول',
                'appropriate': 'ملائم',
                'inappropriate': 'غير ملائم',
                'suitable': 'مناسب',
                'unsuitable': 'غير مناسب',
                'proper': 'صحيح',
                'improper': 'غير صحيح',
                'correct': 'صحيح',
                'incorrect': 'غير صحيح',
                'accurate': 'دقيق',
                'inaccurate': 'غير دقيق',
                'precise': 'دقيق',
                'imprecise': 'غير دقيق',
                'exact': 'بالضبط',
                'approximate': 'تقريبي',
                'right': 'صح',
                'wrong': 'خطأ',
                'true': 'صحيح',
                'false': 'خطأ',
                'real': 'حقيقي',
                'fake': 'مزيف',
                'genuine': 'أصلي',
                'artificial': 'اصطناعي',
                'natural': 'طبيعي',
                'synthetic': 'اصطناعي',
                'organic': 'عضوي',
                'inorganic': 'غير عضوي',
                'healthy': 'صحي',
                'unhealthy': 'غير صحي',
                'fit': 'لائق',
                'unfit': 'غير لائق',
                'sick': 'مريض',
                'well': 'بصحة جيدة',
                'ill': 'مريض',
                'injured': 'مصاب',
                'wounded': 'مجروح',
                'hurt': 'متألم',
                'painful': 'مؤلم',
                'painless': 'غير مؤلم',
                'comfortable': 'مريح',
                'uncomfortable': 'غير مريح',
                'pleasant': 'ممتع',
                'unpleasant': 'غير ممتع',
                'enjoyable': 'ممتع',
                'boring': 'ممل',
                'interesting': 'مثير للاهتمام',
                'uninteresting': 'غير مثير للاهتمام',
                'exciting': 'مثير',
                'calm': 'هادئ',
                'peaceful': 'سلمي',
                'violent': 'عنيف',
                'aggressive': 'عدواني',
                'passive': 'سلبي',
                'active': 'نشط',
                'energetic': 'نشيط',
                'lazy': 'كسول',
                'hardworking': 'مجتهد',
                'diligent': 'مجتهد',
                'careless': 'مهمل',
                'careful': 'حذر',
                'cautious': 'حذر',
                'reckless': 'متهور',
                'brave': 'شجاع',
                'cowardly': 'جبان',
                'fearless': 'عديم الخوف',
                'fearful': 'خائف',
                'confident': 'واثق',
                'insecure': 'غير واثق',
                'optimistic': 'متفائل',
                'pessimistic': 'متشائم',
                'realistic': 'واقعي',
                'idealistic': 'مثالي',
                'practical': 'عملي',
                'impractical': 'غير عملي',
                'logical': 'منطقي',
                'illogical': 'غير منطقي',
                'rational': 'عقلاني',
                'irrational': 'غير عقلاني',
                'sensible': 'معقول',
                'senseless': 'غير معقول',
                'reasonable': 'معقول',
                'unreasonable': 'غير معقول',
                'fair': 'عادل',
                'unfair': 'غير عادل',
                'just': 'عادل',
                'unjust': 'غير عادل',
                'equal': 'متساوي',
                'unequal': 'غير متساوي',
                'balanced': 'متوازن',
                'unbalanced': 'غير متوازن',
                'stable': 'مستقر',
                'unstable': 'غير مستقر',
                'steady': 'ثابت',
                'unsteady': 'غير ثابت',
                'consistent': 'متسق',
                'inconsistent': 'غير متسق',
                'constant': 'ثابت',
                'variable': 'متغير',
                'regular': 'منتظم',
                'irregular': 'غير منتظم',
                'normal': 'طبيعي',
                'abnormal': 'غير طبيعي',
                'usual': 'معتاد',
                'unusual': 'غير معتاد',
                'common': 'شائع',
                'rare': 'نادر',
                'unique': 'فريد',
                'ordinary': 'عادي',
                'extraordinary': 'غير عادي',
                'special': 'خاص',
                'general': 'عام',
                'specific': 'محدد',
                'vague': 'غامض',
                'clear': 'واضح',
                'obvious': 'واضح',
                'hidden': 'مخفي',
                'visible': 'مرئي',
                'invisible': 'غير مرئي',
                'apparent': 'واضح',
                'transparent': 'شفاف',
                'translucent': 'شبه شفاف',
                'opaque': 'معتم',
                'solid': 'صلب',
                'liquid': 'سائل',
                'gas': 'غاز',
                'fluid': 'سائل',
                'rigid': 'صلب',
                'flexible': 'مرن',
                'elastic': 'مرن',
                'plastic': 'بلاستيكي',
                'metal': 'معدن',
                'wood': 'خشب',
                'glass': 'زجاج',
                'paper': 'ورق',
                'fabric': 'قماش',
                'leather': 'جلد',
                'rubber': 'مطاط',
                'ceramic': 'سيراميك',
                'concrete': 'خرسانة',
                'brick': 'طوب',
                'stone': 'حجر',
                'sand': 'رمل',
                'soil': 'تربة',
                'water': 'ماء',
                'air': 'هواء',
                'fire': 'نار',
                'earth': 'أرض',
                'space': 'فضاء',
                'time': 'زمن',
                'energy': 'طاقة',
                'power': 'قوة',
                'force': 'قوة',
                'speed': 'سرعة',
                'velocity': 'سرعة',
                'acceleration': 'تسارع',
                'deceleration': 'تباطؤ',
                'momentum': 'زخم',
                'gravity': 'جاذبية',
                'weight': 'وزن',
                'mass': 'كتلة',
                'volume': 'حجم',
                'density': 'كثافة',
                'pressure': 'ضغط',
                'temperature': 'درجة حرارة',
                'heat': 'حرارة',
                'cold': 'برودة',
                'light': 'ضوء',
                'dark': 'ظلام',
                'sound': 'صوت',
                'noise': 'ضجيج',
                'silence': 'صمت',
                'music': 'موسيقى',
                'song': 'أغنية',
                'voice': 'صوت',
                'word': 'كلمة',
                'sentence': 'جملة',
                'paragraph': 'فقرة',
                'text': 'نص',
                'image': 'صورة',
                'picture': 'صورة',
                'photo': 'صورة',
                'video': 'فيديو',
                'audio': 'صوت',
                'file': 'ملف',
                'document': 'وثيقة',
                'folder': 'مجلد',
                'directory': 'دليل',
                'path': 'مسار',
                'link': 'رابط',
                'url': 'رابط',
                'website': 'موقع ويب',
                'webpage': 'صفحة ويب',
                'browser': 'متصفح',
                'server': 'خادم',
                'client': 'عميل',
                'network': 'شبكة',
                'internet': 'إنترنت',
                'wifi': 'واي فاي',
                'bluetooth': 'بلوتوث',
                'signal': 'إشارة',
                'connection': 'اتصال',
                'disconnection': 'انفصال',
                'online': 'متصل',
                'offline': 'غير متصل',
                'digital': 'رقمي',
                'analog': 'تناظري',
                'electronic': 'إلكتروني',
                'electric': 'كهربائي',
                'mechanical': 'ميكانيكي',
                'manual': 'يدوي',
                'automatic': 'تلقائي',
                'robot': 'روبوت',
                'machine': 'آلة',
                'tool': 'أداة',
                'device': 'جهاز',
                'equipment': 'معدات',
                'instrument': 'أداة',
                'appliance': 'جهاز',
                'gadget': 'أداة',
                'technology': 'تكنولوجيا',
                'science': 'علم',
                'art': 'فن',
                'culture': 'ثقافة',
                'history': 'تاريخ',
                'geography': 'جغرافيا',
                'mathematics': 'رياضيات',
                'physics': 'فيزياء',
                'chemistry': 'كيمياء',
                'biology': 'أحياء',
                'medicine': 'طب',
                'engineering': 'هندسة',
                'architecture': 'عمارة',
                'design': 'تصميم',
                'business': 'أعمال',
                'commerce': 'تجارة',
                'trade': 'تجارة',
                'industry': 'صناعة',
                'manufacturing': 'تصنيع',
                'production': 'إنتاج',
                'consumption': 'استهلاك',
                'distribution': 'توزيع',
                'marketing': 'تسويق',
                'advertising': 'إعلان',
                'sales': 'مبيعات',
                'purchase': 'شراء',
                'sell': 'بيع',
                'buy': 'شراء',
                'price': 'سعر',
                'cost': 'تكلفة',
                'value': 'قيمة',
                'worth': 'قيمة',
                'expensive': 'غالي',
                'cheap': 'رخيص',
                'affordable': 'معقول السعر',
                'free': 'مجاني',
                'paid': 'مدفوع',
                'payment': 'دفع',
                'refund': 'استرداد',
                'discount': 'خصم',
                'offer': 'عرض',
                'deal': 'صفقة',
                'bargain': 'صفقة',
                'auction': 'مزاد',
                'bid': 'مزايدة',
                'profit': 'ربح',
                'loss': 'خسارة',
                'income': 'دخل',
                'expense': 'مصروف',
                'revenue': 'إيراد',
                'budget': 'ميزانية',
                'investment': 'استثمار',
                'savings': 'مدخرات',
                'debt': 'دين',
                'credit': 'ائتمان',
                'loan': 'قرض',
                'interest': 'فائدة',
                'tax': 'ضريبة',
                'salary': 'راتب',
                'wage': 'أجر',
                'income': 'دخل',
                'wealth': 'ثروة',
                'rich': 'غني',
                'poor': 'فقير',
                'wealthy': 'ثري',
                'poverty': 'فقر',
                'money': 'مال',
                'cash': 'نقد',
                'coin': 'عملة معدنية',
                'banknote': 'عملة ورقية',
                'currency': 'عملة',
                'exchange': 'صرف',
                'rate': 'سعر',
                'market': 'سوق',
                'store': 'متجر',
                'shop': 'محل',
                'mall': 'مركز تجاري',
                'supermarket': 'سوبرماركت',
                'grocery': 'بقالة',
                'restaurant': 'مطعم',
                'cafe': 'مقهى',
                'hotel': 'فندق',
                'hospital': 'مستشفى',
                'school': 'مدرسة',
                'university': 'جامعة',
                'college': 'كلية',
                'library': 'مكتبة',
                'museum': 'متحف',
                'park': 'حديقة',
                'garden': 'حديقة',
                'zoo': 'حديقة حيوانات',
                'beach': 'شاطئ',
                'mountain': 'جبل',
                'river': 'نهر',
                'lake': 'بحيرة',
                'sea': 'بحر',
                'ocean': 'محيط',
                'island': 'جزيرة',
                'desert': 'صحراء',
                'forest': 'غابة',
                'jungle': 'غابة',
                'field': 'حقل',
                'farm': 'مزرعة',
                'village': 'قرية',
                'town': 'بلدة',
                'city': 'مدينة',
                'capital': 'عاصمة',
                'country': 'دولة',
                'nation': 'أمة',
                'government': 'حكومة',
                'politics': 'سياسة',
                'law': 'قانون',
                'justice': 'عدالة',
                'court': 'محكمة',
                'police': 'شرطة',
                'army': 'جيش',
                'war': 'حرب',
                'peace': 'سلام',
                'freedom': 'حرية',
                'rights': 'حقوق',
                'duties': 'واجبات',
                'responsibilities': 'مسؤوليات',
                'privileges': 'امتيازات',
                'obligations': 'التزامات',
                'contract': 'عقد',
                'agreement': 'اتفاق',
                'deal': 'صفقة',
                'negotiation': 'تفاوض',
                'compromise': 'تنازل',
                'conflict': 'نزاع',
                'dispute': 'خلاف',
                'solution': 'حل',
                'problem': 'مشكلة',
                'issue': 'قضية',
                'challenge': 'تحدي',
                'opportunity': 'فرصة',
                'risk': 'خطر',
                'danger': 'خطر',
                'safety': 'أمان',
                'security': 'أمن',
                'protection': 'حماية',
                'defense': 'دفاع',
                'attack': 'هجوم',
                'victory': 'نصر',
                'defeat': 'هزيمة',
                'success': 'نجاح',
                'failure': 'فشل',
                'achievement': 'إنجاز',
                'accomplishment': 'إنجاز',
                'goal': 'هدف',
                'objective': 'هدف',
                'purpose': 'غرض',
                'aim': 'هدف',
                'target': 'هدف',
                'plan': 'خطة',
                'strategy': 'استراتيجية',
                'tactic': 'تكتيك',
                'method': 'طريقة',
                'approach': 'نهج',
                'technique': 'تقنية',
                'skill': 'مهارة',
                'ability': 'قدرة',
                'talent': 'موهبة',
                'gift': 'هدية',
                'knowledge': 'معرفة',
                'information': 'معلومات',
                'data': 'بيانات',
                'fact': 'حقيقة',
                'truth': 'حقيقة',
                'lie': 'كذبة',
                'secret': 'سر',
                'mystery': 'غموض',
                'puzzle': 'لغز',
                'riddle': 'لغز',
                'question': 'سؤال',
                'answer': 'إجابة',
                'solution': 'حل',
                'explanation': 'شرح',
                'description': 'وصف',
                'definition': 'تعريف',
                'example': 'مثال',
                'instance': 'حالة',
                'case': 'حالة',
                'situation': 'موقف',
                'circumstance': 'ظرف',
                'condition': 'شرط',
                'requirement': 'متطلب',
                'need': 'حاجة',
                'want': 'رغبة',
                'desire': 'رغبة',
                'wish': 'أمنية',
                'hope': 'أمل',
                'dream': 'حلم',
                'fantasy': 'خيال',
                'reality': 'واقع',
                'imagination': 'خيال',
                'thought': 'فكرة',
                'idea': 'فكرة',
                'concept': 'مفهوم',
                'notion': 'فكرة',
                'opinion': 'رأي',
                'view': 'رأي',
                'perspective': 'وجهة نظر',
                'attitude': 'موقف',
                'belief': 'اعتقاد',
                'faith': 'إيمان',
                'religion': 'دين',
                'god': 'الله',
                'spirit': 'روح',
                'soul': 'روح',
                'mind': 'عقل',
                'brain': 'دماغ',
                'heart': 'قلب',
                'body': 'جسم',
                'health': 'صحة',
                'illness': 'مرض',
                'disease': 'مرض',
                'infection': 'عدوى',
                'virus': 'فيروس',
                'bacteria': 'بكتيريا',
                'germ': 'جرثومة',
                'medicine': 'دواء',
                'drug': 'دواء',
                'treatment': 'علاج',
                'cure': 'علاج',
                'recovery': 'شفاء',
                'healing': 'شفاء',
                'death': 'موت',
                'life': 'حياة',
                'birth': 'ولادة',
                'age': 'عمر',
                'child': 'طفل',
                'adult': 'بالغ',
                'teenager': 'مراهق',
                'youth': 'شاب',
                'elderly': 'مسن',
                'old': 'قديم',
                'young': 'شاب',
                'baby': 'رضيع',
                'infant': 'رضيع',
                'toddler': 'طفل صغير',
                'kid': 'طفل',
                'boy': 'ولد',
                'girl': 'بنت',
                'man': 'رجل',
                'woman': 'امرأة',
                'male': 'ذكر',
                'female': 'أنثى',
                'gender': 'جنس',
                'sex': 'جنس',
                'family': 'عائلة',
                'parent': 'والد',
                'father': 'أب',
                'mother': 'أم',
                'son': 'ابن',
                'daughter': 'ابنة',
                'brother': 'أخ',
                'sister': 'أخت',
                'grandparent': 'جد',
                'grandfather': 'جد',
                'grandmother': 'جدة',
                'grandchild': 'حفيد',
                'grandson': 'حفيد',
                'granddaughter': 'حفيدة',
                'uncle': 'عم',
                'aunt': 'عمة',
                'cousin': 'ابن عم',
                'nephew': 'ابن أخ',
                'niece': 'ابنة أخ',
                'relative': 'قريب',
                'friend': 'صديق',
                'enemy': 'عدو',
                'stranger': 'غريب',
                'neighbor': 'جار',
                'colleague': 'زميل',
                'partner': 'شريك',
                'associate': 'شريك',
                'companion': 'رفيق',
                'acquaintance': 'معارف',
                'contact': 'اتصال',
                'network': 'شبكة',
                'community': 'مجتمع',
                'society': 'مجتمع',
                'population': 'سكان',
                'people': 'ناس',
                'person': 'شخص',
                'individual': 'فرد',
                'human': 'إنسان',
                'being': 'كائن',
                'creature': 'مخلوق',
                'animal': 'حيوان',
                'pet': 'حيوان أليف',
                'dog': 'كلب',
                'cat': 'قط',
                'bird': 'طائر',
                'fish': 'سمك',
                'insect': 'حشرة',
                'plant': 'نبات',
                'tree': 'شجرة',
                'flower': 'زهرة',
                'fruit': 'فاكهة',
                'vegetable': 'خضار',
                'food': 'طعام',
                'meal': 'وجبة',
                'breakfast': 'فطور',
                'lunch': 'غداء',
                'dinner': 'عشاء',
                'snack': 'وجبة خفيفة',
                'drink': 'شراب',
                'water': 'ماء',
                'juice': 'عصير',
                'coffee': 'قهوة',
                'tea': 'شاي',
                'milk': 'حليب',
                'alcohol': 'كحول',
                'wine': 'نبيذ',
                'beer': 'بيرة',
                'sugar': 'سكر',
                'salt': 'ملح',
                'spice': 'توابل',
                'herb': 'عشب',
                'meat': 'لحم',
                'chicken': 'دجاج',
                'beef': 'لحم بقري',
                'pork': 'لحم خنزير',
                'fish': 'سمك',
                'seafood': 'مأكولات بحرية',
                'egg': 'بيض',
                'cheese': 'جبن',
                'bread': 'خبز',
                'rice': 'أرز',
                'pasta': 'معكرونة',
                'soup': 'شوربة',
                'salad': 'سلطة',
                'dessert': 'حلوى',
                'cake': 'كعكة',
                'chocolate': 'شوكولاتة',
                'ice cream': 'آيس كريم',
                'candy': 'حلوى',
                'cookie': 'بسكويت',
                'pie': 'فطيرة',
                'pastry': 'معجنات',
                'dish': 'طبق',
                'plate': 'طبق',
                'bowl': 'وعاء',
                'cup': 'كوب',
                'glass': 'كوب',
                'bottle': 'زجاجة',
                'can': 'علبة',
                'box': 'صندوق',
                'bag': 'حقيبة',
                'container': 'حاوية',
                'package': 'طرد',
                'parcel': 'طرد',
                'gift': 'هدية',
                'present': 'هدية',
                'card': 'بطاقة',
                'letter': 'رسالة',
                'envelope': 'ظرف',
                'post': 'بريد',
                'mail': 'بريد',
                'email': 'بريد إلكتروني',
                'message': 'رسالة',
                'text': 'نص',
                'call': 'مكالمة',
                'phone': 'هاتف',
                'mobile': 'جوال',
                'smartphone': 'هاتف ذكي',
                'computer': 'حاسوب',
                'laptop': 'حاسوب محمول',
                'tablet': 'جهاز لوحي',
                'screen': 'شاشة',
                'monitor': 'شاشة',
                'keyboard': 'لوحة مفاتيح',
                'mouse': 'فأرة',
                'printer': 'طابعة',
                'scanner': 'ماسح ضوئي',
                'camera': 'كاميرا',
                'microphone': 'ميكروفون',
                'speaker': 'مكبر صوت',
                'headphone': 'سماعة',
                'charger': 'شاحن',
                'battery': 'بطارية',
                'power': 'طاقة',
                'electricity': 'كهرباء',
                'gas': 'غاز',
                'oil': 'نفط',
                'fuel': 'وقود',
                'energy': 'طاقة',
                'source': 'مصدر',
                'resource': 'مورد',
                'material': 'مادة',
                'substance': 'مادة',
                'element': 'عنصر',
                'compound': 'مركب',
                'mixture': 'خليط',
                'solution': 'محلول',
                'chemical': 'مادة كيميائية',
                'reaction': 'تفاعل',
                'experiment': 'تجربة',
                'research': 'بحث',
                'study': 'دراسة',
                'analysis': 'تحليل',
                'test': 'اختبار',
                'exam': 'امتحان',
                'quiz': 'اختبار',
                'homework': 'واجب منزلي',
                'assignment': 'مهمة',
                'project': 'مشروع',
                'task': 'مهمة',
                'job': 'عمل',
                'work': 'عمل',
                'career': 'مهنة',
                'profession': 'مهنة',
                'occupation': 'مهنة',
                'employment': 'توظيف',
                'unemployment': 'بطالة',
                'retirement': 'تقاعد',
                'vacation': 'إجازة',
                'holiday': 'عطلة',
                'weekend': 'عطلة نهاية الأسبوع',
                'break': 'استراحة',
                'rest': 'راحة',
                'sleep': 'نوم',
                'dream': 'حلم',
                'nightmare': 'كابوس',
                'wake': 'استيقاظ',
                'awake': 'مستيقظ',
                'asleep': 'نائم',
                'tired': 'متعب',
                'exhausted': 'مرهق',
                'energetic': 'نشيط',
                'active': 'نشط',
                'lazy': 'كسول',
                'busy': 'مشغول',
                'free': 'حر',
                'available': 'متاح',
                'unavailable': 'غير متاح',
                'occupied': 'مشغول',
                'empty': 'فارغ',
                'full': 'ممتلئ',
                'crowded': 'مزدحم',
                'quiet': 'هادئ',
                'noisy': 'صاخب',
                'loud': 'عالي',
                'soft': 'منخفض',
                'silent': 'صامت',
                'still': 'ساكن',
                'moving': 'متحرك',
                'motion': 'حركة',
                'movement': 'حركة',
                'action': 'فعل',
                'activity': 'نشاط',
                'event': 'حدث',
                'occasion': 'مناسبة',
                'celebration': 'احتفال',
                'party': 'حفلة',
                'festival': 'مهرجان',
                'ceremony': 'مراسم',
                'ritual': 'طقس',
                'tradition': 'تقليد',
                'custom': 'عادة',
                'habit': 'عادة',
                'routine': 'روتين',
                'schedule': 'جدول',
                'timetable': 'جدول زمني',
                'calendar': 'تقويم',
                'date': 'تاريخ',
                'day': 'يوم',
                'week': 'أسبوع',
                'month': 'شهر',
                'year': 'سنة',
                'century': 'قرن',
                'decade': 'عقد',
                'season': 'فصل',
                'spring': 'ربيع',
                'summer': 'صيف',
                'autumn': 'خريف',
                'fall': 'خريف',
                'winter': 'شتاء',
                'weather': 'طقس',
                'climate': 'مناخ',
                'temperature': 'درجة حرارة',
                'hot': 'ساخن',
                'cold': 'بارد',
                'warm': 'دافئ',
                'cool': 'بارد',
                'sunny': 'مشمس',
                'cloudy': 'غائم',
                'rainy': 'ممطر',
                'snowy': 'ثلجي',
                'windy': 'عاصف',
                'stormy': 'عاصف',
                'foggy': 'ضبابي',
                'clear': 'صافي',
                'bright': 'ساطع',
                'dark': 'مظلم',
                'light': 'مضيء',
                'shadow': 'ظل',
                'shade': 'ظل',
                'sun': 'شمس',
                'moon': 'قمر',
                'star': 'نجم',
                'planet': 'كوكب',
                'earth': 'أرض',
                'sky': 'سماء',
                'cloud': 'سحاب',
                'rain': 'مطر',
                'snow': 'ثلج',
                'ice': 'جليد',
                'frost': 'صقيع',
                'wind': 'ريح',
                'breeze': 'نسيم',
                'storm': 'عاصفة',
                'thunder': 'رعد',
                'lightning': 'برق',
                'hurricane': 'إعصار',
                'tornado': 'إعصار',
                'earthquake': 'زلزال',
                'volcano': 'بركان',
                'flood': 'فيضان',
                'drought': 'جفاف',
                'fire': 'حريق',
                'smoke': 'دخان',
                'ash': 'رماد',
                'dust': 'غبار',
                'dirt': 'تراب',
                'mud': 'طين',
                'soil': 'تربة',
                'sand': 'رمل',
                'rock': 'صخر',
                'stone': 'حجر',
                'mountain': 'جبل',
                'hill': 'تل',
                'valley': 'وادي',
                'plain': 'سهل',
                'plateau': 'هضبة',
                'canyon': 'وادي',
                'cave': 'كهف',
                'waterfall': 'شلال',
                'river': 'نهر',
                'stream': 'جدول',
                'brook': 'جدول',
                'creek': 'جدول',
                'lake': 'بحيرة',
                'pond': 'بركة',
                'ocean': 'محيط',
                'sea': 'بحر',
                'bay': 'خليج',
                'gulf': 'خليج',
                'strait': 'مضيق',
                'channel': 'قناة',
                'island': 'جزيرة',
                'peninsula': 'شبه جزيرة',
                'continent': 'قارة',
                'country': 'دولة',
                'nation': 'أمة',
                'state': 'ولاية',
                'province': 'مقاطعة',
                'county': 'مقاطعة',
                'city': 'مدينة',
                'town': 'بلدة',
                'village': 'قرية',
                'hamlet': 'قرية صغيرة',
                'capital': 'عاصمة',
                'metropolis': 'مدينة كبرى',
                'megalopolis': 'منطقة حضرية',
                'urban': 'حضري',
                'rural': 'ريفي',
                'suburb': 'ضاحية',
                'neighborhood': 'حي',
                'district': 'حي',
                'region': 'منطقة',
                'area': 'منطقة',
                'zone': 'منطقة',
                'territory': 'إقليم',
                'border': 'حدود',
                'boundary': 'حدود',
                'frontier': 'حدود',
                'coast': 'ساحل',
                'shore': 'شاطئ',
                'beach': 'شاطئ',
                'port': 'ميناء',
                'harbor': 'ميناء',
                'dock': 'رصيف',
                'pier': 'رصيف',
                'wharf': 'رصيف',
                'airport': 'مطار',
                'station': 'محطة',
                'terminal': 'محطة',
                'stop': 'موقف',
                'bus': 'حافلة',
                'train': 'قطار',
                'subway': 'مترو',
                'metro': 'مترو',
                'tram': 'ترام',
                'taxi': 'تاكسي',
                'cab': 'تاكسي',
                'car': 'سيارة',
                'automobile': 'سيارة',
                'vehicle': 'مركبة',
                'truck': 'شاحنة',
                'van': 'فان',
                'bus': 'حافلة',
                'motorcycle': 'دراجة نارية',
                'bicycle': 'دراجة هوائية',
                'scooter': 'سكوتر',
                'boat': 'قارب',
                'ship': 'سفينة',
                'yacht': 'يخت',
                'ferry': 'عبارة',
                'airplane': 'طائرة',
                'aircraft': 'طائرة',
                'helicopter': 'هليكوبتر',
                'rocket': 'صاروخ',
                'spaceship': 'مركبة فضائية',
                'satellite': 'قمر صناعي',
                'orbit': 'مدار',
                'space': 'فضاء',
                'universe': 'كون',
                'galaxy': 'مجرة',
                'star': 'نجم',
                'planet': 'كوكب',
                'moon': 'قمر',
                'sun': 'شمس',
                'solar': 'شمسي',
                'lunar': 'قمري',
                'earth': 'أرضي',
                'world': 'عالم',
                'globe': 'كرة أرضية',
                'map': 'خريطة',
                'atlas': 'أطلس',
                'globe': 'كرة أرضية',
                'compass': 'بوصلة',
                'direction': 'اتجاه',
                'north': 'شمال',
                'south': 'جنوب',
                'east': 'شرق',
                'west': 'غرب',
                'northeast': 'شمال شرق',
                'northwest': 'شمال غرب',
                'southeast': 'جنوب شرق',
                'southwest': 'جنوب غرب',
                'up': 'أعلى',
                'down': 'أسفل',
                'left': 'يسار',
                'right': 'يمين',
                'forward': 'أمام',
                'backward': 'خلف',
                'inside': 'داخل',
                'outside': 'خارج',
                'top': 'أعلى',
                'bottom': 'أسفل',
                'front': 'أمام',
                'back': 'خلف',
                'side': 'جانب',
                'edge': 'حافة',
                'corner': 'زاوية',
                'center': 'مركز',
                'middle': 'وسط',
                'end': 'نهاية',
                'beginning': 'بداية',
                'start': 'بداية',
                'finish': 'نهاية',
                'complete': 'مكتمل',
                'incomplete': 'غير مكتمل',
                'whole': 'كامل',
                'part': 'جزء',
                'piece': 'قطعة',
                'section': 'قسم',
                'segment': 'قطعة',
                'fraction': 'كسر',
                'percentage': 'نسبة مئوية',
                'ratio': 'نسبة',
                'proportion': 'نسبة',
                'rate': 'معدل',
                'speed': 'سرعة',
                'velocity': 'سرعة',
                'acceleration': 'تسارع',
                'deceleration': 'تباطؤ',
                'momentum': 'زخم',
                'force': 'قوة',
                'power': 'قوة',
                'energy': 'طاقة',
                'work': 'عمل',
                'pressure': 'ضغط',
                'stress': 'إجهاد',
                'tension': 'توتر',
                'strain': 'إجهاد',
                'weight': 'وزن',
                'mass': 'كتلة',
                'volume': 'حجم',
                'density': 'كثافة',
                'temperature': 'درجة حرارة',
                'heat': 'حرارة',
                'cold': 'برودة',
                'warm': 'دفء',
                'cool': 'برودة',
                'freezing': 'تجمد',
                'boiling': 'غليان',
                'melting': 'انصهار',
                'evaporation': 'تبخر',
                'condensation': 'تكثيف',
                'sublimation': 'تصعيد',
                'deposition': 'ترسيب',
                'fusion': 'انصهار',
                'fission': 'انشطار',
                'reaction': 'تفاعل',
                'chemical': 'كيميائي',
                'physical': 'فيزيائي',
                'biological': 'بيولوجي',
                'natural': 'طبيعي',
                'artificial': 'اصطناعي',
                'synthetic': 'اصطناعي',
                'organic': 'عضوي',
                'inorganic': 'غير عضوي',
                'metal': 'معدن',
                'nonmetal': 'غير معدني',
                'element': 'عنصر',
                'compound': 'مركب',
                'mixture': 'خليط',
                'solution': 'محلول',
                'suspension': 'معلق',
                'colloid': 'مستعلق',
                'emulsion': 'مستحلب',
                'foam': 'رغوة',
                'aerosol': 'هباء',
                'gel': 'هلام',
                'paste': 'معجون',
                'powder': 'مسحوق',
                'crystal': 'بلورة',
                'mineral': 'معدن',
                'ore': 'خام',
                'rock': 'صخر',
                'stone': 'حجر',
                'gem': 'حجر كريم',
                'jewel': 'جوهرة',
                'diamond': 'ألماس',
                'ruby': 'ياقوت',
                'emerald': 'زمرد',
                'sapphire': 'ياقوت أزرق',
                'pearl': 'لؤلؤ',
                'gold': 'ذهب',
                'silver': 'فضة',
                'copper': 'نحاس',
                'iron': 'حديد',
                'steel': 'صلب',
                'aluminum': 'ألومنيوم',
                'lead': 'رصاص',
                'tin': 'قصدير',
                'zinc': 'زنك',
                'nickel': 'نيكل',
                'platinum': 'بلاتين',
                'mercury': 'زئبق',
                'uranium': 'يورانيوم',
                'radium': 'راديوم',
                'carbon': 'كربون',
                'oxygen': 'أكسجين',
                'hydrogen': 'هيدروجين',
                'nitrogen': 'نيتروجين',
                'helium': 'هيليوم',
                'neon': 'نيون',
                'argon': 'أرجون',
                'krypton': 'كريبتون',
                'xenon': 'زينون',
                'radon': 'رادون',
                'chlorine': 'كلور',
                'fluorine': 'فلور',
                'bromine': 'بروم',
                'iodine': 'يود',
                'sulfur': 'كبريت',
                'phosphorus': 'فوسفور',
                'silicon': 'سيليكون',
                'germanium': 'جرمانيوم',
                'arsenic': 'زرنيخ',
                'antimony': 'إثمد',
                'bismuth': 'بزموت',
                'selenium': 'سيلينيوم',
                'tellurium': 'تيلوريوم',
                'polonium': 'بولونيوم',
                'astatine': 'أستاتين',
                'francium': 'فرانسيوم',
                'radium': 'راديوم',
                'actinium': 'أكتينيوم',
                'thorium': 'ثوريوم',
                'protactinium': 'بروتكتينيوم',
                'uranium': 'يورانيوم',
                'neptunium': 'نبتونيوم',
                'plutonium': 'بلوتونيوم',
                'americium': 'أمريكيوم',
                'curium': 'كوريوم',
                'berkelium': 'بركليوم',
                'californium': 'كاليفورنيوم',
                'einsteinium': 'أينشتاينيوم',
                'fermium': 'فرميوم',
                'mendelevium': 'مندليفيوم',
                'nobelium': 'نوبليوم',
                'lawrencium': 'لورنسيوم',
                'rutherfordium': 'رذرفورديوم',
                'dubnium': 'دوبنيوم',
                'seaborgium': 'سيبورغيوم',
                'bohrium': 'بوريوم',
                'hassium': 'هاسيوم',
                'meitnerium': 'مايتنريوم',
                'darmstadtium': 'دارمشتاتيوم',
                'roentgenium': 'رونتجينيوم',
                'copernicium': 'كوبرنيسيوم',
                'nihonium': 'نيهونيوم',
                'flerovium': 'فليروفيوم',
                'moscovium': 'موسكوفيوم',
                'livermorium': 'ليفرموريوم',
                'tennessine': 'تينيسين',
                'oganesson': 'أوغانيسون',
            },
            'en': {
                'dashboard': 'Dashboard',
                'invoices': 'Invoices',
                'clients': 'Clients',
                'products': 'Products',
                'reports': 'Reports',
                'ai_insights': 'AI Insights',
                'profile': 'Profile',
                'settings': 'Settings',
                'logout': 'Logout',
                'welcome': 'Welcome',
                'total_invoices': 'Total Invoices',
                'total_revenue': 'Total Revenue',
                'pending_invoices': 'Pending Invoices',
                'total_clients': 'Total Clients',
                'create_invoice': 'Create Invoice',
                'view_all': 'View All',
                'recent_invoices': 'Recent Invoices',
                'quick_actions': 'Quick Actions',
                'performance_summary': 'Performance Summary',
                'recent_activity': 'Recent Activity',
                'paid': 'Paid',
                'pending': 'Pending',
                'overdue': 'Overdue',
                'cancelled': 'Cancelled',
                'view': 'View',
                'download': 'Download',
                'edit': 'Edit',
                'delete': 'Delete',
                'save': 'Save',
                'cancel': 'Cancel',
                'search': 'Search',
                'filter': 'Filter',
                'export': 'Export',
                'import': 'Import',
                'print': 'Print',
                'send': 'Send',
                'status': 'Status',
                'amount': 'Amount',
                'date': 'Date',
                'actions': 'Actions',
                'client': 'Client',
                'invoice_number': 'Invoice Number',
                'issue_date': 'Issue Date',
                'due_date': 'Due Date',
                'payment_method': 'Payment Method',
                'notes': 'Notes',
                'subtotal': 'Subtotal',
                'tax': 'Tax',
                'discount': 'Discount',
                'total': 'Total',
                'item': 'Item',
                'quantity': 'Quantity',
                'price': 'Price',
                'unit': 'Unit',
                'description': 'Description',
                'category': 'Category',
                'active': 'Active',
                'inactive': 'Inactive',
                'company': 'Company',
                'phone': 'Phone',
                'email': 'Email',
                'address': 'Address',
                'website': 'Website',
                'tax_number': 'Tax Number',
                'created_at': 'Created At',
                'last_login': 'Last Login',
                'language': 'Language',
                'currency': 'Currency',
                'timezone': 'Timezone',
                'notifications': 'Notifications',
                'security': 'Security',
                'preferences': 'Preferences',
                'help': 'Help',
                'support': 'Support',
                'documentation': 'Documentation',
                'feedback': 'Feedback',
                'version': 'Version',
                'copyright': 'Copyright',
                'all_rights_reserved': 'All Rights Reserved',
                'login': 'Login',
                'register': 'Register',
                'username': 'Username',
                'password': 'Password',
                'confirm_password': 'Confirm Password',
                'remember_me': 'Remember Me',
                'forgot_password': 'Forgot Password?',
                'dont_have_account': 'Don\'t have an account?',
                'already_have_account': 'Already have an account?',
                'sign_up': 'Sign Up',
                'sign_in': 'Sign In',
                'full_name': 'Full Name',
                'company_name': 'Company Name',
                'phone_number': 'Phone Number',
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Info',
                'loading': 'Loading...',
                'processing': 'Processing...',
                'saving': 'Saving...',
                'deleting': 'Deleting...',
                'updating': 'Updating...',
                'sending': 'Sending...',
                'please_wait': 'Please wait...',
                'operation_successful': 'Operation Successful',
                'operation_failed': 'Operation Failed',
                'data_saved': 'Data Saved',
                'data_deleted': 'Data Deleted',
                'data_updated': 'Data Updated',
                'invalid_input': 'Invalid Input',
                'required_field': 'This field is required',
                'invalid_email': 'Invalid Email',
                'password_too_short': 'Password too short',
                'passwords_dont_match': 'Passwords don\'t match',
                'user_exists': 'User already exists',
                'user_not_found': 'User not found',
                'incorrect_password': 'Incorrect password',
                'account_locked': 'Account locked',
                'session_expired': 'Session expired',
                'access_denied': 'Access denied',
                'permission_denied': 'Permission denied',
                'not_authorized': 'Not authorized',
                'maintenance': 'Maintenance',
                'under_maintenance': 'Under maintenance',
                'coming_soon': 'Coming soon',
                'new': 'New',
                'old': 'Old',
                'today': 'Today',
                'yesterday': 'Yesterday',
                'tomorrow': 'Tomorrow',
                'this_week': 'This week',
                'this_month': 'This month',
                'this_year': 'This year',
                'last_week': 'Last week',
                'last_month': 'Last month',
                'last_year': 'Last year',
                'next_week': 'Next week',
                'next_month': 'Next month',
                'next_year': 'Next year',
                'january': 'January',
                'february': 'February',
                'march': 'March',
                'april': 'April',
                'may': 'May',
                'june': 'June',
                'july': 'July',
                'august': 'August',
                'september': 'September',
                'october': 'October',
                'november': 'November',
                'december': 'December',
                'sunday': 'Sunday',
                'monday': 'Monday',
                'tuesday': 'Tuesday',
                'wednesday': 'Wednesday',
                'thursday': 'Thursday',
                'friday': 'Friday',
                'saturday': 'Saturday',
                'am': 'AM',
                'pm': 'PM',
                'morning': 'Morning',
                'afternoon': 'Afternoon',
                'evening': 'Evening',
                'night': 'Night',
                'seconds': 'Seconds',
                'minutes': 'Minutes',
                'hours': 'Hours',
                'days': 'Days',
                'weeks': 'Weeks',
                'months': 'Months',
                'years': 'Years',
                'now': 'Now',
                'soon': 'Soon',
                'later': 'Later',
                'never': 'Never',
                'always': 'Always',
                'sometimes': 'Sometimes',
                'rarely': 'Rarely',
                'often': 'Often',
                'very_often': 'Very often',
                'almost_never': 'Almost never',
                'almost_always': 'Almost always',
                'yes': 'Yes',
                'no': 'No',
                'ok': 'OK',
                'apply': 'Apply',
                'reset': 'Reset',
                'close': 'Close',
                'back': 'Back',
                'next': 'Next',
                'previous': 'Previous',
                'first': 'First',
                'last': 'Last',
                'more': 'More',
                'less': 'Less',
                'all': 'All',
                'none': 'None',
                'some': 'Some',
                'many': 'Many',
                'few': 'Few',
                'several': 'Several',
                'any': 'Any',
                'each': 'Each',
                'every': 'Every',
                'other': 'Other',
                'another': 'Another',
                'same': 'Same',
                'different': 'Different',
                'similar': 'Similar',
                'opposite': 'Opposite',
                'better': 'Better',
                'worse': 'Worse',
                'best': 'Best',
                'worst': 'Worst',
                'good': 'Good',
                'bad': 'Bad',
                'excellent': 'Excellent',
                'poor': 'Poor',
                'average': 'Average',
                'high': 'High',
                'low': 'Low',
                'medium': 'Medium',
                'large': 'Large',
                'small': 'Small',
                'big': 'Big',
                'tiny': 'Tiny',
                'huge': 'Huge',
                'enormous': 'Enormous',
                'giant': 'Giant',
                'microscopic': 'Microscopic',
                'short': 'Short',
                'long': 'Long',
                'tall': 'Tall',
                'wide': 'Wide',
                'narrow': 'Narrow',
                'deep': 'Deep',
                'shallow': 'Shallow',
                'heavy': 'Heavy',
                'light': 'Light',
                'strong': 'Strong',
                'weak': 'Weak',
                'hard': 'Hard',
                'soft': 'Soft',
                'smooth': 'Smooth',
                'rough': 'Rough',
                'sharp': 'Sharp',
                'dull': 'Dull',
                'bright': 'Bright',
                'dark': 'Dark',
                'light': 'Light',
                'colorful': 'Colorful',
                'colorless': 'Colorless',
                'transparent': 'Transparent',
                'opaque': 'Opaque',
                'shiny': 'Shiny',
                'matte': 'Matte',
                'wet': 'Wet',
                'dry': 'Dry',
                'hot': 'Hot',
                'cold': 'Cold',
                'warm': 'Warm',
                'cool': 'Cool',
                'freezing': 'Freezing',
                'boiling': 'Boiling',
                'clean': 'Clean',
                'dirty': 'Dirty',
                'tidy': 'Tidy',
                'messy': 'Messy',
                'organized': 'Organized',
                'disorganized': 'Disorganized',
                'neat': 'Neat',
                'sloppy': 'Sloppy',
                'elegant': 'Elegant',
                'clumsy': 'Clumsy',
                'graceful': 'Graceful',
                'awkward': 'Awkward',
                'beautiful': 'Beautiful',
                'ugly': 'Ugly',
                'handsome': 'Handsome',
                'pretty': 'Pretty',
                'cute': 'Cute',
                'attractive': 'Attractive',
                'unattractive': 'Unattractive',
                'charming': 'Charming',
                'repulsive': 'Repulsive',
                'friendly': 'Friendly',
                'unfriendly': 'Unfriendly',
                'kind': 'Kind',
                'mean': 'Mean',
                'nice': 'Nice',
                'rude': 'Rude',
                'polite': 'Polite',
                'impolite': 'Impolite',
                'respectful': 'Respectful',
                'disrespectful': 'Disrespectful',
                'honest': 'Honest',
                'dishonest': 'Dishonest',
                'trustworthy': 'Trustworthy',
                'untrustworthy': 'Untrustworthy',
                'reliable': 'Reliable',
                'unreliable': 'Unreliable',
                'responsible': 'Responsible',
                'irresponsible': 'Irresponsible',
                'mature': 'Mature',
                'immature': 'Immature',
                'wise': 'Wise',
                'foolish': 'Foolish',
                'intelligent': 'Intelligent',
                'stupid': 'Stupid',
                'smart': 'Smart',
                'dumb': 'Dumb',
                'clever': 'Clever',
                'naive': 'Naive',
                'experienced': 'Experienced',
                'inexperienced': 'Inexperienced',
                'skilled': 'Skilled',
                'unskilled': 'Unskilled',
                'talented': 'Talented',
                'untalented': 'Untalented',
                'creative': 'Creative',
                'uncreative': 'Uncreative',
                'innovative': 'Innovative',
                'traditional': 'Traditional',
                'modern': 'Modern',
                'ancient': 'Ancient',
                'contemporary': 'Contemporary',
                'future': 'Future',
                'past': 'Past',
                'present': 'Present',
                'temporary': 'Temporary',
                'permanent': 'Permanent',
                'eternal': 'Eternal',
                'finite': 'Finite',
                'infinite': 'Infinite',
                'limited': 'Limited',
                'unlimited': 'Unlimited',
                'enough': 'Enough',
                'insufficient': 'Insufficient',
                'adequate': 'Adequate',
                'inadequate': 'Inadequate',
                'satisfactory': 'Satisfactory',
                'unsatisfactory': 'Unsatisfactory',
                'acceptable': 'Acceptable',
                'unacceptable': 'Unacceptable',
                'appropriate': 'Appropriate',
                'inappropriate': 'Inappropriate',
                'suitable': 'Suitable',
                'unsuitable': 'Unsuitable',
                'proper': 'Proper',
                'improper': 'Improper',
                'correct': 'Correct',
                'incorrect': 'Incorrect',
                'accurate': 'Accurate',
                'inaccurate': 'Inaccurate',
                'precise': 'Precise',
                'imprecise': 'Imprecise',
                'exact': 'Exact',
                'approximate': 'Approximate',
                'right': 'Right',
                'wrong': 'Wrong',
                'true': 'True',
                'false': 'False',
                'real': 'Real',
                'fake': 'Fake',
                'genuine': 'Genuine',
                'artificial': 'Artificial',
                'natural': 'Natural',
                'synthetic': 'Synthetic',
                'organic': 'Organic',
                'inorganic': 'Inorganic',
                'healthy': 'Healthy',
                'unhealthy': 'Unhealthy',
                'fit': 'Fit',
                'unfit': 'Unfit',
                'sick': 'Sick',
                'well': 'Well',
                'ill': 'Ill',
                'injured': 'Injured',
                'wounded': 'Wounded',
                'hurt': 'Hurt',
                'painful': 'Painful',
                'painless': 'Painless',
                'comfortable': 'Comfortable',
                'uncomfortable': 'Uncomfortable',
                'pleasant': 'Pleasant',
                'unpleasant': 'Unpleasant',
                'enjoyable': 'Enjoyable',
                'boring': 'Boring',
                'interesting': 'Interesting',
                'uninteresting': 'Uninteresting',
                'exciting': 'Exciting',
                'calm': 'Calm',
                'peaceful': 'Peaceful',
                'violent': 'Violent',
                'aggressive': 'Aggressive',
                'passive': 'Passive',
                'active': 'Active',
                'energetic': 'Energetic',
                'lazy': 'Lazy',
                'hardworking': 'Hardworking',
                'diligent': 'Diligent',
                'careless': 'Careless',
                'careful': 'Careful',
                'cautious': 'Cautious',
                'reckless': 'Reckless',
                'brave': 'Brave',
                'cowardly': 'Cowardly',
                'fearless': 'Fearless',
                'fearful': 'Fearful',
                'confident': 'Confident',
                'insecure': 'Insecure',
                'optimistic': 'Optimistic',
                'pessimistic': 'Pessimistic',
                'realistic': 'Realistic',
                'idealistic': 'Idealistic',
                'practical': 'Practical',
                'impractical': 'Impractical',
                'logical': 'Logical',
                'illogical': 'Illogical',
                'rational': 'Rational',
                'irrational': 'Irrational',
                'sensible': 'Sensible',
                'senseless': 'Senseless',
                'reasonable': 'Reasonable',
                'unreasonable': 'Unreasonable',
                'fair': 'Fair',
                'unfair': 'Unfair',
                'just': 'Just',
                'unjust': 'Unjust',
                'equal': 'Equal',
                'unequal': 'Unequal',
                'balanced': 'Balanced',
                'unbalanced': 'Unbalanced',
                'stable': 'Stable',
                'unstable': 'Unstable',
                'steady': 'Steady',
                'unsteady': 'Unsteady',
                'consistent': 'Consistent',
                'inconsistent': 'Inconsistent',
                'constant': 'Constant',
                'variable': 'Variable',
                'regular': 'Regular',
                'irregular': 'Irregular',
                'normal': 'Normal',
                'abnormal': 'Abnormal',
                'usual': 'Usual',
                'unusual': 'Unusual',
                'common': 'Common',
                'rare': 'Rare',
                'unique': 'Unique',
                'ordinary': 'Ordinary',
                'extraordinary': 'Extraordinary',
                'special': 'Special',
                'general': 'General',
                'specific': 'Specific',
                'vague': 'Vague',
                'clear': 'Clear',
                'obvious': 'Obvious',
                'hidden': 'Hidden',
                'visible': 'Visible',
                'invisible': 'Invisible',
                'apparent': 'Apparent',
                'transparent': 'Transparent',
                'translucent': 'Translucent',
                'opaque': 'Opaque',
                'solid': 'Solid',
                'liquid': 'Liquid',
                'gas': 'Gas',
                'fluid': 'Fluid',
                'rigid': 'Rigid',
                'flexible': 'Flexible',
                'elastic': 'Elastic',
                'plastic': 'Plastic',
                'metal': 'Metal',
                'wood': 'Wood',
                'glass': 'Glass',
                'paper': 'Paper',
                'fabric': 'Fabric',
                'leather': 'Leather',
                'rubber': 'Rubber',
                'ceramic': 'Ceramic',
                'concrete': 'Concrete',
                'brick': 'Brick',
                'stone': 'Stone',
                'sand': 'Sand',
                'soil': 'Soil',
                'water': 'Water',
                'air': 'Air',
                'fire': 'Fire',
                'earth': 'Earth',
                'space': 'Space',
                'time': 'Time',
                'energy': 'Energy',
                'power': 'Power',
                'force': 'Force',
                'speed': 'Speed',
                'velocity': 'Velocity',
                'acceleration': 'Acceleration',
                'deceleration': 'Deceleration',
                'momentum': 'Momentum',
                'gravity': 'Gravity',
                'weight': 'Weight',
                'mass': 'Mass',
                'volume': 'Volume',
                'density': 'Density',
                'pressure': 'Pressure',
                'temperature': 'Temperature',
                'heat': 'Heat',
                'cold': 'Cold',
                'light': 'Light',
                'dark': 'Dark',
                'sound': 'Sound',
                'noise': 'Noise',
                'silence': 'Silence',
                'music': 'Music',
                'song': 'Song',
                'voice': 'Voice',
                'word': 'Word',
                'sentence': 'Sentence',
                'paragraph': 'Paragraph',
                'text': 'Text',
                'image': 'Image',
                'picture': 'Picture',
                'photo': 'Photo',
                'video': 'Video',
                'audio': 'Audio',
                'file': 'File',
                'document': 'Document',
                'folder': 'Folder',
                'directory': 'Directory',
                'path': 'Path',
                'link': 'Link',
                'url': 'URL',
                'website': 'Website',
                'webpage': 'Webpage',
                'browser': 'Browser',
                'server': 'Server',
                'client': 'Client',
                'network': 'Network',
                'internet': 'Internet',
                'wifi': 'Wi-Fi',
                'bluetooth': 'Bluetooth',
                'signal': 'Signal',
                'connection': 'Connection',
                'disconnection': 'Disconnection',
                'online': 'Online',
                'offline': 'Offline',
                'digital': 'Digital',
                'analog': 'Analog',
                'electronic': 'Electronic',
                'electric': 'Electric',
                'mechanical': 'Mechanical',
                'manual': 'Manual',
                'automatic': 'Automatic',
                'robot': 'Robot',
                'machine': 'Machine',
                'tool': 'Tool',
                'device': 'Device',
                'equipment': 'Equipment',
                'instrument': 'Instrument',
                'appliance': 'Appliance',
                'gadget': 'Gadget',
                'technology': 'Technology',
                'science': 'Science',
                'art': 'Art',
                'culture': 'Culture',
                'history': 'History',
                'geography': 'Geography',
                'mathematics': 'Mathematics',
                'physics': 'Physics',
                'chemistry': 'Chemistry',
                'biology': 'Biology',
                'medicine': 'Medicine',
                'engineering': 'Engineering',
                'architecture': 'Architecture',
                'design': 'Design',
                'business': 'Business',
                'commerce': 'Commerce',
                'trade': 'Trade',
                'industry': 'Industry',
                'manufacturing': 'Manufacturing',
                'production': 'Production',
                'consumption': 'Consumption',
                'distribution': 'Distribution',
                'marketing': 'Marketing',
                'advertising': 'Advertising',
                'sales': 'Sales',
                'purchase': 'Purchase',
                'sell': 'Sell',
                'buy': 'Buy',
                'price': 'Price',
                'cost': 'Cost',
                'value': 'Value',
                'worth': 'Worth',
                'expensive': 'Expensive',
                'cheap': 'Cheap',
                'affordable': 'Affordable',
                'free': 'Free',
                'paid': 'Paid',
                'payment': 'Payment',
                'refund': 'Refund',
                'discount': 'Discount',
                'offer': 'Offer',
                'deal': 'Deal',
                'bargain': 'Bargain',
                'auction': 'Auction',
                'bid': 'Bid',
                'profit': 'Profit',
                'loss': 'Loss',
                'income': 'Income',
                'expense': 'Expense',
                'revenue': 'Revenue',
                'budget': 'Budget',
                'investment': 'Investment',
                'savings': 'Savings',
                'debt': 'Debt',
                'credit': 'Credit',
                'loan': 'Loan',
                'interest': 'Interest',
                'tax': 'Tax',
                'salary': 'Salary',
                'wage': 'Wage',
                'income': 'Income',
                'wealth': 'Wealth',
                'rich': 'Rich',
                'poor': 'Poor',
                'wealthy': 'Wealthy',
                'poverty': 'Poverty',
                'money': 'Money',
                'cash': 'Cash',
                'coin': 'Coin',
                'banknote': 'Banknote',
                'currency': 'Currency',
                'exchange': 'Exchange',
                'rate': 'Rate',
                'market': 'Market',
                'store': 'Store',
                'shop': 'Shop',
                'mall': 'Mall',
                'supermarket': 'Supermarket',
                'grocery': 'Grocery',
                'restaurant': 'Restaurant',
                'cafe': 'Cafe',
                'hotel': 'Hotel',
                'hospital': 'Hospital',
                'school': 'School',
                'university': 'University',
                'college': 'College',
                'library': 'Library',
                'museum': 'Museum',
                'park': 'Park',
                'garden': 'Garden',
                'zoo': 'Zoo',
                'beach': 'Beach',
                'mountain': 'Mountain',
                'river': 'River',
                'lake': 'Lake',
                'sea': 'Sea',
                'ocean': 'Ocean',
                'island': 'Island',
                'desert': 'Desert',
                'forest': 'Forest',
                'jungle': 'Jungle',
                'field': 'Field',
                'farm': 'Farm',
                'village': 'Village',
                'town': 'Town',
                'city': 'City',
                'capital': 'Capital',
                'country': 'Country',
                'nation': 'Nation',
                'government': 'Government',
                'politics': 'Politics',
                'law': 'Law',
                'justice': 'Justice',
                'court': 'Court',
                'police': 'Police',
                'army': 'Army',
                'war': 'War',
                'peace': 'Peace',
                'freedom': 'Freedom',
                'rights': 'Rights',
                'duties': 'Duties',
                'responsibilities': 'Responsibilities',
                'privileges': 'Privileges',
                'obligations': 'Obligations',
                'contract': 'Contract',
                'agreement': 'Agreement',
                'deal': 'Deal',
                'negotiation': 'Negotiation',
                'compromise': 'Compromise',
                'conflict': 'Conflict',
                'dispute': 'Dispute',
                'solution': 'Solution',
                'problem': 'Problem',
                'issue': 'Issue',
                'challenge': 'Challenge',
                'opportunity': 'Opportunity',
                'risk': 'Risk',
                'danger': 'Danger',
                'safety': 'Safety',
                'security': 'Security',
                'protection': 'Protection',
                'defense': 'Defense',
                'attack': 'Attack',
                'victory': 'Victory',
                'defeat': 'Defeat',
                'success': 'Success',
                'failure': 'Failure',
                'achievement': 'Achievement',
                'accomplishment': 'Accomplishment',
                'goal': 'Goal',
                'objective': 'Objective',
                'purpose': 'Purpose',
                'aim': 'Aim',
                'target': 'Target',
                'plan': 'Plan',
                'strategy': 'Strategy',
                'tactic': 'Tactic',
                'method': 'Method',
                'approach': 'Approach',
                'technique': 'Technique',
                'skill': 'Skill',
                'ability': 'Ability',
                'talent': 'Talent',
                'gift': 'Gift',
                'knowledge': 'Knowledge',
                'information': 'Information',
                'data': 'Data',
                'fact': 'Fact',
                'truth': 'Truth',
                'lie': 'Lie',
                'secret': 'Secret',
                'mystery': 'Mystery',
                'puzzle': 'Puzzle',
                'riddle': 'Riddle',
                'question': 'Question',
                'answer': 'Answer',
                'solution': 'Solution',
                'explanation': 'Explanation',
                'description': 'Description',
                'definition': 'Definition',
                'example': 'Example',
                'instance': 'Instance',
                'case': 'Case',
                'situation': 'Situation',
                'circumstance': 'Circumstance',
                'condition': 'Condition',
                'requirement': 'Requirement',
                'need': 'Need',
                'want': 'Want',
                'desire': 'Desire',
                'wish': 'Wish',
                'hope': 'Hope',
                'dream': 'Dream',
                'fantasy': 'Fantasy',
                'reality': 'Reality',
                'imagination': 'Imagination',
                'thought': 'Thought',
                'idea': 'Idea',
                'concept': 'Concept',
                'notion': 'Notion',
                'opinion': 'Opinion',
                'view': 'View',
                'perspective': 'Perspective',
                'attitude': 'Attitude',
                'belief': 'Belief',
                'faith': 'Faith',
                'religion': 'Religion',
                'god': 'God',
                'spirit': 'Spirit',
                'soul': 'Soul',
                'mind': 'Mind',
                'brain': 'Brain',
                'heart': 'Heart',
                'body': 'Body',
                'health': 'Health',
                'illness': 'Illness',
                'disease': 'Disease',
                'infection': 'Infection',
                'virus': 'Virus',
                'bacteria': 'Bacteria',
                'germ': 'Germ',
                'medicine': 'Medicine',
                'drug': 'Drug',
                'treatment': 'Treatment',
                'cure': 'Cure',
                'recovery': 'Recovery',
                'healing': 'Healing',
                'death': 'Death',
                'life': 'Life',
                'birth': 'Birth',
                'age': 'Age',
                'child': 'Child',
                'adult': 'Adult',
                'teenager': 'Teenager',
                'youth': 'Youth',
                'elderly': 'Elderly',
                'old': 'Old',
                'young': 'Young',
                'baby': 'Baby',
                'infant': 'Infant',
                'toddler': 'Toddler',
                'kid': 'Kid',
                'boy': 'Boy',
                'girl': 'Girl',
                'man': 'Man',
                'woman': 'Woman',
                'male': 'Male',
                'female': 'Female',
                'gender': 'Gender',
                'sex': 'Sex',
                'family': 'Family',
                'parent': 'Parent',
                'father': 'Father',
                'mother': 'Mother',
                'son': 'Son',
                'daughter': 'Daughter',
                'brother': 'Brother',
                'sister': 'Sister',
                'grandparent': 'Grandparent',
                'grandfather': 'Grandfather',
                'grandmother': 'Grandmother',
                'grandchild': 'Grandchild',
                'grandson': 'Grandson',
                'granddaughter': 'Granddaughter',
                'uncle': 'Uncle',
                'aunt': 'Aunt',
                'cousin': 'Cousin',
                'nephew': 'Nephew',
                'niece': 'Niece',
                'relative': 'Relative',
                'friend': 'Friend',
                'enemy': 'Enemy',
                'stranger': 'Stranger',
                'neighbor': 'Neighbor',
                'colleague': 'Colleague',
                'partner': 'Partner',
                'associate': 'Associate',
                'companion': 'Companion',
                'acquaintance': 'Acquaintance',
                'contact': 'Contact',
                'network': 'Network',
                'community': 'Community',
                'society': 'Society',
                'population': 'Population',
                'people': 'People',
                'person': 'Person',
                'individual': 'Individual',
                'human': 'Human',
                'being': 'Being',
                'creature': 'Creature',
                'animal': 'Animal',
                'pet': 'Pet',
                'dog': 'Dog',
                'cat': 'Cat',
                'bird': 'Bird',
                'fish': 'Fish',
                'insect': 'Insect',
                'plant': 'Plant',
                'tree': 'Tree',
                'flower': 'Flower',
                'fruit': 'Fruit',
                'vegetable': 'Vegetable',
                'food': 'Food',
                'meal': 'Meal',
                'breakfast': 'Breakfast',
                'lunch': 'Lunch',
                'dinner': 'Dinner',
                'snack': 'Snack',
                'drink': 'Drink',
                'water': 'Water',
                'juice': 'Juice',
                'coffee': 'Coffee',
                'tea': 'Tea',
                'milk': 'Milk',
                'alcohol': 'Alcohol',
                'wine': 'Wine',
                'beer': 'Beer',
                'sugar': 'Sugar',
                'salt': 'Salt',
                'spice': 'Spice',
                'herb': 'Herb',
                'meat': 'Meat',
                'chicken': 'Chicken',
                'beef': 'Beef',
                'pork': 'Pork',
                'fish': 'Fish',
                'seafood': 'Seafood',
                'egg': 'Egg',
                'cheese': 'Cheese',
                'bread': 'Bread',
                'rice': 'Rice',
                'pasta': 'Pasta',
                'soup': 'Soup',
                'salad': 'Salad',
                'dessert': 'Dessert',
                'cake': 'Cake',
                'chocolate': 'Chocolate',
                'ice cream': 'Ice Cream',
                'candy': 'Candy',
                'cookie': 'Cookie',
                'pie': 'Pie',
                'pastry': 'Pastry',
                'dish': 'Dish',
                'plate': 'Plate',
                'bowl': 'Bowl',
                'cup': 'Cup',
                'glass': 'Glass',
                'bottle': 'Bottle',
                'can': 'Can',
                'box': 'Box',
                'bag': 'Bag',
                'container': 'Container',
                'package': 'Package',
                'parcel': 'Parcel',
                'gift': 'Gift',
                'present': 'Present',
                'card': 'Card',
                'letter': 'Letter',
                'envelope': 'Envelope',
                'post': 'Post',
                'mail': 'Mail',
                'email': 'Email',
                'message': 'Message',
                'text': 'Text',
                'call': 'Call',
                'phone': 'Phone',
                'mobile': 'Mobile',
                'smartphone': 'Smartphone',
                'computer': 'Computer',
                'laptop': 'Laptop',
                'tablet': 'Tablet',
                'screen': 'Screen',
                'monitor': 'Monitor',
                'keyboard': 'Keyboard',
                'mouse': 'Mouse',
                'printer': 'Printer',
                'scanner': 'Scanner',
                'camera': 'Camera',
                'microphone': 'Microphone',
                'speaker': 'Speaker',
                'headphone': 'Headphone',
                'charger': 'Charger',
                'battery': 'Battery',
                'power': 'Power',
                'electricity': 'Electricity',
                'gas': 'Gas',
                'oil': 'Oil',
                'fuel': 'Fuel',
                'energy': 'Energy',
                'source': 'Source',
                'resource': 'Resource',
                'material': 'Material',
                'substance': 'Substance',
                'element': 'Element',
                'compound': 'Compound',
                'mixture': 'Mixture',
                'solution': 'Solution',
                'chemical': 'Chemical',
                'reaction': 'Reaction',
                'experiment': 'Experiment',
                'research': 'Research',
                'study': 'Study',
                'analysis': 'Analysis',
                'test': 'Test',
                'exam': 'Exam',
                'quiz': 'Quiz',
                'homework': 'Homework',
                'assignment': 'Assignment',
                'project': 'Project',
                'task': 'Task',
                'job': 'Job',
                'work': 'Work',
                'career': 'Career',
                'profession': 'Profession',
                'occupation': 'Occupation',
                'employment': 'Employment',
                'unemployment': 'Unemployment',
                'retirement': 'Retirement',
                'vacation': 'Vacation',
                'holiday': 'Holiday',
                'weekend': 'Weekend',
                'break': 'Break',
                'rest': 'Rest',
                'sleep': 'Sleep',
                'dream': 'Dream',
                'nightmare': 'Nightmare',
                'wake': 'Wake',
                'awake': 'Awake',
                'asleep': 'Asleep',
                'tired': 'Tired',
                'exhausted': 'Exhausted',
                'energetic': 'Energetic',
                'active': 'Active',
                'lazy': 'Lazy',
                'busy': 'Busy',
                'free': 'Free',
                'available': 'Available',
                'unavailable': 'Unavailable',
                'occupied': 'Occupied',
                'empty': 'Empty',
                'full': 'Full',
                'crowded': 'Crowded',
                'quiet': 'Quiet',
                'noisy': 'Noisy',
                'loud': 'Loud',
                'soft': 'Soft',
                'silent': 'Silent',
                'still': 'Still',
                'moving': 'Moving',
                'motion': 'Motion',
                'movement': 'Movement',
                'action': 'Action',
                'activity': 'Activity',
                'event': 'Event',
                'occasion': 'Occasion',
                'celebration': 'Celebration',
                'party': 'Party',
                'festival': 'Festival',
                'ceremony': 'Ceremony',
                'ritual': 'Ritual',
                'tradition': 'Tradition',
                'custom': 'Custom',
                'habit': 'Habit',
                'routine': 'Routine',
                'schedule': 'Schedule',
                'timetable': 'Timetable',
                'calendar': 'Calendar',
                'date': 'Date',
                'day': 'Day',
                'week': 'Week',
                'month': 'Month',
                'year': 'Year',
                'century': 'Century',
                'decade': 'Decade',
                'season': 'Season',
                'spring': 'Spring',
                'summer': 'Summer',
                'autumn': 'Autumn',
                'fall': 'Fall',
                'winter': 'Winter',
                'weather': 'Weather',
                'climate': 'Climate',
                'temperature': 'Temperature',
                'hot': 'Hot',
                'cold': 'Cold',
                'warm': 'Warm',
                'cool': 'Cool',
                'freezing': 'Freezing',
                'boiling': 'Boiling',
                'melting': 'Melting',
                'evaporation': 'Evaporation',
                'condensation': 'Condensation',
                'sublimation': 'Sublimation',
                'deposition': 'Deposition',
                'fusion': 'Fusion',
                'fission': 'Fission',
                'reaction': 'Reaction',
                'chemical': 'Chemical',
                'physical': 'Physical',
                'biological': 'Biological',
                'natural': 'Natural',
                'artificial': 'Artificial',
                'synthetic': 'Synthetic',
                'organic': 'Organic',
                'inorganic': 'Inorganic',
                'metal': 'Metal',
                'nonmetal': 'Nonmetal',
                'element': 'Element',
                'compound': 'Compound',
                'mixture': 'Mixture',
                'solution': 'Solution',
                'suspension': 'Suspension',
                'colloid': 'Colloid',
                'emulsion': 'Emulsion',
                'foam': 'Foam',
                'aerosol': 'Aerosol',
                'gel': 'Gel',
                'paste': 'Paste',
                'powder': 'Powder',
                'crystal': 'Crystal',
                'mineral': 'Mineral',
                'ore': 'Ore',
                'rock': 'Rock',
                'stone': 'Stone',
                'gem': 'Gem',
                'jewel': 'Jewel',
                'diamond': 'Diamond',
                'ruby': 'Ruby',
                'emerald': 'Emerald',
                'sapphire': 'Sapphire',
                'pearl': 'Pearl',
                'gold': 'Gold',
                'silver': 'Silver',
                'copper': 'Copper',
                'iron': 'Iron',
                'steel': 'Steel',
                'aluminum': 'Aluminum',
                'lead': 'Lead',
                'tin': 'Tin',
                'zinc': 'Zinc',
                'nickel': 'Nickel',
                'platinum': 'Platinum',
                'mercury': 'Mercury',
                'uranium': 'Uranium',
                'radium': 'Radium',
                'carbon': 'Carbon',
                'oxygen': 'Oxygen',
                'hydrogen': 'Hydrogen',
                'nitrogen': 'Nitrogen',
                'helium': 'Helium',
                'neon': 'Neon',
                'argon': 'Argon',
                'krypton': 'Krypton',
                'xenon': 'Xenon',
                'radon': 'Radon',
                'chlorine': 'Chlorine',
                'fluorine': 'Fluorine',
                'bromine': 'Bromine',
                'iodine': 'Iodine',
                'sulfur': 'Sulfur',
                'phosphorus': 'Phosphorus',
                'silicon': 'Silicon',
                'germanium': 'Germanium',
                'arsenic': 'Arsenic',
                'antimony': 'Antimony',
                'bismuth': 'Bismuth',
                'selenium': 'Selenium',
                'tellurium': 'Tellurium',
                'polonium': 'Polonium',
                'astatine': 'Astatine',
                'francium': 'Francium',
                'radium': 'Radium',
                'actinium': 'Actinium',
                'thorium': 'Thorium',
                'protactinium': 'Protactinium',
                'uranium': 'Uranium',
                'neptunium': 'Neptunium',
                'plutonium': 'Plutonium',
                'americium': 'Americium',
                'curium': 'Curium',
                'berkelium': 'Berkelium',
                'californium': 'Californium',
                'einsteinium': 'Einsteinium',
                'fermium': 'Fermium',
                'mendelevium': 'Mendelevium',
                'nobelium': 'Nobelium',
                'lawrencium': 'Lawrencium',
                'rutherfordium': 'Rutherfordium',
                'dubnium': 'Dubnium',
                'seaborgium': 'Seaborgium',
                'bohrium': 'Bohrium',
                'hassium': 'Hassium',
                'meitnerium': 'Meitnerium',
                'darmstadtium': 'Darmstadtium',
                'roentgenium': 'Roentgenium',
                'copernicium': 'Copernicium',
                'nihonium': 'Nihonium',
                'flerovium': 'Flerovium',
                'moscovium': 'Moscovium',
                'livermorium': 'Livermorium',
                'tennessine': 'Tennessine',
                'oganesson': 'Oganesson',
            }
        }
    
    def get_text(self, key, lang='ar'):
        """الحصول على النص باللغة المحددة"""
        return self.translations.get(lang, {}).get(key, key)
    
    def get_language(self):
        """الحصول على اللغة الحالية"""
        return session.get('language', 'ar')
    
    def set_language(self, lang):
        """تعيين اللغة"""
        if lang in self.translations:
            session['language'] = lang
            return True
        return False

multilang = MultiLanguage()

# ================== نظام قاعدة البيانات المحسن ==================
class EnhancedDatabaseSystem:
    def __init__(self):
        self.db_path = app.config['DATABASE_PATH']
        self.lock = Lock()
        self.init_database()
    
    def init_database(self):
        """تهيئة قاعدة البيانات مع جداول جديدة"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    company_name TEXT DEFAULT 'شركتي',
                    phone TEXT,
                    address TEXT,
                    logo TEXT,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    language TEXT DEFAULT 'ar',
                    currency TEXT DEFAULT 'USD',
                    timezone TEXT DEFAULT 'Asia/Riyadh',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    settings TEXT DEFAULT '{}',
                    failed_login_attempts INTEGER DEFAULT 0,
                    login_blocked_until TIMESTAMP,
                    email_verified BOOLEAN DEFAULT 0,
                    verification_token TEXT,
                    reset_token TEXT,
                    reset_token_expires TIMESTAMP
                )
            ''')
            
            # جدول العملاء
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    company TEXT,
                    tax_number TEXT,
                    category TEXT DEFAULT 'عام',
                    total_purchases REAL DEFAULT 0,
                    last_purchase DATE,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول الفواتير
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    client_id INTEGER,
                    client_name TEXT NOT NULL,
                    client_email TEXT,
                    client_phone TEXT,
                    client_address TEXT,
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    items TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    tax_rate REAL DEFAULT 0,
                    tax_amount REAL DEFAULT 0,
                    discount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT DEFAULT 'نقدي',
                    notes TEXT,
                    pdf_path TEXT,
                    qr_code TEXT,
                    sent_via_email BOOLEAN DEFAULT 0,
                    sent_via_sms BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL
                )
            ''')
            
            # جدول المنتجات/الخدمات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    unit TEXT DEFAULT 'قطعة',
                    tax_rate REAL DEFAULT 0,
                    category TEXT DEFAULT 'عام',
                    sku TEXT,
                    barcode TEXT,
                    stock_quantity INTEGER DEFAULT 0,
                    min_stock INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول الإشعارات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول الأنشطة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    description TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول الإعدادات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    UNIQUE(user_id, key)
                )
            ''')
            
            # إضافة مستخدم افتراضي إذا لم يكن موجود
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                default_hash = generate_password_hash("Admin@123")
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, full_name, company_name, role, email_verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', ('admin', 'admin@invoiceflow.com', default_hash, 'مدير النظام', 'InvoiceFlow Pro', 'admin', 1))
            
            conn.commit()
            conn.close()
            print("✅ قاعدة البيانات المحسنة جاهزة!")
    
    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=(), fetchone=False, fetchall=False, commit=True):
        """تنفيذ استعلام"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
                
                if fetchone:
                    result = cursor.fetchone()
                    if result:
                        result = dict(result)
                elif fetchall:
                    results = cursor.fetchall()
                    result = [dict(row) for row in results]
                else:
                    result = None
                
                if commit:
                    conn.commit()
                else:
                    conn.rollback()
                
                return result
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

db = EnhancedDatabaseSystem()

# ================== نظام الإشعارات ==================
class NotificationSystem:
    @staticmethod
    def create_notification(user_id, notification_type, title, message, data=None):
        """إنشاء إشعار جديد"""
        return db.execute_query('''
            INSERT INTO notifications (user_id, type, title, message, data, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, notification_type, title, message, json.dumps(data or {})))
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=50):
        """الحصول على إشعارات المستخدم"""
        query = '''
            SELECT * FROM notifications 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if unread_only:
            query += ' AND is_read = 0'
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        return db.execute_query(query, params, fetchall=True)
    
    @staticmethod
    def mark_as_read(notification_id):
        """تحديد الإشعار كمقروء"""
        return db.execute_query(
            "UPDATE notifications SET is_read = 1 WHERE id = ?",
            (notification_id,)
        )
    
    @staticmethod
    def mark_all_as_read(user_id):
        """تحديد جميع إشعارات المستخدم كمقروءة"""
        return db.execute_query(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0",
            (user_id,)
        )
    
    @staticmethod
    def delete_notification(notification_id):
        """حذف إشعار"""
        return db.execute_query(
            "DELETE FROM notifications WHERE id = ?",
            (notification_id,)
        )

# ================== نظام الأنشطة ==================
class ActivityLogger:
    @staticmethod
    def log_activity(user_id, action, description, request=None):
        """تسجيل نشاط"""
        ip_address = request.remote_addr if request else None
        user_agent = request.user_agent.string if request else None
        
        return db.execute_query('''
            INSERT INTO activities (user_id, action, description, ip_address, user_agent, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, action, description, ip_address, user_agent))

# ================== نظام المصادقة المحسن ==================
def login_required(f):
    """مصادقة تسجيل الدخول"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('login', next=request.url))
        
        # التحقق من انتهاء الجلسة
        if 'last_activity' in session:
            last_activity = session['last_activity']
            if time.time() - last_activity > 3600:  # 1 ساعة
                session.clear()
                flash('انتهت جلسة العمل، يرجى تسجيل الدخول مرة أخرى', 'warning')
                return redirect(url_for('login'))
        
        # تحديث وقت النشاط الأخير
        session['last_activity'] = time.time()
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """مصادقة المدير"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('يرجى تسجيل الدخول', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ================== تنسيقات CSS الأساسية ==================
BASE_CSS = """
/* ================== إعدادات التصميم الأساسية ================== */
:root {
    /* الألوان الأساسية - تصميم احترافي */
    --primary-color: #2563eb;
    --primary-dark: #1e40af;
    --primary-light: #60a5fa;
    --secondary-color: #10b981;
    --secondary-dark: #059669;
    --secondary-light: #34d399;
    --accent-color: #8b5cf6;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
    --info-color: #3b82f6;
    --success-color: #10b981;
    
    /* درجات الرمادي */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* الألوان الداكنة */
    --dark-bg: #0f172a;
    --dark-card: #1e293b;
    --dark-border: #334155;
    --dark-text: #f1f5f9;
    --dark-text-secondary: #cbd5e1;
    
    /* ظلال */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    
    /* زوايا */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-2xl: 1.5rem;
    --radius-full: 9999px;
    
    /* التباعد */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;
    --space-16: 4rem;
    --space-20: 5rem;
    --space-24: 6rem;
    
    /* الأنيميشن */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* ================== إعدادات الأساس ================== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Tajawal', Roboto, sans-serif;
    background: linear-gradient(135deg, var(--dark-bg) 0%, #1e293b 100%);
    color: var(--dark-text);
    line-height: 1.6;
    min-height: 100vh;
    direction: rtl;
    text-align: right;
    overflow-x: hidden;
}

/* ================== التمرير المخصص ================== */
::-webkit-scrollbar {
    width: 12px;
    height: 12px;
}

::-webkit-scrollbar-track {
    background: var(--dark-card);
    border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    border-radius: var(--radius-full);
    border: 2px solid var(--dark-card);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, var(--primary-dark), var(--accent-color));
}

/* ================== الأنيميشن ================== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInRight {
    from { transform: translateX(20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideInLeft {
    from { transform: translateX(-20px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

@keyframes scaleIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ================== الطباعة ================== */
@media print {
    .no-print {
        display: none !important;
    }
    
    body {
        background: white !important;
        color: black !important;
    }
    
    .print-only {
        display: block !important;
    }
}

/* ================== التجاوب ================== */
@media (max-width: 768px) {
    :root {
        --space-8: 1rem;
        --space-12: 1.5rem;
        --space-16: 2rem;
    }
}

@media (max-width: 480px) {
    :root {
        --space-4: 0.75rem;
        --space-6: 1rem;
    }
}
"""

# ================== دوال المساعدة للقوالب ==================
def get_flashed_messages_html():
    """إنشاء HTML لرسائل التنبيه"""
    messages_html = ""
    try:
        from flask import get_flashed_messages
        messages = get_flashed_messages(with_categories=True)
        for category, message in messages:
            icon = {
                'success': 'check-circle',
                'error': 'exclamation-circle',
                'warning': 'exclamation-triangle',
                'info': 'info-circle'
            }.get(category, 'info-circle')
            
            messages_html += f"""
            <div class="alert alert-{category} fade-in">
                <i class="fas fa-{icon} alert-icon"></i>
                <div class="alert-content">
                    <p class="alert-message">{message}</p>
                </div>
            </div>
            """
    except:
        pass
    
    return messages_html

def get_time_ago(timestamp):
    """الحصول على الوقت المنقضي"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return "الآن" if session.get('language', 'ar') == 'ar' else "Just now"
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"منذ {years} سنة" if session.get('language', 'ar') == 'ar' else f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"منذ {months} شهر" if session.get('language', 'ar') == 'ar' else f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"منذ {diff.days} يوم" if session.get('language', 'ar') == 'ar' else f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"منذ {hours} ساعة" if session.get('language', 'ar') == 'ar' else f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"منذ {minutes} دقيقة" if session.get('language', 'ar') == 'ar' else f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "الآن" if session.get('language', 'ar') == 'ar' else "Just now"

def generate_notifications_list(notifications):
    """إنشاء قائمة الإشعارات"""
    if not notifications:
        return """
        <div class="p-6 text-center">
            <i class="fas fa-bell-slash text-3xl text-muted mb-3"></i>
            <p class="text-muted">لا توجد إشعارات جديدة</p>
        </div>
        """
    
    notifications_html = ""
    for notification in notifications:
        icon_class = {
            'info': 'fas fa-info-circle text-primary',
            'success': 'fas fa-check-circle text-success',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'error': 'fas fa-times-circle text-danger',
            'invoice': 'fas fa-file-invoice-dollar text-accent',
            'payment': 'fas fa-money-bill-wave text-success',
            'client': 'fas fa-user-plus text-info',
            'system': 'fas fa-cog text-muted'
        }.get(notification['type'], 'fas fa-bell text-muted')
        
        time_ago = get_time_ago(notification['created_at'])
        
        notifications_html += f"""
        <div class="notification {'unread' if not notification['is_read'] else ''}" data-notification-id="{notification['id']}">
            <div class="notification-icon">
                <i class="{icon_class}"></i>
            </div>
            <div class="notification-content">
                <p class="notification-title">{notification['title']}</p>
                <p class="notification-message">{notification['message']}</p>
                <p class="notification-time">{time_ago}</p>
            </div>
        </div>
        """
    
    return notifications_html

# ================== قوالب الصفحات ==================
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    if session.get('user_logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if session.get('user_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')
        
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return redirect(url_for('login'))
        
        user = db.execute_query(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,),
            fetchone=True
        )
        
        if not user:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return redirect(url_for('login'))
        
        if not check_password_hash(user['password_hash'], password):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            return redirect(url_for('login'))
        
        # تحديث وقت الدخول الأخير
        db.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        
        # إنشاء الجلسة
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_role'] = user['role']
        session['company_name'] = user['company_name']
        session['full_name'] = user['full_name'] or user['username']
        session['user_logged_in'] = True
        session['language'] = user.get('language', 'ar')
        session['currency'] = user.get('currency', 'USD')
        session.permanent = bool(remember)
        session['last_activity'] = time.time()
        
        flash(f'مرحباً بك {session["full_name"]}!', 'success')
        return redirect(url_for('dashboard'))
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceFlow Pro - تسجيل الدخول</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            {BASE_CSS}
            
            .login-container {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, var(--dark-bg) 0%, #1a202c 100%);
                padding: var(--space-4);
            }}
            
            .login-card {{
                background: var(--dark-card);
                border-radius: var(--radius-2xl);
                padding: var(--space-8);
                width: 100%;
                max-width: 400px;
                box-shadow: var(--shadow-2xl);
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: scaleIn 0.5s ease;
            }}
            
            .login-header {{
                text-align: center;
                margin-bottom: var(--space-8);
            }}
            
            .login-logo {{
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                border-radius: var(--radius-xl);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto var(--space-4);
                font-size: 2rem;
                color: white;
                box-shadow: var(--shadow-primary);
            }}
            
            .login-title {{
                font-size: 1.875rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: var(--space-2);
            }}
            
            .login-subtitle {{
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }}
            
            .login-form .form-group {{
                margin-bottom: var(--space-4);
            }}
            
            .login-form .form-label {{
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--dark-text-secondary);
            }}
            
            .login-options {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--space-6);
            }}
            
            .login-remember {{
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }}
            
            .login-forgot {{
                color: var(--primary-color);
                text-decoration: none;
                font-size: 0.875rem;
            }}
            
            .login-forgot:hover {{
                text-decoration: underline;
            }}
            
            .login-button {{
                width: 100%;
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                color: white;
                border: none;
                font-weight: 600;
                cursor: pointer;
                transition: all var(--transition-normal);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: var(--space-2);
            }}
            
            .login-button:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-primary);
            }}
            
            .login-button:active {{
                transform: translateY(0);
            }}
            
            .login-footer {{
                margin-top: var(--space-6);
                text-align: center;
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }}
            
            .login-footer a {{
                color: var(--primary-color);
                text-decoration: none;
            }}
            
            .login-footer a:hover {{
                text-decoration: underline;
            }}
            
            .test-credentials {{
                margin-top: var(--space-6);
                padding: var(--space-4);
                background: rgba(255, 255, 255, 0.03);
                border-radius: var(--radius-lg);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .test-credentials h4 {{
                font-size: 0.875rem;
                margin-bottom: var(--space-2);
                color: var(--dark-text-secondary);
            }}
            
            .test-credentials .credentials {{
                display: grid;
                gap: var(--space-2);
            }}
            
            .credential-item {{
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            
            .credential-label {{
                font-size: 0.75rem;
                color: var(--dark-text-secondary);
            }}
            
            .credential-value {{
                font-family: monospace;
                background: rgba(0, 0, 0, 0.3);
                padding: var(--space-1) var(--space-2);
                border-radius: var(--radius-sm);
                font-size: 0.75rem;
                color: var(--primary-color);
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <div class="login-logo">
                        <i class="fas fa-file-invoice-dollar"></i>
                    </div>
                    <h1 class="login-title">InvoiceFlow Pro</h1>
                    <p class="login-subtitle">نظام إدارة الفواتير الاحترافي</p>
                </div>
                
                {get_flashed_messages_html()}
                
                <form class="login-form" method="POST" action="{url_for('login')}">
                    <input type="hidden" name="next" value="{request.args.get('next', '')}">
                    
                    <div class="form-group">
                        <label class="form-label">
                            <i class="fas fa-user"></i>
                            اسم المستخدم
                        </label>
                        <input type="text" name="username" class="form-control" 
                               placeholder="أدخل اسم المستخدم" required autofocus>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">
                            <i class="fas fa-lock"></i>
                            كلمة المرور
                        </label>
                        <input type="password" name="password" class="form-control" 
                               placeholder="أدخل كلمة المرور" required>
                    </div>
                    
                    <div class="login-options">
                        <label class="login-remember">
                            <input type="checkbox" name="remember" class="form-check-input">
                            <span class="form-check-label">تذكرني</span>
                        </label>
                        
                        <a href="#" class="login-forgot">نسيت كلمة المرور؟</a>
                    </div>
                    
                    <button type="submit" class="login-button">
                        <i class="fas fa-sign-in-alt"></i>
                        تسجيل الدخول
                    </button>
                </form>
                
                <!-- بيانات الاختبار -->
                <div class="test-credentials">
                    <h4><i class="fas fa-info-circle"></i> بيانات الاختبار:</h4>
                    <div class="credentials">
                        <div class="credential-item">
                            <span class="credential-label">المستخدم:</span>
                            <code class="credential-value">admin</code>
                        </div>
                        <div class="credential-item">
                            <span class="credential-label">كلمة المرور:</span>
                            <code class="credential-value">Admin@123</code>
                        </div>
                    </div>
                </div>
                
                <div class="login-footer">
                    <p>
                        ليس لديك حساب؟ 
                        <a href="{url_for('register')}">إنشاء حساب جديد</a>
                    </p>
                    <p class="mt-2 text-xs">
                        © 2024 InvoiceFlow Pro. جميع الحقوق محفوظة.
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            // إضافة تأثير عند التحميل
            document.addEventListener('DOMContentLoaded', function() {{
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {{
                    document.body.style.opacity = '1';
                }}, 100);
            }});
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة التسجيل"""
    if session.get('user_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        company_name = request.form.get('company_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        errors = []
        
        if not username or len(username) < 3:
            errors.append('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if not email or '@' not in email:
            errors.append('البريد الإلكتروني غير صالح')
        
        if len(password) < 6:
            errors.append('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
        
        if password != confirm_password:
            errors.append('كلمتا المرور غير متطابقتين')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('register'))
        
        existing_user = db.execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
            fetchone=True
        )
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً', 'error')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        
        db.execute_query('''
            INSERT INTO users (username, email, password_hash, full_name, company_name, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, company_name, phone))
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('login'))
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceFlow Pro - إنشاء حساب</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            {BASE_CSS}
            
            .register-container {{
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, var(--dark-bg) 0%, #1a202c 100%);
                padding: var(--space-4);
            }}
            
            .register-card {{
                background: var(--dark-card);
                border-radius: var(--radius-2xl);
                padding: var(--space-8);
                width: 100%;
                max-width: 500px;
                box-shadow: var(--shadow-2xl);
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: scaleIn 0.5s ease;
            }}
            
            .register-header {{
                text-align: center;
                margin-bottom: var(--space-8);
            }}
            
            .register-logo {{
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                border-radius: var(--radius-xl);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto var(--space-4);
                font-size: 2rem;
                color: white;
                box-shadow: var(--shadow-primary);
            }}
            
            .register-title {{
                font-size: 1.875rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: var(--space-2);
            }}
            
            .register-subtitle {{
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }}
            
            .register-form .form-group {{
                margin-bottom: var(--space-4);
            }}
            
            .register-form .form-label {{
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }}
            
            .register-button {{
                width: 100%;
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                background: linear-gradient(135deg, var(--success-color), var(--secondary-dark));
                color: white;
                border: none;
                font-weight: 600;
                cursor: pointer;
                transition: all var(--transition-normal);
                display: flex;
                align-items: center;
                justify-content: center;
                gap: var(--space-2);
                margin-top: var(--space-6);
            }}
            
            .register-button:hover {{
                transform: translateY(-2px);
                box-shadow: var(--shadow-secondary);
            }}
            
            .register-button:active {{
                transform: translateY(0);
            }}
            
            .register-footer {{
                margin-top: var(--space-6);
                text-align: center;
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }}
            
            .register-footer a {{
                color: var(--primary-color);
                text-decoration: none;
            }}
            
            .register-footer a:hover {{
                text-decoration: underline;
            }}
            
            .form-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--space-4);
            }}
            
            @media (max-width: 640px) {{
                .form-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="register-container">
            <div class="register-card">
                <div class="register-header">
                    <div class="register-logo">
                        <i class="fas fa-user-plus"></i>
                    </div>
                    <h1 class="register-title">إنشاء حساب جديد</h1>
                    <p class="register-subtitle">انضم إلى نظام InvoiceFlow Pro</p>
                </div>
                
                {get_flashed_messages_html()}
                
                <form class="register-form" method="POST" action="{url_for('register')}">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-user"></i>
                                اسم المستخدم *
                            </label>
                            <input type="text" name="username" class="form-control" 
                                   placeholder="اختر اسم مستخدم فريد" required>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-envelope"></i>
                                البريد الإلكتروني *
                            </label>
                            <input type="email" name="email" class="form-control" 
                                   placeholder="example@email.com" required>
                        </div>
                    </div>
                    
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-id-card"></i>
                                الاسم الكامل
                            </label>
                            <input type="text" name="full_name" class="form-control" 
                                   placeholder="الاسم الثلاثي">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-building"></i>
                                اسم الشركة
                            </label>
                            <input type="text" name="company_name" class="form-control" 
                                   placeholder="اسم شركتك">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">
                            <i class="fas fa-phone"></i>
                            رقم الهاتف
                        </label>
                        <input type="tel" name="phone" class="form-control" 
                               placeholder="+966 5X XXX XXXX">
                    </div>
                    
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-lock"></i>
                                كلمة المرور *
                            </label>
                            <input type="password" name="password" id="password" class="form-control" 
                                   placeholder="6 أحرف على الأقل" required>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-lock"></i>
                                تأكيد كلمة المرور *
                            </label>
                            <input type="password" name="confirm_password" id="confirmPassword" class="form-control" 
                                   placeholder="أعد إدخال كلمة المرور" required>
                        </div>
                    </div>
                    
                    <button type="submit" class="register-button">
                        <i class="fas fa-user-plus"></i>
                        إنشاء الحساب
                    </button>
                </form>
                
                <div class="register-footer">
                    <p>
                        لديك حساب بالفعل؟ 
                        <a href="{url_for('login')}">سجل الدخول</a>
                    </p>
                    <p class="mt-2 text-xs">
                        © 2024 InvoiceFlow Pro. جميع الحقوق محفوظة.
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            // إضافة تأثير عند التحميل
            document.addEventListener('DOMContentLoaded', function() {{
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {{
                    document.body.style.opacity = '1';
                }}, 100);
            }});
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)

@app.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم المحسنة"""
    user_id = session['user_id']
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    # إحصائيات المستخدم
    stats = {
        'total_invoices': db.execute_query(
            "SELECT COUNT(*) FROM invoices WHERE user_id = ?", 
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0,
        
        'total_revenue': db.execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE user_id = ? AND status = 'paid'", 
            (user_id,), fetchone=True
        )['COALESCE(SUM(total_amount), 0)'] or 0,
        
        'pending_invoices': db.execute_query(
            "SELECT COUNT(*) FROM invoices WHERE user_id = ? AND status = 'pending'", 
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0,
        
        'total_clients': db.execute_query(
            "SELECT COUNT(*) FROM clients WHERE user_id = ?", 
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0,
    }
    
    # تحضير المحتوى
    content = f"""
    <div class="grid grid-4 gap-6 mb-6">
        <!-- البطاقات الإحصائية -->
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-file-invoice-dollar"></i>
            </div>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p class="stat-label">{t('total_invoices')}</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-dollar-sign"></i>
            </div>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p class="stat-label">{t('total_revenue')}</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="stat-number">{stats['pending_invoices']}</div>
            <p class="stat-label">{t('pending_invoices')}</p>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-number">{stats['total_clients']}</div>
            <p class="stat-label">{t('total_clients')}</p>
        </div>
    </div>
    
    <div class="grid grid-2 gap-6 mb-6">
        <!-- الإجراءات السريعة -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">{t('quick_actions')}</h3>
            </div>
            <div class="grid grid-2 gap-4">
                <a href="{url_for('create_invoice')}" class="btn btn-primary">
                    <i class="fas fa-plus-circle"></i>
                    {t('create_invoice')}
                </a>
                
                <a href="{url_for('clients')}" class="btn btn-outline">
                    <i class="fas fa-user-plus"></i>
                    {t('add_client')}
                </a>
                
                <a href="{url_for('products')}" class="btn btn-outline">
                    <i class="fas fa-box"></i>
                    {t('add_product')}
                </a>
                
                <a href="{url_for('reports')}" class="btn btn-outline">
                    <i class="fas fa-chart-bar"></i>
                    {t('view_reports')}
                </a>
            </div>
        </div>
        
        <!-- نظرة سريعة -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">{t('quick_overview')}</h3>
            </div>
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <span class="text-muted">{t('invoices_this_month')}:</span>
                    <span class="font-bold">0</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">{t('revenue_this_month')}:</span>
                    <span class="font-bold text-success">$0</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">{t('new_clients')}:</span>
                    <span class="font-bold">0</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- معلومات النظام -->
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">{t('system_info')}</h3>
        </div>
        <div class="p-6">
            <div class="grid grid-3 gap-4">
                <div class="text-center">
                    <i class="fas fa-cube text-3xl text-primary mb-2"></i>
                    <p class="font-bold">InvoiceFlow Pro</p>
                    <p class="text-sm text-muted">v1.0.0</p>
                </div>
                <div class="text-center">
                    <i class="fas fa-language text-3xl text-secondary mb-2"></i>
                    <p class="font-bold">{t('language')}</p>
                    <p class="text-sm text-muted">{t('arabic') if lang == 'ar' else t('english')}</p>
                </div>
                <div class="text-center">
                    <i class="fas fa-database text-3xl text-accent mb-2"></i>
                    <p class="font-bold">{t('database')}</p>
                    <p class="text-sm text-muted">SQLite</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('dashboard')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                /* تنسيقات لوحة التحكم */
                .dashboard-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: var(--space-6);
                }}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    transition: all var(--transition-normal);
                    position: relative;
                    overflow: hidden;
                }}
                
                .card:hover {{
                    transform: translateY(-4px);
                    box-shadow: var(--shadow-2xl);
                    border-color: rgba(37, 99, 235, 0.3);
                }}
                
                .card-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: var(--space-6);
                    padding-bottom: var(--space-4);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .card-title {{
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--dark-text);
                }}
                
                .stat-card {{
                    text-align: center;
                    padding: var(--space-8) var(--space-6);
                    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
                    border: 1px solid rgba(255, 255, 255, 0.05);
                }}
                
                .stat-icon {{
                    width: 64px;
                    height: 64px;
                    border-radius: var(--radius-full);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto var(--space-4);
                    font-size: 1.5rem;
                    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                    color: white;
                    box-shadow: var(--shadow-primary);
                }}
                
                .stat-number {{
                    font-size: 2.5rem;
                    font-weight: 800;
                    margin-bottom: var(--space-2);
                    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .stat-label {{
                    font-size: 0.875rem;
                    color: var(--dark-text-secondary);
                    margin-bottom: var(--space-3);
                }}
                
                .grid {{
                    display: grid;
                    gap: var(--space-6);
                }}
                
                .grid-1 {{ grid-template-columns: repeat(1, 1fr); }}
                .grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
                .grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
                .grid-4 {{ grid-template-columns: repeat(4, 1fr); }}
                
                .btn {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: var(--space-2);
                    padding: var(--space-3) var(--space-6);
                    border-radius: var(--radius-lg);
                    font-weight: 500;
                    text-decoration: none;
                    transition: all var(--transition-fast);
                    border: none;
                    cursor: pointer;
                    font-size: 0.875rem;
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                    color: white;
                    box-shadow: var(--shadow-primary);
                }}
                
                .btn-primary:hover {{
                    background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
                    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
                }}
                
                .btn-outline {{
                    background: transparent;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    color: var(--dark-text-secondary);
                }}
                
                .btn-outline:hover {{
                    border-color: var(--primary-color);
                    color: var(--primary-color);
                    background: rgba(37, 99, 235, 0.05);
                }}
                
                .space-y-4 > * + * {{
                    margin-top: var(--space-4);
                }}
                
                .flex {{
                    display: flex;
                }}
                
                .items-center {{
                    align-items: center;
                }}
                
                .justify-between {{
                    justify-content: space-between;
                }}
                
                .text-muted {{
                    color: var(--dark-text-secondary);
                }}
                
                .font-bold {{
                    font-weight: 700;
                }}
                
                .font-medium {{
                    font-weight: 500;
                }}
                
                .text-success {{
                    color: var(--success-color);
                }}
                
                .text-primary {{
                    color: var(--primary-color);
                }}
                
                .text-secondary {{
                    color: var(--secondary-color);
                }}
                
                .text-accent {{
                    color: var(--accent-color);
                }}
                
                .text-center {{
                    text-align: center;
                }}
                
                .mb-6 {{
                    margin-bottom: var(--space-6);
                }}
                
                @media (max-width: 768px) {{
                    .grid-2, .grid-3, .grid-4 {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('dashboard')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <span style="color: var(--dark-text-secondary);">
                                <i class="fas fa-user"></i> {session.get('username', 'User')}
                            </span>
                            <a href="{url_for('logout')}" style="padding: var(--space-2) var(--space-4); background: rgba(239, 68, 68, 0.1); color: var(--danger-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-sign-out-alt"></i> {t('logout')}
                            </a>
                        </div>
                    </div>
                    
                    <!-- قائمة التنقل -->
                    <div style="display: flex; gap: var(--space-2); margin-top: var(--space-4); flex-wrap: wrap;">
                        <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                            <i class="fas fa-tachometer-alt"></i> {t('dashboard')}
                        </a>
                        <a href="{url_for('clients')}" style="padding: var(--space-2) var(--space-4); color: var(--dark-text-secondary); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                            <i class="fas fa-users"></i> {t('clients')}
                        </a>
                        <a href="{url_for('products')}" style="padding: var(--space-2) var(--space-4); color: var(--dark-text-secondary); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                            <i class="fas fa-box"></i> {t('products')}
                        </a>
                        <a href="{url_for('reports')}" style="padding: var(--space-2) var(--space-4); color: var(--dark-text-secondary); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                            <i class="fas fa-chart-bar"></i> {t('reports')}
                        </a>
                        <a href="{url_for('ai_insights')}" style="padding: var(--space-2) var(--space-4); color: var(--dark-text-secondary); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                            <i class="fas fa-robot"></i> {t('ai_insights')}
                        </a>
                        <a href="{url_for('settings')}" style="padding: var(--space-2) var(--space-4); color: var(--dark-text-secondary); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                            <i class="fas fa-cog"></i> {t('settings')}
                        </a>
                    </div>
                </nav>
                
                <!-- رسائل التنبيه -->
                {get_flashed_messages_html()}
                
                <!-- محتوى لوحة التحكم -->
                {content}
            </div>
        </body>
        </html>
        """
    )

@app.route('/create-invoice')
@login_required
def create_invoice():
    """إنشاء فاتورة"""
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    content = f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">{t('create_invoice')}</h2>
            <p class="text-muted">{t('create_new_invoice_description')}</p>
        </div>
        <div class="p-6">
            <div style="text-align: center; padding: var(--space-12) 0;">
                <i class="fas fa-file-invoice-dollar text-4xl text-primary mb-4"></i>
                <h3 class="text-xl font-bold mb-2">{t('feature_coming_soon')}</h3>
                <p class="text-muted mb-6">{t('invoice_creation_coming_soon')}</p>
                <a href="{url_for('dashboard')}" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                </a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('create_invoice')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .card-header {{
                    margin-bottom: var(--space-6);
                    padding-bottom: var(--space-4);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .card-title {{
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--dark-text);
                }}
                
                .text-muted {{
                    color: var(--dark-text-secondary);
                }}
                
                .text-primary {{
                    color: var(--primary-color);
                }}
                
                .text-xl {{
                    font-size: 1.25rem;
                }}
                
                .font-bold {{
                    font-weight: 700;
                }}
                
                .mb-2 {{
                    margin-bottom: var(--space-2);
                }}
                
                .mb-4 {{
                    margin-bottom: var(--space-4);
                }}
                
                .mb-6 {{
                    margin-bottom: var(--space-6);
                }}
                
                .p-6 {{
                    padding: var(--space-6);
                }}
                
                .text-center {{
                    text-align: center;
                }}
                
                .btn {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: var(--space-2);
                    padding: var(--space-3) var(--space-6);
                    border-radius: var(--radius-lg);
                    font-weight: 500;
                    text-decoration: none;
                    transition: all var(--transition-fast);
                    border: none;
                    cursor: pointer;
                    font-size: 0.875rem;
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                    color: white;
                    box-shadow: var(--shadow-primary);
                }}
                
                .btn-primary:hover {{
                    background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
                    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
                }}
            </style>
        </head>
        <body>
            <div style="max-width: 1200px; margin: 0 auto; padding: var(--space-6);">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('create_invoice')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                            </a>
                        </div>
                    </div>
                </nav>
                
                <!-- المحتوى -->
                {content}
            </div>
        </body>
        </html>
        """
    )

# ================== الصفحات الأساسية ==================
@app.route('/clients')
@login_required
def clients():
    """صفحة العملاء"""
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    content = f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">{t('clients')}</h2>
            <p class="text-muted">{t('manage_your_clients')}</p>
        </div>
        <div class="p-6">
            <div style="text-align: center; padding: var(--space-12) 0;">
                <i class="fas fa-users text-4xl text-primary mb-4"></i>
                <h3 class="text-xl font-bold mb-2">{t('feature_coming_soon')}</h3>
                <p class="text-muted mb-6">{t('clients_management_coming_soon')}</p>
                <a href="{url_for('dashboard')}" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                </a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('clients')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .card-header {{
                    margin-bottom: var(--space-6);
                    padding-bottom: var(--space-4);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .card-title {{
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--dark-text);
                }}
                
                .btn {{
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    gap: var(--space-2);
                    padding: var(--space-3) var(--space-6);
                    border-radius: var(--radius-lg);
                    font-weight: 500;
                    text-decoration: none;
                    transition: all var(--transition-fast);
                    border: none;
                    cursor: pointer;
                    font-size: 0.875rem;
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                    color: white;
                    box-shadow: var(--shadow-primary);
                }}
            </style>
        </head>
        <body>
            <div style="max-width: 1200px; margin: 0 auto; padding: var(--space-6);">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('clients')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                            </a>
                        </div>
                    </div>
                </nav>
                
                <!-- المحتوى -->
                {content}
            </div>
        </body>
        </html>
        """
    )

@app.route('/products')
@login_required
def products():
    """صفحة المنتجات"""
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    content = f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">{t('products')}</h2>
            <p class="text-muted">{t('manage_products_and_services')}</p>
        </div>
        <div class="p-6">
            <div style="text-align: center; padding: var(--space-12) 0;">
                <i class="fas fa-box text-4xl text-primary mb-4"></i>
                <h3 class="text-xl font-bold mb-2">{t('feature_coming_soon')}</h3>
                <p class="text-muted mb-6">{t('products_management_coming_soon')}</p>
                <a href="{url_for('dashboard')}" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                </a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('products')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    max-width: 800px;
                    margin: 0 auto;
                }}
                
                .card-header {{
                    margin-bottom: var(--space-6);
                    padding-bottom: var(--space-4);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
            </style>
        </head>
        <body>
            <div style="max-width: 1200px; margin: 0 auto; padding: var(--space-6);">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('products')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                            </a>
                        </div>
                    </div>
                </nav>
                
                <!-- المحتوى -->
                {content}
            </div>
        </body>
        </html>
        """
    )

@app.route('/reports')
@login_required
def reports():
    """صفحة التقارير"""
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    content = f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">{t('reports')}</h2>
            <p class="text-muted">{t('analytics_and_insights')}</p>
        </div>
        <div class="p-6">
            <div style="text-align: center; padding: var(--space-12) 0;">
                <i class="fas fa-chart-bar text-4xl text-primary mb-4"></i>
                <h3 class="text-xl font-bold mb-2">{t('feature_coming_soon')}</h3>
                <p class="text-muted mb-6">{t('reports_coming_soon')}</p>
                <a href="{url_for('dashboard')}" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                </a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('reports')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    max-width: 800px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div style="max-width: 1200px; margin: 0 auto; padding: var(--space-6);">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('reports')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                            </a>
                        </div>
                    </div>
                </nav>
                
                <!-- المحتوى -->
                {content}
            </div>
        </body>
        </html>
        """
    )

@app.route('/ai-insights')
@login_required
def ai_insights():
    """صفحة الذكاء الاصطناعي"""
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    content = f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">{t('ai_insights')}</h2>
            <p class="text-muted">{t('smart_analytics_and_predictions')}</p>
        </div>
        <div class="p-6">
            <div style="text-align: center; padding: var(--space-12) 0;">
                <i class="fas fa-robot text-4xl text-primary mb-4"></i>
                <h3 class="text-xl font-bold mb-2">{t('feature_coming_soon')}</h3>
                <p class="text-muted mb-6">{t('ai_insights_coming_soon')}</p>
                <a href="{url_for('dashboard')}" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                </a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('ai_insights')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    max-width: 800px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div style="max-width: 1200px; margin: 0 auto; padding: var(--space-6);">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('ai_insights')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                            </a>
                        </div>
                    </div>
                </nav>
                
                <!-- المحتوى -->
                {content}
            </div>
        </body>
        </html>
        """
    )

@app.route('/settings')
@login_required
def settings():
    """صفحة الإعدادات"""
    lang = session.get('language', 'ar')
    t = lambda key: multilang.get_text(key, lang)
    
    content = f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">{t('settings')}</h2>
            <p class="text-muted">{t('configure_your_system')}</p>
        </div>
        <div class="p-6">
            <div style="text-align: center; padding: var(--space-12) 0;">
                <i class="fas fa-cog text-4xl text-primary mb-4"></i>
                <h3 class="text-xl font-bold mb-2">{t('feature_coming_soon')}</h3>
                <p class="text-muted mb-6">{t('settings_coming_soon')}</p>
                <a href="{url_for('dashboard')}" class="btn btn-primary">
                    <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                </a>
            </div>
        </div>
    </div>
    """
    
    return render_template_string(
        f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="{lang}">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>InvoiceFlow Pro - {t('settings')}</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                {BASE_CSS}
                
                .card {{
                    background: var(--dark-card);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--radius-xl);
                    padding: var(--space-6);
                    max-width: 800px;
                    margin: 0 auto;
                }}
            </style>
        </head>
        <body>
            <div style="max-width: 1200px; margin: 0 auto; padding: var(--space-6);">
                <!-- شريط التنقل -->
                <nav style="margin-bottom: var(--space-6); padding: var(--space-4); background: var(--dark-card); border-radius: var(--radius-xl); border: 1px solid rgba(255, 255, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--primary-color), var(--accent-color)); border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; color: white;">
                                <i class="fas fa-file-invoice-dollar"></i>
                            </div>
                            <div>
                                <h1 style="font-size: 1.25rem; font-weight: 700;">InvoiceFlow Pro</h1>
                                <p style="font-size: 0.875rem; color: var(--dark-text-secondary);">{t('settings')}</p>
                            </div>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: var(--space-4);">
                            <a href="{url_for('dashboard')}" style="padding: var(--space-2) var(--space-4); background: rgba(37, 99, 235, 0.1); color: var(--primary-color); border-radius: var(--radius-lg); text-decoration: none; font-size: 0.875rem;">
                                <i class="fas fa-arrow-right"></i> {t('back_to_dashboard')}
                            </a>
                        </div>
                    </div>
                </nav>
                
                <!-- المحتوى -->
                {content}
            </div>
        </body>
        </html>
        """
    )

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

# ================== API للغة ==================
@app.route('/api/set-language', methods=['POST'])
@login_required
def set_language():
    """تحديد اللغة"""
    try:
        data = request.get_json()
        lang = data.get('language', 'ar')
        
        if lang not in ['ar', 'en']:
            return jsonify({'success': False, 'error': 'لغة غير مدعومة'})
        
        # تحديث اللغة في الجلسة
        session['language'] = lang
        
        # تحديث اللغة في قاعدة البيانات
        db.execute_query(
            "UPDATE users SET language = ? WHERE id = ?",
            (lang, session['user_id'])
        )
        
        return jsonify({'success': True, 'language': lang})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ================== API للإشعارات ==================
@app.route('/api/notifications/mark-as-read', methods=['POST'])
@login_required
def mark_notification_as_read():
    """تحديد إشعار كمقروء"""
    try:
        data = request.get_json()
        notification_id = data.get('id')
        
        if not notification_id:
            return jsonify({'success': False, 'error': 'معرف الإشعار مطلوب'})
        
        NotificationSystem.mark_as_read(notification_id)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications/mark-all-as-read', methods=['POST'])
@login_required
def mark_all_notifications_as_read():
    """تحديد جميع الإشعارات كمقروءة"""
    try:
        NotificationSystem.mark_all_as_read(session['user_id'])
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ================== تشغيل التطبيق ==================
if __name__ == '__main__':
    try:
        print("\n" + "="*80)
        print("🚀 InvoiceFlow Pro - النظام الاحترافي المتكامل")
        print("="*80)
        print("✅ النظام جاهز للعمل!")
        print(f"🌐 الخادم يعمل على: http://0.0.0.0:{port}")
        print(f"📊 قاعدة البيانات: {app.config['DATABASE_PATH']}")
        print("\n📋 المسارات المتاحة:")
        print("🔹 / - الصفحة الرئيسية")
        print("🔹 /login - تسجيل الدخول")
        print("🔹 /register - إنشاء حساب")
        print("🔹 /dashboard - لوحة التحكم")
        print("🔹 /create-invoice - إنشاء فاتورة")
        print("🔹 /clients - إدارة العملاء")
        print("🔹 /products - المنتجات والخدمات")
        print("🔹 /reports - التقارير والإحصائيات")
        print("🔹 /ai-insights - الذكاء الاصطناعي")
        print("🔹 /settings - الإعدادات")
        print("🔹 /logout - تسجيل الخروج")
        print("\n🔧 واجهات API:")
        print("🔹 /api/set-language - تحديث اللغة")
        print("🔹 /api/notifications/* - إدارة الإشعارات")
        print("\n👑 فريق العمل المحترف - النسخة الاحترافية")
        print("="*80)
        
        # تشغيل الخادم
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        import traceback
        traceback.print_exc()
