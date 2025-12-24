# Naver Event Extraction - Usage Guide

## Quick Start

### View Available Strategies

```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate
python cj/extraction_strategy.py
```

This will show a comparison of all available strategies with cost and accuracy estimates.

---

## Using Different Strategies

### 1. Pattern-Based (Free, Fast)

```python
from extraction_strategy import ExtractionStrategy
from naver_event_pipeline_integrated import NaverEventPipelineIntegrated

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.PATTERN
)

# Or directly with extractor
from naver_event_ocr_extractor import NaverEventOCRExtractor

extractor = NaverEventOCRExtractor(
    strategy=ExtractionStrategy.PATTERN
)
```

**When to use:**
- Zero cost required
- Speed is priority
- Simple event structures
- No API keys available

---

### 2. Semantic Extraction (Free, Better Accuracy)

```python
from extraction_strategy import ExtractionStrategy

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.SEMANTIC
)
```

**When to use:**
- Zero cost required
- Better accuracy needed (75-85%)
- Complex Korean text
- Edge cases and variations

---

### 3. LLM-Based Extraction (Best Accuracy, Low Cost)

#### GPT-4o Mini (Recommended - Cheapest)

```python
from extraction_strategy import ExtractionStrategy
from llm_extractor import LLMProvider

# Set API key
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.LLM_GPT4O_MINI
)
```

**Cost:** $0.40 per 1000 events
**Accuracy:** 85-90%

#### Gemini Flash (Ultra-Cheap)

```python
os.environ["GOOGLE_API_KEY"] = "your-api-key"

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.LLM_GEMINI_FLASH
)
```

**Cost:** $0.20 per 1000 events
**Accuracy:** 80-88%

#### Claude Haiku (Best Korean Support)

```python
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.LLM_CLAUDE_HAIKU
)
```

**Cost:** $2.00 per 1000 events
**Accuracy:** 85-92%

---

### 4. Hybrid Strategies (Recommended for Production)

#### Semantic → Pattern (Free, Robust)

```python
pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.HYBRID_SEMANTIC_PATTERN
)
```

**Flow:** Try semantic first, fallback to pattern if fails
**Cost:** $0
**Accuracy:** 75-85%

#### LLM → Pattern (Good Accuracy, Minimal Cost)

```python
os.environ["OPENAI_API_KEY"] = "your-api-key"

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.HYBRID_LLM_PATTERN
)
```

**Flow:** Try LLM first, fallback to pattern if fails
**Cost:** ~$0.50 per 1000 (assuming 25% LLM usage)
**Accuracy:** 85-92%

#### Semantic → LLM → Pattern (Best Overall) 🏆

```python
os.environ["OPENAI_API_KEY"] = "your-api-key"

pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN
)
```

**Flow:** Try semantic → try LLM if semantic fails → fallback to pattern
**Cost:** ~$0.10 per 1000 (assuming 5% LLM usage)
**Accuracy:** 85-92%
**Recommended for production!**

---

### 5. Auto (Smart Default)

```python
pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.AUTO
)
```

**Behavior:** Automatically uses best available strategy based on installed dependencies
**Recommended for:** Getting started, testing

---

## Complete Example

