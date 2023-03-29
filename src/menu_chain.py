from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from database import *
import logging
from bot import inserter, game_cancel, start, help_me, game, danet, netda, meme, del_keyboard, profile, \
    assignments, class_choosing, chronos, lab, guild_house, upgrade_champ, change_subclass, subclass_choosing
from customization import custom_name_choice, custom_avatar, custom_avatar_body, custom_avatar_face, \
    custom_avatar_hair, received_body_choice, received_face_choice, received_hair_choice, enter_change, regen_avatar
from telegram.ext import ContextTypes
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

AVATAR_CHANGE = range(1)
MENU = range(1)
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY, CUSTOM_AVATAR_CHOICE = range(5)
CLASS_CHOOSING, SUBMIT_CLASS, WHERE_CHOOSING, CHRONOS_CHOOSING, SUBCLASS_CHOOSING = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Начать"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    message = update.message
    user = message.from_user
    user_id = message.from_user.id
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
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Добро пожаловать в Team Builder Bot! Нажмите начать, если готовы отправиться "
                                        "в путешествие",
                                   reply_markup = markup)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Играть"], ["Кастомизация"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Нажмите кастомизация, если хотите изменить персонажа\n Нажмите начать, "
                                    "если хотите начать игру", reply_markup=markup)
    return MENU

async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["name"] = text
    user_id = update.message.from_user.id
    inserter('personal_username', text, user_id)
    await update.message.reply_text(f"Имя изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed personal name on {text}")
    return ConversationHandler.END

async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return AVATAR_CHANGE

async def custom_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Играть"], ["Кастомизация"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Нажмите кастомизация, если хотите изменить персонажа\n Нажмите начать, "
                                    "если хотите начать игру", reply_markup=markup)
    return ConversationHandler.END

def get_custom_name_handler(text):
    custom_name_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{text}$"), custom_name_choice)],
        states={
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Отмена$")), received_name)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), main_menu)],
    )
    return custom_name_handler

def get_avatar_handler(text):
    avatar_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{text}$"), custom_avatar)],
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
                MessageHandler(
                    filters.Regex("^Подтвердить$") & ~filters.COMMAND,
                    custom_avatar,
                ),
            ],
            TYPING_FACE: [
                MessageHandler(
                    filters.Regex("^Вариант 1$|^Вариант 2$|^Вариант 3$|^Вариант 4$|^Вариант 5$") & ~filters.COMMAND,
                    received_face_choice,
                ),
                MessageHandler(
                    filters.Regex("^Подтвердить$") & ~filters.COMMAND,
                    custom_avatar,
                ),
            ],
            TYPING_BODY: [
                MessageHandler(
                    filters.Regex("^Вариант 1$|^Вариант 2$|^Вариант 3$|^Вариант 4$|^Вариант 5$") & ~filters.COMMAND,
                    received_body_choice,
                ),
                MessageHandler(
                    filters.Regex("^Подтвердить$") & ~filters.COMMAND,
                    custom_avatar,
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Назад$"), enter_change),
                   MessageHandler(filters.Regex("^Подтвердить$"), custom_avatar)],
    )
    return avatar_handler

def get_class_handler(text):
    class_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{text}"), game)],
        states={
            CLASS_CHOOSING: [
                MessageHandler(filters.Regex("^Рыцарь$|^Маг$|^Лучник$|^Охотник$"), class_choosing),
            ],
            WHERE_CHOOSING: [
                MessageHandler(filters.Regex("^Дом поручений$"), assignments),
                MessageHandler(filters.Regex("^Храм Хроноса$"), chronos),
                MessageHandler(filters.Regex("^Лаборатория$"), lab),
                MessageHandler(filters.Regex("^Дом гильдий$"), guild_house),
                #  Сюда добавим все остальные локации
            ],
            CHRONOS_CHOOSING: [
                MessageHandler(filters.Regex("^Улучшить персонажа$"), upgrade_champ),
                MessageHandler(filters.Regex("^Изменить подкласс$"), change_subclass),
                MessageHandler(filters.Regex("^Назад$"), game),
            ],
            SUBCLASS_CHOOSING: [
                MessageHandler(filters.Regex(
                    "^Латник$|^Паладин$|^Чернокнижник$|^Элементаль$|^Ангел$|^Арбалетчик$|^Шаман$|^Инженер$|^Убийца$"
                    "|^Шиноби$"),
                    subclass_choosing),
                MessageHandler(filters.Regex("^Назад$"), chronos),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), game_cancel)],
    )
    return class_handler

def get_custom_handler(text):
    custom_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{text}"), custom)],
        states={
            AVATAR_CHANGE: [
                get_avatar_handler("Изменить аватара"),
                get_custom_name_handler("Изменить имя"),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), custom_end)],
    )
    return custom_handler

def get_main_menu_handler(text):
    main_menu_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(f"^{text}"), main_menu)],
        states={
            MENU: [
                get_custom_handler("Кастомизация"),
                get_class_handler("Играть")
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), game_cancel)],
    )
    return main_menu_handler

if __name__ == '__main__':
    token_file = open("../tokens/tg_app_token.txt", "r")
    application = ApplicationBuilder().token(token_file.read()).build()
    token_file.close()

    custom_handler = get_main_menu_handler('Начать')
    application.add_handler(custom_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_me))
    application.add_handler(CommandHandler('game', game))

    application.add_handler(MessageHandler(filters.Regex("^Да$|^да$"), danet))
    application.add_handler(MessageHandler(filters.Regex("^Нет$|^нет$"), netda))
    application.add_handler(CommandHandler('meme', meme))

    application.add_handler(CommandHandler('del', del_keyboard))
    application.add_handler(CommandHandler('profile', profile))
    application.run_polling()
