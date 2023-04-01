# use this file to create functions used to help admins manage global events & other admin-related stuff
import logging

from database import *
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

ADMIN_CHOOSING, OP, DEL_OP, EVENT_INPUT = range(4)


# This function checks if a user has admin privileges and sends an appropriate message to the chat depending on the
# result. If the user is an admin, an admin menu is also sent with options for the user to choose from.
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    user_id = update.message.from_user.id
    request = f"SELECT admin FROM users WHERE id={user_id}"
    is_admin = int(execute_read_query(con, request)[0][0])
    con.close()
    if is_admin:
        admin_keyboard = [["Добавить администратора", "Удалить администратора"], ["Добавить событие"], ["Отмена"]]
        markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
        message = "Доступ получен. Меню администратора:"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return ADMIN_CHOOSING
    else:
        message = "В доступе отказано!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


# This function is used to send a message to the chat indicating that all changes have been applied and the
# conversation with the user should end. This is typically used when an admin operation has been completed or cancelled.
async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Все изменения применены. Хорошего дня!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return ConversationHandler.END


# This function is used to send a message to the chat explaining how to format information about a new event and 
# asking the user to input that information. This is typically used when an admin wants to add a new event.
async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


# This function parse_new_event_info_string takes a string text containing information about a new event, parses and
# validates it. It returns a tuple consisting of a boolean value indicating whether the information is valid or not,
# and a string message indicating the reason for validation failure if applicable.
def parse_new_event_info_string(text):
    minutes_in_year = 525600
    fields = text.split('\n')

    if len(fields) != 5:
        return False, 'Вы указали недостаточно информации о новом событии. ' \
                      'Возможно, Вы забыли разделить информацию с помощью Shift+Enter, либо пропустили какое-то из ' \
                      'полей.'

    name = fields[0]
    if len(name) > 50:
        return False, 'Вы указали слишком длинное имя для события. Оно не должно превышать 50 символов.'

    descr = fields[1]
    if len(descr) > 500:
        return False, 'Вы указали слишком длинное описание для события. Оно не должно превышать 500 символов.'

    start_time = fields[2]
    if not ensure_time_format(start_time):
        return False, 'Указанное Вами время события не прошло проверку на правильность формата. ' \
                      'Не забывайте, что формат должен СТРОГО соответствовать следующему формату: ' \
                      'yyyy-MM-dd hh:mm:ss. Также, возможно, Вы ввели несуществующую дату.'

    duration = fields[3]
    if not duration.isdigit():
        return False, 'Указанная Вами продолжительность события не является числом.'
    if int(duration) < 1:
        return False, 'Продолжительность события не может быть меньше 1 минуты.'
    if int(duration) > minutes_in_year:
        return False, f"Продолжительность события не может быть больше года ('{minutes_in_year}' минут)."

    exp_reward = fields[4]
    if not exp_reward.isdigit():
        return False, 'Указанная Вами награда в опыте за событие не является числом.'
    if int(exp_reward) < 0:
        return False, 'Награда в опыте за событие не может быть отрицательной.'

    return True, 'Все поля валидны.'


# This is function that handles the input of a new event. It uses the parse_new_event_info_string function to parse
# the text of the new event, and depending on whether the information is valid or not, it sends a response message to
# the user and returns the appropriate state. The function also generates a keyboard markup based on the outcome of
# the input.
async def event_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_keyboard = [["Добавить администратора", "Удалить администратора"], ["Добавить событие"], ["Отмена"]]
    cancel_keyboard = [["Назад"]]
    text = update.message.text
    is_ok, msg = parse_new_event_info_string(text)
    if is_ok:
        response = f"Создание нового события прошло успешно!\nКомментарий: {msg}"
        save_new_event_info_string_to_db(text)
        logging.info(f"[{update.message.from_user.id}] New event was added by admin")
        markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return ADMIN_CHOOSING
    else:
        markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True)
        response = f"Ошибка при создании события!\nКомментарий: {msg}\n\nПопробуйте ещё раз."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return EVENT_INPUT


