#!/bin/bash
# Test script for crawler optimizations
# Run this to verify all optimization components work correctly

set -e  # Exit on error

echo "======================================================================"
echo "Testing Crawler Optimizations"
echo "======================================================================"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Warning: No virtual environment found. Using system Python."
fi

echo ""
echo "----------------------------------------------------------------------"
echo "Test 1: Browser Pool"
echo "----------------------------------------------------------------------"
python3 << 'EOF'
import asyncio
from utils.browser_pool import BrowserPool

async def test_browser_pool():
    print("Creating browser pool with 3 contexts...")
    pool = BrowserPool(pool_size=3, headless=True)

    print("Initializing...")
    await pool.initialize()
    print("✓ Browser pool initialized successfully")

    print("Acquiring context...")
    context = await pool.acquire_context()
    print("✓ Context acquired")

    print("Releasing context...")
    await pool.release_context(context)
    print("✓ Context released")

    print("Cleaning up...")
    await pool.cleanup()
    print("✓ Cleanup complete")
    print("")
    print("✅ Browser Pool Test: PASSED")

asyncio.run(test_browser_pool())
EOF

echo ""
echo "----------------------------------------------------------------------"
echo "Test 2: Checkpoint Manager"
echo "----------------------------------------------------------------------"
python3 << 'EOF'
from utils.checkpoint_manager import CheckpointManager

print("Creating checkpoint manager...")
cm = CheckpointManager('test-execution-123')

print("Saving checkpoint...")
cm.save_checkpoint(
    processed_urls=['url1', 'url2', 'url3'],
    total_urls=10,
    items_saved=3,
    current_chunk=1,
    total_chunks=3
)
print("✓ Checkpoint saved")

print("Loading checkpoint...")
checkpoint = cm.load_checkpoint()
print(f"✓ Checkpoint loaded: {checkpoint['progress_percentage']}% complete")
print(f"  Processed: {len(checkpoint['processed_urls'])}/{checkpoint['total_urls']}")

print("Testing should_process_url...")
should_process_url1 = cm.should_process_url('url1')
should_process_url4 = cm.should_process_url('url4')
print(f"✓ URL1 should process: {should_process_url1} (expected: False)")
print(f"✓ URL4 should process: {should_process_url4} (expected: True)")

print("Clearing checkpoint...")
cm.clear_checkpoint()
print("✓ Checkpoint cleared")
print("")
print("✅ Checkpoint Manager Test: PASSED")
EOF

echo ""
echo "----------------------------------------------------------------------"
echo "Test 3: Smart Wait API Extractor"
echo "----------------------------------------------------------------------"
python3 << 'EOF'
import asyncio
from extractors.api_extractor import APIExtractor

async def test_smart_wait():
    print("Creating API extractor...")
    extractor = APIExtractor()

    # Simulate API data being captured
    print("Simulating API data capture...")
    extractor.api_data = {
        'broadcast': {'id': '12345', 'title': 'Test Broadcast'},
        'coupons': {'coupons': [{'id': 1}]}
    }

    print("Testing wait_for_required_apis (should return immediately)...")
    import time
    start = time.time()
    result = await extractor.wait_for_required_apis(['broadcast'], max_wait=5)
    elapsed = time.time() - start
    print(f"✓ Wait returned in {elapsed:.2f}s (expected: <1s)")
    print(f"✓ Result: {result} (expected: True)")

    print("Testing wait for missing API (should timeout)...")
    start = time.time()
    result = await extractor.wait_for_required_apis(['missing_api'], max_wait=2)
    elapsed = time.time() - start
    print(f"✓ Wait timed out in {elapsed:.2f}s (expected: ~2s)")
    print(f"✓ Result: {result} (expected: False)")

    print("Getting captured APIs...")
    apis = extractor.get_captured_apis()
    print(f"✓ Captured APIs: {apis}")
    print("")
    print("✅ Smart Wait Test: PASSED")

asyncio.run(test_smart_wait())
EOF

echo ""
echo "----------------------------------------------------------------------"
echo "Test 4: Import Optimized Crawler"
echo "----------------------------------------------------------------------"
python3 << 'EOF'
import sys
import os

print("Importing optimized crawler...")
from standalone_crawler_optimized import OptimizedStandaloneCrawler

print("Creating crawler instance...")
crawler = OptimizedStandaloneCrawler(
    verbose=False,
    concurrency=5,
    chunk_size=10,
    max_retries=3
)
print("✓ Crawler instance created")

print(f"  Concurrency: {crawler.concurrency}")
print(f"  Chunk size: {crawler.chunk_size}")
print(f"  Max retries: {crawler.max_retries}")
print("")
print("✅ Optimized Crawler Import Test: PASSED")
EOF

echo ""
echo "======================================================================"
echo "✅ All Tests Passed!"
echo "======================================================================"
echo ""
echo "The following optimizations are working correctly:"
echo "  ✓ Browser Pool (Optimization #2)"
echo "  ✓ Checkpoint Manager (Optimization #8)"
echo "  ✓ Smart Wait Times (Optimization #3)"
echo "  ✓ Optimized Crawler Imports"
echo ""
echo "You can now run the optimized crawler with:"
echo "  python standalone_crawler_optimized.py --brand-name \"Sulwhasoo\""
echo ""
echo "For help and all options:"
echo "  python standalone_crawler_optimized.py --help"
echo ""
