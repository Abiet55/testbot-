import os

# Telegram Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Admin user IDs (replace with actual admin Telegram IDs)
# To get your Telegram ID:
# 1. Start a chat with @userinfobot on Telegram
# 2. The bot will reply with your user ID
# 3. Copy that ID and replace it in the list below
ADMIN_IDS = [7715819534]  # Admin Telegram user ID

# Available services and their prices
SERVICES = {
    "Telegram Premium - 1 Month": 1000,
    "Telegram Premium - 3 Months": 2000,
    "Telegram Premium - 6 Months": 5000,
    "Telegram Premium - 1 Year": 8000,
    "Telegram Stars": 2000
}

# Payment methods
PAYMENT_METHODS = ["TeleBirr", "CBE"]

# Order statuses
STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_COMPLETED = "completed"