# This function prompts the user to enter a player ID for security reasons and then returns the state OP. It is used
# as a step in a larger conversation flow. Op means "Make an operator"
async def op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Для безопасности, требуется ввести ID игрока.\nЕго можно узнать с помощью команды /profile"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    await update.message.reply_text("Введите ID игрока:")
    return OP


# This function receives the ID of a user and adds them as an administrator if the user exists in the database. If
# the user does not exist, the function sends a message indicating that the user does not exist. The function then
# returns the user to the administrator choosing menu.
async def received_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    query = f"""
                SELECT id FROM users
                """
    res = execute_read_query(con, query)
    all_ids = []
    for i in range(len(res)):
        all_ids.append(res[i][0])
    admin_keyboard = [["Добавить администратора", "Удалить администратора"], ["Добавить событие"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
    try:
        new_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(f"Требуется ввести ID пользователя. Полученный текст не является ID!",
                                        reply_markup=markup)
        return ADMIN_CHOOSING
    if new_admin_id in all_ids:
        context.user_data["admin"] = new_admin_id
        inserter('admin', 1, new_admin_id)
        await update.message.reply_text(f"Пользователь с ID: {new_admin_id} теперь администратор.", reply_markup=markup)
        logging.info(f"[{update.message.from_user.id}] New admin with ID {new_admin_id} was added")
    else:
        await update.message.reply_text(f"Пользователя с ID: {new_admin_id} не существует!", reply_markup=markup)
    return ADMIN_CHOOSING


# This function prompts the user to enter a player ID for security reasons and then returns the state DEOP. It is used
# as a step in a larger conversation flow. Deop means "Delete an operator"
async def deop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Для безопасности, требуется ввести ID игрока.\nЕго можно узнать с помощью команды /profile"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    await update.message.reply_text("Введите ID игрока:")
    return DEL_OP


# This function receives the ID of a user and delete them as an administrator if the user exists in the database. If
# the user does not exist, the function sends a message indicating that the user does not exist. The function then
# returns the user to the administrator choosing menu.
async def received_deop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    query = f"""
                SELECT id FROM users
                """
    res = execute_read_query(con, query)
    all_ids = []
    for i in range(len(res)):
        all_ids.append(res[i][0])
    admin_keyboard = [["Добавить администратора", "Удалить администратора"], ["Добавить событие"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
    try:
        del_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(f"Требуется ввести ID пользователя. Полученный текст не является ID!",
                                        reply_markup=markup)
        return ADMIN_CHOOSING
    if del_admin_id in all_ids:
        context.user_data["admin"] = del_admin_id
        inserter('admin', 0, del_admin_id)
        await update.message.reply_text(f"Пользователь с ID: {del_admin_id} больше не администратор.",
                                        reply_markup=markup)
        logging.info(f"[{update.message.from_user.id}] User with ID {del_admin_id} now is not admin")
    else:
        await update.message.reply_text(f"Пользователя с ID: {del_admin_id} не существует!", reply_markup=markup)
    return ADMIN_CHOOSING


admin_handler = ConversationHandler(
    entry_points=[CommandHandler("admin", admin)],
    states={
        ADMIN_CHOOSING: [
            MessageHandler(filters.Regex("^Добавить событие$"), add_event),
            MessageHandler(filters.Regex("^Добавить администратора$"), op),
            MessageHandler(filters.Regex("^Удалить администратора$"), deop),
        ],
        OP: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), received_op)
        ],
        DEL_OP: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), received_deop)
        ],
        EVENT_INPUT: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$|^Назад$")), event_input),
            MessageHandler(filters.Regex("^Назад$"), admin),
        ]
    },
    fallbacks=[MessageHandler(filters.Regex("^Отмена$"), admin_cancel)],
)
