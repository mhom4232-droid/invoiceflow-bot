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

# ================== نظام التصميم المحسن ==================
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
    
    .container {
        padding-left: var(--space-4);
        padding-right: var(--space-4);
    }
}

@media (max-width: 480px) {
    :root {
        --space-4: 0.75rem;
        --space-6: 1rem;
    }
}

/* ================== تنسيق النصوص العربية ================== */
.arabic-text {
    font-family: 'Tajawal', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.8;
    letter-spacing: 0;
}

.ltr-text {
    direction: ltr;
    text-align: left;
}

/* ================== فئات المساعدة ================== */
.fade-in {
    animation: fadeIn var(--transition-normal);
}

.slide-in-right {
    animation: slideInRight var(--transition-normal);
}

.slide-in-left {
    animation: slideInLeft var(--transition-normal);
}

.pulse {
    animation: pulse 2s infinite;
}

.spin {
    animation: spin 1s linear infinite;
}

.shimmer {
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

.float {
    animation: float 3s ease-in-out infinite;
}

.bounce {
    animation: bounce 0.5s ease infinite;
}

.scale-in {
    animation: scaleIn var(--transition-normal);
}

.gradient-animation {
    background-size: 200% 200%;
    animation: gradient 3s ease infinite;
}

.hidden {
    display: none !important;
}

.visible {
    display: block !important;
}

.text-center {
    text-align: center !important;
}

.text-right {
    text-align: right !important;
}

.text-left {
    text-align: left !important;
}

.flex {
    display: flex !important;
}

.flex-col {
    flex-direction: column !important;
}

.flex-row {
    flex-direction: row !important;
}

.items-center {
    align-items: center !important;
}

.items-start {
    align-items: flex-start !important;
}

.items-end {
    align-items: flex-end !important;
}

.justify-center {
    justify-content: center !important;
}

.justify-between {
    justify-content: space-between !important;
}

.justify-start {
    justify-content: flex-start !important;
}

.justify-end {
    justify-content: flex-end !important;
}

.flex-wrap {
    flex-wrap: wrap !important;
}

.flex-nowrap {
    flex-wrap: nowrap !important;
}

.flex-1 {
    flex: 1 1 0% !important;
}

.flex-auto {
    flex: 1 1 auto !important;
}

.gap-1 { gap: var(--space-1) !important; }
.gap-2 { gap: var(--space-2) !important; }
.gap-3 { gap: var(--space-3) !important; }
.gap-4 { gap: var(--space-4) !important; }
.gap-5 { gap: var(--space-5) !important; }
.gap-6 { gap: var(--space-6) !important; }
.gap-8 { gap: var(--space-8) !important; }

.w-full { width: 100% !important; }
.w-screen { width: 100vw !important; }
.h-full { height: 100% !important; }
.h-screen { height: 100vh !important; }
.min-h-screen { min-height: 100vh !important; }

.m-1 { margin: var(--space-1) !important; }
.m-2 { margin: var(--space-2) !important; }
.m-3 { margin: var(--space-3) !important; }
.m-4 { margin: var(--space-4) !important; }
.m-5 { margin: var(--space-5) !important; }
.m-6 { margin: var(--space-6) !important; }

.mt-1 { margin-top: var(--space-1) !important; }
.mt-2 { margin-top: var(--space-2) !important; }
.mt-3 { margin-top: var(--space-3) !important; }
.mt-4 { margin-top: var(--space-4) !important; }
.mt-5 { margin-top: var(--space-5) !important; }
.mt-6 { margin-top: var(--space-6) !important; }
.mt-8 { margin-top: var(--space-8) !important; }
.mt-10 { margin-top: var(--space-10) !important; }

.mb-1 { margin-bottom: var(--space-1) !important; }
.mb-2 { margin-bottom: var(--space-2) !important; }
.mb-3 { margin-bottom: var(--space-3) !important; }
.mb-4 { margin-bottom: var(--space-4) !important; }
.mb-5 { margin-bottom: var(--space-5) !important; }
.mb-6 { margin-bottom: var(--space-6) !important; }
.mb-8 { margin-bottom: var(--space-8) !important; }
.mb-10 { margin-bottom: var(--space-10) !important; }

.mr-1 { margin-right: var(--space-1) !important; }
.mr-2 { margin-right: var(--space-2) !important; }
.mr-3 { margin-right: var(--space-3) !important; }
.mr-4 { margin-right: var(--space-4) !important; }
.mr-5 { margin-right: var(--space-5) !important; }
.mr-6 { margin-right: var(--space-6) !important; }

.ml-1 { margin-left: var(--space-1) !important; }
.ml-2 { margin-left: var(--space-2) !important; }
.ml-3 { margin-left: var(--space-3) !important; }
.ml-4 { margin-left: var(--space-4) !important; }
.ml-5 { margin-left: var(--space-5) !important; }
.ml-6 { margin-left: var(--space-6) !important; }

.p-1 { padding: var(--space-1) !important; }
.p-2 { padding: var(--space-2) !important; }
.p-3 { padding: var(--space-3) !important; }
.p-4 { padding: var(--space-4) !important; }
.p-5 { padding: var(--space-5) !important; }
.p-6 { padding: var(--space-6) !important; }
.p-8 { padding: var(--space-8) !important; }

.pt-1 { padding-top: var(--space-1) !important; }
.pt-2 { padding-top: var(--space-2) !important; }
.pt-3 { padding-top: var(--space-3) !important; }
.pt-4 { padding-top: var(--space-4) !important; }
.pt-5 { padding-top: var(--space-5) !important; }
.pt-6 { padding-top: var(--space-6) !important; }

.pb-1 { padding-bottom: var(--space-1) !important; }
.pb-2 { padding-bottom: var(--space-2) !important; }
.pb-3 { padding-bottom: var(--space-3) !important; }
.pb-4 { padding-bottom: var(--space-4) !important; }
.pb-5 { padding-bottom: var(--space-5) !important; }
.pb-6 { padding-bottom: var(--space-6) !important; }

.pr-1 { padding-right: var(--space-1) !important; }
.pr-2 { padding-right: var(--space-2) !important; }
.pr-3 { padding-right: var(--space-3) !important; }
.pr-4 { padding-right: var(--space-4) !important; }
.pr-5 { padding-right: var(--space-5) !important; }
.pr-6 { padding-right: var(--space-6) !important; }

.pl-1 { padding-left: var(--space-1) !important; }
.pl-2 { padding-left: var(--space-2) !important; }
.pl-3 { padding-left: var(--space-3) !important; }
.pl-4 { padding-left: var(--space-4) !important; }
.pl-5 { padding-left: var(--space-5) !important; }
.pl-6 { padding-left: var(--space-6) !important; }

.rounded-sm { border-radius: var(--radius-sm) !important; }
.rounded-md { border-radius: var(--radius-md) !important; }
.rounded-lg { border-radius: var(--radius-lg) !important; }
.rounded-xl { border-radius: var(--radius-xl) !important; }
.rounded-2xl { border-radius: var(--radius-2xl) !important; }
.rounded-full { border-radius: var(--radius-full) !important; }

.shadow-sm { box-shadow: var(--shadow-sm) !important; }
.shadow-md { box-shadow: var(--shadow-md) !important; }
.shadow-lg { box-shadow: var(--shadow-lg) !important; }
.shadow-xl { box-shadow: var(--shadow-xl) !important; }
.shadow-2xl { box-shadow: var(--shadow-2xl) !important; }

.shadow-primary { box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3) !important; }
.shadow-secondary { box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3) !important; }
.shadow-accent { box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3) !important; }

.bg-primary { background-color: var(--primary-color) !important; }
.bg-primary-dark { background-color: var(--primary-dark) !important; }
.bg-primary-light { background-color: var(--primary-light) !important; }
.bg-secondary { background-color: var(--secondary-color) !important; }
.bg-accent { background-color: var(--accent-color) !important; }
.bg-danger { background-color: var(--danger-color) !important; }
.bg-warning { background-color: var(--warning-color) !important; }
.bg-info { background-color: var(--info-color) !important; }
.bg-success { background-color: var(--success-color) !important; }

.bg-dark { background-color: var(--dark-bg) !important; }
.bg-dark-card { background-color: var(--dark-card) !important; }

.bg-gradient-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color)) !important;
}

.bg-gradient-secondary {
    background: linear-gradient(135deg, var(--secondary-color), var(--accent-color)) !important;
}

.bg-gradient-dark {
    background: linear-gradient(135deg, var(--dark-bg), var(--dark-card)) !important;
}

.border {
    border: 1px solid var(--dark-border) !important;
}

.border-primary { border-color: var(--primary-color) !important; }
.border-secondary { border-color: var(--secondary-color) !important; }
.border-danger { border-color: var(--danger-color) !important; }
.border-warning { border-color: var(--warning-color) !important; }
.border-success { border-color: var(--success-color) !important; }

.text-primary { color: var(--primary-color) !important; }
.text-secondary { color: var(--secondary-color) !important; }
.text-accent { color: var(--accent-color) !important; }
.text-danger { color: var(--danger-color) !important; }
.text-warning { color: var(--warning-color) !important; }
.text-info { color: var(--info-color) !important; }
.text-success { color: var(--success-color) !important; }
.text-white { color: white !important; }
.text-dark { color: var(--dark-text) !important; }
.text-muted { color: var(--dark-text-secondary) !important; }

.text-xs { font-size: 0.75rem !important; }
.text-sm { font-size: 0.875rem !important; }
.text-base { font-size: 1rem !important; }
.text-lg { font-size: 1.125rem !important; }
.text-xl { font-size: 1.25rem !important; }
.text-2xl { font-size: 1.5rem !important; }
.text-3xl { font-size: 1.875rem !important; }
.text-4xl { font-size: 2.25rem !important; }
.text-5xl { font-size: 3rem !important; }

.font-light { font-weight: 300 !important; }
.font-normal { font-weight: 400 !important; }
.font-medium { font-weight: 500 !important; }
.font-semibold { font-weight: 600 !important; }
.font-bold { font-weight: 700 !important; }
.font-extrabold { font-weight: 800 !important; }

.leading-tight { line-height: 1.25 !important; }
.leading-normal { line-height: 1.5 !important; }
.leading-relaxed { line-height: 1.625 !important; }
.leading-loose { line-height: 2 !important; }

.tracking-tight { letter-spacing: -0.025em !important; }
.tracking-normal { letter-spacing: 0 !important; }
.tracking-wide { letter-spacing: 0.025em !important; }

