#!/usr/bin/env python3
"""
DNM.EG User Behavior Simulator
محاكاة شاملة لسلوك المستخدم وتحليل رحلة العميل
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin, urlparse
from datetime import datetime

class UserBehaviorSimulator:
    def __init__(self):
        self.base_url = "https://dnmeg.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.journey_data = {
            'user_sessions': [],
            'conversion_funnel': {},
            'friction_points': [],
            'user_flows': [],
            'abandonment_reasons': [],
            'recommendations': []
        }
        
    def simulate_user_session(self, user_type='new_visitor'):
        """محاكاة جلسة مستخدم كاملة"""
        session_data = {
            'user_type': user_type,
            'timestamp': datetime.now().isoformat(),
            'journey_steps': [],
            'total_time': 0,
            'converted': False,
            'cart_value': 0,
            'abandonment_point': None
        }
        
        try:
            # الخطوة 1: زيارة الصفحة الرئيسية
            start_time = time.time()
            homepage_response = self.session.get(self.base_url, timeout=10)
            homepage_time = time.time() - start_time
            
            session_data['journey_steps'].append({
                'step': 1,
                'action': 'homepage_visit',
                'url': self.base_url,
                'time_spent': round(homepage_time, 2),
                'success': homepage_response.status_code == 200,
                'elements_found': self.analyze_page_elements(homepage_response.text, 'homepage')
            })
            
            # محاكاة قرار المستخدم
            if random.random() < 0.7:  # 70% يستكشفون الموقع
                # الخطوة 2: استكشاف المنتجات
                products_response = self.session.get(f"{self.base_url}/collections/all", timeout=10)
                products_time = time.time() - start_time - homepage_time
                
                session_data['journey_steps'].append({
                    'step': 2,
                    'action': 'browse_products',
                    'url': f"{self.base_url}/collections/all",
                    'time_spent': round(products_time, 2),
                    'success': products_response.status_code == 200,
                    'products_found': self.count_products(products_response.text)
                })
                
                # الخطوة 3: عرض تفاصيل المنتج
                if random.random() < 0.8:  # 80% يضغطون على منتج
                    product_urls = self.extract_product_urls(products_response.text)
                    if product_urls:
                        selected_product = random.choice(product_urls)
                        product_response = self.session.get(selected_product, timeout=10)
                        product_time = time.time() - start_time - homepage_time - products_time
                        
                        session_data['journey_steps'].append({
                            'step': 3,
                            'action': 'view_product_details',
                            'url': selected_product,
                            'time_spent': round(product_time, 2),
                            'success': product_response.status_code == 200,
                            'product_analysis': self.analyze_product_page(product_response.text)
                        })
                        
                        # الخطوة 4: محاولة إضافة للسلة
                        if random.random() < 0.6:  # 60% يحاولون الإضافة للسلة
                            add_to_cart_result = self.simulate_add_to_cart(selected_product, product_response.text)
                            
                            session_data['journey_steps'].append({
                                'step': 4,
                                'action': 'add_to_cart',
                                'url': selected_product,
                                'time_spent': 0.5,
                                'success': add_to_cart_result['success'],
                                'issues': add_to_cart_result['issues']
                            })
                            
                            if add_to_cart_result['success']:
                                # الخطوة 5: عملية الخروج
                                if random.random() < 0.4:  # 40% يكملون الشراء
                                    checkout_result = self.simulate_checkout_process()
                                    
                                    session_data['journey_steps'].append({
                                        'step': 5,
                                        'action': 'checkout',
                                        'url': f"{self.base_url}/checkout",
                                        'time_spent': checkout_result['time_spent'],
                                        'success': checkout_result['success'],
                                        'issues': checkout_result['issues']
                                    })
                                    
                                    if checkout_result['success']:
                                        session_data['converted'] = True
                                        session_data['cart_value'] = checkout_result['cart_value']
                                    else:
                                        session_data['abandonment_point'] = 'checkout'
                                        session_data['abandonment_reason'] = checkout_result['issues']
                            else:
                                session_data['abandonment_point'] = 'add_to_cart'
                                session_data['abandonment_reason'] = add_to_cart_result['issues']
                        else:
                            session_data['abandonment_point'] = 'product_view'
                            session_data['abandonment_reason'] = 'No purchase intent'
                    else:
                        session_data['abandonment_point'] = 'product_browse'
                        session_data['abandonment_reason'] = 'No products available'
                else:
                    session_data['abandonment_point'] = 'product_browse'
                    session_data['abandonment_reason'] = 'Left products page'
            else:
                session_data['abandonment_point'] = 'homepage'
                session_data['abandonment_reason'] = 'Bounced immediately'
            
            session_data['total_time'] = round(time.time() - start_time, 2)
            
        except Exception as e:
            session_data['error'] = str(e)
            session_data['abandonment_point'] = 'error'
            session_data['abandonment_reason'] = f'Technical error: {str(e)}'
        
        return session_data
    
    def analyze_page_elements(self, html_content, page_type):
        """تحليل عناصر الصفحة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        elements = {
            'navigation_links': len(soup.find_all('nav a')),
            'product_cards': len(soup.find_all(['div', 'article'], class_=lambda x: x and 'product' in x.lower())),
            'call_to_action_buttons': len(soup.find_all(['button', 'a'], class_=lambda x: x and ('btn' in x.lower() or 'button' in x.lower()))),
            'trust_signals': len(soup.find_all(['img', 'div'], class_=lambda x: x and ('trust' in x.lower() or 'secure' in x.lower() or 'badge' in x.lower()))),
            'search_box': len(soup.find_all('input', {'type': 'search'})),
            'cart_icon': len(soup.find_all(['a', 'div'], class_=lambda x: x and 'cart' in x.lower())),
            'social_links': len(soup.find_all('a', href=lambda x: x and any(social in x for social in ['instagram', 'facebook', 'twitter', 'tiktok'])))
        }
        
        # تحليل خاص حسب نوع الصفحة
        if page_type == 'homepage':
            elements['hero_section'] = len(soup.find_all(['section', 'div'], class_=lambda x: x and ('hero' in x.lower() or 'banner' in x.lower())))
            elements['featured_products'] = len(soup.find_all(['div', 'section'], class_=lambda x: x and ('featured' in x.lower() or 'popular' in x.lower())))
        
        return elements
    
    def count_products(self, html_content):
        """عدد المنتجات في الصفحة"""
        soup = BeautifulSoup(html_content, 'html.parser')
        products = soup.find_all(['div', 'article'], class_=lambda x: x and 'product' in x.lower())
        return len(products)
    
    def extract_product_urls(self, html_content):
        """استخراج روابط المنتجات"""
        soup = BeautifulSoup(html_content, 'html.parser')
        product_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/products/' in href:
                full_url = urljoin(self.base_url, href)
                product_links.append(full_url)
        
        return list(set(product_links))  # إزالة التكرار
    
    def analyze_product_page(self, html_content):
        """تحليل صفحة المنتج"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            'product_title': bool(soup.find('h1')),
            'price_display': bool(soup.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower())),
            'product_images': len(soup.find_all('img')),
            'size_selector': bool(soup.find(['select', 'div'], class_=lambda x: x and 'size' in x.lower())),
            'add_to_cart_button': bool(soup.find(['button', 'input'], {'type': 'submit'}, value=lambda x: x and 'cart' in x.lower() if x else False)),
            'product_description': bool(soup.find(['div', 'p'], class_=lambda x: x and 'description' in x.lower())),
            'reviews_section': bool(soup.find(['div', 'section'], class_=lambda x: x and 'review' in x.lower())),
            'stock_status': self.extract_stock_status(soup),
            'shipping_info': bool(soup.find(['div', 'p'], class_=lambda x: x and 'shipping' in x.lower()))
        }
        
        return analysis
    
    def extract_stock_status(self, soup):
        """استخراج حالة المخزون"""
        stock_indicators = soup.find_all(['span', 'div', 'p'], string=lambda x: x and any(indicator in x.lower() for indicator in ['sold out', 'out of stock', 'unavailable', 'in stock']))
        
        if stock_indicators:
            return [indicator.text.strip() for indicator in stock_indicators]
        return ['Unknown']
    
    def simulate_add_to_cart(self, product_url, product_html):
        """محاكاة إضافة المنتج للسلة"""
        soup = BeautifulSoup(product_html, 'html.parser')
        
        # تحقق من وجود زر إضافة للسلة
        add_button = soup.find(['button', 'input'], {'type': 'submit'}, value=lambda x: x and 'cart' in x.lower() if x else False)
        
        if not add_button:
            return {
                'success': False,
                'issues': ['No add to cart button found']
            }
        
        # تحقق من حالة المخزون
        stock_status = self.extract_stock_status(soup)
        if any('sold out' in status.lower() or 'out of stock' in status.lower() for status in stock_status):
            return {
                'success': False,
                'issues': ['Product is out of stock']
            }
        
        # تحقق من محدد المقاس
        size_selector = soup.find(['select', 'div'], class_=lambda x: x and 'size' in x.lower())
        if not size_selector:
            return {
                'success': False,
                'issues': ['No size selector available']
            }
        
        # محاكاة نجاح الإضافة
        return {
            'success': True,
            'issues': []
        }
    
    def simulate_checkout_process(self):
        """محاكاة عملية الخروج"""
        try:
            # محاكاة زيارة صفحة الخروج
            checkout_response = self.session.get(f"{self.base_url}/checkout", timeout=10)
            
            if checkout_response.status_code != 200:
                return {
                    'success': False,
                    'time_spent': 0,
                    'issues': ['Checkout page not accessible'],
                    'cart_value': 0
                }
            
            # تحليل صفحة الخروج
            soup = BeautifulSoup(checkout_response.text, 'html.parser')
            
            # تحقق من عناصر الخروج
            checkout_elements = {
                'customer_info_form': bool(soup.find('form', id=lambda x: x and 'checkout' in x.lower())),
                'shipping_options': bool(soup.find(['div', 'select'], class_=lambda x: x and 'shipping' in x.lower())),
                'payment_options': bool(soup.find(['div', 'select'], class_=lambda x: x and 'payment' in x.lower())),
                'place_order_button': bool(soup.find(['button', 'input'], value=lambda x: x and ('place order' in x.lower() or 'complete purchase' in x.lower()) if x else False))
            }
            
            # محاكاة وقت إتمام العملية
            checkout_time = random.uniform(2, 5)  # 2-5 ثواني لإتمام الخروج
            
            # محاكاة قيمة السلة
            cart_value = random.uniform(350, 1200)  # بناءً على الأسعار الفعلية
            
            # محاكاة نسبة النجاح
            if all(checkout_elements.values()) and random.random() < 0.7:  # 70% نجاح إذا كانت جميع العناصر موجودة
                return {
                    'success': True,
                    'time_spent': round(checkout_time, 2),
                    'issues': [],
                    'cart_value': round(cart_value, 2)
                }
            else:
                missing_elements = [key for key, value in checkout_elements.items() if not value]
                return {
                    'success': False,
                    'time_spent': round(checkout_time, 2),
                    'issues': [f'Missing checkout elements: {", ".join(missing_elements)}'],
                    'cart_value': round(cart_value, 2)
                }
        
        except Exception as e:
            return {
                'success': False,
                'time_spent': 0,
                'issues': [f'Checkout error: {str(e)}'],
                'cart_value': 0
            }
    
    def run_multiple_simulations(self, num_sessions=20):
        """تشغيل محاكاة متعددة الجلسات"""
        print(f"🚀 بدء محاكاة {num_sessions} جلسة مستخدم...")
        
        user_types = ['new_visitor', 'returning_customer', 'bargain_hunter', 'brand_loyal']
        
        for i in range(num_sessions):
            user_type = random.choice(user_types)
            session_data = self.simulate_user_session(user_type)
            self.journey_data['user_sessions'].append(session_data)
            
            print(f"✅ تمت محاكاة الجلسة {i+1}/{num_sessions} - النوع: {user_type} - التحويل: {'✅' if session_data['converted'] else '❌'}")
            
            # تأخير صغير بين المحاكاة
            time.sleep(0.5)
        
        # تحليل البيانات
        self.analyze_simulation_results()
        
        return self.journey_data
    
    def analyze_simulation_results(self):
        """تحليل نتائج المحاكاة"""
        sessions = self.journey_data['user_sessions']
        
        # تحليل قمع التحويل
        funnel_analysis = {
            'homepage_visitors': len(sessions),
            'product_browsers': len([s for s in sessions if len(s['journey_steps']) > 1]),
            'product_viewers': len([s for s in sessions if len(s['journey_steps']) > 2]),
            'cart_adders': len([s for s in sessions if any(step['action'] == 'add_to_cart' for step in s['journey_steps'])]),
            'checkout_starters': len([s for s in sessions if any(step['action'] == 'checkout' for step in s['journey_steps'])]),
            'converted_users': len([s for s in sessions if s['converted']])
        }
        
        # حساب معدلات التحويل
        if funnel_analysis['homepage_visitors'] > 0:
            funnel_analysis['browse_rate'] = round((funnel_analysis['product_browsers'] / funnel_analysis['homepage_visitors']) * 100, 2)
            funnel_analysis['view_rate'] = round((funnel_analysis['product_viewers'] / funnel_analysis['homepage_visitors']) * 100, 2)
            funnel_analysis['cart_rate'] = round((funnel_analysis['cart_adders'] / funnel_analysis['homepage_visitors']) * 100, 2)
            funnel_analysis['checkout_rate'] = round((funnel_analysis['checkout_starters'] / funnel_analysis['homepage_visitors']) * 100, 2)
            funnel_analysis['conversion_rate'] = round((funnel_analysis['converted_users'] / funnel_analysis['homepage_visitors']) * 100, 2)
        
        self.journey_data['conversion_funnel'] = funnel_analysis
        
        # تحليل نقاط الاحتكاك
        abandonment_points = {}
        abandonment_reasons = {}
        
        for session in sessions:
            if not session['converted'] and session.get('abandonment_point'):
                point = session['abandonment_point']
                reason = session.get('abandonment_reason', 'Unknown')
                
                # التأكد من أن السبب ليس قائمة
                if isinstance(reason, list):
                    reason = ', '.join(str(r) for r in reason)
                
                abandonment_points[point] = abandonment_points.get(point, 0) + 1
                abandonment_reasons[reason] = abandonment_reasons.get(reason, 0) + 1
        
        self.journey_data['friction_points'] = [
            {'point': point, 'count': count, 'percentage': round((count / len(sessions)) * 100, 2)}
            for point, count in sorted(abandonment_points.items(), key=lambda x: x[1], reverse=True)
        ]
        
        self.journey_data['abandonment_reasons'] = [
            {'reason': reason, 'count': count, 'percentage': round((count / len(sessions)) * 100, 2)}
            for reason, count in sorted(abandonment_reasons.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # توليد التوصيات
        self.generate_behavior_recommendations()
    
    def generate_behavior_recommendations(self):
        """توليد توصيات بناءً على سلوك المستخدم"""
        recommendations = []
        
        # تحليل قمع التحويل
        funnel = self.journey_data['conversion_funnel']
        
        if funnel.get('browse_rate', 0) < 70:
            recommendations.append({
                'category': 'user_experience',
                'priority': 'high',
                'title': 'تحسين استكشاف المنتجات',
                'description': f'معدل الاستكشاف الحالي: {funnel.get("browse_rate", 0)}% - يجب تحسينه لأكثر من 70%',
                'expected_impact': 'زيادة عدد المستخدمين الذين يستكشفون المنتجات',
                'implementation_difficulty': 'medium'
            })
        
        if funnel.get('cart_rate', 0) < 30:
            recommendations.append({
                'category': 'conversion',
                'priority': 'high',
                'title': 'تحسين إضافة للسلة',
                'description': f'معدل الإضافة للسلة الحالي: {funnel.get("cart_rate", 0)}% - يجب تحسينه لأكثر من 30%',
                'expected_impact': 'زيادة عدد المستخدمين الذين يضيفون للسلة',
                'implementation_difficulty': 'medium'
            })
        
        if funnel.get('conversion_rate', 0) < 2:
            recommendations.append({
                'category': 'conversion',
                'priority': 'critical',
                'title': 'تحسين معدل التحويل',
                'description': f'معدل التحويل الحالي: {funnel.get("conversion_rate", 0)}% - يجب تحسينه لأكثر من 2%',
                'expected_impact': 'زيادة المبيعات والإيرادات',
                'implementation_difficulty': 'high'
            })
        
        # تحليل نقاط الاحتكاك
        friction_points = self.journey_data['friction_points']
        if friction_points:
            top_friction = friction_points[0]
            if top_friction['percentage'] > 30:
                recommendations.append({
                    'category': 'user_experience',
                    'priority': 'high',
                    'title': f'معالجة نقطة الاحتكاك الرئيسية: {top_friction["point"]}',
                    'description': f'{top_friction["percentage"]} من المستخدمين يتوقفون عند هذه النقطة',
                    'expected_impact': 'تقليل معدل التخلي وزيادة التحويل',
                    'implementation_difficulty': 'medium'
                })
        
        self.journey_data['recommendations'] = recommendations
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        print("\n" + "="*60)
        print("👥 ملخص محاكاة سلوك المستخدم:")
        print("="*60)
        
        # قمع التحويل
        funnel = self.journey_data['conversion_funnel']
        print(f"📊 إجمالي الجلسات: {funnel.get('homepage_visitors', 0)}")
        print(f"🔍 مستكشفو المنتجات: {funnel.get('product_browsers', 0)} ({funnel.get('browse_rate', 0)}%)")
        print(f"👀 عارضو المنتجات: {funnel.get('product_viewers', 0)} ({funnel.get('view_rate', 0)}%)")
        print(f"🛒 مضافو السلة: {funnel.get('cart_adders', 0)} ({funnel.get('cart_rate', 0)}%)")
        print(f"💳 مبدئو الخروج: {funnel.get('checkout_starters', 0)} ({funnel.get('checkout_rate', 0)}%)")
        print(f"✅ المحولون: {funnel.get('converted_users', 0)} ({funnel.get('conversion_rate', 0)}%)")
        
        # نقاط الاحتكاك
        print(f"\n⚠️ نقاط الاحتكاك الرئيسية:")
        for point in self.journey_data['friction_points'][:3]:
            print(f"  • {point['point']}: {point['percentage']}%")
        
        # أسباب التخلي
        print(f"\n📉 أسباب التخلي الرئيسية:")
        for reason in self.journey_data['abandonment_reasons'][:3]:
            print(f"  • {reason['reason']}: {reason['percentage']}%")
        
        # التوصيات
        print(f"\n💡 عدد التوصيات: {len(self.journey_data['recommendations'])}")
        
        print("="*60)
    
    def save_results(self):
        """حفظ النتائج"""
        with open('dnmeg_user_behavior_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.journey_data, f, ensure_ascii=False, indent=2)
        
        print("📁 تم حفظ النتائج في dnmeg_user_behavior_analysis.json")

def main():
    """الوظيفة الرئيسية"""
    simulator = UserBehaviorSimulator()
    results = simulator.run_multiple_simulations(20)
    simulator.print_summary()
    simulator.save_results()

if __name__ == "__main__":
    main()
