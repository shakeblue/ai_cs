#!/usr/bin/env python3
"""
Vision-Based Event Information Extractor
Extracts event data directly from images without OCR step
Supports: Claude Haiku, GPT-4o Mini, Gemini Flash (all with vision)
"""

import os
import json
import base64
from typing import Dict, Optional, List
from pathlib import Path
from enum import Enum
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import LLM clients (all optional)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠ Anthropic not installed. Install with: pip install anthropic")

try:
    import openai
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠ OpenAI not installed. Install with: pip install openai")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠ Google Generative AI not installed. Install with: pip install google-generativeai")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠ PIL not installed. Install with: pip install Pillow")


class VisionProvider(Enum):
    """Available vision LLM providers"""
    CLAUDE_HAIKU = "claude-haiku-vision"
    GPT_4O_MINI = "gpt-4o-mini-vision"
    GEMINI_FLASH = "gemini-flash-vision"


class VisionExtractor:
    """Extract event information directly from images using vision LLMs"""

    # Model identifiers
    MODELS = {
        VisionProvider.CLAUDE_HAIKU: "claude-3-5-haiku-20241022",
        VisionProvider.GPT_4O_MINI: "gpt-5-mini",
        VisionProvider.GEMINI_FLASH: "gemini-1.5-flash",
    }

    # Cost per million tokens (input, output) + vision cost per image
    COSTS = {
        VisionProvider.CLAUDE_HAIKU: (0.80, 4.00, 0.0004),  # ~$0.0004 per image
        VisionProvider.GPT_4O_MINI: (0.15, 0.60, 0.0007),   # ~$0.0007 per image
        VisionProvider.GEMINI_FLASH: (0.075, 0.30, 0.0002), # ~$0.0002 per image
    }

    # Maximum image size for APIs (in pixels)
    MAX_IMAGE_SIZE = {
        VisionProvider.CLAUDE_HAIKU: (1568, 1568),
        VisionProvider.GPT_4O_MINI: (2048, 2048),
        VisionProvider.GEMINI_FLASH: (3072, 3072),
    }

    def __init__(self, provider: VisionProvider = VisionProvider.GPT_4O_MINI):
        """
        Initialize Vision extractor

        Args:
            provider: Which vision LLM provider to use (default: GPT-4o Mini)
        """
        self.provider = provider
        self.model = self.MODELS[provider]

        # Initialize appropriate client
        if provider == VisionProvider.CLAUDE_HAIKU:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic library not installed")
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = anthropic.Anthropic(api_key=api_key)

        elif provider == VisionProvider.GPT_4O_MINI:
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not installed")
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            # Create httpx client with SSL verification disabled
            http_client = httpx.Client(verify=False)
            self.client = openai.OpenAI(api_key=api_key, http_client=http_client)

        elif provider == VisionProvider.GEMINI_FLASH:
            if not GOOGLE_AVAILABLE:
                raise ImportError("Google Generative AI library not installed")
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)

        print(f"✓ Vision Extractor initialized: {provider.value} ({self.model})")

    def _resize_image_if_needed(self, image_path: str) -> str:
        """
        Resize image if it exceeds API limits

        Args:
            image_path: Path to image file

        Returns:
            Path to (possibly resized) image
        """
        if not PIL_AVAILABLE:
            return image_path

        max_width, max_height = self.MAX_IMAGE_SIZE[self.provider]

        try:
            img = Image.open(image_path)
            width, height = img.size

            if width <= max_width and height <= max_height:
                return image_path

            # Calculate resize ratio
            ratio = min(max_width / width, max_height / height)
            new_size = (int(width * ratio), int(height * ratio))

            # Resize and save to temp file
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
            temp_path = f"{image_path}.resized.jpg"
            img_resized.save(temp_path, "JPEG", quality=95)

            print(f"  ℹ Resized image: {width}x{height} → {new_size[0]}x{new_size[1]}")
            return temp_path

        except Exception as e:
            print(f"  ⚠ Image resize failed: {e}")
            return image_path

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_image_media_type(self, image_path: str) -> str:
        """Detect image media type from file extension"""
        ext = Path(image_path).suffix.lower()
        media_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return media_types.get(ext, 'image/jpeg')

    def _build_prompt(self) -> str:
        """Build extraction prompt for Korean event data"""
        return """이 이미지는 Naver Brand 이벤트 페이지입니다.
이미지에서 이벤트 정보를 추출해주세요.

다음 정보를 JSON 형식으로 추출하세요:

1. event_title: 이벤트 제목 (가장 눈에 띄는 제목 또는 기획전 이름)

2. event_date: 이벤트 기간 (날짜 범위가 있으면 추출)

3. benefits_by_purchase_amount: 구매 금액별 혜택 리스트
   ✅ 포함할 항목:
   - 사은품 증정 (예: "5만원 이상 구매시 파우치 증정")
   - 포인트 적립 (예: "N pay 1% 적립", "뷰티포인트 적립")
   - 무료 배송
   - 추가 할인 (단, "쿠폰" 키워드가 없는 경우만)

   ❌ 제외할 항목:
   - "쿠폰" 키워드가 포함된 모든 항목 (이건 coupon_benefits에 넣기)

4. coupon_benefits: 쿠폰 혜택 리스트
   ✅ 포함할 항목:
   - "쿠폰"이라는 키워드가 명시된 모든 항목
   - 예: "10% 할인 쿠폰", "4천원 쿠폰", "장바구니 쿠폰"

   ❌ 제외할 항목:
   - 쿠폰이 아닌 일반 혜택 (사은품, 포인트 등)

⚠️ 중요 규칙:
- 각 항목은 하나의 카테고리에만 포함하세요 (중복 금지!)
- "쿠폰" 키워드가 있으면 → coupon_benefits
- "쿠폰" 키워드가 없으면 → benefits_by_purchase_amount

응답 형식 (JSON만 출력):
{
  "event_title": "제목 또는 null",
  "event_date": "날짜 또는 null",
  "benefits_by_purchase_amount": ["혜택1", "혜택2"],
  "coupon_benefits": ["쿠폰1", "쿠폰2"]
}

예시:
입력: "5만원 이상 구매시 파우치 증정, 10% 할인 쿠폰 제공"
출력:
{
  "benefits_by_purchase_amount": ["5만원 이상 구매시 파우치 증정"],
  "coupon_benefits": ["10% 할인 쿠폰"]
}

최종 확인:
- 모든 혜택을 빠짐없이 추출했나요?
- 중복된 항목이 없나요?
- "쿠폰" 키워드로 정확히 분류했나요?
- JSON 형식만 응답하세요 (설명 없이)
"""

    def extract_from_images(self, image_paths: List[str], url: str = None) -> Optional[Dict]:
        """
        Extract event information from images using vision LLM

        Args:
            image_paths: List of paths to event images
            url: Event URL (for reference)

        Returns:
            Dictionary with extracted event information, or None if failed
        """
        if not image_paths:
            print("⚠ No images provided")
            return None

        print(f"  Processing {len(image_paths)} images with vision LLM...")

        try:
            if self.provider == VisionProvider.CLAUDE_HAIKU:
                return self._extract_claude(image_paths)
            elif self.provider == VisionProvider.GPT_4O_MINI:
                return self._extract_openai(image_paths)
            elif self.provider == VisionProvider.GEMINI_FLASH:
                return self._extract_gemini(image_paths)
        except Exception as e:
            print(f"⚠ Vision extraction failed ({self.provider.value}): {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_claude(self, image_paths: List[str]) -> Optional[Dict]:
        """Extract using Claude Vision API"""
        prompt = self._build_prompt()

        # Build content with multiple images
        content = []
        for img_path in image_paths:
            resized_path = self._resize_image_if_needed(img_path)
            image_data = self._encode_image(resized_path)
            media_type = self._get_image_media_type(resized_path)

            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data,
                }
            })

        # Add text prompt
        content.append({
            "type": "text",
            "text": prompt
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        result_text = response.content[0].text
        return self._parse_json_response(result_text)

    def _extract_openai(self, image_paths: List[str]) -> Optional[Dict]:
        """Extract using OpenAI Vision API"""
        prompt = self._build_prompt()

        # Build content with multiple images
        content = [{"type": "text", "text": prompt}]

        for img_path in image_paths:
            resized_path = self._resize_image_if_needed(img_path)
            image_data = self._encode_image(resized_path)
            media_type = self._get_image_media_type(resized_path)

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{image_data}"
                }
            })

        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        result_text = response.choices[0].message.content
        return self._parse_json_response(result_text)

    def _extract_gemini(self, image_paths: List[str]) -> Optional[Dict]:
        """Extract using Google Gemini Vision API"""
        prompt = self._build_prompt()

        # Build content with multiple images
        content = [prompt]

        for img_path in image_paths:
            resized_path = self._resize_image_if_needed(img_path)
            img = Image.open(resized_path)
            content.append(img)

        response = self.client.generate_content(
            content,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )

        result_text = response.text
        return self._parse_json_response(result_text)

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        try:
            # Try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            if "```json" in text:
                json_text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_text = text.split("```")[1].split("```")[0].strip()
            else:
                # Try to find JSON object
                match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
                if match:
                    json_text = match.group(0)
                else:
                    print(f"⚠ Could not find JSON in response: {text[:200]}")
                    return None

            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"⚠ JSON parsing failed: {e}")
                print(f"   Text: {json_text[:200]}")
                return None

    def estimate_cost(self, num_images: int) -> Dict[str, float]:
        """
        Estimate API cost for vision extraction

        Args:
            num_images: Number of images to process

        Returns:
            Dictionary with cost breakdown
        """
        input_cost_per_mtok, output_cost_per_mtok, cost_per_image = self.COSTS[self.provider]

        # Vision models have fixed cost per image + text tokens
        prompt_tokens = 500  # Approximate prompt overhead
        output_tokens = 200  # Expected JSON output

        image_cost = num_images * cost_per_image
        text_input_cost = (prompt_tokens / 1_000_000) * input_cost_per_mtok
        text_output_cost = (output_tokens / 1_000_000) * output_cost_per_mtok

        total_cost = image_cost + text_input_cost + text_output_cost

        return {
            "num_images": num_images,
            "image_cost": image_cost,
            "text_cost": text_input_cost + text_output_cost,
            "total_cost": total_cost,
            "provider": self.provider.value,
            "model": self.model
        }


