from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY, CUSTOM_AVATAR_CHOICE = range(5)

def menu_chain(custom):
    custom_name_handler = ConversationHandler(
        entry_points=[CommandHandler("custom", custom)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Изменить имя$"), custom_name_choice),
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), received_name, )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), main_menu)],
    )
    return custom_name_handler


def avatar_chain():
    avatar_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Изменить аватара$'), custom_avatar)],
        states={
            CHOOSING_AVATAR: [
                MessageHandler(filters.Regex("^Изменить волосы$"), custom_avatar_hair),
                MessageHandler(filters.Regex("^Изменить лицо$"), custom_avatar_face),
                MessageHandler(filters.Regex("^Изменить тело$"), custom_avatar_body),
            ],
            TYPING_HAIR: [
                MessageHandler(
                    filters.Regex("^Вариант 1$|^Вариант 2$|^Вариант 3$|^Вариант 4$|^Вариант 5$") & ~filters.COMMAND,
                    received_hair_choice,
                ),
            ],
            TYPING_FACE: [
                MessageHandler(
                    filters.Regex("^Вариант 1$|^Вариант 2$|^Вариант 3$|^Вариант 4$|^Вариант 5$") & ~filters.COMMAND,
                    received_face_choice,
                ),
            ],
            TYPING_BODY: [
                MessageHandler(
                    filters.Regex("^Вариант 1$|^Вариант 2$|^Вариант 3$|^Вариант 4$|^Вариант 5$") & ~filters.COMMAND,
                    received_body_choice,
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Назад$"), custom),
                   MessageHandler(filters.Regex("^Подтвердить$"), custom_avatar)],
    )
    return avatar_handler

