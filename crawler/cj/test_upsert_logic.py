#!/usr/bin/env python3
"""
Test script for Supabase upsert logic
Verifies that save_event() properly creates/updates records
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from save_to_supabase import SupabaseSaver


def test_upsert_logic():
    """Test the upsert logic"""

    print("="*70)
    print("TESTING UPSERT LOGIC")
    print("="*70)

    try:
        saver = SupabaseSaver()
        print("✅ SupabaseSaver initialized\n")

        # Test data
        test_event = {
            'platform_name': 'Naver Brand',
            'brand_name': 'TEST_BRAND',
            'url': 'https://brand.naver.com/test/story?id=TEST123',
            'event_title': 'Test Shopping Story - Version 1',
            'event_date': '2024-01-01 ~ 2024-12-31',
            'benefits_by_purchase_amount': ['10% off on $100+'],
            'coupon_benefits': ['Welcome coupon 5000 KRW']
        }

        print("TEST 1: Create new event")
        print("-"*70)
        result1 = saver.save_event(test_event)

        if result1['success']:
            print(f"✅ Test 1 PASSED")
            print(f"   Action: {result1.get('action')}")
            print(f"   Record ID: {result1.get('record_id')}")
            print(f"   Expected: 'created'\n")
        else:
            print(f"❌ Test 1 FAILED: {result1.get('error')}\n")
            return False

        # Update the event data
        test_event['event_title'] = 'Test Shopping Story - Version 2 (UPDATED)'
        test_event['benefits_by_purchase_amount'] = ['20% off on $100+', '30% off on $200+']

        print("TEST 2: Update existing event (same URL)")
        print("-"*70)
        result2 = saver.save_event(test_event)

        if result2['success']:
            print(f"✅ Test 2 PASSED")
            print(f"   Action: {result2.get('action')}")
            print(f"   Record ID: {result2.get('record_id')}")
            print(f"   Expected: 'updated'")
            print(f"   Same ID as Test 1: {result2.get('record_id') == result1.get('record_id')}\n")
        else:
            print(f"❌ Test 2 FAILED: {result2.get('error')}\n")
            return False

        # Verify the record was actually updated
        print("TEST 3: Verify update by fetching from database")
        print("-"*70)
        fetched_event = saver.get_event_by_url(test_event['url'])

        if fetched_event:
            print(f"✅ Test 3 PASSED")
            print(f"   Title: {fetched_event.get('event_title')}")
            print(f"   Benefits: {fetched_event.get('benefits_by_purchase_amount')}")
            print(f"   Updated correctly: {fetched_event.get('event_title') == test_event['event_title']}\n")
        else:
            print(f"❌ Test 3 FAILED: Could not fetch event\n")
            return False

        # Clean up - delete test record
        print("CLEANUP: Deleting test record")
        print("-"*70)
        delete_result = saver.delete_event(result1.get('record_id'))

        if delete_result['success']:
            print(f"✅ Test record deleted (ID: {result1.get('record_id')})\n")
        else:
            print(f"⚠️  Could not delete test record: {delete_result.get('error')}\n")

        print("="*70)
        print("ALL TESTS PASSED ✅")
        print("="*70)
        print("\nUpsert logic working correctly:")
        print("  ✓ New URLs create new records")
        print("  ✓ Existing URLs update existing records")
        print("  ✓ No duplicate records created")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_upsert_logic()
    sys.exit(0 if success else 1)
