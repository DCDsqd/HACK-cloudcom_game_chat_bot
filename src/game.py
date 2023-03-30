import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from common_func import is_available
from database import *

CLASS_CHOOSING, SUBMIT_CLASS, WHERE_CHOOSING, CHRONOS_CHOOSING, SUBCLASS_CHOOSING, TASKS = range(6)


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    con = create_connection('../db/database.db')
    user_id = update.message.from_user.id
    request = f"SELECT game_class FROM users WHERE id={user_id}"
    user_class = execute_read_query(con, request)
    con.close()
    if user_class[0][0] is None:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=open(os.path.abspath('../res/locations/gate.png'), 'rb'),
                                     caption="Добро пожаловать в Великую Империю. Ее выбрали вы, или ее выбрали за вас" \
                                             "— это лучшее государство из оставшихся.\n\n Сейчас Вам нужно получить "
                                             "лицензию на роль класса.")
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
        where_keyboard = [["Дом поручений", "Храм Хроноса", "Лаборатория"],
                          ["Дом гильдий", 'Кузница', 'Рынок'],
                          ['Арена', 'Великая библиотека', 'Зал легионеров'], ["Отмена"]]
        markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
        message = 'С возвращением! Куда отправимся?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return WHERE_CHOOSING


async def class_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    context.user_data["choice"] = text
    inserter('game_class', text, user_id)
    message = f'Вы успешно получили лицензию на роль "{text}".\n\n' \
              "На данный момент вам недоступны все преимущества служителя империи, " \
              "однако не расстраивайтесь, вам будут доступны новые возможности по мере получения следующих рангов. " \
              "Вам предстоит пройти много испытаний и битв, но мы уверены, что вы сможете преодолеть все трудности" \
              " и стать одним из лучших в нашей империи. Желаем Вам удачи!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    where_keyboard = [["Дом поручений", "Храм Хроноса", "Лаборатория"],
                      ["Дом гильдий", 'Кузница', 'Рынок'],
                      ['Арена', 'Великая библиотека', 'Зал легионеров'], ["Отмена"]]
    markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
    message = 'Куда отправимся?'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return WHERE_CHOOSING


async def assignments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = 'Вы подходите к небольшому зданию с вывеской "Дом поручений". ' \
              'При входе Вы замечаете, что на стенах висят доски объявлений с различными заданиями.\n' \
              'Может и получится найти, что-то, что Вам по душе...\n\n' \
              'В одиночку или с друзьями?'
    count_keyboard = [["В одиночку", "С друзьями"], ["Назад"]]
    markup = ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message,
                                   reply_markup=markup)  # Здесь будут задания
    return TASKS


async def alone_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # Сюда добавим одиночные задания


async def multiplayer_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # Сюда добавим мультиплеер задания


async def chronos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 500):
        message = 'Вы подходите к огромному храму, но какая-то неведомая сила не даёт Вам пройти внутрь.\nВозможно, ' \
                  'Вам пока что не хватает опыта.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = 'Добро пожаловать в Храм Хроноса. Здесь вы сможете получить новые навыки для своего персонажа, ' \
                  'а также, по достижении определённого ранга, изменить подкласс.'
        if not is_available(update.message.from_user.id, 2000):  # Если опыт больше 2000, даём доступ к смене подкласса
            chronos_keyboard = [["Улучшить персонажа"], ["Назад"]]
        else:
            chronos_keyboard = [["Улучшить персонажа", "Изменить подкласс"], ["Назад"]]
        markup = ReplyKeyboardMarkup(chronos_keyboard, one_time_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return CHRONOS_CHOOSING


async def upgrade_champ(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass  # Здесь будет улучшение персонажа


async def change_subclass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_available(update.message.from_user.id, 1000):
        con = create_connection('../db/database.db')
        user_id = update.message.from_user.id
        request = f"SELECT game_class FROM users WHERE id={user_id}"
        class_data = execute_read_query(con, request)
        con.close()
        if class_data[0][0] == 'Рыцарь':
            subclass_keyboard = [["Латник", "Паладин"], ["Назад"]]
            message = "Описание подклассов:\n\n" \
                      "⚜️ Латник - упор в защиту, носит массивный щит и меч\n" \
                      "⚔️ Паладин - упор в атаку, носит тяжелые доспехи и молот"

        elif class_data[0][0] == 'Маг':
            subclass_keyboard = [["Чернокнижник", "Элементаль", "Ангел"], ["Назад"]]
            message = "Описание подклассов:\n\n" \
                      "📓 Чернокнижник - упор в атаку, носит книгу\n" \
                      "🔥 Элементаль - упор в контроль, носит посох\n" \
                      "💫 Ангел - упор в поддержку, носит перчатки"
        elif class_data[0][0] == 'Лучник':
            subclass_keyboard = [["Арбалетчик", "Шаман", "Инженер"], ["Назад"]]
            message = "Описание подклассов:\n\n" \
                      "↣ Арбалетчик - упор в атаку, носит автомат, наебал, арбалет\n" \
                      "🏹 Шаман - упор в контроль, носит лук и колчан\n" \
                      "💥 Инженер - упор в поддержку, носит"  # Сюда добавить что носит
        elif class_data[0][0] == 'Охотник':
            subclass_keyboard = [["Убийца", "Шиноби"], ["Назад"]]
            message = "Описание подклассов:\n\n" \
                      "⚔ Убийца - упор в атаку, носит кинжалы\n" \
                      "🗡 Шиноби - упор в атаку и контроль, носит клинок"
        else:
            return logging.error(f"SUBCLASSES DO NOT EXIT FOR CLASS {class_data[0][0]}")
        markup = ReplyKeyboardMarkup(subclass_keyboard, one_time_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return SUBCLASS_CHOOSING
    else:
        message = 'У вас пока что нет доступа к смене подкласса!'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def subclass_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    context.user_data["choice"] = text
    inserter('game_subclass', text, user_id)
    message = f'Вы успешно изменили подкласс на "{text}!"'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def lab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 500):
        message = 'Вы приходите к лаборатории, но дверь оказывается закрытой.\nВозможно, Вам пока что не хватает опыта.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет крафтить расходники


async def guild_house(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 1000):
        message = 'Вы приходите к дому гильдий. По крайней мере так сказал стражник...\nОн не пропускает Вас под ' \
                  'предлогом, что Вы недостаточно опытны.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет запрашивать ресурсы


async def forge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 4000):
        message = 'Вы подходите к кузнице, но мастер-кузнец категорически отказывается принимать Ваш заказ. \n' \
                  'Он объясняет, что его работа требует большого опыта и мастерства, и он не хочет рисковать' \
                  ' испортить изделие.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет крафтить броню и оружие


async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 4000):
        message = 'Вы приходите на рынок, но продавцы не проявляют к Вам интереса.\n' \
                  'Возможно, Ваш опыт в покупке товаров на рынке еще недостаточен, и Вы не знаете, ' \
                  'как правильно торговаться или выбирать качественные товары.\n' \
                  'Вам стоит набраться опыта и знаний, чтобы стать более уверенным и компетентным покупателем.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет покупать товары


