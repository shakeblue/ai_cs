#!/usr/bin/env python3
"""
Wrapper script for running Naver Event Pipeline with configurable LLM extractors
Provides easy command-line interface for all extraction strategies
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from naver_event_pipeline_integrated import NaverEventPipelineIntegrated
from extraction_strategy import ExtractionStrategy, StrategyConfig
from llm_extractor import LLMProvider


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run Naver Event Pipeline with configurable extraction strategies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using GPT-4o Mini (recommended - best value):
  python run_pipeline.py "https://brand.naver.com/iope/..." --strategy llm-gpt4o-mini

  # Using Claude Haiku (highest accuracy):
  python run_pipeline.py "https://brand.naver.com/iope/..." --strategy llm-claude-haiku

  # Using Gemini Flash (fastest LLM):
  python run_pipeline.py "https://brand.naver.com/iope/..." --strategy llm-gemini-flash

  # Using hybrid approach (best value with fallback):
  python run_pipeline.py "https://brand.naver.com/iope/..." --strategy hybrid-semantic-llm-pattern --llm gpt

  # Using pattern-based (free, no API key needed):
  python run_pipeline.py "https://brand.naver.com/iope/..." --strategy pattern

  # Compare all strategies:
  python run_pipeline.py --compare

Available Extraction Strategies:
  - pattern                       : Regex-based (free, 60-70% accuracy)
  - semantic                      : NLP-based (free, 75-85% accuracy)
  - llm-claude-haiku             : Claude Haiku ($2.00/1000, 85-92% accuracy)
  - llm-gpt4o-mini               : GPT-4o Mini ($0.40/1000, 85-90% accuracy)
  - llm-gemini-flash             : Gemini Flash ($0.20/1000, 80-88% accuracy)
  - hybrid-semantic-pattern      : Semantic → Pattern (free, 75-85% accuracy)
  - hybrid-llm-pattern           : LLM → Pattern ($0.50/1000, 85-92% accuracy)
  - hybrid-semantic-llm-pattern  : Semantic → LLM → Pattern ($0.10/1000, 85-92% accuracy) ⭐ RECOMMENDED
  - auto                         : Automatic selection ($0.10/1000, 85-92% accuracy)
        """
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='Naver brand event URL to process'
    )

    parser.add_argument(
        '--strategy', '-s',
        choices=[
            'pattern',
            'semantic',
            'llm-claude-haiku',
            'llm-gpt4o-mini',
            'llm-gemini-flash',
            'hybrid-semantic-pattern',
            'hybrid-llm-pattern',
            'hybrid-semantic-llm-pattern',
            'auto'
        ],
        default='hybrid-semantic-llm-pattern',
        help='Extraction strategy to use (default: hybrid-semantic-llm-pattern)'
    )

    parser.add_argument(
        '--llm',
        choices=['claude', 'gpt', 'gemini'],
        default='gpt',
        help='LLM provider for LLM/hybrid strategies (default: gpt)'
    )

    parser.add_argument(
        '--crawler',
        choices=['gentle', 'moderate', 'aggressive'],
        default='moderate',
        help='Crawler strategy (default: moderate)'
    )

    parser.add_argument(
        '--output',
        default='naver_event_images',
        help='Output directory for images (default: naver_event_images)'
    )

    parser.add_argument(
        '--ocr-key',
        help='OCR.space API key (overrides default)'
    )

    parser.add_argument(
        '--compare',
        action='store_true',
        help='Show comparison of all extraction strategies'
    )

    parser.add_argument(
        '--list-strategies',
        action='store_true',
        help='List all available extraction strategies with details'
    )

    return parser.parse_args()


def show_strategy_comparison():
    """Display comparison of all strategies"""
    StrategyConfig.print_comparison()


def map_strategy_to_enum(strategy_str: str) -> ExtractionStrategy:
    """Map strategy string to ExtractionStrategy enum"""
    strategy_map = {
        'pattern': ExtractionStrategy.PATTERN,
        'semantic': ExtractionStrategy.SEMANTIC,
        'llm-claude-haiku': ExtractionStrategy.LLM_CLAUDE_HAIKU,
        'llm-gpt4o-mini': ExtractionStrategy.LLM_GPT4O_MINI,
        'llm-gemini-flash': ExtractionStrategy.LLM_GEMINI_FLASH,
        'hybrid-semantic-pattern': ExtractionStrategy.HYBRID_SEMANTIC_PATTERN,
        'hybrid-llm-pattern': ExtractionStrategy.HYBRID_LLM_PATTERN,
        'hybrid-semantic-llm-pattern': ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN,
        'auto': ExtractionStrategy.AUTO,
    }
    return strategy_map[strategy_str]


