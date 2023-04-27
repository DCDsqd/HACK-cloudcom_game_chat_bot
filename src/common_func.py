from database import *
from customization import regen_avatar
from menu_chain import main_menu, menu_markup
from duels import *
from admin import parse_new_event_info_string

import os
import re
import logging
import threading
from telegram import Update, ReplyKeyboardRemove, Chat, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    ChatMember, ChatMemberUpdated
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image

EVENT_INPUT = 0
TOTAL_VOTER_COUNT = 10


# This function takes a ChatMemberUpdated object as input, which represents an update of a member's status in a chat.
# It extracts whether there was a change in the member's status, and if so, whether the member was added or removed
# from the chat. It returns a tuple of two boolean values, the first indicating whether the member was in the chat
# before the update, and the second indicating whether the member is in the chat after the update. If there was no
# change in status, the function returns None.
def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


# This is a function that tracks changes in chats where the bot is a member, specifically when the bot is added or
# removed from a group. It extracts information about the status change, the user responsible for the change,
# and the chat in question. Depending on the status change, it adds or deletes the chat ID and title to/from the
# database, respectively. It also logs the event using the Python logging module.
async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    cause_name = update.effective_user.full_name

    chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logging.info("%s added the bot to the group %s", cause_name, chat.title)
            db.add_chat_id(chat.id, chat.title)
        elif was_member and not is_member:
            logging.info("%s removed the bot from the group %s", cause_name, chat.title)
            db.delete_chat_id(chat.id)


def merge_photos(background: str, user_id: int) -> BytesIO:
    back = Image.open(os.path.abspath(f'../res/locations/{background}.png')).convert("RGBA")
    character = Image.open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png')).convert("RGBA")
    new_size = (character.size[0] // 2, character.size[1] // 2)
    character = character.resize(new_size, Image.NEAREST)
    if background == 'AnvilHouse' or background == 'Taverna':
        back.paste(character, (250, 172), character)
    else:
        back.paste(character, (250, 250), character)
    result_image = BytesIO()
    result_image.name = 'image.jpeg'
    back.save(result_image, 'PNG')
    result_image.seek(0)
    return result_image


def merge_arena(user1_id: int, user2_id: int) -> BytesIO:
    files1 = db.get_item_file_name(user1_id)
    files2 = db.get_item_file_name(user2_id)
    back = Image.open(os.path.abspath(f'../res/locations/Arena.png')).convert("RGBA")

    character1 = Image.open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user1_id}.png')).convert("RGBA")
    item1 = Image.open(os.path.abspath(f'../res/armor/{files1[0]}.png')).convert("RGBA")
    nsize = (item1.size[0] * 5, item1.size[1] * 5)
    item1 = item1.resize(nsize, Image.NEAREST)
    item2 = Image.open(os.path.abspath(f'../res/armor/{files1[1]}.png')).convert("RGBA")
    nsize = (item2.size[0] * 5, item2.size[1] * 5)
    item2 = item2.resize(nsize, Image.NEAREST)

    # увеличение размеров изображения character1 до размеров, достаточных для размещения item1 и item2
    new_width = max(character1.width, item1.width, item2.width)
    new_height = max(character1.height, item1.height, item2.height)
    background = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    x_offset = (new_width - character1.width) // 2
    y_offset = (new_height - character1.height) // 2
    background.paste(character1, (x_offset, y_offset))
    character1 = background
    character1.paste(item1, (0, -20), item1)
    character1.paste(item2, (0, -20), item2)

    character2 = Image.open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user2_id}.png')).convert("RGBA")
    item1 = Image.open(os.path.abspath(f'../res/armor/{files2[0]}.png')).convert("RGBA")
    nsize = (item1.size[0] * 5, item1.size[1] * 5)
    item1 = item1.resize(nsize, Image.NEAREST)
    item2 = Image.open(os.path.abspath(f'../res/armor/{files2[1]}.png')).convert("RGBA")
    nsize = (item2.size[0] * 5, item2.size[1] * 5)
    item2 = item2.resize(nsize, Image.NEAREST)

    background = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    x_offset = (new_width - character2.width) // 2
    y_offset = (new_height - character2.height) // 2
    background.paste(character2, (x_offset, y_offset))
    character2 = background
    character2.paste(item1, (0, -20), item1)
    character2.paste(item2, (0, -20), item2)
    new_size = (character1.size[0] // 2, character1.size[1] // 2)
    character1 = character1.resize(new_size, Image.NEAREST)
    new_size = (character2.size[0] // 2, character2.size[1] // 2)
    character2 = character2.resize(new_size, Image.NEAREST)
    back.paste(character1, (70, 250), character1)
    back.paste(character2, (370, 250), character2)
    result_image = BytesIO()
    result_image.name = 'image.jpeg'
    back.save(result_image, 'PNG')
    result_image.seek(0)
    return result_image


# This function retrieves the top 10 players based on their experience and sends a message to the chat with their
# username, level and experience. The message is formatted in HTML.
async def rating_by_exp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    res = db.get_top_10_players()
    events = "Топ-10 игроков по опыту:\n"
    for row in res:
        event = f"<b>{row[0]} ({row[1]}) - {row[2]}</b>\n"
        events += event
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')


# This code defines an async function poll that creates a poll message in a chat and stores its information in a
# database. If the parse_new_event_info_string() function returns True, the function creates a poll message with two
# possible answers ("Да" and "Нет") and stores its id in a database table called polls. Then, it extracts the fields
# from the text variable, updates the database table with the information, and updates the bot_data dictionary with
# information about the poll. If parse_new_event_info_string() returns False, the function sends an error message to
# the chat.
async def event_chat_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    is_ok, msg = parse_new_event_info_string(text)
    if is_ok:
        context.bot_data["new_event_info"] = text
        questions = ["Да", "Нет"]
        message = await context.bot.send_poll(
            update.effective_chat.id,
            "Поддерживаете ли вы проведение данного мероприятия?",
            questions,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        poll_id = message.poll.id
        db.create_poll_from_text(poll_id, text)
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
    col = 'for' if answer['option_ids'][0] == 0 else 'against'
    db.increment_poll_votes(poll_id, col)
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
    for_and_against = db.get_poll_votes_both_col(poll_id)
    if for_and_against[0] == TOTAL_VOTER_COUNT or for_and_against[1] == TOTAL_VOTER_COUNT:
        await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
        db.finish_poll(poll_id)
        results = db.get_poll_votes_both_col(poll_id)
        if results[0] < results[1]:
            logging.info(f"[{poll_id}] Голосование окончено. Мероприятие НЕ принято!")
        else:
            logging.info(f"[{poll_id}] Голосование окончено. Мероприятие принято и добавлено в БД!")
            db.save_new_event_info_string_to_db(context.bot_data["new_event_info"])


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
                filters.TEXT & ~filters.COMMAND, event_chat_poll),
        ]
    },
    fallbacks=[],
)


