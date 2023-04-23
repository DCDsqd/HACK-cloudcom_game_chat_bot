from database import *
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from time_control import ensure_time_format
from menu_chain import main_menu

ADMIN_MENU, ADD_ADMIN, DELETE_ADMIN, EVENT_INPUT, \
    DELETE_EVENT_MENU, EVENT_BY_DATE, EVENT_BY_NAME, GET_EVENT_ID = range(8)
admin_keyboard = [["Добавить администратора", "Удалить администратора"], ["Добавить событие", "Удалить событие"],
                  ["Отмена"]]
admin_markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
back_keyboard = [["Назад"]]
back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True)
events_keyboard = [["Ближайшие события"], ["По дате", "По имени"], ["Назад"]]
events_markup = ReplyKeyboardMarkup(events_keyboard, one_time_keyboard=True)


# This function checks if a user has admin privileges and sends an appropriate message to the chat depending on the
# result. If the user is an admin, an admin menu is also sent with options for the user to choose from.
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if db.check_if_user_is_admin(update.message.from_user.id):
        success_message = "Доступ получен. Меню администратора:"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=success_message,
                                       reply_markup=admin_markup)
        return ADMIN_MENU
    else:
        failed_message = "В доступе отказано!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=failed_message)


# This function is used to send a message to the chat explaining how to format information about a new event and 
# asking the user to input that information. This is typically used when an admin wants to add a new event.
async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    event_info_message = "Вы собираетесь добавить новое глобальное событие\n\n" \
                         "Обратите внимание, что информацию о новом событии необходимо вводить СТРОГО в указанном " \
                         "ниже формате.\n" \
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text=event_info_message, reply_markup=back_markup)
    return EVENT_INPUT


# This function parse_new_event_info_string takes a string text containing information about a new event, parses and
# validates it. It returns a tuple consisting of a boolean value indicating whether the information is valid or not,
# and a string message indicating the reason for validation failure if applicable.
def parse_new_event_info_string(event_info_string: str) -> tuple[bool, str]:
    MAX_DURATION = 525600
    event_info_fields = event_info_string.split('\n')

    if len(event_info_fields) != 5:
        return False, 'Вы указали недостаточно информации о новом событии. ' \
                      'Возможно, Вы забыли разделить информацию с помощью Shift+Enter, либо пропустили какое-то из ' \
                      'полей.'

    event_name = event_info_fields[0]
    if len(event_name) > 50:
        return False, 'Вы указали слишком длинное имя для события. Оно не должно превышать 50 символов.'

    event_description = event_info_fields[1]
    if len(event_description) > 500:
        return False, 'Вы указали слишком длинное описание для события. Оно не должно превышать 500 символов.'

    start_time = event_info_fields[2]
    if not ensure_time_format(start_time):
        return False, 'Указанное Вами время события не прошло проверку на правильность формата. ' \
                      'Не забывайте, что формат должен СТРОГО соответствовать следующему формату: ' \
                      'yyyy-MM-dd hh:mm:ss. Также, возможно, Вы ввели несуществующую дату.'

    duration = event_info_fields[3]
    if not duration.isdigit():
        return False, 'Указанная Вами продолжительность события не является числом.'
    if int(duration) < 1:
        return False, 'Продолжительность события не может быть меньше 1 минуты.'
    if int(duration) > MAX_DURATION:
        return False, f"Продолжительность события не может быть больше года ('{MAX_DURATION}' минут)."

    exp_reward = event_info_fields[4]
    if not exp_reward.isdigit():
        return False, 'Указанная Вами награда в опыте за событие не является числом.'
    if int(exp_reward) < 0:
        return False, 'Награда в опыте за событие не может быть отрицательной.'

    return True, 'Все поля валидны.'


# This is function that handles the input of a new event. It uses the parse_new_event_info_string function to parse
# the text of the new event, and depending on whether the information is valid or not, it sends a response message to
# the user and returns the appropriate state. The function also generates a keyboard markup based on the outcome of
# the input.
async def event_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_event_text = update.message.text
    is_ok, msg = parse_new_event_info_string(new_event_text)
    if is_ok:
        success_response = f"Создание нового события прошло успешно!\nКомментарий: {msg}"
        db.save_new_event_info_string_to_db(new_event_text)
        logging.info(f"[{update.message.from_user.id}] New event was added by admin")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=success_response,
                                       reply_markup=admin_markup)
        return ADMIN_MENU
    else:
        error_response = f"Ошибка при создании события!\nКомментарий: {msg}\n\nПопробуйте ещё раз."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_response, reply_markup=back_markup)
        return EVENT_INPUT


