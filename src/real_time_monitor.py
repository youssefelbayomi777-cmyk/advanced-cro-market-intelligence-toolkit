#!/usr/bin/env python3
"""
Real-time Monitoring System
نظام مراقبة في الوقت الفعلي
"""

import json
import time
import schedule
import requests
from datetime import datetime, timedelta
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import os

class RealTimeMonitor:
    def __init__(self):
        self.base_url = "https://dnmeg.com"
        self.monitoring_data = {
            'uptime_status': {},
            'performance_metrics': {},
            'inventory_alerts': [],
            'conversion_tracking': {},
            'system_health': {}
        }
        self.db_file = 'monitoring_database.db'
        self.setup_database()
        
    def setup_database(self):
        """إعداد قاعدة البيانات"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # إنشاء جداول المراقبة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uptime_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                response_time REAL,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                page_load_time REAL,
                availability_score REAL,
                error_count INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_products INTEGER,
                out_of_stock INTEGER,
                low_stock INTEGER,
                availability_percentage REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_uptime(self):
        """فحص وقت التشغيل"""
        try:
            start_time = time.time()
            response = requests.get(self.base_url, timeout=10)
            response_time = time.time() - start_time
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'status': 'up' if response.status_code == 200 else 'down',
                'response_time': response_time,
                'status_code': response.status_code,
                'error': None
            }
            
            # حفظ في قاعدة البيانات
            self.save_uptime_data(status)
            
            # التحقق من التنبيهات
            if response.status_code != 200:
                self.create_alert('uptime', 'critical', 
                              f"Website is down! Status code: {response.status_code}")
            
            self.monitoring_data['uptime_status'] = status
            
        except Exception as e:
            status = {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'response_time': 0,
                'status_code': None,
                'error': str(e)
            }
            
            self.save_uptime_data(status)
            self.create_alert('uptime', 'critical', f"Website monitoring error: {str(e)}")
            
            self.monitoring_data['uptime_status'] = status
    
    def save_uptime_data(self, status):
        """حفظ بيانات وقت التشغيل"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO uptime_monitoring (status, response_time, error_message)
            VALUES (?, ?, ?)
        ''', (status['status'], status['response_time'], status['error']))
        
        conn.commit()
        conn.close()
    
    def check_performance_metrics(self):
        """فحص مقاييس الأداء"""
        try:
            # محاكاة فحص الأداء
            start_time = time.time()
            response = requests.get(self.base_url, timeout=10)
            load_time = time.time() - start_time
            
            # حساب مقاييس الأداء
            performance_score = self.calculate_performance_score(load_time, response.status_code)
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'page_load_time': load_time,
                'availability_score': performance_score,
                'status_code': response.status_code,
                'error_count': 1 if response.status_code != 200 else 0
            }
            
            # حفظ في قاعدة البيانات
            self.save_performance_data(metrics)
            
            # التحقق من التنبيهات
            if load_time > 3.0:  # بطيء جداً
                self.create_alert('performance', 'high', 
                              f"Slow page load time: {load_time:.2f}s")
            
            if performance_score < 80:  # أداء ضعيف
                self.create_alert('performance', 'medium', 
                              f"Low performance score: {performance_score:.1f}")
            
            self.monitoring_data['performance_metrics'] = metrics
            
        except Exception as e:
            self.create_alert('performance', 'critical', f"Performance monitoring error: {str(e)}")
    
    def calculate_performance_score(self, load_time, status_code):
        """حساب درجة الأداء"""
        score = 100
        
        # خصم بسبب وقت التحميل
        if load_time > 5.0:
            score -= 50
        elif load_time > 3.0:
            score -= 30
        elif load_time > 2.0:
            score -= 15
        elif load_time > 1.0:
            score -= 5
        
        # خصم بسبب حالة الاستجابة
        if status_code != 200:
            score -= 20
        
        return max(0, score)
    
    def save_performance_data(self, metrics):
        """حفظ بيانات الأداء"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics (page_load_time, availability_score, error_count)
            VALUES (?, ?, ?)
        ''', (metrics['page_load_time'], metrics['availability_score'], metrics['error_count']))
        
        conn.commit()
        conn.close()
    
    def check_inventory_status(self):
        """فحص حالة المخزون"""
        try:
            # محاكاة فحص المخزون (في الواقع، سيتم استدعاء API حقيقي)
            total_products = 10  # من بياناتنا السابقة
            out_of_stock = 10  # جميع المنتجات نافدة
            low_stock = 0
            
            availability_percentage = ((total_products - out_of_stock) / total_products) * 100
            
            inventory_data = {
                'timestamp': datetime.now().isoformat(),
                'total_products': total_products,
                'out_of_stock': out_of_stock,
                'low_stock': low_stock,
                'availability_percentage': availability_percentage
            }
            
            # حفظ في قاعدة البيانات
            self.save_inventory_data(inventory_data)
            
            # التحقق من التنبيهات
            if availability_percentage < 20:  # أزمة مخزون
                self.create_alert('inventory', 'critical', 
                              f"Critical inventory shortage: {availability_percentage:.1f}% available")
            elif availability_percentage < 50:  # مخزون منخفض
                self.create_alert('inventory', 'high', 
                              f"Low inventory: {availability_percentage:.1f}% available")
            
            self.monitoring_data['inventory_status'] = inventory_data
            
        except Exception as e:
            self.create_alert('inventory', 'critical', f"Inventory monitoring error: {str(e)}")
    
    def save_inventory_data(self, data):
        """حفظ بيانات المخزون"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO inventory_status (total_products, out_of_stock, low_stock, availability_percentage)
            VALUES (?, ?, ?, ?)
        ''', (data['total_products'], data['out_of_stock'], 
                data['low_stock'], data['availability_percentage']))
        
        conn.commit()
        conn.close()
    
    def create_alert(self, alert_type, severity, message):
        """إنشاء تنبيه"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'severity': severity,
            'message': message,
            'resolved': False
        }
        
        # حفظ في قاعدة البيانات
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, message)
            VALUES (?, ?, ?)
        ''', (alert_type, severity, message))
        
        conn.commit()
        conn.close()
        
        # إرسال الإشعار
        self.send_notification(alert)
        
        # إضافة إلى قائمة التنبيهات الحالية
        self.monitoring_data['alerts'] = self.monitoring_data.get('alerts', [])
        self.monitoring_data['alerts'].append(alert)
    
    def send_notification(self, alert):
        """إرسال إشعار التنبيه"""
        # يمكن إضافة إعدادات البريد الإلكتروني هنا
        email_settings = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'your-email@gmail.com',
            'sender_password': 'your-app-password',
            'recipient_email': 'admin@dnmeg.com'
        }
        
        # في هذا المثال، سنطبع فقط التنبيه
        print(f"🚨 ALERT [{alert['severity'].upper()}]: {alert['message']}")
        print(f"📅 Time: {alert['timestamp']}")
        print(f"🏷️ Type: {alert['type']}")
        
        # هنا يمكن إضافة إرسال بريد إلكتروني حقيقي
        # self.send_email_notification(alert, email_settings)
    
    def send_email_notification(self, alert, email_settings):
        """إرسال إشعار عبر البريد الإلكتروني"""
        try:
            msg = MIMEMultipart()
            msg['From'] = email_settings['sender_email']
            msg['To'] = email_settings['recipient_email']
            msg['Subject'] = f"🚨 {alert['severity'].upper()} Alert: {alert['type']}"
            
            body = f"""
            Alert Details:
            - Type: {alert['type']}
            - Severity: {alert['severity']}
            - Message: {alert['message']}
            - Time: {alert['timestamp']}
            
            Please take immediate action.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port'])
            server.starttls()
            server.login(email_settings['sender_email'], email_settings['sender_password'])
            text = msg.as_string()
            server.sendmail(email_settings['sender_email'], email_settings['recipient_email'], text)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email notification: {e}")
    
    def check_system_health(self):
        """فحص صحة النظام"""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'database_status': 'healthy',
                'monitoring_status': 'active',
                'disk_space': self.get_disk_usage(),
                'memory_usage': self.get_memory_usage(),
                'cpu_usage': self.get_cpu_usage()
            }
            
            self.monitoring_data['system_health'] = health_status
            
        except Exception as e:
            self.create_alert('system', 'critical', f"System health check error: {str(e)}")
    
    def get_disk_usage(self):
        """الحصول على استخدام القرص"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            usage_percent = (used / total) * 100
            return {
                'total_gb': total // (1024**3),
                'used_gb': used // (1024**3),
                'free_gb': free // (1024**3),
                'usage_percent': usage_percent
            }
        except:
            return {'usage_percent': 0}
    
    def get_memory_usage(self):
        """الحصول على استخدام الذاكرة"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                'total_gb': memory.total // (1024**3),
                'used_gb': memory.used // (1024**3),
                'available_gb': memory.available // (1024**3),
                'usage_percent': memory.percent
            }
        except:
            return {'usage_percent': 0}
    
    def get_cpu_usage(self):
        """الحصول على استخدام المعالج"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0
    
    def generate_monitoring_report(self):
        """توليد تقرير المراقبة"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # استخراج بيانات آخر 24 ساعة
        yesterday = datetime.now() - timedelta(hours=24)
        
        cursor.execute('''
            SELECT COUNT(*) as total_checks,
                   AVG(response_time) as avg_response_time,
                   SUM(CASE WHEN status != 'up' THEN 1 ELSE 0 END) as downtime_count
            FROM uptime_monitoring
            WHERE timestamp > ?
        ''', (yesterday.isoformat(),))
        
        uptime_stats = cursor.fetchone()
        
        cursor.execute('''
            SELECT AVG(page_load_time) as avg_load_time,
                   AVG(availability_score) as avg_score
            FROM performance_metrics
            WHERE timestamp > ?
        ''', (yesterday.isoformat(),))
        
        performance_stats = cursor.fetchone()
        
        cursor.execute('''
            SELECT COUNT(*) as alert_count
            FROM alerts
            WHERE timestamp > ? AND resolved = FALSE
        ''', (yesterday.isoformat(),))
        
        alert_count = cursor.fetchone()
        
        conn.close()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': 'Last 24 hours',
            'uptime_stats': {
                'total_checks': uptime_stats[0] or 0,
                'avg_response_time': uptime_stats[1] or 0,
                'downtime_count': uptime_stats[2] or 0,
                'uptime_percentage': ((uptime_stats[0] - uptime_stats[2]) / uptime_stats[0] * 100) if uptime_stats[0] > 0 else 100
            },
            'performance_stats': {
                'avg_load_time': performance_stats[0] or 0,
                'avg_availability_score': performance_stats[1] or 0
            },
            'active_alerts': alert_count[0] or 0
        }
        
        return report
    
    def save_monitoring_report(self, report):
        """حفظ تقرير المراقبة"""
        with open('monitoring_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("📁 تم حفظ تقرير المراقبة في monitoring_report.json")
    
    def run_monitoring_cycle(self):
        """تشغيل دورة المراقبة"""
        print(f"🔄 بدء دورة المراقبة: {datetime.now()}")
        
        # فحص وقت التشغيل
        self.check_uptime()
        
        # فحص مقاييس الأداء
        self.check_performance_metrics()
        
        # فحص حالة المخزون
        self.check_inventory_status()
        
        # فحص صحة النظام
        self.check_system_health()
        
        # توليد تقرير المراقبة
        report = self.generate_monitoring_report()
        self.save_monitoring_report(report)
        
        print("✅ تمت دورة المراقبة بنجاح")
    
    def start_monitoring(self):
        """بدء المراقبة المستمرة"""
        print("🚀 بدء نظام المراقبة في الوقت الفعلي...")
        
        # جدولة المراقبة
        schedule.every(5).minutes.do(self.run_monitoring_cycle)
        schedule.every(1).hours.do(self.generate_monitoring_report)
        
        # تشغيل المراقبة المستمرة
        while True:
            schedule.run_pending()
            time.sleep(60)  # انتظار دقيقة واحدة
    
    def start_background_monitoring(self):
        """بدء المراقبة في الخلفية"""
        def monitoring_thread():
            self.start_monitoring()
        
        thread = threading.Thread(target=monitoring_thread, daemon=True)
        thread.start()
        
        print("🔄 بدء المراقبة في الخلفية...")
        return thread

def main():
    """الوظيفة الرئيسية"""
    monitor = RealTimeMonitor()
    
    # تشغيل دورة مراقبة واحدة
    monitor.run_monitoring_cycle()
    
    # بدء المراقبة المستمرة (اختياري)
    # monitor.start_background_monitoring()

if __name__ == "__main__":
    main()
