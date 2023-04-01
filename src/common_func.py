from database import *
from customization import regen_avatar
import os
import random
from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)


# This function takes a user ID as input and returns the rank of the user based on their experience points,
# using a pre-selected table of ranks. It assumes that the ranks table is ordered by the exp_to_earn column. If the
# user's experience points are greater than the highest rank, the function returns the highest rank.
def get_rank(user_id):
    user_exp = get_user_exp(user_id)
    ranks = select_ranks_table()
    # Relies on the fact that ranks variable is ordered by exp_to_earn column
    for i in range(1, len(ranks)):
        if ranks[i][1] > user_exp:
            return ranks[i - 1][0]
    return ranks[len(ranks) - 1][0]


# This function takes a user ID and a required amount of experience points as input and returns a boolean indicating
# whether the user has at least the required amount of experience points. It returns True if the user has at least
# the required amount, and False otherwise.
def is_available(user_id, required_exp):
    con = create_connection('../db/database.db')
    request = f"SELECT exp FROM users WHERE id={user_id}"
    user_exp = execute_read_query(con, request)
    con.close()
    return int(user_exp[0][0]) >= required_exp


# This is a function that updates the experience points of a user in the database. It takes in two arguments,
# the user_id of the user whose experience points need to be updated and the amount of experience points to add. It
# fetches the current experience points of the user from the database, adds the new experience points to it,
# and then updates the database with the new experience points.
def add_exp(user_id, exp):
    con = create_connection('../db/database.db')
    request = f"SELECT exp FROM users WHERE id={user_id}"
    db_data = execute_read_query(con, request)
    con.close()
    inserter('exp', int(db_data[0][0]) + exp, user_id)


# This function that sends a welcome message to the user and then checks if the user exists in the database. If the
# user does not exist, the function creates a connection to a database, executes an SQL query to insert the user's ID
# and username (if available) into a users table, generates an avatar for the user, and then closes the connection.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await context.bot.send_message(chat_id=user_id,
                                   text="Добро пожаловать в Team Builder Bot! Введите /help, чтобы просмотреть "
                                        "доступные команды.")
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    message = update.message
    user = message.from_user
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


# This is a temporary solution. It will have to be deleted!
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['/custom', '/game'], ['/fight', '/help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.message.from_user.id,
                                   text="Выберите команду:",
                                   reply_markup=reply_markup)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    return ConversationHandler.END


# This function that retrieves user data from a database, generates a message containing the user's profile
# information (including personal username, Telegram username, subclass, rank, class, and experience points),
# sends the message along with the user's avatar, and then deletes the message that triggered the function.
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username
    request = f"SELECT personal_username, game_class, exp, game_subclass FROM users WHERE id={user_id}"
    db_data = execute_read_query(con, request)
    message = "Ваш профиль:\n\n" \
              f"Игровое имя: {db_data[0][0]}\n" \
              f"ID: {user_id}\n" \
              f"Имя Telegram: {username}\n" \
              f"Подкласс: {db_data[0][3]}\n" \
              f"Ранг: {get_rank(user_id)}\n" \
              f"Ваш класс: {db_data[0][1]}\n" \
              f"Опыт: {db_data[0][2]}"
    await context.bot.send_photo(chat_id=user_id, caption=message,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    con.close()


# Function retrieves events from the database and formats them as an HTML-formatted string before sending them as a
# message to the Telegram chat. It uses the create_connection() function to connect to the database, executes a SQL
# query to select all the events in the global_events table and order them by their start time. Then it loops through
# the results and formats each event's data as an HTML string.
async def get_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    query = """
        SELECT * FROM global_events
        ORDER BY start_time
    """
    res = execute_read_query(con, query)
    con.close()
    events = ""
    for row in res:
        event = f"<b>{row[1]}</b>\n"
        event += f"<i>{row[2]}</i>\n"
        event += f"<u>Start time:</u> {row[3]}\n"
        event += f"<u>Duration:</u> {row[4]}\n"
        event += f"<u>Participants:</u> {row[5]}\n"
        event += f"<u>Experience reward:</u> {row[6]}\n"
        events += event + "\n"
    con.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')


# This function sends a message to the user with the available commands for the bot. It  sends a message containing a
# list of commands that the user can enter.
async def help_me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Вот доступные команды:\n\n" \
              "/start - Начало использования бота\n" \
              "/help - Просмотр доступных команд\n" \
              "/custom - Настройка вашего игрового персонажа"
    await context.bot.send_message(chat_id=update.message.from_user.id, text=message)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


async def danet(update: Update, context: ContextTypes.DEFAULT_TYPE):  # не забыть бы удалить
    message = "пизда"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def netda(update: Update, context: ContextTypes.DEFAULT_TYPE):  # и это
    message = "пидора ответ"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


# Требуемая функция на этапе разработки, потом нужно будет убрать
async def del_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Клавиатура удалена!',
                                   reply_markup=ReplyKeyboardRemove())


# Не уверен, что нам нужно существование этой функции, но в принципе потом уберём
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rand = random.randint(1, 9)
    photo = [InputMediaPhoto(open(os.path.abspath('../res/meme/meme_' + str(rand) + '.jpg'), 'rb'))]
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=photo)
