from datebase import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from common_func import start, main_menu, profile, help_me, upgrade, fight, danet, netda

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY = range(4)


async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return CHOOSING


async def custom_name_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["choice"] = text
    if text == "Изменить имя":
        await update.message.reply_text("Введите новое имя:")
        return TYPING_REPLY


async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["name"] = text
    user_id = update.message.from_user.id
    con = create_connection('../db/database.db')
    update_name = f"""
        UPDATE users
        SET personal_username = '{text}'
        WHERE id = '{user_id}';
        """
    execute_query(con, update_name)
    con.close()
    await update.message.reply_text(f"Имя изменено на {text}.")
    logging.info(f"User with ID {user_id} changed personal name on {text}")
    return CHOOSING


async def custom_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить волосы", "Изменить лицо", "Изменить тело"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить в аватаре?",
        reply_markup=markup,
    )
    return CHOOSING_AVATAR


async def custom_avatar_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):  # Не работает
    text = update.message.text
    context.user_data["choice"] = text
    if text == "Изменить волосы":
        # Add functionality to select hair image
        await update.message.reply_text("Изменяем волосы...")
        return TYPING_HAIR
    elif text == "Изменить лицо":
        # Add functionality to select face image
        await update.message.reply_text("Изменяем лицо...")
        return TYPING_FACE
    elif text == "Изменить тело":
        # Add functionality to select body image
        await update.message.reply_text("Изменяем тело...")
        return TYPING_BODY
    elif text == "Назад":
        return CHOOSING


if __name__ == '__main__':
    token_file = open("../tokens/tg_app_token.txt", "r")
    application = ApplicationBuilder().token(token_file.read()).build()
    token_file.close()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_me))
    custom_name_handler = ConversationHandler(
        entry_points=[CommandHandler("custom", custom)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Изменить имя$"), custom_name_choice),
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), received_name, )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), main_menu)],
    )
    avatar_handler = ConversationHandler(
        entry_points=[CommandHandler("custom", custom)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex('^Изменить аватара$'), custom_avatar),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Назад$"), custom)],
    )
    application.add_handler(custom_name_handler)
    application.add_handler(avatar_handler)
    application.add_handler(CommandHandler('upgrade', upgrade))
    application.add_handler(MessageHandler(filters.Regex("^Да$|^да$"), danet))
    application.add_handler(MessageHandler(filters.Regex("^Нет$|^нет$"), netda))
    application.add_handler(CommandHandler('menu', main_menu))
    application.add_handler(CommandHandler('fight', fight))
    application.add_handler(CommandHandler('profile', profile))
    application.run_polling()
