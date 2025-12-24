#!/usr/bin/env python3
"""
Test script for persistence layer (without requiring Supabase connection)

This tests the transformer and validator components.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from persistence.transformer import DataTransformer
from persistence.validator import SchemaValidator


def test_transformer_and_validator():
    """Test data transformation and validation"""

    print("="*60)
    print("Testing Persistence Layer Components")
    print("="*60)

    # Load sample data
    sample_file = Path(__file__).parent.parent / 'output' / 'broadcast_1810235.json'

    if not sample_file.exists():
        print(f"\n✗ Sample file not found: {sample_file}")
        print("Please run the crawler first to generate sample data.")
        return False

    print(f"\n1. Loading sample data from {sample_file.name}...")

    with open(sample_file, 'r', encoding='utf-8') as f:
        crawler_data = json.load(f)

    broadcast_id = crawler_data['broadcast']['broadcast_id']
    title = crawler_data['broadcast']['title']

    print(f"   ✓ Loaded broadcast {broadcast_id}")
    print(f"     Title: {title}")

    # Test transformer
    print("\n2. Testing DataTransformer...")

    try:
        transformed = DataTransformer.transform_all(crawler_data)

        print(f"   ✓ Transformation successful")
        print(f"     - Broadcast: {transformed['broadcast']['id']}")
        print(f"     - Products: {len(transformed['products'])} items")
        print(f"     - Coupons: {len(transformed['coupons'])} items")
        print(f"     - Benefits: {len(transformed['benefits'])} items")
        print(f"     - Chat: {len(transformed['chat'])} messages")
        print(f"     - Metadata: extraction_method={transformed['metadata'].get('extraction_method')}")

    except Exception as e:
        print(f"   ✗ Transformation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test validator
    print("\n3. Testing SchemaValidator...")

    try:
        valid, errors = SchemaValidator.validate_all(transformed)

        if valid:
            print(f"   ✓ Validation successful - all data is valid")
        else:
            print(f"   ⚠ Validation found issues:")
            for key, error_list in errors.items():
                print(f"     - {key}:")
                for error in error_list:
                    print(f"       * {error}")

    except Exception as e:
        print(f"   ✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test individual transformers
    print("\n4. Testing individual transformers...")

    # Test broadcast transform
    broadcast_data = DataTransformer.transform_broadcast(crawler_data)
    valid, errors = SchemaValidator.validate_broadcast(broadcast_data)

    if valid:
        print(f"   ✓ Broadcast data valid")
    else:
        print(f"   ✗ Broadcast validation errors: {errors}")

    # Test products transform
    products = crawler_data['broadcast'].get('products', [])
    if products:
        product_data = DataTransformer.transform_products(broadcast_id, products)
        valid, errors = SchemaValidator.validate_product(product_data[0])

        if valid:
            print(f"   ✓ Product data valid")
        else:
            print(f"   ⚠ Product validation errors: {errors}")

    # Test metadata transform
    metadata = DataTransformer.transform_metadata(crawler_data)
    valid, errors = SchemaValidator.validate_metadata(metadata)

    if valid:
        print(f"   ✓ Metadata valid")
    else:
        print(f"   ✗ Metadata validation errors: {errors}")

    print("\n" + "="*60)
    print("✓ All component tests passed!")
    print("="*60)

    print("\nNext steps:")
    print("1. Set up Supabase and create database tables")
    print("2. Configure .env file with Supabase credentials")
    print("3. Run: python scripts/save_broadcast.py --test-connection")
    print("4. Run: python scripts/save_broadcast.py --json output/broadcast_1810235.json")

    return True


if __name__ == '__main__':
    try:
        success = test_transformer_and_validator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
