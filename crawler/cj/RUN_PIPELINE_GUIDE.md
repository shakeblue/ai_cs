# Naver Event Pipeline - Usage Guide

## Quick Start

```bash
# Activate virtual environment
cd /home/long/ai_cs/crawler
source venv/bin/activate

# Run with recommended settings (hybrid approach with GPT-4o Mini)
python cj/run_pipeline.py "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"
```

## Command-Line Options

### Basic Usage

```bash
python cj/run_pipeline.py <URL> [OPTIONS]
```

### Available Options

| Option | Choices | Default | Description |
|--------|---------|---------|-------------|
| `--strategy, -s` | See below | `hybrid-semantic-llm-pattern` | Extraction strategy |
| `--llm` | `claude`, `gpt`, `gemini` | `gpt` | LLM provider for LLM strategies |
| `--crawler` | `gentle`, `moderate`, `aggressive` | `moderate` | Crawler speed/delay |
| `--output` | directory path | `naver_event_images` | Output directory |
| `--ocr-key` | API key | Uses default | Override OCR.space API key |
| `--compare` | - | - | Show comparison of all strategies |
| `--list-strategies` | - | - | List all strategies with details |

## Extraction Strategies

### Recommended Strategies

#### 🏆 Best Overall: Hybrid Semantic-LLM-Pattern
```bash
python cj/run_pipeline.py "https://..." --strategy hybrid-semantic-llm-pattern --llm gpt
```
- **Cost**: $0.10 per 1000 events
- **Accuracy**: 85-92%
- **How it works**: Tries semantic extraction first, falls back to LLM if needed, then pattern as last resort

#### 💰 Best Value: GPT-4o Mini (Pure LLM)
```bash
python cj/run_pipeline.py "https://..." --strategy llm-gpt4o-mini
```
- **Cost**: $0.40 per 1000 events
- **Accuracy**: 85-90%
- **Speed**: Medium

#### 🎯 Highest Accuracy: Claude Haiku
```bash
python cj/run_pipeline.py "https://..." --strategy llm-claude-haiku
```
- **Cost**: $2.00 per 1000 events
- **Accuracy**: 85-92%
- **Speed**: Medium

#### ⚡ Fastest LLM: Gemini Flash
```bash
python cj/run_pipeline.py "https://..." --strategy llm-gemini-flash
```
- **Cost**: $0.20 per 1000 events
- **Accuracy**: 80-88%
- **Speed**: Fast

### Free Strategies (No API Key Required)

#### Pattern-Based (Regex)
```bash
python cj/run_pipeline.py "https://..." --strategy pattern
```
- **Cost**: Free
- **Accuracy**: 60-70%
- **Speed**: Very Fast

#### Semantic (NLP)
```bash
python cj/run_pipeline.py "https://..." --strategy semantic
```
- **Cost**: Free
- **Accuracy**: 75-85%
- **Speed**: Fast

## Prerequisites

### 1. Install Dependencies

```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate

# For GPT-4o Mini (recommended):
pip install openai

# For Claude Haiku:
pip install anthropic

# For Gemini Flash:
pip install google-generativeai
```

### 2. Set API Keys

Create or edit `/home/long/ai_cs/crawler/.env`:

```bash
# For GPT-4o Mini
OPENAI_API_KEY=sk-...

# For Claude Haiku
ANTHROPIC_API_KEY=sk-ant-...

# For Gemini Flash
GOOGLE_API_KEY=...

# OCR.space API key (optional, has default)
OCR_SPACE_API_KEY=K87899142388957
```

## Examples

### Example 1: Quick Test with Free Strategy
```bash
python cj/run_pipeline.py \
  "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684" \
  --strategy semantic
```

### Example 2: Production Run with Hybrid Strategy
```bash
python cj/run_pipeline.py \
  "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684" \
  --strategy hybrid-semantic-llm-pattern \
  --llm gpt \
  --crawler moderate \
  --output my_events
```

### Example 3: High Accuracy with Claude
```bash
python cj/run_pipeline.py \
  "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684" \
  --strategy llm-claude-haiku \
  --crawler gentle
```

### Example 4: Fast Processing with Gemini
```bash
python cj/run_pipeline.py \
  "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684" \
  --strategy llm-gemini-flash \
  --crawler aggressive
```

### Example 5: Compare All Strategies
```bash
python cj/run_pipeline.py --compare
```

## Pipeline Steps

The pipeline executes these steps automatically:

1. **Download Images**: Uses Playwright to bypass Naver rate limits
2. **OCR Extraction**: Extracts text from images using OCR.space API
3. **Event Parsing**: Parses event information using selected strategy
4. **Database Save**: Saves to Supabase (optional) and local JSON

## Output

Results are saved to:
- **JSON file**: `{output_dir}/event_data_{brand_name}.json`
- **Supabase**: If configured (automatic)
- **Images**: `{output_dir}/` directory

## Strategy Comparison

To view a detailed comparison of all strategies:

```bash
python cj/run_pipeline.py --compare
```

This shows:
- Cost per 1000 events
- Expected accuracy range
- Processing speed
- Recommendations

## Troubleshooting

### "API key not found"
Make sure you've set the required API key in `.env` file:
```bash
# Edit .env file
nano /home/long/ai_cs/crawler/.env

# Add the required key:
OPENAI_API_KEY=your_key_here
```

### "Module not installed"
Install the required package:
```bash
source venv/bin/activate
pip install openai  # or anthropic, or google-generativeai
```

### Rate Limit Errors
Try a gentler crawler strategy:
```bash
python cj/run_pipeline.py "https://..." --crawler gentle
```

## Cost Estimation

| Strategy | 10 events | 100 events | 1000 events |
|----------|-----------|------------|-------------|
| Pattern/Semantic | Free | Free | Free |
| Gemini Flash | $0.002 | $0.02 | $0.20 |
| GPT-4o Mini | $0.004 | $0.04 | $0.40 |
| Hybrid (recommended) | $0.001 | $0.01 | $0.10 |
| Claude Haiku | $0.02 | $0.20 | $2.00 |

## Best Practices

1. **Start with free strategies** to test your workflow
2. **Use hybrid strategy** for production (best accuracy/cost ratio)
3. **Use gentle crawler** for large batches to avoid rate limits
4. **Check output JSON** before processing many events
5. **Set API keys in .env** rather than command line

## Support

For issues or questions:
- Check the [main crawler guide](../USAGE_GUIDE.md)
- Review [extraction tuning guide](COUPON_EXTRACTION_TUNING_GUIDE.md)
- Compare [LLM options](LLM_OPTIONS_COMPARISON.md)
