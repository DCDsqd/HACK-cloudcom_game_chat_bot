from database import *
from customization import regen_avatar
import os
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, Chat
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from admin import parse_new_event_info_string

EVENT_INPUT = 0
TOTAL_VOTER_COUNT = 10


async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    con = create_connection('../db/database.db')
    query = """
        SELECT * FROM users
        ORDER BY exp
        DESC LIMIT 10
    """
    res = execute_read_query(con, query)
    con.close()
    events = "Топ-10 игроков по опыту:\n"
    for row in res:
        event = f"<b>{row[2]} ({row[1]}) - {row[5]}</b>\n"
        events += event
    con.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')


# This code defines an async function poll that creates a poll message in a chat and stores its information in a
# database. If the parse_new_event_info_string() function returns True, the function creates a poll message with two
# possible answers ("Да" and "Нет") and stores its id in a database table called polls. Then, it extracts the fields
# from the text variable, updates the database table with the information, and updates the bot_data dictionary with
# information about the poll. If parse_new_event_info_string() returns False, the function sends an error message to
# the chat.
async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        with create_connection('../db/database.db') as con:
            create_poll_query = f"""
                    INSERT INTO
                    polls (poll_id)
                    VALUES
                    ('{poll_id}');
                    """
            execute_query(con, create_poll_query)
            fields = text.split('\n')
            name, descr, start_time, duration, exp_reward = fields[:5]
            update_poll_query = f"""
                    UPDATE polls SET name='{name}', descr='{descr}', start_time='{start_time}', duration='{duration}', 
                    exp_reward='{exp_reward}'
                    WHERE poll_id={poll_id};
                    """
            execute_query(con, update_poll_query)
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


# The receive_poll_answer function updates the poll data in the database and handles the answers received from users.
# It increments the vote count for the respective option and checks if the poll is ended. If the poll is ended,
# it stops the poll, updates the database, and logs the result. If the event is accepted, it is added to the database.
async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = update.poll_answer
    poll_id = answer['poll_id']
    option_id = answer['option_ids'][0]
    col = 'for' if option_id == 0 else 'against'
    with create_connection('../db/database.db') as con:
        request = f"SELECT {col} FROM polls WHERE poll_id={poll_id}"
        db_data = execute_read_query(con, request)
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
    with create_connection('../db/database.db') as con:
        request = f"SELECT for, against FROM polls WHERE poll_id={poll_id}"
        for_and_against = execute_read_query(con, request)
    if for_and_against[0][0] == TOTAL_VOTER_COUNT or for_and_against[0][1] == TOTAL_VOTER_COUNT:
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
            logging.info(f"[{poll_id}] Голосование окончено. Мероприятие НЕ принято!")
        else:
            request = "INSERT INTO global_events (name, descr, start_time, duration, exp_reward) SELECT name, descr, " \
                      f"start_time, duration, exp_reward FROM polls WHERE poll_id = {poll_id}"
            execute_query(con, request)
            logging.info(f"[{poll_id}] Голосование окончено. Мероприятие принято и добавлено в БД!")
        con.close()


# This is function, that checks if the chat is a group or supergroup and sends a message with instructions on how to
# add a new global event. If the chat is not a group or supergroup, the function sends an error message and
# terminates the conversation. If the chat is a group or supergroup, the function sends a message with instructions
# on how to add a new global event and returns EVENT_INPUT, which is the next state in the conversation.
async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat: Chat = update.effective_chat
    chat_members_count: int = await context.bot.getChatMemberCount(chat.id) - 1
    global TOTAL_VOTER_COUNT
    TOTAL_VOTER_COUNT = chat_members_count // 2 if chat_members_count > 1 else 1
    if chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        response = "Провести голосование можно только в групповых чатах!"
        await context.bot.send_message(chat_id=chat.id, text=response)
        return ConversationHandler.END

    new_event_info = (
        "Вы собираетесь добавить новое глобальное событие\n\n"
        "Обратите внимание, что информацию о новом событии необходимо вводить СТРОГО в указанном ниже формате.\n"
        "Все поля должны быть разделены знаком переноса строки (через Shift+Enter).\n\n"
        "Формат информации о событии: \n"
        "Название события (не более 50 символов)\n"
        "Описание события (не более 500 символов)\n"
        "Время начала события в формате yyyy-MM-dd hh:mm:ss\n"
        "Продолжительность события (целое число, в минутах)\n"
        "Награда опытом за событие (целое число >=0)\n\n\n"
        "Пример ввода информации для нового события: \n"
        "Мое новое событие\n"
        "Это событие будет лучшим в истории!\n"
        "2027-12-12 23:59:59\n"
        "60\n"
        "365\n\n\n"
        "Теперь введите информацию о новом событии в ответном сообщении."
    )

    await update.message.reply_text(new_event_info)
    return EVENT_INPUT


poll_handler = ConversationHandler(
    entry_points=[CommandHandler("poll", add_event)],
    states={
        EVENT_INPUT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, poll),
        ]
    },
    fallbacks=[],
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
def add_exp(user_id, exp) -> None:
    con = create_connection('../db/database.db')
    request = f"SELECT exp FROM users WHERE id={user_id}"
    db_data = execute_read_query(con, request)
    con.close()
    inserter('exp', int(db_data[0][0]) + exp, user_id)


# This function that sends a welcome message to the user and then checks if the user exists in the database. If the
# user does not exist, the function creates a connection to a database, executes an SQL query to insert the user's ID
# and username (if available) into a users table, generates an avatar for the user, and then closes the connection.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        users (id, username, personal_username)
        VALUES
        ('{user_id}', '{username}', '{username}');
        """
        execute_query(con, create_users)
        regen_avatar(user_id)

        con.close()


# This function that retrieves user data from a database, generates a message containing the user's profile
# information (including personal username, Telegram username, subclass, rank, class, and experience points),
# sends the message along with the user's avatar, and then deletes the message that triggered the function.
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
async def get_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        event += f"<u>Начало :</u> {row[3]}\n"
        event += f"<u>Длительность:</u> {row[4]}\n"
        event += f"<u>Участники:</u> {row[5]}\n"
        event += f"<u>Награда (опыт):</u> {row[6]}\n"
        events += event + "\n"
    con.close()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')


# This function sends a message to the user with the available commands for the bot. It  sends a message containing a
# list of commands that the user can enter.
async def help_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "Вот доступные команды:\n\n" \
              "/start - Начало использования бота\n" \
              "/help - Просмотр доступных команд\n" \
              "/custom - Настройка вашего игрового персонажа"
    await context.bot.send_message(chat_id=update.message.from_user.id, text=message)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


# Требуемая функция на этапе разработки, потом нужно будет убрать
async def del_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Клавиатура удалена!',
                                   reply_markup=ReplyKeyboardRemove())
