from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

menu_keyboard = [['Кастомизация', 'Игра'], ['Друзья', 'События'], ['Инвентарь', 'Рейтинг']]

menu_markup = ReplyKeyboardMarkup(menu_keyboard, one_time_keyboard=False)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = " Вы вернулись в главное меню!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=menu_markup)
    return ConversationHandler.END
