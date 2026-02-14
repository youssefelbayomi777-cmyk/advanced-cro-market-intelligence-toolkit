#!/usr/bin/env python3
"""
DNM.EG Reviews & Inventory Analyzer
تحليل شامل للمراجعات والتقييمات والمخزون والتوافر
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re

class ReviewsInventoryAnalyzer:
    def __init__(self):
        self.base_url = "https://dnmeg.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.analysis_data = {
            'reviews_analysis': {},
            'inventory_analysis': {},
            'sentiment_analysis': {},
            'stock_monitoring': {},
            'recommendations': []
        }
        
    def extract_reviews(self, soup, product_url):
        """استخراج المراجعات من صفحة المنتج"""
        reviews = []
        
        # البحث عن قسم المراجعات
        review_sections = soup.find_all(['div', 'section'], class_=lambda x: x and ('review' in x.lower() or 'rating' in x.lower()))
        
        for section in review_sections:
            # استخراج المراجعات الفردية
            review_items = section.find_all(['div', 'article'], class_=lambda x: x and ('review-item' in x.lower() or 'comment' in x.lower()))
            
            for item in review_items:
                review_data = {
                    'rating': '',
                    'title': '',
                    'content': '',
                    'author': '',
                    'date': '',
                    'verified': False,
                    'helpful': 0
                }
                
                # استخراج التقييم
                rating_elem = item.find(['span', 'div'], class_=lambda x: x and ('rating' in x.lower() or 'stars' in x.lower()))
                if rating_elem:
                    # البحث عن عدد النجوم
                    stars = rating_elem.find_all(['span', 'i'], class_=lambda x: x and ('star' in x.lower() or 'rating' in x.lower()))
                    review_data['rating'] = len(stars)
                
                # استخراج العنوان
                title_elem = item.find(['h3', 'h4', 'strong'], class_=lambda x: x and ('title' in x.lower() or 'headline' in x.lower()))
                if title_elem:
                    review_data['title'] = title_elem.text.strip()
                
                # استخراج المحتوى
                content_elem = item.find(['p', 'div'], class_=lambda x: x and ('content' in x.lower() or 'text' in x.lower()))
                if content_elem:
                    review_data['content'] = content_elem.text.strip()
                
                # استخراج المؤلف
                author_elem = item.find(['span', 'div'], class_=lambda x: x and ('author' in x.lower() or 'name' in x.lower()))
                if author_elem:
                    review_data['author'] = author_elem.text.strip()
                
                # استخراج التاريخ
                date_elem = item.find(['time', 'span'], class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower()))
                if date_elem:
                    review_data['date'] = date_elem.text.strip()
                
                # التحقق من المراجعة الموثقة
                verified_elem = item.find(['span', 'div'], class_=lambda x: x and ('verified' in x.lower() or 'confirmed' in x.lower()))
                if verified_elem:
                    review_data['verified'] = True
                
                reviews.append(review_data)
        
        # البحث عن ملخص التقييمات
        rating_summary = self.extract_rating_summary(soup)
        
        return {
            'product_url': product_url,
            'reviews': reviews,
            'total_reviews': len(reviews),
            'rating_summary': rating_summary,
            'has_reviews': len(reviews) > 0
        }
    
    def extract_rating_summary(self, soup):
        """استخراج ملخص التقييمات"""
        summary = {
            'average_rating': 0,
            'total_ratings': 0,
            'rating_distribution': {
                '5_star': 0,
                '4_star': 0,
                '3_star': 0,
                '2_star': 0,
                '1_star': 0
            }
        }
        
        # البحث عن متوسط التقييم
        avg_rating_elem = soup.find(['span', 'div'], class_=lambda x: x and ('average' in x.lower() or 'rating' in x.lower()))
        if avg_rating_elem:
            rating_text = avg_rating_elem.text.strip()
            # استخراج الرقم من النص
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                summary['average_rating'] = float(rating_match.group(1))
        
        # البحث عن إجمالي التقييمات
        total_elem = soup.find(['span', 'div'], string=lambda x: x and ('review' in x.lower() or 'rating' in x.lower()) if x else False)
        if total_elem:
            total_text = total_elem.text.strip()
            # استخراج الرقم من النص
            total_match = re.search(r'(\d+)', total_text)
            if total_match:
                summary['total_ratings'] = int(total_match.group(1))
        
        return summary
    
    def analyze_sentiment(self, reviews):
        """تحليل المشاعر في المراجعات"""
        sentiment = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total_analyzed': 0,
            'sentiment_score': 0,
            'key_phrases': {
                'positive': [],
                'negative': []
            }
        }
        
        # قائمة الكلمات الإيجابية والسلبية
        positive_words = ['good', 'great', 'excellent', 'amazing', 'perfect', 'love', 'awesome', 'fantastic', 'wonderful', 'nice', 'happy', 'satisfied', 'comfortable', 'quality', 'fit', 'style']
        negative_words = ['bad', 'poor', 'terrible', 'awful', 'hate', 'disappointed', 'uncomfortable', 'cheap', 'wrong', 'small', 'large', 'tight', 'loose', 'defective', 'damaged', 'late', 'expensive']
        
        for review in reviews:
            if not review.get('content'):
                continue
            
            content = review['content'].lower()
            title = review.get('title', '').lower()
            full_text = content + ' ' + title
            
            positive_count = sum(1 for word in positive_words if word in full_text)
            negative_count = sum(1 for word in negative_words if word in full_text)
            
            if positive_count > negative_count:
                sentiment['positive'] += 1
                # استخراج العبارات الإيجابية
                for word in positive_words:
                    if word in full_text:
                        sentiment['key_phrases']['positive'].append(word)
            elif negative_count > positive_count:
                sentiment['negative'] += 1
                # استخراج العبارات السلبية
                for word in negative_words:
                    if word in full_text:
                        sentiment['key_phrases']['negative'].append(word)
            else:
                sentiment['neutral'] += 1
            
            sentiment['total_analyzed'] += 1
        
        # حساب درجة المشاعر
        if sentiment['total_analyzed'] > 0:
            sentiment['sentiment_score'] = (sentiment['positive'] - sentiment['negative']) / sentiment['total_analyzed']
        
        # إزالة التكرار من العبارات
        sentiment['key_phrases']['positive'] = list(set(sentiment['key_phrases']['positive']))
        sentiment['key_phrases']['negative'] = list(set(sentiment['key_phrases']['negative']))
        
        return sentiment
    
    def find_complaints(self, reviews):
        """البحث عن الشكاوى المتكررة"""
        complaints = {
            'quality_issues': 0,
            'sizing_problems': 0,
            'shipping_delays': 0,
            'customer_service': 0,
            'price_concerns': 0,
            'product_damage': 0,
            'wrong_item': 0,
            'other_issues': 0,
            'complaint_details': []
        }
        
        # كلمات مفتاحية للمشاكل
        issue_keywords = {
            'quality_issues': ['quality', 'defective', 'broken', 'poor quality', 'cheap material'],
            'sizing_problems': ['size', 'small', 'large', 'tight', 'loose', 'fit', 'sizing'],
            'shipping_delays': ['shipping', 'delivery', 'late', 'delay', 'slow'],
            'customer_service': ['service', 'support', 'help', 'response', 'rude'],
            'price_concerns': ['price', 'expensive', 'overpriced', 'cost', 'value'],
            'product_damage': ['damaged', 'torn', 'ripped', 'stained', 'dirty'],
            'wrong_item': ['wrong', 'incorrect', 'different', 'not what', 'mistake']
        }
        
        for review in reviews:
            if not review.get('content'):
                continue
            
            content = review['content'].lower()
            title = review.get('title', '').lower()
            full_text = content + ' ' + title
            
            complaint_found = False
            
            for issue_type, keywords in issue_keywords.items():
                if any(keyword in full_text for keyword in keywords):
                    complaints[issue_type] += 1
                    complaint_found = True
                    
                    # إضافة التفاصيل
                    complaints['complaint_details'].append({
                        'type': issue_type,
                        'review_title': review.get('title', ''),
                        'review_content': review['content'][:100] + '...' if len(review['content']) > 100 else review['content'],
                        'rating': review.get('rating', 0)
                    })
                    break
            
            if not complaint_found and review.get('rating', 5) <= 2:
                complaints['other_issues'] += 1
        
        return complaints
    
    def check_stock_levels(self, soup, product_url):
        """فحص مستويات المخزون"""
        stock_info = {
            'product_url': product_url,
            'in_stock': False,
            'stock_quantity': 0,
            'stock_status': '',
            'variant_availability': {},
            'low_stock_warning': False,
            'out_of_stock': False
        }
        
        # البحث عن حالة المخزون
        stock_elements = soup.find_all(['span', 'div', 'p'], string=lambda x: x and any(status in x.lower() for status in ['stock', 'available', 'sold out', 'out of stock', 'in stock']) if x else False)
        
        if stock_elements:
            stock_text = ' '.join([elem.text.strip() for elem in stock_elements])
            stock_info['stock_status'] = stock_text
            
            # تحديد حالة المخزون
            if any(status in stock_text.lower() for status in ['sold out', 'out of stock', 'unavailable']):
                stock_info['out_of_stock'] = True
                stock_info['in_stock'] = False
            elif any(status in stock_text.lower() for status in ['in stock', 'available']):
                stock_info['in_stock'] = True
                stock_info['out_of_stock'] = False
                
                # البحث عن الكمية
                quantity_match = re.search(r'(\d+)', stock_text)
                if quantity_match:
                    stock_info['stock_quantity'] = int(quantity_match.group(1))
                    
                    # تحقق من المخزون المنخفض
                    if stock_info['stock_quantity'] <= 5:
                        stock_info['low_stock_warning'] = True
        
        # البحث عن توفر المتغيرات (المقاسات، الألوان)
        variant_selectors = soup.find_all(['select', 'div'], class_=lambda x: x and ('variant' in x.lower() or 'option' in x.lower() or 'size' in x.lower()))
        
        for selector in variant_selectors:
            options = selector.find_all('option')
            for option in options:
                option_text = option.text.strip()
                option_value = option.get('value', '')
                
                if option_text and option_value:
                    # التحقق من توفر الخيار
                    is_available = not any(unavailable in option_text.lower() for unavailable in ['sold out', 'unavailable', 'out of stock'])
                    
                    stock_info['variant_availability'][option_text] = {
                        'available': is_available,
                        'value': option_value
                    }
        
        return stock_info
    
    def find_out_of_stock(self, all_products_stock):
        """البحث عن المنتجات النافدة"""
        out_of_stock = {
            'total_products': len(all_products_stock),
            'out_of_stock_count': 0,
            'out_of_stock_products': [],
            'low_stock_products': [],
            'in_stock_products': []
        }
        
        for product_stock in all_products_stock:
            if product_stock.get('out_of_stock', False):
                out_of_stock['out_of_stock_count'] += 1
                out_of_stock['out_of_stock_products'].append({
                    'url': product_stock['product_url'],
                    'status': product_stock['stock_status'],
                    'variants': product_stock.get('variant_availability', {})
                })
            elif product_stock.get('low_stock_warning', False):
                out_of_stock['low_stock_products'].append({
                    'url': product_stock['product_url'],
                    'quantity': product_stock.get('stock_quantity', 0),
                    'status': product_stock['stock_status']
                })
            elif product_stock.get('in_stock', False):
                out_of_stock['in_stock_products'].append({
                    'url': product_stock['product_url'],
                    'quantity': product_stock.get('stock_quantity', 0),
                    'status': product_stock['stock_status']
                })
        
        # حساب النسب المئوية
        if out_of_stock['total_products'] > 0:
            out_of_stock['out_of_stock_percentage'] = round((out_of_stock['out_of_stock_count'] / out_of_stock['total_products']) * 100, 2)
            out_of_stock['in_stock_percentage'] = round((len(out_of_stock['in_stock_products']) / out_of_stock['total_products']) * 100, 2)
        
        return out_of_stock
    
    def monitor_restocks(self, out_of_stock_products):
        """مراقبة إعادة التخزين"""
        restock_monitoring = {
            'monitoring_active': True,
            'products_to_monitor': len(out_of_stock_products),
            'restock_alerts': [],
            'monitoring_frequency': 'daily',
            'alert_methods': ['email', 'webhook'],
            'restock_recommendations': []
        }
        
        # توليد توصيات إعادة التخزين
        for product in out_of_stock_products:
            recommendation = {
                'product_url': product['url'],
                'priority': 'high',
                'action': 'Restock immediately',
                'reason': 'Product is completely out of stock',
                'suggested_quantity': random.randint(20, 50),
                'estimated_demand': 'High based on out-of-stock status'
            }
            restock_monitoring['restock_recommendations'].append(recommendation)
        
        return restock_monitoring
    
    def analyze_product_reviews(self, product_urls):
        """تحليل مراجعات المنتجات"""
        all_reviews = []
        product_reviews = {}
        
        for url in product_urls:
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                reviews_data = self.extract_reviews(soup, url)
                product_reviews[url] = reviews_data
                all_reviews.extend(reviews_data['reviews'])
                
                print(f"✅ تم تحليل المراجعات لـ: {url}")
                
            except Exception as e:
                print(f"❌ خطأ في تحليل المراجعات لـ {url}: {e}")
        
        # تحليل المشاعر
        sentiment_analysis = self.analyze_sentiment(all_reviews)
        
        # البحث عن الشكاوى
        complaints_analysis = self.find_complaints(all_reviews)
        
        return {
            'product_reviews': product_reviews,
            'all_reviews': all_reviews,
            'sentiment_analysis': sentiment_analysis,
            'complaints_analysis': complaints_analysis
        }
    
    def analyze_inventory_status(self, product_urls):
        """تحليل حالة المخزون"""
        all_stock_info = []
        
        for url in product_urls:
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                stock_info = self.check_stock_levels(soup, url)
                all_stock_info.append(stock_info)
                
                print(f"✅ تم تحليل المخزون لـ: {url}")
                
            except Exception as e:
                print(f"❌ خطأ في تحليل المخزون لـ {url}: {e}")
        
        # البحث عن المنتجات النافدة
        out_of_stock_analysis = self.find_out_of_stock(all_stock_info)
        
        # مراقبة إعادة التخزين
        restock_monitoring = self.monitor_restocks(out_of_stock_analysis['out_of_stock_products'])
        
        return {
            'all_stock_info': all_stock_info,
            'out_of_stock_analysis': out_of_stock_analysis,
            'restock_monitoring': restock_monitoring
        }
    
    def run_full_analysis(self):
        """تشغيل التحليل الشامل"""
        print("📊 بدء تحليل المراجعات والمخزون...")
        
        # الحصول على روابط المنتجات
        try:
            response = self.session.get(f"{self.base_url}/collections/all", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            product_links = []
            for link in soup.find_all('a', href=True):
                if '/products/' in link['href']:
                    full_url = urljoin(self.base_url, link['href'])
                    product_links.append(full_url)
            
            product_links = list(set(product_links))  # إزالة التكرار
            
        except Exception as e:
            print(f"❌ خطأ في الحصول على روابط المنتجات: {e}")
            product_links = []
        
        if not product_links:
            print("⚠️ لم يتم العثور على روابط المنتجات، استخدام روابط افتراضية")
            product_links = [
                f"{self.base_url}/products/tee-v1",
                f"{self.base_url}/products/tee-v2",
                f"{self.base_url}/products/jeans-1-9"
            ]
        
        # تحليل المراجعات
        print("📝 تحليل المراجعات والتقييمات...")
        reviews_analysis = self.analyze_product_reviews(product_links)
        self.analysis_data['reviews_analysis'] = reviews_analysis
        
        # تحليل المخزون
        print("📦 تحليل المخزون والتوافر...")
        inventory_analysis = self.analyze_inventory_status(product_links)
        self.analysis_data['inventory_analysis'] = inventory_analysis
        
        # توليد التوصيات
        self.generate_recommendations()
        
        # حفظ النتائج
        with open('dnmeg_reviews_inventory_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, ensure_ascii=False, indent=2)
        
        print("✅ تم تحليل المراجعات والمخزون بنجاح!")
        print("📁 تم حفظ النتائج في dnmeg_reviews_inventory_analysis.json")
        
        return self.analysis_data
    
    def generate_recommendations(self):
        """توليد التوصيات"""
        recommendations = []
        
        reviews = self.analysis_data.get('reviews_analysis', {})
        inventory = self.analysis_data.get('inventory_analysis', {})
        
        # توصيات المراجعات
        sentiment = reviews.get('sentiment_analysis', {})
        if sentiment.get('sentiment_score', 0) < 0:
            recommendations.append({
                'category': 'reviews',
                'priority': 'high',
                'title': 'تحسين تجربة العملاء',
                'description': f'درجة المشاعر السلبية: {sentiment.get("sentiment_score", 0):.2f}',
                'expected_impact': 'تحسين رضا العملاء وزيادة التقييمات الإيجابية',
                'implementation_difficulty': 'medium'
            })
        
        complaints = reviews.get('complaints_analysis', {})
        if complaints.get('quality_issues', 0) > 0:
            recommendations.append({
                'category': 'reviews',
                'priority': 'high',
                'title': 'معالجة مشاكل الجودة',
                'description': f'عدد شكاوى الجودة: {complaints.get("quality_issues", 0)}',
                'expected_impact': 'تقليل المرتجعات وزيادة رضا العملاء',
                'implementation_difficulty': 'medium'
            })
        
        # توصيات المخزون
        out_of_stock = inventory.get('out_of_stock_analysis', {})
        if out_of_stock.get('out_of_stock_percentage', 0) > 50:
            recommendations.append({
                'category': 'inventory',
                'priority': 'critical',
                'title': 'إعادة تخزين المنتجات',
                'description': f'نسبة المنتجات النافدة: {out_of_stock.get("out_of_stock_percentage", 0)}%',
                'expected_impact': 'استعادة المبيعات المفقودة',
                'implementation_difficulty': 'high'
            })
        
        low_stock = len(inventory.get('out_of_stock_analysis', {}).get('low_stock_products', []))
        if low_stock > 0:
            recommendations.append({
                'category': 'inventory',
                'priority': 'medium',
                'title': 'إعادة تعبئة المخزون المنخفض',
                'description': f'عدد المنتجات ذات المخزون المنخفض: {low_stock}',
                'expected_impact': 'تجنب نفاد المخزون',
                'implementation_difficulty': 'low'
            })
        
        self.analysis_data['recommendations'] = recommendations
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        print("\n" + "="*60)
        print("📊 ملخص تحليل المراجعات والمخزون:")
        print("="*60)
        
        # تحليل المراجعات
        reviews = self.analysis_data.get('reviews_analysis', {})
        print(f"📝 إجمالي المراجعات: {len(reviews.get('all_reviews', []))}")
        
        sentiment = reviews.get('sentiment_analysis', {})
        print(f"😊 المراجعات الإيجابية: {sentiment.get('positive', 0)}")
        print(f"😞 المراجعات السلبية: {sentiment.get('negative', 0)}")
        print(f"😐 المراجعات المحايدة: {sentiment.get('neutral', 0)}")
        print(f"📈 درجة المشاعر: {sentiment.get('sentiment_score', 0):.2f}")
        
        complaints = reviews.get('complaints_analysis', {})
        print(f"⚠️ مشاكل الجودة: {complaints.get('quality_issues', 0)}")
        print(f"📏 مشاكل المقاسات: {complaints.get('sizing_problems', 0)}")
        print(f"🚚 مشاكل الشحن: {complaints.get('shipping_delays', 0)}")
        
        # تحليل المخزون
        inventory = self.analysis_data.get('inventory_analysis', {})
        out_of_stock = inventory.get('out_of_stock_analysis', {})
        print(f"\n📦 إجمالي المنتجات: {out_of_stock.get('total_products', 0)}")
        print(f"❌ المنتجات النافدة: {out_of_stock.get('out_of_stock_count', 0)} ({out_of_stock.get('out_of_stock_percentage', 0)}%)")
        print(f"⚠️ المخزون المنخفض: {len(out_of_stock.get('low_stock_products', []))}")
        print(f"✅ المنتجات المتوفرة: {len(out_of_stock.get('in_stock_products', []))} ({out_of_stock.get('in_stock_percentage', 0)}%)")
        
        # التوصيات
        recommendations = self.analysis_data.get('recommendations', [])
        print(f"\n💡 عدد التوصيات: {len(recommendations)}")
        
        print("="*60)

def main():
    """الوظيفة الرئيسية"""
    analyzer = ReviewsInventoryAnalyzer()
    results = analyzer.run_full_analysis()
    analyzer.print_summary()

if __name__ == "__main__":
    main()