# This function takes a user ID as input and returns the rank of the user based on their experience points,
# using a pre-selected table of ranks. It assumes that the ranks table is ordered by the exp_to_earn column. If the
# user's experience points are greater than the highest rank, the function returns the highest rank.
def get_rank(user_id):
    user_exp = db.get_user_exp(user_id)
    ranks = db.select_ranks_table()
    # Relies on the fact that ranks variable is ordered by exp_to_earn column
    for i in range(1, len(ranks)):
        if ranks[i][1] > user_exp:
            return ranks[i - 1][0]
    return ranks[len(ranks) - 1][0]


# This function takes a user ID and a required amount of experience points as input and returns a boolean indicating
# whether the user has at least the required amount of experience points. It returns True if the user has at least
# the required amount, and False otherwise.
def check_if_user_exp_is_enough(user_id, required_exp) -> bool:
    user_exp = db.get_user_exp(user_id)
    return int(user_exp) >= required_exp


# This function that sends a welcome message to the user and then checks if the user exists in the database. If the
# user does not exist, the function creates a connection to a database, executes an SQL query to insert the user's ID
# and username (if available) into a users table, generates an avatar for the user, and then closes the connection.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    await context.bot.send_message(chat_id=user_id,
                                   text="Добро пожаловать в Team Builder Bot! Введите /help, чтобы просмотреть "
                                        "доступные команды.",
                                   reply_markup=menu_markup)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    message = update.message
    user = message.from_user
    if user.username:
        username = user.username
    else:
        username = None
    if not db.check_if_user_exists(user_id):
        db.create_user(user_id, username)
        regen_avatar(user_id)


