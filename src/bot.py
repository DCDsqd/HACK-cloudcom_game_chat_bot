import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import sqlite3
from sqlite3 import Error

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
    message = "Чтобы настроить своего игрового персонажа, отправьте мне прямое сообщение с желаемым ником."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Чтобы улучшить своего персонажа, участвуйте в реальных событиях или выполняйте внутриигровые задания. Более подробная информация скоро появится!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    
async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Чтобы сразиться с другими игроками, отправьте мне прямое сообщение с именем пользователя вашего противника и начинайте битву! Более подробная информация скоро появится."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

if __name__ == '__main__':
    token_file = open("../tokens/tg_app_token.txt", "r")
    application = ApplicationBuilder().token(token_file.read()).build() # надеюсь тут тоже не переебет
    token_file.close()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('custom', custom))
    application.add_handler(CommandHandler('upgrade', upgrade))
    application.add_handler(CommandHandler('fight', fight))
    
    application.run_polling()