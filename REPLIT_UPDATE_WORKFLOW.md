# Replit Update Workflow

## Initial Setup (Do Once)

1. **In Replit Shell, configure Git:**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your-email@example.com"
   ```

2. **Connect to your GitHub repository:**
   ```bash
   git remote add origin https://github.com/yourusername/hive-checkin-bot.git
   # or if already exists:
   git remote set-url origin https://github.com/yourusername/hive-checkin-bot.git
   ```

## Regular Update Process

### Method 1: Local → GitHub → Replit (Recommended)

1. **Work locally** in VS Code
2. **Test locally** using tasks
3. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update bot features"
   git push origin main
   ```
4. **Update Replit:**
   - Go to Replit Shell
   - Run: `git pull origin main`
   - Restart bot if needed

### Method 2: Direct Replit Development

1. **Edit code directly in Replit**
2. **Test in Replit**
3. **Push to GitHub from Replit:**
   ```bash
   git add .
   git commit -m "Update from Replit"
   git push origin main
   ```

## Current File Status

- **Local**: Your working copy (most up-to-date)
- **GitHub**: Repository backup and collaboration
- **Replit**: Production environment

## Important Notes

- Always pull before pushing to avoid conflicts
- Keep your `.env` file separate on each platform
- Test thoroughly before pushing to production
- Use meaningful commit messages

## Quick Commands

**Update Replit from GitHub:**
```bash
git pull origin main
```

**Push local changes to GitHub:**
```bash
git add .
git commit -m "Your message"
git push origin main
```

**Check status:**
```bash
git status
git log --oneline -5
```
