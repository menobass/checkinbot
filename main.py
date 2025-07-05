#!/usr/bin/env python3
"""
Hive Ecuador Check-in Bot

This bot monitors the hive-115276 community for introduction posts with specific metadata
and automatically replies, sends HBD transfers, and upvotes qualifying posts.

Requirements:
- app: "checkinecuador/1.0.0"
- developer: "menobass"  
- tags: ["introduceyourself", "checkin"]
- beneficiaries: [{"account": "hiveecuador", "weight": 8000}]
- country: "Ecuador"
- onboarder field present
- image field present (selfie requirement)
"""

import json
import time
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import requests
from dataclasses import dataclass

# Hive blockchain imports
try:
    from lighthive.client import Client
    LIGHTHIVE_AVAILABLE = True
except ImportError:
    LIGHTHIVE_AVAILABLE = False
    logging.warning("lighthive library not available - blockchain transactions will be simulated")

# Legacy beem support (fallback)
try:
    from beem import Hive
    from beem.account import Account
    from beem.comment import Comment
    from beem.exceptions import AccountDoesNotExistsException, WalletLocked
    BEEM_AVAILABLE = True
except ImportError:
    BEEM_AVAILABLE = False
    if not LIGHTHIVE_AVAILABLE:
        logging.warning("No Hive blockchain library available - transactions will be simulated")

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging(log_file: str = "bot.log"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

@dataclass
class PostValidation:
    """Data class for post validation results."""
    is_valid: bool
    reasons: List[str]
    post_data: Dict

@dataclass
class DailyStats:
    """Data class for daily statistics."""
    date: str
    posts_processed: int
    hbd_sent: float
    upvotes_given: int
    errors: int

class DatabaseManager:
    """Handle SQLite database operations."""
    
    def __init__(self, db_file: str = "processed_posts.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Processed posts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author TEXT NOT NULL,
                    permlink TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    hbd_sent REAL,
                    upvoted BOOLEAN,
                    commented BOOLEAN,
                    UNIQUE(author, permlink)
                )
            ''')
            
            # Daily stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    posts_processed INTEGER DEFAULT 0,
                    hbd_sent REAL DEFAULT 0.0,
                    upvotes_given INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0
                )
            ''')
            
            # Daily transfer limits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_transfers (
                    date TEXT PRIMARY KEY,
                    transfer_count INTEGER DEFAULT 0,
                    total_amount REAL DEFAULT 0.0
                )
            ''')
            
            conn.commit()
    
    def is_post_processed(self, author: str, permlink: str) -> bool:
        """Check if a post has already been processed."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM processed_posts WHERE author = ? AND permlink = ?",
                (author, permlink)
            )
            return cursor.fetchone()[0] > 0
    
    def can_send_transfer_today(self, max_daily_transfers: int) -> bool:
        """Check if we can send more transfers today."""
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT transfer_count FROM daily_transfers WHERE date = ?",
                (today,)
            )
            result = cursor.fetchone()
            current_count = result[0] if result else 0
            return current_count < max_daily_transfers
    
    def record_processed_post(self, author: str, permlink: str, hbd_sent: float, upvoted: bool, commented: bool):
        """Record a processed post in the database."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO processed_posts 
                (author, permlink, hbd_sent, upvoted, commented)
                VALUES (?, ?, ?, ?, ?)
            ''', (author, permlink, hbd_sent, upvoted, commented))
            conn.commit()
    
    def update_daily_stats(self, posts_processed: int = 0, hbd_sent: float = 0.0, upvotes_given: int = 0, errors: int = 0):
        """Update daily statistics."""
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (date, posts_processed, hbd_sent, upvotes_given, errors)
                VALUES (?, 
                    COALESCE((SELECT posts_processed FROM daily_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT hbd_sent FROM daily_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT upvotes_given FROM daily_stats WHERE date = ?), 0) + ?,
                    COALESCE((SELECT errors FROM daily_stats WHERE date = ?), 0) + ?
                )
            ''', (today, today, posts_processed, today, hbd_sent, today, upvotes_given, today, errors))
            
            # Update daily transfer count
            cursor.execute('''
                INSERT OR REPLACE INTO daily_transfers 
                (date, transfer_count, total_amount)
                VALUES (?, 
                    COALESCE((SELECT transfer_count FROM daily_transfers WHERE date = ?), 0) + ?,
                    COALESCE((SELECT total_amount FROM daily_transfers WHERE date = ?), 0) + ?
                )
            ''', (today, today, 1 if hbd_sent > 0 else 0, today, hbd_sent))
            
            conn.commit()
    
    def get_daily_stats(self, date: str = None) -> Optional[DailyStats]:
        """Get daily statistics for a specific date."""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, posts_processed, hbd_sent, upvotes_given, errors FROM daily_stats WHERE date = ?",
                (date,)
            )
            result = cursor.fetchone()
            if result:
                return DailyStats(*result)
            return None

class HiveEcuadorBot:
    """Main bot class for handling Hive Ecuador community interactions."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the bot with configuration."""
        self.config = self.load_config(config_path)
        self.db = DatabaseManager(self.config.get('database_file', 'processed_posts.db'))
        
        # Get credentials from environment variables
        self.account_name = os.getenv('HIVE_ACCOUNT_NAME')
        self.posting_key = os.getenv('HIVE_POSTING_KEY')
        self.active_key = os.getenv('HIVE_ACTIVE_KEY')
        self.hive_node = os.getenv('HIVE_NODE', 'https://api.hive.blog')
        
        if not all([self.account_name, self.posting_key, self.active_key]):
            raise ValueError("Missing required environment variables for Hive credentials")
        
        # Initialize HTTP session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HiveEcuadorBot/1.0'
        })
        
        # Initialize hive client for blockchain transactions
        self.hive_client = None
        if LIGHTHIVE_AVAILABLE:
            try:
                self.hive_client = Client(
                    nodes=[self.hive_node],
                    keys=[self.posting_key, self.active_key]
                )
                logger.info("Lighthive client initialized successfully for blockchain transactions")
            except Exception as e:
                logger.error(f"Failed to initialize lighthive client: {e}")
                self.hive_client = None
        elif BEEM_AVAILABLE:
            try:
                self.hive = Hive(node=self.hive_node, keys=[self.posting_key, self.active_key])
                logger.info("Beem initialized successfully for blockchain transactions")
            except Exception as e:
                logger.error(f"Failed to initialize beem: {e}")
                self.hive = None
        else:
            logger.warning("No Hive blockchain library available - transactions will be simulated")
        
        logger.info(f"Bot initialized for community: {self.config.get('community')}")
        logger.info(f"Dry run mode: {self.config.get('dry_run', False)}")
        logger.info(f"Blockchain transactions enabled: {self.hive_client is not None or (hasattr(self, 'hive') and self.hive is not None)}")
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file {config_path}")
            raise
    
    def hive_api_call(self, method: str, params: List = None) -> Optional[Dict]:
        """Make a call to the Hive API."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or [],
                "id": 1
            }
            
            response = self.session.post(self.hive_node, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'error' in result:
                logger.error(f"API Error: {result['error']}")
                return None
                
            return result.get('result')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API call: {e}")
            return None
    
    def get_account_balance(self) -> float:
        """Get the bot account's HBD balance."""
        try:
            accounts = self.hive_api_call('condenser_api.get_accounts', [[self.account_name]])
            if accounts and len(accounts) > 0:
                hbd_balance = accounts[0].get('hbd_balance', '0.000 HBD')
                return float(hbd_balance.split()[0])
            return 0.0
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 0.0
    
    def monitor_community(self, community: str) -> List[Dict]:
        """Monitor a specific community for new posts."""
        try:
            logger.info(f"Monitoring community: {community}")
            
            # Get discussions from the community using bridge API
            params = {
                "tag": community,
                "limit": 20,
                "sort": "created"
            }
            
            response = self.hive_api_call('bridge.get_ranked_posts', [params])
            
            if not response:
                logger.warning(f"No response from API for community {community}")
                return []
            
            posts = []
            for post_data in response:
                # Skip already processed posts
                if self.db.is_post_processed(post_data['author'], post_data['permlink']):
                    continue
                    
                # Only process posts from the last 24 hours
                created_time = datetime.strptime(post_data['created'], '%Y-%m-%dT%H:%M:%S')
                if datetime.now() - created_time > timedelta(hours=24):
                    continue
                
                # Debug: log what fields are available
                logger.info(f"DEBUG: Available fields in post_data: {list(post_data.keys())}")
                logger.info(f"DEBUG: Extensions in post_data: {post_data.get('extensions', 'NOT FOUND')}")
                
                post = {
                    'id': f"{post_data['author']}/{post_data['permlink']}",
                    'author': post_data['author'],
                    'permlink': post_data['permlink'],
                    'title': post_data['title'],
                    'body': post_data['body'],
                    'created': post_data['created'],
                    'json_metadata': post_data.get('json_metadata', {}),
                    'extensions': post_data.get('extensions', []),
                    'beneficiaries': post_data.get('beneficiaries', [])  # Add direct beneficiaries field
                }
                posts.append(post)
            
            logger.info(f"Found {len(posts)} unprocessed recent posts in {community}")
            return posts
            
        except Exception as e:
            logger.error(f"Error monitoring community {community}: {e}")
            self.db.update_daily_stats(errors=1)
            return []
    
    def validate_post(self, post: Dict) -> PostValidation:
        """Comprehensive post validation."""
        reasons = []
        required_metadata = self.config.get('required_metadata', {})
        
        # Add debug logging
        logger.info(f"DEBUG: Validating post by {post.get('author')}: {post.get('permlink')}")
        logger.info(f"DEBUG: Post extensions: {post.get('extensions', [])}")
        
        # Parse json_metadata if it's a string
        json_metadata = post.get('json_metadata', {})
        if isinstance(json_metadata, str):
            try:
                json_metadata = json.loads(json_metadata)
            except json.JSONDecodeError:
                reasons.append("Invalid JSON metadata")
                return PostValidation(False, reasons, post)
        
        logger.info(f"DEBUG: Post json_metadata: {json_metadata}")
        
        # Check app field
        required_app = required_metadata.get('app')
        if required_app and json_metadata.get('app') != required_app:
            reasons.append(f"App mismatch: expected {required_app}, got {json_metadata.get('app')}")
        
        # Check developer field
        required_developer = required_metadata.get('developer')
        if required_developer and json_metadata.get('developer') != required_developer:
            reasons.append(f"Developer mismatch: expected {required_developer}, got {json_metadata.get('developer')}")
        
        # Check tags (both must be present)
        required_tags = required_metadata.get('tags', [])
        post_tags = json_metadata.get('tags', [])
        missing_tags = [tag for tag in required_tags if tag not in post_tags]
        if missing_tags:
            reasons.append(f"Missing required tags: {missing_tags}")
        
        # Check beneficiaries (can be in json_metadata, extensions, or direct field)
        required_beneficiaries = required_metadata.get('beneficiaries', [])
        post_beneficiaries = json_metadata.get('beneficiaries', [])
        
        logger.info(f"DEBUG: Required beneficiaries: {required_beneficiaries}")
        logger.info(f"DEBUG: Beneficiaries from json_metadata: {post_beneficiaries}")
        
        # Check direct beneficiaries field (where they're actually stored in API response)
        direct_beneficiaries = post.get('beneficiaries', [])
        logger.info(f"DEBUG: Direct beneficiaries from API: {direct_beneficiaries}")
        if direct_beneficiaries:
            post_beneficiaries.extend(direct_beneficiaries)
        
        # Also check extensions field for beneficiaries (fallback)
        extensions = post.get('extensions', [])
        logger.info(f"DEBUG: Extensions to check: {extensions}")
        
        for ext in extensions:
            logger.info(f"DEBUG: Processing extension: {ext}")
            if isinstance(ext, list) and len(ext) >= 2 and ext[0] == 0:
                logger.info(f"DEBUG: Found beneficiary extension: {ext}")
                # Beneficiary extension format: [0, {"beneficiaries": [...]}]
                if isinstance(ext[1], dict) and 'beneficiaries' in ext[1]:
                    logger.info(f"DEBUG: Found beneficiaries in extension: {ext[1]['beneficiaries']}")
                    post_beneficiaries.extend(ext[1]['beneficiaries'])
        
        logger.info(f"DEBUG: Final post_beneficiaries list: {post_beneficiaries}")
        
        for req_ben in required_beneficiaries:
            found = False
            logger.info(f"DEBUG: Looking for required beneficiary: {req_ben}")
            for post_ben in post_beneficiaries:
                logger.info(f"DEBUG: Checking against post beneficiary: {post_ben}")
                logger.info(f"DEBUG: Account match: {post_ben.get('account')} == {req_ben.get('account')} -> {post_ben.get('account') == req_ben.get('account')}")
                logger.info(f"DEBUG: Weight match: {post_ben.get('weight')} == {req_ben.get('weight')} -> {post_ben.get('weight') == req_ben.get('weight')}")
                if (post_ben.get('account') == req_ben.get('account') and 
                    post_ben.get('weight') == req_ben.get('weight')):
                    found = True
                    logger.info(f"DEBUG: Found matching beneficiary!")
                    break
            if not found:
                logger.info(f"DEBUG: Missing beneficiary: {req_ben}")
                reasons.append(f"Missing beneficiary: {req_ben}")
        
        # Check country
        required_country = required_metadata.get('country')
        if required_country and json_metadata.get('country') != required_country:
            reasons.append(f"Country mismatch: expected {required_country}, got {json_metadata.get('country')}")
        
        # Check required fields
        required_fields = required_metadata.get('required_fields', [])
        for field in required_fields:
            if field not in json_metadata or not json_metadata[field]:
                reasons.append(f"Missing required field: {field}")
        
        # Check if post has introduction content (basic validation)
        if len(post.get('body', '')) < 100:
            reasons.append("Post body too short for introduction")
        
        is_valid = len(reasons) == 0
        
        if is_valid:
            logger.info(f"Post {post['permlink']} by {post['author']} passed validation")
        else:
            logger.info(f"Post {post['permlink']} by {post['author']} failed validation: {reasons}")
        
        return PostValidation(is_valid, reasons, post)
    
    def send_welcome_comment(self, post: Dict) -> bool:
        """Send a welcome comment to a post."""
        try:
            if self.config.get('dry_run', False):
                logger.info(f"[DRY RUN] Would send welcome comment to {post['author']}/{post['permlink']}")
                return True
            
            welcome_message = self.config.get('welcome_message', 'Welcome to Hive Ecuador!')
            
            # Use lighthive for real blockchain transactions
            if self.hive_client and LIGHTHIVE_AVAILABLE:
                try:
                    # Create comment
                    comment_body = welcome_message
                    comment_permlink = f"re-{post['permlink']}-{int(time.time())}"
                    
                    logger.info(f"DEBUG: Attempting to comment on {post['author']}/{post['permlink']}")
                    logger.info(f"DEBUG: Comment body: {comment_body}")
                    logger.info(f"DEBUG: Comment permlink: {comment_permlink}")
                    
                    # Post the comment using lighthive
                    op = {
                        'parent_author': post['author'],
                        'parent_permlink': post['permlink'],
                        'author': self.account_name,
                        'permlink': comment_permlink,
                        'title': '',
                        'body': comment_body,
                        'json_metadata': '{"tags":["checkinecuador"]}'
                    }
                    
                    result = self.hive_client.broadcast_operation('comment', op)
                    
                    if result:
                        logger.info(f"✅ REAL COMMENT POSTED to {post['author']}/{post['permlink']}")
                        return True
                    else:
                        logger.error(f"❌ Failed to post comment - no result returned")
                        return False
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to post comment: {e}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    return False
            
            # Fallback to beem if available
            elif hasattr(self, 'hive') and self.hive and BEEM_AVAILABLE:
                try:
                    # Get the parent post
                    parent_post = Comment(f"@{post['author']}/{post['permlink']}", hive_instance=self.hive)
                    
                    # Create comment
                    comment_body = welcome_message
                    comment_permlink = f"re-{post['permlink']}-{int(time.time())}"
                    
                    logger.info(f"DEBUG: Attempting to comment on {post['author']}/{post['permlink']} using beem")
                    
                    # Post the comment
                    parent_post.reply(
                        body=comment_body,
                        author=self.account_name,
                        permlink=comment_permlink
                    )
                    
                    logger.info(f"✅ REAL COMMENT POSTED to {post['author']}/{post['permlink']} (beem)")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to post comment (beem): {e}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    return False
            else:
                logger.warning("❌ No blockchain library available - simulating comment")
                logger.info(f"[SIMULATED] Sent welcome comment to {post['author']}/{post['permlink']}")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error sending welcome comment: {e}")
            return False
    
    def send_hbd_transfer(self, recipient: str, amount: float) -> bool:
        """Send HBD transfer to a user."""
        try:
            if self.config.get('dry_run', False):
                logger.info(f"[DRY RUN] Would send {amount} HBD to {recipient}")
                return True
            
            # Check if we can send more transfers today
            if not self.db.can_send_transfer_today(self.config.get('max_daily_transfers', 10)):
                logger.warning("❌ Daily transfer limit reached")
                return False
            
            # Check minimum balance
            current_balance = self.get_account_balance()
            min_balance = self.config.get('min_account_balance', 5.0)
            if current_balance < min_balance:
                logger.warning(f"❌ Insufficient balance: {current_balance} HBD (minimum: {min_balance})")
                return False
            
            memo = self.config.get('hbd_transfer_memo', 'Welcome to Hive Ecuador!')
            
            # Use lighthive for real blockchain transactions
            if self.hive_client and LIGHTHIVE_AVAILABLE:
                try:
                    logger.info(f"DEBUG: Attempting to send {amount} HBD to {recipient}")
                    logger.info(f"DEBUG: Memo: {memo}")
                    logger.info(f"DEBUG: Current balance: {current_balance} HBD")
                    
                    # Send the transfer using lighthive
                    op = {
                        'from': self.account_name,
                        'to': recipient,
                        'amount': f"{amount:.3f} HBD",
                        'memo': memo
                    }
                    
                    result = self.hive_client.broadcast_operation('transfer', op)
                    
                    if result:
                        logger.info(f"✅ REAL HBD TRANSFER SENT: {amount} HBD to {recipient}")
                        return True
                    else:
                        logger.error(f"❌ Failed to send HBD transfer - no result returned")
                        return False
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to send HBD transfer: {e}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    return False
            
            # Fallback to beem if available
            elif hasattr(self, 'hive') and self.hive and BEEM_AVAILABLE:
                try:
                    logger.info(f"DEBUG: Attempting to send {amount} HBD to {recipient} using beem")
                    
                    # Send the transfer using the hive instance
                    self.hive.transfer(
                        to=recipient,
                        amount=amount,
                        asset="HBD",
                        memo=memo,
                        account=self.account_name
                    )
                    
                    logger.info(f"✅ REAL HBD TRANSFER SENT: {amount} HBD to {recipient} (beem)")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to send HBD transfer (beem): {e}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    return False
            else:
                logger.warning("❌ No blockchain library available - simulating transfer")
                logger.info(f"[SIMULATED] Sent {amount} HBD to {recipient}")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error sending HBD transfer: {e}")
            return False
    
    def upvote_post(self, author: str, permlink: str, weight: int = 10000) -> bool:
        """Upvote a post."""
        try:
            if self.config.get('dry_run', False):
                logger.info(f"[DRY RUN] Would upvote {author}/{permlink} with {weight/100}%")
                return True
            
            # Use lighthive for real blockchain transactions
            if self.hive_client and LIGHTHIVE_AVAILABLE:
                try:
                    logger.info(f"DEBUG: Attempting to upvote {author}/{permlink} with {weight/100}%")
                    
                    # Create vote operation
                    op = {
                        'voter': self.account_name,
                        'author': author,
                        'permlink': permlink,
                        'weight': weight
                    }
                    
                    result = self.hive_client.broadcast_operation('vote', op)
                    
                    if result:
                        logger.info(f"✅ REAL UPVOTE GIVEN: {author}/{permlink} with {weight/100}%")
                        return True
                    else:
                        logger.error(f"❌ Failed to upvote post - no result returned")
                        return False
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to upvote post: {e}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    return False
            
            # Fallback to beem if available
            elif hasattr(self, 'hive') and self.hive and BEEM_AVAILABLE:
                try:
                    logger.info(f"DEBUG: Attempting to upvote {author}/{permlink} with {weight/100}% using beem")
                    
                    # Get the post and upvote it
                    post = Comment(f"@{author}/{permlink}", hive_instance=self.hive)
                    post.upvote(weight=weight/100.0, voter=self.account_name)
                    
                    logger.info(f"✅ REAL UPVOTE GIVEN: {author}/{permlink} with {weight/100}% (beem)")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ FAILED to upvote post (beem): {e}")
                    logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                    return False
            else:
                logger.warning("❌ No blockchain library available - simulating upvote")
                logger.info(f"[SIMULATED] Upvoted {author}/{permlink} with {weight/100}%")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error upvoting post: {e}")
            return False
    
    def process_post(self, post: Dict) -> bool:
        """Process a validated post with all actions."""
        try:
            # Validate post
            validation = self.validate_post(post)
            if not validation.is_valid:
                logger.info(f"Post {post['permlink']} by {post['author']} failed validation: {validation.reasons}")
                return False
            
            author = post['author']
            permlink = post['permlink']
            
            logger.info(f"Processing valid post: {author}/{permlink}")
            
            # Perform actions - only record success if they actually work
            commented = False
            hbd_sent = 0.0
            upvoted = False
            
            # Try to send comment
            if self.send_welcome_comment(post):
                commented = True
                logger.info(f"✅ Comment successful for {author}/{permlink}")
            else:
                logger.error(f"❌ Comment failed for {author}/{permlink}")
            
            # Try to send HBD transfer
            transfer_amount = self.config.get('transfer_amount', 1.0)
            if self.send_hbd_transfer(author, transfer_amount):
                hbd_sent = transfer_amount
                logger.info(f"✅ HBD transfer successful: {transfer_amount} HBD to {author}")
            else:
                logger.error(f"❌ HBD transfer failed to {author}")
            
            # Try to upvote
            upvote_weight = self.config.get('upvote_percentage', 100) * 100  # Convert to weight
            if self.upvote_post(author, permlink, upvote_weight):
                upvoted = True
                logger.info(f"✅ Upvote successful for {author}/{permlink}")
            else:
                logger.error(f"❌ Upvote failed for {author}/{permlink}")
            
            # Record in database - only what actually succeeded
            self.db.record_processed_post(author, permlink, hbd_sent, upvoted, commented)
            
            # Update stats
            self.db.update_daily_stats(
                posts_processed=1,
                hbd_sent=hbd_sent,
                upvotes_given=1 if upvoted else 0
            )
            
            # Summary log
            actions_summary = []
            if commented:
                actions_summary.append("comment")
            if hbd_sent > 0:
                actions_summary.append(f"{hbd_sent} HBD transfer")
            if upvoted:
                actions_summary.append("upvote")
            
            if actions_summary:
                logger.info(f"✅ Successfully processed post {author}/{permlink}: {', '.join(actions_summary)}")
            else:
                logger.warning(f"⚠️  Post {author}/{permlink} was processed but no actions succeeded")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing post: {e}")
            self.db.update_daily_stats(errors=1)
            return False
    
    def print_daily_stats(self):
        """Print daily statistics."""
        stats = self.db.get_daily_stats()
        if stats:
            logger.info("=== Daily Statistics ===")
            logger.info(f"Date: {stats.date}")
            logger.info(f"Posts processed: {stats.posts_processed}")
            logger.info(f"HBD sent: {stats.hbd_sent}")
            logger.info(f"Upvotes given: {stats.upvotes_given}")
            logger.info(f"Errors: {stats.errors}")
            logger.info("========================")
    
    def run(self):
        """Main bot loop."""
        logger.info("Starting Hive Ecuador Check-in Bot...")
        logger.info(f"Monitoring community: {self.config.get('community')}")
        
        try:
            # Print initial stats
            self.print_daily_stats()
            
            while True:
                community = self.config.get('community', '')
                if not community:
                    logger.error("No community specified in config")
                    break
                
                # Monitor community for new posts
                posts = self.monitor_community(community)
                
                # Process each post
                for post in posts:
                    try:
                        self.process_post(post)
                    except Exception as e:
                        logger.error(f"Error processing post {post.get('permlink', 'unknown')}: {e}")
                        self.db.update_daily_stats(errors=1)
                
                # Print stats every hour
                if int(time.time()) % 3600 < 60:  # Roughly every hour
                    self.print_daily_stats()
                
                # Wait before next check
                sleep_time = self.config.get('check_interval', 60)
                logger.info(f"Waiting {sleep_time} seconds before next check...")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.db.update_daily_stats(errors=1)
            raise
        finally:
            logger.info("Bot shutdown complete")


if __name__ == "__main__":
    bot = HiveEcuadorBot()
    bot.run()
