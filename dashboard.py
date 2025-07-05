#!/usr/bin/env python3
"""
Dashboard for monitoring Hive Ecuador Check-in Bot performance.
Shows daily statistics, processed posts, and bot health.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os

class BotDashboard:
    """Dashboard for monitoring bot performance."""
    
    def __init__(self, db_file: str = "processed_posts.db"):
        self.db_file = db_file
        
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily statistics for the last N days."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT date, posts_processed, hbd_sent, upvotes_given, errors
                    FROM daily_stats
                    ORDER BY date DESC
                    LIMIT ?
                ''', (days,))
                
                results = cursor.fetchall()
                return [
                    {
                        'date': row[0],
                        'posts_processed': row[1],
                        'hbd_sent': row[2],
                        'upvotes_given': row[3],
                        'errors': row[4]
                    }
                    for row in results
                ]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_processed_posts(self, limit: int = 20) -> List[Dict]:
        """Get recently processed posts."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT author, permlink, timestamp, hbd_sent, upvoted, commented
                    FROM processed_posts
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                return [
                    {
                        'author': row[0],
                        'permlink': row[1],
                        'timestamp': row[2],
                        'hbd_sent': row[3],
                        'upvoted': bool(row[4]),
                        'commented': bool(row[5])
                    }
                    for row in results
                ]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def get_total_stats(self) -> Dict:
        """Get total statistics since bot started."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Total posts processed
                cursor.execute('SELECT COUNT(*) FROM processed_posts')
                total_posts = cursor.fetchone()[0]
                
                # Total HBD sent
                cursor.execute('SELECT SUM(hbd_sent) FROM processed_posts WHERE hbd_sent > 0')
                total_hbd = cursor.fetchone()[0] or 0
                
                # Total upvotes given
                cursor.execute('SELECT COUNT(*) FROM processed_posts WHERE upvoted = 1')
                total_upvotes = cursor.fetchone()[0]
                
                # Total errors
                cursor.execute('SELECT SUM(errors) FROM daily_stats')
                total_errors = cursor.fetchone()[0] or 0
                
                # Days active
                cursor.execute('SELECT COUNT(DISTINCT date) FROM daily_stats')
                days_active = cursor.fetchone()[0]
                
                return {
                    'total_posts': total_posts,
                    'total_hbd': total_hbd,
                    'total_upvotes': total_upvotes,
                    'total_errors': total_errors,
                    'days_active': days_active,
                    'avg_posts_per_day': total_posts / max(days_active, 1),
                    'avg_hbd_per_day': total_hbd / max(days_active, 1)
                }
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
    
    def check_bot_health(self) -> Dict:
        """Check bot health and potential issues."""
        health = {
            'status': 'healthy',
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check if database exists
            if not os.path.exists(self.db_file):
                health['status'] = 'error'
                health['issues'].append('Database file not found')
                return health
            
            # Check recent activity
            daily_stats = self.get_daily_stats(1)
            if not daily_stats:
                health['warnings'].append('No recent activity recorded')
            else:
                today_stats = daily_stats[0]
                if today_stats['errors'] > 0:
                    health['warnings'].append(f"Errors detected today: {today_stats['errors']}")
                
                # Check if bot is processing posts
                if today_stats['posts_processed'] == 0:
                    health['warnings'].append('No posts processed today')
            
            # Check configuration
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    if config.get('dry_run', False):
                        health['warnings'].append('Bot is in dry-run mode')
            
            # Check log file
            if os.path.exists('bot.log'):
                # Check if log file has been updated recently
                log_modified = datetime.fromtimestamp(os.path.getmtime('bot.log'))
                if datetime.now() - log_modified > timedelta(hours=1):
                    health['warnings'].append('Log file not updated recently - bot may not be running')
            else:
                health['warnings'].append('Log file not found')
            
            # Set status based on issues
            if health['issues']:
                health['status'] = 'error'
            elif health['warnings']:
                health['status'] = 'warning'
            
        except Exception as e:
            health['status'] = 'error'
            health['issues'].append(f'Health check failed: {str(e)}')
        
        return health
    
    def print_dashboard(self):
        """Print a formatted dashboard."""
        print("=" * 70)
        print("    HIVE ECUADOR CHECK-IN BOT DASHBOARD")
        print("=" * 70)
        
        # Bot Health
        health = self.check_bot_health()
        status_icon = "🟢" if health['status'] == 'healthy' else "🟡" if health['status'] == 'warning' else "🔴"
        print(f"\n{status_icon} Bot Status: {health['status'].upper()}")
        
        if health['issues']:
            print("\n❌ Issues:")
            for issue in health['issues']:
                print(f"   • {issue}")
        
        if health['warnings']:
            print("\n⚠️ Warnings:")
            for warning in health['warnings']:
                print(f"   • {warning}")
        
        # Total Statistics
        total_stats = self.get_total_stats()
        if total_stats:
            print(f"\n📊 TOTAL STATISTICS")
            print(f"   Posts Processed: {total_stats['total_posts']}")
            print(f"   HBD Sent: {total_stats['total_hbd']:.3f}")
            print(f"   Upvotes Given: {total_stats['total_upvotes']}")
            print(f"   Days Active: {total_stats['days_active']}")
            print(f"   Avg Posts/Day: {total_stats['avg_posts_per_day']:.1f}")
            print(f"   Avg HBD/Day: {total_stats['avg_hbd_per_day']:.3f}")
            if total_stats['total_errors'] > 0:
                print(f"   Total Errors: {total_stats['total_errors']}")
        
        # Daily Statistics
        daily_stats = self.get_daily_stats(7)
        if daily_stats:
            print(f"\n📅 DAILY STATISTICS (Last 7 Days)")
            print(f"{'Date':<12} {'Posts':<6} {'HBD':<8} {'Upvotes':<8} {'Errors':<8}")
            print("-" * 50)
            for stat in daily_stats:
                print(f"{stat['date']:<12} {stat['posts_processed']:<6} {stat['hbd_sent']:<8.1f} {stat['upvotes_given']:<8} {stat['errors']:<8}")
        
        # Recent Posts
        recent_posts = self.get_processed_posts(10)
        if recent_posts:
            print(f"\n📝 RECENT PROCESSED POSTS (Last 10)")
            print(f"{'Author':<15} {'Permlink':<25} {'HBD':<6} {'Vote':<6} {'Comment':<8}")
            print("-" * 70)
            for post in recent_posts:
                hbd_icon = "✓" if post['hbd_sent'] > 0 else "✗"
                vote_icon = "✓" if post['upvoted'] else "✗"
                comment_icon = "✓" if post['commented'] else "✗"
                
                author = post['author'][:14] + "..." if len(post['author']) > 14 else post['author']
                permlink = post['permlink'][:24] + "..." if len(post['permlink']) > 24 else post['permlink']
                
                print(f"{author:<15} {permlink:<25} {hbd_icon:<6} {vote_icon:<6} {comment_icon:<8}")
        
        print("\n" + "=" * 70)
        print(f"Dashboard generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

def main():
    """Main dashboard function."""
    dashboard = BotDashboard()
    
    try:
        dashboard.print_dashboard()
    except Exception as e:
        print(f"Error generating dashboard: {e}")
        print("Make sure the bot has been running and the database file exists.")

if __name__ == "__main__":
    main()
