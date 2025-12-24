#!/usr/bin/env python3
"""
LLM-Based Event Information Extractor
Supports multiple providers: Claude Haiku, GPT-4o Mini, Gemini Flash
"""

import os
import json
import re
from typing import Dict, Optional, List
from enum import Enum

# Import LLM clients (all optional)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠ Anthropic not installed. Install with: pip install anthropic")

try:
    import openai
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


class LLMProvider(Enum):
    """Available LLM providers"""
    CLAUDE_HAIKU = "claude-haiku"
    GPT_4O_MINI = "gpt-5-mini"
    GEMINI_FLASH = "gemini-flash"


class LLMExtractor:
    """Extract event information using LLM APIs"""

    # Model identifiers
    MODELS = {
        LLMProvider.CLAUDE_HAIKU: "claude-3-5-haiku-20241022",
        LLMProvider.GPT_4O_MINI: "gpt-4o-mini",
        LLMProvider.GEMINI_FLASH: "gemini-1.5-flash",
    }

    # Cost per million tokens (input, output)
    COSTS = {
        LLMProvider.CLAUDE_HAIKU: (0.80, 4.00),
        LLMProvider.GPT_4O_MINI: (0.15, 0.60),
        LLMProvider.GEMINI_FLASH: (0.075, 0.30),
    }

    def __init__(self, provider: LLMProvider = LLMProvider.GPT_4O_MINI):
        """
        Initialize LLM extractor

        Args:
            provider: Which LLM provider to use (default: GPT-4o Mini)
        """
        self.provider = provider
        self.model = self.MODELS[provider]

        # Initialize appropriate client
        if provider == LLMProvider.CLAUDE_HAIKU:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic library not installed")
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = anthropic.Anthropic(api_key=api_key)

        elif provider == LLMProvider.GPT_4O_MINI:
            if not OPENAI_AVAILABLE:
                raise ImportError("OpenAI library not installed")
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = openai.OpenAI(api_key=api_key)

        elif provider == LLMProvider.GEMINI_FLASH:
            if not GOOGLE_AVAILABLE:
                raise ImportError("Google Generative AI library not installed")
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)

        print(f"✓ LLM Extractor initialized: {provider.value} ({self.model})")

    def _build_prompt(self, ocr_text: str) -> str:
        """Build extraction prompt for Korean event data"""
        return f"""다음은 Naver Brand 이벤트 페이지의 OCR 텍스트입니다.
이 텍스트에서 이벤트 정보를 추출해주세요.

OCR 텍스트:
{ocr_text}

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
{{
  "event_title": "제목 또는 null",
  "event_date": "날짜 또는 null",
  "benefits_by_purchase_amount": ["혜택1", "혜택2"],
  "coupon_benefits": ["쿠폰1", "쿠폰2"]
}}

예시:
입력: "5만원 이상 구매시 파우치 증정, 10% 할인 쿠폰 제공"
출력:
{{
  "benefits_by_purchase_amount": ["5만원 이상 구매시 파우치 증정"],
  "coupon_benefits": ["10% 할인 쿠폰"]
}}

최종 확인:
- 모든 혜택을 빠짐없이 추출했나요?
- 중복된 항목이 없나요?
- "쿠폰" 키워드로 정확히 분류했나요?
- JSON 형식만 응답하세요 (설명 없이)
"""

    def extract_event_info(self, ocr_text: str, url: str = None) -> Optional[Dict]:
        """
        Extract event information using LLM

        Args:
            ocr_text: OCR text from event images
            url: Event URL (for reference)

        Returns:
            Dictionary with extracted event information, or None if failed
        """
        prompt = self._build_prompt(ocr_text)

        try:
            if self.provider == LLMProvider.CLAUDE_HAIKU:
                return self._extract_claude(prompt)
            elif self.provider == LLMProvider.GPT_4O_MINI:
                return self._extract_openai(prompt)
            elif self.provider == LLMProvider.GEMINI_FLASH:
                return self._extract_gemini(prompt)
        except Exception as e:
            print(f"⚠ LLM extraction failed ({self.provider.value}): {e}")
            return None

    def _extract_claude(self, prompt: str) -> Optional[Dict]:
        """Extract using Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        result_text = response.content[0].text
        return self._parse_json_response(result_text)

    def _extract_openai(self, prompt: str) -> Optional[Dict]:
        """Extract using OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        result_text = response.choices[0].message.content
        return self._parse_json_response(result_text)

    def _extract_gemini(self, prompt: str) -> Optional[Dict]:
        """Extract using Google Gemini API"""
        response = self.client.generate_content(
            prompt,
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

    def estimate_cost(self, ocr_text: str) -> Dict[str, float]:
        """
        Estimate API cost for extraction

        Args:
            ocr_text: OCR text to process

        Returns:
            Dictionary with cost breakdown
        """
        # Rough token estimation (1 token ≈ 4 characters for English, 1-2 for Korean)
        input_tokens = len(ocr_text) / 2  # Conservative estimate for Korean
        prompt_tokens = 500  # Approximate prompt overhead
        total_input = input_tokens + prompt_tokens

        output_tokens = 200  # Expected JSON output

        input_cost_per_mtok, output_cost_per_mtok = self.COSTS[self.provider]

        input_cost = (total_input / 1_000_000) * input_cost_per_mtok
        output_cost = (output_tokens / 1_000_000) * output_cost_per_mtok
        total_cost = input_cost + output_cost

        return {
            "input_tokens": int(total_input),
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "provider": self.provider.value,
            "model": self.model
        }


def test_llm_extractor():
    """Test LLM extractor with sample data"""

    sample_text = """
뷰티 포인트 적립 이벤트
IOPE
2024.01.01 - 2024.01.31

연동 후 구매 시 N pay 1% 적립
연동 후 상시 구매 시 뷰티포인트 1% 적립

5만원 이상 구매 시 사은품 증정
10만원 이상 구매 시 추가 할인

4천원 할인 쿠폰
무료배송 쿠폰

XMD 스템 3 세럼
59,800원 37,310원
    """

    print("=" * 70)
    print("Testing LLM Extractors")
    print("=" * 70)

    # Test available providers
    providers_to_test = []

    if ANTHROPIC_AVAILABLE and os.environ.get("ANTHROPIC_API_KEY"):
        providers_to_test.append(LLMProvider.CLAUDE_HAIKU)

    if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
        providers_to_test.append(LLMProvider.GPT_4O_MINI)

    if GOOGLE_AVAILABLE and os.environ.get("GOOGLE_API_KEY"):
        providers_to_test.append(LLMProvider.GEMINI_FLASH)

    if not providers_to_test:
        print("❌ No LLM providers available")
        print("   Set API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY")
        return

    for provider in providers_to_test:
        print(f"\n{'=' * 70}")
        print(f"Testing: {provider.value}")
        print(f"{'=' * 70}\n")

        try:
            extractor = LLMExtractor(provider=provider)

            # Estimate cost
            cost = extractor.estimate_cost(sample_text)
            print(f"💰 Estimated cost: ${cost['total_cost']:.6f}")
            print(f"   Input: {cost['input_tokens']} tokens (${cost['input_cost']:.6f})")
            print(f"   Output: {cost['output_tokens']} tokens (${cost['output_cost']:.6f})")

            # Extract
            print("\n🔄 Extracting...")
            result = extractor.extract_event_info(sample_text)

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

    print(f"\n{'=' * 70}")
    print("✓ Testing complete")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    test_llm_extractor()
