#!/usr/bin/env python3
"""
Naver Event OCR Data Extractor
Extracts event information from images using OCR.space API
"""

import requests
import os
import json
import re
import time
import random
from pathlib import Path
from typing import Dict, List, Optional


class NaverEventOCRExtractor:
    """Extract event information from images using OCR"""

    def __init__(self, api_key: str = "K87899142388957", delay_min=1, delay_max=3):
        self.api_key = api_key
        self.ocr_url = "https://api.ocr.space/parse/image"
        self.delay_min = delay_min
        self.delay_max = delay_max

    def _delay(self, message="OCR API rate limiting"):
        """Add delay to respect API rate limits"""
        delay = random.uniform(self.delay_min, self.delay_max)
        print(f"    ⏱ {message}: {delay:.1f}초 대기 중...")
        time.sleep(delay)

    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using OCR.space API"""
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'apikey': self.api_key,
                    'language': 'kor',
                    'isOverlayRequired': False,
                    'detectOrientation': True,
                    'scale': True,
                    'OCREngine': 2  # Engine 2 for Asian languages
                }

                response = requests.post(
                    self.ocr_url,
                    files=files,
                    data=data,
                    timeout=30,
                    verify=False
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get('ParsedResults'):
                        text = result['ParsedResults'][0].get('ParsedText', '')
                        return text.strip()

            return None

        except Exception as e:
            print(f"    ✗ OCR 추출 실패: {e}")
            return None

    def extract_all_text(self, image_files: List[str]) -> Dict[str, str]:
        """Extract text from all images with rate limiting"""
        print(f"\n{'='*70}")
        print("OCR 텍스트 추출 시작")
        print(f"{'='*70}\n")

        extracted_texts = {}

        for idx, image_file in enumerate(image_files, 1):
            # Add delay between API calls (except first one)
            if idx > 1:
                self._delay(f"이미지 {idx} OCR 전 대기")

            print(f"[{idx}/{len(image_files)}] {os.path.basename(image_file)} 처리 중...")

            text = self.extract_text_from_image(image_file)
            extracted_texts[image_file] = text or ""

            if text:
                print(f"    ✓ {len(text)} 문자 추출")
            else:
                print(f"    ✗ 텍스트 추출 실패")

        print(f"\n{'='*70}")
        print(f"✓ OCR 완료: {len([t for t in extracted_texts.values() if t])}/{len(image_files)}개 성공")
        print(f"{'='*70}\n")

        return extracted_texts

    def parse_event_info(self, texts: Dict[str, str], url: str, brand_name: str = None) -> Dict:
        """Parse event information from extracted texts"""
        print(f"\n{'='*70}")
        print("이벤트 정보 파싱")
        print(f"{'='*70}\n")

        # Combine all text
        all_text = '\n'.join(texts.values())

        event_data = {
            'platform_name': 'Naver Brand',
            'brand_name': brand_name or self._extract_brand(all_text),
            'url': url,
            'event_title': self._extract_title(all_text),
            'event_date': self._extract_date(all_text),
            'benefits_by_purchase_amount': self._extract_purchase_benefits(all_text),
            'coupon_benefits': self._extract_coupon_benefits(all_text)
        }

        # Print results
        print(f"✓ 플랫폼: {event_data['platform_name']}")
        print(f"✓ 브랜드: {event_data['brand_name']}")
        print(f"✓ 이벤트 제목: {event_data['event_title']}")
        print(f"✓ 이벤트 기간: {event_data['event_date']}")
        print(f"✓ 금액대별 혜택: {len(event_data['benefits_by_purchase_amount'])}개")
        print(f"✓ 쿠폰 혜택: {len(event_data['coupon_benefits'])}개")

        return event_data

    def _extract_brand(self, text: str) -> Optional[str]:
        """Extract brand name from text"""
        # Common brand patterns
        brands = [
            'IOPE', '아이오페', 'iope',
            '설화수', 'Sulwhasoo',
            '라네즈', 'LANEIGE',
            '헤라', 'HERA',
            '에스트라', 'AESTURA',
            '이니스프리', 'innisfree'
        ]

        for brand in brands:
            if re.search(brand, text, re.IGNORECASE):
                return brand.upper() if brand.isupper() else brand

        return None

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract event title from text"""
        # Look for common event title patterns
        patterns = [
            r'([^\n]{5,50}기획전)',
            r'([^\n]{5,50}이벤트)',
            r'([^\n]{5,50}특가)',
            r'([^\n]{5,50}프로모션)',
            r'(XMD[^\n]{0,40})',
            r'(스템3[^\n]{0,40})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                title = match.group(1).strip()
                # Clean up title
                title = re.sub(r'\s+', ' ', title)
                if 5 <= len(title) <= 100:
                    return title

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract event date from text"""
        # Date patterns
        patterns = [
            r'(\d{1,2}\.\d{1,2}\s*[~-]\s*\d{1,2}\.\d{1,2})',
            r'(\d{4}\.\d{1,2}\.\d{1,2}\s*[~-]\s*\d{4}\.\d{1,2}\.\d{1,2})',
            r'(\d{1,2}/\d{1,2}\s*[~-]\s*\d{1,2}/\d{1,2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_purchase_benefits(self, text: str) -> List[str]:
        """Extract benefits by purchase amount"""
        benefits = []
        lines = text.split('\n')

        current_benefit = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Look for purchase amount pattern (e.g., "5만원 이상 구매")
            if re.search(r'(\d+만원|만\s*원)\s*이상\s*구매', line):
                if current_benefit:
                    benefits.append(' '.join(current_benefit))
                current_benefit = [line]

                # Look ahead for benefit details
                if i + 1 < len(lines) and lines[i+1].strip():
                    next_line = lines[i+1].strip()
                    if not re.search(r'\d+만원', next_line):
                        current_benefit.append(next_line)

            elif current_benefit and not re.search(r'쿠폰|천원', line):
                current_benefit.append(line)
                if len(current_benefit) >= 2:
                    benefits.append(' '.join(current_benefit))
                    current_benefit = []

        # Add remaining benefit
        if current_benefit:
            benefits.append(' '.join(current_benefit))

        # Clean up and deduplicate
        benefits = [' '.join(b.split()) for b in benefits]
        benefits = list(dict.fromkeys(benefits))  # Remove duplicates while preserving order

        return benefits

    def _extract_coupon_benefits(self, text: str) -> List[str]:
        """Extract coupon benefits"""
        coupons = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Look for coupon amount pattern (e.g., "4천원", "5천원")
            if re.search(r'\d+천\s*원', line):
                coupon_info = [line]

                # Get previous line for coupon type
                if i > 0 and '쿠폰' in lines[i-1]:
                    coupon_info.insert(0, lines[i-1].strip())

                # Get next line for condition
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and not re.search(r'^\d+천원', next_line):
                        coupon_info.append(next_line)

                coupon_text = ' '.join(coupon_info)
                if coupon_text and coupon_text not in coupons:
                    coupons.append(coupon_text)

        # Clean up
        coupons = [' '.join(c.split()) for c in coupons]

        return coupons

    def save_results(self, event_data: Dict, texts: Dict[str, str], output_file: str = 'naver_event_data.json'):
        """Save extraction results to JSON file"""
        result = {
            'event_data': event_data,
            'raw_ocr_texts': {os.path.basename(k): v for k, v in texts.items()}
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 결과 저장: {output_file}")

        return output_file


def main():
    """Test function"""
    # Test with downloaded images
    image_dir = 'naver_brand_images'

    if not os.path.exists(image_dir):
        print(f"❌ 이미지 디렉토리가 없습니다: {image_dir}")
        return

    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
        image_files.extend(Path(image_dir).glob(ext))

    image_files = [str(f) for f in image_files]

    if not image_files:
        print(f"❌ 이미지 파일이 없습니다")
        return

    print(f"📁 발견된 이미지: {len(image_files)}개")

    # Extract OCR text
    extractor = NaverEventOCRExtractor()
    texts = extractor.extract_all_text(image_files)

    # Parse event info
    url = 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684'
    event_data = extractor.parse_event_info(texts, url, 'IOPE')

    # Save results
    extractor.save_results(event_data, texts)

    # Display results
    print(f"\n{'='*70}")
    print("추출된 이벤트 정보")
    print(f"{'='*70}\n")
    print(json.dumps(event_data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
