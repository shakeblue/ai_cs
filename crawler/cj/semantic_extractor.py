"""
Semantic Extractor for Naver Event Information
Uses NLP/Semantic similarity to extract event information from OCR text
"""

from typing import List, Optional, Dict
import re
import warnings
warnings.filterwarnings('ignore')

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("⚠ Semantic extraction dependencies not installed")
    print("  Install with: pip install sentence-transformers scikit-learn")


class SemanticExtractor:
    """Use semantic similarity to extract event information"""

    def __init__(self):
        if not SEMANTIC_AVAILABLE:
            raise ImportError("Semantic extraction dependencies not available")

        print("🔄 Loading multilingual sentence transformer model...")
        # Using paraphrase-multilingual-MiniLM-L12-v2 as default
        # This is a lightweight, fast multilingual model that works well for Korean
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✓ Model loaded: paraphrase-multilingual-MiniLM-L12-v2")

        # Reference embeddings for event components
        self.benefit_examples = [
            "5만원 이상 구매시 할인",
            "10% 적립",
            "포인트 적립",
            "구매 금액별 사은품 증정",
            "무료 배송",
            "N pay 적립",
            "뷰티포인트 적립",
            "연동 후 구매 시 적립",
            "구매 시 증정",
            "쿠폰 제공",
        ]

        self.coupon_examples = [
            "4천원 할인 쿠폰",
            "10% 할인 쿠폰",
            "무료배송 쿠폰",
            "추가 할인 쿠폰",
            "즉시 할인 쿠폰",
            "5천원 쿠폰 증정",
            "웰컴 쿠폰 제공",
            "신규 가입 쿠폰",
            "첫 구매 쿠폰",
            "생일 축하 쿠폰",
        ]

        # Negative examples - things that are NOT coupons
        # These help the model distinguish coupons from general benefits
        self.non_coupon_examples = [
            "구매 시 포인트 적립",
            "뷰티포인트 적립 이벤트",
            "5만원 이상 구매 시 사은품",
            "구매 금액별 혜택 제공",
            "이벤트 기간 할인",
            "N pay 적립",
        ]

        self.title_examples = [
            "신년 특별 기획전",
            "럭키백 이벤트",
            "봄맞이 세일",
            "뷰티 포인트 적립",
            "신제품 런칭",
            "특별 할인",
        ]

        # Precompute embeddings
        print("🔄 Precomputing reference embeddings...")
        self.benefit_embeddings = self.model.encode(self.benefit_examples)
        self.coupon_embeddings = self.model.encode(self.coupon_examples)
        self.non_coupon_embeddings = self.model.encode(self.non_coupon_examples)
        self.title_embeddings = self.model.encode(self.title_examples)
        print("✓ Reference embeddings ready")

    def extract_benefits_semantic(self, text: str, threshold: float = 0.5) -> List[str]:
        """
        Extract benefits using semantic similarity

        Args:
            text: OCR text to extract benefits from
            threshold: Minimum similarity score (0-1) to consider a match

        Returns:
            List of benefit strings
        """
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 10]

        if not lines:
            return []

        # Encode all lines
        line_embeddings = self.model.encode(lines)

        # Compute similarity with benefit examples
        similarities = cosine_similarity(line_embeddings, self.benefit_embeddings)
        max_similarities = similarities.max(axis=1)

        # Extract lines with high similarity
        benefits = []
        for i, sim in enumerate(max_similarities):
            if sim > threshold:
                benefit_text = lines[i]

                # Look ahead for related context (next 2 lines)
                context = [benefit_text]
                for j in range(i + 1, min(i + 3, len(lines))):
                    if max_similarities[j] <= threshold:  # Not another benefit
                        context.append(lines[j])
                    else:
                        break

                combined = ' '.join(context)
                if combined not in benefits:
                    benefits.append(combined)

        return benefits

    def extract_coupons_semantic(self, text: str, threshold: float = 0.65,
                                  exclude_benefits: List[str] = None) -> List[str]:
        """
        Extract coupons using enhanced semantic similarity with negative filtering

        Args:
            text: OCR text to extract coupons from
            threshold: Minimum similarity score (0-1) - HIGHER threshold to reduce false positives
            exclude_benefits: List of already extracted benefits to exclude

        Returns:
            List of coupon strings
        """
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]

        if not lines:
            return []

        # Encode all lines
        line_embeddings = self.model.encode(lines)

        # Compute similarity with coupon examples
        coupon_similarities = cosine_similarity(line_embeddings, self.coupon_embeddings)
        max_coupon_sim = coupon_similarities.max(axis=1)

        # Compute similarity with NON-coupon examples (negative filtering)
        non_coupon_similarities = cosine_similarity(line_embeddings, self.non_coupon_embeddings)
        max_non_coupon_sim = non_coupon_similarities.max(axis=1)

        # Extract lines with high similarity or containing "쿠폰"
        coupons = []
        processed = set()
        exclude_set = set(exclude_benefits) if exclude_benefits else set()

        for i, coupon_sim in enumerate(max_coupon_sim):
            if i in processed:
                continue

            line = lines[i]

            # Skip if this line was already extracted as a benefit
            # Check exact match or if line is a substring of any benefit
            if exclude_set:
                skip = False
                for benefit in exclude_set:
                    if line == benefit or line in benefit or benefit in line:
                        skip = True
                        break
                if skip:
                    continue

            # Calculate confidence score
            # Coupon score should be higher than non-coupon score
            confidence = coupon_sim - max_non_coupon_sim[i]

            # Strong coupon indicators
            has_coupon_keyword = '쿠폰' in line
            high_confidence = confidence > 0.2  # Coupon similarity is significantly higher
            high_similarity = coupon_sim > threshold

            # STRICT filtering: Require either keyword OR very high confidence
            is_coupon = False

            if has_coupon_keyword:
                # Lines with "쿠폰" keyword - always include
                is_coupon = True
            elif high_similarity and high_confidence:
                # High semantic similarity AND clearly not a benefit
                is_coupon = True
            elif coupon_sim > 0.75:
                # Very high similarity - likely a coupon even without keyword
                is_coupon = True

            if is_coupon:
                # Filter out lines that look like prices or product names
                if re.match(r'^[\d,]+원\s+[\d,]+원$', line):
                    continue
                if re.match(r'^[\d,]+원$', line):
                    continue

                # Only add context for lines with explicit "쿠폰" keyword
                if has_coupon_keyword:
                    coupon_parts = [line]
                    processed.add(i)

                    # Optionally add next line if it looks like a condition
                    if i + 1 < len(lines) and i + 1 not in processed:
                        next_line = lines[i+1]
                        # Only add if it's clearly a condition, not another coupon/benefit
                        if (any(keyword in next_line for keyword in ['구매', '이상', '조건', '적용'])
                            and '쿠폰' not in next_line
                            and max_coupon_sim[i+1] < threshold):
                            coupon_parts.append(next_line)
                            processed.add(i+1)

                    coupons.append(' '.join(coupon_parts))
                else:
                    # For semantic matches without "쿠폰" keyword, be very conservative
                    coupons.append(line)
                    processed.add(i)

        return list(dict.fromkeys(coupons))  # Remove duplicates while preserving order

    def extract_title_semantic(self, text: str, threshold: float = 0.4) -> Optional[str]:
        """
        Extract title using semantic similarity

        Args:
            text: OCR text to extract title from
            threshold: Minimum similarity score (0-1) to consider a match

        Returns:
            Title string or None
        """
        # Focus on first 10 lines (titles usually at top)
        lines = [l.strip() for l in text.split('\n')
                if l.strip() and 10 <= len(l.strip()) <= 100][:10]

        if not lines:
            return None

        # Encode lines
        line_embeddings = self.model.encode(lines)

        # Compute similarity with title examples
        similarities = cosine_similarity(line_embeddings, self.title_embeddings)
        max_similarities = similarities.max(axis=1)

        # Return line with highest similarity
        best_idx = max_similarities.argmax()
        if max_similarities[best_idx] > threshold:
            return lines[best_idx]

        # Fallback: return first substantial line
        return lines[0] if lines else None

    def extract_all_semantic(self, text: str,
                            benefit_threshold: float = 0.5,
                            coupon_threshold: float = 0.65,  # Higher default for coupons
                            title_threshold: float = 0.4) -> Dict[str, any]:
        """
        Extract all event information using semantic similarity

        Args:
            text: OCR text to extract from
            benefit_threshold: Threshold for benefit extraction
            coupon_threshold: Threshold for coupon extraction (higher = more strict)
            title_threshold: Threshold for title extraction

        Returns:
            Dictionary with extracted information
        """
        # Extract benefits first
        benefits = self.extract_benefits_semantic(text, benefit_threshold)

        # Extract coupons, excluding already-found benefits
        coupons = self.extract_coupons_semantic(text, coupon_threshold, exclude_benefits=benefits)

        return {
            'title': self.extract_title_semantic(text, title_threshold),
            'benefits': benefits,
            'coupons': coupons,
        }


