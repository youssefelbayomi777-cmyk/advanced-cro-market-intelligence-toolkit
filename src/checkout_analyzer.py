#!/usr/bin/env python3
"""
DNM.EG Checkout Analyzer
تحليل شامل لسلة التسوع وعملية الخروج
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin, urlparse
from datetime import datetime

class CheckoutAnalyzer:
    def __init__(self):
        self.base_url = "https://dnmeg.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.checkout_data = {
            'cart_analysis': {},
            'checkout_process': {},
            'payment_options': {},
            'shipping_analysis': {},
            'friction_points': [],
            'recommendations': []
        }
        
    def analyze_cart_page(self):
        """تحليل صفحة السلة"""
        try:
            # محاولة الوصول لصفحة السلة
            cart_url = f"{self.base_url}/cart"
            response = self.session.get(cart_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'accessible': False,
                    'status_code': response.status_code,
                    'error': 'Cart page not accessible'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            cart_analysis = {
                'accessible': True,
                'page_title': soup.find('title').text.strip() if soup.find('title') else '',
                'cart_items': self.extract_cart_items(soup),
                'cart_functionality': self.analyze_cart_functionality(soup),
                'trust_elements': self.analyze_trust_elements(soup),
                'cross_sell_elements': self.analyze_cross_sell(soup),
                'checkout_button': self.find_checkout_button(soup),
                'cart_summary': self.extract_cart_summary(soup)
            }
            
            return cart_analysis
            
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e)
            }
    
    def extract_cart_items(self, soup):
        """استخراج عناصر السلة"""
        items = []
        
        # البحث عن عناصر السلة
        cart_items = soup.find_all(['div', 'tr'], class_=lambda x: x and ('cart-item' in x.lower() or 'item' in x.lower()))
        
        for item in cart_items:
            item_data = {
                'name': '',
                'price': '',
                'quantity': '',
                'image': '',
                'remove_button': False,
                'quantity_selector': False
            }
            
            # استخراج اسم المنتج
            name_elem = item.find(['h3', 'h4', 'span', 'a'], class_=lambda x: x and ('name' in x.lower() or 'title' in x.lower()))
            if name_elem:
                item_data['name'] = name_elem.text.strip()
            
            # استخراج السعر
            price_elem = item.find(['span', 'div'], class_=lambda x: x and ('price' in x.lower() or 'money' in x.lower()))
            if price_elem:
                item_data['price'] = price_elem.text.strip()
            
            # استخراج الكمية
            qty_elem = item.find(['input', 'select'], class_=lambda x: x and ('quantity' in x.lower() or 'qty' in x.lower()))
            if qty_elem:
                item_data['quantity'] = qty_elem.get('value', '1') if qty_elem.name == 'input' else ''
                item_data['quantity_selector'] = True
            
            # استخراج الصورة
            img_elem = item.find('img')
            if img_elem:
                item_data['image'] = img_elem.get('src', '')
            
            # التحقق من زر الإزالة
            remove_elem = item.find(['button', 'a'], class_=lambda x: x and ('remove' in x.lower() or 'delete' in x.lower()))
            if remove_elem:
                item_data['remove_button'] = True
            
            if item_data['name'] or item_data['price']:
                items.append(item_data)
        
        return {
            'total_items': len(items),
            'items': items,
            'has_items': len(items) > 0
        }
    
    def analyze_cart_functionality(self, soup):
        """تحليل وظائف السلة"""
        functionality = {
            'update_quantity': False,
            'remove_item': False,
            'apply_coupon': False,
            'continue_shopping': False,
            'clear_cart': False
        }
        
        # التحقق من تحديث الكمية
        qty_inputs = soup.find_all(['input', 'select'], class_=lambda x: x and ('quantity' in x.lower() or 'qty' in x.lower()))
        update_buttons = soup.find_all(['button', 'input'], value=lambda x: x and ('update' in x.lower() if x else False))
        
        if qty_inputs and update_buttons:
            functionality['update_quantity'] = True
        
        # التحقق من زر الإزالة
        remove_buttons = soup.find_all(['button', 'a'], class_=lambda x: x and ('remove' in x.lower() or 'delete' in x.lower()))
        if remove_buttons:
            functionality['remove_item'] = True
        
        # التحقق من كوبون الخصم
        coupon_input = soup.find('input', {'name': lambda x: x and ('coupon' in x.lower() or 'discount' in x.lower())})
        coupon_button = soup.find('button', string=lambda x: x and ('apply' in x.lower() or 'coupon' in x.lower()) if x else False)
        
        if coupon_input and coupon_button:
            functionality['apply_coupon'] = True
        
        # التحقق من زر المتابعة للتسوق
        continue_button = soup.find('a', string=lambda x: x and ('continue' in x.lower() and 'shopping' in x.lower()) if x else False)
        if continue_button:
            functionality['continue_shopping'] = True
        
        return functionality
    
    def analyze_trust_elements(self, soup):
        """تحليل عناصر الثقة في السلة"""
        trust_elements = {
            'security_badges': 0,
            'payment_icons': 0,
            'ssl_indicators': 0,
            'return_policy': 0,
            'customer_support': 0,
            'trust_seals': 0
        }
        
        # البحث عن شارات الأمان
        security_imgs = soup.find_all('img', src=lambda x: x and any(sec in x.lower() for sec in ['secure', 'ssl', 'lock', 'norton', 'mcafee']))
        trust_elements['security_badges'] = len(security_imgs)
        
        # البحث عن أيقونات الدفع
        payment_imgs = soup.find_all('img', src=lambda x: x and any(payment in x.lower() for payment in ['visa', 'mastercard', 'paypal', 'stripe', 'apple-pay']))
        trust_elements['payment_icons'] = len(payment_imgs)
        
        # البحث عن مؤشرات SSL
        ssl_text = soup.find_all(string=lambda x: x and 'ssl' in x.lower() or 'secure' in x.lower())
        trust_elements['ssl_indicators'] = len(ssl_text)
        
        # البحث عن سياسة الإرجاع
        return_links = soup.find_all('a', href=lambda x: x and ('return' in x.lower() or 'refund' in x.lower()))
        trust_elements['return_policy'] = len(return_links)
        
        # البحث عن دعم العملاء
        support_links = soup.find_all('a', href=lambda x: x and ('support' in x.lower() or 'help' in x.lower() or 'contact' in x.lower()))
        trust_elements['customer_support'] = len(support_links)
        
        # البحث عن أختام الثقة
        trust_seals = soup.find_all(['div', 'span'], class_=lambda x: x and ('trust' in x.lower() or 'seal' in x.lower() or 'verified' in x.lower()))
        trust_elements['trust_seals'] = len(trust_seals)
        
        return trust_elements
    
    def analyze_cross_sell(self, soup):
        """تحليل عروض البيع المتبادل"""
        cross_sell = {
            'recommendations': False,
            'upsell_items': 0,
            'free_shipping_banner': False,
            'savings_calculator': False,
            'bundle_offers': False
        }
        
        # البحث عن توصيات المنتجات
        recommend_sections = soup.find_all(['div', 'section'], class_=lambda x: x and ('recommend' in x.lower() or 'suggestion' in x.lower()))
        if recommend_sections:
            cross_sell['recommendations'] = True
            cross_sell['upsell_items'] = len(recommend_sections)
        
        # البحث عن لافتة الشحن المجاني
        free_shipping_text = soup.find_all(string=lambda x: x and 'free shipping' in x.lower())
        if free_shipping_text:
            cross_sell['free_shipping_banner'] = True
        
        # البحث عن حاسبة التوفير
        savings_text = soup.find_all(string=lambda x: x and 'save' in x.lower() or 'saving' in x.lower())
        if savings_text:
            cross_sell['savings_calculator'] = True
        
        # البحث عن عروض الحزم
        bundle_text = soup.find_all(string=lambda x: x and 'bundle' in x.lower() or 'package' in x.lower())
        if bundle_text:
            cross_sell['bundle_offers'] = True
        
        return cross_sell
    
    def find_checkout_button(self, soup):
        """البحث عن زر الخروج"""
        checkout_button = {
            'found': False,
            'text': '',
            'type': '',
            'prominent': False
        }
        
        # البحث عن زر الخروج
        checkout_buttons = soup.find_all(['button', 'a', 'input'], 
                                       string=lambda x: x and ('checkout' in x.lower() or 'proceed' in x.lower()) if x else False)
        
        if checkout_buttons:
            button = checkout_buttons[0]
            checkout_button['found'] = True
            checkout_button['text'] = button.text.strip() if hasattr(button, 'text') else button.get('value', '')
            checkout_button['type'] = button.name
            
            # التحقق من مدى بروز الزر
            button_classes = button.get('class', [])
            if any(prominent in ' '.join(button_classes).lower() for prominent in ['btn', 'button', 'primary', 'large']):
                checkout_button['prominent'] = True
        
        return checkout_button
    
    def extract_cart_summary(self, soup):
        """استخراج ملخص السلة"""
        summary = {
            'subtotal': '',
            'shipping': '',
            'tax': '',
            'total': '',
            'savings': '',
            'currency': ''
        }
        
        # البحث عن ملخص الأسعار
        summary_divs = soup.find_all(['div', 'table'], class_=lambda x: x and ('summary' in x.lower() or 'total' in x.lower()))
        
        for div in summary_divs:
            # استخراج المجموع الفرعي
            subtotal_elem = div.find(string=lambda x: x and 'subtotal' in x.lower() if x else False)
            if subtotal_elem:
                parent = subtotal_elem.parent
                if parent:
                    price_text = parent.text.strip()
                    summary['subtotal'] = price_text
            
            # استخراج الشحن
            shipping_elem = div.find(string=lambda x: x and 'shipping' in x.lower() if x else False)
            if shipping_elem:
                parent = shipping_elem.parent
                if parent:
                    price_text = parent.text.strip()
                    summary['shipping'] = price_text
            
            # استخراج الضريبة
            tax_elem = div.find(string=lambda x: x and 'tax' in x.lower() if x else False)
            if tax_elem:
                parent = tax_elem.parent
                if parent:
                    price_text = parent.text.strip()
                    summary['tax'] = price_text
            
            # استخراج الإجمالي
            total_elem = div.find(string=lambda x: x and 'total' in x.lower() if x else False)
            if total_elem:
                parent = total_elem.parent
                if parent:
                    price_text = parent.text.strip()
                    summary['total'] = price_text
        
        return summary
    
    def analyze_checkout_process(self):
        """تحليل عملية الخروج"""
        try:
            # محاولة الوصول لصفحة الخروج
            checkout_url = f"{self.base_url}/checkout"
            response = self.session.get(checkout_url, timeout=10)
            
            if response.status_code != 200:
                return {
                    'accessible': False,
                    'status_code': response.status_code,
                    'error': 'Checkout page not accessible'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            checkout_analysis = {
                'accessible': True,
                'page_title': soup.find('title').text.strip() if soup.find('title') else '',
                'checkout_steps': self.analyze_checkout_steps(soup),
                'form_fields': self.analyze_checkout_fields(soup),
                'payment_methods': self.analyze_payment_methods(soup),
                'shipping_options': self.analyze_shipping_options(soup),
                'progress_indicator': self.check_progress_indicator(soup),
                'trust_elements': self.analyze_checkout_trust(soup),
                'error_handling': self.analyze_error_handling(soup)
            }
            
            return checkout_analysis
            
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e)
            }
    
    def analyze_checkout_steps(self, soup):
        """تحليل خطوات الخروج"""
        steps = {
            'step_indicators': 0,
            'current_step': '',
            'total_steps': 0,
            'step_names': []
        }
        
        # البحث عن مؤشرات الخطوات
        step_indicators = soup.find_all(['ol', 'ul'], class_=lambda x: x and ('step' in x.lower() or 'progress' in x.lower()))
        if step_indicators:
            steps['step_indicators'] = len(step_indicators)
            
            # استخراج أسماء الخطوات
            for indicator in step_indicators:
                step_items = indicator.find_all('li')
                for item in step_items:
                    step_text = item.text.strip()
                    if step_text:
                        steps['step_names'].append(step_text)
                        
                        # التحقق من الخطوة الحالية
                        if 'active' in ' '.join(item.get('class', [])).lower():
                            steps['current_step'] = step_text
            
            steps['total_steps'] = len(steps['step_names'])
        
        return steps
    
    def analyze_checkout_fields(self, soup):
        """تحليل حقول النموذج"""
        fields = {
            'customer_info': {
                'email': False,
                'first_name': False,
                'last_name': False,
                'phone': False
            },
            'shipping_address': {
                'address1': False,
                'address2': False,
                'city': False,
                'country': False,
                'postal_code': False
            },
            'billing_address': {
                'same_as_shipping': False,
                'address1': False,
                'city': False,
                'country': False
            },
            'field_validation': False,
            'required_fields': 0,
            'optional_fields': 0
        }
        
        # البحث عن حقول النموذج
        all_inputs = soup.find_all(['input', 'select', 'textarea'])
        
        for input_elem in all_inputs:
            input_name = input_elem.get('name', '').lower()
            input_type = input_elem.get('type', '').lower()
            input_required = input_elem.get('required', False)
            
            # تحليل حقول معلومات العميل
            if 'email' in input_name:
                fields['customer_info']['email'] = True
            elif 'first_name' in input_name or 'fname' in input_name:
                fields['customer_info']['first_name'] = True
            elif 'last_name' in input_name or 'lname' in input_name:
                fields['customer_info']['last_name'] = True
            elif 'phone' in input_name or 'tel' in input_name:
                fields['customer_info']['phone'] = True
            
            # تحليل حقول عنوان الشحن
            elif 'address' in input_name and '1' in input_name:
                fields['shipping_address']['address1'] = True
            elif 'address' in input_name and '2' in input_name:
                fields['shipping_address']['address2'] = True
            elif 'city' in input_name:
                fields['shipping_address']['city'] = True
            elif 'country' in input_name:
                fields['shipping_address']['country'] = True
            elif 'postal' in input_name or 'zip' in input_name:
                fields['shipping_address']['postal_code'] = True
            
            # تحليل حقول عنوان الفوترة
            elif 'billing' in input_name:
                if 'same' in input_name or 'use_shipping' in input_name:
                    fields['billing_address']['same_as_shipping'] = True
            
            # عد الحقول المطلوبة والاختيارية
            if input_required:
                fields['required_fields'] += 1
            else:
                fields['optional_fields'] += 1
        
        # التحقق من وجود تحقق من صحة الحقول
        validation_scripts = soup.find_all('script', string=lambda x: x and ('validation' in x.lower() or 'required' in x.lower()) if x else False)
        if validation_scripts:
            fields['field_validation'] = True
        
        return fields
    
    def analyze_payment_methods(self, soup):
        """تحليل طرق الدفع"""
        payment_methods = {
            'credit_card': False,
            'paypal': False,
            'apple_pay': False,
            'google_pay': False,
            'cash_on_delivery': False,
            'bank_transfer': False,
            'installments': False,
            'total_methods': 0,
            'method_details': []
        }
        
        # البحث عن طرق الدفع
        payment_options = soup.find_all(['div', 'section'], class_=lambda x: x and ('payment' in x.lower() or 'method' in x.lower()))
        
        for option in payment_options:
            # التحقق من البطاقة الائتمانية
            credit_inputs = option.find_all('input', {'name': lambda x: x and ('card' in x.lower() or 'credit' in x.lower())})
            if credit_inputs:
                payment_methods['credit_card'] = True
                payment_methods['method_details'].append('Credit Card')
            
            # التحقق من باي بال
            paypal_elements = option.find_all(string=lambda x: x and 'paypal' in x.lower() if x else False)
            if paypal_elements:
                payment_methods['paypal'] = True
                payment_methods['method_details'].append('PayPal')
            
            # التحقق من Apple Pay
            apple_pay_elements = option.find_all(string=lambda x: x and 'apple pay' in x.lower() if x else False)
            if apple_pay_elements:
                payment_methods['apple_pay'] = True
                payment_methods['method_details'].append('Apple Pay')
            
            # التحقق من الدفع عند الاستلام
            cod_elements = option.find_all(string=lambda x: x and ('cash' in x.lower() or 'cod' in x.lower()) if x else False)
            if cod_elements:
                payment_methods['cash_on_delivery'] = True
                payment_methods['method_details'].append('Cash on Delivery')
            
            # التحقص من التقسيط
            installment_elements = option.find_all(string=lambda x: x and ('installment' in x.lower() or 'valU' in x.lower() or 'sympl' in x.lower()) if x else False)
            if installment_elements:
                payment_methods['installments'] = True
                payment_methods['method_details'].append('Installments')
        
        payment_methods['total_methods'] = len([method for method, available in payment_methods.items() if available and method not in ['total_methods', 'method_details']])
        
        return payment_methods
    
    def analyze_shipping_options(self, soup):
        """تحليل خيارات الشحن"""
        shipping = {
            'standard_shipping': False,
            'express_shipping': False,
            'free_shipping': False,
            'pickup_option': False,
            'shipping_calculator': False,
            'total_options': 0,
            'option_details': []
        }
        
        # البحث عن خيارات الشحن
        shipping_options = soup.find_all(['div', 'section'], class_=lambda x: x and ('shipping' in x.lower() or 'delivery' in x.lower()))
        
        for option in shipping_options:
            # التحقق من الشحن القياسي
            standard_elements = option.find_all(string=lambda x: x and ('standard' in x.lower() or 'regular' in x.lower()) if x else False)
            if standard_elements:
                shipping['standard_shipping'] = True
                shipping['option_details'].append('Standard Shipping')
            
            # التحقق من الشحن السريع
            express_elements = option.find_all(string=lambda x: x and ('express' in x.lower() or 'fast' in x.lower()) if x else False)
            if express_elements:
                shipping['express_shipping'] = True
                shipping['option_details'].append('Express Shipping')
            
            # التحقق من الشحن المجاني
            free_elements = option.find_all(string=lambda x: x and 'free shipping' in x.lower() if x else False)
            if free_elements:
                shipping['free_shipping'] = True
                shipping['option_details'].append('Free Shipping')
            
            # التحقق من خيار الاستلام
            pickup_elements = option.find_all(string=lambda x: x and ('pickup' in x.lower() or 'collect' in x.lower()) if x else False)
            if pickup_elements:
                shipping['pickup_option'] = True
                shipping['option_details'].append('Store Pickup')
        
        # التحقق من حاسبة الشحن
        calculator_inputs = soup.find_all('input', {'name': lambda x: x and ('postal' in x.lower() or 'zip' in x.lower())})
        if calculator_inputs:
            shipping['shipping_calculator'] = True
        
        shipping['total_options'] = len([option for option, available in shipping.items() if available and option not in ['total_options', 'option_details']])
        
        return shipping
    
    def check_progress_indicator(self, soup):
        """التحقق من مؤشر التقدم"""
        progress = {
            'has_progress': False,
            'current_step': 0,
            'total_steps': 0,
            'progress_bar': False,
            'step_numbers': False
        }
        
        # البحث عن مؤشر التقدم
        progress_elements = soup.find_all(['div', 'ol'], class_=lambda x: x and ('progress' in x.lower() or 'step' in x.lower()))
        
        if progress_elements:
            progress['has_progress'] = True
            
            for elem in progress_elements:
                # التحقق من شريط التقدم
                if 'progress' in elem.get('class', []):
                    progress['progress_bar'] = True
                
                # التحقق من أرقام الخطوات
                step_items = elem.find_all('li')
                if step_items:
                    progress['total_steps'] = len(step_items)
                    
                    for i, item in enumerate(step_items):
                        if 'active' in ' '.join(item.get('class', [])).lower():
                            progress['current_step'] = i + 1
                        
                        # التحقق من أرقام الخطوات
                        if item.text.strip().isdigit():
                            progress['step_numbers'] = True
        
        return progress
    
    def analyze_checkout_trust(self, soup):
        """تحليل عناصر الثقة في الخروج"""
        trust = {
            'ssl_badge': False,
            'payment_security': False,
            'privacy_policy': False,
            'terms_of_service': False,
            'return_policy': False,
            'support_contact': False,
            'trust_seals': 0
        }
        
        # البحث عن شارة SSL
        ssl_elements = soup.find_all(string=lambda x: x and ('ssl' in x.lower() or 'secure' in x.lower()) if x else False)
        if ssl_elements:
            trust['ssl_badge'] = True
        
        # البحث عن أمان الدفع
        payment_security = soup.find_all(string=lambda x: x and ('payment security' in x.lower() or 'secure payment' in x.lower()) if x else False)
        if payment_security:
            trust['payment_security'] = True
        
        # البحث عن سياسة الخصوصية
        privacy_links = soup.find_all('a', href=lambda x: x and 'privacy' in x.lower())
        if privacy_links:
            trust['privacy_policy'] = True
        
        # البحث عن شروط الخدمة
        terms_links = soup.find_all('a', href=lambda x: x and 'terms' in x.lower())
        if terms_links:
            trust['terms_of_service'] = True
        
        # البحث عن سياسة الإرجاع
        return_links = soup.find_all('a', href=lambda x: x and 'return' in x.lower())
        if return_links:
            trust['return_policy'] = True
        
        # البحث عن اتصل بالدعم
        support_links = soup.find_all('a', href=lambda x: x and ('support' in x.lower() or 'contact' in x.lower()))
        if support_links:
            trust['support_contact'] = True
        
        # البحث عن أختام الثقة
        trust_seals = soup.find_all(['img', 'div'], class_=lambda x: x and ('trust' in x.lower() or 'seal' in x.lower() or 'verified' in x.lower()))
        trust['trust_seals'] = len(trust_seals)
        
        return trust
    
    def analyze_error_handling(self, soup):
        """تحليل معالجة الأخطاء"""
        error_handling = {
            'error_messages': False,
            'validation_errors': False,
            'payment_errors': False,
            'shipping_errors': False,
            'error_display': 'none'
        }
        
        # البحث عن رسائل الخطأ
        error_elements = soup.find_all(['div', 'span'], class_=lambda x: x and ('error' in x.lower() or 'alert' in x.lower()))
        if error_elements:
            error_handling['error_messages'] = True
            error_handling['error_display'] = 'inline'
        
        # البحث عن تحقق من صحة الأخطاء
        validation_scripts = soup.find_all('script', string=lambda x: x and ('validation' in x.lower() or 'error' in x.lower()) if x else False)
        if validation_scripts:
            error_handling['validation_errors'] = True
        
        return error_handling
    
    def run_full_analysis(self):
        """تشغيل التحليل الشامل"""
        print("🛒 بدء تحليل سلة التسوع وعملية الخروج...")
        
        # تحليل صفحة السلة
        print("📊 تحليل صفحة السلة...")
        cart_analysis = self.analyze_cart_page()
        self.checkout_data['cart_analysis'] = cart_analysis
        
        # تحليل عملية الخروج
        print("🚀 تحليل عملية الخروج...")
        checkout_analysis = self.analyze_checkout_process()
        self.checkout_data['checkout_process'] = checkout_analysis
        
        # تحليل نقاط الاحتكاك
        self.identify_friction_points()
        
        # توليد التوصيات
        self.generate_recommendations()
        
        # حفظ النتائج
        with open('dnmeg_checkout_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.checkout_data, f, ensure_ascii=False, indent=2)
        
        print("✅ تم تحليل سلة التسوع وعملية الخروج بنجاح!")
        print("📁 تم حفظ النتائج في dnmeg_checkout_analysis.json")
        
        return self.checkout_data
    
    def identify_friction_points(self):
        """تحديد نقاط الاحتكاك"""
        friction_points = []
        
        cart = self.checkout_data.get('cart_analysis', {})
        checkout = self.checkout_data.get('checkout_process', {})
        
        # نقاط احتكاك السلة
        if not cart.get('accessible', False):
            friction_points.append({
                'stage': 'cart',
                'severity': 'critical',
                'issue': 'Cart page not accessible',
                'impact': 'Users cannot view or modify cart'
            })
        
        if cart.get('cart_items', {}).get('total_items', 0) == 0:
            friction_points.append({
                'stage': 'cart',
                'severity': 'high',
                'issue': 'No items in cart analysis',
                'impact': 'Cannot analyze cart functionality'
            })
        
        if not cart.get('checkout_button', {}).get('found', False):
            friction_points.append({
                'stage': 'cart',
                'severity': 'critical',
                'issue': 'No checkout button found',
                'impact': 'Users cannot proceed to checkout'
            })
        
        # نقاط احتكاك الخروج
        if not checkout.get('accessible', False):
            friction_points.append({
                'stage': 'checkout',
                'severity': 'critical',
                'issue': 'Checkout page not accessible',
                'impact': 'Users cannot complete purchase'
            })
        
        payment_methods = checkout.get('payment_methods', {})
        if payment_methods.get('total_methods', 0) < 2:
            friction_points.append({
                'stage': 'checkout',
                'severity': 'high',
                'issue': f'Limited payment options: {payment_methods.get("total_methods", 0)} methods',
                'impact': 'Reduced conversion due to payment limitations'
            })
        
        shipping_options = checkout.get('shipping_options', {})
        if shipping_options.get('total_options', 0) < 2:
            friction_points.append({
                'stage': 'checkout',
                'severity': 'medium',
                'issue': f'Limited shipping options: {shipping_options.get("total_options", 0)} options',
                'impact': 'Reduced flexibility for customers'
            })
        
        self.checkout_data['friction_points'] = friction_points
    
    def generate_recommendations(self):
        """توليد التوصيات"""
        recommendations = []
        
        cart = self.checkout_data.get('cart_analysis', {})
        checkout = self.checkout_data.get('checkout_process', {})
        
        # توصيات السلة
        if not cart.get('accessible', False):
            recommendations.append({
                'category': 'cart',
                'priority': 'critical',
                'title': 'Fix cart page accessibility',
                'description': 'Ensure cart page is accessible and functional',
                'expected_impact': 'Enable users to view and modify cart',
                'implementation_difficulty': 'high'
            })
        
        if not cart.get('checkout_button', {}).get('found', False):
            recommendations.append({
                'category': 'cart',
                'priority': 'critical',
                'title': 'Add prominent checkout button',
                'description': 'Ensure clear and visible checkout button in cart',
                'expected_impact': 'Improve cart-to-checkout conversion',
                'implementation_difficulty': 'low'
            })
        
        # توصيات الخروج
        if not checkout.get('accessible', False):
            recommendations.append({
                'category': 'checkout',
                'priority': 'critical',
                'title': 'Fix checkout page accessibility',
                'description': 'Ensure checkout page is accessible and functional',
                'expected_impact': 'Enable users to complete purchases',
                'implementation_difficulty': 'high'
            })
        
        payment_methods = checkout.get('payment_methods', {})
        if payment_methods.get('total_methods', 0) < 3:
            recommendations.append({
                'category': 'checkout',
                'priority': 'high',
                'title': 'Expand payment options',
                'description': f'Add more payment methods (currently {payment_methods.get("total_methods", 0)})',
                'expected_impact': 'Increase conversion by offering preferred payment methods',
                'implementation_difficulty': 'medium'
            })
        
        shipping_options = checkout.get('shipping_options', {})
        if not shipping_options.get('free_shipping', False):
            recommendations.append({
                'category': 'checkout',
                'priority': 'medium',
                'title': 'Add free shipping option',
                'description': 'Offer free shipping for orders above certain threshold',
                'expected_impact': 'Increase average order value',
                'implementation_difficulty': 'low'
            })
        
        self.checkout_data['recommendations'] = recommendations
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        print("\n" + "="*60)
        print("🛒 ملخص تحليل سلة التسوع وعملية الخروج:")
        print("="*60)
        
        # تحليل السلة
        cart = self.checkout_data.get('cart_analysis', {})
        print(f"📊 صفحة السلة: {'✅ متاحة' if cart.get('accessible') else '❌ غير متاحة'}")
        print(f"🛒 عناصر السلة: {cart.get('cart_items', {}).get('total_items', 0)}")
        print(f"🔘 زر الخروج: {'✅ موجود' if cart.get('checkout_button', {}).get('found') else '❌ غير موجود'}")
        
        # تحليل الخروج
        checkout = self.checkout_data.get('checkout_process', {})
        print(f"🚀 صفحة الخروج: {'✅ متاحة' if checkout.get('accessible') else '❌ غير متاحة'}")
        
        payment_methods = checkout.get('payment_methods', {})
        print(f"💳 طرق الدفع: {payment_methods.get('total_methods', 0)}")
        
        shipping_options = checkout.get('shipping_options', {})
        print(f"📦 خيارات الشحن: {shipping_options.get('total_options', 0)}")
        
        # نقاط الاحتكاك
        friction_points = self.checkout_data.get('friction_points', [])
        print(f"⚠️ نقاط الاحتكاك: {len(friction_points)}")
        
        # التوصيات
        recommendations = self.checkout_data.get('recommendations', [])
        print(f"💡 عدد التوصيات: {len(recommendations)}")
        
        print("="*60)

def main():
    """الوظيفة الرئيسية"""
    analyzer = CheckoutAnalyzer()
    results = analyzer.run_full_analysis()
    analyzer.print_summary()

if __name__ == "__main__":
    main()
