#!/usr/bin/env python3
"""
Test script for the Hive Check-in Bot.
This script helps test individual components of the bot.
"""

import os
from dotenv import load_dotenv
from main import HiveCheckinBot

def test_configuration():
    """Test bot configuration loading."""
    print("Testing configuration...")
    try:
        bot = HiveCheckinBot()
        print("✓ Configuration loaded successfully")
        print(f"  - Community: {bot.config.get('community', 'Not set')}")
        print(f"  - Required tags: {bot.config.get('required_metadata', {}).get('tags', [])}")
        print(f"  - Required developer: {bot.config.get('required_metadata', {}).get('developer', 'Not set')}")
        print(f"  - Check interval: {bot.config.get('check_interval', 'Not set')} seconds")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False

def test_environment_variables():
    """Test environment variables."""
    print("\nTesting environment variables...")
    load_dotenv()
    
    required_vars = [
        'HIVE_ACCOUNT_NAME',
        'HIVE_POSTING_KEY', 
        'HIVE_ACTIVE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("  Please create a .env file with your Hive credentials")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

def test_hive_connection():
    """Test Hive blockchain connection."""
    print("\nTesting Hive connection...")
    try:
        bot = HiveCheckinBot()
        bot.connect_to_hive()
        print("✓ Successfully connected to Hive blockchain")
        print(f"  - Account: {bot.account_name}")
        print(f"  - Node: {bot.hive_node}")
        return True
    except Exception as e:
        print(f"✗ Hive connection failed: {e}")
        return False

def test_metadata_checking():
    """Test metadata checking logic."""
    print("\nTesting metadata checking...")
    try:
        bot = HiveCheckinBot()
        
        # Test post with matching metadata for hive-115276
        test_post = {
            'title': 'Mi introducción a la comunidad Check-in Ecuador',
            'tags': ['introduceyourself', 'checkinecuador'],
            'author': 'testuser',
            'permlink': 'mi-introduccion-ecuador',
            'json_metadata': {
                'developer': 'meno',
                'tags': ['introduceyourself', 'checkinecuador']
            }
        }
        
        result = bot.check_post_metadata(test_post)
        if result:
            print("✓ Metadata checking works correctly")
            return True
        else:
            print("✗ Metadata checking may need adjustment")
            return False
    except Exception as e:
        print(f"✗ Metadata checking failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Hive Check-in Bot Test Suite")
    print("=" * 40)
    
    tests = [
        test_configuration,
        test_environment_variables,
        test_metadata_checking,
        # test_hive_connection,  # Commented out as it requires valid credentials
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Your bot is ready to run.")
    else:
        print("✗ Some tests failed. Please check the configuration.")
    
    print("\nNext steps:")
    print("1. Create a .env file with your Hive credentials")
    print("2. Update config.json with your community settings")
    print("3. Run the bot with: python main.py")

if __name__ == "__main__":
    main()
