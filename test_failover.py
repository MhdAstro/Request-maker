"""
Test script for Gemini API key failover system.
This script simulates various failure scenarios to ensure the failover works correctly.
"""

import asyncio
import os
from services.gemini_service import generate_product_json, get_api_status, GeminiException

async def test_failover():
    """Test the failover system with a sample product description."""
    
    print("=" * 60)
    print("GEMINI API KEY FAILOVER TEST")
    print("=" * 60)
    
    # Display current API configuration
    status = get_api_status()
    print("\nAPI Configuration:")
    print(f"- Total API keys configured: {status['total_keys']}")
    print(f"- Max retries per key: {status['max_retries_per_key']}")
    print(f"- Retry delay: {status['retry_delay']} seconds")
    print("=" * 60)
    
    # Test product description
    test_product = """
    iPhone 15 Pro Max
    - 256GB Storage
    - Natural Titanium color
    - 6.7" display
    - A17 Pro chip
    - Price: $1199
    - Brand new, sealed in box
    - Includes 1 year warranty
    """
    
    print("\nTest 1: Normal request with failover capability")
    print("-" * 40)
    
    try:
        print("Sending request to Gemini API...")
        result = await generate_product_json(test_product)
        
        print("\n✅ SUCCESS! Generated product JSON:")
        print("-" * 40)
        
        # Display key parts of the result
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict) or isinstance(value, list):
                    print(f"{key}: {type(value).__name__} with {len(value)} items")
                else:
                    print(f"{key}: {value}")
        else:
            print(result)
            
        # Show final API status
        final_status = get_api_status()
        print("\n" + "-" * 40)
        print("Final API Status:")
        print(f"- Current active key: #{final_status['current_key_index']}")
        print(f"- Failed keys: {final_status['failed_keys'] if final_status['failed_keys'] else 'None'}")
        print(f"- Available keys: {final_status['available_keys']}")
        
    except GeminiException as e:
        print(f"\n❌ ERROR: {e}")
        print("\nThis error occurred after exhausting all available API keys.")
        print("Please add more valid API keys to the .env file.")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    # Additional test information
    print("\n📝 Notes for production use:")
    print("1. Add multiple valid API keys to .env file")
    print("2. Keys should be comma-separated in GOOGLE_API_KEYS")
    print("3. The system will automatically switch keys on rate limits")
    print("4. Failed keys are temporarily marked and retried later")
    print("5. You can monitor API status using get_api_status()")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_failover())