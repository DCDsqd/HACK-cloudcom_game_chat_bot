from database import *
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from menu_chain import main_menu

FRIENDS_CHOOSING, ADD_FRIEND_REQUEST, DELETE_FRIEND_REQUEST, ACCEPT_AND_DENY, ACCEPT_FRIEND_REQUEST, DENY_FRIEND_REQUEST, \
    DENY = range(7)
back_keyboard = [['Назад']]
friends_keyboard = [['Посмотреть список друзей'], ['Добавить друга', 'Удалить друга'],
                    ['Входящие запросы', 'Исходящие запросы'], ['Назад']]
accept_deny_keyboard = [['Принять запрос', 'Отклонить запрос'], ['Назад']]
cancel_request_keyboard = [['Отменить запрос'], ['Назад']]


# This function returns an integer value of FRIENDS_CHOOSING. Inside the function, it sends a message to the user
# with a keyboard markup of the options available for the friends feature.
async def friends_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = "Выберите действие"
    markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return FRIENDS_CHOOSING


# This is an async Python function that retrieves a user's friends list and sends it as a message to a chat using a bot.
async def get_friends_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = "Ваш список друзей:\n\n"
    friend_list = db.get_friend_list_ids(update.message.from_user.id)
    if len(friend_list) == 0:
        response = "У Вас нет друзей :("
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    else:
        for i in range(len(friend_list)):
            response += f"{db.get_user_nick(friend_list[i])} - {str(friend_list[i])}\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


