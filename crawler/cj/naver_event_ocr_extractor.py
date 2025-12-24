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

# Import extraction strategies
try:
    from .extraction_strategy import ExtractionStrategy
    from .semantic_extractor import SemanticExtractor, SEMANTIC_AVAILABLE
    from .llm_extractor import LLMExtractor, LLMProvider
except ImportError:
    try:
        from extraction_strategy import ExtractionStrategy
        from semantic_extractor import SemanticExtractor, SEMANTIC_AVAILABLE
        from llm_extractor import LLMExtractor, LLMProvider
    except ImportError:
        SEMANTIC_AVAILABLE = False
        SemanticExtractor = None
        LLMExtractor = None
        ExtractionStrategy = None
        LLMProvider = None


class NaverEventOCRExtractor:
    """Extract event information from images using OCR"""

    def __init__(self, api_key: str = "K87899142388957", delay_min=1, delay_max=3,
                 strategy: 'ExtractionStrategy' = None, llm_provider: 'LLMProvider' = None):
        """
        Initialize OCR extractor

        Args:
            api_key: OCR.space API key
            delay_min: Minimum delay between API calls (seconds)
            delay_max: Maximum delay between API calls (seconds)
            strategy: Extraction strategy to use (default: AUTO)
            llm_provider: LLM provider if using LLM strategy (default: GPT4O_MINI)
        """
        self.api_key = api_key
        self.ocr_url = "https://api.ocr.space/parse/image"
        self.delay_min = delay_min
        self.delay_max = delay_max

        # Set default strategy
        if strategy is None:
            if ExtractionStrategy:
                strategy = ExtractionStrategy.AUTO
            else:
                strategy = "pattern"  # Fallback if module not available

        self.strategy = strategy
        self.llm_provider = llm_provider

        # Initialize extractors
        self.semantic_extractor = None
        self.llm_extractor = None

        # Initialize based on strategy
        self._initialize_extractors()

    def _initialize_extractors(self):
        """Initialize extractors based on selected strategy"""
        strategy_str = self.strategy.value if hasattr(self.strategy, 'value') else str(self.strategy)

        print(f"🔧 Initializing extraction strategy: {strategy_str}")

        # Determine which extractors are needed
        needs_semantic = any(s in strategy_str for s in ['semantic', 'auto'])
        needs_llm = any(s in strategy_str for s in ['llm', 'auto'])

        # Initialize semantic extractor if needed
        if needs_semantic and SEMANTIC_AVAILABLE:
            try:
                print("  🔄 Loading semantic extractor...")
                self.semantic_extractor = SemanticExtractor()
                print("  ✓ Semantic extractor ready")
            except Exception as e:
                print(f"  ⚠ Semantic extractor failed: {e}")
                self.semantic_extractor = None

        # Initialize LLM extractor if needed
        if needs_llm and LLMExtractor:
            try:
                # Determine LLM provider
                if 'claude' in strategy_str:
                    provider = LLMProvider.CLAUDE_HAIKU
                elif 'gemini' in strategy_str:
                    provider = LLMProvider.GEMINI_FLASH
                elif 'gpt' in strategy_str:
                    provider = LLMProvider.GPT_4O_MINI
                elif self.llm_provider:
                    provider = self.llm_provider
                else:
                    provider = LLMProvider.GPT_4O_MINI  # Default

                print(f"  🔄 Loading LLM extractor ({provider.value})...")
                self.llm_extractor = LLMExtractor(provider=provider)
                print("  ✓ LLM extractor ready")
            except Exception as e:
                print(f"  ⚠ LLM extractor failed: {e}")
                self.llm_extractor = None

        print(f"✓ Strategy initialized: {strategy_str}")

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
        """Parse event information using selected strategy"""
        print(f"\n{'='*70}")
        print("이벤트 정보 파싱")
        print(f"{'='*70}\n")

        # Combine all text
        all_text = '\n'.join(texts.values())

        strategy_str = self.strategy.value if hasattr(self.strategy, 'value') else str(self.strategy)
        print(f"📋 Strategy: {strategy_str}")

        # Route to appropriate extraction method
        if strategy_str == 'pattern':
            event_data = self._extract_with_patterns(all_text, url, brand_name)

        elif strategy_str == 'semantic':
            event_data = self._extract_with_semantic(all_text, url, brand_name)

        elif 'llm-' in strategy_str:
            event_data = self._extract_with_llm(all_text, url, brand_name)

        elif strategy_str == 'hybrid-semantic-pattern':
            event_data = self._extract_hybrid_semantic_pattern(all_text, url, brand_name)

        elif strategy_str == 'hybrid-llm-pattern':
            event_data = self._extract_hybrid_llm_pattern(all_text, url, brand_name)

        elif strategy_str == 'hybrid-semantic-llm-pattern':
            event_data = self._extract_hybrid_semantic_llm_pattern(all_text, url, brand_name)

        elif strategy_str == 'auto':
            event_data = self._extract_auto(all_text, url, brand_name)

        else:
            print(f"⚠ Unknown strategy '{strategy_str}', using pattern-based")
            event_data = self._extract_with_patterns(all_text, url, brand_name)

        # Print results
        print(f"\n✓ 플랫폼: {event_data['platform_name']}")
        print(f"✓ 브랜드: {event_data['brand_name']}")
        print(f"✓ 이벤트 제목: {event_data['event_title']}")
        print(f"✓ 이벤트 기간: {event_data['event_date']}")
        print(f"✓ 금액대별 혜택: {len(event_data['benefits_by_purchase_amount'])}개")
        print(f"✓ 쿠폰 혜택: {len(event_data['coupon_benefits'])}개")

        return event_data

    def _extract_with_patterns(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Extract event information using pattern-based approach"""
        print("🔍 Using pattern-based extraction...")
        return {
            'platform_name': 'Naver Brand',
            'brand_name': brand_name or self._extract_brand(all_text, url),
            'url': url,
            'event_title': self._extract_title(all_text),
            'event_date': self._extract_date(all_text),
            'benefits_by_purchase_amount': self._extract_purchase_benefits(all_text),
            'coupon_benefits': self._extract_coupon_benefits(all_text)
        }

    def _extract_with_semantic(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Extract using semantic/NLP approach"""
        print("🔍 Using semantic extraction...")

        if not self.semantic_extractor:
            print("⚠ Semantic extractor not available, falling back to patterns")
            return self._extract_with_patterns(all_text, url, brand_name)

        try:
            result = self.semantic_extractor.extract_all_semantic(all_text)
            return {
                'platform_name': 'Naver Brand',
                'brand_name': brand_name or self._extract_brand(all_text, url),
                'url': url,
                'event_title': result.get('title') or self._extract_title(all_text),
                'event_date': self._extract_date(all_text),
                'benefits_by_purchase_amount': result.get('benefits', []),
                'coupon_benefits': result.get('coupons', [])
            }
        except Exception as e:
            print(f"⚠ Semantic extraction failed: {e}, falling back to patterns")
            return self._extract_with_patterns(all_text, url, brand_name)

    def _extract_with_llm(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Extract using LLM approach"""
        print("🔍 Using LLM extraction...")

        if not self.llm_extractor:
            print("⚠ LLM extractor not available, falling back to patterns")
            return self._extract_with_patterns(all_text, url, brand_name)

        try:
            result = self.llm_extractor.extract_event_info(all_text, url)
            if result:
                return {
                    'platform_name': 'Naver Brand',
                    'brand_name': brand_name or result.get('brand_name') or self._extract_brand(all_text, url),
                    'url': url,
                    'event_title': result.get('event_title'),
                    'event_date': result.get('event_date'),
                    'benefits_by_purchase_amount': result.get('benefits_by_purchase_amount', []),
                    'coupon_benefits': result.get('coupon_benefits', [])
                }
            else:
                print("⚠ LLM returned no results, falling back to patterns")
                return self._extract_with_patterns(all_text, url, brand_name)
        except Exception as e:
            print(f"⚠ LLM extraction failed: {e}, falling back to patterns")
            return self._extract_with_patterns(all_text, url, brand_name)

    def _extract_hybrid_semantic_pattern(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Hybrid: Try semantic first, fallback to pattern"""
        print("🔍 Using hybrid extraction (Semantic → Pattern)...")

        if self.semantic_extractor:
            try:
                result = self.semantic_extractor.extract_all_semantic(all_text)
                # Validate results
                if result.get('title') or result.get('benefits') or result.get('coupons'):
                    print("✓ Semantic successful")
                    return {
                        'platform_name': 'Naver Brand',
                        'brand_name': brand_name or self._extract_brand(all_text, url),
                        'url': url,
                        'event_title': result.get('title') or self._extract_title(all_text),
                        'event_date': self._extract_date(all_text),
                        'benefits_by_purchase_amount': result.get('benefits', []),
                        'coupon_benefits': result.get('coupons', [])
                    }
            except Exception as e:
                print(f"⚠ Semantic failed: {e}")

        print("→ Falling back to pattern-based")
        return self._extract_with_patterns(all_text, url, brand_name)

    def _extract_hybrid_llm_pattern(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Hybrid: Try LLM first, fallback to pattern"""
        print("🔍 Using hybrid extraction (LLM → Pattern)...")

        if self.llm_extractor:
            try:
                result = self.llm_extractor.extract_event_info(all_text, url)
                if result:
                    print("✓ LLM successful")
                    return {
                        'platform_name': 'Naver Brand',
                        'brand_name': brand_name or result.get('brand_name') or self._extract_brand(all_text, url),
                        'url': url,
                        'event_title': result.get('event_title'),
                        'event_date': result.get('event_date'),
                        'benefits_by_purchase_amount': result.get('benefits_by_purchase_amount', []),
                        'coupon_benefits': result.get('coupon_benefits', [])
                    }
            except Exception as e:
                print(f"⚠ LLM failed: {e}")

        print("→ Falling back to pattern-based")
        return self._extract_with_patterns(all_text, url, brand_name)

    def _extract_hybrid_semantic_llm_pattern(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Hybrid: Try semantic → LLM → pattern"""
        print("🔍 Using hybrid extraction (Semantic → LLM → Pattern)...")

        # Try semantic first
        if self.semantic_extractor:
            try:
                result = self.semantic_extractor.extract_all_semantic(all_text)
                if result.get('title') or result.get('benefits') or result.get('coupons'):
                    print("✓ Semantic successful")
                    return {
                        'platform_name': 'Naver Brand',
                        'brand_name': brand_name or self._extract_brand(all_text, url),
                        'url': url,
                        'event_title': result.get('title') or self._extract_title(all_text),
                        'event_date': self._extract_date(all_text),
                        'benefits_by_purchase_amount': result.get('benefits', []),
                        'coupon_benefits': result.get('coupons', [])
                    }
            except Exception as e:
                print(f"⚠ Semantic failed: {e}")

        # Try LLM if semantic failed
        print("→ Trying LLM...")
        if self.llm_extractor:
            try:
                result = self.llm_extractor.extract_event_info(all_text, url)
                if result:
                    print("✓ LLM successful")
                    return {
                        'platform_name': 'Naver Brand',
                        'brand_name': brand_name or result.get('brand_name') or self._extract_brand(all_text, url),
                        'url': url,
                        'event_title': result.get('event_title'),
                        'event_date': result.get('event_date'),
                        'benefits_by_purchase_amount': result.get('benefits_by_purchase_amount', []),
                        'coupon_benefits': result.get('coupon_benefits', [])
                    }
            except Exception as e:
                print(f"⚠ LLM failed: {e}")

        # Final fallback to pattern
        print("→ Falling back to pattern-based")
        return self._extract_with_patterns(all_text, url, brand_name)

    def _extract_auto(self, all_text: str, url: str, brand_name: str = None) -> Dict:
        """Auto: Use best available strategy"""
        print("🔍 Using auto extraction (best available)...")

        # Prefer semantic if available
        if self.semantic_extractor:
            return self._extract_hybrid_semantic_llm_pattern(all_text, url, brand_name)
        # Try LLM if no semantic
        elif self.llm_extractor:
            return self._extract_hybrid_llm_pattern(all_text, url, brand_name)
        # Fallback to pattern
        else:
            return self._extract_with_patterns(all_text, url, brand_name)

    def _extract_brand(self, text: str, url: str = None) -> Optional[str]:
        """Extract brand with dynamic detection"""

        # 1. Try to extract from URL first
        if url:
            url_match = re.search(r'brand\.naver\.com/([^/]+)', url)
            if url_match:
                brand_from_url = url_match.group(1)
                # Validate it appears in text
                if re.search(brand_from_url, text, re.IGNORECASE):
                    return brand_from_url

        # 2. Known brands (extended list)
        known_brands = [
            'IOPE', '아이오페', 'iope',
            '설화수', 'Sulwhasoo',
            '라네즈', 'LANEIGE',
            '헤라', 'HERA',
            '에스트라', 'AESTURA',
            '이니스프리', 'innisfree',
            # NEW: Add more brands
            '마몽드', 'MAMONDE',
            '려', 'RYO',
            '미쟝센', 'MISE EN SCENE',
            '에뛰드', 'ETUDE',
            '아모레퍼시픽', 'AMOREPACIFIC',
        ]

        for brand in known_brands:
            if re.search(brand, text, re.IGNORECASE):
                return brand.upper() if brand.isupper() else brand

        # 3. NEW: Look for brand-like patterns (capitalized words)
        brand_pattern = r'\b([A-Z][A-Za-z]{2,15})\b'
        matches = re.findall(brand_pattern, text)
        if matches:
            # Return most frequent capitalized word
            from collections import Counter
            counter = Counter(matches)
            most_common = counter.most_common(1)[0][0]
            if counter[most_common] >= 2:  # Appears at least twice
                return most_common

        return None

    def _extract_title(self, text: str) -> Optional[str]:
        """Extract event title with expanded patterns"""
        patterns = [
            # Original patterns
            r'([^\n]{5,50}기획전)',
            r'([^\n]{5,50}이벤트)',
            r'([^\n]{5,50}특가)',
            r'([^\n]{5,50}프로모션)',

            # NEW: Additional event keywords
            r'([^\n]{5,50}딜)',
            r'([^\n]{5,50}할인)',
            r'([^\n]{5,50}세일)',
            r'([^\n]{5,50}쇼핑)',
            r'([^\n]{5,50}런칭)',
            r'([^\n]{5,50}오픈)',
            r'([^\n]{5,50}단독)',
            r'([^\n]{5,50}혜택)',
            r'([^\n]{5,50}적립)',

            # NEW: Pattern for lines ending with exclamation/emphasis
            r'([^\n]{10,60}[!！])',

            # NEW: Pattern for ALL CAPS titles
            r'([A-Z\s]{10,50})',

            # Keep product-specific as fallback
            r'(XMD[^\n]{0,40})',
            r'(스템3[^\n]{0,40})',
        ]

        # Try patterns in order, return first valid match
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                title = match.group(1).strip()
                title = re.sub(r'\s+', ' ', title)
                if 5 <= len(title) <= 100:
                    return title

        # NEW: Fallback - use first substantial line
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:5]:  # Check first 5 lines
            if 10 <= len(line) <= 100 and not re.search(r'^\d+', line):
                return line

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
        """Extract benefits with expanded patterns"""
        benefits = []
        lines = text.split('\n')

        # EXPANDED: Multiple benefit patterns
        benefit_patterns = [
            # Original
            r'(\d+만원|만\s*원)\s*이상\s*구매',

            # NEW: Additional amount patterns
            r'(\d+)천원\s*이상',
            r'(\d+)원\s*이상',
            r'(\d{1,3})(,\d{3})+원\s*이상',

            # NEW: Percentage patterns
            r'\d+%\s*(할인|적립|증정)',

            # NEW: Gift/benefit keywords
            r'구매\s*시\s*.*?(증정|제공|적립)',
            r'구매금액별',
            r'금액대별',

            # NEW: Loyalty/points patterns
            r'(포인트|적립)\s*\d+%',
            r'N\s*pay\s*\d+%',
            r'뷰티포인트.*?적립',
        ]

        current_benefit = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check if line matches any benefit pattern
            is_benefit = False
            for pattern in benefit_patterns:
                if re.search(pattern, line):
                    is_benefit = True
                    break

            if is_benefit:
                if current_benefit:
                    benefits.append(' '.join(current_benefit))
                current_benefit = [line]

                # Look ahead for details (next 2 lines)
                for j in range(i+1, min(i+3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not any(re.search(p, next_line) for p in benefit_patterns):
                        current_benefit.append(next_line)
                    else:
                        break

                if current_benefit:
                    benefits.append(' '.join(current_benefit))
                    current_benefit = []

        # Clean up
        benefits = [' '.join(b.split()) for b in benefits]
        benefits = list(dict.fromkeys(benefits))

        return benefits

    def _extract_coupon_benefits(self, text: str) -> List[str]:
        """Extract coupons with expanded patterns"""
        coupons = []
        lines = text.split('\n')
        processed_indices = set()  # Track processed lines to avoid duplicates

        # REFINED: More specific coupon patterns
        coupon_patterns = [
            # Strong coupon indicators (high priority)
            r'쿠폰',
            r'\d+%\s*(할인|OFF)',
            r'\d+천\s*원.*?(쿠폰|할인)',

            # Special benefits
            r'무료\s*배송',
            r'무료\s*증정',
            r'추가\s*증정',
        ]

        for i, line in enumerate(lines):
            if i in processed_indices:
                continue

            line = line.strip()
            if not line or len(line) < 5:  # Skip very short lines
                continue

            # Check if this line is a real coupon indicator
            is_coupon_line = False
            for pattern in coupon_patterns:
                if re.search(pattern, line):
                    is_coupon_line = True
                    break

            # Skip pure price displays (e.g., "59,800원 37,310원")
            if re.match(r'^[\d,]+원\s+[\d,]+원$', line):
                continue

            if is_coupon_line:
                coupon_info = [line]
                processed_indices.add(i)

                # Only add context if current line has strong coupon keyword
                if '쿠폰' in line or '할인' in line or 'OFF' in line:
                    # Context: previous line for coupon type (but avoid price-only lines)
                    if i > 0 and i-1 not in processed_indices:
                        prev_line = lines[i-1].strip()
                        if prev_line and len(prev_line) < 50:
                            # Skip if it's just prices
                            if not re.match(r'^[\d,]+원\s+[\d,]+원$', prev_line):
                                if not re.match(r'^\d+[\.,]\d+', prev_line):  # Skip number-only
                                    coupon_info.insert(0, prev_line)
                                    processed_indices.add(i-1)

                    # Context: next line for conditions (but avoid duplicating price displays)
                    if i + 1 < len(lines) and i+1 not in processed_indices:
                        next_line = lines[i+1].strip()
                        if next_line and len(next_line) < 100:
                            # Skip if it's just prices or already processed
                            if not re.match(r'^[\d,]+원\s+[\d,]+원$', next_line):
                                # Check if next line adds value
                                if '구매' in next_line or '이상' in next_line or '조건' in next_line:
                                    coupon_info.append(next_line)
                                    processed_indices.add(i+1)

                coupon_text = ' '.join(coupon_info)
                if coupon_text and len(coupon_text) > 5:
                    coupons.append(coupon_text)

        # Advanced deduplication: remove substrings
        unique_coupons = []
        for coupon in coupons:
            # Check if this coupon is a substring of any existing coupon
            is_substring = False
            for existing in unique_coupons:
                if coupon in existing or existing in coupon:
                    # Keep the longer one
                    if len(coupon) > len(existing):
                        unique_coupons.remove(existing)
                        unique_coupons.append(coupon)
                    is_substring = True
                    break

            if not is_substring:
                unique_coupons.append(coupon)

        # Clean up
        unique_coupons = [' '.join(c.split()) for c in unique_coupons]

        return unique_coupons

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