# This function that retrieves user data from a database, generates a message containing the user's profile
# information (including personal username, Telegram username, subclass, rank, class, and experience points),
# sends the message along with the user's avatar, and then deletes the message that triggered the function.
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user_id = message.from_user.id
    username = message.from_user.username
    db_data = db.get_user_info(user_id)
    message = "🗣️ Ваш профиль:\n\n" \
              f"📋 Игровое имя: {db_data[0][0]}\n" \
              f"🆔 ID: {user_id}\n" \
              f"👨‍✈️ Имя Telegram: {username}\n" \
              f"🛠️ Класс: {db_data[0][1]}\n" \
              f"🗡️ Подкласс: {db_data[0][3]}\n" \
              f"🏆 Ранг: {get_rank(user_id)}\n" \
              f"🌡️ Опыт: {db_data[0][2]}\n" \
              f"🧤 Счёт в дуэлях: {db.get_duels_record_for_user(user_id)}\n" \
              f"💰 Баланс средств: {db.get_user_money(user_id)}\n"
    await context.bot.send_photo(chat_id=user_id, caption=message,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


EVENT_CHOOSING, GET_EVENT_ID, EVENT_ID_TO_APPROVE = range(3)
events_keyboard = [['Просмотр событий', 'Принять участие'], ['Подтвердить выполнение'], ['Назад']]
back_keyboard = [['Назад']]
events_markup = ReplyKeyboardMarkup(events_keyboard, one_time_keyboard=False)
back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True)


async def irl_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Выберите действие"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=events_markup)
    return EVENT_CHOOSING


# Function retrieves events from the database and formats them as an HTML-formatted string before sending them as a
# message to the Telegram chat. It uses the create_connection() function to connect to the database, executes a SQL
# query to select all the events in the global_events table and order them by their start time. Then it loops through
# the results and formats each event's data as an HTML string.
async def get_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    res = db.get_20_closest_global_events()
    events = "Ближайшие 20 событий:\n\n"
    for row in res:
        event = f"<b>{row[1]}</b>\n"
        event += f"<i>{row[2]}</i>\n"
        event += f"<u>Начало :</u> {row[3]}\n"
        event += f"<u>Длительность:</u> {row[4]}\n"
        event += f"<u>Награда (опыт):</u> {row[5]}\n"
        events += event + "\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')


async def send_closest_events_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    res = db.get_20_closest_global_events()
    res = sorted(res, key=lambda x: x[3])
    events = "Ближайшие доступные события:\n\n"
    for row in res:
        if row[3] > cur_time():
            event = f"<b>ID: {row[0]}</b>\n"
            event += f"<b>{row[1]}</b>\n"
            event += f"<i>{row[2]}</i>\n"
            event += f"<u>Начало :</u> {row[3]}\n"
            event += f"<u>Длительность:</u> {row[4]}\n"
            event += f"<u>Награда (опыт):</u> {row[5]}\n"
            events += event + "\n"
    events += "\nВведите ID события, в котором хотите принять участие"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML',
                                   reply_markup=back_markup)
    return GET_EVENT_ID


async def add_participant(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        event_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(f"Требуется ввести ID события. Полученный текст не является ID!",
                                        reply_markup=events_markup)
        return EVENT_CHOOSING
    db.update_participants_in_global_event(event_id, update.message.from_user.id)
    await update.message.reply_text(f"Теперь вы учавствуете в событии с ID {event_id}",
                                    reply_markup=events_markup)
    return EVENT_CHOOSING


async def complete_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_events = db.get_user_events(update.message.from_user.id)
    if len(user_events) == 0:
        await update.message.reply_text(f"Вы не учавствуете ни в одном событии!",
                                        reply_markup=events_markup)
        return EVENT_CHOOSING
    events = "Доступные мероприятия:\n\n"
    for row in user_events:
        event = f"<b>ID: {row[0]}</b>\n"
        event += f"<b>{row[1]}</b>\n"
        event += f"<i>{row[2]}</i>\n"
        event += f"<u>Начало :</u> {row[3]}\n"
        event += f"<u>Длительность:</u> {row[4]}\n"
        event += f"<u>Награда (опыт):</u> {row[5]}\n"
        events += event + "\n"
    events += "\nВведите ID мероприятия, выполнение которого хотите подтвердить и приложите фото выполненного задания."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML',
                                   reply_markup=back_markup)
    return EVENT_ID_TO_APPROVE


