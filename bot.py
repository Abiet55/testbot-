import logging
from typing import Optional, cast
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.error import Conflict
from config import BOT_TOKEN
from handlers import (
    start,
    help_command,
    menu,
    handle_callback,
    handle_feedback,
    handle_admin_approval,
    edit_price,
    handle_edit_price
)

# Enhanced logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

async def error_handler(update: Optional[object], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Extract chat_id from update, if available
    chat_id = None
    if isinstance(update, Update) and update.effective_chat:
        chat_id = update.effective_chat.id

    if isinstance(context.error, Conflict):
        logger.warning(f"Conflict error occurred for chat_id {chat_id}, another instance might be running")
        return

    # For any other errors, we want to inform the user
    if chat_id:
        try:
            text = "Sorry, I encountered an error while processing your request. Please try again later."
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("editprice", edit_price))
    application.add_handler(MessageHandler(filters.Regex(r'^/editprice\s+"[^"]+"\s+\d+(?:\.\d{1,2})?$'), handle_edit_price))

    # Admin approval handler should be first to handle approval callbacks
    application.add_handler(CallbackQueryHandler(handle_admin_approval, pattern="^(approve|reject)_"))
    # Add payment confirmation handler
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="^(confirm_payment_|cancel_payment)"))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling(drop_pending_updates=True)
    logger.info("Bot stopped.")

if __name__ == '__main__':
    main()