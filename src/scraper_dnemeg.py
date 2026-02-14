#!/usr/bin/env python3
"""
DNM.EG Website Scraper
تحليل موقع dnmeg.com باستخدام Python و BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

class DNMScraper:
    def __init__(self):
        self.base_url = "https://dnmeg.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page(self, url):
        """الحصول على محتوى الصفحة"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_homepage_data(self, soup):
        """استخراج بيانات الصفحة الرئيسية"""
        data = {
            'title': soup.find('title').text.strip() if soup.find('title') else '',
            'description': soup.find('meta', {'name': 'description'}).get('content', '') if soup.find('meta', {'name': 'description'}) else '',
            'products': [],
            'categories': [],
            'trust_signals': [],
            'navigation': []
        }
        
        # استخراج المنتجات الرئيسية
        product_elements = soup.find_all('div', class_='product-item')
        for product in product_elements:
            product_data = {
                'name': product.find('h2').text.strip() if product.find('h2') else '',
                'price': product.find('span', class_='price').text.strip() if product.find('span', class_='price') else '',
                'url': product.find('a')['href'] if product.find('a') else ''
            }
            data['products'].append(product_data)
        
        return data
    
    def extract_category_data(self, soup):
        """استخراج بيانات صفحات الفئات"""
        data = {
            'category_name': soup.find('h1').text.strip() if soup.find('h1') else '',
            'products': [],
            'filters': [],
            'sorting': []
        }
        
        # استخراج المنتجات في الفئة
        product_elements = soup.find_all('div', class_='product-item')
        for product in product_elements:
            product_data = {
                'name': product.find('h2').text.strip() if product.find('h2') else '',
                'price': product.find('span', class_='price').text.strip() if product.find('span', class_='price') else '',
                'url': product.find('a')['href'] if product.find('a') else ''
            }
            data['products'].append(product_data)
        
        return data
    
    def scrape_site(self):
        """الوظيفة الرئيسية للتحليل"""
        print("🚀 بدء تحليل موقع dnmeg.com...")
        
        # تحليل الصفحة الرئيسية
        print("📊 تحليل الصفحة الرئيسية...")
        homepage = self.get_page(self.base_url)
        if homepage:
            homepage_data = self.extract_homepage_data(homepage)
            print(f"✅ تم العثور على {len(homepage_data['products'])} منتج في الصفحة الرئيسية")
        
        # تحليل صفحات المنتجات
        print("📦 تحليل صفحات المنتجات...")
        products_data = []
        
        # الحصول على روابط المنتجات
        if homepage:
            product_links = homepage.find_all('a', href=True)
            for link in product_links:
                if '/products/' in link['href']:
                    product_url = urljoin(self.base_url, link['href'])
                    print(f"🔍 تحليل المنتج: {product_url}")
                    
                    product_page = self.get_page(product_url)
                    if product_page:
                        product_data = self.extract_product_data(product_page)
                        products_data.append(product_data)
                    
                    time.sleep(1)  # تأخير لمنع الحظر
        
        # حفظ البيانات
        final_data = {
            'scrape_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'homepage': homepage_data if homepage else {},
            'products': products_data,
            'total_products': len(products_data),
            'analysis_summary': {
                'homepage_products': len(homepage_data['products']) if homepage else 0,
                'total_products_found': len(products_data)
            }
        }
        
        # حفظ في ملف JSON
        with open('dnmeg_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ تم تحليل {len(products_data)} منتج بنجاح!")
        print("📁 تم حفظ البيانات في dnmemeg_analysis.json")
        
        return final_data
    
    def extract_product_data(self, soup):
        """استخراج بيانات المنتج المفصلة"""
        data = {
            'name': '',
            'price': '',
            'description': '',
            'images': [],
            'specifications': {},
            'availability': '',
            'reviews': []
        }
        
        # استخراج اسم المنتج
        title_element = soup.find('h1') or soup.find('title')
        if title_element:
            data['name'] = title_element.text.strip()
        
        # استخراج السعر
        price_element = soup.find('span', class_='price') or soup.find('div', class_='price')
        if price_element:
            data['price'] = price_element.text.strip()
        
        # استخراج الوصف
        desc_element = soup.find('div', class_='description') or soup.find('meta', {'name': 'description'})
        if desc_element:
            if desc_element.name == 'meta':
                data['description'] = desc_element.get('content', '')
            else:
                data['description'] = desc_element.text.strip()
        
        # استخراج الصور
        img_elements = soup.find_all('img')
        for img in img_elements:
            if img.get('src'):
                data['images'].append(img['src'])
        
        # استخراج التوفر
        availability_element = soup.find('span', class_='availability') or soup.find('div', class_='stock')
        if availability_element:
            data['availability'] = availability_element.text.strip()
        
        return data

def main():
    """الوظيفة الرئيسية"""
    scraper = DNMScraper()
    results = scraper.scrape_site()
    
    # طباعة الملخص
    print("\n" + "="*50)
    print("📊 ملخص التحليل:")
    print(f"📦 إجمالي المنتجات: {results['total_products']}")
    print(f"🏠 منتجات الصفحة الرئيسية: {results['analysis_summary']['homepage_products']}")
    print(f"📈 وقت التحليل: {results['scrape_time']}")
    print("="*50)

if __name__ == "__main__":
    main()
