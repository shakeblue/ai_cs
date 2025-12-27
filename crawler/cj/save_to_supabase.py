#!/usr/bin/env python3
"""
Supabase saver for Naver Event data
Saves event information extracted from images to Supabase database
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
import urllib3
import ssl

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Disable SSL verification globally (for development)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Add parent directory to path to import supabase_client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from supabase_client import get_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    try:
        # Try relative import
        import sys
        sys.path.append('..')
        from supabase_client import get_supabase_client
        SUPABASE_AVAILABLE = True
    except ImportError:
        SUPABASE_AVAILABLE = False
        print("⚠️ Warning: supabase_client not available")


class SupabaseSaver:
    """Save Naver event data to Supabase"""

    def __init__(self):
        """Initialize Supabase saver"""
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase client is not available. Please check your setup.")

        self.supabase = get_supabase_client()
        self.table_name = 'naver_smartstore_event'

    def save_event(self, event_data: Dict[str, Any],
                   image_urls: List[str] = None,
                   raw_ocr_data: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Save event data to Supabase with upsert logic

        Checks if event with same URL already exists:
        - If exists: Updates the existing record
        - If new: Creates a new record

        Args:
            event_data: Event information dictionary with keys:
                - platform_name: Platform name (e.g., 'Naver Brand')
                - brand_name: Brand name
                - url: Event URL
                - event_title: Event title
                - event_date: Event date period
                - benefits_by_purchase_amount: List of purchase amount benefits
                - coupon_benefits: List of coupon benefits
            image_urls: List of image URLs
            raw_ocr_data: Raw OCR text data (dict of filename -> text)

        Returns:
            Dictionary with success status and saved data
        """
        try:
            url = event_data.get('url', '')

            if not url:
                return {
                    'success': False,
                    'data': None,
                    'error': 'URL is required for save/update operations'
                }

            # Prepare data for insertion/update
            data = {
                'platform_name': event_data.get('platform_name', 'Naver Brand'),
                'brand_name': event_data.get('brand_name', ''),
                'url': url,
                'event_title': event_data.get('event_title', ''),
                'event_date': event_data.get('event_date', ''),
                'benefits_by_purchase_amount': event_data.get('benefits_by_purchase_amount', []),
                'coupon_benefits': event_data.get('coupon_benefits', []),
                'image_urls': image_urls or [],
                'raw_ocr_data': raw_ocr_data or {},
                'updated_at': datetime.now().isoformat()
            }

            print(f"💾 Saving event data to Supabase table: {self.table_name}")
            print(f"   Brand: {data['brand_name']}")
            print(f"   Event: {data['event_title']}")
            print(f"   URL: {url}")

            # Check if event already exists
            existing_event = self.get_event_by_url(url)

            if existing_event:
                # Update existing record
                event_id = existing_event['id']
                print(f"   📝 Event exists (ID: {event_id}), updating...")

                response = self.supabase.table(self.table_name)\
                    .update(data)\
                    .eq('id', event_id)\
                    .execute()

                if response.data:
                    print(f"✅ Event data updated successfully!")
                    print(f"   Record ID: {event_id}")

                    return {
                        'success': True,
                        'data': response.data[0],
                        'record_id': event_id,
                        'action': 'updated',
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'data': None,
                        'error': 'No data returned from update'
                    }
            else:
                # Insert new record
                print(f"   ➕ New event, creating...")
                data['created_at'] = datetime.now().isoformat()

                response = self.supabase.table(self.table_name).insert(data).execute()

                if response.data:
                    new_id = response.data[0].get('id')
                    print(f"✅ Event data created successfully!")
                    print(f"   Record ID: {new_id}")

                    return {
                        'success': True,
                        'data': response.data[0],
                        'record_id': new_id,
                        'action': 'created',
                        'error': None
                    }
                else:
                    return {
                        'success': False,
                        'data': None,
                        'error': 'No data returned from insert'
                    }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Failed to save event data to Supabase: {error_msg}")

            # Check if it's a table not found error
            if 'relation' in error_msg and 'does not exist' in error_msg:
                print(f"\n⚠️ Table '{self.table_name}' does not exist!")
                print(f"   Please create the table using the SQL script in CREATE_SUPABASE_TABLE.md")
                print(f"   Location: /home/long/ai_cs/CREATE_SUPABASE_TABLE.md")

            return {
                'success': False,
                'data': None,
                'error': error_msg
            }

    def get_event_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve event data by URL

        Args:
            url: Event URL

        Returns:
            Event data dictionary or None if not found
        """
        try:
            response = self.supabase.table(self.table_name).select('*').eq('url', url).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]

            return None

        except Exception as e:
            print(f"❌ Failed to retrieve event data: {e}")
            return None

    def update_event(self, event_id: int, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing event data

        Args:
            event_id: Event record ID
            event_data: Updated event data

        Returns:
            Dictionary with success status and updated data
        """
        try:
            # Add updated_at timestamp
            update_data = {**event_data, 'updated_at': datetime.now().isoformat()}

            response = self.supabase.table(self.table_name).update(update_data).eq('id', event_id).execute()

            if response.data:
                print(f"✅ Event data updated successfully! (ID: {event_id})")

                return {
                    'success': True,
                    'data': response.data[0],
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'error': 'No data returned from update'
                }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Failed to update event data: {error_msg}")

            return {
                'success': False,
                'data': None,
                'error': error_msg
            }

    def delete_event(self, event_id: int) -> Dict[str, Any]:
        """
        Delete event data

        Args:
            event_id: Event record ID

        Returns:
            Dictionary with success status
        """
        try:
            response = self.supabase.table(self.table_name).delete().eq('id', event_id).execute()

            print(f"✅ Event data deleted successfully! (ID: {event_id})")

            return {
                'success': True,
                'data': response.data,
                'error': None
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Failed to delete event data: {error_msg}")

            return {
                'success': False,
                'data': None,
                'error': error_msg
            }

    def list_events(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List event data with pagination

        Args:
            limit: Number of records to return
            offset: Number of records to skip

        Returns:
            List of event data dictionaries
        """
        try:
            response = self.supabase.table(self.table_name)\
                .select('*')\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return response.data or []

        except Exception as e:
            print(f"❌ Failed to list events: {e}")
            return []


# Test function
if __name__ == '__main__':
    """Test Supabase connection and table access"""
    print("Testing Supabase connection...\n")

    try:
        saver = SupabaseSaver()
        print("✅ Supabase saver initialized successfully!")

        # Test listing events
        print("\nTesting list_events()...")
        events = saver.list_events(limit=5)
        print(f"✅ Found {len(events)} events in database")

        if events:
            print("\nLatest event:")
            latest = events[0]
            print(f"  ID: {latest.get('id')}")
            print(f"  Brand: {latest.get('brand_name')}")
            print(f"  Event: {latest.get('event_title')}")
            print(f"  Date: {latest.get('event_date')}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
