import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from common_func import is_available, merge_photos
from menu_chain import main_menu
from duels import *  # this also imports database
import random

CLASS_CHOOSING, SUBMIT_CLASS, WHERE_CHOOSING, CHRONOS_CHOOSING, SUBCLASS_CHOOSING, TASKS, ALONE_TASK_CHOOSING, \
    MULTIPLAYER_TASK_CHOOSING, ARENA_CHOOSING, GET_USER_TO_DUEL_ID, GET_CHAT_ID = range(11)

TOTAL_VOTER_COUNT = 3

POLL_INPUT = range(1)


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    con = create_connection('../db/database.db')
    user_id = update.message.from_user.id
    request = f"SELECT game_class FROM users WHERE id={user_id}"
    user_class = execute_read_query(con, request)
    con.close()
    if user_class[0][0] is None or user_class[0][0] == '':
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
        all_buildings = db.select_all_buildings()
        where_keyboard = []
        for i in range(2, len(all_buildings) // 3 * 3, 3):
            where_keyboard.append([all_buildings[i - 2][1], all_buildings[i - 1][1], all_buildings[i][1]])

        residue_of_buildings = []
        for i in range(len(all_buildings) // 3 * 3 + 1, len(all_buildings)):
            residue_of_buildings.append(all_buildings[i][1])

        where_keyboard.append(residue_of_buildings)
        where_keyboard.append(["Отмена"])
        markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
        message = 'С возвращением! Куда отправимся?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return WHERE_CHOOSING


async def class_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    user_id = update.message.from_user.id
    context.user_data["choice"] = text
    db.update_users('game_class', text, user_id)
    message = f'Вы успешно получили лицензию на роль "{text}".\n\n' \
              "На данный момент Вам недоступны все преимущества служителя империи, " \
              "однако не расстраивайтесь, Вам будут доступны новые возможности по мере получения следующих рангов. " \
              "Вам предстоит пройти много испытаний и битв, но мы уверены, что Вы сможете преодолеть все трудности" \
              " и стать одним из лучших в нашей империи. Желаем Вам удачи!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    where_keyboard = [["Дом поручений", "Храм Хроноса", "Лаборатория"],
                      ["Дом гильдий", 'Кузница', 'Рынок'],
                      ['Арена', 'Великая библиотека', 'Зал легионеров'], ["Отмена"]]
    markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
    message = 'Куда отправимся?'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return WHERE_CHOOSING


async def assignments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = 'Вы подходите к небольшому зданию с вывеской "Дом поручений". ' \
              'При входе Вы замечаете, что на стенах висят доски объявлений с различными заданиями.\n' \
              'Может и получится найти, что-то, что Вам по душе...\n\n' \
              'В одиночку или с друзьями?'
    count_keyboard = [["В одиночку", "С друзьями"], ["Назад"]]
    markup = ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message,
                                   reply_markup=markup)
    return TASKS


