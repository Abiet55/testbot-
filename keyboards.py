from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import SERVICES, PAYMENT_METHODS

def get_services_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="📱 Telegram Premium", callback_data="telegram_premium")],
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="telegram_stars")],
        [InlineKeyboardButton(text="↩️ Back to Main Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_premium_duration_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="1️⃣ 1 Month - 1000", callback_data="premium_1month")],
        [InlineKeyboardButton(text="3️⃣ 3 Months - 2000", callback_data="premium_3months")],
        [InlineKeyboardButton(text="6️⃣ 6 Months - 5000", callback_data="premium_6months")],
        [InlineKeyboardButton(text="🗓️ 1 Year - 8000", callback_data="premium_1year")],
        [InlineKeyboardButton(text="↩️ Back", callback_data="back_to_services")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_methods_keyboard():
    keyboard = [
        [InlineKeyboardButton(text=method, callback_data=f"payment_{method}")]
        for method in PAYMENT_METHODS
    ]
    keyboard.append([InlineKeyboardButton(text="↩️ Back to Main Menu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_payment_confirmation_keyboard(payment_method: str, order_id: str):
    keyboard = [
        [InlineKeyboardButton(text="✅ I've Made the Payment", callback_data=f"confirm_payment_{payment_method}_{order_id}")],
        [InlineKeyboardButton(text="❌ Cancel Payment", callback_data="cancel_payment")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_approval_keyboard(item_id: str, item_type: str):
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{item_type}_{item_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject_{item_type}_{item_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="🛍️ Place Order", callback_data="place_order")],
        [InlineKeyboardButton(text="📋 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton(text="💬 Submit Feedback", callback_data="submit_feedback")]
    ]
    return InlineKeyboardMarkup(keyboard)