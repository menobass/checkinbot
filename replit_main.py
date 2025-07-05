"""
Replit configuration for the Hive Check-in Bot.
This file helps configure the bot for running on Replit.
"""

import os
from main import HiveCheckinBot

def setup_replit_environment():
    """Set up environment variables for Replit deployment."""
    
    # Check if we're running on Replit
    if os.getenv('REPLIT'):
        print("Running on Replit environment")
        
        # Replit uses different environment variable names
        # You can set these in Replit's "Secrets" tab
        os.environ['HIVE_ACCOUNT_NAME'] = os.getenv('REPLIT_HIVE_ACCOUNT_NAME', '')
        os.environ['HIVE_POSTING_KEY'] = os.getenv('REPLIT_HIVE_POSTING_KEY', '')
        os.environ['HIVE_ACTIVE_KEY'] = os.getenv('REPLIT_HIVE_ACTIVE_KEY', '')
        os.environ['HIVE_NODE'] = os.getenv('REPLIT_HIVE_NODE', 'https://api.hive.blog')
        os.environ['COMMUNITY_NAME'] = os.getenv('REPLIT_COMMUNITY_NAME', '')

def run_bot():
    """Run the bot with Replit configuration."""
    setup_replit_environment()
    
    # Create and run the bot
    bot = HiveCheckinBot()
    bot.run()

if __name__ == "__main__":
    run_bot()
