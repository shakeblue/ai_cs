# Vision-Based Extraction Guide

## Overview

This guide covers the new **vision-based extraction pipeline** that extracts event data directly from images without using OCR.

## How It Works

### Traditional OCR-Based Pipeline (3 steps):
1. Download images
2. **Extract text using OCR.space API**
3. Parse text with LLM
4. Save to database

### New Vision-Based Pipeline (2 steps):
1. Download images
2. **Extract data directly from images with Vision LLM** ✨
3. Save to database

## Advantages of Vision-Based Approach

✅ **Simpler**: One less API dependency (no OCR.space needed)
✅ **More Accurate**: LLM sees layout, colors, emphasis, formatting
✅ **Better Context**: Understands visual hierarchy and design
✅ **No OCR Errors**: Eliminates text recognition errors

## Cost Comparison

| Provider | OCR-based (per 1000) | Vision-based (per 1000) | Difference |
|----------|---------------------|------------------------|------------|
| GPT-4o Mini | $0.40 | ~$0.60 | +$0.20 |
| Claude Haiku | $2.00 | ~$2.50 | +$0.50 |
| Gemini Flash | $0.20 | ~$0.30 | +$0.10 |

Vision is slightly more expensive but provides better accuracy and a simpler pipeline.

## Quick Start

### 1. Prerequisites

```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate

# Install required packages
pip install openai anthropic google-generativeai Pillow
```

### 2. Set API Keys

Edit `/home/long/ai_cs/crawler/.env`:

```bash
# For GPT-4o Mini (recommended)
OPENAI_API_KEY=sk-...

# For Claude Haiku
ANTHROPIC_API_KEY=sk-ant-...

# For Gemini Flash
GOOGLE_API_KEY=...
```

### 3. Run Vision Pipeline

```bash
# Using GPT-4o Mini (recommended - best value)
python cj/vision_pipeline.py "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"

# Using Claude Haiku (highest accuracy)
python cj/vision_pipeline.py "https://brand.naver.com/iope/..." --provider claude

# Using Gemini Flash (fastest)
python cj/vision_pipeline.py "https://brand.naver.com/iope/..." --provider gemini
```

## Compare OCR vs Vision

Run both pipelines and compare accuracy:

```bash
# Compare using GPT-4o Mini for both
python cj/compare_ocr_vs_vision.py "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"

# Compare different providers
python cj/compare_ocr_vs_vision.py "https://brand.naver.com/iope/..." \
  --ocr-llm gpt \
  --vision-provider claude

# Use free OCR strategy vs Vision
python cj/compare_ocr_vs_vision.py "https://brand.naver.com/iope/..." \
  --ocr-strategy semantic \
  --vision-provider gpt
```

The comparison script will:
- Run both pipelines on the same URL
- Compare extracted data field-by-field
- Show similarity scores
- Display cost and performance metrics
- Save detailed comparison report

## Command-Line Options

### Vision Pipeline

```bash
python cj/vision_pipeline.py <URL> [OPTIONS]
```

| Option | Choices | Default | Description |
|--------|---------|---------|-------------|
| `--provider` | `claude`, `gpt`, `gemini` | `gpt` | Vision LLM provider |
| `--crawler` | `gentle`, `moderate`, `aggressive` | `moderate` | Crawler speed |
| `--output` | directory path | `vision_event_images` | Output directory |

### Comparison Script

```bash
python cj/compare_ocr_vs_vision.py <URL> [OPTIONS]
```

| Option | Choices | Default | Description |
|--------|---------|---------|-------------|
| `--ocr-strategy` | various | `hybrid-semantic-llm-pattern` | OCR pipeline strategy |
| `--ocr-llm` | `claude`, `gpt`, `gemini` | `gpt` | LLM for OCR pipeline |
| `--vision-provider` | `claude`, `gpt`, `gemini` | `gpt` | Vision provider |

## Testing Individual Components

### Test Vision Extractor

```bash
# Test with downloaded images
python cj/vision_extractor.py naver_event_images/image1.jpg naver_event_images/image2.jpg
```

This will test all available vision providers and show extracted data.

## Output

Results are saved to:
- **JSON file**: `vision_event_images/vision_event_data_{brand_name}.json`
- **Supabase**: If configured (automatic)
- **Comparison report**: `comparison_report_{timestamp}.json` (when using compare script)

## Comparison Metrics

The comparison script evaluates:

1. **Event Title Match**: Exact match (✓/✗)
2. **Event Date Match**: Exact match (✓/✗)
3. **Benefits Similarity**: Jaccard similarity (0-100%)
4. **Coupons Similarity**: Jaccard similarity (0-100%)
5. **Overall Similarity**: Average of all scores (0-100%)

Plus cost and performance metrics.

## Recommendations

### When to Use Vision-Based:
- **Complex layouts**: Multiple columns, overlapping text
- **Visual emphasis**: Colors, fonts, sizes matter
- **High accuracy needed**: Want best possible extraction
- **Simpler pipeline**: Prefer fewer dependencies

### When to Use OCR-Based:
- **Cost-sensitive**: Need lowest possible cost
- **Text-heavy**: Simple text extraction
- **Free tier**: Using semantic/pattern strategies

### Best of Both:
Use the comparison script to test both approaches on your actual data and make an informed decision!

## Troubleshooting

### "API key not found"
Set the required API key in `.env` file.

### "PIL not installed"
```bash
pip install Pillow
```

### "Image too large"
The vision extractor automatically resizes images to fit API limits.

### Rate Limit Errors
Use gentler crawler:
```bash
python cj/vision_pipeline.py "https://..." --crawler gentle
```

## Next Steps

1. **Test with sample URL**: Run comparison on one event
2. **Evaluate accuracy**: Check which method works better for your data
3. **Consider costs**: Balance accuracy vs cost for your use case
4. **Choose approach**: Use vision for production or keep OCR-based

## Examples

### Example 1: Quick Test
```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate
python cj/vision_pipeline.py "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"
```

### Example 2: Full Comparison
```bash
python cj/compare_ocr_vs_vision.py \
  "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684" \
  --ocr-llm gpt \
  --vision-provider gpt
```

### Example 3: Compare Providers
```bash
# Test Claude vision vs GPT OCR
python cj/compare_ocr_vs_vision.py \
  "https://brand.naver.com/iope/..." \
  --ocr-llm gpt \
  --vision-provider claude
```

## Support

For issues:
- Check API keys are set correctly
- Ensure all packages are installed
- Review error messages for specific issues
- Try different providers if one fails
