#!/usr/bin/env python3
"""
Complete Naver Event Pipeline
1. Downloads images using Playwright (bypasses rate limits)
2. Extracts text using local OCR (PaddleOCR - no API limits)
3. Parses event information
"""

import asyncio
import os
import json
import re
import time
import random
from pathlib import Path
from typing import Dict, List, Optional

# Import Playwright crawler
import sys
sys.path.append(os.path.dirname(__file__))
from naver_playwright_crawler import NaverPlaywrightCrawler


class LocalOCRExtractor:
    """Extract text using local PaddleOCR (no API rate limits)"""

    def __init__(self):
        self.ocr = None
        self._init_ocr()

    def _init_ocr(self):
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            print("🔧 Initializing PaddleOCR (Korean)...")

            # Check for local models
            det_model = 'models/paddleocr/ch_PP-OCRv4_det_infer'
            rec_model = 'models/paddleocr/korean_PP-OCRv3_rec_infer'
            cls_model = 'models/paddleocr/ch_ppocr_mobile_v2.0_cls_infer'

            # Fallback to v3 detection
            if not os.path.exists(det_model):
                det_model = 'models/paddleocr/ch_PP-OCRv3_det_infer'

            if os.path.exists(det_model) and os.path.exists(rec_model):
                print(f"    ✓ Using local models")
                self.ocr = PaddleOCR(
                    text_detection_model_dir=det_model,
                    text_recognition_model_dir=rec_model,
                    textline_orientation_model_dir=cls_model if os.path.exists(cls_model) else None,
                    use_textline_orientation=os.path.exists(cls_model),
                    lang='korean'
                )
            else:
                print(f"    ⚠ Local models not found, downloading...")
                os.environ['DISABLE_MODEL_SOURCE_CHECK'] = 'True'
                self.ocr = PaddleOCR(
                    lang='korean',
                    use_textline_orientation=True
                )

            print("    ✓ PaddleOCR initialized")

        except ImportError:
            print("    ✗ PaddleOCR not installed")
            print("    Install: pip install paddlepaddle paddleocr")
            self.ocr = None
        except Exception as e:
            print(f"    ✗ Failed to initialize PaddleOCR: {e}")
            self.ocr = None

    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image"""
        if not self.ocr:
            return None

        try:
            results = self.ocr.ocr(image_path, cls=True)

            if results and results[0]:
                text_lines = [line[1][0] for line in results[0]]
                return '\n'.join(text_lines)

            return ""

        except Exception as e:
            print(f"    ✗ OCR error on {os.path.basename(image_path)}: {e}")
            return None

    def extract_all_text(self, image_files: List[str]) -> Dict[str, str]:
        """Extract text from all images"""
        print(f"\n{'='*70}")
        print("OCR Text Extraction (Local PaddleOCR)")
        print(f"{'='*70}\n")

        extracted_texts = {}

        for idx, image_file in enumerate(image_files, 1):
            print(f"[{idx}/{len(image_files)}] {os.path.basename(image_file)}")

            text = self.extract_text_from_image(image_file)
            extracted_texts[image_file] = text or ""

            if text:
                print(f"    ✓ Extracted {len(text)} characters")
            else:
                print(f"    ✗ No text extracted")

            # Small delay
            time.sleep(0.5)

        success_count = len([t for t in extracted_texts.values() if t])
        print(f"\n{'='*70}")
        print(f"✓ OCR Complete: {success_count}/{len(image_files)} successful")
        print(f"{'='*70}\n")

        return extracted_texts


class EventInfoParser:
    """Parse event information from OCR text"""

    @staticmethod
    def parse_event_info(texts: Dict[str, str], url: str, brand_name: str = None) -> Dict:
        """Parse event information from extracted texts"""
        print(f"\n{'='*70}")
        print("Event Information Parsing")
        print(f"{'='*70}\n")

        # Combine all text
        all_text = '\n'.join(texts.values())

        event_data = {
            'platform_name': 'Naver Brand',
            'brand_name': brand_name or EventInfoParser._extract_brand(all_text),
            'url': url,
            'event_title': EventInfoParser._extract_title(all_text),
            'event_date': EventInfoParser._extract_date(all_text),
            'benefits_by_purchase_amount': EventInfoParser._extract_purchase_benefits(all_text),
            'coupon_benefits': EventInfoParser._extract_coupon_benefits(all_text)
        }

        # Print results
        print(f"Platform: {event_data['platform_name']}")
        print(f"Brand: {event_data['brand_name']}")
        print(f"Event Title: {event_data['event_title']}")
        print(f"Event Period: {event_data['event_date']}")
        print(f"Purchase Benefits: {len(event_data['benefits_by_purchase_amount'])} found")
        print(f"Coupon Benefits: {len(event_data['coupon_benefits'])} found")

        return event_data

    @staticmethod
    def _extract_brand(text: str) -> Optional[str]:
        """Extract brand name"""
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

    @staticmethod
    def _extract_title(text: str) -> Optional[str]:
        """Extract event title"""
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
                title = re.sub(r'\s+', ' ', title)
                if 5 <= len(title) <= 100:
                    return title

        return None

    @staticmethod
    def _extract_date(text: str) -> Optional[str]:
        """Extract event date"""
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

    @staticmethod
    def _extract_purchase_benefits(text: str) -> List[str]:
        """Extract benefits by purchase amount"""
        benefits = []
        lines = text.split('\n')
        current_benefit = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Look for purchase amount pattern
            if re.search(r'(\d+만원|만\s*원)\s*이상\s*구매', line):
                if current_benefit:
                    benefits.append(' '.join(current_benefit))
                current_benefit = [line]

                # Look ahead for details
                if i + 1 < len(lines) and lines[i+1].strip():
                    next_line = lines[i+1].strip()
                    if not re.search(r'\d+만원', next_line):
                        current_benefit.append(next_line)

            elif current_benefit and not re.search(r'쿠폰|천원', line):
                current_benefit.append(line)
                if len(current_benefit) >= 2:
                    benefits.append(' '.join(current_benefit))
                    current_benefit = []

        if current_benefit:
            benefits.append(' '.join(current_benefit))

        # Clean up
        benefits = [' '.join(b.split()) for b in benefits]
        benefits = list(dict.fromkeys(benefits))

        return benefits

    @staticmethod
    def _extract_coupon_benefits(text: str) -> List[str]:
        """Extract coupon benefits"""
        coupons = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Look for coupon amount
            if re.search(r'\d+천\s*원', line):
                coupon_info = [line]

                # Get previous line for type
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


async def main():
    """Run complete pipeline"""
    import sys

    # Configuration
    url = 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684'
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'moderate'

    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║           Complete Naver Event Extraction Pipeline               ║
║                                                                  ║
║  Step 1: Download images (Playwright - bypasses rate limits)    ║
║  Step 2: Extract text (Local OCR - no API limits)               ║
║  Step 3: Parse event info                                       ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Download images with Playwright
    print("\n" + "="*70)
    print("STEP 1: Downloading Images with Playwright")
    print("="*70)

    crawler = NaverPlaywrightCrawler(
        output_dir='naver_playwright_images',
        strategy=strategy,
        headless=True
    )

    crawl_result = await crawler.crawl(url)

    if not crawl_result['success']:
        print(f"\n❌ Failed to download images: {crawl_result['error']}")
        return

    brand_name = crawl_result['brand_name']
    image_files = crawl_result['downloaded_images']

    print(f"\n✅ Successfully downloaded {len(image_files)} images")

    # Step 2: Extract text with local OCR
    print("\n" + "="*70)
    print("STEP 2: Extracting Text with Local OCR")
    print("="*70)

    ocr_extractor = LocalOCRExtractor()

    if not ocr_extractor.ocr:
        print("\n❌ OCR not available. Please install:")
        print("   pip install paddlepaddle paddleocr")
        return

    texts = ocr_extractor.extract_all_text(image_files)

    # Step 3: Parse event information
    print("\n" + "="*70)
    print("STEP 3: Parsing Event Information")
    print("="*70)

    event_data = EventInfoParser.parse_event_info(texts, url, brand_name)

    # Save results
    output_file = 'naver_complete_event_data.json'
    result = {
        'event_data': event_data,
        'raw_ocr_texts': {os.path.basename(k): v for k, v in texts.items()},
        'metadata': {
            'images_downloaded': len(image_files),
            'ocr_method': 'PaddleOCR (Local)',
            'crawler_method': 'Playwright Stealth'
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*70}")
    print("FINAL RESULTS")
    print(f"{'='*70}\n")
    print(json.dumps(event_data, ensure_ascii=False, indent=2))
    print(f"\n✓ Results saved to: {output_file}")
    print(f"\n✅ Pipeline completed successfully!")


if __name__ == '__main__':
    # Suppress warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run pipeline
    asyncio.run(main())
