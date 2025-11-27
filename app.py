# 📁 تطوير واجهة التقارير المتقدمة

@app.route('/reports')
def enhanced_reports():
    """واجهة التقارير المحسنة"""
    if 'user_logged_in' not in session:
        return redirect(url_for('login'))
    
    stats = invoice_manager.get_user_stats(session['username'])
    invoices = invoice_manager.get_user_invoices(session['username'])
    
    # تحليل البيانات للإحصائيات
    analysis = analyze_financial_data(invoices)
    
    content = f"""
    <div class="dashboard-header">
        <h1><i class="fas fa-chart-bar"></i> التقارير والتحليلات المتقدمة</h1>
        <p>رؤى شاملة وأدوات تحليل متقدمة لأعمالك</p>
    </div>

    <!-- بطاقات الإحصائيات السريعة -->
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white;">
            <i class="fas fa-receipt"></i>
            <div class="stat-number">{stats['total_invoices']}</div>
            <p>إجمالي الفواتير</p>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #0D9488, #0F766E); color: white;">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-number">${stats['total_revenue']:,.0f}</div>
            <p>إجمالي الإيرادات</p>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #059669, #047857); color: white;">
            <i class="fas fa-percentage"></i>
            <div class="stat-number">${stats['tax_amount']:,.0f}</div>
            <p>إجمالي الضرائب</p>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, #7C3AED, #6D28D9); color: white;">
            <i class="fas fa-trend-up"></i>
            <div class="stat-number">+{analysis['growth_rate']}%</div>
            <p>معدل النمو</p>
        </div>
    </div>

    <!-- لوحة التحليلات المتقدمة -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 25px; margin-top: 25px;">
        <!-- التحليلات الرئيسية -->
        <div class="content-section">
            <h3 style="margin-bottom: 20px; color: var(--primary-dark); display: flex; align-items: center;">
                <i class="fas fa-chart-line" style="margin-left: 10px; color: var(--accent-blue);"></i>
                نظرة عامة على الأداء
            </h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <div style="background: var(--light-gray); padding: 20px; border-radius: 12px;">
                    <h4 style="color: var(--accent-blue); margin-bottom: 10px;">📈 أداء الفواتير</h4>
                    <p>• متوسط الفاتورة: <b>${analysis['avg_invoice']:,.2f}</b></p>
                    <p>• أكبر فاتورة: <b>${analysis['max_invoice']:,.2f}</b></p>
                    <p>• أصغر فاتورة: <b>${analysis['min_invoice']:,.2f}</b></p>
                </div>
                
                <div style="background: var(--light-gray); padding: 20px; border-radius: 12px;">
                    <h4 style="color: var(--accent-teal); margin-bottom: 10px;">💰 التحليل المالي</h4>
                    <p>• الإيرادات الشهرية: <b>${analysis['monthly_revenue']:,.2f}</b></p>
                    <p>• المصروفات الضريبية: <b>${stats['tax_amount']:,.2f}</b></p>
                    <p>• صافي الإيرادات: <b>${analysis['net_revenue']:,.2f}</b></p>
                </div>
            </div>
            
            <!-- جدول الفواتير -->
            <h4 style="margin-bottom: 15px; color: var(--primary-dark);">
                <i class="fas fa-table" style="margin-left: 8px;"></i>
                أحدث الفواتير
            </h4>
            
            <div style="overflow-x: auto;">
                <table class="services-table">
                    <thead>
                        <tr>
                            <th>رقم الفاتورة</th>
                            <th>العميل</th>
                            <th>التاريخ</th>
                            <th>المبلغ</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_invoices_table(invoices)}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- اللوحة الجانبية -->
        <div>
            <!-- تحليل سريع -->
            <div class="content-section">
                <h4 style="margin-bottom: 15px; color: var(--primary-dark); display: flex; align-items: center;">
                    <i class="fas fa-bolt" style="margin-left: 8px; color: var(--warning);"></i>
                    تحليل سريع
                </h4>
                <div style="color: var(--light-slate); line-height: 2;">
                    <p>📊 <b>{stats['total_invoices']}</b> فاتورة تم إنشاؤها</p>
                    <p>💰 <b>${stats['total_revenue']:,.2f}</b> إجمالي الإيرادات</p>
                    <p>⏳ <b>{stats['pending_invoices']}</b> فاتورة قيد المعالجة</p>
                    <p>✅ <b>${stats['paid_amount']:,.2f}</b> تم تحصيلها</p>
                    <p>🎯 <b>{analysis['growth_rate']}%</b> معدل النمو</p>
                </div>
            </div>
            
            <!-- أدوات سريعة -->
            <div class="content-section">
                <h4 style="margin-bottom: 15px; color: var(--primary-dark); display: flex; align-items: center;">
                    <i class="fas fa-tools" style="margin-left: 8px; color: var(--accent-teal);"></i>
                    أدوات سريعة
                </h4>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="btn" onclick="exportToPDF()" style="background: var(--accent-blue);">
                        <i class="fas fa-file-pdf"></i> تصدير تقرير PDF
                    </button>
                    <button class="btn btn-secondary" onclick="showRevenueChart()">
                        <i class="fas fa-chart-bar"></i> عرض مخطط الإيرادات
                    </button>
                    <button class="btn btn-secondary" onclick="generateMonthlyReport()">
                        <i class="fas fa-calendar"></i> تقرير شهري
                    </button>
                </div>
            </div>
            
            <!-- نصائح المساعد الذكي -->
            <div class="content-section" style="background: linear-gradient(135deg, #0F172A, #1E293B); color: white;">
                <h4 style="margin-bottom: 15px; color: #0D9488; display: flex; align-items: center;">
                    <i class="fas fa-robot" style="margin-left: 8px;"></i>
                    نصائح ذكية
                </h4>
                <div style="font-size: 0.9em; line-height: 1.6;">
                    <p>🎯 {get_ai_tip(stats)}</p>
                    <p>💡 {get_ai_tip2(stats)}</p>
                    <p>🚀 {get_ai_tip3(analysis)}</p>
                </div>
            </div>
        </div>
    </div>

    <style>
        .stat-card {
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .services-table {
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
        }
        
        .services-table th,
        .services-table td {
            padding: 12px 15px;
            text-align: right;
            border-bottom: 1px solid var(--border-light);
        }
        
        .services-table th {
            background: var(--light-gray);
            font-weight: 600;
            color: var(--primary-dark);
        }
        
        .services-table tr:hover {
            background: var(--light-gray);
        }
    </style>

    <script>
        function exportToPDF() {
            alert('سيتم تنفيذ تصدير PDF في الإصدار القادم');
        }
        
        function showRevenueChart() {
            alert('مخططات الإيرادات التفاعلية قريباً في التحديث القادم');
        }
        
        function generateMonthlyReport() {
            alert('التقارير الشهرية الآلية قريباً في التحديث القادم');
        }
    </script>
    """
    
    uptime = time.time() - monitor.uptime_start
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    uptime_str = f"{hours} ساعة {minutes} دقيقة"
    
    return render_template_string(PROFESSIONAL_DESIGN, title="التقارير - InvoiceFlow Pro", 
                                uptime=uptime_str, content=content, is_auth_page=False)

