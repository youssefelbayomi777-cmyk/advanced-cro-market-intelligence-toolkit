#!/usr/bin/env python3
"""
DNM.EG Performance Analyzer
تحليل أداء تقني شامل لموقع dnmeg.com
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
import re

class PerformanceAnalyzer:
    def __init__(self):
        self.base_url = "https://dnmeg.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = {
            'page_load_times': {},
            'image_analysis': {},
            'mobile_performance': {},
            'seo_analysis': {},
            'technical_issues': [],
            'recommendations': []
        }
        
    def measure_page_load_time(self, url):
        """قياس وقت تحميل الصفحة"""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            load_time = time.time() - start_time
            
            # تحليل حجم الصفحة
            page_size = len(response.content) / 1024  # بالكيلوبايت
            
            return {
                'url': url,
                'load_time': round(load_time, 3),
                'page_size_kb': round(page_size, 2),
                'status_code': response.status_code,
                'response_headers': dict(response.headers)
            }
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'load_time': 999,
                'page_size_kb': 0,
                'status_code': 0
            }
    
    def analyze_images(self, soup, page_url):
        """تحليل الصور وتحسينها"""
        images = soup.find_all('img')
        image_analysis = {
            'total_images': len(images),
            'optimized_images': 0,
            'large_images': 0,
            'missing_alt': 0,
            'external_images': 0,
            'image_details': []
        }
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # تحليل الصورة
            image_info = {
                'src': src,
                'alt': alt,
                'has_alt': bool(alt),
                'is_external': not src.startswith('//dnmeg.com') and not src.startswith('/cdn/'),
                'size_estimate': 'unknown'
            }
            
            # تحقق من حجم الصورة (تقديري)
            if 'width=' in src:
                width = re.search(r'width=(\d+)', src)
                if width:
                    width_val = int(width.group(1))
                    if width_val > 1500:
                        image_analysis['large_images'] += 1
                        image_info['is_large'] = True
            
            # تحقق من التحسين
            if any(optimized in src.lower() for optimized in ['webp', 'optimized', 'compressed']):
                image_analysis['optimized_images'] += 1
                image_info['is_optimized'] = True
            
            # تحقق من ALT text
            if not alt:
                image_analysis['missing_alt'] += 1
            
            # تحقق من الصور الخارجية
            if image_info['is_external']:
                image_analysis['external_images'] += 1
            
            image_analysis['image_details'].append(image_info)
        
        return image_analysis
    
    def test_mobile_performance(self, url):
        """اختبار أداء الجوال (محاكاة)"""
        try:
            # محاكاة طلب الجوال
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            mobile_session = requests.Session()
            mobile_session.headers.update(mobile_headers)
            
            start_time = time.time()
            response = mobile_session.get(url, timeout=10)
            mobile_load_time = time.time() - start_time
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحليل مدى توافق الجوال
            mobile_analysis = {
                'mobile_load_time': round(mobile_load_time, 3),
                'viewport_meta': bool(soup.find('meta', {'name': 'viewport'})),
                'responsive_images': len(soup.find_all('img', {'srcset': True})),
                'mobile_navigation': bool(soup.find('nav', class_='mobile-menu')),
                'touch_friendly': self.check_touch_friendly(soup),
                'font_sizes': self.analyze_font_sizes(soup)
            }
            
            return mobile_analysis
            
        except Exception as e:
            return {
                'error': str(e),
                'mobile_load_time': 999
            }
    
    def check_touch_friendly(self, soup):
        """فحص توافق اللمس"""
        # تحقق من أزرار اللمس
        buttons = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|touch'))
        touch_friendly = len(buttons) > 0
        
        return touch_friendly
    
    def analyze_font_sizes(self, soup):
        """تحليل أحجام الخطوط"""
        font_sizes = []
        
        # تحقق من عناصر النص الرئيسية
        text_elements = soup.find_all(['h1', 'h2', 'h3', 'p', 'span'])
        
        for element in text_elements:
            style = element.get('style', '')
            if 'font-size' in style:
                font_size = re.search(r'font-size:\s*(\d+)px', style)
                if font_size:
                    font_sizes.append(int(font_size.group(1)))
        
        return {
            'min_font_size': min(font_sizes) if font_sizes else 0,
            'max_font_size': max(font_sizes) if font_sizes else 0,
            'average_font_size': sum(font_sizes) / len(font_sizes) if font_sizes else 0
        }
    
    def analyze_seo(self, soup, page_url):
        """تحليل SEO"""
        seo_analysis = {
            'title': {
                'exists': bool(soup.find('title')),
                'content': soup.find('title').text.strip() if soup.find('title') else '',
                'length': len(soup.find('title').text.strip()) if soup.find('title') else 0,
                'optimal': False
            },
            'meta_description': {
                'exists': bool(soup.find('meta', {'name': 'description'})),
                'content': soup.find('meta', {'name': 'description'}).get('content', '') if soup.find('meta', {'name': 'description'}) else '',
                'length': len(soup.find('meta', {'name': 'description'}).get('content', '')) if soup.find('meta', {'name': 'description'}) else 0,
                'optimal': False
            },
            'headings': {
                'h1_count': len(soup.find_all('h1')),
                'h2_count': len(soup.find_all('h2')),
                'h3_count': len(soup.find_all('h3')),
                'structure_ok': False
            },
            'images_alt': {
                'total_images': len(soup.find_all('img')),
                'with_alt': len([img for img in soup.find_all('img') if img.get('alt')]),
                'percentage': 0
            },
            'internal_links': {
                'total': len(soup.find_all('a', href=True)),
                'internal': 0,
                'external': 0
            }
        }
        
        # تحقق من الحجم الأمثل
        seo_analysis['title']['optimal'] = 30 <= seo_analysis['title']['length'] <= 60
        seo_analysis['meta_description']['optimal'] = 120 <= seo_analysis['meta_description']['length'] <= 160
        
        # تحقق من هيكل العناوين
        seo_analysis['headings']['structure_ok'] = (
            seo_analysis['headings']['h1_count'] == 1 and
            seo_analysis['headings']['h2_count'] > 0
        )
        
        # حساب نسبة ALT text
        if seo_analysis['images_alt']['total_images'] > 0:
            seo_analysis['images_alt']['percentage'] = round(
                (seo_analysis['images_alt']['with_alt'] / seo_analysis['images_alt']['total_images']) * 100, 2
            )
        
        # تحليل الروابط
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http') and not href.startswith(self.base_url):
                seo_analysis['internal_links']['external'] += 1
            else:
                seo_analysis['internal_links']['internal'] += 1
        
        return seo_analysis
    
    def identify_technical_issues(self, analysis_results):
        """تحديد المشاكل التقنية"""
        issues = []
        
        # مشاكل وقت التحميل
        for page, data in analysis_results['page_load_times'].items():
            if data.get('load_time', 0) > 3:
                issues.append({
                    'type': 'performance',
                    'severity': 'high',
                    'page': page,
                    'issue': f'بطء تحميل الصفحة: {data["load_time"]} ثانية',
                    'recommendation': 'تحسين الصور وتقليل حجم الصفحة'
                })
        
        # مشاكل الصور
        img_analysis = analysis_results.get('image_analysis', {})
        if img_analysis.get('missing_alt', 0) > 0:
            issues.append({
                'type': 'seo',
                'severity': 'medium',
                'issue': f'صور بدون ALT text: {img_analysis["missing_alt"]}',
                'recommendation': 'إضافة وصف للصور لتحسين SEO وإمكانية الوصول'
            })
        
        if img_analysis.get('large_images', 0) > 0:
            issues.append({
                'type': 'performance',
                'severity': 'medium',
                'issue': f'صور كبيرة الحجم: {img_analysis["large_images"]}',
                'recommendation': 'ضغط الصور وتحسينها للويب'
            })
        
        # مشاكل SEO
        seo_analysis = analysis_results.get('seo_analysis', {})
        if not seo_analysis.get('title', {}).get('optimal', False):
            issues.append({
                'type': 'seo',
                'severity': 'high',
                'issue': 'عنوان الصفحة غير محسن',
                'recommendation': 'تحسين عنوان الصفحة ليكون بين 30-60 حرف'
            })
        
        if not seo_analysis.get('meta_description', {}).get('optimal', False):
            issues.append({
                'type': 'seo',
                'severity': 'high',
                'issue': 'وصف الصفحة غير محسن',
                'recommendation': 'تحسين وصف الصفحة ليكون بين 120-160 حرف'
            })
        
        # مشاكل الجوال
        mobile_analysis = analysis_results.get('mobile_performance', {})
        if not mobile_analysis.get('viewport_meta', False):
            issues.append({
                'type': 'mobile',
                'severity': 'high',
                'issue': 'لا يوجد viewport meta tag',
                'recommendation': 'إضافة viewport meta tag لتحسين تجربة الجوال'
            })
        
        return issues
    
    def generate_recommendations(self, analysis_results):
        """توليد التوصيات"""
        recommendations = []
        
        # توصيات الأداء
        recommendations.append({
            'category': 'performance',
            'priority': 'high',
            'title': 'تحسين سرعة التحميل',
            'description': 'تحسين الصور وتقليل حجم الملفات',
            'expected_impact': 'تحسين تجربة المستخدم وتقليل معدل الارتداد',
            'implementation_difficulty': 'medium'
        })
        
        # توصيات SEO
        recommendations.append({
            'category': 'seo',
            'priority': 'high',
            'title': 'تحسين عناصر SEO',
            'description': 'تحسين العناوين والأوصاف وإضافة ALT text',
            'expected_impact': 'تحسين ترتيب محركات البحث',
            'implementation_difficulty': 'low'
        })
        
        # توصيات الجوال
        recommendations.append({
            'category': 'mobile',
            'priority': 'high',
            'title': 'تحسين تجربة الجوال',
            'description': 'إضافة viewport meta tag وتحسين الأزرار لللمس',
            'expected_impact': 'تحسين تجربة المستخدم على الجوال',
            'implementation_difficulty': 'medium'
        })
        
        return recommendations
    
    def run_full_analysis(self):
        """تشغيل التحليل الشامل"""
        print("🚀 بدء تحليل الأداء التقني لموقع dnmeg.com...")
        
        # تحليل الصفحة الرئيسية
        print("📊 تحليل أداء الصفحة الرئيسية...")
        homepage_performance = self.measure_page_load_time(self.base_url)
        self.results['page_load_times']['homepage'] = homepage_performance
        
        # تحليل صفحات المنتجات
        print("📦 تحليل صفحات المنتجات...")
        product_urls = [
            f"{self.base_url}/products/tee-v1",
            f"{self.base_url}/products/tee-v2",
            f"{self.base_url}/products/jeans-1-9"
        ]
        
        for url in product_urls:
            try:
                performance = self.measure_page_load_time(url)
                page_name = url.split('/')[-1]
                self.results['page_load_times'][page_name] = performance
                print(f"✅ تم تحليل {page_name}")
            except Exception as e:
                print(f"❌ خطأ في تحليل {url}: {e}")
        
        # تحليل الصفحة الرئيسية بالتفصيل
        print("🔍 تحليل تفصيلي للصفحة الرئيسية...")
        try:
            response = self.session.get(self.base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # تحليل الصور
            self.results['image_analysis'] = self.analyze_images(soup, self.base_url)
            
            # تحليل الجوال
            self.results['mobile_performance'] = self.test_mobile_performance(self.base_url)
            
            # تحليل SEO
            self.results['seo_analysis'] = self.analyze_seo(soup, self.base_url)
            
        except Exception as e:
            print(f"❌ خطأ في التحليل التفصيلي: {e}")
        
        # تحديد المشاكل
        self.results['technical_issues'] = self.identify_technical_issues(self.results)
        
        # توليد التوصيات
        self.results['recommendations'] = self.generate_recommendations(self.results)
        
        # حفظ النتائج
        with open('dnmeg_performance_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print("✅ تم تحليل الأداء التقني بنجاح!")
        print("📁 تم حفظ النتائج في dnmeg_performance_analysis.json")
        
        return self.results
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        print("\n" + "="*60)
        print("📊 ملخص تحليل الأداء التقني:")
        print("="*60)
        
        # أداء التحميل
        print(f"⚡ وقت تحميل الصفحة الرئيسية: {self.results['page_load_times'].get('homepage', {}).get('load_time', 'N/A')} ثانية")
        
        # تحليل الصور
        img_analysis = self.results.get('image_analysis', {})
        print(f"🖼️ إجمالي الصور: {img_analysis.get('total_images', 0)}")
        print(f"📸 صور بدون ALT: {img_analysis.get('missing_alt', 0)}")
        print(f"📏 صور كبيرة: {img_analysis.get('large_images', 0)}")
        
        # تحليل الجوال
        mobile = self.results.get('mobile_performance', {})
        print(f"📱 وقت تحميل الجوال: {mobile.get('mobile_load_time', 'N/A')} ثانية")
        print(f"📱 viewport meta: {'✅' if mobile.get('viewport_meta') else '❌'}")
        
        # تحليل SEO
        seo = self.results.get('seo_analysis', {})
        print(f"🔍 عنوان الصفحة: {'✅' if seo.get('title', {}).get('optimal') else '❌'}")
        print(f"📝 وصف الصفحة: {'✅' if seo.get('meta_description', {}).get('optimal') else '❌'}")
        
        # المشاكل
        issues = self.results.get('technical_issues', [])
        print(f"⚠️ عدد المشاكل: {len(issues)}")
        
        # التوصيات
        recommendations = self.results.get('recommendations', [])
        print(f"💡 عدد التوصيات: {len(recommendations)}")
        
        print("="*60)

def main():
    """الوظيفة الرئيسية"""
    analyzer = PerformanceAnalyzer()
    results = analyzer.run_full_analysis()
    analyzer.print_summary()

if __name__ == "__main__":
    main()
