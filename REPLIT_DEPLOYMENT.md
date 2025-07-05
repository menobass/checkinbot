# Replit Deployment Guide

This guide will help you deploy your Hive Check-in Bot on Replit.

## Step 1: Create a Replit Account

1. Go to [replit.com](https://replit.com)
2. Sign up for a free account
3. Click "Create Repl"

## Step 2: Set Up Your Replit Project

1. Choose "Import from GitHub" or "Upload files"
2. Upload all your bot files:
   - `main.py`
   - `replit_main.py`
   - `config.json`
   - `requirements.txt`
   - `README.md`

## Step 3: Configure Environment Variables

1. In your Replit project, click on "Secrets" in the left sidebar
2. Add the following secrets:

```
REPLIT_HIVE_ACCOUNT_NAME = your-bot-account-name
REPLIT_HIVE_POSTING_KEY = your-posting-key
REPLIT_HIVE_ACTIVE_KEY = your-active-key
REPLIT_HIVE_NODE = https://api.hive.blog
REPLIT_COMMUNITY_NAME = your-community-name
```

## Step 4: Install Dependencies

1. Open the Shell tab in Replit
2. Run: `pip install -r requirements.txt`

## Step 5: Configure Your Bot

1. Edit `config.json` to match your community settings:
   - Update `community` with your community name
   - Customize `welcome_message`
   - Set `required_metadata` criteria

## Step 6: Test Your Bot

1. Run the test script: `python test_bot.py`
2. Check that all tests pass

## Step 7: Deploy Your Bot

1. Change the main file to `replit_main.py` in Replit settings
2. Click "Run" to start your bot
3. Monitor the console for logs

## Step 8: Keep Your Bot Running

1. Replit free accounts have limited uptime
2. Consider upgrading to Replit Pro for 24/7 uptime
3. Use the "Always On" feature for continuous operation

## Troubleshooting

### Common Issues:

1. **Import errors**: Make sure all dependencies are installed
2. **Authentication errors**: Check your Hive keys in Secrets
3. **Community not found**: Verify the community name format
4. **No posts found**: Check if the community has recent posts

### Debugging:

1. Check the console output for error messages
2. Use `python test_bot.py` to test individual components
3. Verify your Hive account has sufficient HBD for transfers

## Security Notes

- Never share your private keys
- Use the Replit Secrets feature for sensitive data
- Consider using a dedicated bot account
- Monitor your bot's activity regularly

## Support

If you encounter issues:
1. Check the logs in the Replit console
2. Verify your configuration files
3. Test with a small community first
4. Monitor your HBD balance
