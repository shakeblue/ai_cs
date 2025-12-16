#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네이버 쇼핑 전시 페이지 구조 분석 스크립트
페이지 구조를 분석하여 크롤러 개발에 필요한 CSS 선택자를 찾습니다.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def analyze_page():
    """네이버 쇼핑 전시 페이지 분석"""
    
    # 샘플 URL
    _v_url = "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"
    
    print("=" * 80)
    print("네이버 쇼핑 전시 페이지 구조 분석")
    print("=" * 80)
    print(f"\n분석 URL: {_v_url}\n")
    
    # Chrome 옵션 설정
    _v_chrome_options = Options()
    _v_chrome_options.add_argument('--headless')  # 헤드리스 모드
    _v_chrome_options.add_argument('--no-sandbox')
    _v_chrome_options.add_argument('--disable-dev-shm-usage')
    _v_chrome_options.add_argument('--disable-gpu')
    _v_chrome_options.add_argument('--window-size=1920,1080')
    _v_chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    # WebDriver 초기화
    _v_driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=_v_chrome_options
    )
    
    try:
        # 페이지 로드
        print("📄 페이지 로딩 중...")
        _v_driver.get(_v_url)
        time.sleep(5)  # 동적 콘텐츠 로딩 대기
        
        # 페이지 스크롤 (lazy loading 콘텐츠 로드)
        print("📜 페이지 스크롤 중...")
        _v_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        _v_driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # HTML 저장
        _v_html = _v_driver.page_source
        with open('naver_shopping_page_source.html', 'w', encoding='utf-8') as f:
            f.write(_v_html)
        print("✅ HTML 소스 저장: naver_shopping_page_source.html")
        
        # 스크린샷 저장
        _v_driver.save_screenshot('naver_shopping_screenshot.png')
        print("✅ 스크린샷 저장: naver_shopping_screenshot.png")
        
        # BeautifulSoup으로 파싱
        _v_soup = BeautifulSoup(_v_html, 'html.parser')
        
        print("\n" + "=" * 80)
        print("📊 페이지 구조 분석 결과")
        print("=" * 80)
        
        # 1. 타이틀 찾기
        print("\n[1] 행사 타이틀 후보:")
        _v_title_selectors = [
            'h1', 'h2', 'h3',
            '[class*="title"]', '[class*="Title"]',
            '[class*="heading"]', '[class*="Heading"]',
            '[class*="name"]', '[class*="Name"]'
        ]
        for selector in _v_title_selectors:
            elements = _v_soup.select(selector)
            if elements:
                for idx, elem in enumerate(elements[:3], 1):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3:
                        print(f"   {selector} [{idx}]: {text[:100]}")
        
        # 2. 날짜 정보 찾기
        print("\n[2] 행사 일자 후보:")
        _v_date_pattern = re.compile(r'\d{2,4}[./-]\d{1,2}[./-]\d{1,2}')
        _v_all_text = _v_soup.get_text()
        _v_dates = _v_date_pattern.findall(_v_all_text)
        if _v_dates:
            print(f"   발견된 날짜 패턴: {set(_v_dates)}")
        
        # 날짜 관련 클래스 찾기
        _v_date_selectors = [
            '[class*="date"]', '[class*="Date"]',
            '[class*="period"]', '[class*="Period"]',
            '[class*="time"]', '[class*="Time"]'
        ]
        for selector in _v_date_selectors:
            elements = _v_soup.select(selector)
            if elements:
                for idx, elem in enumerate(elements[:3], 1):
                    text = elem.get_text(strip=True)
                    if text:
                        print(f"   {selector} [{idx}]: {text[:100]}")
        
        # 3. 혜택 정보 찾기
        print("\n[3] 혜택 정보 후보:")
        _v_benefit_selectors = [
            '[class*="benefit"]', '[class*="Benefit"]',
            '[class*="coupon"]', '[class*="Coupon"]',
            '[class*="event"]', '[class*="Event"]',
            '[class*="promotion"]', '[class*="Promotion"]',
            '[class*="gift"]', '[class*="Gift"]'
        ]
        for selector in _v_benefit_selectors:
            elements = _v_soup.select(selector)
            if elements:
                print(f"   {selector}: {len(elements)}개 발견")
                for idx, elem in enumerate(elements[:2], 1):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5:
                        print(f"      [{idx}]: {text[:150]}")
        
        # 4. 쿠폰 정보 찾기
        print("\n[4] 쿠폰 정보 후보:")
        _v_coupon_keywords = ['쿠폰', 'COUPON', 'coupon']
        for keyword in _v_coupon_keywords:
            elements = _v_soup.find_all(string=re.compile(keyword))
            if elements:
                print(f"   '{keyword}' 키워드: {len(elements)}개 발견")
                for idx, elem in enumerate(elements[:3], 1):
                    parent_class = elem.parent.get('class', [])
                    print(f"      [{idx}]: {elem.strip()[:100]}")
                    print(f"           부모 클래스: {parent_class}")
        
        # 5. 금액대별 혜택 찾기
        print("\n[5] 금액대별 혜택 후보:")
        _v_price_pattern = re.compile(r'\d+만?\s*원')
        _v_price_texts = _v_soup.find_all(string=_v_price_pattern)
        if _v_price_texts:
            print(f"   금액 패턴: {len(_v_price_texts)}개 발견")
            for idx, text in enumerate(_v_price_texts[:5], 1):
                parent_class = text.parent.get('class', [])
                print(f"      [{idx}]: {text.strip()[:100]}")
                print(f"           부모 클래스: {parent_class}")
        
        # 6. 상품 정보 찾기
        print("\n[6] 상품 정보 후보:")
        _v_product_selectors = [
            '[class*="product"]', '[class*="Product"]',
            '[class*="item"]', '[class*="Item"]',
            '[class*="goods"]', '[class*="Goods"]'
        ]
        for selector in _v_product_selectors:
            elements = _v_soup.select(selector)
            if elements:
                print(f"   {selector}: {len(elements)}개 발견")
                for idx, elem in enumerate(elements[:2], 1):
                    # 상품명 찾기
                    name_elem = elem.select_one('[class*="name"], [class*="Name"], [class*="title"], [class*="Title"]')
                    if name_elem:
                        print(f"      [{idx}] 상품명: {name_elem.get_text(strip=True)[:100]}")
                    
                    # 가격 찾기
                    price_elem = elem.select_one('[class*="price"], [class*="Price"]')
                    if price_elem:
                        print(f"           가격: {price_elem.get_text(strip=True)[:50]}")
        
        # 7. 공통 클래스명 분석
        print("\n[7] 자주 사용되는 클래스명 (TOP 20):")
        _v_all_classes = {}
        for elem in _v_soup.find_all(class_=True):
            for cls in elem.get('class', []):
                _v_all_classes[cls] = _v_all_classes.get(cls, 0) + 1
        
        _v_sorted_classes = sorted(_v_all_classes.items(), key=lambda x: x[1], reverse=True)
        for idx, (cls, count) in enumerate(_v_sorted_classes[:20], 1):
            # 혜택/쿠폰/상품 관련 클래스만 출력
            if any(keyword in cls.lower() for keyword in ['benefit', 'coupon', 'product', 'item', 'event', 'promotion', 'gift', 'title', 'date']):
                print(f"   {idx}. {cls}: {count}회")
        
        # 8. iframe 확인
        print("\n[8] iframe 확인:")
        _v_iframes = _v_soup.find_all('iframe')
        if _v_iframes:
            print(f"   iframe {len(_v_iframes)}개 발견")
            for idx, iframe in enumerate(_v_iframes, 1):
                src = iframe.get('src', 'N/A')
                print(f"      [{idx}] src: {src[:100]}")
        else:
            print("   iframe 없음")
        
        print("\n" + "=" * 80)
        print("✅ 분석 완료!")
        print("=" * 80)
        print("\n📁 생성된 파일:")
        print("   - naver_shopping_page_source.html (HTML 소스)")
        print("   - naver_shopping_screenshot.png (스크린샷)")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        _v_driver.quit()
        print("\n🔚 브라우저 종료")

if __name__ == "__main__":
    analyze_page()
