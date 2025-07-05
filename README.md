# Hive Ecuador Check-in Bot 🇪🇨

A sophisticated Python bot that monitors the `hive-115276` community for introduction posts with specific metadata and automatically provides a complete welcome experience: replies, HBD transfers, and upvotes.

## 🎯 Mission

Create an instant "wow" moment for new Hive users by providing:
- **Immediate response** with a personalized Spanish welcome message
- **Real money** (1 HBD) sent directly to their wallet
- **Community support** through upvotes
- **Seamless onboarding** that demonstrates Hive's value immediately

## ✨ Features

### 🔍 **Advanced Post Detection**
- Monitors `hive-115276` community in real-time
- Validates complex metadata requirements:
  - `app: "checkinecuador/1.0.0"`
  - `developer: "menobass"`
  - `tags: ["introduceyourself", "checkin"]` (both required)
  - `beneficiaries: [{"account": "hiveecuador", "weight": 8000}]`
  - `country: "Ecuador"`
  - `onboarder` field present
  - `image` field present (selfie requirement)

### 🛡️ **Smart Safety Features**
- **Duplicate prevention**: SQLite database tracks all processed posts
- **Daily limits**: Configurable maximum transfers per day
- **Balance checks**: Ensures sufficient HBD before transfers
- **Dry-run mode**: Test without real transactions
- **Account verification**: Validates recipients exist

### 💰 **Automated Actions**
- **Welcome comments** in Spanish with community guidelines
- **HBD transfers** (1.000 HBD default) with custom memo
- **Upvotes** (100% default) showing community support
- **Comprehensive logging** for all actions

### � **Monitoring & Analytics**
- Real-time dashboard with daily statistics
- SQLite database with processed posts tracking
- Error monitoring and health checks
- Performance metrics and trends

## 🚀 Quick Start

### 1. Environment Setup

### 1. Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configuration

Edit `.env` with your bot credentials:
```env
HIVE_ACCOUNT_NAME=your-bot-account
HIVE_POSTING_KEY=your-posting-key
HIVE_ACTIVE_KEY=your-active-key
```

### 3. Test Configuration

```bash
# Run comprehensive tests
python test_advanced.py

# View dashboard (after running bot)
python dashboard.py
```

### 4. Run the Bot

```bash
# Start with dry-run mode (safe testing)
python main.py

# For production, set "dry_run": false in config.json
```

## 🔧 Configuration

### `config.json` Options

```json
{
  "community": "hive-115276",
  "transfer_amount": 1.0,
  "upvote_percentage": 100,
  "max_daily_transfers": 10,
  "min_account_balance": 5.0,
  "dry_run": false,
  "check_interval": 60
}
```

### Required Post Metadata

Posts must include this exact structure:
```json
{
  "app": "checkinecuador/1.0.0",
  "developer": "menobass",
  "tags": ["introduceyourself", "checkin"],
  "beneficiaries": [
    {"account": "hiveecuador", "weight": 8000}
  ],
  "country": "Ecuador",
  "onboarder": "sponsor-username",
  "image": "https://example.com/selfie.jpg"
}
```

## 📊 Monitoring

### Real-time Dashboard
```bash
python dashboard.py
```

Shows:
- Bot health status
- Daily statistics
- Total performance metrics
- Recent processed posts
- Error tracking

### Log Files
- `bot.log`: Detailed operation logs
- `processed_posts.db`: SQLite database with all records

## 🛡️ Safety Features

### Duplicate Prevention
- Each author can only receive rewards once per day
- Database tracks all processed posts permanently
- Prevents accidental double-payments

### Financial Safety
- Minimum account balance checks
- Daily transfer limits
- Real-time balance monitoring
- Dry-run mode for testing

### Error Handling
- Network failure recovery
- Rate limit management
- Database corruption protection
- Comprehensive error logging

## 🚀 Deployment

### Replit (Recommended)
1. Create new Replit project
2. Upload all files
3. Set environment variables in Secrets tab
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python main.py`

### Local Development
1. Ensure Python 3.8+ installed
2. Create virtual environment
3. Install dependencies
4. Configure credentials
5. Start with dry-run mode

## 📈 Performance Metrics

The bot tracks:
- **Posts processed**: Daily count of valid introductions
- **HBD distributed**: Total welcome payments sent
- **Upvotes given**: Community support actions
- **Response time**: Average time from post to response
- **Success rate**: Percentage of successful actions

## 🔍 Troubleshooting

### Common Issues

1. **No posts detected**
   - Check community name in config
   - Verify API connectivity
   - Ensure metadata format is correct

2. **Database errors**
   - Check file permissions
   - Verify SQLite installation
   - Review error logs

3. **Transfer failures**
   - Confirm sufficient HBD balance
   - Check daily limits
   - Verify account permissions

### Debug Mode
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test thoroughly with dry-run mode
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files (`bot.log`)
3. Run the test suite (`python test_advanced.py`)
4. Check the dashboard (`python dashboard.py`)

---

**Built with ❤️ for the Hive Ecuador community**