.opacity-0 { opacity: 0 !important; }
.opacity-25 { opacity: 0.25 !important; }
.opacity-50 { opacity: 0.5 !important; }
.opacity-75 { opacity: 0.75 !important; }
.opacity-100 { opacity: 1 !important; }

.cursor-pointer { cursor: pointer !important; }
.cursor-default { cursor: default !important; }
.cursor-not-allowed { cursor: not-allowed !important; }

.select-none { user-select: none !important; }
.select-text { user-select: text !important; }

.overflow-hidden { overflow: hidden !important; }
.overflow-auto { overflow: auto !important; }
.overflow-x-auto { overflow-x: auto !important; }
.overflow-y-auto { overflow-y: auto !important; }

.whitespace-nowrap { white-space: nowrap !important; }
.whitespace-pre-wrap { white-space: pre-wrap !important; }

.truncate {
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

.break-words { word-wrap: break-word !important; }
.break-all { word-break: break-all !important; }

.z-0 { z-index: 0 !important; }
.z-10 { z-index: 10 !important; }
.z-20 { z-index: 20 !important; }
.z-30 { z-index: 30 !important; }
.z-40 { z-index: 40 !important; }
.z-50 { z-index: 50 !important; }
.z-auto { z-index: auto !important; }

.transition-all {
    transition-property: all !important;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important;
    transition-duration: 300ms !important;
}

.transition-colors {
    transition-property: background-color, border-color, color, fill, stroke !important;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important;
    transition-duration: 300ms !important;
}

.transition-transform {
    transition-property: transform !important;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important;
    transition-duration: 300ms !important;
}

.transition-opacity {
    transition-property: opacity !important;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important;
    transition-duration: 300ms !important;
}

.ease-in { transition-timing-function: cubic-bezier(0.4, 0, 1, 1) !important; }
.ease-out { transition-timing-function: cubic-bezier(0, 0, 0.2, 1) !important; }
.ease-in-out { transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1) !important; }

.duration-75 { transition-duration: 75ms !important; }
.duration-100 { transition-duration: 100ms !important; }
.duration-150 { transition-duration: 150ms !important; }
.duration-200 { transition-duration: 200ms !important; }
.duration-300 { transition-duration: 300ms !important; }
.duration-500 { transition-duration: 500ms !important; }
.duration-700 { transition-duration: 700ms !important; }
.duration-1000 { transition-duration: 1000ms !important; }
"""

# ================== تنسيقات لوحة التحكم ==================
DASHBOARD_CSS = """
/* ================== تصميم لوحة التحكم ================== */
.dashboard-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    min-height: 100vh;
    background: linear-gradient(135deg, var(--dark-bg) 0%, #1a202c 100%);
}

/* الشريط الجانبي */
.sidebar {
    background: linear-gradient(180deg, var(--dark-card) 0%, rgba(30, 41, 59, 0.95) 100%);
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    padding: var(--space-6) 0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
    z-index: 40;
}

.sidebar::-webkit-scrollbar {
    width: 6px;
}

.sidebar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-full);
}

.sidebar-header {
    padding: 0 var(--space-6) var(--space-6);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: var(--space-6);
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-6);
}

.sidebar-brand-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: white;
    box-shadow: var(--shadow-primary);
}

.sidebar-brand-text h2 {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-brand-text p {
    font-size: 0.75rem;
    color: var(--dark-text-secondary);
}

.sidebar-nav {
    padding: 0 var(--space-6);
}

.nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    margin-bottom: var(--space-2);
    border-radius: var(--radius-lg);
    color: var(--dark-text-secondary);
    text-decoration: none;
    transition: all var(--transition-fast);
    position: relative;
    overflow: hidden;
}

.nav-item::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 3px;
    height: 0;
    background: linear-gradient(180deg, var(--primary-color), var(--accent-color));
    border-radius: 0 var(--radius-full) var(--radius-full) 0;
    transition: height var(--transition-normal);
}

.nav-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--dark-text);
    transform: translateX(-5px);
}

.nav-item:hover::before {
    height: 100%;
}

.nav-item.active {
    background: rgba(37, 99, 235, 0.1);
    color: var(--primary-color);
    font-weight: 500;
}

.nav-item.active::before {
    height: 100%;
}

.nav-item .nav-icon {
    width: 20px;
    text-align: center;
    font-size: 1.125rem;
    transition: transform var(--transition-normal);
}

.nav-item:hover .nav-icon {
    transform: scale(1.1);
}

.nav-item .nav-badge {
    margin-right: auto;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: var(--radius-full);
    background: rgba(239, 68, 68, 0.2);
    color: var(--danger-color);
}

/* المحتوى الرئيسي */
.main-content {
    overflow-y: auto;
    max-height: 100vh;
    padding: var(--space-6);
}

.navbar {
    background: var(--dark-card);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: var(--space-4) var(--space-6);
    position: sticky;
    top: 0;
    z-index: 50;
    margin-bottom: var(--space-6);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
}

.navbar-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
}

.navbar-title h1 {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.navbar-title p {
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
    margin-top: var(--space-1);
}

.navbar-actions {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.notification-btn {
    position: relative;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--dark-text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
}

.notification-btn:hover {
    background: rgba(37, 99, 235, 0.1);
    color: var(--primary-color);
    border-color: rgba(37, 99, 235, 0.3);
}

.notification-badge {
    position: absolute;
    top: -2px;
    right: -2px;
    width: 18px;
    height: 18px;
    background: linear-gradient(135deg, var(--danger-color), #dc2626);
    color: white;
    font-size: 0.75rem;
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.time-display {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-full);
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
}

.time-display i {
    color: var(--primary-color);
}

/* الكروت */
.card {
    background: var(--dark-card);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    transition: all var(--transition-normal);
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.02), transparent);
    transform: translateX(-100%);
    transition: transform 0.6s ease;
}

.card:hover::before {
    transform: translateX(100%);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-2xl);
    border-color: rgba(37, 99, 235, 0.3);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--dark-text);
}

.card-subtitle {
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
    margin-top: var(--space-1);
}

.card-actions {
    display: flex;
    gap: var(--space-2);
}

/* الشبكات */
.grid {
    display: grid;
    gap: var(--space-6);
}

.grid-1 { grid-template-columns: repeat(1, 1fr); }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-5 { grid-template-columns: repeat(5, 1fr); }
.grid-6 { grid-template-columns: repeat(6, 1fr); }

/* الأزرار */
.btn {
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
    position: relative;
    overflow: hidden;
}

.btn::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.btn:hover::before {
    width: 300px;
    height: 300px;
}

.btn:active {
    transform: scale(0.98);
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    box-shadow: var(--shadow-primary);
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
}

.btn-secondary {
    background: linear-gradient(135deg, var(--secondary-color), var(--secondary-dark));
    color: white;
    box-shadow: var(--shadow-secondary);
}

.btn-success {
    background: linear-gradient(135deg, var(--success-color), #059669);
    color: white;
}

.btn-danger {
    background: linear-gradient(135deg, var(--danger-color), #dc2626);
    color: white;
}

.btn-warning {
    background: linear-gradient(135deg, var(--warning-color), #d97706);
    color: white;
}

.btn-accent {
    background: linear-gradient(135deg, var(--accent-color), #7c3aed);
    color: white;
    box-shadow: var(--shadow-accent);
}

.btn-outline {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: var(--dark-text-secondary);
}

.btn-outline:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
    background: rgba(37, 99, 235, 0.05);
}

.btn-sm {
    padding: var(--space-2) var(--space-4);
    font-size: 0.75rem;
}

.btn-lg {
    padding: var(--space-4) var(--space-8);
    font-size: 1rem;
}

.btn-icon {
    width: 40px;
    height: 40px;
    padding: 0;
    border-radius: var(--radius-full);
}

/* الجداول */
.table-container {
    overflow-x: auto;
    border-radius: var(--radius-lg);
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.02);
}

.table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    min-width: 800px;
}

.table thead {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(139, 92, 246, 0.1));
}

.table th {
    padding: var(--space-4) var(--space-6);
    text-align: right;
    font-weight: 600;
    color: var(--primary-color);
    border-bottom: 2px solid rgba(37, 99, 235, 0.2);
    white-space: nowrap;
}

.table td {
    padding: var(--space-4) var(--space-6);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--dark-text-secondary);
}

.table tbody tr {
    transition: all var(--transition-fast);
}

.table tbody tr:hover {
    background: rgba(255, 255, 255, 0.03);
    transform: translateX(-4px);
}

.table tbody tr:last-child td {
    border-bottom: none;
}

/* البطاقات الإحصائية */
.stat-card {
    text-align: center;
    padding: var(--space-8) var(--space-6);
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-icon {
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
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: var(--space-2);
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
    margin-bottom: var(--space-3);
}

.stat-change {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: 0.875rem;
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.stat-change.negative {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

/* الأشكال الهندسية */
.badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

.badge-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    color: white;
}

.badge-success {
    background: linear-gradient(135deg, var(--success-color), #059669);
    color: white;
}

.badge-warning {
    background: linear-gradient(135deg, var(--warning-color), #d97706);
    color: white;
}

.badge-danger {
    background: linear-gradient(135deg, var(--danger-color), #dc2626);
    color: white;
}

.badge-info {
    background: linear-gradient(135deg, var(--info-color), #2563eb);
    color: white;
}

.badge-outline {
    background: transparent;
    border: 1px solid currentColor;
    color: currentColor;
}

/* النماذج */
.form-group {
    margin-bottom: var(--space-6);
}

.form-label {
    display: block;
    margin-bottom: var(--space-2);
    font-weight: 500;
    color: var(--dark-text);
    font-size: 0.875rem;
}

.form-control {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    color: var(--dark-text);
    font-size: 0.875rem;
    transition: all var(--transition-fast);
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    background: rgba(255, 255, 255, 0.08);
}

.form-control::placeholder {
    color: var(--dark-text-secondary);
}

.form-control:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.form-text {
    display: block;
    margin-top: var(--space-1);
    font-size: 0.75rem;
    color: var(--dark-text-secondary);
}

.form-select {
    appearance: none;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%239ca3af' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
    background-position: left 0.5rem center;
    background-repeat: no-repeat;
    background-size: 1.5em 1.5em;
    padding-left: 2.5rem;
}

.form-check {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    cursor: pointer;
}

.form-check-input {
    width: 18px;
    height: 18px;
    border-radius: var(--radius-sm);
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.05);
    transition: all var(--transition-fast);
    appearance: none;
    position: relative;
}

.form-check-input:checked {
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    border-color: var(--primary-color);
}

.form-check-input:checked::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.form-check-label {
    font-size: 0.875rem;
    color: var(--dark-text);
}

/* شريط التقدم */
.progress {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-full);
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    border-radius: var(--radius-full);
    transition: width 1s ease;
}

/* الأدوات */
.tooltip {
    position: relative;
}

.tooltip-text {
    position: absolute;
    bottom: 100%;
    right: 50%;
    transform: translateX(50%);
    background: var(--dark-card);
    color: var(--dark-text);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-fast);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: var(--shadow-lg);
    z-index: 50;
    margin-bottom: var(--space-2);
}

.tooltip:hover .tooltip-text {
    opacity: 1;
    visibility: visible;
}

/* المودال */
.modal {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--space-4);
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-normal);
}

.modal.show {
    opacity: 1;
    visibility: visible;
}

.modal-content {
    background: var(--dark-card);
    border-radius: var(--radius-xl);
    padding: var(--space-8);
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    transform: scale(0.9);
    transition: transform var(--transition-normal);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: var(--shadow-2xl);
}

.modal.show .modal-content {
    transform: scale(1);
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--dark-text);
}