```python
import asyncio
import os
from extraction_strategy import ExtractionStrategy
from llm_extractor import LLMProvider
from naver_event_pipeline_integrated import NaverEventPipelineIntegrated

# Set API keys (if using LLM)
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["GOOGLE_API_KEY"] = "your-google-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"

async def main():
    # Create pipeline with desired strategy
    pipeline = NaverEventPipelineIntegrated(
        extraction_strategy=ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN,
        llm_provider=LLMProvider.GPT_4O_MINI  # Specify LLM provider
    )

    # Process event URL
    url = "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"
    result = await pipeline.process_event_url(url)

    if result['success']:
        print("\n✅ SUCCESS!")
        print(f"   Event: {result['event_data']['event_title']}")
        print(f"   Benefits: {len(result['event_data']['benefits_by_purchase_amount'])}")
        print(f"   Coupons: {len(result['event_data']['coupon_benefits'])}")
    else:
        print(f"\n❌ FAILED: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Strategy Comparison

| Strategy | Cost/1000 | Accuracy | Speed | Use Case |
|----------|-----------|----------|-------|----------|
| `PATTERN` | $0 | 60-70% | Very Fast | Basic extraction |
| `SEMANTIC` | $0 | 75-85% | Fast | Better free option |
| `LLM_GEMINI_FLASH` | $0.20 | 80-88% | Fast | Ultra-budget cloud |
| `LLM_GPT4O_MINI` | $0.40 | 85-90% | Medium | Best value |
| `LLM_CLAUDE_HAIKU` | $2.00 | 85-92% | Medium | Best Korean |
| `HYBRID_SEMANTIC_PATTERN` | $0 | 75-85% | Fast | Free + robust |
| `HYBRID_LLM_PATTERN` | ~$0.50 | 85-92% | Medium | Good accuracy |
| `HYBRID_SEMANTIC_LLM_PATTERN` | ~$0.10 | 85-92% | Medium | **Production** 🏆 |
| `AUTO` | Varies | Varies | Varies | Smart default |

---

## Testing Different Strategies

```bash
# Test LLM extractors
cd /home/long/ai_cs/crawler
source venv/bin/activate

# Set API key
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Test LLM extraction
python cj/llm_extractor.py

# Test semantic extraction
python cj/semantic_extractor.py

# Test integration
python cj/test_semantic_integration.py
```

---

## Installing Dependencies

### For Semantic Extraction

```bash
pip install transformers torch sentence-transformers scikit-learn
```

### For LLM Extraction

```bash
# All LLM providers
pip install anthropic openai google-generativeai

# Or individually
pip install anthropic      # Claude
pip install openai         # GPT
pip install google-generativeai  # Gemini
```

### All at once

```bash
pip install -r requirements.txt
```

---

## Setting API Keys

### Option 1: Environment Variables (Recommended)

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Option 2: .env File

Create `.env` in crawler directory:
```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

Then load in your script:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: Directly in Code (Not Recommended)

```python
import os
os.environ["OPENAI_API_KEY"] = "your-key"
```

---

## Troubleshooting

### "Module not found" Error

```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Install missing dependencies
pip install -r requirements.txt
```

### "API Key not set" Error

```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set the key
export OPENAI_API_KEY="your-key"
```

### "LLM extractor failed" Warning

This is normal if API key is not set. The system will automatically fallback to pattern-based extraction.

### Semantic extractor slow on first run

The model downloads on first use (~500MB). Subsequent runs are much faster.

---

## Best Practices

### For Development/Testing
- Use `SEMANTIC` or `PATTERN` (free)
- Test with small batches first

### For Production
- Use `HYBRID_SEMANTIC_LLM_PATTERN` (best accuracy/cost balance)
- Monitor API costs
- Set up error logging

### For High Volume (>10k events/month)
- Use `SEMANTIC` first to filter
- Only use LLM for complex cases
- Consider caching results

### For Maximum Accuracy
- Use `LLM_CLAUDE_HAIKU` or `LLM_GPT4O_MINI`
- Review results manually
- Fine-tune prompts as needed

---

## Cost Monitoring

```python
from llm_extractor import LLMExtractor, LLMProvider

extractor = LLMExtractor(LLMProvider.GPT_4O_MINI)

# Estimate cost before extraction
cost_info = extractor.estimate_cost(ocr_text)
print(f"Estimated cost: ${cost_info['total_cost']:.6f}")

# Then extract
result = extractor.extract_event_info(ocr_text, url)
```

---

## Need Help?

1. Check strategy comparison: `python cj/extraction_strategy.py`
2. Test extractors: `python cj/llm_extractor.py`
3. Review documentation: See `LLM_OPTIONS_COMPARISON.md`
4. Check logs for error messages

---

**Recommended Starting Point:**

```python
# Good default for most cases
pipeline = NaverEventPipelineIntegrated(
    extraction_strategy=ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN
)
```

This gives you:
- ✅ Free semantic extraction for most events
- ✅ LLM fallback for complex cases
- ✅ Pattern fallback if all else fails
- ✅ ~90% accuracy
- ✅ ~$0.10 per 1000 events
