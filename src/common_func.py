from database import *
from customization import regen_avatar
import os
import random
from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
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

    if not check_if_user_exists(user_id):
        con = create_connection('../db/database.db')
        create_users = f"""
        INSERT INTO
        users (id, username)
        VALUES
        ('{user_id}', '{username}');
        """
        execute_query(con, create_users)
        regen_avatar(user_id)

        con.close()


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['/custom', '/game'], ['/fight', '/help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите команду:",
                                   reply_markup=reply_markup)
    return ConversationHandler.END


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username
    request = f"SELECT personal_username, game_class, exp FROM users WHERE id={user_id}"
    db_data = execute_read_query(con, request)
    message = "Ваш профиль:\n\n" \
              f"Игровое имя: {db_data[0][0]}\n" \
              f"ID: {user_id}\n" \
              f"Имя Telegram: {username}\n" \
              f"Ваш класс: {db_data[0][1]}\n" \
              f"Опыт: {db_data[0][2]}"
    await context.bot.send_photo(chat_id=update.effective_chat.id, caption=message, photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'), 'rb'))
    con.close()


async def help_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Вот доступные команды:\n\n" \
              "/start - Начало использования бота\n" \
              "/help - Просмотр доступных команд\n" \
              "/custom - Настройка вашего игрового персонажа\n" \
              "/upgrade - Улучшайте своего персонажа с помощью реальных событий или внутриигровыми способами\n" \
              "/fight - Сражайтесь с другими игроками в чате"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Чтобы улучшить своего персонажа, участвуйте в реальных событиях или выполняйте внутриигровые задания. Более подробная информация скоро появится!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Чтобы сразиться с другими игроками, отправьте мне прямое сообщение с именем пользователя вашего противника и начинайте битву! Более подробная информация скоро появится."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def danet(update: Update, context: ContextTypes.DEFAULT_TYPE):  # не забыть бы удалить
    message = "пизда"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def netda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "пидора ответ"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rand = random.randint(1, 9)
    photo = [InputMediaPhoto(open(os.path.abspath('../res/meme/meme_' + str(rand) + '.jpg'), 'rb'))]
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=photo)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Не понял нихуя"
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Хуйня")
