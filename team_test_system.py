#!/usr/bin/env python3
"""
فريق الاختبار الشامل - نظام التحقق من الإصلاح
الإصدار: 1.0.0
التاريخ: 2024
الفريق: الدكتورة نور، المهندس باسل، المهندسة لينا
"""

import re
import subprocess
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

class QualityTeam:
    """فريق الجودة والاختبار"""
    
    def __init__(self, file_path="bot_arabic.py"):
        self.file_path = file_path
        self.test_results = []
        
        print(Fore.CYAN + "=" * 70)
        print(Fore.CYAN + "🧪 فريق الجودة والاختبار يبدأ العمل")
        print(Fore.CYAN + "=" * 70)
        print(Fore.YELLOW + "الأعضاء: الدكتورة نور | المهندس باسل | المهندسة لينا")
        print(Fore.CYAN + "=" * 70)
    
    def run_test(self, test_name, test_func):
        """تشغيل اختبار واحد"""
        try:
            print(f"\n🔍 اختبار: {test_name}")
            result = test_func()
            if result:
                self.test_results.append((test_name, True, "✅ ناجح"))
                print(Fore.GREEN + f"   ✅ {test_name}: ناجح")
                return True
            else:
                self.test_results.append((test_name, False, "❌ فشل"))
                print(Fore.RED + f"   ❌ {test_name}: فشل")
                return False
        except Exception as e:
            self.test_results.append((test_name, False, f"⚠️ خطأ: {str(e)}"))
            print(Fore.RED + f"   ⚠️ {test_name}: خطأ - {e}")
            return False
    
    def test_syntax_errors(self):
        """اختبار أخطاء بناء الجملة - المهندس باسل"""
        print("👨‍🔬 المهندس باسل: اختبار بناء الجملة...")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, self.file_path, 'exec')
            return True
        except SyntaxError as e:
            print(f"   خطأ في السطر {e.lineno}: {e.msg}")
            return False
    
    def test_format_in_templates(self):
        """اختبار .format() في templates - المهندسة لينا"""
        print("👩‍🔬 المهندسة لينا: اختبار templates...")
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # البحث عن .format() داخل {{ }}
        matches = re.findall(r'\{\{[^}]*?\.format\([^)]+\)[^}]*?\}\}', content)
        
        if matches:
            print(f"   وجد {len(matches)} مشكلة:")
            for match in matches[:3]:
                print(f"   - {match[:50]}...")
            return False
        return True
    
    def test_specific_lines(self):
        """اختبار السطور المحددة - الدكتورة نور"""
        print("👩‍⚕️ الدكتورة نور: اختبار السطور المهمة...")
        
        test_cases = [
            (5495, ".format(notification['id'])", False, "notification['id']|string"),
            (5288, ".format(notification_count)", False, "notification_count|string"),
        ]
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        all_passed = True
        for line_num, bad_pattern, should_have, good_pattern in test_cases:
            if line_num <= len(lines):
                line = lines[line_num-1]
                has_bad = bad_pattern in line
                has_good = good_pattern in line
                
                if has_bad == should_have and has_good:
                    print(f"   ✅ السطر {line_num}: صحيح")
                else:
                    print(f"   ❌ السطر {line_num}: مشكلة")
                    all_passed = False
        
        return all_passed
    
    def test_jinja2_syntax(self):
        """اختبار صيغة Jinja2"""
        print("🤖 اختبار صيغة Jinja2...")
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التحقق من استخدام ~ و |string
        has_tilde = '~' in content
        has_string_filter = '|string' in content
        has_proper_format = has_tilde and has_string_filter
        
        if has_proper_format:
            print("   ✅ صيغة Jinja2 صحيحة")
            return True
        else:
            print(f"   ❌ صيغة Jinja2 غير صحيحة")
            return False
    
    def test_imports(self):
        """اختبار الاستيرادات"""
        print("📦 اختبار الاستيرادات...")
        try:
            # محاولة استيراد الوحدات الأساسية
            import flask
            import jinja2
            import sqlite3
            import json
            print("   ✅ جميع الاستيرادات تعمل")
            return True
        except ImportError as e:
            print(f"   ❌ خطأ في الاستيراد: {e}")
            return False
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        tests = [
            ("بناء الجملة", self.test_syntax_errors),
            ("Templates", self.test_format_in_templates),
            ("السطور المهمة", self.test_specific_lines),
            ("صيغة Jinja2", self.test_jinja2_syntax),
            ("الاستيرادات", self.test_imports),
        ]
        
        print("\n" + "=" * 70)
        print("🚀 بدء جميع الاختبارات...")
        print("=" * 70)
        
        passed = 0
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        print("\n" + "=" * 70)
        print(Fore.CYAN + "📊 تقرير الاختبارات النهائي")
        print("=" * 70)
        
        for test_name, success, message in self.test_results:
            color = Fore.GREEN if success else Fore.RED
            print(f"{color}{message}: {test_name}")
        
        print("\n" + "=" * 70)
        print(Fore.YELLOW + f"النتيجة: {passed}/{len(tests)} اختبار ناجح")
        
        if passed == len(tests):
            print(Fore.GREEN + "🎉 جميع الاختبارات نجحت!")
            return True
        else:
            print(Fore.RED + f"⚠️ {len(tests) - passed} اختبار فشل")
            return False

def main():
    """الدالة الرئيسية"""
    if len(sys.argv) > 1:
        file_to_test = sys.argv[1]
    else:
        file_to_test = "bot_arabic.py"
    
    import os
    if not os.path.exists(file_to_test):
        print(f"❌ الملف {file_to_test} غير موجود")
        return False
    
    team = QualityTeam(file_to_test)
    return team.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