async def alone_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    if db.check_if_need_to_update_daily_tasks(user_id):
        db.regenerate_daily_tasks(user_id)

    tasks = db.get_cur_user_tasks(user_id)
    task_labels = {
        'small': "Мелкое поручение",
        'medium': "Среднее поручение",
        'class_license': "Классовая лицензия"
    }

    message = f"Доступные ежедневные задания ({cur_date()}):\n\n"
    no_tasks_available = True

    for task_id, label in task_labels.items():
        if tasks[task_id] != -1:
            task = db.get_task_by_id(tasks[task_id])
            message += f"{label}:\n" \
                       f"Название: {task[1]}\n" \
                       f"Описание: {task[2]}\n" \
                       f"Сложность: {task[3]}\n" \
                       f"Награда опытом: {task[4]}\n" \
                       f"Награда предметом: {task[5]}\n\n"
            no_tasks_available = False

    if no_tasks_available:
        message += 'К сожалению, на сегодня у Вас больше нет заданий.\n' \
                   'Возвращайтесь завтра!'
    else:
        message += 'Какое задание хотите взять?'

    all_tasks_labels = [label for task_id, label in task_labels.items() if tasks[task_id] != -1]
    alone_tasks_keyboard = [all_tasks_labels[:2], all_tasks_labels[2:3], ["Назад"]] if len(all_tasks_labels) >= 2 else [
        all_tasks_labels, ["Назад"]]

    markup = ReplyKeyboardMarkup(alone_tasks_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return ALONE_TASK_CHOOSING


async def multiplayer_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    multiplayer_tasks_keyboard = [["Дело особой важности", "Сбор ресурсов"], ["Назад"]]
    tasks = db.get_tasks(1)
    special_tasks = [task for task in tasks if task[6] == 'special']
    random_tasks = [task for task in tasks if task[6] == 'random']
    special_task = random.choice(special_tasks)
    random_task = random.choice(random_tasks)
    message = f"Доступные задания:\n\n" \
              f"Дело особой важности:\n" \
              f"Название: {special_task[1]}\n" \
              f"Описание: {special_task[2]}\n" \
              f"Сложность: {special_task[3]}\n" \
              f"Награда опытом: {special_task[4]}\n" \
              f"Награда предметом: {special_task[5]}\n\n" \
              f"Сбор ресурсов (АФК):\n" \
              f"Описание: {random_task[2]}\n" \
              f"Сложность: {random_task[3]}\n" \
              f"Награда опытом: {random_task[4]}\n" \
              f"Награда предметом: {random_task[5]}\n\n"
    markup = ReplyKeyboardMarkup(multiplayer_tasks_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return MULTIPLAYER_TASK_CHOOSING


async def chronos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('Chronos', update.effective_chat.id))
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


async def subclass_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
    context.user_data["choice"] = text
    db.update_users('game_subclass', text, user_id)
    message = f'Вы успешно изменили подкласс на "{text}!"'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def lab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 500):
        message = 'Вы приходите к лаборатории, но дверь оказывается закрытой.\nВозможно, Вам пока что не хватает опыта.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('Lab', update.effective_chat.id))
        pass  # Здесь можно будет крафтить расходники


async def guild_house(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 1000):
        message = 'Вы приходите к дому гильдий. По крайней мере так сказал стражник...\nОн не пропускает Вас под ' \
                  'предлогом, что Вы недостаточно опытны.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('GuildHouse', update.effective_chat.id))
        pass  # Здесь можно будет запрашивать ресурсы


async def forge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 4000):
        message = 'Вы подходите к кузнице, но мастер-кузнец категорически отказывается принимать Ваш заказ. \n' \
                  'Он объясняет, что его работа требует большого опыта и мастерства, и он не хочет рисковать' \
                  ' испортить изделие.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('AnvilHouse', update.effective_chat.id))
        pass  # Здесь можно будет крафтить броню и оружие


async def market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 4000):
        message = 'Вы приходите на рынок, но продавцы не проявляют к Вам интереса.\n' \
                  'Возможно, Ваш опыт в покупке товаров на рынке еще недостаточен, и Вы не знаете, ' \
                  'как правильно торговаться или выбирать качественные товары.\n' \
                  'Вам стоит набраться опыта и знаний, чтобы стать более уверенным и компетентным покупателем.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('Market', update.effective_chat.id))
        pass  # Здесь можно будет покупать товары


arena_keyboard = [['Вызвать на дуэль', 'Создать открытую дуэль'], ['Назад']]
back_keyboard = [['Назад']]


async def arena(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 8000):
        message = 'Вы приходите на арену для сражений, но охранник не пускает Вас внутрь.\nОн объясняет, что на арене ' \
                  'сражаются только опытные и знающие свое дело бойцы, и он не хочет допустить риска для Вашей жизни.\n' \
                  'Возможно, Вам еще не хватает опыта и навыков в бою, и Вам стоит потренироваться и набраться опыта, ' \
                  'чтобы доказать свою готовность к сражениям на арене.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('Arena', update.effective_chat.id))
        markup = ReplyKeyboardMarkup(arena_keyboard, one_time_keyboard=True)
        message = 'Выберите действие'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return ARENA_CHOOSING


async def challenge_to_duel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Введите ID игрока, которого хотите вызвать на дуэль"
    markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return GET_USER_TO_DUEL_ID


