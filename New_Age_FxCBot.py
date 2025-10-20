#!/usr/bin/env python3
"""
New_Age_FxCBot.py
Daily Telegram message bot — sends messages every day including weekends.
Requires: requests, schedule
"""

import requests, schedule, time, logging
import os
from datetime import datetime
from pathlib import Path


# ------------- CONFIG -------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Your bot token
CHAT_ID = os.getenv("CHAT_ID")  # Your chat ID (note: must be a string, no minus outside quotes)
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "08:00")  # 8 AM Nigeria Time
MESSAGE_FILE = os.getenv("MESSAGE_FILE", "daily_message.txt")  # Message file
LOG_FILE = "bot.log"
SEND_ON_START = os.getenv("SEND_ON_START", "false").lower() == "true"
# ----------------------------------


# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def prompt_for_message():
    """Load the daily message from file if it exists."""
    p = Path(MESSAGE_FILE)
    if p.exists():
        msg = p.read_text(encoding="utf-8").strip()
        logging.info("Loaded message from %s", MESSAGE_FILE)
        return msg
    else:
        logging.warning("No message file found. Using default message.")
        return "Hello traders 👋 — here's your daily update!"


def send_telegram_message(token, chat_id, message):
    """Send a message via Telegram API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": str(chat_id),
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, data=payload, timeout=15)
        if r.status_code == 200:
            logging.info("Message sent successfully.")
            return True
        else:
            logging.error("Failed to send message. Status %s, Response: %s", r.status_code, r.text)
            return False
    except Exception as e:
        logging.exception("Exception sending message: %s", e)
        return False


def job():
    """Main job that runs at scheduled times."""
    global daily_message
    today = datetime.now().strftime("%A")  # e.g. Saturday
    message_to_send = daily_message

    # Weekend special messages
    if today == "Saturday":
        message_to_send = f"🌞 Happy Weekend — ({today})!\n\nEnjoy your rest day traders!"
    elif today == "Sunday":
        message_to_send = f"🌞 Hey traders, Happy {today}!\n\nPrepare for a new trading week ahead 💹"

    logging.info(f"Sending scheduled message for {today}")
    sent = send_telegram_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message_to_send)

    if sent:
        print(f"[{datetime.now()}] {today} message sent successfully.")
    else:
        print(f"[{datetime.now()}] ❌ Failed to send {today} message. Check {LOG_FILE}.")


# ------------- MAIN EXECUTION -------------
if __name__ == "__main__":
    logging.info("Bot starting...")
    print("Starting New_Age_FxCBot...")

    # Validate configuration
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        print("ERROR: Missing TELEGRAM_BOT_TOKEN or CHAT_ID.")
        logging.error("Missing TELEGRAM_BOT_TOKEN or CHAT_ID.")
        exit(1)

    daily_message = prompt_for_message()

    # Schedule daily messages (Mon–Sun)
    schedule.every().day.at(SCHEDULE_TIME).do(job)

    print(f"✅ Bot scheduled to send message daily at {SCHEDULE_TIME} (Nigeria Time).")
    logging.info("Scheduled job at %s", SCHEDULE_TIME)

    # Optional: send immediately at startup
    if SEND_ON_START:
        print("SEND_ON_START=true → sending initial message now...")
        job()

    # Loop forever to keep bot alive
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("Bot stopped by user.")
        logging.info("Bot stopped manually.")
