#!/usr/bin/env python3
"""
فريق العمل الشامل - نظام الإصلاح الشامل
الإصدار: 1.0.0
التاريخ: 2024
الفريق: البروفيسور عامر، الذكاء الاصطناعي، المهندس خالد، الدكتورة سارة
"""

import re
import sys
import os
from datetime import datetime

class TeamWorkFixer:
    """فريق العمل الشامل للإصلاح"""
    
    def __init__(self, file_path="bot_arabic.py"):
        self.file_path = file_path
        self.backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixes_applied = 0
        self.problems_found = []
        
        print("=" * 70)
        print("👥 فريق العمل الشامل يبدأ المهمة")
        print("=" * 70)
        print("الأعضاء: البروفيسور عامر | الذكاء الاصطناعي | المهندس خالد | الدكتورة سارة")
        print("=" * 70)
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        print("📁 العضو: المهندس خالد - إنشاء نسخة احتياطية...")
        try:
            import shutil
            shutil.copy2(self.file_path, self.backup_path)
            print(f"✅ تم إنشاء نسخة احتياطية: {self.backup_path}")
            return True
        except Exception as e:
            print(f"❌ فشل في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def analyze_problems(self):
        """تحليل المشاكل - البروفيسور عامر"""
        print("\n🔍 العضو: البروفيسور عامر - تحليل المشاكل...")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # أنواع المشاكل للبحث عنها
            problem_patterns = [
                (r'\{\{[^}]*?\.format\([^)]+\)[^}]*?\}\}', 'format_in_template', 'مشكلة: .format() داخل template'),
                (r'\{\{[^}]*?\{\}[^}]*?\}\}', 'curly_braces', 'مشكلة: {} داخل template'),
                (r'\{\{\{\{', 'double_open', 'مشكلة: {{{{'),
                (r'\}\}\}\}', 'double_close', 'مشكلة: }}}}'),
                (r'f\'[^\']*\{\}[^\']*\'', 'f_string_braces', 'مشكلة: f-string مع {}'),
            ]
            
            for i, line in enumerate(lines, 1):
                for pattern, ptype, pdesc in problem_patterns:
                    if re.search(pattern, line):
                        self.problems_found.append({
                            'line': i,
                            'type': ptype,
                            'desc': pdesc,
                            'content': line.strip()[:80] + '...' if len(line) > 80 else line.strip()
                        })
            
            print(f"✅ تم العثور على {len(self.problems_found)} مشكلة")
            
            if self.problems_found:
                print("\n📋 قائمة المشاكل:")
                for problem in self.problems_found[:10]:  # عرض أول 10 مشاكل فقط
                    print(f"   السطر {problem['line']}: {problem['desc']}")
                if len(self.problems_found) > 10:
                    print(f"   ... و {len(self.problems_found) - 10} مشكلة أخرى")
            
            return True
            
        except Exception as e:
            print(f"❌ فشل في التحليل: {e}")
            return False
    
    def fix_specific_line(self, line_number, original_line):
        """إصلاح سطر محدد - الدكتورة سارة"""
        fixed_line = original_line
        
        # الإصلاحات المحددة
        if line_number == 5495:
            print(f"🔧 العضو: الدكتورة سارة - إصلاح السطر {line_number}...")
            # السطر 5495 المحدد
            fixed_line = original_line.replace(
                ".format(notification['id'])", ""
            ).replace(
                "{}", "' ~ notification['id']|string ~ '"
            )
        
        elif line_number == 5288:
            print(f"🔧 العضو: الدكتورة سارة - إصلاح السطر {line_number}...")
            # السطر 5288 المحدد
            fixed_line = original_line.replace(
                ".format(notification_count)", ""
            ).replace(
                "{}", "' ~ notification_count|string ~ '"
            )
        
        # الإصلاحات العامة
        elif '.format(' in original_line and '{{' in original_line:
            print(f"🔧 العضو: الدكتورة سارة - إصلاح السطر {line_number}...")
            # استخراج اسم المتغير من .format()
            match = re.search(r'\.format\(([^)]+)\)', original_line)
            if match:
                var_name = match.group(1)
                fixed_line = original_line.replace(
                    f".format({var_name})", ""
                ).replace(
                    "{}", f"' ~ {var_name}|string ~ '"
                )
        
        # تنظيف الأقواس المزدوجة
        fixed_line = fixed_line.replace('{{{{', '{{').replace('}}}}', '}}')
        
        return fixed_line
    
    def apply_all_fixes(self):
        """تطبيق جميع الإصلاحات - الذكاء الاصطناعي"""
        print("\n🤖 العضو: الذكاء الاصطناعي - تطبيق الإصلاحات...")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            fixed_lines = []
            for i, line in enumerate(lines, 1):
                original_line = line
                fixed_line = self.fix_specific_line(i, line)
                
                if fixed_line != original_line:
                    self.fixes_applied += 1
                    print(f"   ✅ تم إصلاح السطر {i}")
                
                fixed_lines.append(fixed_line)
            
            # حفظ الملف المصلح
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            print(f"\n✅ تم تطبيق {self.fixes_applied} إصلاح")
            return True
            
        except Exception as e:
            print(f"❌ فشل في تطبيق الإصلاحات: {e}")
            return False
    
    def verify_fixes(self):
        """التحقق من الإصلاحات - الفريق بأكمله"""
        print("\n🔍 الفريق بأكمله - التحقق النهائي...")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # التحقق من عدم وجود .format() داخل templates
            remaining_problems = re.findall(r'\{\{[^}]*?\.format\([^)]+\)[^}]*?\}\}', content)
            
            if not remaining_problems:
                print("✅ التحقق 1: لا توجد .format() داخل templates ✓")
            else:
                print(f"❌ التحقق 1: لا يزال هناك {len(remaining_problems)} مشكلة")
                return False
            
            # التحقق من صحة بناء الجملة
            try:
                compile(content, self.file_path, 'exec')
                print("✅ التحقق 2: بناء الجملة صحيح ✓")
            except SyntaxError as e:
                print(f"❌ التحقق 2: خطأ في بناء الجملة: {e}")
                return False
            
            print("\n🎉 جميع عمليات التحقق نجحت!")
            return True
            
        except Exception as e:
            print(f"❌ فشل في التحقق: {e}")
            return False
    
    def run_complete_fix(self):
        """تشغيل الإصلاح الشامل"""
        print("\n🚀 بدء الإصلاح الشامل...")
        
        steps = [
            ("النسخ الاحتياطي", self.create_backup),
            ("تحليل المشاكل", self.analyze_problems),
            ("تطبيق الإصلاحات", self.apply_all_fixes),
            ("التحقق النهائي", self.verify_fixes),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📌 الخطوة: {step_name}")
            if not step_func():
                print(f"❌ فشلت الخطوة: {step_name}")
                return False
        
        print("\n" + "=" * 70)
        print("🎉 الإصلاح الشامل مكتمل بنجاح!")
        print(f"📊 الإحصائيات:")
        print(f"   - المشاكل الموجودة: {len(self.problems_found)}")
        print(f"   - الإصلاحات المطبقة: {self.fixes_applied}")
        print(f"   - النسخة الاحتياطية: {self.backup_path}")
        print("=" * 70)
        
        return True

def main():
    """الدالة الرئيسية"""
    if len(sys.argv) > 1:
        file_to_fix = sys.argv[1]
    else:
        file_to_fix = "bot_arabic.py"
    
    if not os.path.exists(file_to_fix):
        print(f"❌ الملف {file_to_fix} غير موجود")
        return False
    
    fixer = TeamWorkFixer(file_to_fix)
    return fixer.run_complete_fix()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
