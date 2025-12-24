"""
Extraction Strategy Configuration
Defines available strategies for event information extraction
"""

from enum import Enum


class ExtractionStrategy(Enum):
    """Available extraction strategies"""

    # Strategy 1: Pattern-based (regex)
    PATTERN = "pattern"

    # Strategy 2: Semantic/NLP
    SEMANTIC = "semantic"

    # Strategy 3: LLM-based
    LLM_CLAUDE_HAIKU = "llm-claude-haiku"
    LLM_GPT4O_MINI = "llm-gpt4o-mini"
    LLM_GEMINI_FLASH = "llm-gemini-flash"

    # Hybrid strategies (fallback chain)
    HYBRID_SEMANTIC_PATTERN = "hybrid-semantic-pattern"  # Semantic → Pattern
    HYBRID_LLM_PATTERN = "hybrid-llm-pattern"  # LLM → Pattern
    HYBRID_SEMANTIC_LLM_PATTERN = "hybrid-semantic-llm-pattern"  # Semantic → LLM → Pattern

    # Auto (best available)
    AUTO = "auto"


class StrategyConfig:
    """Configuration for extraction strategies"""

    # Cost estimates (per 1000 events)
    COSTS = {
        ExtractionStrategy.PATTERN: 0.0,
        ExtractionStrategy.SEMANTIC: 0.0,
        ExtractionStrategy.LLM_CLAUDE_HAIKU: 2.0,
        ExtractionStrategy.LLM_GPT4O_MINI: 0.4,
        ExtractionStrategy.LLM_GEMINI_FLASH: 0.2,
        ExtractionStrategy.HYBRID_SEMANTIC_PATTERN: 0.0,
        ExtractionStrategy.HYBRID_LLM_PATTERN: 0.5,  # ~25% LLM usage
        ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN: 0.1,  # ~5% LLM usage
        ExtractionStrategy.AUTO: 0.1,
    }

    # Expected accuracy
    ACCURACY = {
        ExtractionStrategy.PATTERN: "60-70%",
        ExtractionStrategy.SEMANTIC: "75-85%",
        ExtractionStrategy.LLM_CLAUDE_HAIKU: "85-92%",
        ExtractionStrategy.LLM_GPT4O_MINI: "85-90%",
        ExtractionStrategy.LLM_GEMINI_FLASH: "80-88%",
        ExtractionStrategy.HYBRID_SEMANTIC_PATTERN: "75-85%",
        ExtractionStrategy.HYBRID_LLM_PATTERN: "85-92%",
        ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN: "85-92%",
        ExtractionStrategy.AUTO: "85-92%",
    }

    # Speed (relative)
    SPEED = {
        ExtractionStrategy.PATTERN: "Very Fast",
        ExtractionStrategy.SEMANTIC: "Fast",
        ExtractionStrategy.LLM_CLAUDE_HAIKU: "Medium",
        ExtractionStrategy.LLM_GPT4O_MINI: "Medium",
        ExtractionStrategy.LLM_GEMINI_FLASH: "Fast",
        ExtractionStrategy.HYBRID_SEMANTIC_PATTERN: "Fast",
        ExtractionStrategy.HYBRID_LLM_PATTERN: "Medium",
        ExtractionStrategy.HYBRID_SEMANTIC_LLM_PATTERN: "Medium",
        ExtractionStrategy.AUTO: "Medium",
    }

    @classmethod
    def get_info(cls, strategy: ExtractionStrategy) -> dict:
        """Get information about a strategy"""
        return {
            "strategy": strategy.value,
            "cost_per_1000": f"${cls.COSTS[strategy]:.2f}",
            "accuracy": cls.ACCURACY[strategy],
            "speed": cls.SPEED[strategy],
        }

    @classmethod
    def print_comparison(cls):
        """Print comparison of all strategies"""
        print("\n" + "=" * 80)
        print("Extraction Strategy Comparison")
        print("=" * 80)
        print(f"{'Strategy':<35} {'Cost/1000':<12} {'Accuracy':<12} {'Speed':<12}")
        print("-" * 80)

        for strategy in ExtractionStrategy:
            if strategy == ExtractionStrategy.AUTO:
                continue
            info = cls.get_info(strategy)
            print(f"{info['strategy']:<35} {info['cost_per_1000']:<12} "
                  f"{info['accuracy']:<12} {info['speed']:<12}")

        print("=" * 80)
        print("\nRecommended Strategies:")
        print("  - Best Value: hybrid-semantic-llm-pattern (high accuracy, low cost)")
        print("  - Best Accuracy: llm-claude-haiku or llm-gpt4o-mini")
        print("  - Best Speed: pattern or semantic")
        print("  - Zero Cost: pattern or semantic")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    StrategyConfig.print_comparison()
