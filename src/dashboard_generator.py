#!/usr/bin/env python3
"""
Advanced CRO Intelligence Dashboard Generator
مولد داشبورد تفاعلي لعرض نتائج التحليل
"""

import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import webbrowser
import os

class CRODashboardGenerator:
    def __init__(self):
        self.data_dir = "data"
        self.output_dir = "dashboard"
        self.dashboard_data = {}
        
    def load_all_data(self):
        """تحميل جميع بيانات التحليل"""
        try:
            # تحميل بيانات ScraperAI
            with open(os.path.join(self.data_dir, "dnmeg_analysis.json"), 'r', encoding='utf-8') as f:
                self.dashboard_data['scraper'] = json.load(f)
            
            # تحميل بيانات الأداء
            with open(os.path.join(self.data_dir, "dnmeg_performance_analysis.json"), 'r', encoding='utf-8') as f:
                self.dashboard_data['performance'] = json.load(f)
            
            # تحميل بيانات سلوك المستخدم
            with open(os.path.join(self.data_dir, "dnmeg_user_behavior_analysis.json"), 'r', encoding='utf-8') as f:
                self.dashboard_data['behavior'] = json.load(f)
            
            # تحميل بيانات الخروج
            with open(os.path.join(self.data_dir, "dnmeg_checkout_analysis.json"), 'r', encoding='utf-8') as f:
                self.dashboard_data['checkout'] = json.load(f)
            
            # تحميل بيانات المراجعات والمخزون
            with open(os.path.join(self.data_dir, "dnmeg_reviews_inventory_analysis.json"), 'r', encoding='utf-8') as f:
                self.dashboard_data['reviews_inventory'] = json.load(f)
                
            return True
        except Exception as e:
            print(f"❌ خطأ في تحميل البيانات: {e}")
            return False
    
    def create_overview_kpi_cards(self):
        """إنشاء بطاقات KPI للنظرة العامة"""
        kpi_data = []
        
        # KPI من بيانات ScraperAI
        scraper_data = self.dashboard_data.get('scraper', {})
        products = scraper_data.get('products', [])
        
        kpi_data.append({
            'title': 'إجمالي المنتجات',
            'value': len(products),
            'icon': '📦',
            'color': '#1f77b4',
            'trend': 'stable'
        })
        
        # KPI من بيانات الأداء
        perf_data = self.dashboard_data.get('performance', {})
        homepage_load = perf_data.get('page_load_times', {}).get('homepage', {}).get('load_time', 0)
        
        kpi_data.append({
            'title': 'سرعة التحميل (ثانية)',
            'value': f"{homepage_load:.2f}",
            'icon': '⚡',
            'color': '#2ca02c',
            'trend': 'good' if homepage_load < 1 else 'warning'
        })
        
        # KPI من بيانات سلوك المستخدم
        behavior_data = self.dashboard_data.get('behavior', {})
        funnel = behavior_data.get('conversion_funnel', {})
        conversion_rate = funnel.get('conversion_rate', 0)
        
        kpi_data.append({
            'title': 'معدل التحويل (%)',
            'value': f"{conversion_rate:.1f}",
            'icon': '📈',
            'color': '#d62728',
            'trend': 'critical' if conversion_rate == 0 else 'normal'
        })
        
        # KPI من بيانات المخزون
        inv_data = self.dashboard_data.get('reviews_inventory', {}).get('inventory_analysis', {})
        out_of_stock = inv_data.get('out_of_stock_analysis', {})
        oos_percentage = out_of_stock.get('out_of_stock_percentage', 0)
        
        kpi_data.append({
            'title': 'المنتجات النافدة (%)',
            'value': f"{oos_percentage:.1f}",
            'icon': '🚨',
            'color': '#ff7f0e',
            'trend': 'critical' if oos_percentage > 50 else 'warning'
        })
        
        return kpi_data
    
    def create_conversion_funnel_chart(self):
        """إنشاء مخطط قمع التحويل"""
        behavior_data = self.dashboard_data.get('behavior', {})
        funnel = behavior_data.get('conversion_funnel', {})
        
        fig = go.Figure(go.Funnel(
            y = [
                'زوار الصفحة الرئيسية',
                'مستكشفو المنتجات', 
                'عارضو المنتجات',
                'مضافو السلة',
                'مبدئو الخروج',
                'المحولون'
            ],
            x = [
                funnel.get('homepage_visitors', 0),
                funnel.get('product_browsers', 0),
                funnel.get('product_viewers', 0),
                funnel.get('cart_adders', 0),
                funnel.get('checkout_starters', 0),
                funnel.get('converted_users', 0)
            ],
            textposition = "inside",
            textinfo = "value+percent initial",
            marker = {"color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]},
            connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}},
            insidetextfont = {"color": "white", "size": 14}
        ))
        
        fig.update_layout(
            title="🎯 قمع التحويل",
            font=dict(size=12, color='white'),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            height=600
        )
        
        return fig
    
    def create_performance_chart(self):
        """إنشاء مخطط الأداء التقني"""
        perf_data = self.dashboard_data.get('performance', {})
        load_times = perf_data.get('page_load_times', {})
        
        pages = []
        times = []
        
        for page, data in load_times.items():
            if isinstance(data, dict) and 'load_time' in data:
                pages.append(page.replace('_', ' ').title())
                times.append(data['load_time'])
        
        fig = go.Figure(data=[
            go.Bar(
                x=pages,
                y=times,
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'],
                text=[f"{t:.2f}s" for t in times],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="⚡ أداء تحميل الصفحات",
            xaxis_title="الصفحة",
            yaxis_title="وقت التحميل (ثانية)",
            font=dict(size=12, color='white'),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            height=500
        )
        
        return fig
    
    def create_inventory_status_chart(self):
        """إنشاء مخطط حالة المخزون"""
        inv_data = self.dashboard_data.get('reviews_inventory', {}).get('inventory_analysis', {})
        out_of_stock = inv_data.get('out_of_stock_analysis', {})
        
        labels = ['متوفر', 'نافد', 'مخزون منخفض']
        values = [
            out_of_stock.get('in_stock_percentage', 0),
            out_of_stock.get('out_of_stock_percentage', 0),
            len(out_of_stock.get('low_stock_products', []))
        ]
        colors = ['#2ca02c', '#d62728', '#ff7f0e']
        
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_size=12,
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title="📦 حالة المخزون",
            font=dict(size=12, color='white'),
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#2d2d2d',
            height=500
        )
        
        return fig
    
    def generate_html_dashboard(self):
        """توليد داشبورد HTML كامل"""
        if not self.load_all_data():
            return None
        
        # إنشاء المخططات
        kpi_cards = self.create_overview_kpi_cards()
        funnel_chart = self.create_conversion_funnel_chart()
        performance_chart = self.create_performance_chart()
        inventory_chart = self.create_inventory_status_chart()
        
        # توليد HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 CRO Intelligence Dashboard - DNM.EG</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .kpi-card {{
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .kpi-icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        
        .kpi-title {{
            font-size: 1.1em;
            margin-bottom: 10px;
            opacity: 0.9;
        }}
        
        .kpi-value {{
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .kpi-trend {{
            font-size: 0.9em;
            padding: 5px 10px;
            border-radius: 20px;
            background: rgba(255,255,255,0.2);
        }}
        
        .chart-container {{
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            text-align: center;
            color: white;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .last-updated {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .kpi-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CRO Intelligence Dashboard</h1>
            <p>DNM.EG - تحليل شامل للأداء والتحويل</p>
            <p class="last-updated">آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="kpi-grid">
            {self._generate_kpi_cards_html(kpi_cards)}
        </div>
        
        <div class="chart-container">
            <div class="chart-title">🎯 قمع التحويل</div>
            <div id="funnel-chart"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">⚡ أداء تحميل الصفحات</div>
            <div id="performance-chart"></div>
        </div>
        
        <div class="chart-container">
            <div class="chart-title">📦 حالة المخزون</div>
            <div id="inventory-chart"></div>
        </div>
        
        <div class="footer">
            <p>🔧 تم إنشاؤه باستخدام Advanced CRO Intelligence Toolkit</p>
            <p>📊 البيانات مستخرجة من dnmeg.com في {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
    
    <script>
        // عرض مخطط قمع التحويل
        var funnelData = {funnel_chart.to_json()};
        Plotly.newPlot('funnel-chart', funnelData.data, funnelData.layout);
        
        // عرض مخطط الأداء
        var performanceData = {performance_chart.to_json()};
        Plotly.newPlot('performance-chart', performanceData.data, performanceData.layout);
        
        // عرض مخطط المخزون
        var inventoryData = {inventory_chart.to_json()};
        Plotly.newPlot('inventory-chart', inventoryData.data, inventoryData.layout);
    </script>
</body>
</html>
        """
        
        # حفظ الملف
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, "dashboard.html")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_kpi_cards_html(self, kpi_cards):
        """توليد HTML لبطاقات KPI"""
        cards_html = ""
        
        for card in kpi_cards:
            trend_emoji = {
                'good': '📈',
                'warning': '⚠️',
                'critical': '🚨',
                'stable': '➡️'
            }.get(card['trend'], '➡️')
            
            cards_html += f"""
            <div class="kpi-card">
                <div class="kpi-icon">{card['icon']}</div>
                <div class="kpi-title">{card['title']}</div>
                <div class="kpi-value" style="color: {card['color']}">{card['value']}</div>
                <div class="kpi-trend">{trend_emoji} {card['trend'].title()}</div>
            </div>
            """
        
        return cards_html
    
    def generate_and_open_dashboard(self):
        """توليد وفتح الداشبورد"""
        print("🚀 جاري توليد داشبورد CRO Intelligence...")
        
        dashboard_path = self.generate_html_dashboard()
        
        if dashboard_path:
            print(f"✅ تم إنشاء الداشبورد بنجاح!")
            print(f"📁 المسار: {dashboard_path}")
            
            # فتح الداشبورد في المتصفح
            abs_path = os.path.abspath(dashboard_path)
            webbrowser.open(f'file://{abs_path}')
            
            print("🌐 تم فتح الداشبورد في المتصفح")
            return True
        else:
            print("❌ فشل في إنشاء الداشبورد")
            return False

def main():
    """الوظيفة الرئيسية"""
    dashboard = CRODashboardGenerator()
    dashboard.generate_and_open_dashboard()

if __name__ == "__main__":
    main()
