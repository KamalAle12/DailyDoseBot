from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import logging

# Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Replace with your bot token
TELEGRAM_TOKEN = '8159912327:AAH4ZC8GX1EYfTip_gZqR_ES_KpkuQGPykQ'

# Timezone and scheduler
tz = pytz.timezone('Asia/Kolkata')
scheduler = BackgroundScheduler(timezone=tz)
scheduler.start()

# Tracked channels
channel_ids = set()

# Example: Unique messages and images for each day per channel
channel_daily_content = {
    "@bottextchannel": [
        ("🌞 Stay positive! Day 1", "https://cdn.pixabay.com/photo/2023/01/14/15/33/sand-dunes-7718479_1280.jpg"),
        ("📘 Keep learning! Day 2", "https://cdn.pixabay.com/photo/2023/02/20/12/20/mountain-7802783_1280.jpg"),
        # Add up to 30 entries
    ],
    "@bottextchannel2": [
        ("💡 Stay curious! Day 1", "https://cdn.pixabay.com/photo/2023/01/14/15/33/sand-dunes-7718479_1280.jpg"),
        ("🎯 Stay focused! Day 2", "https://cdn.pixabay.com/photo/2023/01/14/15/33/sand-dunes-7718479_1280.jpg"),
        # Add up to 30 entries
    ]
}

# Send content
def send_daily_content(chat_id, text, image):
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        bot.send_photo(chat_id=chat_id, photo=image, caption=text)
        logging.info(f"✅ Sent to {chat_id}: {text}")
    except Exception as e:
        logging.error(f"❌ Error sending to {chat_id}: {e}")

# Scheduler for each channel
def schedule_for_channel(chat_id):
    content = channel_daily_content.get(chat_id)
    if not content:
        logging.warning(f"⚠️ No content for {chat_id}")
        return

    for i, (text, image) in enumerate(content):
        run_date = datetime.now(tz).date() + timedelta(days=i)
        run_time = tz.localize(datetime.combine(run_date, datetime.strptime("18:00", "%H:%M").time()))

        logging.info(f"📅 Scheduled Day {i+1} at {run_time} for {chat_id}")

        scheduler.add_job(
            send_daily_content,
            'date',
            run_date=run_time,
            kwargs={'chat_id': chat_id, 'text': text, 'image': image}
        )

# Add channel via command
def add_channel(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ Usage: /add_channel @channelusername")
        return

    channel = context.args[0].lower()
    if not (channel.startswith("@") or channel.startswith("-100")):
        update.message.reply_text("⚠️ Invalid format. Use @channelname or -100...")
        return

    if channel not in channel_daily_content:
        update.message.reply_text(f"❌ No content found for {channel}. Please define it in the code.")
        return

    if channel not in channel_ids:
        channel_ids.add(channel)
        update.message.reply_text(f"✅ Channel {channel} added and scheduled!")
        schedule_for_channel(channel)
    else:
        update.message.reply_text(f"ℹ️ Channel {channel} is already scheduled.")

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Welcome! Use /add_channel @channelname to begin scheduling.")

# Bot runner
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
