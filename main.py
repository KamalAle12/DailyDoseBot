from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz
import logging

# Enable logging to help with debugging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = '8159912327:AAH4ZC8GX1EYfTip_gZqR_ES_KpkuQGPykQ'
user_chat_id = None

# List of 30 (message, image_url) pairs
daily_content = [
    ("Day 1: Stay positive!", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    ("Day 2: Keep learning.", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    ("Day 3: You're doing great!", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    ("Day 4: Believe in yourself!", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    ("Day 5: Make today count!", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    ("Day 6: Make today count!", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    ("Day 7: Make today count!", "https://www.recordnet.com/gcdn/presto/2021/03/22/NRCD/9d9dd9e4-e84a-402e-ba8f-daa659e6e6c5-PhotoWord_003.JPG?width=660&height=425&fit=crop&format=pjpg&auto=webp"),
    # Add remaining days here...
]

# Function to send a specific day's message and image
def send_daily_content(chat_id, text, image, **kwargs):
    # Use the bot from the context, which is more efficient than creating a new one each time
    bot = kwargs['context'].bot
    try:
        bot.send_photo(chat_id=chat_id, photo=image, caption=text)
        logging.info(f"Message sent to {chat_id}: {text}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# Command handler for /start
def start(update: Update, context: CallbackContext):
    global user_chat_id
    user_chat_id = update.message.chat_id
    update.message.reply_text("Scheduled your 30 days of messages at 10:15 PM IST!")

    # Set timezone
    tz = pytz.timezone('Asia/Kolkata')
    scheduler = BackgroundScheduler(timezone=tz)
    scheduler.start()

    # Schedule each message at 10:15 PM for 30 days
    for i in range(len(daily_content)):
        run_date = datetime.now(tz).date() + timedelta(days=i)
        run_time = tz.localize(datetime.combine(run_date, datetime.strptime("22:15", "%H:%M").time()))
        
        # Log the scheduled time to verify if the time is correct
        logging.info(f"Scheduled time for Day {i+1}: {run_time}")
        
        scheduler.add_job(
            send_daily_content,
            'date',
            run_date=run_time,
            kwargs={
                'chat_id': user_chat_id,
                'text': daily_content[i][0],
                'image': daily_content[i][1],
                'context': context  # Pass the context so the bot is reused
            }
        )

# Main entry point
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    
    # Ensure scheduler runs in background
    logging.info("Starting bot...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
