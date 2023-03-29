# use this file to create functions used to help admins manage global events & other admin-related stuff
from database import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

ADMIN_CHOOSING, OP = range(2)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    user_id = update.message.from_user.id
    request = f"SELECT admin FROM users WHERE id={user_id}"
    is_admin = int(execute_read_query(con, request)[0][0])
    con.close()
    if is_admin:
        admin_keyboard = [["Добавить событие", "Добавить администратора"], ["Отмена"]]
        markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
        message = "Доступ получен. Меню администратора:"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return ADMIN_CHOOSING
    else:
        message = "В доступе отказано!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Все изменения применены. Хорошего дня!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    return ConversationHandler.END


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # Здесь будет добавление событий


async def op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "Для безопасности, требуется ввести ID игрока.\nЕго можно узнать с помощью команды /profile"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text("Введите ID игрока:")
    return OP


async def received_op(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    query = f"""
                SELECT id FROM users
                """
    res = execute_read_query(con, query)
    all_ids = []
    for i in range(len(res)):
        all_ids.append(res[i][0])
    admin_keyboard = [["Добавить событие", "Добавить администратора"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(admin_keyboard, one_time_keyboard=True)
    new_admin_id = int(update.message.text)
    if new_admin_id in all_ids:
        context.user_data["admin"] = new_admin_id
        inserter('admin', 1, new_admin_id)
        await update.message.reply_text(f"Пользователь с ID: {new_admin_id} теперь администратор.", reply_markup=markup)
    else:
        await update.message.reply_text(f"Пользователя с ID: {new_admin_id} не существует!", reply_markup=markup)
    return ADMIN_CHOOSING


admin_handler = ConversationHandler(
    entry_points=[CommandHandler("admin", admin)],
    states={
        ADMIN_CHOOSING: [
            MessageHandler(filters.Regex("^Добавить событие$"), add_event),
            MessageHandler(filters.Regex("^Добавить администратора$"), op),
        ],
        OP: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), received_op)
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Отмена$"), admin_cancel)],
)


def parse_new_event_info_string(text):
    mins_in_year = 525600
    fields = text.split('\n')

    if len(fields) != 5:
        return {False, 'Вы указали недостаточно информации о новом событии. '
                       'Возможно, вы забыли разделить информацию с помощью Shift+Enter, либо пропустили какое-то из '
                       'полей.'}

    name = fields[0]
    if len(name) > 50:
        return {False, 'Вы указали слишком длинное имя для события. Оно не должно превышать 50 символов.'}

    descr = fields[1]
    if len(descr) > 500:
        return {False, 'Вы указали слишком длинное описание для события. Оно не должно превышать 500 символов.'}

    start_time = fields[2]
    if not ensure_time_format(start_time):
        return {False, 'Указанное вами время события не прошло проверку на правильность формата.'
                       'Не забывайте, что формат должен СТРОГО соответствовать следующему формату: yyyy-MM-dd hh:mm:ss'}

    duration = fields[3]
    if not duration.isdigit():
        return {False, 'Указанная вами продолжительность события не является числом.'}
    if int(duration) < 1:
        return {False, 'Продолжительность события не может быть меньше 1 минуты.'}
    if int(duration) > mins_in_year:
        return {False, f"""Продолжительность события не может быть больше года ('{mins_in_year}' минут)."""}

    exp_reward = fields[4]
    if not exp_reward.isdigit():
        return {False, 'Указанная вами награда в опыте за событие не является числом.'}
    if int(exp_reward) < 0:
        return {False, 'Награда в опыте за событие не может быть отрицательной.'}

    return {True, 'Все поля валидны.'}
