#!/usr/bin/env python3
"""
Script to reset/clear the database
"""
import sqlite3
import os

def reset_database():
    db_file = 'processed_posts.db'
    
    if os.path.exists(db_file):
        print(f"Deleting existing database: {db_file}")
        os.remove(db_file)
        print("Database deleted successfully!")
    else:
        print("No database file found to delete")
    
    # Recreate empty database
    conn = sqlite3.connect(db_file)
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
    conn.close()
    print("Fresh database created!")

if __name__ == "__main__":
    reset_database()
