#!/usr/bin/env python3
"""
Advanced test script for the Hive Ecuador Check-in Bot.
This script tests all components of the advanced bot including database operations.
"""

import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from main import HiveEcuadorBot, DatabaseManager, PostValidation

def test_configuration():
    """Test bot configuration loading."""
    print("Testing configuration...")
    try:
        bot = HiveEcuadorBot()
        config = bot.config
        
        print("✓ Configuration loaded successfully")
        print(f"  - Community: {config.get('community')}")
        print(f"  - Required app: {config.get('required_metadata', {}).get('app')}")
        print(f"  - Required developer: {config.get('required_metadata', {}).get('developer')}")
        print(f"  - Required tags: {config.get('required_metadata', {}).get('tags', [])}")
        print(f"  - Transfer amount: {config.get('transfer_amount')} HBD")
        print(f"  - Upvote percentage: {config.get('upvote_percentage')}%")
        print(f"  - Max daily transfers: {config.get('max_daily_transfers')}")
        print(f"  - Dry run mode: {config.get('dry_run')}")
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
        if not os.getenv(var) or os.getenv(var) == f"your-{var.lower().replace('_', '-')}":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing or placeholder environment variables: {', '.join(missing_vars)}")
        print("  Please update your .env file with actual credentials")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

def test_database_operations():
    """Test database operations."""
    print("\nTesting database operations...")
    try:
        # Use a test database
        db = DatabaseManager("test_processed_posts.db")
        
        # Test basic operations
        test_author = "testuser"
        test_permlink = "test-post"
        
        # Test is_post_processed (should be False initially)
        if db.is_post_processed(test_author, test_permlink):
            print("✗ Database test failed: post should not be processed initially")
            return False
        
        # Test record_processed_post
        db.record_processed_post(test_author, test_permlink, 1.0, True, True)
        
        # Test is_post_processed (should be True now)
        if not db.is_post_processed(test_author, test_permlink):
            print("✗ Database test failed: post should be processed after recording")
            return False
        
        # Test daily stats
        db.update_daily_stats(posts_processed=1, hbd_sent=1.0, upvotes_given=1)
        stats = db.get_daily_stats()
        
        if not stats or stats.posts_processed < 1:
            print("✗ Database test failed: daily stats not working")
            return False
        
        # Test daily transfer limits
        if not db.can_send_transfer_today(10):
            print("✗ Database test failed: daily transfer limit check failed")
            return False
        
        print("✓ Database operations work correctly")
        print(f"  - Posts processed today: {stats.posts_processed}")
        print(f"  - HBD sent today: {stats.hbd_sent}")
        print(f"  - Upvotes given today: {stats.upvotes_given}")
        
        # Clean up test database
        os.remove("test_processed_posts.db")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations failed: {e}")
        return False

def test_post_validation():
    """Test post validation logic."""
    print("\nTesting post validation...")
    try:
        bot = HiveEcuadorBot()
        
        # Test valid post
        valid_post = {
            'author': 'testuser',
            'permlink': 'mi-introduccion-ecuador',
            'title': 'Mi introducción a Hive Ecuador',
            'body': 'Hola a todos! Soy nuevo en Hive Ecuador y quiero presentarme. ' * 10,  # Make it long enough
            'json_metadata': {
                'app': 'checkinecuador/1.0.0',
                'developer': 'menobass',
                'tags': ['introduceyourself', 'checkin'],
                'beneficiaries': [
                    {'account': 'hiveecuador', 'weight': 8000}
                ],
                'country': 'Ecuador',
                'onboarder': 'some_user',
                'image': 'https://example.com/selfie.jpg'
            }
        }
        
        validation = bot.validate_post(valid_post)
        if not validation.is_valid:
            print(f"✗ Valid post failed validation: {validation.reasons}")
            return False
        
        # Test invalid post (missing required fields)
        invalid_post = {
            'author': 'testuser2',
            'permlink': 'invalid-post',
            'title': 'Invalid post',
            'body': 'Short',
            'json_metadata': {
                'app': 'wrong_app',
                'developer': 'wrong_developer',
                'tags': ['wrong', 'tags'],
                'country': 'Wrong Country'
            }
        }
        
        validation = bot.validate_post(invalid_post)
        if validation.is_valid:
            print("✗ Invalid post passed validation when it should have failed")
            return False
        
        print("✓ Post validation works correctly")
        print(f"  - Valid post passed validation")
        print(f"  - Invalid post failed validation with reasons: {validation.reasons[:3]}...")  # Show first 3 reasons
        
        return True
        
    except Exception as e:
        print(f"✗ Post validation failed: {e}")
        return False

def test_api_connection():
    """Test Hive API connection."""
    print("\nTesting Hive API connection...")
    try:
        bot = HiveEcuadorBot()
        
        # Test basic API call
        result = bot.hive_api_call('condenser_api.get_dynamic_global_properties')
        if not result:
            print("✗ API connection failed: no response")
            return False
        
        # Test account balance (might fail if account doesn't exist, but API should respond)
        balance = bot.get_account_balance()
        print(f"✓ API connection successful")
        print(f"  - Bot account balance: {balance} HBD")
        
        return True
        
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        return False

def test_community_monitoring():
    """Test community monitoring."""
    print("\nTesting community monitoring...")
    try:
        bot = HiveEcuadorBot()
        
        # Test monitoring (this will actually call the API)
        posts = bot.monitor_community("hive-115276")
        
        print(f"✓ Community monitoring successful")
        print(f"  - Found {len(posts)} unprocessed posts")
        
        if posts:
            print(f"  - Sample post: {posts[0]['author']}/{posts[0]['permlink']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Community monitoring failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Hive Ecuador Check-in Bot - Advanced Test Suite")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_environment_variables,
        test_database_operations,
        test_post_validation,
        test_api_connection,
        test_community_monitoring,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✓ All tests passed! Your advanced bot is ready to run.")
        print("\nTo start the bot:")
        print("1. Ensure your .env file has real credentials")
        print("2. Set 'dry_run': true in config.json for testing")
        print("3. Run: python main.py")
    else:
        print("✗ Some tests failed. Please check the configuration.")
    
    print("\nFeatures ready:")
    print("• ✓ SQLite database for tracking processed posts")
    print("• ✓ Advanced post validation with all required fields")
    print("• ✓ Daily statistics and transfer limits")
    print("• ✓ Comprehensive logging")
    print("• ✓ Dry-run mode for safe testing")
    print("• ✓ Error handling and recovery")
    print("• ⚠️ Transaction signing (requires beem library on Linux/Replit)")

if __name__ == "__main__":
    main()