.modal-close {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: var(--dark-text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
}

.modal-close:hover {
    background: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

/* التنبيهات */
.alert {
    padding: var(--space-4) var(--space-6);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-4);
    border: 1px solid transparent;
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
}

.alert-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
    margin-top: 2px;
}

.alert-content {
    flex: 1;
}

.alert-title {
    font-weight: 600;
    margin-bottom: var(--space-1);
    color: inherit;
}

.alert-message {
    font-size: 0.875rem;
    color: inherit;
    opacity: 0.9;
}

.alert-success {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
    color: var(--success-color);
}

.alert-danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
    color: var(--danger-color);
}

.alert-warning {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.2);
    color: var(--warning-color);
}

.alert-info {
    background: rgba(37, 99, 235, 0.1);
    border-color: rgba(37, 99, 235, 0.2);
    color: var(--info-color);
}

/* الرسوم البيانية */
.chart-container {
    position: relative;
    height: 300px;
    width: 100%;
}

/* التحميل */
.loading {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
}

.loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* الصور */
.img-fluid {
    max-width: 100%;
    height: auto;
}

.img-thumbnail {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    padding: var(--space-2);
    background: rgba(255, 255, 255, 0.05);
}

/* التجاوب */
@media (max-width: 1024px) {
    .dashboard-layout {
        grid-template-columns: 1fr;
    }
    
    .sidebar {
        display: none;
    }
    
    .grid-3, .grid-4, .grid-5, .grid-6 {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .grid-2, .grid-3, .grid-4, .grid-5, .grid-6 {
        grid-template-columns: 1fr;
    }
    
    .navbar-content {
        flex-direction: column;
        align-items: stretch;
        gap: var(--space-3);
    }
    
    .navbar-actions {
        justify-content: space-between;
    }
    
    .main-content {
        padding: var(--space-4);
    }
}

@media (max-width: 480px) {
    .card {
        padding: var(--space-4);
    }
    
    .table th,
    .table td {
        padding: var(--space-3);
    }
    
    .btn {
        padding: var(--space-2) var(--space-4);
    }
}

/* تأثيرات خاصة */
.glass-effect {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.glow-effect {
    box-shadow: 0 0 20px rgba(37, 99, 235, 0.3);
}

.hover-lift:hover {
    transform: translateY(-4px);
    transition: transform var(--transition-normal);
}

.hover-scale:hover {
    transform: scale(1.05);
    transition: transform var(--transition-normal);
}

/* التحسينات للغة الإنجليزية */
[dir="ltr"] .sidebar {
    border-right: none;
    border-left: 1px solid rgba(255, 255, 255, 0.1);
}

[dir="ltr"] .nav-item::before {
    right: auto;
    left: 0;
    border-radius: var(--radius-full) 0 0 var(--radius-full);
}

[dir="ltr"] .nav-item:hover {
    transform: translateX(5px);
}

[dir="ltr"] .form-select {
    background-position: right 0.5rem center;
    padding-right: 2.5rem;
    padding-left: var(--space-4);
}

[dir="ltr"] .table th,
[dir="ltr"] .table td {
    text-align: left;
}

[dir="ltr"] .table tbody tr:hover {
    transform: translateX(4px);
}

/* إضافة تنسيقات للرموز */
.icon-xs { font-size: 0.75rem !important; }
.icon-sm { font-size: 1rem !important; }
.icon-md { font-size: 1.25rem !important; }
.icon-lg { font-size: 1.5rem !important; }
.icon-xl { font-size: 2rem !important; }
.icon-2xl { font-size: 3rem !important; }

/* تنسيقات إضافية */
.separator {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    margin: var(--space-6) 0;
}

.divider {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin: var(--space-4) 0;
}

.list-group {
    list-style: none;
    padding: 0;
}

.list-group-item {
    padding: var(--space-3) var(--space-4);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    transition: all var(--transition-fast);
}

.list-group-item:hover {
    background: rgba(255, 255, 255, 0.03);
}

.list-group-item:last-child {
    border-bottom: none;
}

.breadcrumb {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-bottom: var(--space-6);
}

.breadcrumb-item {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
}

.breadcrumb-item.active {
    color: var(--primary-color);
}

.breadcrumb-divider {
    color: var(--dark-text-secondary);
    opacity: 0.5;
}

/* تحسينات للأقسام */
.section {
    margin-bottom: var(--space-8);
}

.section-header {
    margin-bottom: var(--space-6);
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: var(--space-2);
    color: var(--dark-text);
}

.section-description {
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
}

/* تحسينات للبطاقات التفاعلية */
.interactive-card {
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.interactive-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent);
    transform: translateX(-100%);
}

.interactive-card:hover::after {
    animation: shimmer 2s infinite;
}

/* تحسينات للأزرار مع الرموز */
.btn-with-icon {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-lg);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--dark-text-secondary);
    text-decoration: none;
    transition: all var(--transition-fast);
}

.btn-with-icon:hover {
    background: rgba(37, 99, 235, 0.1);
    border-color: rgba(37, 99, 235, 0.3);
    color: var(--primary-color);
}

/* تحسينات للجداول التفاعلية */
.table-hover tbody tr {
    cursor: pointer;
}

.table-striped tbody tr:nth-child(odd) {
    background: rgba(255, 255, 255, 0.02);
}

.table-bordered {
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.table-bordered th,
.table-bordered td {
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* تحسينات للأشكال */
.avatar {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 1rem;
}

.avatar-sm {
    width: 32px;
    height: 32px;
    font-size: 0.875rem;
}

.avatar-lg {
    width: 56px;
    height: 56px;
    font-size: 1.25rem;
}

.avatar-xl {
    width: 80px;
    height: 80px;
    font-size: 1.5rem;
}

/* تحسينات للإشعارات */
.notification {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: rgba(255, 255, 255, 0.03);
    border-radius: var(--radius-lg);
    margin-bottom: var(--space-2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all var(--transition-fast);
}

.notification:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
}

.notification.unread {
    background: rgba(37, 99, 235, 0.05);
    border-color: rgba(37, 99, 235, 0.1);
}

.notification-icon {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    background: rgba(37, 99, 235, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary-color);
    flex-shrink: 0;
}

.notification-content {
    flex: 1;
}

.notification-title {
    font-weight: 600;
    margin-bottom: var(--space-1);
    color: var(--dark-text);
}

.notification-message {
    font-size: 0.875rem;
    color: var(--dark-text-secondary);
    margin-bottom: var(--space-1);
}

.notification-time {
    font-size: 0.75rem;
    color: var(--dark-text-secondary);
    opacity: 0.7;
}

/* تحسينات للرموز الحالة */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: var(--radius-full);
    background: currentColor;
}

.status-online {
    color: var(--success-color);
}

.status-offline {
    color: var(--danger-color);
}

.status-away {
    color: var(--warning-color);
}

.status-busy {
    color: var(--accent-color);
}

/* تحسينات للرموز التفاعلية */
.icon-button {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-full);
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--dark-text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.icon-button:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: var(--dark-text);
}

.icon-button:active {
    transform: scale(0.95);
}

.icon-button-primary {
    background: rgba(37, 99, 235, 0.1);
    border-color: rgba(37, 99, 235, 0.2);
    color: var(--primary-color);
}

.icon-button-primary:hover {
    background: rgba(37, 99, 235, 0.2);
    border-color: rgba(37, 99, 235, 0.3);
}

.icon-button-success {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.2);
    color: var(--success-color);
}

.icon-button-success:hover {
    background: rgba(16, 185, 129, 0.2);
    border-color: rgba(16, 185, 129, 0.3);
}

.icon-button-danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
    color: var(--danger-color);
}

.icon-button-danger:hover {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.3);
}

.icon-button-warning {
    background: rgba(245, 158, 11, 0.1);
    border-color: rgba(245, 158, 11, 0.2);
    color: var(--warning-color);
}

.icon-button-warning:hover {
    background: rgba(245, 158, 11, 0.2);
    border-color: rgba(245, 158, 11, 0.3);
}

/* تحسينات للتظليل */
.shadow-inner {
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1);
}

.shadow-none {
    box-shadow: none !important;
}

/* تحسينات للحدود */
.border-0 { border-width: 0 !important; }
.border-2 { border-width: 2px !important; }
.border-4 { border-width: 4px !important; }

.border-t { border-top: 1px solid rgba(255, 255, 255, 0.1) !important; }
.border-r { border-right: 1px solid rgba(255, 255, 255, 0.1) !important; }
.border-b { border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important; }
.border-l { border-left: 1px solid rgba(255, 255, 255, 0.1) !important; }