def analyze_financial_data(invoices):
    """تحليل البيانات المالية"""
    if not invoices:
        return {
            'avg_invoice': 0,
            'max_invoice': 0,
            'min_invoice': 0,
            'monthly_revenue': 0,
            'net_revenue': 0,
            'growth_rate': 0
        }
    
    amounts = [inv['amount'] for inv in invoices]
    
    return {
        'avg_invoice': sum(amounts) / len(amounts),
        'max_invoice': max(amounts),
        'min_invoice': min(amounts),
        'monthly_revenue': sum(amounts) * 0.3,  # تقدير شهري
        'net_revenue': sum(amounts) * 0.85,     # تقدير صافي
        'growth_rate': min(25, len(invoices) * 2)  # نمو تقديري
    }

def generate_invoices_table(invoices):
    """إنشاء جدول الفواتير"""
    if not invoices:
        return '''
        <tr>
            <td colspan="6" style="text-align: center; padding: 20px; color: var(--light-slate);">
                <i class="fas fa-receipt" style="font-size: 2em; margin-bottom: 10px; display: block; opacity: 0.5;"></i>
                لا توجد فواتير لعرضها
            </td>
        </tr>
        '''
    
    html = ""
    for inv in invoices[:10]:  # عرض 10 فواتير كحد أقصى
        payment_class = 'مدفوع' if inv.get('payment_status') == 'مدفوع' else 'غير_مدفوع'
        status_class = inv['status']
        
        html += f"""
        <tr>
            <td><strong>{inv['number']}</strong></td>
            <td>{inv['client']}</td>
            <td>{inv['issue_date']}</td>
            <td style="font-weight: bold; color: var(--accent-blue);">${inv['amount']:,.2f}</td>
            <td><span class="status-badge {status_class}">{inv['status']}</span></td>
            <td>
                <a href="/invoices/{inv['number']}/pdf" class="btn-action" style="background: var(--accent-blue); color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8em;">
                    <i class="fas fa-download"></i> PDF
                </a>
            </td>
        </tr>
        """
    
    return html

def get_ai_tip(stats):
    """نصائح ذكية من المساعد"""
    if stats['total_invoices'] == 0:
        return "ابدأ بإنشاء فاتورتك الأولى اليوم لترى تحليلات مفصلة"
    elif stats['total_invoices'] < 5:
        return "رائع! استمر في إضافة الفواتير لتحصل على تحليلات أكثر دقة"
    else:
        return "أداؤك ممتاز! فكر في توسيع قاعدة عملائك لزيادة الإيرادات"

def get_ai_tip2(stats):
    """نصيحة ذكية ثانية"""
    if stats['pending_invoices'] > 0:
        return "راجع الفواتير المعلقة لتحسين التدفق النقدي"
    else:
        return "جميع فواتيرك مسددة - هذا ممتاز للتدفق النقدي"

def get_ai_tip3(analysis):
    """نصيحة ذكية ثالثة"""
    if analysis['growth_rate'] > 15:
        return "معدل نموك ممتاز! استمر في هذا الأداء الرائع"
    else:
        return "هناك مجال لتحسين النمو - راجع استراتيجية التسعير"
