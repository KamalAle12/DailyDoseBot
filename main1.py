from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import logging
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = '8159912327:AAH4ZC8GX1EYfTip_gZqR_ES_KpkuQGPykQ'  # Replace this with your actual bot token

# Store dynamically added channels
channel_ids = set()

# List of daily content (message, image_url pairs)
daily_content = [
    ("Day 1: Stay positive!", "https://cdn.pixabay.com/photo/2023/01/14/15/33/sand-dunes-7718479_1280.jpg"),
    ("Day 2: Keep learning.", "https://cdn.pixabay.com/photo/2023/01/14/15/33/sand-dunes-7718479_1280.jpg"),
    # Add more days...
]

# Function to send a message and image to a Telegram channel
def send_daily_content(chat_id, text, image, **kwargs):
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        bot.send_photo(chat_id=chat_id, photo=image, caption=text)
        logging.info(f"✅ Sent to {chat_id}: {text}")
    except Exception as e:
        logging.error(f"❌ Error sending to {chat_id}: {e}")

# Function to schedule daily messages
def schedule_for_channel(chat_id):
    tz = pytz.timezone('Asia/Kolkata')
    scheduler = BackgroundScheduler(timezone=tz)
    scheduler.start()

    for i, (text, image) in enumerate(daily_content):
        run_date = datetime.now(tz).date() + timedelta(days=i)
        run_time = tz.localize(datetime.combine(run_date, datetime.strptime("18:01", "%H:%M").time()))

        logging.info(f"📅 Scheduled Day {i+1} at {run_time} for {chat_id}")

        scheduler.add_job(
            send_daily_content,
            'date',
            run_date=run_time,
            kwargs={
                'chat_id': chat_id,
                'text': text,
                'image': image
            }
        )

# Command to manually add a new channel
def add_channel(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ Usage: /add_channel @channelusername or -1001234567890")
        return

    channel = context.args[0]
    if not (channel.startswith("@") or channel.startswith("-100")):
        update.message.reply_text("⚠️ Invalid format. Use @channelname or -100...")
        return

    if channel not in channel_ids:
        channel_ids.add(channel)
        update.message.reply_text(f"✅ Channel {channel} added and scheduled!")
        schedule_for_channel(channel)
    else:
        update.message.reply_text(f"ℹ️ Channel {channel} is already added.")

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Hello! Use /add_channel to start scheduling content for your channel.")

# Main bot setup
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_channel", add_channel))

    logging.info("🚀 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
