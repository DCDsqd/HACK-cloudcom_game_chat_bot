from datebase import *
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from customization import custom_name_handler, avatar_handler
from common_func import start, main_menu, profile, help_me, upgrade, fight, danet, netda, meme

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY, CUSTOM_AVATAR_CHOICE = range(5)

CLASS_CHOOSING, SUBMIT_CLASS, WHERE_CHOOSING = range(3)


async def del_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Клавиатура удалена! (Юра пидор)', reply_markup=ReplyKeyboardRemove())

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    user_id = update.message.from_user.id
    request = f"SELECT game_class FROM users WHERE id={user_id}"
    user_class = execute_read_query(con, request)
    con.close()
    if user_class[0][0] is None:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(os.path.abspath('../res/locations/gate.png'), 'rb'),
                                     caption="Добро пожаловать в Великую Империю. Ее выбрали вы, или ее выбрали за вас" \
                                             " — это лучшее государство из оставшихся.\n\n Сейчас Вам нужно получить лицензию на роль класса.")
        classes_description = "Доступные классы:\n\n" \
                              "🛡 Рыцарь — высокая защита и средняя атака. Носит небольшой щит и меч.\n" \
                              "🧙 Маг — высокая поддержка, атака ниже среднего, низкая защита. Носит посох.\n" \
                              "🏹 Лучник — высокий контроль, атака ниже среднего, низкая защита. Носит лук (вау).\n" \
                              "🗡 Охотник — высокая атака, защита ниже среднего, носит клинок.\n\n" \
                              "Что выберете?"
        class_keyboard = [["Рыцарь", "Маг", "Лучник", "Охотник"], ["Отмена"]]
        markup = ReplyKeyboardMarkup(class_keyboard, one_time_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=classes_description, reply_markup=markup)
        return CLASS_CHOOSING
    else:
        where_keyboard = [["Дом поручений", "Храм Хроноса", "Лаборатория", "Дом гильдий"],
                          ['Кузница', 'Рынок', 'Арена', 'Великая библиотека'], ["Отмена"]]
        markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
        message = 'С возвращением! Куда отправимся?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return WHERE_CHOOSING


async def class_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    context.user_data["choice"] = text
    print(text)
    inserter('game_class', text, user_id)
    message = f'Вы успешно получили лицензию на роль "{text}".\n\n' \
              "На данный момент вам недоступны все преимущества служителя империи, " \
              "однако не расстраивайтесь, вам будут доступны новые возможности по мере получения следующих рангов. " \
              "Вам предстоит пройти много испытаний и битв, но мы уверены, что вы сможете преодолеть все трудности" \
              " и стать одним из лучших в нашей империи. Желаем Вам удачи!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    where_keyboard = [["Дом поручений", "Храм Хроноса", "Лаборатория", "Дом гильдий"],
                      ['Кузница', 'Рынок', 'Арена', 'Великая библиотека'], ["Отмена"]]
    markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
    message = 'Куда отправимся?'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return WHERE_CHOOSING


async def assignments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = 'Вы подходите к небольшому зданию с вывеской "Дом поручений". ' \
              'При входе Вы замечаете, что на стенах висят доски объявлений с различными заданиями.\n' \
              'Может и получится найти, что-то Вам по душе...'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def game_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = " До встречи! Мы будем ждать Вас в Империи!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    token_file = open("../tokens/tg_app_token.txt", "r")
    application = ApplicationBuilder().token(token_file.read()).build()
    token_file.close()
    class_handler = ConversationHandler(
        entry_points=[CommandHandler("game", game)],
        states={
            CLASS_CHOOSING: [
                MessageHandler(filters.Regex("^Рыцарь$|^Маг$|^Лучник$|^Охотник$"), class_choosing),
            ],
            WHERE_CHOOSING: [
                MessageHandler(filters.Regex("^Дом поручений$"), assignments),
                #  Сюда добавим все остальные локации
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), game_cancel)],
    )
    application.add_handler(class_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_me))
    application.add_handler(CommandHandler('game', game))
    application.add_handler(custom_name_handler)
    application.add_handler(avatar_handler)
    application.add_handler(CommandHandler('upgrade', upgrade))
    application.add_handler(MessageHandler(filters.Regex("^Да$|^да$"), danet))
    application.add_handler(MessageHandler(filters.Regex("^Нет$|^нет$"), netda))
    application.add_handler(CommandHandler('meme', meme))
    application.add_handler(CommandHandler('del', del_keyboard))
    application.add_handler(CommandHandler('menu', main_menu))
    application.add_handler(CommandHandler('fight', fight))
    application.add_handler(CommandHandler('profile', profile))
    application.run_polling()
