import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import sqlite3
from sqlite3 import Error

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать в Team Builder Bot! Введите /help, чтобы просмотреть доступные команды.")
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
    con = create_connection('../db/database.db') # perhaps здесь переебет, не уверен что так можно... (ненавижу питон)
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
    
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
     message = "Вот доступные команды:\n\n" \
              "/start - Начало использования бота\n" \
              "/help - Просмотр доступных команд\n" \
              "/custom - Настройка вашего игрового персонажа\n" \
              "/upgrade - Улучшайте своего персонажа с помощью реальных событий или внутриигровыми способами\n" \
              "/fight - Сражайтесь с другими игроками в чате"
     await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
     
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return CHOOSING

async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["choice"] = text
    if text == "Изменить имя":
        await update.message.reply_text("Введите новое имя:")
        return TYPING_REPLY
    elif text == "Назад":
        return custom_cancel
    else:
        await update.message.reply_text("Я не понимаю, что вы хотите. Пожалуйста, выберите из меню.")
        return CHOOSING

async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    application.add_handler(CommandHandler('help', help))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("custom", custom)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Изменить имя|Изменить Аватара)$"), regular_choice
                ),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), regular_choice # нихуя не работает
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), # как и это
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Назад$"), custom_cancel)], # и это
    )

    application.add_handler(conv_handler) # зато в общем работает

    application.add_handler(CommandHandler('upgrade', upgrade))
    application.add_handler(CommandHandler('fight', fight))
    
    application.run_polling()