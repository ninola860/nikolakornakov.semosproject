import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
FLASK_API_URL = os.getenv('FLASK_API_URL')

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm SEMOS BOT!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here are the available commands:\n"
        "/average_spending_by_age - Get average spending data by age groups.\n"
        "/total_spent/user_id - Get the total spending for a specific user. Replace user_id with the actual ID."
    )
    await update.message.reply_text(help_text)

async def average_spending_by_age_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"{FLASK_API_URL}/average_spending_by_age")
        response.raise_for_status()
        data = response.json()
        
        message = "Average spending by age groups:\n"
        for age_range, avg in data.items():
            message += f"{age_range}: ${avg:.2f}\n"
        
        await update.message.reply_text(message)
    except requests.RequestException as e:
        await update.message.reply_text("Failed to fetch average spending data.")
        print(f"Error fetching average spending data: {e}")

async def total_spent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        print("Received an update with no message or text.")
        return

    print(f"Received command: {update.message.text}")  # Debug line

    text = update.message.text
    if not text.startswith('/total_spent/'):
        await update.message.reply_text("Invalid command format. Use /total_spent/user_id.")
        return

    # Extract user_id from the command
    try:
        user_id = int(text.split('/total_spent/')[1])  # Extract ID after "/total_spent/"
        print(f"Extracted user_id: {user_id}")  # Debug line
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid user ID. Use /total_spent/user_id, where user_id is a number.")
        return

    try:
        response = requests.get(f"{FLASK_API_URL}/total_spent/{user_id}")
        response.raise_for_status()
        data = response.json()

        total_spent = data.get('total_spent', 0)
        message = f"User ID {user_id} has spent a total of ${total_spent:.2f}."
        await update.message.reply_text(message)
    except requests.RequestException as e:
        await update.message.reply_text(f"Failed to fetch total spending for User ID {user_id}.")
        print(f"Error fetching total spending for User ID {user_id}: {e}")

# Main bot setup
if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('average_spending_by_age', average_spending_by_age_command))
    app.add_handler(MessageHandler(filters.Regex(r'^/total_spent/\d+$'), total_spent_command))

    # Polling
    print('Polling...')
    app.run_polling(poll_interval=3)


