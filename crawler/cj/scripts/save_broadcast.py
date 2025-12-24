#!/usr/bin/env python3
"""
CLI script to save a single broadcast to Supabase

Usage:
    python scripts/save_broadcast.py --json output/broadcast_1776510.json
    python scripts/save_broadcast.py --json output/broadcast_1776510.json --verbose
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from persistence import BroadcastSaver


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Save Naver Shopping Live broadcast data to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save a single broadcast
  python scripts/save_broadcast.py --json output/broadcast_1776510.json

  # Save with verbose output
  python scripts/save_broadcast.py --json output/broadcast_1776510.json --verbose

  # Test database connection
  python scripts/save_broadcast.py --test-connection
        """
    )

    parser.add_argument(
        '--json',
        type=str,
        help='Path to broadcast JSON file'
    )

    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test database connection and exit'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        # Initialize saver
        print("Initializing Broadcast Saver...")
        saver = BroadcastSaver()

        # Test connection if requested
        if args.test_connection:
            print("Testing database connection...")
            if saver.test_connection():
                print("✓ Database connection successful!")
                return 0
            else:
                print("✗ Database connection failed!")
                return 1

        # Validate arguments
        if not args.json:
            parser.print_help()
            print("\nError: --json argument is required")
            return 1

        json_path = Path(args.json)

        if not json_path.exists():
            print(f"✗ Error: File not found: {json_path}")
            return 1

        # Save broadcast
        print(f"\nSaving broadcast from {json_path}...")
        result = saver.save_from_json_file(json_path)

        # Display results
        print("\n" + "="*60)

        if result['status'] == 'success':
            print(f"✓ SUCCESS: Broadcast {result['broadcast_id']} saved!")
            print(f"\nRecords saved:")
            print(f"  - Products: {result['records_saved']['products']}")
            print(f"  - Coupons: {result['records_saved']['coupons']}")
            print(f"  - Benefits: {result['records_saved']['benefits']}")
            print(f"  - Chat messages: {result['records_saved']['chat']}")
            print(f"\nDuration: {result['duration_seconds']}s")
            print("="*60 + "\n")
            return 0
        else:
            print(f"✗ FAILED: {result.get('error', 'Unknown error')}")

            if 'validation_errors' in result:
                print("\nValidation errors:")
                for key, errors in result['validation_errors'].items():
                    print(f"  {key}:")
                    for error in errors:
                        print(f"    - {error}")

            print("="*60 + "\n")
            return 1

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