def map_llm_to_enum(llm_str: str) -> LLMProvider:
    """Map LLM string to LLMProvider enum"""
    llm_map = {
        'claude': LLMProvider.CLAUDE_HAIKU,
        'gpt': LLMProvider.GPT_4O_MINI,
        'gemini': LLMProvider.GEMINI_FLASH,
    }
    return llm_map[llm_str]


def needs_llm(strategy: ExtractionStrategy) -> bool:
    """Check if strategy requires LLM"""
    llm_strategies = [
        ExtractionStrategy.LLM_CLAUDE_HAIKU,
        ExtractionStrategy.LLM_GPT4O_MINI,
        ExtractionStrategy.LLM_GEMINI_FLASH,
        ExtractionStrategy.HYBRID_LLM_PATTERN,
        ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN,
        ExtractionStrategy.AUTO,
    ]
    return strategy in llm_strategies


async def main():
    """Main execution function"""
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Parse arguments
    args = parse_arguments()

    # Handle special commands
    if args.compare or args.list_strategies:
        show_strategy_comparison()
        return 0

    # Validate URL is provided
    if not args.url:
        print("❌ Error: URL is required")
        print("   Usage: python run_pipeline.py <url> [options]")
        print("   Run with --help for more information")
        return 1

    # Map strategy and LLM
    extraction_strategy = map_strategy_to_enum(args.strategy)
    llm_provider = map_llm_to_enum(args.llm) if needs_llm(extraction_strategy) else None

    # Get OCR API key
    ocr_api_key = args.ocr_key or os.getenv('OCR_SPACE_API_KEY', 'K87899142388957')

    # Display configuration
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║              Naver Event Pipeline - Configuration                ║
╚══════════════════════════════════════════════════════════════════╝

  URL:                 {args.url}
  Extraction Strategy: {args.strategy}
  LLM Provider:        {args.llm if llm_provider else 'N/A (not using LLM)'}
  Crawler Strategy:    {args.crawler}
  Output Directory:    {args.output}
  OCR API:             OCR.space
  Database:            Supabase

Strategy Details:
""")

    strategy_info = StrategyConfig.get_info(extraction_strategy)
    print(f"  Cost per 1000:       {strategy_info['cost_per_1000']}")
    print(f"  Expected Accuracy:   {strategy_info['accuracy']}")
    print(f"  Speed:               {strategy_info['speed']}")
    print()

    # Validate LLM API key if needed
    if llm_provider:
        api_key_map = {
            LLMProvider.CLAUDE_HAIKU: 'ANTHROPIC_API_KEY',
            LLMProvider.GPT_4O_MINI: 'OPENAI_API_KEY',
            LLMProvider.GEMINI_FLASH: 'GOOGLE_API_KEY',
        }
        required_key = api_key_map[llm_provider]

        if not os.getenv(required_key):
            print(f"❌ Error: {required_key} not found in environment")
            print(f"   Please set it in .env file or environment variables")
            print(f"\n   Required packages:")
            if llm_provider == LLMProvider.CLAUDE_HAIKU:
                print(f"   pip install anthropic")
            elif llm_provider == LLMProvider.GPT_4O_MINI:
                print(f"   pip install openai")
            elif llm_provider == LLMProvider.GEMINI_FLASH:
                print(f"   pip install google-generativeai")
            return 1

    # Create and run pipeline
    try:
        pipeline = NaverEventPipelineIntegrated(
            ocr_api_key=ocr_api_key,
            crawler_strategy=args.crawler,
            extraction_strategy=extraction_strategy,
            llm_provider=llm_provider
        )

        result = await pipeline.process_event_url(args.url, args.output)

        if result['success']:
            print("\n🎉 All steps completed successfully!")
            return 0
        else:
            print(f"\n💥 Pipeline failed at step: {result.get('step', 'unknown')}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run pipeline
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
