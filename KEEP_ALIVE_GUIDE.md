# Keeping Your Hive Bot Alive 24/7

## Option 1: Replit Always On (Paid - Recommended)

1. **Subscribe to Replit Core** ($20/month)
2. **Go to your Replit project**
3. **Click the "Always On" toggle**
4. **Your bot runs 24/7** automatically

## Option 2: UptimeRobot + Keep Alive (Free)

### Step 1: Set up the bot with keep alive
1. Install Flask: `pip install flask`
2. The bot now includes a web server that responds to pings
3. When you run `python main.py`, it will start both the bot AND a web server

### Step 2: Get your Replit URL
1. **Run your bot** on Replit
2. **Copy the URL** that Replit gives you (looks like: `https://your-repl-name.username.repl.co`)

### Step 3: Set up UptimeRobot
1. **Go to** [uptimerobot.com](https://uptimerobot.com) 
2. **Create a free account**
3. **Add New Monitor**:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: **Hive Ecuador Bot**
   - URL: **Your Replit URL** (from step 2)
   - Monitoring Interval: **5 minutes**
4. **Save the monitor**

### How it works:
- **UptimeRobot pings your bot every 5 minutes**
- **This keeps Replit awake** and prevents it from sleeping
- **Your bot runs 24/7 for free**

### Important Notes:
- The free Replit plan has limited CPU hours per month
- If you exceed the limit, the bot will stop until next month
- For production use, **Always On** is more reliable

## Option 3: Deploy to a VPS (Advanced)

You can also deploy to:
- **DigitalOcean** ($5/month)
- **Linode** ($5/month) 
- **AWS EC2** (free tier available)
- **Google Cloud** (free tier available)

This gives you full control and guaranteed uptime.

## Monitoring Your Bot

Check these to make sure your bot is working:
1. **Bot logs** - Check for errors
2. **UptimeRobot dashboard** - Shows uptime status
3. **Your Hive account** - Check for recent comments/transfers
4. **Dashboard** - Run `python dashboard.py` to see stats

## Troubleshooting

**Bot stops responding:**
1. Check Replit console for errors
2. Check if CPU hours are exhausted
3. Restart the bot manually
4. Check UptimeRobot is still pinging

**UptimeRobot shows "down":**
1. Check if Replit is running
2. Check the bot URL is accessible
3. Look for error messages in logs
