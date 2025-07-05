#!/usr/bin/env python3
"""
Simple script to check the database contents
"""
import sqlite3

def check_database():
    conn = sqlite3.connect('processed_posts.db')
    cursor = conn.cursor()
    
    print("=== PROCESSED POSTS ===")
    cursor.execute('SELECT * FROM processed_posts')
    rows = cursor.fetchall()
    if rows:
        print("ID | Author | Permlink | Timestamp | HBD Sent | Upvoted | Commented")
        print("-" * 70)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")
    else:
        print("No processed posts found")
    
    print("\n=== DAILY STATS ===")
    cursor.execute('SELECT * FROM daily_stats')
    rows = cursor.fetchall()
    if rows:
        print("Date | Posts Processed | HBD Sent | Upvotes | Errors")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
    else:
        print("No daily stats found")
    
    print("\n=== DAILY TRANSFERS ===")
    cursor.execute('SELECT * FROM daily_transfers')
    rows = cursor.fetchall()
    if rows:
        print("Date | Transfer Count | Total Amount")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")
    else:
        print("No daily transfers found")
    
    conn.close()

if __name__ == "__main__":
    check_database()