# This function prompts the user to enter a player ID for security reasons and then returns the state OP. It is used
# as a step in a larger conversation flow. Op means "Make an operator"
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Для безопасности, требуется ввести ID игрока.\nЕго можно узнать с помощью команды /profile"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
    await update.message.reply_text("Введите ID игрока:")
    return ADD_ADMIN


# This function receives the ID of a user and adds them as an administrator if the user exists in the database. If
# the user does not exist, the function sends a message indicating that the user does not exist. The function then
# returns the user to the administrator choosing menu.
async def received_new_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    all_ids = db.get_all_user_ids()
    try:
        new_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(f"Требуется ввести ID пользователя. Полученный текст не является ID!",
                                        reply_markup=admin_markup)
        return ADMIN_MENU
    if new_admin_id in all_ids:
        context.user_data["admin"] = new_admin_id
        db.update_users('admin', 1, new_admin_id)
        await update.message.reply_text(f"Пользователь с ID: {new_admin_id} теперь администратор.",
                                        reply_markup=admin_markup)
        logging.info(f"[{update.message.from_user.id}] New admin with ID {new_admin_id} was added")
    else:
        await update.message.reply_text(f"Пользователя с ID: {new_admin_id} не существует!", reply_markup=admin_markup)
    return ADMIN_MENU


# This function prompts the user to enter a player ID for security reasons and then returns the state DEOP. It is used
# as a step in a larger conversation flow. Deop means "Delete an operator"
async def delete_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Для безопасности, требуется ввести ID игрока.\nЕго можно узнать с помощью команды /profile"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
    await update.message.reply_text("Введите ID игрока:")
    return DELETE_ADMIN


# This function receives the ID of a user and delete them as an administrator if the user exists in the database. If
# the user does not exist, the function sends a message indicating that the user does not exist. The function then
# returns the user to the administrator choosing menu.
async def received_admin_id_to_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    all_ids = db.get_all_user_ids()
    try:
        del_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(f"Требуется ввести ID пользователя. Полученный текст не является ID!",
                                        reply_markup=admin_markup)
        return ADMIN_MENU
    if del_admin_id in all_ids:
        context.user_data["admin"] = del_admin_id
        db.update_users('admin', 0, del_admin_id)
        await update.message.reply_text(f"Пользователь с ID: {del_admin_id} больше не администратор.",
                                        reply_markup=admin_markup)
        logging.info(f"[{update.message.from_user.id}] User with ID {del_admin_id} now is not admin")
    else:
        await update.message.reply_text(f"Пользователя с ID: {del_admin_id} не существует!", reply_markup=admin_markup)
    return ADMIN_MENU


# The "delete_event" function sends a message to a chat with a specified reply markup and returns an integer value.
async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response_text = "Как хотите посмотреть события?"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, reply_markup=events_markup)
    return DELETE_EVENT_MENU


# The "nearest_events" function retrieves the closest global events from a database, formats them into a string,
# sends the formatted events text and a prompt message to a chat, and returns an integer value. It uses HTML
# formatting for the message sent.
async def nearest_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    closest_events = db.get_20_closest_global_events()
    events_text = ""
    for event in closest_events:
        event_text = f"<b>ID: {event[0]}</b>\n"
        event_text += f"<b>{event[1]}</b>\n"
        event_text += f"<i>{event[2]}</i>\n"
        event_text += f"<u>Начало:</u> {event[3]}\n"
        event_text += f"<u>Длительность:</u> {event[4]}\n"
        events_text += event_text + "\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events_text, parse_mode='HTML')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите ID события, которое хотите удалить.",
                                   reply_markup=back_markup)
    return GET_EVENT_ID


# The "event_by_data" function prompts the user to enter a date and returns an integer value. It sends a message to a
# chat with a specified text and reply markup.
async def event_by_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    get_date_text = "Введите дату в формате YYYY-MM-DD"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=get_date_text, reply_markup=back_markup)
    return EVENT_BY_DATE