async def send_event_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    try:
        event_id = int(message.caption)
    except Exception as e:
        await update.message.reply_text(f"Требуется ввести ID события и приложить фото!",
                                        reply_markup=events_markup)
        logging.info("The user did not attach a photo or did not enter the event ID: " + str(e))
        return EVENT_CHOOSING
    admins = db.get_admins_id()
    event = db.get_event_by_id(event_id)
    event_text = f"<b>ID: {event[0][0]}</b>\n" \
                 f"<b>{event[0][1]}</b>\n" \
                 f"<i>{event[0][2]}</i>\n" \
                 f"<u>Начало:</u> {event[0][3]}\n" \
                 f"<u>Длительность:</u> {event[0][4]}\n" \
                 f"<u>Награда (опыт):</u> {event[0][5]}\n"
    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data="accept_event"),
            InlineKeyboardButton("❌ Отклонить", callback_data="reject_event"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for admin in admins:
        await context.bot.send_message(chat_id=admin[0],
                                       text=event_text,
                                       parse_mode='HTML')
        await context.bot.forward_message(admin[0], update.effective_chat.id, message.id)
        await context.bot.send_message(chat_id=admin[0],
                                       text=f"Пользователь с ID {update.effective_chat.id} выполнил мероприятие "
                                            f"# {event_id} с наградой {event[0][5]} опыта.\n\n"
                                            f"Подтверждаете ли Вы выполнение данного мероприятия?",
                                       reply_markup=reply_markup)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Задание успешно отправленно на проверку!")
    return EVENT_CHOOSING


attacks_keyboard = [['Физическая атака', 'Использовать способность', 'Использовать предмет']]
attacks_markup = ReplyKeyboardMarkup(attacks_keyboard, one_time_keyboard=False)

solo_danges_attacks_keyboard = [['Физическая атака!', 'Использовать способность!', 'Использовать предмет!']]
solo_danges_attacks_markup = ReplyKeyboardMarkup(attacks_keyboard, one_time_keyboard=False)


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    receiver_id = query.from_user.id
    sender_id = re.search(r"ID\s+(\d+)", query.message.text).group(1)
    await query.answer()
    if query.data == "accept_multiplayer_task":
        try:
            db.user_multiplayer_accept_task(sender_id, receiver_id)
            await query.edit_message_text(text=f"Вы приняли приглашение на задание")
            await context.bot.send_message(chat_id=sender_id, text=f"Игрок с ID {receiver_id} принял Ваше приглашение!")
        except Exception:
            await query.edit_message_text(text=f"К сожалению, задание было отменено.")
    elif query.data == "reject_multiplayer_task":
        await query.edit_message_text(text=f"Вы отклонили приглашение на задание")
        db.delete_multiplayer_task_participants(sender_id)
        await context.bot.send_message(chat_id=sender_id, text=f"Игрок с ID {receiver_id} отклонил Ваше приглашение. "
                                                               f"Задание отменено.\n\nТребуется заново собрать группу "
                                                               f"для задания!")
    if query.data == "accept_event":
        event_id = re.search(r"#\s+(\d+)", query.message.text).group(1)
        if db.is_complited(event_id):
            await query.edit_message_text(text=f"Другой администратор уже подтвердил выполнение этого задания!")
        else:
            exp = re.search(r"наградой\s+(\d+)", query.message.text).group(1)
            db.complete_task(event_id)
            db.add_exp(sender_id, exp)
            await query.edit_message_text(text=f"Выполнение задания подтверждено! Опыт успешно начислен.")
            await context.bot.send_message(chat_id=sender_id, text="Администратор подтвердил выполнение задания!")
    elif query.data == "reject_event":
        event_id = re.search(r"#\s+(\d+)", query.message.text).group(1)
        if db.is_complited(event_id):
            await query.edit_message_text(text=f"Другой администратор уже подтвердил выполнение этого задания!")
        else:
            await query.edit_message_text(text=f"Вы отклонили задание!")
            await context.bot.send_message(chat_id=sender_id, text="Администратор отклонил выполнение задания!")
    elif query.data == "accept_duel":
        if int(sender_id) == int(receiver_id):
            await context.bot.send_message(chat_id=sender_id,
                                           text=f"Вы не можете вызвать на дуэль самого себя!")
            return ConversationHandler.END
        duel_id = db.get_pending_duel(sender_id, receiver_id)
        if duel_id == -1:  # Duel was not found or other error occurred during db query execution, check logs
            db.add_participant_to_open_duel(sender_id, receiver_id)
            duel_id = db.get_pending_duel(sender_id, receiver_id)
            new_duel_obj = Duel(duel_id, sender_id, receiver_id)
            init_duel(new_duel_obj)
            logging.info(f"Started duel between {sender_id} and {receiver_id}, duel id = {duel_id}")
            context.bot_data['duel_id' + str(sender_id)] = duel_id
            context.bot_data['duel_id' + str(receiver_id)] = duel_id
            await context.bot.send_photo(chat_id=sender_id,
                                         photo=merge_arena(sender_id, receiver_id),
                                         caption=f"Игрок с ID {receiver_id} принял приглашение на дуэль!")
            await context.bot.send_photo(chat_id=receiver_id,
                                         photo=merge_arena(sender_id, receiver_id),
                                         caption=f"Игрок с ID {receiver_id} принял приглашение на дуэль!")
            await context.bot.send_message(chat_id=sender_id,
                                           text=f"Дуэль между {sender_id} and {receiver_id}:\nСейчас Ваш ход! Не забывайте, что на каждый ход отведено не более 30 секунд!",
                                           reply_markup=attacks_markup)
            await context.bot.send_message(chat_id=receiver_id,
                                           text=f"Дуэль между {sender_id} and {receiver_id}:\nСейчас ход оппонента! Не забывайте, что на каждый ход отведено не более 30 секунд!",
                                           reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        else:
            await query.edit_message_text(text=f"Игрок с ID {receiver_id} принял приглашение на дуэль!")
            new_duel_obj = Duel(duel_id, sender_id, receiver_id)
            init_duel(new_duel_obj)
            logging.info(f"Started duel between {sender_id} and {receiver_id}, duel id = {duel_id}")
            context.bot_data['duel_id' + str(sender_id)] = duel_id
            context.bot_data['duel_id' + str(receiver_id)] = duel_id
            await context.bot.send_photo(chat_id=sender_id,
                                         photo=merge_arena(sender_id, receiver_id),
                                         caption=f"Игрок с ID {receiver_id} принял приглашение на дуэль!")
            await context.bot.send_photo(chat_id=receiver_id,
                                         photo=merge_arena(sender_id, receiver_id),
                                         caption=f"Игрок с ID {receiver_id} принял приглашение на дуэль!")
            await context.bot.send_message(chat_id=sender_id,
                                           text=f"Дуэль между {sender_id} and {receiver_id}:\nСейчас Ваш ход!",
                                           reply_markup=attacks_markup)
            await context.bot.send_message(chat_id=receiver_id,
                                           text=f"Дуэль между {sender_id} and {receiver_id}:\nСейчас ход оппонента!",
                                           reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    elif query.data == "reject_duel":
        await query.edit_message_text(text=f"Вы отклонили приглашение на дуэль!")


events_handler = ConversationHandler(
    entry_points=[CommandHandler("events", irl_events_menu),
                  MessageHandler(filters.Regex("^События$"), irl_events_menu)],
    states={
        EVENT_CHOOSING: [
            MessageHandler(filters.Regex("^Просмотр событий$"), get_events),
            MessageHandler(filters.Regex("^Принять участие$"), send_closest_events_message),
            MessageHandler(filters.Regex("^Подтвердить выполнение$"), complete_event)
        ],
        GET_EVENT_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), add_participant),
            MessageHandler(filters.Regex("^Назад$"), irl_events_menu),
        ],
        EVENT_ID_TO_APPROVE: [
            MessageHandler((filters.TEXT | filters.PHOTO) & ~(filters.COMMAND | filters.Regex("^Назад$")),
                           send_event_approval_request),
            MessageHandler(filters.Regex("^Назад$"), irl_events_menu),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
)


# This function sends a message to the user with the available commands for the bot. It  sends a message containing a
# list of commands that the user can enter.
async def help_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "Вот доступные команды:\n\n" \
              "/start - Начало использования бота\n" \
              "/help - Просмотр доступных команд\n" \
              "/custom - Настройка вашего игрового персонажа\n" \
              "/game - Войти в игру"
    await context.bot.send_message(chat_id=update.message.from_user.id, text=message)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


def start_duels_checking_coroutine():
    threading_event_duels = threading.Event()
    manage_expired_duels(threading_event_duels)
    logging.info("Duels checking coroutine started")


def manage_expired_duels(threading_event_duels) -> None:
    # logging.info("Entered duels checking coroutine")
    expired_duels_list = decrease_time_to_all_duels()
    # if expired_duels_list:
    #     info = "Found expired duels with ids = "
    #     for duel in expired_duels_list:
    #         info += str(duel.id)
    #         info += ";"
    #     logging.info(info)

    for cur_duel in expired_duels_list:
        notify_expired_duel(cur_duel.get_attacker_player_in_game().user_id,
                            cur_duel.get_defender_player_in_game().user_id)  # TODO: more args here!!!
        cur_duel.force_switch_turn()

    if not threading_event_duels.is_set():
        # Call the function again in 1 second
        threading.Timer(1, manage_expired_duels, [threading_event_duels]).start()


async def notify_expired_duel(user_id: int, opponent_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=user_id,
                                   text="Вы не успели совершить ход! Он будет передан сопернику.",
                                   reply_markup=ReplyKeyboardRemove())
    await context.bot.send_message(chat_id=opponent_id,
                                   text="Соперник не успел совершить свой ход! Он передан Вам!",
                                   reply_markup=attacks_markup)


async def del_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "Клавиатура удалена!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