/* تحسينات للظلال النصية */
.text-shadow {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.text-shadow-sm {
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.text-shadow-lg {
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.7);
}

/* تحسينات للتدرجات النصية */
.text-gradient {
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.text-gradient-primary {
    background-image: linear-gradient(135deg, var(--primary-color), var(--accent-color));
}

.text-gradient-secondary {
    background-image: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
}

/* تحسينات للخلفيات */
.bg-blur {
    backdrop-filter: blur(8px);
}

.bg-blur-sm {
    backdrop-filter: blur(4px);
}

.bg-blur-lg {
    backdrop-filter: blur(16px);
}

/* تحسينات للارتفاعات */
.min-h-0 { min-height: 0 !important; }
.min-h-full { min-height: 100% !important; }
.min-h-screen { min-height: 100vh !important; }

.max-h-0 { max-height: 0 !important; }
.max-h-full { max-height: 100% !important; }
.max-h-screen { max-height: 100vh !important; }

.h-0 { height: 0 !important; }
.h-full { height: 100% !important; }
.h-screen { height: 100vh !important; }

/* تحسينات للعروض */
.min-w-0 { min-width: 0 !important; }
.min-w-full { min-width: 100% !important; }

.max-w-0 { max-width: 0 !important; }
.max-w-full { max-width: 100% !important; }
.max-w-screen-sm { max-width: 640px !important; }
.max-w-screen-md { max-width: 768px !important; }
.max-w-screen-lg { max-width: 1024px !important; }
.max-w-screen-xl { max-width: 1280px !important; }
.max-w-screen-2xl { max-width: 1536px !important; }

.w-0 { width: 0 !important; }
.w-full { width: 100% !important; }
.w-screen { width: 100vw !important; }

/* تحسينات للفواصل */
.space-x-1 > * + * { margin-right: var(--space-1) !important; }
.space-x-2 > * + * { margin-right: var(--space-2) !important; }
.space-x-3 > * + * { margin-right: var(--space-3) !important; }
.space-x-4 > * + * { margin-right: var(--space-4) !important; }
.space-x-5 > * + * { margin-right: var(--space-5) !important; }
.space-x-6 > * + * { margin-right: var(--space-6) !important; }

.space-y-1 > * + * { margin-top: var(--space-1) !important; }
.space-y-2 > * + * { margin-top: var(--space-2) !important; }
.space-y-3 > * + * { margin-top: var(--space-3) !important; }
.space-y-4 > * + * { margin-top: var(--space-4) !important; }
.space-y-5 > * + * { margin-top: var(--space-5) !important; }
.space-y-6 > * + * { margin-top: var(--space-6) !important; }

/* تحسينات للعرض */
.block { display: block !important; }
.inline-block { display: inline-block !important; }
.inline { display: inline !important; }
.inline-flex { display: inline-flex !important; }
.table { display: table !important; }
.table-row { display: table-row !important; }
.table-cell { display: table-cell !important; }

/* تحسينات للموضع */
.static { position: static !important; }
.fixed { position: fixed !important; }
.absolute { position: absolute !important; }
.relative { position: relative !important; }
.sticky { position: sticky !important; }

.inset-0 {
    top: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    left: 0 !important;
}

.top-0 { top: 0 !important; }
.right-0 { right: 0 !important; }
.bottom-0 { bottom: 0 !important; }
.left-0 { left: 0 !important; }

.top-auto { top: auto !important; }
.right-auto { right: auto !important; }
.bottom-auto { bottom: auto !important; }
.left-auto { left: auto !important; }

/* تحسينات للتحويلات */
.transform { transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y)) !important; }
.transform-none { transform: none !important; }

.translate-x-0 { --tw-translate-x: 0px !important; }
.translate-x-full { --tw-translate-x: 100% !important; }
.translate-y-0 { --tw-translate-y: 0px !important; }
.translate-y-full { --tw-translate-y: 100% !important; }

.rotate-0 { --tw-rotate: 0deg !important; }
.rotate-90 { --tw-rotate: 90deg !important; }
.rotate-180 { --tw-rotate: 180deg !important; }
.rotate-270 { --tw-rotate: 270deg !important; }

.scale-0 { --tw-scale-x: 0 !important; --tw-scale-y: 0 !important; }
.scale-50 { --tw-scale-x: .5 !important; --tw-scale-y: .5 !important; }
.scale-75 { --tw-scale-x: .75 !important; --tw-scale-y: .75 !important; }
.scale-90 { --tw-scale-x: .9 !important; --tw-scale-y: .9 !important; }
.scale-95 { --tw-scale-x: .95 !important; --tw-scale-y: .95 !important; }
.scale-100 { --tw-scale-x: 1 !important; --tw-scale-y: 1 !important; }
.scale-105 { --tw-scale-x: 1.05 !important; --tw-scale-y: 1.05 !important; }
.scale-110 { --tw-scale-x: 1.1 !important; --tw-scale-y: 1.1 !important; }
.scale-125 { --tw-scale-x: 1.25 !important; --tw-scale-y: 1.25 !important; }

/* تحسينات لمؤشرات التحميل */
.spinner {
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-top-color: var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.spinner-sm {
    width: 16px;
    height: 16px;
}

.spinner-md {
    width: 24px;
    height: 24px;
}

.spinner-lg {
    width: 32px;
    height: 32px;
}

.spinner-xl {
    width: 48px;
    height: 48px;
}

/* تحسينات للخطوط */
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important; }
.font-serif { font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif !important; }
.font-sans { font-family: ui-sans-serif, system-ui, -apple-system, sans-serif !important; }

/* تحسينات للحروف */
.uppercase { text-transform: uppercase !important; }
.lowercase { text-transform: lowercase !important; }
.capitalize { text-transform: capitalize !important; }
.normal-case { text-transform: none !important; }

.italic { font-style: italic !important; }
.not-italic { font-style: normal !important; }

.underline { text-decoration: underline !important; }
.line-through { text-decoration: line-through !important; }
.no-underline { text-decoration: none !important; }

/* تحسينات للقوائم */
.list-none { list-style-type: none !important; }
.list-disc { list-style-type: disc !important; }
.list-decimal { list-style-type: decimal !important; }

.list-inside { list-style-position: inside !important; }
.list-outside { list-style-position: outside !important; }

/* تحسينات للمحتوى */
.content-center { align-content: center !important; }
.content-start { align-content: flex-start !important; }
.content-end { align-content: flex-end !important; }
.content-between { align-content: space-between !important; }
.content-around { align-content: space-around !important; }
.content-evenly { align-content: space-evenly !important; }

/* تحسينات لمحاذاة العناصر */
.place-items-center { place-items: center !important; }
.place-items-start { place-items: start !important; }
.place-items-end { place-items: end !important; }
.place-items-stretch { place-items: stretch !important; }

.place-content-center { place-content: center !important; }
.place-content-start { place-content: start !important; }
.place-content-end { place-content: end !important; }
.place-content-between { place-content: space-between !important; }
.place-content-around { place-content: space-around !important; }
.place-content-evenly { place-content: space-evenly !important; }
.place-content-stretch { place-content: stretch !important; }

.place-self-auto { place-self: auto !important; }
.place-self-start { place-self: start !important; }
.place-self-end { place-self: end !important; }
.place-self-center { place-self: center !important; }
.place-self-stretch { place-self: stretch !important; }

/* تحسينات للعرض والشاشات */
@media (min-width: 640px) {
    .sm\\:grid-2 { grid-template-columns: repeat(2, 1fr) !important; }
    .sm\\:grid-3 { grid-template-columns: repeat(3, 1fr) !important; }
    .sm\\:grid-4 { grid-template-columns: repeat(4, 1fr) !important; }
}

@media (min-width: 768px) {
    .md\\:grid-2 { grid-template-columns: repeat(2, 1fr) !important; }
    .md\\:grid-3 { grid-template-columns: repeat(3, 1fr) !important; }
    .md\\:grid-4 { grid-template-columns: repeat(4, 1fr) !important; }
    .md\\:grid-5 { grid-template-columns: repeat(5, 1fr) !important; }
    .md\\:grid-6 { grid-template-columns: repeat(6, 1fr) !important; }
}

@media (min-width: 1024px) {
    .lg\\:grid-2 { grid-template-columns: repeat(2, 1fr) !important; }
    .lg\\:grid-3 { grid-template-columns: repeat(3, 1fr) !important; }
    .lg\\:grid-4 { grid-template-columns: repeat(4, 1fr) !important; }
    .lg\\:grid-5 { grid-template-columns: repeat(5, 1fr) !important; }
    .lg\\:grid-6 { grid-template-columns: repeat(6, 1fr) !important; }
}

@media (min-width: 1280px) {
    .xl\\:grid-2 { grid-template-columns: repeat(2, 1fr) !important; }
    .xl\\:grid-3 { grid-template-columns: repeat(3, 1fr) !important; }
    .xl\\:grid-4 { grid-template-columns: repeat(4, 1fr) !important; }
    .xl\\:grid-5 { grid-template-columns: repeat(5, 1fr) !important; }
    .xl\\:grid-6 { grid-template-columns: repeat(6, 1fr) !important; }
}

