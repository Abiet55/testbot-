import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import (
    ADMIN_IDS, SERVICES, STATUS_PENDING, STATUS_APPROVED,
    STATUS_REJECTED
)
import re
from storage import Storage
from keyboards import (
    get_services_keyboard,
    get_payment_methods_keyboard,
    get_admin_approval_keyboard,
    get_main_menu_keyboard,
    get_premium_duration_keyboard,
    get_payment_confirmation_keyboard
)
from datetime import datetime

logger = logging.getLogger(__name__)

storage = Storage()

async def is_admin(user_id: int, context: ContextTypes.DEFAULT_TYPE = None) -> bool:
    is_admin = user_id in ADMIN_IDS
    if context and not is_admin:
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ You are not authorized to perform this action. Please contact an administrator."
        )
    return is_admin

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to our Service Bot! 🤖\n"
        "Use /menu to see available options or /help for assistance.",
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Available commands:
/start - Start the bot
/menu - Show main menu
/help - Show this help message

Use the buttons below to navigate through the bot's features.
"""
    await update.message.reply_text(help_text)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please select an option:",
        reply_markup=get_main_menu_keyboard()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "place_order":
        await query.message.edit_text(
            "🛍️ Please select a service:",
            reply_markup=get_services_keyboard()
        )

    elif query.data == "telegram_premium":
        await query.message.edit_text(
            "🌟 Telegram Premium Subscription\n"
            "━━━━━━━━━━━━━━━\n"
            "Choose your preferred subscription duration:\n\n"
            "All plans include:\n"
            "• Premium stickers and reactions\n"
            "• 4GB file uploads\n"
            "• Faster downloads\n"
            "• Voice-to-text conversion\n"
            "• Ad-free experience\n"
            "• Unique badge and profile features\n\n"
            "Select a plan that suits you best:",
            reply_markup=get_premium_duration_keyboard()
        )

    elif query.data.startswith("premium_"):
        duration = query.data.replace("premium_", "")
        duration_display = {
            "1month": "1 Month",
            "3months": "3 Months",
            "6months": "6 Months",
            "1year": "1 Year"
        }

        service_name = f"Telegram Premium - {duration_display[duration]}"
        order_id = storage.create_order(query.from_user.id, service_name)
        price = SERVICES.get("Telegram Premium", 1000) #Updated price logic

        await query.message.edit_text(
            f"✨ Telegram Premium Order Created!\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📋 Order Details:\n"
            f"🔖 Order ID: {order_id}\n"
            f"📦 Package: Telegram Premium\n"
            f"⏳ Duration: {duration_display[duration]}\n"
            f"💰 Price: ${price}\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"Your order will be reviewed shortly.\n"
            f"We'll notify you once it's approved!",
            reply_markup=get_main_menu_keyboard()
        )

        # Notify admins about the new premium order
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🔔 New Premium Subscription Order\n"
                     f"━━━━━━━━━━━━━━━\n"
                     f"🔖 Order ID: {order_id}\n"
                     f"👤 User ID: {query.from_user.id}\n"
                     f"📦 Package: Telegram Premium\n"
                     f"⏳ Duration: {duration_display[duration]}\n"
                     f"💰 Price: ${price}\n"
                     f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                     f"━━━━━━━━━━━━━━━\n"
                     f"Please review and take action:",
                reply_markup=get_admin_approval_keyboard(order_id, "order")
            )
            logger.info(f"Sent premium order approval request to admin {admin_id} for order {order_id}")

    elif query.data.startswith("confirm_payment_"):
        parts = query.data.split("_", 3)  # confirm_payment_method_orderid
        if len(parts) == 4:
            _, _, payment_method, order_id = parts
            order = storage.get_order(order_id)

            if order:
                # Update the message to show confirmation
                await query.message.edit_text(
                    f"✅ Payment Confirmation Received!\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"Thank you for confirming your payment. Our team will verify the payment and process your order shortly.\n\n"
                    f"Order Details:\n"
                    f"🔖 Order ID: {order_id}\n"
                    f"🛠️ Service: {order['service']}\n"
                    f"💳 Payment Method: {payment_method}\n"
                    f"━━━━━━━━━━━━━━━",
                    reply_markup=get_main_menu_keyboard()
                )

                # Notify admin about payment confirmation
                for admin_id in ADMIN_IDS:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"💰 Payment Confirmation Received\n"
                             f"━━━━━━━━━━━━━━━\n"
                             f"🔖 Order ID: {order_id}\n"
                             f"👤 User ID: {query.from_user.id}\n"
                             f"🛠️ Service: {order['service']}\n"
                             f"💳 Method: {payment_method}\n"
                             f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                             f"━━━━━━━━━━━━━━━\n"
                             f"Please verify the payment and process the order."
                    )
                    logger.info(f"Payment confirmation sent to admin {admin_id} for order {order_id}")

    elif query.data == "cancel_payment":
        await query.message.edit_text(
            "❌ Payment Cancelled\n"
            "━━━━━━━━━━━━━━━\n"
            "You can try again or choose a different payment method from the main menu.",
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "back_to_services":
        await query.message.edit_text(
            "🛍️ Please select a service:",
            reply_markup=get_services_keyboard()
        )

    elif query.data == "back_to_menu":
        await query.message.edit_text(
            "Please select an option:",
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "place_order":
        await query.message.edit_text(
            "🛍️ Please select a service:",
            reply_markup=get_services_keyboard()
        )

    elif query.data == "telegram_stars":
        await query.message.edit_text(
            "⭐ Telegram Stars Program\n"
            "━━━━━━━━━━━━━━━\n"
            "🏆 Exclusive Benefits:\n"
            "• Special member badge\n"
            "• Priority customer support\n"
            "• Early access to new features\n"
            "• Monthly rewards\n"
            "• Community spotlight\n"
            "• Exclusive events access\n\n"
            "🚀 Program launch coming soon!",
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "my_orders":
        user_id = query.from_user.id
        pending_orders = storage.get_user_pending_orders(user_id)
        all_orders = storage.get_user_orders(user_id)

        if not all_orders:
            await query.message.edit_text(
                "📭 You don't have any orders yet.\nUse the menu below to place your first order!",
                reply_markup=get_main_menu_keyboard()
            )
            return

        message = "📋 Your Orders Summary:\n\n"

        # First show pending orders
        if pending_orders:
            message += "🕒 PENDING ORDERS:\n"
            message += "━━━━━━━━━━━━━━━\n"
            for order_id, order in pending_orders.items():
                message += f"🔖 ID: {order_id}\n"
                message += f"🛠️ Service: {order['service']}\n"
                message += "⏳ Status: Awaiting Admin Approval\n"
                message += "━━━━━━━━━━━━━━━\n"

        # Then show other orders
        other_orders = {k: v for k, v in all_orders.items() if k not in pending_orders}
        if other_orders:
            if pending_orders:  # Add spacing if we had pending orders
                message += "\n"
            message += "📝 OTHER ORDERS:\n"
            message += "━━━━━━━━━━━━━━━\n"
            for order_id, order in other_orders.items():
                message += f"🔖 ID: {order_id}\n"
                message += f"🛠️ Service: {order['service']}\n"
                status_emoji = "✅" if order['status'] == STATUS_APPROVED else "❌" if order['status'] == STATUS_REJECTED else "⏳"
                message += f"Status: {status_emoji} {order['status'].upper()}\n"
                if order['payment_method']:
                    message += f"💳 Payment: {order['payment_method']}\n"
                message += "━━━━━━━━━━━━━━━\n"

        await query.message.edit_text(
            message,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data.startswith("payment_"):
        payment_method = query.data.replace("payment_", "")
        user_id = query.from_user.id
        order_id = storage.get_user_session(user_id, "current_order")

        if order_id and storage.update_payment_method(order_id, payment_method):
            order = storage.get_order(order_id)

            # Customize message based on payment method
            payment_details = ""
            if payment_method == "TeleBirr":
                payment_details = (
                    f"\nTeleBirr Payment Details:\n"
                    f"📱 Phone Number: 096139850\n"
                    f"👤 Name: Abdisa Feleke\n"
                )
            if payment_method == "CBE":
                payment_details = (
                    f"\nCBE Payment Details:\n"
                    f"📱 Phone Number: 010000006623\n"
                    f"👤 Name: Abdisa Feleke\n"
                )

            await query.message.edit_text(
                f"💫 Payment Method Selected\n\n"
                f"Order Details:\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔖 Order ID: {order_id}\n"
                f"🛠️ Service: {order['service']}\n"
                f"💳 Payment Method: {payment_method}\n"
                f"✅ Status: {order['status'].upper()}\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{payment_details}\n"
                f"Please make the payment using the details above and click 'I've Made the Payment' once completed.",
                reply_markup=get_payment_confirmation_keyboard(payment_method, order_id)
            )

        else:
            await query.message.edit_text(
                "❌ Sorry, there was an error processing your payment method selection. Please try again.",
                reply_markup=get_main_menu_keyboard()
            )

    elif query.data.startswith("confirm_payment_"):
        parts = query.data.split("_", 3)  # confirm_payment_method_orderid
        if len(parts) == 4:
            _, _, payment_method, order_id = parts
            order = storage.get_order(order_id)

            if order:
                await query.message.edit_text(
                    f"✅ Payment Confirmation Received!\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"Thank you for confirming your payment. Our team will verify the payment and process your order shortly.\n\n"
                    f"Order Details:\n"
                    f"🔖 Order ID: {order_id}\n"
                    f"🛠️ Service: {order['service']}\n"
                    f"💳 Payment Method: {payment_method}\n"
                    f"━━━━━━━━━━━━━━━",
                    reply_markup=get_main_menu_keyboard()
                )

                # Notify admin about payment confirmation
                for admin_id in ADMIN_IDS:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"💰 Payment Confirmation Received\n"
                             f"━━━━━━━━━━━━━━━\n"
                             f"🔖 Order ID: {order_id}\n"
                             f"👤 User ID: {query.from_user.id}\n"
                             f"🛠️ Service: {order['service']}\n"
                             f"💳 Method: {payment_method}\n"
                             f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                             f"━━━━━━━━━━━━━━━\n"
                             f"Please verify the payment and process the order."
                    )
                    logger.info(f"Payment confirmation sent to admin {admin_id} for order {order_id}")

    elif query.data == "cancel_payment":
        await query.message.edit_text(
            "❌ Payment Cancelled\n"
            "━━━━━━━━━━━━━━━\n"
            "You can try again or choose a different payment method from the main menu.",
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data.startswith("service_"):
        service = query.data.replace("service_", "")
        order_id = storage.create_order(query.from_user.id, service)
        price = SERVICES.get(service, 0)

        pending_orders = storage.get_user_pending_orders(query.from_user.id)
        message = "🎉 NEW ORDER CREATED!\n"
        message += "━━━━━━━━━━━━━━━\n\n"
        message += "📋 Order Details:\n"
        message += f"🔖 ID: {order_id}\n"
        message += f"🛠️ Service: {service}\n"
        message += f"💰 Price: ${price}\n"
        message += "⏳ Status: Awaiting Admin Approval\n\n"

        if len(pending_orders) > 1:  # More than just the current order
            message += "📑 YOUR OTHER PENDING ORDERS:\n"
            message += "━━━━━━━━━━━━━━━\n"
            for p_order_id, order in pending_orders.items():
                if p_order_id != order_id:  # Don't show the current order again
                    message += f"🔖 ID: {p_order_id}\n"
                    message += f"🛠️ Service: {order['service']}\n"
                    message += "⏳ Status: Awaiting Admin Approval\n"
                    message += "━━━━━━━━━━━━━━━\n"

            message += "\n✨ We'll notify you when your orders are reviewed!"

        await query.message.edit_text(
            message,
            reply_markup=get_main_menu_keyboard()
        )

        # Notify admins about the new order
        for admin_id in ADMIN_IDS:
            # Get the correct price based on the service type
            service_price = SERVICES.get(service, 0)
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"🔔 New Order Requires Approval\n"
                     f"━━━━━━━━━━━━━━━\n"
                     f"🔖 Order ID: {order_id}\n"
                     f"👤 User ID: {query.from_user.id}\n"
                     f"🛠️ Service: {service}\n"
                     f"💰 Price: ${service_price}\n"
                     f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                     f"━━━━━━━━━━━━━━━\n"
                     f"Please review and take action:",
                reply_markup=get_admin_approval_keyboard(order_id, "order")
            )
            logger.info(f"Sent order approval request to admin {admin_id} for order {order_id}")

    elif query.data.startswith("approve_"):
        parts = query.data.split("_",2)
        if len(parts) != 3:
            logger.error(f"Invalid callback data format: {query.data}")
            await query.message.edit_text(
                "❌ Error: Invalid approval format",
                reply_markup=None
            )
            return
        action, item_type, item_id = parts
        if item_type == "order":
            order = storage.get_order(item_id)
            if action == "approve":
                storage.update_order_status(item_id, STATUS_APPROVED)
                await context.bot.send_message(
                    chat_id=order["user_id"],
                    text=f"Your order {item_id} has been approved!\nPlease select a payment method:",
                    reply_markup=get_payment_methods_keyboard()
                )
                storage.set_user_session(order["user_id"], "current_order", item_id)
            else:
                storage.update_order_status(item_id, STATUS_REJECTED)
                await context.bot.send_message(
                    chat_id=order["user_id"],
                    text=f"Your order {item_id} has been rejected."
                )
        elif item_type == "feedback":
            storage.update_feedback_status(item_id, "approved" if action == "approve" else "rejected")
            # Add handling for feedback approval/rejection here if needed

        await query.message.edit_text(
            f"{item_type.capitalize()} has been {action}d.",
            reply_markup=None
        )

async def handle_admin_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not await is_admin(user_id, context):
        logger.warning(f"⚠️ Unauthorized admin action attempt by user {user_id}")
        return

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        logger.error(f"Invalid callback data format: {query.data}")
        await query.message.edit_text(
            "❌ Error: Invalid approval format",
            reply_markup=None
        )
        return

    action, item_type, item_id = parts
    logger.info(f"Admin {user_id} performing {action} on {item_type} {item_id}")

    if item_type == "order":
        order = storage.get_order(item_id)
        if not order:
            logger.error(f"Order {item_id} not found for admin approval")
            await query.message.edit_text(
                "❌ Error: Order not found",
                reply_markup=None
            )
            return

        if action == "approve":
            storage.update_order_status(item_id, STATUS_APPROVED)
            price = SERVICES.get(order['service'], 0)

            await context.bot.send_message(
                chat_id=order["user_id"],
                text=f"🎉 Congratulations! Your Order Has Been Approved!\n"
                     f"━━━━━━━━━━━━━━━\n"
                     f"🔖 Order ID: {item_id}\n"
                     f"🛠️ Service: {order['service']}\n"
                     f"💰 Price: ${price}\n"
                     f"✅ Status: APPROVED\n"
                     f"━━━━━━━━━━━━━━━\n\n"
                     f"📝 Next Steps:\n"
                     f"1. Choose your preferred payment method (TeleBirr or CBE)\n"
                     f"2. We'll process your order once payment is confirmed\n\n"
                     f"Please select your payment method:",
                reply_markup=get_payment_methods_keyboard()
            )
            storage.set_user_session(order["user_id"], "current_order", item_id)
            logger.info(f"Order {item_id} approved by admin {user_id}")
        else:
            storage.update_order_status(item_id, STATUS_REJECTED)
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=f"❌ Order Update\n"
                     f"━━━━━━━━━━━━━━━\n"
                     f"🔖 Order ID: {item_id}\n"
                     f"🛠️ Service: {order['service']}\n"
                     f"Status: REJECTED\n"
                     f"━━━━━━━━━━━━━━━\n\n"
                     f"You can place a new order from the main menu.",
                reply_markup=get_main_menu_keyboard()
            )
            logger.info(f"Order {item_id} rejected by admin {user_id}")

        # Update admin's message
        admin_response = "✅" if action == "approve" else "❌"
        await query.message.edit_text(
            f"{admin_response} Order {item_id} has been {action}d successfully.",
            reply_markup=None
        )

    elif item_type == "feedback":
        try:
            feedback_id = int(item_id)
            status = "approved" if action == "approve" else "rejected"
            if storage.update_feedback_status(feedback_id, status):
                await query.message.edit_text(
                    f"✅ Feedback #{feedback_id} has been {status}.",
                    reply_markup=None
                )
                logger.info(f"Feedback {feedback_id} {status} by admin {user_id}")
            else:
                await query.message.edit_text(
                    "❌ Error: Feedback not found",
                    reply_markup=None
                )
                logger.error(f"Feedback {feedback_id} not found for admin approval")
        except ValueError:
            logger.error(f"Invalid feedback ID format: {item_id}")
            await query.message.edit_text(
                "❌ Error: Invalid feedback ID",
                reply_markup=None
            )

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    feedback_text = update.message.text

    feedback_id = storage.add_feedback(user_id, feedback_text)

    await update.message.reply_text(
        "Thank you for your feedback! It will be reviewed by our administrators."
    )

    # Notify admins
    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"New feedback requires approval:\nUser ID: {user_id}\n"
                 f"Feedback: {feedback_text}",
            reply_markup=get_admin_approval_keyboard(str(feedback_id), "feedback")
        )

async def edit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.message.from_user.id, context):
        return
    
    from config import SERVICES
    services_text = "Current Premium Prices:\n\n"
    for service, price in SERVICES.items():
        if service.startswith("Telegram Premium"):
            services_text += f"- {service}: ${price}\n"
    
    services_text += "\nTo edit a price, use the format:\n"
    services_text += '/editprice "Telegram Premium - [Duration]" [New Price]\n'
    services_text += 'Example: /editprice "Telegram Premium - 1 Month" 1500'
    
    await update.message.reply_text(services_text)

async def handle_edit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update.message.from_user.id, context):
        return

    text = update.message.text.strip()
    if text == "/editprice":
        await edit_price(update, context)
        return
        
    match = re.match(r'/editprice\s+"([^"]+)"\s+(\d+(?:\.\d{1,2})?)', text)
    
    if not match:
        await update.message.reply_text(
            "❌ Invalid format. Use:\n"
            '/editprice "Telegram Premium - Duration" price\n'
            'Example: /editprice "Telegram Premium - 1 Month" 1500\n\n'
            'Available durations:\n'
            '- Telegram Premium - 1 Month\n'
            '- Telegram Premium - 3 Months\n'
            '- Telegram Premium - 6 Months\n'
            '- Telegram Premium - 1 Year'
        )
        return
        
    service_name, new_price = match.groups()
    new_price = float(new_price)
    
    valid_services = [
        "Telegram Premium - 1 Month",
        "Telegram Premium - 3 Months", 
        "Telegram Premium - 6 Months",
        "Telegram Premium - 1 Year"
    ]
    
    if service_name in valid_services:
        try:
            import config
            config.SERVICES[service_name] = new_price
            
            success_text = f"✅ Price updated successfully!\n\n"
            success_text += f"Service: {service_name}\n"
            success_text += f"New Price: ${new_price}\n\n"
            success_text += "Current Prices:\n"
            
            for service in valid_services:
                price = config.SERVICES.get(service, 0)
                success_text += f"• {service}: ${price}\n"
                
            await update.message.reply_text(success_text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error updating price: {str(e)}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error updating price: {str(e)}")
    else:
        await update.message.reply_text(
            "❌ Invalid premium duration. Please use the exact format:\n\n"
            '/editprice "Telegram Premium - 1 Month" [price]\n'
            '/editprice "Telegram Premium - 3 Months" [price]\n'
            '/editprice "Telegram Premium - 6 Months" [price]\n'
            '/editprice "Telegram Premium - 1 Year" [price]'
        )