async def get_user_duel_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    getting_user_id = update.message.text
    if not getting_user_id.isdigit():
        response = "ID должен быть числовым значением!"
        markup = ReplyKeyboardMarkup(arena_keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return ARENA_CHOOSING
    if not db.check_if_could_send_duel(update.message.from_user.id, getting_user_id):
        response = "Невозможно отрпавить запрос данному игроку. Запрос уже отправлен или бой уже идёт."
        markup = ReplyKeyboardMarkup(arena_keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return ARENA_CHOOSING
    db.add_pending_duel(update.message.from_user.id, getting_user_id)
    message = "Запрос на дуэль успешно отправлен"
    markup = ReplyKeyboardMarkup(arena_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    message = f"Игрок с ID {update.effective_chat.id} вызывает вас на дуэль!"
    keyboard = [
        [
            InlineKeyboardButton("Принять", callback_data="accept"),
            InlineKeyboardButton("Отклонить", callback_data="reject"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=getting_user_id, text=message, reply_markup=reply_markup)
    return ARENA_CHOOSING


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    receiver_id = query.from_user.id
    await query.answer()
    if query.data == "accept":
        # init_duel(Duel(duel_id, sender_id, receiver_id))
        # Здесь нужно сделать добавление в бд статуса "принято"
        await query.edit_message_text(text=f"Вы приняли приглашение на дуэль!")
    elif query.data == "reject":
        await query.edit_message_text(text=f"Вы отклонили приглашение на дуэль!")


async def create_open_duel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True)
    message = "Доступные чаты для открытой дуэли: \n\n"
    chats = db.get_chat_ids()
    for chat in chats:
        message += f"{str(chat[2])}: {str(chat[1])}\n"
    message += "\nВведите ID чата, в который хотите отправить приглашение!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return GET_CHAT_ID


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    getting_chat_id = update.message.text
    if not getting_chat_id[1:].isdigit():
        response = "ID должен быть числовым значением!"
        markup = ReplyKeyboardMarkup(arena_keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response, reply_markup=markup)
        return ARENA_CHOOSING
    message = "Запрос на дуэль успешно отправлен"
    db.add_pending_duel(update.effective_chat.id, 0)
    markup = ReplyKeyboardMarkup(arena_keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    message = f"Игрок с ID {update.effective_chat.id} создал открытую дуэль!"
    keyboard = [
        [
            InlineKeyboardButton("Принять", callback_data="accept")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=getting_chat_id, text=message, reply_markup=reply_markup)
    return ARENA_CHOOSING


async def library(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 8000):
        message = 'Вы подходите к великой библиотеке, но библиотекарь отказывается выдать Вам книгу, на которую Вы ' \
                  'хотели бы посмотреть.\nОн объясняет, что для того чтобы обращаться с такими ценностями, как книги, ' \
                  'необходимо обладать определенным уровнем знаний и образования.\nВозможно, Вам еще нужно изучить ' \
                  'некоторые основы науки, чтобы получить доступ к определенным книгам в библиотеке.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет за деньги покупать абилки


async def hall_of_legionnaires(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_available(update.message.from_user.id, 16000):
        message = 'Вы приходите в зал легионеров, но стражник не позволяет Вам войти внутрь.\nОн объясняет, что в зале ' \
                  'собираются только настоящие воины, которые прошли определенные испытания и доказали свою боевую ' \
                  'готовность.\nВозможно, Вам еще не хватает опыта и навыков в бою, чтобы присоединиться к легионерам.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        pass  # Здесь можно будет брать задания легиона (Возможно стоит перенести это в дом поручений)


game_handler = ConversationHandler(
    entry_points=[CommandHandler("game", game),
                  MessageHandler(filters.Regex("^Игра$"), game)],
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
        ALONE_TASK_CHOOSING: [
            # ADD MORE FUNCTIONS
            MessageHandler(filters.Regex("^Назад$"), assignments),
        ],
        MULTIPLAYER_TASK_CHOOSING: [
            # ADD MORE FUNCTIONS
            MessageHandler(filters.Regex("^Назад$"), assignments),
        ],
        ARENA_CHOOSING: [
            MessageHandler(filters.Regex("^Вызвать на дуэль$"), challenge_to_duel),
            MessageHandler(filters.Regex("^Создать открытую дуэль$"), create_open_duel),
            MessageHandler(filters.Regex("^Назад$"), game),
        ],
        GET_USER_TO_DUEL_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_user_duel_id),
            MessageHandler(filters.Regex("^Назад$"), arena),
        ],
        GET_CHAT_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_chat_id),
            MessageHandler(filters.Regex("^Назад$"), arena),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Отмена$"), main_menu)],
)