@media (min-width: 1536px) {
    .\\32xl\\:grid-2 { grid-template-columns: repeat(2, 1fr) !important; }
    .\\32xl\\:grid-3 { grid-template-columns: repeat(3, 1fr) !important; }
    .\\32xl\\:grid-4 { grid-template-columns: repeat(4, 1fr) !important; }
    .\\32xl\\:grid-5 { grid-template-columns: repeat(5, 1fr) !important; }
    .\\32xl\\:grid-6 { grid-template-columns: repeat(6, 1fr) !important; }
}
"""

# ================== قالب لوحة التحكم المحسن ==================
def get_dashboard_template(title, subtitle, content, current_lang='ar'):
    """إنشاء قالب لوحة التحكم مع دعم اللغات"""
    lang = current_lang if current_lang in ['ar', 'en'] else 'ar'
    dir = 'rtl' if lang == 'ar' else 'ltr'
    
    # الحصول على النصوص باللغة المحددة
    t = lambda key: multilang.get_text(key, lang)
    
    # إحصائيات الإشعارات
    notification_count = 0
    if session.get('user_logged_in'):
        notifications = NotificationSystem.get_user_notifications(session['user_id'], unread_only=True, limit=10)
        notification_count = len(notifications)
    
    template = f"""
    <!DOCTYPE html>
    <html dir="{dir}" lang="{lang}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - InvoiceFlow Pro</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            {BASE_CSS}
            {DASHBOARD_CSS}
            
            /* تنسيقات إضافية للغة الإنجليزية */
            [dir="ltr"] .arabic-text {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
            }}
            
            [dir="ltr"] .sidebar-nav {{
                padding-left: 0;
                padding-right: 0;
            }}
            
            [dir="ltr"] .nav-item {{
                padding-left: var(--space-4);
                padding-right: var(--space-4);
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-layout">
            <!-- الشريط الجانبي -->
            <aside class="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-brand">
                        <div class="sidebar-brand-icon">
                            <i class="fas fa-file-invoice-dollar"></i>
                        </div>
                        <div class="sidebar-brand-text">
                            <h2>InvoiceFlow Pro</h2>
                            <p>{t('professional_system')}</p>
                        </div>
                    </div>
                    
                    <div class="card bg-dark-card p-4">
                        <div class="flex items-center gap-3">
                            <div class="avatar bg-gradient-primary">
                                {session.get('username', 'A')[0].upper()}
                            </div>
                            <div>
                                <p class="font-semibold text-dark">{session.get('username', 'User')}</p>
                                <p class="text-xs text-muted">{session.get('company_name', t('my_company'))}</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <nav class="sidebar-nav">
                    <a href="{{{{ url_for('dashboard') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'dashboard' else '' }}}}">
                        <i class="fas fa-tachometer-alt nav-icon"></i>
                        <span>{t('dashboard')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('invoices') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'invoices' else '' }}}}">
                        <i class="fas fa-file-invoice-dollar nav-icon"></i>
                        <span>{t('invoices')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('create_invoice') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'create_invoice' else '' }}}}">
                        <i class="fas fa-plus-circle nav-icon"></i>
                        <span>{t('create_invoice')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('clients') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'clients' else '' }}}}">
                        <i class="fas fa-users nav-icon"></i>
                        <span>{t('clients')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('products') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'products' else '' }}}}">
                        <i class="fas fa-box nav-icon"></i>
                        <span>{t('products')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('reports') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'reports' else '' }}}}">
                        <i class="fas fa-chart-bar nav-icon"></i>
                        <span>{t('reports')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('ai_insights') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'ai_insights' else '' }}}}">
                        <i class="fas fa-robot nav-icon"></i>
                        <span>{t('ai_insights')}</span>
                    </a>
                    
                    <div class="separator"></div>
                    
                    <a href="{{{{ url_for('profile') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'profile' else '' }}}}">
                        <i class="fas fa-user-cog nav-icon"></i>
                        <span>{t('profile')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('settings') }}}}" class="nav-item {{{{ 'active' if request.endpoint == 'settings' else '' }}}}">
                        <i class="fas fa-cog nav-icon"></i>
                        <span>{t('settings')}</span>
                    </a>
                    
                    <a href="{{{{ url_for('logout') }}}}" class="nav-item">
                        <i class="fas fa-sign-out-alt nav-icon"></i>
                        <span>{t('logout')}</span>
                    </a>
                </nav>
                
                <div class="px-6 mt-auto pt-6 border-t border-dark-border">
                    <div class="text-center">
                        <p class="text-sm text-muted mb-2">InvoiceFlow Pro</p>
                        <p class="text-xs text-muted">{t('professional_version')} 2024</p>
                        
                        <!-- تبديل اللغة -->
                        <div class="mt-4">
                            <select id="languageSwitch" class="form-control form-select text-sm" onchange="switchLanguage(this.value)">
                                <option value="ar" {{{{ 'selected' if session.get('language', 'ar') == 'ar' else '' }}}}>العربية</option>
                                <option value="en" {{{{ 'selected' if session.get('language', 'ar') == 'en' else '' }}}}>English</option>
                            </select>
                        </div>
                    </div>
                </div>
            </aside>
            
            <!-- المحتوى الرئيسي -->
            <main class="main-content">
                <!-- شريط التنقل العلوي -->
                <nav class="navbar">
                    <div class="navbar-content">
                        <div class="navbar-title">
                            <h1>{title}</h1>
                            <p>{subtitle}</p>
                        </div>
                        
                        <div class="navbar-actions">
                            <!-- زر الإشعارات -->
                            <div class="relative">
                                <button class="notification-btn" onclick="toggleNotifications()">
                                    <i class="fas fa-bell"></i>
                                    {{{{ '<span class="notification-badge">{}</span>'.format(notification_count) if notification_count > 0 else '' }}}}
                                </button>
                                
                                <!-- قائمة الإشعارات -->
                                <div id="notificationsPanel" class="hidden absolute top-full left-0 mt-2 w-80 bg-dark-card border border-dark-border rounded-xl shadow-2xl z-50">
                                    <div class="p-4 border-b border-dark-border">
                                        <div class="flex items-center justify-between">
                                            <h3 class="font-semibold">{t('notifications')}</h3>
                                            <button class="text-sm text-primary hover:underline" onclick="markAllNotificationsAsRead()">
                                                {t('mark_all_as_read')}
                                            </button>
                                        </div>
                                    </div>
                                    <div class="max-h-96 overflow-y-auto">
                                        {{{{ generate_notifications_list(notifications if notifications else []) }}}}
                                    </div>
                                    <div class="p-4 border-t border-dark-border text-center">
                                        <a href="#" class="text-sm text-primary hover:underline">{t('view_all_notifications')}</a>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- الوقت -->
                            <div class="time-display">
                                <i class="fas fa-clock"></i>
                                <span id="currentTime">{datetime.now().strftime('%I:%M %p')}</span>
                            </div>
                            
                            <!-- معلومات المستخدم -->
                            <div class="flex items-center gap-2">
                                <div class="avatar bg-gradient-primary">
                                    {session.get('username', 'U')[0].upper()}
                                </div>
                            </div>
                        </div>
                    </div>
                </nav>
                
                <!-- رسائل التنبيه -->
                {{{{ get_flashed_messages_html() }}}}
                
                <!-- محتوى الصفحة -->
                <div class="content-container">
                    {content}
                </div>
            </main>
        </div>
        
        <!-- نصوص JavaScript -->
        <script>
            // تحديث الوقت
            function updateTime() {{
                const now = new Date();
                const timeStr = now.toLocaleTimeString('{{{{ 'ar-SA' if '{lang}' == 'ar' else 'en-US' }}}}');
                document.getElementById('currentTime').textContent = timeStr;
            }}
            
            setInterval(updateTime, 1000);
            updateTime();
            
            // تبديل اللغة
            function switchLanguage(lang) {{
                fetch('{{{{ url_for('set_language') }}}}', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{language: lang}})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        window.location.reload();
                    }}
                }});
            }}
            
            // عرض/إخفاء الإشعارات
            function toggleNotifications() {{
                const panel = document.getElementById('notificationsPanel');
                panel.classList.toggle('hidden');
            }}
            
            // إغلاق الإشعارات عند النقر خارجها
            document.addEventListener('click', function(event) {{
                const notificationsBtn = document.querySelector('.notification-btn');
                const notificationsPanel = document.getElementById('notificationsPanel');
                
                if (!notificationsBtn.contains(event.target) && !notificationsPanel.contains(event.target)) {{
                    notificationsPanel.classList.add('hidden');
                }}
            }});
            
            // تحديد جميع الإشعارات كمقروءة
            function markAllNotificationsAsRead() {{
                fetch('{{{{ url_for('mark_all_notifications_as_read') }}}}', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        window.location.reload();
                    }}
                }});
            }}
            
            // تحديد إشعار كمقروء
            function markNotificationAsRead(notificationId) {{
                fetch('{{{{ url_for('mark_notification_as_read') }}}}', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{id: notificationId}})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        document.querySelector(`[data-notification-id="${{notificationId}}"]`).classList.remove('unread');
                    }}
                }});
            }}
            
            // تحميل الصفحة
            document.addEventListener('DOMContentLoaded', function() {{
                // إضافة تأثير التحميل
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {{
                    document.body.style.opacity = '1';
                }}, 100);
                
                // إضافة تأثيرات للبطاقات
                document.querySelectorAll('.card').forEach(card => {{
                    card.classList.add('scale-in');
                }});
            }});
        </script>
    </body>
    </html>
    """
    return template

# ================== دوال المساعدة ==================
def get_flashed_messages_html():
    """إنشاء HTML لرسائل التنبيه"""
    messages_html = ""
    with app.test_request_context():
        messages = session.get('_flashes', [])
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
    
    return messages_html

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
        <div class="notification {{{{ 'unread' if not notification['is_read'] else '' }}}}" data-notification-id="{notification['id']}">
            <div class="notification-icon">
                <i class="{icon_class}"></i>
            </div>
            <div class="notification-content">
                <p class="notification-title">{notification['title']}</p>
                <p class="notification-message">{notification['message']}</p>
                <p class="notification-time">{time_ago}</p>
            </div>
            {{{{ '<button class="icon-button icon-button-primary" onclick="markNotificationAsRead({})"><i class="fas fa-check"></i></button>'.format(notification['id']) if not notification['is_read'] else '' }}}}
        </div>
        """
    
    return notifications_html