async def arena(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 8000):
        message = 'Вы приходите на арену для сражений, но охранник не пускает Вас внутрь.\nОн объясняет, что на арене ' \
                  'сражаются только опытные и знающие свое дело бойцы, и он не хочет допустить риска для Вашей жизни.\n' \
                  'Возможно, Вам еще не хватает опыта и навыков в бою, и Вам стоит потренироваться и набраться опыта, ' \
                  'чтобы доказать свою готовность к сражениям на арене.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет устроить состязание


async def library(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 8000):
        message = 'Вы подходите к великой библиотеке, но библиотекарь отказывается выдать Вам книгу, на которую Вы ' \
                  'хотели бы посмотреть.\nОн объясняет, что для того чтобы обращаться с такими ценностями, как книги, ' \
                  'необходимо обладать определенным уровнем знаний и образования.\nВозможно, Вам еще нужно изучить ' \
                  'некоторые основы науки, чтобы получить доступ к определенным книгам в библиотеке.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет за деньги покупать абилки


async def hall_of_legionnaires(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_available(update.message.from_user.id, 16000):
        message = 'Вы приходите в зал легионеров, но стражник не позволяет Вам войти внутрь.\nОн объясняет, что в зале ' \
                  'собираются только настоящие воины, которые прошли определенные испытания и доказали свою боевую ' \
                  'готовность.\nВозможно, Вам еще не хватает опыта и навыков в бою, чтобы присоединиться к легионерам.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет брать задания легиона (Возможно стоит перенести это в дом поручений)


async def game_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = " До встречи! Мы будем ждать Вас в Империи!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


game_handler = ConversationHandler(
    entry_points=[CommandHandler("game", game)],
    states={
        CLASS_CHOOSING: [
            MessageHandler(filters.Regex("^Рыцарь$|^Маг$|^Лучник$|^Охотник$"), class_choosing),
        ],
        WHERE_CHOOSING: [
            MessageHandler(filters.Regex("^Дом поручений$"), assignments),
            MessageHandler(filters.Regex("^Храм Хроноса$"), chronos),
            MessageHandler(filters.Regex("^Лаборатория$"), lab),
            MessageHandler(filters.Regex("^Дом гильдий$"), guild_house),
            MessageHandler(filters.Regex("^Кузница$"), forge),
            MessageHandler(filters.Regex("^Рынок$"), market),
            MessageHandler(filters.Regex("^Арена$"), arena),
            MessageHandler(filters.Regex("^Великая библиотека$"), library),
            MessageHandler(filters.Regex("^Зал легионеров$"), hall_of_legionnaires),
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
        TASKS: [
            MessageHandler(filters.Regex("^В одиночку$"), alone_tasks),
            MessageHandler(filters.Regex("^С друзьями$"), multiplayer_tasks),
            MessageHandler(filters.Regex("^Назад$"), game),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Отмена$"), game_cancel)],
)