# It sends a message to the user asking for an ID to add a friend. It also returns a constant ADD_FRIEND_REQUEST
async def create_friend_request_function(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = "Введите ID игрока, которого хотите добавить в друзья"
    markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return ADD_FRIEND_REQUEST


# This function sends a friend request from the user to the specified user ID, sends a message to the user informing
# them that the friend request has been sent successfully, and returns a constant FRIENDS_CHOOSING. If the user ID is
# not numeric, it sends a message to the user informing them that the ID should be numeric.
async def friend_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
    getting_user_id = update.message.text
    if not getting_user_id.isdigit():
        response = "ID должен быть числовым значением!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return FRIENDS_CHOOSING
    getting_user_id = int(getting_user_id)
    db.create_friend_request(update.message.from_user.id, getting_user_id)
    response = "Запрос успешно отправлен!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return FRIENDS_CHOOSING


# It sends a message to the user asking for an ID to delete a friend. It also returns a constant DELETE_FRIEND_REQUEST
async def create_friend_deletion_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = "Введите ID игрока, которого хотите удалить из друзей"
    markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return DELETE_FRIEND_REQUEST


# This function processes the user ID received from the user, deletes the friendship between the users if the ID is
# valid, sends a message to the user informing them of the status, and returns a constant FRIENDS_CHOOSING
async def delete_friend_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
    getting_user_id = update.message.text
    if not getting_user_id.isdigit():
        response = "ID должен быть числовым значением!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return FRIENDS_CHOOSING
    getting_user_id = int(getting_user_id)
    db.delete_from_friends(update.message.from_user.id, getting_user_id)
    response = f"Пользователь с ID {getting_user_id} больше не является Вашим другом."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return FRIENDS_CHOOSING


# This function retrieves a list of incoming friend requests and sends a message to the user with the list of
# requests and options to cancel them if any exist.
async def get_incoming_friends_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    incoming_requests = db.get_incoming_pending_friend_requests(update.message.from_user.id)
    if not incoming_requests:
        response = "У вас нет входящих запросов на дружбу."
        markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return FRIENDS_CHOOSING
    else:
        response = "Входящие запросы от пользователей с ID:\n\n" + "\n".join(
            str(ids) for ids in incoming_requests) + "\n\nВыберите действие:"
        markup = ReplyKeyboardMarkup(accept_deny_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return ACCEPT_AND_DENY


# This function retrieves a list of outgoing friend requests and sends a message to the user with the list of
# requests and options to cancel them if any exist.
async def get_outgoing_friends_requests(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    outgoing_requests = db.get_outgoing_pending_friend_requests(update.message.from_user.id)
    if len(outgoing_requests) == 0:
        response = "У вас нет исходящих запросов на дружбу."
        markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    else:
        response = "Исходящие запросы пользователям с ID:\n\n"
        for i in range(len(outgoing_requests)):
            response += str(outgoing_requests[i]) + "\n"
        response += "\nВыберите действие:"
        markup = ReplyKeyboardMarkup(cancel_request_keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return DENY


# It sends a message to the user asking for an ID to accept a friend request. It also returns a constant
# ACCEPT_FRIEND_REQUEST
async def accept_friend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = "Введите ID человека, от которого хотите принять запрос"
    markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return ACCEPT_FRIEND_REQUEST


# This function is responsible for processing the ID received from the user. It first checks if the ID is a valid
# number, and if not, it sends a message informing the user. If the ID is valid, it calls accept_friend_request
# function and sends a response message indicating that the friend request from the specified user ID has been
# accepted. Finally, it returns a constant FRIENDS_CHOOSING
async def get_accepted_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
    getting_user_id = update.message.text
    if not getting_user_id.isdigit():
        response = "ID должен быть числовым значением!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return FRIENDS_CHOOSING
    db.accept_friend_request(update.message.from_user.id, int(getting_user_id))
    response = f"Пользователь с ID {getting_user_id} теперь Ваш друг"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return FRIENDS_CHOOSING


# It sends a message to the user asking for an ID to reject a friend request. It also returns a constant
# DENY_FRIEND_REQUEST
async def deny_friend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = "Введите ID человека, от которого/к которому хотите отклонить/отменить запрос"
    markup = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return DENY_FRIEND_REQUEST


# This function is responsible for processing the ID received from the user. It first checks if the ID is a valid
# number, and if not, it sends a message informing the user. If the ID is valid, it calls delete_from_friends
# function and sends a response message indicating that the friend request from the specified user ID has been
# rejected. Finally, it returns a constant FRIENDS_CHOOSING
async def get_denied_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    markup = ReplyKeyboardMarkup(friends_keyboard, resize_keyboard=True)
    getting_user_id = update.message.text
    if not getting_user_id.isdigit():
        response = "ID должен быть числовым значением!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return FRIENDS_CHOOSING
    db.delete_from_friends(update.message.from_user.id, int(getting_user_id))
    response = f"Запрос от пользователя с ID {getting_user_id} отклонён."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
    return FRIENDS_CHOOSING


# This is a ConversationHandler that defines the conversation flow for the "Friends" feature in a chatbot. The
# conversation flow starts with the friends function triggered by the "/friends" command. The conversation has
# several states that depend on the user's input. For example, if the user chooses to add a friend, the conversation
# flow will go to the ADD_FRIEND_REQUEST state, where the user will input the friend's ID. The conversation flow is
# defined by several MessageHandler objects that check for user input and execute the appropriate function based on
# the current state. The fallbacks parameter specifies the fallback MessageHandler for when the user input does not
# match any of the defined states.
friends_handler = ConversationHandler(
    entry_points=[CommandHandler("friends", friends_menu),
                  MessageHandler(filters.Regex("^Друзья$"), friends_menu)],
    states={
        FRIENDS_CHOOSING: [
            MessageHandler(filters.Regex("^Посмотреть список друзей$"), get_friends_list),
            MessageHandler(filters.Regex("^Добавить друга$"), create_friend_request_function),
            MessageHandler(filters.Regex("^Удалить друга$"), create_friend_deletion_request),
            MessageHandler(filters.Regex("^Входящие запросы$"), get_incoming_friends_requests),
            MessageHandler(filters.Regex("^Исходящие запросы$"), get_outgoing_friends_requests),
        ],
        ADD_FRIEND_REQUEST: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), friend_request),
            MessageHandler(filters.Regex("^Назад$"), friends_menu),
        ],
        DELETE_FRIEND_REQUEST: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), delete_friend_request),
            MessageHandler(filters.Regex("^Назад$"), friends_menu),
        ],
        ACCEPT_AND_DENY: [
            MessageHandler(filters.Regex("^Принять запрос$"), accept_friend),
            MessageHandler(filters.Regex("^Отклонить запрос$"), deny_friend),
            MessageHandler(filters.Regex("^Назад$"), friends_menu),
        ],
        ACCEPT_FRIEND_REQUEST: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_accepted_id),
            MessageHandler(filters.Regex("^Назад$"), friends_menu),
        ],
        DENY_FRIEND_REQUEST: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_denied_id),
            MessageHandler(filters.Regex("^Назад$"), friends_menu),
        ],
        DENY: [
            MessageHandler(filters.Regex("^Назад$"), friends_menu),
            MessageHandler(filters.Regex("^Отменить запрос$"), deny_friend),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
)