# The "received_date" function checks the validity of a received date and filters global events accordingly. It sends
# a formatted list of filtered events to the chat and prompts the user to enter the ID of the event they want to
# delete. It returns an integer value. If the date is invalid, it sends a response message and prompts the user to
# input the date again.
async def received_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    event_date = update.message.text
    if len(event_date) == 10 and event_date[4] == '-' and event_date[7] == '-' and \
            event_date[0:4].isdigit() and event_date[5:7].isdigit() and event_date[8:10].isdigit():
        events_data = db.get_all_global_events()
        filtered_events = [event for event in events_data if event_date in event[3]]
        if len(filtered_events) == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=f"Не найдены события с началом в {event_date}",
                                           reply_markup=events_markup)
            return DELETE_EVENT_MENU
        events = ""
        for row in filtered_events:
            event_text = f"<b>ID: {row[0]}</b>\n"
            event_text += f"<b>{row[1]}</b>\n"
            event_text += f"<i>{row[2]}</i>\n"
            event_text += f"<u>Начало:</u> {row[3]}\n"
            event_text += f"<u>Длительность:</u> {row[4]}\n"
            events += event_text + "\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Введите ID события, которое хотите удалить.", reply_markup=back_markup)
        return GET_EVENT_ID
    else:
        response = "Введённая дата не соответствует формату YYYY-MM-DD. Попробуйте ещё раз."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=back_markup)
        return EVENT_BY_DATE


# The "event_by_name" function prompts the user to enter the name of an event and returns an integer value. It sends
# a message to a chat with a specified text and reply markup.
async def event_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    get_event_name_text = "Введите название мероприятия"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=get_event_name_text, reply_markup=back_markup)
    return EVENT_BY_NAME


# This function receives an event name from the user and filters the events from the database that contain this name.
# If there are no events with that name, it sends a message to the user, otherwise it sends a formatted list of
# events and prompts the user to enter the ID of the event they want to delete.
async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    event_name = update.message.text
    events_data = db.get_all_global_events()
    filtered_events = [event for event in events_data if event_name in event[1]]
    if len(filtered_events) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Не найдены события с названием {event_name}", reply_markup=events_markup)
        return DELETE_EVENT_MENU
    events = ""
    for row in filtered_events:
        event_text = f"<b>ID: {row[0]}</b>\n"
        event_text += f"<b>{row[1]}</b>\n"
        event_text += f"<i>{row[2]}</i>\n"
        event_text += f"<u>Начало:</u> {row[3]}\n"
        event_text += f"<u>Длительность:</u> {row[4]}\n"
        events += event_text + "\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=events, parse_mode='HTML')
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Введите ID события, которое хотите удалить.", reply_markup=back_markup)
    return GET_EVENT_ID


# This function handles the deletion of a global event by ID. It takes the ID from the user input, checks if it is a
# digit and deletes the corresponding event from the database. If successful, it sends a confirmation message to the
# user and returns to the admin menu. If the ID is not a digit, it sends an error message and returns to the previous
# step of getting the event ID.
async def delete_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    event_id = update.message.text
    if event_id.isdigit():
        db.delete_global_event(event_id)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Событие с ID {event_id} успешно удалено!", reply_markup=admin_markup)
        logging.info(f"[{update.message.from_user.id}] Event with ID {event_id} was deleted")
        return ADMIN_MENU
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="ID должно быть числовым значением. Попробуйте ещё раз.",
                                       reply_markup=back_markup)
        return GET_EVENT_ID


admin_handler = ConversationHandler(
    entry_points=[CommandHandler("admin", admin)],
    states={
        ADMIN_MENU: [
            MessageHandler(filters.Regex("^Добавить событие$"), add_event),
            MessageHandler(filters.Regex("^Удалить событие$"), delete_event),
            MessageHandler(filters.Regex("^Добавить администратора$"), add_admin),
            MessageHandler(filters.Regex("^Удалить администратора$"), delete_admin),
        ],
        ADD_ADMIN: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), received_new_admin_id),
            MessageHandler(filters.Regex("^Назад$"), admin),
        ],
        DELETE_ADMIN: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), received_admin_id_to_delete),
            MessageHandler(filters.Regex("^Назад$"), admin),
        ],
        EVENT_INPUT: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), event_input),
            MessageHandler(filters.Regex("^Назад$"), admin),
        ],
        DELETE_EVENT_MENU: [
            MessageHandler(filters.Regex("^Ближайшие события$"), nearest_events),
            MessageHandler(filters.Regex("^По дате$"), event_by_data),
            MessageHandler(filters.Regex("^По имени$"), event_by_name),
            MessageHandler(filters.Regex("^Назад$"), admin),
        ],
        EVENT_BY_DATE: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), received_date),
            MessageHandler(filters.Regex("^Назад$"), delete_event),
        ],
        EVENT_BY_NAME: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), received_name),
            MessageHandler(filters.Regex("^Назад$"), delete_event),
        ],
        GET_EVENT_ID: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), delete_by_id),
            MessageHandler(filters.Regex("^Назад$"), delete_event),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Отмена$"), main_menu)],
)
