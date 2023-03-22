import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import sqlite3
from sqlite3 import Error

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY = range(4)


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добро пожаловать в Team Builder Bot! Введите /help, чтобы просмотреть доступные команды.")
    message = update.message
    user = message.from_user
    user_id = message.from_user.id
    if user.username:
        username = user.username
    else:
        username = None
    create_users = f"""
    INSERT INTO
      users (id, username)
    VALUES
      ('{user_id}', '{username}');
    """
    con = create_connection('../db/database.db')  # perhaps здесь переебет, не уверен что так можно... (ненавижу питон)
    # ну кстати, не переебало
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL, 
      personal_username TEXT
    );
    """
    execute_query(con, create_users_table)
    execute_query(con, create_users)
    con.close()


async def help_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Вот доступные команды:\n\n" \
              "/start - Начало использования бота\n" \
              "/help - Просмотр доступных команд\n" \
              "/custom - Настройка вашего игрового персонажа\n" \
              "/upgrade - Улучшайте своего персонажа с помощью реальных событий или внутриигровыми способами\n" \
              "/fight - Сражайтесь с другими игроками в чате"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


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
    else:
        await update.message.reply_text("Я не понимаю, что вы хотите. Пожалуйста, выберите из меню.")
        return TYPING_CHOICE


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
    return ConversationHandler.END


async def custom_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Чтобы улучшить своего персонажа, участвуйте в реальных событиях или выполняйте внутриигровые задания. Более подробная информация скоро появится!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Чтобы сразиться с другими игроками, отправьте мне прямое сообщение с именем пользователя вашего противника и начинайте битву! Более подробная информация скоро появится."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


if __name__ == '__main__':
    token_file = open("../tokens/tg_app_token.txt", "r")
    application = ApplicationBuilder().token(token_file.read()).build()
    token_file.close()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_me))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("custom", custom)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Изменить имя$"), custom_name_choice),
                MessageHandler(filters.Regex('^Изменить аватара$'), custom_avatar),
            ],
            TYPING_CHOICE: [MessageHandler(filters=filters.Regex('^Изменить волосы$'),  # Пока что не работает
                                           callback=custom_avatar_choice),
                            MessageHandler(filters=filters.Regex('^Изменить лицо$'),
                                           callback=custom_avatar_choice),
                            MessageHandler(filters=filters.Regex('^Изменить тело$'),
                                           callback=custom_avatar_choice)],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), received_name, )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), custom_cancel)],
    )
    back_to_custom_handler = MessageHandler(filters=filters.Regex("Назад"), callback=custom)
    application.add_handler(back_to_custom_handler, group=1)
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('upgrade', upgrade))
    application.add_handler(CommandHandler('fight', fight))

    application.run_polling()