def test_vision_extractor():
    """Test vision extractor with sample images"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vision_extractor.py <image_path1> [image_path2] ...")
        print("\nExample:")
        print("  python vision_extractor.py naver_event_images/event1.jpg")
        return

    image_paths = sys.argv[1:]

    # Validate images exist
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"❌ Image not found: {img_path}")
            return

    print("=" * 70)
    print("Testing Vision Extractors")
    print("=" * 70)
    print(f"Images: {len(image_paths)}")
    for img in image_paths:
        print(f"  - {img}")
    print()

    # Test available providers
    providers_to_test = []

    if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
        providers_to_test.append(VisionProvider.CLAUDE_HAIKU)

    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        providers_to_test.append(VisionProvider.GPT_4O_MINI)

    if GOOGLE_AVAILABLE and os.environ.get("GOOGLE_API_KEY"):
        providers_to_test.append(VisionProvider.GEMINI_FLASH)

    if not providers_to_test:
        print("❌ No LLM providers available")
        print("   Set API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY")
        return

    for provider in providers_to_test:
        print(f"\n{'=' * 70}")
        print(f"Testing: {provider.value}")
        print(f"{'=' * 70}\n")

        try:
            extractor = VisionExtractor(provider=provider)

            # Estimate cost
            cost = extractor.estimate_cost(len(image_paths))
            print(f"💰 Estimated cost: ${cost['total_cost']:.6f}")
            print(f"   Images: {cost['num_images']} images (${cost['image_cost']:.6f})")
            print(f"   Text: ${cost['text_cost']:.6f}")

            # Extract
            print("\n🔄 Extracting...")
            result = extractor.extract_from_images(image_paths)

            if result:
                print("✓ Extraction successful\n")
                print(json.dumps(result, ensure_ascii=False, indent=2))

                # Validate
                print("\n📊 Validation:")
                print(f"   Title: {'✓' if result.get('event_title') else '✗'}")
                print(f"   Date: {'✓' if result.get('event_date') else '✗'}")
                print(f"   Benefits: {len(result.get('benefits_by_purchase_amount', []))} found")
                print(f"   Coupons: {len(result.get('coupon_benefits', []))} found")
            else:
                print("✗ Extraction failed")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 70}")
    print("✓ Testing complete")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    test_vision_extractor()
