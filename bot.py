import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.environ["TELEGRAM_TOKEN"]
ADMIN_ID = 8649249738

TARGET, REASON, DETAILS = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ Scam Reporter\n\n"
        "سلام 👋\n"
        "برای ثبت گزارش اکانت مشکوک، روی /report بزن.\n\n"
        "دستورها:\n"
        "/report - ثبت گزارش\n"
        "/cancel - لغو گزارش"
    )


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔎 مرحله ۱ از ۳\n\n"
        "لینک یا @username اکانت موردنظر را ارسال کن."
    )
    return TARGET


async def get_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["target"] = update.message.text

    await update.message.reply_text(
        "📝 مرحله ۲ از ۳\n\n"
        "دلیل گزارش را بنویس.\n\n"
        "مثلاً:\n"
        "• کلاهبرداری\n"
        "• جعل هویت\n"
        "• فروش جعلی\n"
        "• لینک مشکوک"
    )

    return REASON


async def get_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["reason"] = update.message.text

    await update.message.reply_text(
        "📄 مرحله ۳ از ۳\n\n"
        "اگر توضیح یا مدرک بیشتری داری، بنویس.\n"
        "اگر نداری، بنویس «ندارم»."
    )

    return DETAILS


async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    target = context.user_data.get("target", "نامشخص")
    reason = context.user_data.get("reason", "نامشخص")
    details = update.message.text

    report_text = (
        "🚨 گزارش جدید\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🎯 اکانت گزارش‌شده:\n{target}\n\n"
        f"⚠️ دلیل:\n{reason}\n\n"
        f"📄 توضیحات:\n{details}\n\n"
        "👤 گزارش‌دهنده:\n"
        f"ID: {user.id}\n"
        f"Username: @{user.username if user.username else 'ندارد'}\n"
        f"Name: {user.full_name}\n"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=report_text
    )

    await update.message.reply_text(
        "✅ گزارش با موفقیت ثبت شد.\n\n"
        "گزارش برای بررسی ارسال شد."
    )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ گزارش لغو شد."
    )

    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("report", report)
        ],
        states={
            TARGET: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_target
                )
            ],
            REASON: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_reason
                )
            ],
            DETAILS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_details
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()