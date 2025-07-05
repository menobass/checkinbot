#!/usr/bin/env python3
"""
Keep alive web server for Replit
This creates a simple web server that UptimeRobot can ping to keep the bot alive
"""

from flask import Flask
from threading import Thread
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Hive Ecuador Bot is alive! 🤖"

@app.route('/status')
def status():
    return {
        "status": "running",
        "bot": "Hive Ecuador Check-in Bot",
        "timestamp": time.time()
    }

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
