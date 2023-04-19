from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

menu_keyboard = [['Кастомизация', 'Игра'], ['Друзья', 'События']]


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = " Вы вернулись в главное меню!"
    markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return ConversationHandler.END

