#!/usr/bin/env python3
"""
CLI script to save multiple broadcasts to Supabase in batch

Usage:
    python scripts/bulk_save.py --input-dir output/
    python scripts/bulk_save.py --input-dir output/ --pattern "broadcast_*.json"
    python scripts/bulk_save.py --files output/broadcast_1.json output/broadcast_2.json
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

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


def display_results(result: dict):
    """Display batch save results"""
    print("\n" + "="*60)
    print(f"BATCH SAVE RESULTS")
    print("="*60)

    print(f"\nTotal broadcasts: {result['total']}")
    print(f"✓ Successful: {result['successful']}")
    print(f"✗ Failed: {result['failed']}")

    if result['successful'] > 0:
        success_rate = (result['successful'] / result['total']) * 100
        print(f"\nSuccess rate: {success_rate:.1f}%")

    # Show details of each save
    if result.get('results'):
        print("\nDetails:")
        for i, res in enumerate(result['results'], 1):
            if res['status'] == 'success':
                print(f"  {i}. ✓ Broadcast {res['broadcast_id']}: "
                      f"{res['records_saved']['products']} products, "
                      f"{res['records_saved']['coupons']} coupons "
                      f"({res['duration_seconds']}s)")
            else:
                broadcast_id = res.get('broadcast_id', 'unknown')
                error = res.get('error', 'Unknown error')
                print(f"  {i}. ✗ Broadcast {broadcast_id}: {error}")

    print("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch save Naver Shopping Live broadcasts to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save all broadcasts from directory
  python scripts/bulk_save.py --input-dir output/

  # Save with custom pattern
  python scripts/bulk_save.py --input-dir output/ --pattern "broadcast_*.json"

  # Save specific files
  python scripts/bulk_save.py --files output/broadcast_1.json output/broadcast_2.json

  # Save with verbose output
  python scripts/bulk_save.py --input-dir output/ --verbose
        """
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        help='Directory containing broadcast JSON files'
    )

    parser.add_argument(
        '--pattern',
        type=str,
        default='broadcast_*.json',
        help='Glob pattern for matching files (default: broadcast_*.json)'
    )

    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific JSON files to save'
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
        # Validate arguments
        if not args.input_dir and not args.files:
            parser.print_help()
            print("\nError: Either --input-dir or --files argument is required")
            return 1

        # Initialize saver
        print("Initializing Broadcast Saver...")
        saver = BroadcastSaver()

        # Test connection
        print("Testing database connection...")
        if not saver.test_connection():
            print("✗ Database connection failed!")
            return 1
        print("✓ Database connection successful")

        # Save broadcasts
        if args.input_dir:
            # Save from directory
            input_dir = Path(args.input_dir)

            if not input_dir.exists():
                print(f"✗ Error: Directory not found: {input_dir}")
                return 1

            print(f"\nSearching for files in {input_dir} matching '{args.pattern}'...")
            result = saver.save_from_directory(input_dir, args.pattern)

        else:
            # Save specific files
            files: List[Path] = [Path(f) for f in args.files]

            # Check all files exist
            missing_files = [f for f in files if not f.exists()]
            if missing_files:
                print(f"✗ Error: Files not found:")
                for f in missing_files:
                    print(f"  - {f}")
                return 1

            print(f"\nSaving {len(files)} broadcasts...")
            result = saver.save_multiple(files)

        # Display results
        display_results(result)

        # Return exit code based on success rate
        if result['failed'] == 0:
            return 0
        elif result['successful'] > 0:
            return 2  # Partial success
        else:
            return 1  # Complete failure

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
