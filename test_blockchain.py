#!/usr/bin/env python3
"""
Test script to check if the bot can actually perform blockchain transactions
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import HiveEcuadorBot
    
    def test_blockchain_transactions():
        """Test if the bot can perform real blockchain transactions."""
        print("=== Testing Blockchain Transaction Capability ===\n")
        
        # Initialize the bot
        try:
            bot = HiveEcuadorBot()
            print(f"✅ Bot initialized successfully")
            print(f"   - Account: {bot.account_name}")
            print(f"   - Lighthive available: {bot.hive_client is not None}")
            print(f"   - Dry run mode: {bot.config.get('dry_run', False)}")
            
            # Check balance
            balance = bot.get_account_balance()
            print(f"   - Current HBD balance: {balance}")
            
            # Check if we have the required credentials
            if not bot.hive_client:
                print("❌ WARNING: Lighthive client not properly initialized!")
                print("   This means blockchain transactions will be simulated only.")
                print("   Possible issues:")
                print("   - Missing lighthive library installation")
                print("   - Invalid credentials")
                print("   - Network connection issues")
                return False
            
            print("✅ Bot is ready for real blockchain transactions!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing bot: {e}")
            return False
    
    if __name__ == "__main__":
        success = test_blockchain_transactions()
        
        if success:
            print("\n=== RECOMMENDATION ===")
            print("The bot should now be able to perform real blockchain transactions.")
            print("If you want to test with the previously processed post:")
            print("1. Delete the database entry: python reset_db.py")
            print("2. Run the bot again to reprocess the post")
            print("3. Check the blockchain for actual comment and HBD transfer")
        else:
            print("\n=== ISSUES FOUND ===")
            print("The bot cannot perform real blockchain transactions.")
            print("Please check:")
            print("- Environment variables are set correctly")
            print("- Internet connection is working")
            print("- Account credentials are valid")
            
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