def get_time_ago(timestamp):
    """الحصول على الوقت المنقضي"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
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

# ================== نظام PDF المحترف ==================
class ProfessionalPDFGenerator:
    def __init__(self):
        # تسجيل الخطوط العربية
        try:
            # استخدام خط افتراضي إذا لم تكن الخطوط متوفرة
            self.arabic_font = "Helvetica"
        except:
            self.arabic_font = "Helvetica"
    
    def reshape_arabic_text(self, text):
        """تعديل النص العربي للعرض الصحيح"""
        if not text:
            return ""
        
        try:
            # إعادة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(text)
            # عكس النص للعرض من اليمين لليسار
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text
    
    def generate_invoice_pdf(self, invoice_data, user_data):
        """إنشاء فاتورة PDF احترافية"""
        try:
            # إنشاء buffer للـ PDF
            buffer = io.BytesIO()
            
            # إنشاء المستند
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm,
                title=f"Invoice {invoice_data.get('invoice_number', '')}"
            )
            
            styles = getSampleStyleSheet()
            
            # إنشاء أنماط مخصصة
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.black,
                alignment=1,  # Center
                spaceAfter=20
            )
            
            # نمط للنصوص العربية
            arabic_style = ParagraphStyle(
                'Arabic',
                parent=styles['Normal'],
                fontName=self.arabic_font,
                fontSize=10,
                textColor=colors.black,
                alignment=2,  # Right
                wordWrap='RTL'
            )
            
            # نمط للعناوين
            heading_style = ParagraphStyle(
                'Heading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.black,
                alignment=2,  # Right
                spaceAfter=10
            )
            
            # نمط للبيانات
            data_style = ParagraphStyle(
                'Data',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                alignment=2  # Right
            )
            
            elements = []
            
            # رأس الفاتورة
            header_table_data = [
                [
                    # معلومات الشركة
                    Paragraph(f"<b>{self.reshape_arabic_text(user_data.get('company_name', 'شركتي'))}</b>", arabic_style),
                    # العنوان
                    Paragraph(f"<b>فاتورة ضريبية</b>", title_style)
                ]
            ]
            
            header_table = Table(header_table_data, colWidths=[250, 250])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ]))
            
            elements.append(header_table)
            elements.append(Spacer(1, 20))
            
            # معلومات الشركة والعميل
            company_info = f"""
            <b>معلومات البائع:</b><br/>
            {self.reshape_arabic_text(user_data.get('company_name', 'شركتي'))}<br/>
            {self.reshape_arabic_text(user_data.get('address', 'العنوان'))}<br/>
            الهاتف: {user_data.get('phone', '0000000000')}<br/>
            البريد الإلكتروني: {user_data.get('email', 'info@company.com')}<br/>
            الرقم الضريبي: {user_data.get('tax_number', '')}
            """
            
            client_info = f"""
            <b>معلومات العميل:</b><br/>
            {self.reshape_arabic_text(invoice_data.get('client_name', 'عميل'))}<br/>
            {self.reshape_arabic_text(invoice_data.get('client_address', 'العنوان'))}<br/>
            الهاتف: {invoice_data.get('client_phone', '0000000000')}<br/>
            البريد الإلكتروني: {invoice_data.get('client_email', 'client@email.com')}<br/>
            الرقم الضريبي: {invoice_data.get('client_tax_number', '')}
            """
            
            info_table_data = [
                [
                    Paragraph(company_info, arabic_style),
                    Paragraph(client_info, arabic_style)
                ]
            ]
            
            info_table = Table(info_table_data, colWidths=[250, 250])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F8F9FA')),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#F8F9FA')),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 20))
            
            # تفاصيل الفاتورة
            details_data = [
                ['رقم الفاتورة', invoice_data.get('invoice_number', 'INV-0001')],
                ['تاريخ الإصدار', invoice_data.get('issue_date', datetime.now().strftime('%Y/%m/%d'))],
                ['تاريخ الاستحقاق', invoice_data.get('due_date', datetime.now().strftime('%Y/%m/%d'))],
                ['طريقة الدفع', invoice_data.get('payment_method', 'نقدي')],
                ['الحالة', invoice_data.get('status', 'معلقة')]
            ]
            
            details_table = Table(details_data, colWidths=[100, 100])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            elements.append(details_table)
            elements.append(Spacer(1, 20))
            
            # جدول العناصر
            items = invoice_data.get('items', [])
            if not items:
                items = [
                    {'name': 'خدمة استشارية', 'description': 'استشارة تقنية متخصصة', 'quantity': 1, 'price': 1000, 'total': 1000},
                    {'name': 'تصميم جرافيك', 'description': 'تصميم شعار احترافي', 'quantity': 2, 'price': 500, 'total': 1000}
                ]
            
            items_data = [
                [
                    'الوصف',
                    'الكمية', 
                    'سعر الوحدة',
                    'المجموع'
                ]
            ]
            
            for item in items:
                items_data.append([
                    self.reshape_arabic_text(item.get('name', '')),
                    str(item.get('quantity', 1)),
                    f"{item.get('price', 0):.2f}",
                    f"{item.get('total', 0):.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[200, 60, 80, 80])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),
            ]))
            
            elements.append(items_table)
            elements.append(Spacer(1, 10))
            
            # إضافة المجاميع
            subtotal = invoice_data.get('subtotal', 2000)
            tax_rate = invoice_data.get('tax_rate', 15)
            tax_amount = invoice_data.get('tax_amount', 300)
            discount = invoice_data.get('discount', 0)
            total = invoice_data.get('total_amount', 2300)
            
            totals_data = [
                ['', '', 'المجموع الفرعي:', f"{subtotal:.2f}"],
                ['', '', 'الضريبة:', f"{tax_amount:.2f}"],
                ['', '', 'الخصم:', f"-{discount:.2f}"],
                ['', '', '<b>الإجمالي:</b>', f"<b>{total:.2f}</b>"]
            ]
            
            totals_table = Table(totals_data, colWidths=[200, 60, 80, 80])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                ('FONTNAME', (2, -1), (3, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (2, -1), (3, -1), 11),
                ('TEXTCOLOR', (2, -1), (3, -1), colors.HexColor('#2C3E50')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(totals_table)
            elements.append(Spacer(1, 20))
            
            # الملاحظات
            if invoice_data.get('notes'):
                notes_text = f"<b>ملاحظات:</b><br/>{self.reshape_arabic_text(invoice_data.get('notes'))}"
                elements.append(Paragraph(notes_text, arabic_style))
                elements.append(Spacer(1, 20))
            
            # التوقيعات
            signatures_data = [
                [
                    Paragraph("_________________________<br/>توقيع البائع", data_style),
                    Paragraph("_________________________<br/>توقيع العميل", data_style)
                ]
            ]
            
            signatures_table = Table(signatures_data, colWidths=[250, 250])
            signatures_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('TOPPADDING', (0, 0), (-1, -1), 40),
            ]))
            
            elements.append(signatures_table)
            elements.append(Spacer(1, 20))
            
            # تذييل الصفحة
            footer_text = f"""
            <b>شكراً لتعاملك معنا</b><br/>
            للاستفسارات: {user_data.get('phone', '')} | {user_data.get('email', '')}<br/>
            هذه الفاتورة تم إنشاؤها تلقائياً بواسطة نظام InvoiceFlow Pro
            """
            
            elements.append(Paragraph(self.reshape_arabic_text(footer_text), ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=1,  # Center
                spaceBefore=20
            )))
            
            # إنشاء الـ QR Code
            try:
                # إنشاء QR Code يحتوي على معلومات الفاتورة
                qr_data = {
                    'invoice_number': invoice_data.get('invoice_number', ''),
                    'company': user_data.get('company_name', ''),
                    'client': invoice_data.get('client_name', ''),
                    'amount': total,
                    'date': invoice_data.get('issue_date', ''),
                    'url': f"https://invoiceflow.pro/invoice/{invoice_data.get('invoice_number', '')}"
                }
                
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=2,
                )
                qr.add_data(json.dumps(qr_data, ensure_ascii=False))
                qr.make(fit=True)
                
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_buffer = io.BytesIO()
                qr_img.save(qr_buffer, format='PNG')
                qr_buffer.seek(0)
                
                # إضافة QR Code إلى PDF
                qr_image = Image(qr_buffer, width=60, height=60)
                qr_image.hAlign = 'LEFT'
                elements.append(qr_image)
                
            except Exception as e:
                print(f"خطأ في إنشاء QR Code: {e}")
            
            # بناء المستند
            doc.build(elements)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"خطأ في إنشاء PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

# ================== الصفحات الرئيسية ==================

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
        
        # التحقق من المدخلات
        if not username or not password:
            flash('يرجى إدخال اسم المستخدم وكلمة المرور', 'error')
            return redirect(url_for('login'))
        
        # التحقق من الحظر المؤقت
        if session.get('login_blocked_until') and time.time() < session['login_blocked_until']:
            remaining = int((session['login_blocked_until'] - time.time()) / 60)
            flash(f'تم تجاوز عدد المحاولات المسموحة، يرجى المحاولة بعد {remaining} دقيقة', 'error')
            return redirect(url_for('login'))
        
        # البحث عن المستخدم
        user = db.execute_query(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,),
            fetchone=True
        )
        
        if not user:
            # زيادة عدد المحاولات الفاشلة
            failed_attempts = session.get('failed_login_attempts', 0) + 1
            session['failed_login_attempts'] = failed_attempts
            
            if failed_attempts >= 5:
                session['login_blocked_until'] = time.time() + 900  # 15 دقيقة
                flash('تم تجاوز عدد المحاولات المسموحة، يرجى المحاولة بعد 15 دقيقة', 'error')
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            
            return redirect(url_for('login'))
        
        # التحقق من كلمة المرور
        if not check_password_hash(user['password_hash'], password):
            # زيادة عدد المحاولات الفاشلة
            failed_attempts = session.get('failed_login_attempts', 0) + 1
            session['failed_login_attempts'] = failed_attempts
            
            if failed_attempts >= 5:
                session['login_blocked_until'] = time.time() + 900  # 15 دقيقة
                flash('تم تجاوز عدد المحاولات المسموحة، يرجى المحاولة بعد 15 دقيقة', 'error')
            else:
                flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
            
            # تحديث عدد محاولات الدخول الفاشلة في قاعدة البيانات
            db.execute_query(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = ?",
                (user['id'],)
            )
            
            return redirect(url_for('login'))
        
        # إعادة تعيين محاولات الدخول الفاشلة
        session.pop('failed_login_attempts', None)
        session.pop('login_blocked_until', None)
        
        # تحديث وقت الدخول الأخير وإعادة تعيين المحاولات الفاشلة
        db.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP, failed_login_attempts = 0 WHERE id = ?",
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
        
        # تسجيل النشاط
        ActivityLogger.log_activity(
            user['id'],
            'login',
            'تسجيل دخول ناجح',
            request
        )
        
        # إنشاء إشعار ترحيبي
        NotificationSystem.create_notification(
            user['id'],
            'info',
            'مرحباً بك في InvoiceFlow Pro',
            f'مرحباً {user["full_name"] or user["username"]}! تم تسجيل دخولك بنجاح.',
            {'type': 'welcome'}
        )
        
        flash(f'مرحباً بك {session["full_name"]}!', 'success')
        
        next_page = request.form.get('next') or url_for('dashboard')
        return redirect(next_page)
    
    # التحقق من الحظر المؤقت
    if session.get('login_blocked_until') and time.time() < session['login_blocked_until']:
        remaining = int((session['login_blocked_until'] - time.time()) / 60)
        flash(f'الدخول محظور مؤقتاً، يرجى المحاولة بعد {remaining} دقيقة', 'error')
    
    # صفحة تسجيل الدخول
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceFlow Pro - تسجيل الدخول</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            {{ css }}
            
            .login-container {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, var(--dark-bg) 0%, #1a202c 100%);
                padding: var(--space-4);
            }
            
            .login-card {
                background: var(--dark-card);
                border-radius: var(--radius-2xl);
                padding: var(--space-8);
                width: 100%;
                max-width: 400px;
                box-shadow: var(--shadow-2xl);
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: scaleIn 0.5s ease;
            }
            
            .login-header {
                text-align: center;
                margin-bottom: var(--space-8);
            }
            
            .login-logo {
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
            }
            
            .login-title {
                font-size: 1.875rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: var(--space-2);
            }
            
            .login-subtitle {
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }
            
            .login-form .form-group {
                margin-bottom: var(--space-4);
            }
            
            .login-form .form-label {
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--dark-text-secondary);
            }
            
            .login-options {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--space-6);
            }
            
            .login-remember {
                display: flex;
                align-items: center;
                gap: var(--space-2);
            }
            
            .login-forgot {
                color: var(--primary-color);
                text-decoration: none;
                font-size: 0.875rem;
            }
            
            .login-forgot:hover {
                text-decoration: underline;
            }
            
            .login-button {
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
            }
            
            .login-button:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-primary);
            }
            
            .login-button:active {
                transform: translateY(0);
            }
            
            .login-footer {
                margin-top: var(--space-6);
                text-align: center;
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }
            
            .login-footer a {
                color: var(--primary-color);
                text-decoration: none;
            }
            
            .login-footer a:hover {
                text-decoration: underline;
            }
            
            .test-credentials {
                margin-top: var(--space-6);
                padding: var(--space-4);
                background: rgba(255, 255, 255, 0.03);
                border-radius: var(--radius-lg);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .test-credentials h4 {
                font-size: 0.875rem;
                margin-bottom: var(--space-2);
                color: var(--dark-text-secondary);
            }
            
            .test-credentials .credentials {
                display: grid;
                gap: var(--space-2);
            }
            
            .credential-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .credential-label {
                font-size: 0.75rem;
                color: var(--dark-text-secondary);
            }
            
            .credential-value {
                font-family: monospace;
                background: rgba(0, 0, 0, 0.3);
                padding: var(--space-1) var(--space-2);
                border-radius: var(--radius-sm);
                font-size: 0.75rem;
                color: var(--primary-color);
            }
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
                
                {{ get_flashed_messages_html() }}
                
                <form class="login-form" method="POST" action="{{ url_for('login') }}">
                    <input type="hidden" name="next" value="{{ request.args.get('next', '') }}">
                    
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
                        <a href="{{ url_for('register') }}">إنشاء حساب جديد</a>
                    </p>
                    <p class="mt-2 text-xs">
                        © 2024 InvoiceFlow Pro. جميع الحقوق محفوظة.
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            // إضافة تأثير عند التحميل
            document.addEventListener('DOMContentLoaded', function() {
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {
                    document.body.style.opacity = '1';
                }, 100);
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html, css=BASE_CSS)

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
        
        # التحقق من المدخلات
        errors = []
        
        if not username or len(username) < 3:
            errors.append('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        
        if not email or '@' not in email:
            errors.append('البريد الإلكتروني غير صالح')
        
        # التحقق من قوة كلمة المرور
        if len(password) < 8:
            errors.append('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        elif not any(char.isdigit() for char in password):
            errors.append('كلمة المرور يجب أن تحتوي على رقم واحد على الأقل')
        elif not any(char.isupper() for char in password):
            errors.append('كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل')
        elif not any(char.islower() for char in password):
            errors.append('كلمة المرور يجب أن تحتوي على حرف صغير واحد على الأقل')
        
        if password != confirm_password:
            errors.append('كلمتا المرور غير متطابقتين')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('register'))
        
        # التحقق من عدم وجود المستخدم مسبقاً
        existing_user = db.execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email),
            fetchone=True
        )
        
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً', 'error')
            return redirect(url_for('register'))
        
        # إنشاء المستخدم الجديد
        password_hash = generate_password_hash(password)
        verification_token = secrets.token_urlsafe(32)
        
        db.execute_query('''
            INSERT INTO users (username, email, password_hash, full_name, company_name, phone, verification_token)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, company_name, phone, verification_token))
        
        # الحصول على معرف المستخدم الجديد
        new_user = db.execute_query(
            "SELECT id FROM users WHERE username = ?", 
            (username,), fetchone=True
        )
        
        if new_user:
            # تسجيل النشاط
            ActivityLogger.log_activity(
                new_user['id'],
                'register',
                'إنشاء حساب جديد',
                request
            )
            
            # إنشاء إشعار ترحيبي
            NotificationSystem.create_notification(
                new_user['id'],
                'info',
                'مرحباً بك في InvoiceFlow Pro',
                'تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.',
                {'type': 'welcome'}
            )
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('login'))
    
    # صفحة التسجيل
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceFlow Pro - إنشاء حساب</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            {{ css }}
            
            .register-container {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, var(--dark-bg) 0%, #1a202c 100%);
                padding: var(--space-4);
            }
            
            .register-card {
                background: var(--dark-card);
                border-radius: var(--radius-2xl);
                padding: var(--space-8);
                width: 100%;
                max-width: 500px;
                box-shadow: var(--shadow-2xl);
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: scaleIn 0.5s ease;
            }
            
            .register-header {
                text-align: center;
                margin-bottom: var(--space-8);
            }
            
            .register-logo {
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
            }
            
            .register-title {
                font-size: 1.875rem;
                font-weight: 700;
                background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: var(--space-2);
            }
            
            .register-subtitle {
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }
            
            .register-form .form-group {
                margin-bottom: var(--space-4);
            }
            
            .register-form .form-label {
                display: flex;
                align-items: center;
                gap: var(--space-2);
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }
            
            .password-strength {
                height: 4px;
                background: var(--gray-700);
                border-radius: var(--radius-full);
                margin-top: var(--space-1);
                overflow: hidden;
            }
            
            .strength-bar {
                height: 100%;
                width: 0;
                border-radius: var(--radius-full);
                transition: width var(--transition-normal), background-color var(--transition-normal);
            }
            
            .strength-weak { width: 25%; background: var(--danger-color); }
            .strength-medium { width: 50%; background: var(--warning-color); }
            .strength-strong { width: 75%; background: var(--info-color); }
            .strength-very-strong { width: 100%; background: var(--success-color); }
            
            .password-requirements {
                margin-top: var(--space-2);
                font-size: 0.75rem;
                color: var(--dark-text-secondary);
            }
            
            .requirement {
                display: flex;
                align-items: center;
                gap: var(--space-1);
                margin-bottom: var(--space-1);
            }
            
            .requirement.met {
                color: var(--success-color);
            }
            
            .requirement.unmet {
                color: var(--dark-text-secondary);
            }
            
            .requirement i {
                font-size: 0.875rem;
            }
            
            .register-button {
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
            }
            
            .register-button:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-secondary);
            }
            
            .register-button:active {
                transform: translateY(0);
            }
            
            .register-footer {
                margin-top: var(--space-6);
                text-align: center;
                color: var(--dark-text-secondary);
                font-size: 0.875rem;
            }
            
            .register-footer a {
                color: var(--primary-color);
                text-decoration: none;
            }
            
            .register-footer a:hover {
                text-decoration: underline;
            }
            
            .form-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: var(--space-4);
            }
            
            @media (max-width: 640px) {
                .form-grid {
                    grid-template-columns: 1fr;
                }
            }
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
                
                {{ get_flashed_messages_html() }}
                
                <form class="register-form" method="POST" action="{{ url_for('register') }}">
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
                                   placeholder="8 أحرف على الأقل" required
                                   oninput="checkPasswordStrength()">
                            <div class="password-strength">
                                <div class="strength-bar" id="strengthBar"></div>
                            </div>
                            <div class="password-requirements" id="passwordRequirements">
                                <div class="requirement unmet" id="reqLength">
                                    <i class="fas fa-times"></i>
                                    <span>8 أحرف على الأقل</span>
                                </div>
                                <div class="requirement unmet" id="reqNumber">
                                    <i class="fas fa-times"></i>
                                    <span>رقم واحد على الأقل</span>
                                </div>
                                <div class="requirement unmet" id="reqUpper">
                                    <i class="fas fa-times"></i>
                                    <span>حرف كبير واحد على الأقل</span>
                                </div>
                                <div class="requirement unmet" id="reqLower">
                                    <i class="fas fa-times"></i>
                                    <span>حرف صغير واحد على الأقل</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">
                                <i class="fas fa-lock"></i>
                                تأكيد كلمة المرور *
                            </label>
                            <input type="password" name="confirm_password" id="confirmPassword" class="form-control" 
                                   placeholder="أعد إدخال كلمة المرور" required
                                   oninput="checkPasswordMatch()">
                            <div class="password-match text-sm mt-1" id="passwordMatch"></div>
                        </div>
                    </div>
                    
                    <button type="submit" class="register-button" id="submitButton" disabled>
                        <i class="fas fa-user-plus"></i>
                        إنشاء الحساب
                    </button>
                </form>
                
                <div class="register-footer">
                    <p>
                        لديك حساب بالفعل؟ 
                        <a href="{{ url_for('login') }}">سجل الدخول</a>
                    </p>
                    <p class="mt-2 text-xs">
                        © 2024 InvoiceFlow Pro. جميع الحقوق محفوظة.
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            function checkPasswordStrength() {
                const password = document.getElementById('password').value;
                const strengthBar = document.getElementById('strengthBar');
                const submitButton = document.getElementById('submitButton');
                
                // إعادة تعيين المتطلبات
                document.querySelectorAll('.requirement').forEach(req => {
                    req.classList.remove('met');
                    req.classList.add('unmet');
                    req.querySelector('i').className = 'fas fa-times';
                });
                
                let strength = 0;
                
                // التحقق من الطول
                if (password.length >= 8) {
                    strength++;
                    document.getElementById('reqLength').classList.remove('unmet');
                    document.getElementById('reqLength').classList.add('met');
                    document.getElementById('reqLength').querySelector('i').className = 'fas fa-check';
                }
                
                // التحقق من وجود أرقام
                if (/\d/.test(password)) {
                    strength++;
                    document.getElementById('reqNumber').classList.remove('unmet');
                    document.getElementById('reqNumber').classList.add('met');
                    document.getElementById('reqNumber').querySelector('i').className = 'fas fa-check';
                }
                
                // التحقق من وجود أحرف كبيرة
                if (/[A-Z]/.test(password)) {
                    strength++;
                    document.getElementById('reqUpper').classList.remove('unmet');
                    document.getElementById('reqUpper').classList.add('met');
                    document.getElementById('reqUpper').querySelector('i').className = 'fas fa-check';
                }
                
                // التحقق من وجود أحرف صغيرة
                if (/[a-z]/.test(password)) {
                    strength++;
                    document.getElementById('reqLower').classList.remove('unmet');
                    document.getElementById('reqLower').classList.add('met');
                    document.getElementById('reqLower').querySelector('i').className = 'fas fa-check';
                }
                
                // تحديث شريط القوة
                strengthBar.className = 'strength-bar';
                if (strength === 0) {
                    strengthBar.style.width = '0%';
                } else if (strength === 1) {
                    strengthBar.classList.add('strength-weak');
                } else if (strength === 2) {
                    strengthBar.classList.add('strength-medium');
                } else if (strength === 3) {
                    strengthBar.classList.add('strength-strong');
                } else if (strength === 4) {
                    strengthBar.classList.add('strength-very-strong');
                }
                
                // التحقق من مطابقة كلمة المرور
                checkPasswordMatch();
            }
            
            function checkPasswordMatch() {
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirmPassword').value;
                const matchDiv = document.getElementById('passwordMatch');
                const submitButton = document.getElementById('submitButton');
                
                if (password === '' || confirmPassword === '') {
                    matchDiv.innerHTML = '';
                    submitButton.disabled = true;
                    return;
                }
                
                if (password === confirmPassword) {
                    matchDiv.innerHTML = '<span class="text-success"><i class="fas fa-check"></i> كلمات المرور متطابقة</span>';
                    submitButton.disabled = false;
                } else {
                    matchDiv.innerHTML = '<span class="text-danger"><i class="fas fa-times"></i> كلمات المرور غير متطابقة</span>';
                    submitButton.disabled = true;
                }
            }
            
            // إضافة تأثير عند التحميل
            document.addEventListener('DOMContentLoaded', function() {
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.3s ease';
                
                setTimeout(() => {
                    document.body.style.opacity = '1';
                }, 100);
                
                // تفعيل التحقق الأولي
                checkPasswordStrength();
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html, css=BASE_CSS)

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

# ================== لوحة التحكم المحسنة ==================
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
        
        'overdue_invoices': db.execute_query(
            "SELECT COUNT(*) FROM invoices WHERE user_id = ? AND status = 'pending' AND due_date < DATE('now')",
            (user_id,), fetchone=True
        )['COUNT(*)'] or 0,
        
        'monthly_revenue': db.execute_query(
            "SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE user_id = ? AND status = 'paid' AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')",
            (user_id,), fetchone=True
        )['COALESCE(SUM(total_amount), 0)'] or 0
    }
    
    # الفواتير الأخيرة
    recent_invoices = db.execute_query(
        """SELECT i.*, c.name as client_name 
           FROM invoices i 
           LEFT JOIN clients c ON i.client_id = c.id 
           WHERE i.user_id = ? 
           ORDER BY i.created_at DESC 
           LIMIT 5""",
        (user_id,), fetchall=True
    )
    
    # الإشعارات الحديثة
    recent_notifications = NotificationSystem.get_user_notifications(user_id, limit=3)
    
    # الأنشطة الحديثة
    recent_activities = db.execute_query(
        """SELECT * FROM activities 
           WHERE user_id = ? 
           ORDER BY created_at DESC 
           LIMIT 5""",
        (user_id,), fetchall=True
    )
    
    # العملاء الجدد
    new_clients = db.execute_query(
        """SELECT * FROM clients 
           WHERE user_id = ? 
           ORDER BY created_at DESC 
           LIMIT 3""",
        (user_id,), fetchall=True
    )
    
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
            <div class="stat-change positive">
                <i class="fas fa-arrow-up"></i>
                12% {t('from_last_month')}
            </div>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-dollar-sign"></i>
            </div>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p class="stat-label">{t('total_revenue')}</p>
            <div class="stat-change positive">
                <i class="fas fa-arrow-up"></i>
                18% {t('from_last_month')}
            </div>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-clock"></i>
            </div>
            <div class="stat-number">{stats['pending_invoices']}</div>
            <p class="stat-label">{t('pending_invoices')}</p>
            <div class="stat-change negative">
                <i class="fas fa-arrow-down"></i>
                5% {t('from_last_week')}
            </div>
        </div>
        
        <div class="card stat-card">
            <div class="stat-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-number">{stats['total_clients']}</div>
            <p class="stat-label">{t('total_clients')}</p>
            <div class="stat-change positive">
                <i class="fas fa-arrow-up"></i>
                8% {t('new_clients')}
            </div>
        </div>
    </div>
    
    <div class="grid grid-2 gap-6 mb-6">
        <!-- الإجراءات السريعة -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">{t('quick_actions')}</h3>
            </div>
            <div class="grid grid-2 gap-4">
                <a href="{{ url_for('create_invoice') }}" class="btn btn-primary">
                    <i class="fas fa-plus-circle"></i>
                    {t('create_invoice')}
                </a>
                
                <a href="{{ url_for('clients') }}" class="btn btn-outline">
                    <i class="fas fa-user-plus"></i>
                    {t('add_client')}
                </a>
                
                <a href="{{ url_for('products') }}" class="btn btn-outline">
                    <i class="fas fa-box"></i>
                    {t('add_product')}
                </a>
                
                <a href="{{ url_for('reports') }}" class="btn btn-outline">
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
                    <span class="font-bold">{stats['monthly_revenue'] / 1000 if stats['monthly_revenue'] > 0 else 0}K</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">{t('revenue_this_month')}:</span>
                    <span class="font-bold text-success">${stats['monthly_revenue']:,.0f}</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">{t('new_clients')}:</span>
                    <span class="font-bold">{len(new_clients)}</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-muted">{t('collection_rate')}:</span>
                    <span class="font-bold text-warning">{
                        f"{((stats['total_invoices'] - stats['pending_invoices']) / stats['total_invoices'] * 100):.1f}%" 
                        if stats['total_invoices'] > 0 else "0%"
                    }</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- الفواتير الأخيرة -->
    <div class="card mb-6">
        <div class="card-header">
            <h3 class="card-title">{t('recent_invoices')}</h3>
            <a href="{{ url_for('invoices') }}" class="btn btn-sm btn-outline">
                {t('view_all')} <i class="fas fa-arrow-left"></i>
            </a>
        </div>
        
        <div class="table-container">
            <table class="table">
                <thead>
                    <tr>
                        <th>{t('invoice_number')}</th>
                        <th>{t('client')}</th>
                        <th>{t('date')}</th>
                        <th>{t('amount')}</th>
                        <th>{t('status')}</th>
                        <th>{t('actions')}</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td class="font-medium">{inv['invoice_number']}</td>
                        <td>{inv['client_name'] or t('no_client')}</td>
                        <td>{inv['issue_date']}</td>
                        <td class="font-bold">${inv['total_amount']:,.2f}</td>
                        <td>
                            <span class="badge {{
                                'badge-success' if inv['status'] == 'paid' else 
                                'badge-warning' if inv['status'] == 'pending' else 
                                'badge-error' if inv['status'] == 'overdue' else 
                                'badge-info'
                            }}">
                                {{
                                    t('paid') if inv['status'] == 'paid' else 
                                    t('pending') if inv['status'] == 'pending' else 
                                    t('overdue') if inv['status'] == 'overdue' else 
                                    t('cancelled')
                                }}
                            </span>
                        </td>
                        <td>
                            <div class="flex gap-2">
                                <a href="/api/invoice/download/{inv['id']}" class="icon-button icon-button-primary" title="{t('download')}">
                                    <i class="fas fa-download"></i>
                                </a>
                                <a href="/api/invoice/preview/{inv['id']}" class="icon-button" title="{t('preview')}">
                                    <i class="fas fa-eye"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    ''' for inv in recent_invoices]) if recent_invoices else f'''
                    <tr>
                        <td colspan="6" class="text-center p-6 text-muted">
                            <i class="fas fa-file-invoice-dollar text-3xl mb-3"></i>
                            <p>{t('no_invoices')}</p>
                            <a href="{{ url_for('create_invoice') }}" class="btn btn-primary mt-3">
                                {t('create_first_invoice')}
                            </a>
                        </td>
                    </tr>
                    '''}
                </tbody>
            </table>
        </div>
    </div>
    
    <!-- الأنشطة والإشعارات -->
    <div class="grid grid-2 gap-6">
        <!-- الأنشطة الحديثة -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">{t('recent_activity')}</h3>
            </div>
            <div class="space-y-3">
                {"".join([f'''
                <div class="flex items-center gap-3 p-3 bg-dark-card rounded-lg">
                    <div class="avatar bg-gradient-primary">
                        <i class="fas fa-{{
                            'user' if act['action'] == 'login' else
                            'file-invoice' if 'invoice' in act['action'] else
                            'users' if 'client' in act['action'] else
                            'box' if 'product' in act['action'] else
                            'cog'
                        }}"></i>
                    </div>
                    <div class="flex-1">
                        <p class="font-medium">{act['description']}</p>
                        <p class="text-xs text-muted">{get_time_ago(act['created_at'])}</p>
                    </div>
                </div>
                ''' for act in recent_activities]) if recent_activities else f'''
                <div class="text-center p-6 text-muted">
                    <i class="fas fa-history text-3xl mb-3"></i>
                    <p>{t('no_recent_activity')}</p>
                </div>
                '''}
            </div>
        </div>
        
        <!-- الإشعارات الحديثة -->
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">{t('recent_notifications')}</h3>
                <a href="#" onclick="markAllNotificationsAsRead()" class="btn btn-sm btn-outline">
                    {t('mark_all_as_read')}
                </a>
            </div>
            <div class="space-y-3">
                {generate_notifications_list(recent_notifications)}
            </div>
        </div>
    </div>
    """
    
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(
        get_dashboard_template(
            t('dashboard'),
            t('welcome_to_dashboard'),
            content,
            lang
        ),
        css=BASE_CSS,
        generate_notifications_list=generate_notifications_list,
        get_time_ago=get_time_ago,
        datetime=datetime,
        t=t
    )

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
        print("🔹 /invoices - إدارة الفواتير")
        print("🔹 /invoices/create - إنشاء فاتورة")
        print("🔹 /clients - إدارة العملاء")
        print("🔹 /products - المنتجات والخدمات")
        print("🔹 /reports - التقارير والإحصائيات")
        print("🔹 /ai - الذكاء الاصطناعي")
        print("🔹 /profile - الملف الشخصي")
        print("🔹 /settings - الإعدادات")
        print("🔹 /logout - تسجيل الخروج")
        print("\n🔧 واجهات API:")
        print("🔹 /api/set-language - تحديث اللغة")
        print("🔹 /api/notifications/* - إدارة الإشعارات")
        print("🔹 /api/invoice/generate - إنشاء فاتورة")
        print("🔹 /api/ai/analyze - تحليل ذكاء اصطناعي")
        print("\n👑 فريق العمل المحترف - النسخة الاحترافية")
        print("="*80)
        
        # تشغيل الخادم
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ خطأ في التشغيل: {e}")
        import traceback
        traceback.print_exc()
        print("🔄 إعادة المحاولة خلال 5 ثوان...")
        time.sleep(5)
