from database import *
from customization import regen_avatar
import os
import random
from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto, ReplyKeyboardRemove, Chat
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from admin import parse_new_event_info_string

EVENT_INPUT = range(1)

TOTAL_VOTER_COUNT = 10


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    is_ok, msg = parse_new_event_info_string(text)
    if is_ok:
        questions = ["Да", "Нет"]
        message = await context.bot.send_poll(
            update.effective_chat.id,
            "Поддерживаете ли вы проведение данного мероприятия?",
            questions,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        poll_id = message.poll.id
        con = create_connection('../db/database.db')
        create_users = f"""
                INSERT INTO
                polls (poll_id)
                VALUES
                ('{poll_id}');
                """
        execute_query(con, create_users)
        fields = text.split('\n')
        name = fields[0]
        descr = fields[1]
        start_time = fields[2]
        duration = fields[3]
        exp_reward = fields[4]
        query = f"""
                UPDATE polls SET name='{name}', descr='{descr}', start_time='{start_time}', duration='{duration}', 
                exp_reward='{exp_reward}'
                WHERE poll_id={poll_id};
                """
        execute_query(con, query)
        con.close()
        payload = {
            message.poll.id: {
                "questions": questions,
                "message_id": message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0,
            }
        }
        context.bot_data.update(payload)
    else:
        response = f"Ошибка при создании события!\nКомментарий: {msg}\n\nПопробуйте ещё раз."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    return ConversationHandler.END


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.poll_answer
    poll_id = answer['poll_id']
    option_id = answer['option_ids'][0]
    col = 'for' if option_id == 0 else 'against'
    with create_connection('../db/database.db') as con:
        request = f"SELECT {col} FROM polls WHERE poll_id={poll_id}"
        db_data = execute_read_query(con, request)
        con = create_connection('../db/database.db')
        updater = f"""
                    UPDATE polls
                    SET '{col}' = '{int(db_data[0][0]) + 1}'
                    WHERE poll_id = '{poll_id}';
                    """
        execute_query(con, updater)
    answered_poll = context.bot_data[answer.poll_id]
    try:
        questions = answered_poll["questions"]
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    answered_poll["answers"] += 1
    # Close poll after three participants voted
    if answered_poll["answers"] == TOTAL_VOTER_COUNT:
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
        con = create_connection('../db/database.db')
        updater = f"""
                        UPDATE polls
                        SET 'is_ended' = '1'
                        WHERE poll_id = '{poll_id}';
                        """
        execute_query(con, updater)
        request = f"SELECT for, against FROM polls WHERE poll_id={poll_id}"
        db_data = execute_read_query(con, request)
        if db_data[0][0] < db_data[0][1]:
            print("Голосование окончено. Мероприятие НЕ принято!")  # DEBUG
        else:
            request = "INSERT INTO global_events (name, descr, start_time, duration, exp_reward) SELECT name, descr, " \
                      f"start_time, duration, exp_reward FROM polls WHERE poll_id = {poll_id}"
            execute_query(con, request)
        con.close()


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_members_count = await context.bot.getChatMemberCount(update.effective_chat.id) - 1
    global TOTAL_VOTER_COUNT
    if chat_members_count > 1:
        TOTAL_VOTER_COUNT = chat_members_count // 2
    else:
        TOTAL_VOTER_COUNT = 1
    chat: Chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        msg = "Вы собираетесь добавить новое глобальное событие\n\n" \
              "Обратите внимание, что информацию о новом событии необходимо вводить СТРОГО в указанном ниже формате.\n" \
              "Все поля должны быть разделены знаком переноса строки (через Shift+Enter).\n\n" \
              "Формат информации о событии: \n" \
              "Название события (не более 50 символов)\n" \
              "Описание события (не более 500 символов)\n" \
              "Время начала события в формате yyyy-MM-dd hh:mm:ss\n" \
              "Продолжительность события (целое число, в минутах)\n" \
              "Награда опытом за событие (целое число >=0)\n\n\n" \
              "Пример ввода информации для нового события: \n" \
              "Мое новое событие\n" \
              "Это событие будет лучшим в истории!\n" \
              "2027-12-12 23:59:59\n" \
              "60\n" \
              "365\n\n\n" \
              "Теперь введите информацию о новом событии в ответном сообщении."
        await update.message.reply_text(msg)
        return EVENT_INPUT
    else:
        response = "Провести голосование можно только в групповых чатах!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


poll_handler = ConversationHandler(
    entry_points=[CommandHandler("poll", add_event)],
    states={
        EVENT_INPUT: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), poll),
        ]
    },
    fallbacks=[MessageHandler(filters.Regex("^Отмена$"), cancel)],
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
def is_available(user_id, required_exp) -> bool:
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
        DESC LIMIT 20
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