def test_semantic_extractor():
    """Test the semantic extractor with sample data"""

    if not SEMANTIC_AVAILABLE:
        print("❌ Cannot test - dependencies not installed")
        return

    # Sample OCR text
    sample_text = """
뷰티 포인트 적립 이벤트
2024.01.01 - 2024.01.31

연동 후 구매 시 N pay 1% 적립
연동 후 상시 구매 시 뷰티포인트 1% 적립

5만원 이상 구매 시 사은품 증정
10만원 이상 구매 시 추가 할인

4천원 할인 쿠폰
무료배송 쿠폰
    """

    print("=== Testing Semantic Extractor ===\n")
    print(f"Sample text:\n{sample_text}\n")

    try:
        extractor = SemanticExtractor()

        print("\n=== Extraction Results (Using extract_all_semantic) ===\n")

        # Use extract_all_semantic which properly excludes benefits from coupons
        results = extractor.extract_all_semantic(sample_text)

        print(f"Title: {results['title']}")

        print(f"\nBenefits ({len(results['benefits'])}):")
        for i, benefit in enumerate(results['benefits'], 1):
            print(f"  {i}. {benefit}")

        print(f"\nCoupons ({len(results['coupons'])}):")
        for i, coupon in enumerate(results['coupons'], 1):
            print(f"  {i}. {coupon}")

        print("\n✓ Test completed successfully")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_semantic_extractor()
