import logging
import os
import re
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import telegram.error

from common_func import check_if_user_exp_is_enough, merge_photos, attacks_markup
from menu_chain import main_menu
from duels import *  # this also imports database
from equipment import switch_equip_type_to_russian
import random

CLASS_CHOOSING, SUBMIT_CLASS, WHERE_CHOOSING, CHRONOS_CHOOSING, SUBCLASS_CHOOSING, TASKS, ALONE_TASK_CHOOSING, \
    MULTIPLAYER_TASK_CHOOSING, ARENA_CHOOSING, GET_USER_TO_DUEL_ID, GET_CHAT_ID, GET_USER_FOR_SPECIAL_MULTIPLAYER_ID, \
    GET_USER_FOR_RANDOM_MULTIPLAYER_ID, INVENTORY_CHOOSING, LAB_CHOOSING, GETTING_ITEM_ID, GUILD_CHOOSING, \
    GUILD_REQUEST, GUILD_ID_GETTING, FORGE_CHOOSING, ITEM_INPUT = range(21)

TOTAL_VOTER_COUNT = 3

POLL_INPUT = range(1)


async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_class = db.get_player_class_by_id(user_id)
    if user_class is None or user_class == '':
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
        class_keyboard = [["Рыцарь", "Маг", "Лучник", "Охотник"], ["Назад"]]
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
        where_keyboard.append(["Назад"])
        markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
        message = 'С возвращением! Куда отправимся?'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return WHERE_CHOOSING


async def class_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    class_name = update.message.text
    user_id = update.message.from_user.id
    context.user_data["choice"] = class_name
    db.update_users('game_class', class_name, user_id)
    db.give_default_items_to_user(user_id, class_name)
    message = f'Вы успешно получили лицензию на роль "{class_name}".\n\n' \
              "На данный момент Вам недоступны все преимущества служителя империи, " \
              "однако не расстраивайтесь, Вам будут доступны новые возможности по мере получения следующих рангов. " \
              "Вам предстоит пройти много испытаний и битв, но мы уверены, что Вы сможете преодолеть все трудности" \
              " и стать одним из лучших в нашей империи. Желаем Вам удачи!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=ReplyKeyboardRemove())
    where_keyboard = [["Дом поручений", "Храм Хроноса", "Лаборатория"],
                      ["Дом гильдий", 'Кузница', 'Арена'],
                      ["Назад"]]
    markup = ReplyKeyboardMarkup(where_keyboard, one_time_keyboard=True)
    message = 'Куда отправимся?'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return WHERE_CHOOSING


count_keyboard = [["В одиночку", "С друзьями"], ["Назад"]]


async def assignments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = 'Вы подходите к небольшому зданию с вывеской "Дом поручений". ' \
              'При входе Вы замечаете, что на стенах висят доски объявлений с различными заданиями.\n' \
              'Может и получится найти, что-то, что Вам по душе...\n\n' \
              'В одиночку или с друзьями?'
    markup = ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=merge_photos('RequestHome', update.effective_chat.id))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message,
                                   reply_markup=markup)
    return TASKS


async def alone_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    if db.check_if_need_to_update_daily_tasks(user_id):
        db.regenerate_daily_tasks(user_id)

    tasks = db.get_cur_user_tasks(user_id, False)
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
    user_id = update.message.from_user.id
    if db.check_if_need_to_update_daily_tasks(user_id):
        db.regenerate_daily_tasks(user_id)

    if db.check_if_request_already_exists_in_multiplayer(user_id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Вы уже отправили запрос на Выполнение заданий с друзьями!")
        return TASKS
    context.user_data['multiplayer_task_id'] = db.get_cur_user_tasks(user_id, True)
    task_labels = {
        'special': "Дело особой важности",
        'random': "Сбор ресурсов"
    }

    message = f"Доступные ежедневные задания ({cur_date()}):\n\n"
    no_tasks_available = True
    for task_id, label in task_labels.items():
        if context.user_data['multiplayer_task_id'][task_id] != -1:
            task = db.get_task_by_id(context.user_data['multiplayer_task_id'][task_id])
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

    all_tasks_labels = [label for task_id, label in task_labels.items() if
                        context.user_data['multiplayer_task_id'][task_id] != -1]
    alone_tasks_keyboard = [all_tasks_labels[:2], all_tasks_labels[2:3], ["Назад"]] if len(all_tasks_labels) >= 2 else [
        all_tasks_labels, ["Назад"]]

    markup = ReplyKeyboardMarkup(alone_tasks_keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return MULTIPLAYER_TASK_CHOOSING


async def get_special_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    friends = db.get_friend_list_ids(update.effective_chat.id)
    text = "Ваш список друзей:\n"
    for friend in friends:
        text += str(friend) + "\n"
    text += f"\nВведите ID людей (от 1 до 3), которых хотите пригласить\nВводите каждый ID с " \
            f"новой строки!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return GET_USER_FOR_SPECIAL_MULTIPLAYER_ID


async def get_random_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    friends = db.get_friend_list_ids(update.effective_chat.id)
    text = "Ваш список друзей:\n"
    for friend in friends:
        text += str(friend) + "\n"
    text += f"\nВведите ID людей (от 1 до 3), которых хотите пригласить\nВводите каждый ID с " \
            f"новой строки!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return GET_USER_FOR_RANDOM_MULTIPLAYER_ID


async def get_ids_for_special_multiplayer_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_ids = update.message.text
    task_id = context.user_data['multiplayer_task_id']['special']
    result = db.add_multiplayer_participants(update.message.from_user.id, task_id, user_ids)
    if not result[0]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=result[1])
        return MULTIPLAYER_TASK_CHOOSING
    keyboard = [
        [
            InlineKeyboardButton("Принять", callback_data="accept_multiplayer_task"),
            InlineKeyboardButton("Отклонить", callback_data="reject_multiplayer_task"),
        ]
    ]
    user_ids = list(map(int, user_ids.split()))
    reply_markup = InlineKeyboardMarkup(keyboard)
    for user in user_ids:
        try:
            await context.bot.send_message(chat_id=user,
                                           text=f"Пользователь с ID {update.effective_chat.id} пригласил Вас на "
                                                f"совместное задание.\n\n"
                                                f"Подтверждаете ли Вы своё участие?",
                                           reply_markup=reply_markup)
        except telegram.error.BadRequest:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Один или несколько пользователей не существует!")
            db.delete_multiplayer_task_participants(update.effective_chat.id)
            return MULTIPLAYER_TASK_CHOOSING
    markup = ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Приглашения успешно отправлены!",
                                   reply_markup=markup)
    return TASKS


async def get_ids_for_random_multiplayer_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_ids = update.message.text
    task_id = context.user_data['multiplayer_task_id']['random']
    result = db.add_multiplayer_participants(update.message.from_user.id, task_id, user_ids)
    if not result[0]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=result[1])
        return MULTIPLAYER_TASK_CHOOSING
    keyboard = [
        [
            InlineKeyboardButton("Принять", callback_data="accept_multiplayer_task"),
            InlineKeyboardButton("Отклонить", callback_data="reject_multiplayer_task"),
        ]
    ]
    user_ids = list(map(int, user_ids.split()))
    reply_markup = InlineKeyboardMarkup(keyboard)
    for user in user_ids:
        try:
            await context.bot.send_message(chat_id=user,
                                           text=f"Пользователь с ID {update.effective_chat.id} пригласил Вас на "
                                                f"совместное задание.\n\n"
                                                f"Подтверждаете ли Вы своё участие?",
                                           reply_markup=reply_markup)
        except telegram.error.BadRequest:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Один или несколько пользователей не существует!")
            db.delete_multiplayer_task_participants(update.effective_chat.id)
            return MULTIPLAYER_TASK_CHOOSING
    markup = ReplyKeyboardMarkup(count_keyboard, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Приглашения успешно отправлены!",
                                   reply_markup=markup)
    return TASKS


async def chronos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not check_if_user_exp_is_enough(update.message.from_user.id, 500):
        message = 'Вы подходите к огромному храму, но какая-то неведомая сила не даёт Вам пройти внутрь.\nВозможно, ' \
                  'Вам пока что не хватает опыта.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = 'Добро пожаловать в Храм Хроноса. Здесь вы сможете получить новые навыки для своего персонажа, ' \
                  'а также, по достижении определённого ранга, изменить подкласс.'
        if not check_if_user_exp_is_enough(update.message.from_user.id, 2000):  # Если опыт больше 2000, даём доступ к смене подкласса
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
    if check_if_user_exp_is_enough(update.message.from_user.id, 1000):
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
    if not check_if_user_exp_is_enough(update.message.from_user.id, 500):
        message = 'Вы приходите к лаборатории, но дверь оказывается закрытой.\nВозможно, Вам пока что не хватает опыта.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('Lab', update.effective_chat.id))
        message = "Что Вы хотите сделать?"
        lab_keyboard = [["Создать расходники", "Посмотреть ресурсы"], ['Назад']]
        markup = ReplyKeyboardMarkup(lab_keyboard, one_time_keyboard=False)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
        return LAB_CHOOSING


async def craft_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:  # TODO Заменить крафты в бд
    message = "На стене Вы видите рецепты расходников:\n\n" \
              "1. Граната: камень + металл\n" \
              "2. Микстура Ивлева: подорожник + яркосвет\n" \
              "3. Регенеративный эликсир: подорожник + Святая вода\n" \
              "4. Божественный эликсир: Святая вода + яркосвет\n" \
              "5. Ветряное зелье: перья + грибы\n" \
              "6. Огненная банка: золото + металл\n" \
              "7. Зелье металлической кожи - металл + подорожник\n" \
              "8. Склянка ледяной души: хладовик + древесина\n" \
              "9. Микстура грибного смещения: грибы + Святая вода\n" \
              "10. Жидкость ослепительного проклятия: перья + яркосвет\n\n" \
              "Вы вошли в решим создания. Чтобы выйти из него, нажмите 'Назад'\n" \
              "Введите номер расходного предмета, чтобы создать его"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
    return GETTING_ITEM_ID


async def craft(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    item_number = update.message.text
    if not item_number.isdigit():
        message = "Введённый Вами текст не является числом!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
        return GETTING_ITEM_ID
    if int(item_number) == 69:
        message = "Бордель в настоящее время закрыт, приносим свои извенения"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
        return GETTING_ITEM_ID
    elif int(item_number) > 10 or int(item_number) < 1:
        message = "Такого предмета не существует!"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
        return GETTING_ITEM_ID
    result = db.craft_item(update.message.from_user.id, item_number)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=result, reply_markup=back_markup)


async def show_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = db.get_inventory_by_user_id(update.message.from_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def guild_house(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not check_if_user_exp_is_enough(update.message.from_user.id, 1000):
        message = 'Вы приходите к дому гильдий. По крайней мере так сказал стражник...\nОн не пропускает Вас под ' \
                  'предлогом, что Вы недостаточно опытны.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        message = "Вы приходите в дом гильдий. Здесь можно запросить или поделиться ресурсами с другими " \
                  "игроками.\n\nЧто вы хотите сделать?"
        guild_keyboard = [['Запросить ресурсы', 'Поделиться ресурсами'], ['Назад']]
        guild_markup = ReplyKeyboardMarkup(guild_keyboard, one_time_keyboard=False)
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('GuildHouse', update.effective_chat.id), caption=message,
                                     reply_markup=guild_markup)
        return GUILD_CHOOSING


async def res_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Вот что Вы можете запросить:\n" \
              "1 - Метал\n" \
              "2 - Грибы\n" \
              "3 - Камни\n" \
              "4 - Древесина\n" \
              "5 - Хладовик\n" \
              "6 - Перья\n" \
              "7 - Яркосвет\n" \
              "8 - Подорожник\n" \
              "9 - Святая вода\n" \
              "10 - Золото\n\n" \
              "Введите номер ресурса и количество (через пробел, не больше 10 ресурсов)\n" \
              "Помните: чем меньше Вы запрашиваете, тем приоритетнее Ваш запрос!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
    return GUILD_REQUEST


async def create_res_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    res_string = update.message.text
    ans = db.add_guild_request(update.message.from_user.id, res_string)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ans, reply_markup=back_markup)


async def res_share(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = db.get_guild_requests(update.message.from_user.id)
    if message[0]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message[1], reply_markup=back_markup)
        return GUILD_ID_GETTING
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message[1])


async def request_id_getting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    request_id = update.message.text
    ans = db.send_res(update.message.from_user.id, request_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ans, reply_markup=back_markup)


async def forge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not check_if_user_exp_is_enough(update.message.from_user.id, 4000):
        message = 'Вы подходите к кузнице, но мастер-кузнец категорически отказывается принимать Ваш заказ. \n' \
                  'Он объясняет, что его работа требует большого опыта и мастерства, и он не хочет рисковать' \
                  ' испортить изделие.'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        forge_keyboard = [['Оружие', 'Броня'], ['Назад']]
        forge_markup = ReplyKeyboardMarkup(forge_keyboard, one_time_keyboard=True)
        await context.bot.send_photo(chat_id=update.effective_chat.id,
                                     photo=merge_photos('AnvilHouse', update.effective_chat.id),
                                     caption="Что бы Вы хотели создать?", reply_markup=forge_markup)
        return FORGE_CHOOSING


async def weapon_creating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = db.show_possible_item_crafts('weapon', db.get_eng_class(update.message.from_user.id))
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message + '\nВведите ID оружия, которое хотите создать',
                                   reply_markup=back_markup)
    return ITEM_INPUT


async def armor_creating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = db.show_possible_item_crafts('armor', db.get_eng_class(update.message.from_user.id))
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message + '\nВведите ID брони, которое хотите создать',
                                   reply_markup=back_markup)
    return ITEM_INPUT


arena_keyboard = [['Вызвать на дуэль', 'Создать открытую дуэль'], ['Назад']]
back_keyboard = [['Назад']]
back_markup = ReplyKeyboardMarkup(back_keyboard, one_time_keyboard=True)


async def get_item_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    item_id = update.message.text
    message = db.create_new_item(update.message.from_user.id, item_id)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message,
                                   reply_markup=back_markup)


async def arena(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not check_if_user_exp_is_enough(update.message.from_user.id, 8000):
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
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
    if int(getting_user_id) == update.message.from_user.id:
        response = "Вы не можете отправить запрос самому себе!"
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
            InlineKeyboardButton("Принять", callback_data="accept_duel"),
            InlineKeyboardButton("Отклонить", callback_data="reject_duel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=getting_user_id, text=message, reply_markup=reply_markup)
    return ARENA_CHOOSING


async def create_open_duel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Доступные чаты для открытой дуэли: \n\n"
    chats = db.get_chat_ids()
    for chat in chats:
        message += f"{str(chat[2])}: {str(chat[1])}\n"
    message += "\nВведите ID чата, в который хотите отправить приглашение!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=back_markup)
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
            InlineKeyboardButton("Принять", callback_data="accept_duel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=getting_chat_id, text=message, reply_markup=reply_markup)
    return ARENA_CHOOSING


async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [['Посмотреть инвентарь'], ['Назад']]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    message = "Выберите действие:"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=markup)
    return INVENTORY_CHOOSING


async def show_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = db.get_users_items(update.effective_chat.id)
    text = "В вашем инвенторе имеются:\n\n\n"
    for item in items:
        text += item[0] + f" ({switch_equip_type_to_russian(str(item[2]))}). Сила: {item[3]}.\n"
        if item[1] == "":
            text += "Зачарований нет.\n"
        else:
            text += "Зачарования: "
            ench_names = []
            for ench in item[1].split(','):
                ench_name = db.get_ench_name_by_id(ench, item[2])
                ench_names.append(ench_name)
            ench_str = ", ".join(ench_names)
            text += ench_str
            text += "\n\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def physic_attack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duel_id = context.bot_data['duel_id' + str(update.message.from_user.id)]
    # Prevent fast double click abuse
    if int(duels_ongoing_dict[duel_id].get_attacker_player_in_game().user_id) != int(update.message.from_user.id):
        pass
    opponent_id = int(db.get_duel_opponent(duel_id, update.message.from_user.id))
    duels_ongoing_dict[duel_id].process_turn(Turn(update.message.from_user.id, TurnType.PHYSICAL_ATTACK, opponent_id))

    opponent = duels_ongoing_dict[duel_id].get_player_in_game(opponent_id)
    me = duels_ongoing_dict[duel_id].get_player_in_game(update.message.from_user.id)

    if opponent.is_stuned:
        opponent.is_stuned = False
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=opponent_id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=attacks_markup)
    else:
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=opponent_id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=attacks_markup)

    if opponent.is_dead() and me.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Ничья! Вы убили друг друга...",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Ничья! Вы убили друг друга...",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    elif opponent.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Оппонент пал! Вы победили!",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Вы проиграли! В этот раз соперник оказался сильнее!",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    elif me.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Вы проиграли! В этот раз соперник оказался сильнее!",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Оппонент пал! Вы победили!",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    return ConversationHandler.END


ABILITY_CHOOSING, CONSUMABLE_CHOOSING = range(2)


async def magic_attack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duel_id = context.bot_data['duel_id' + str(update.message.from_user.id)]
    if int(duels_ongoing_dict[duel_id].get_attacker_player_in_game().user_id) != int(update.message.from_user.id):
        pass
    abilities = duels_ongoing_dict[duel_id].get_possible_abilities(update.message.from_user.id)
    abilities_id_and_name = []
    for a in abilities:
        abilities_id_and_name.append((a, db.get_ability_name(a)))
    keyboard = []
    i = 0
    while i < len(abilities_id_and_name):
        if i % 3 == 0:
            keyboard.append([])
        keyboard[len(keyboard) - 1].append(abilities_id_and_name[i][1])
        i += 1
    magic_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    await context.bot.send_message(chat_id=update.message.from_user.id,
                                   text=f"Выберите способность из доступных: ",
                                   reply_markup=magic_markup)
    return ABILITY_CHOOSING


async def receive_magic_attack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ability_name = update.message.text
    duel_id = context.bot_data['duel_id' + str(update.message.from_user.id)]
    ability_id = db.get_ability_id_from_name(ability_name)
    opponent_id = int(db.get_duel_opponent(duel_id, update.message.from_user.id))

    opponent = duels_ongoing_dict[duel_id].get_player_in_game(opponent_id)
    me = duels_ongoing_dict[duel_id].get_player_in_game(update.message.from_user.id)

    duels_ongoing_dict[duel_id].process_turn(
        Turn(update.message.from_user.id, TurnType.MAGIC_ATTACK, opponent_id, Ability(ability_id, opponent_id)))

    if opponent.is_stuned:
        opponent.is_stuned = False
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=opponent_id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=attacks_markup)
    else:
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=opponent_id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=attacks_markup)

    if opponent.is_dead() and me.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Ничья! Вы убили друг друга...",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Ничья! Вы убили друг друга...",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    elif opponent.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Оппонент пал! Вы победили!",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Вы проиграли! В этот раз соперник оказался сильнее!",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    elif me.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Вы проиграли! В этот раз соперник оказался сильнее!",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Оппонент пал! Вы победили!",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    return ConversationHandler.END


async def choose_consumable_to_use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duel_id = context.bot_data['duel_id' + str(update.message.from_user.id)]
    if int(duels_ongoing_dict[duel_id].get_attacker_player_in_game().user_id) != int(update.message.from_user.id):
        pass
    consumables_list_ids = duels_ongoing_dict[duel_id].get_possible_consumables(update.message.from_user.id)
    consumables_id_and_name = []
    for c in consumables_list_ids:
        consumables_id_and_name.append((c, db.get_consumable_main_info(c)[0]))
    keyboard = []
    i = 0
    while i < len(consumables_id_and_name):
        if i % 3 == 0:
            keyboard.append([])
        keyboard[len(keyboard) - 1].append(consumables_id_and_name[i][1])
        i += 1
    consumable_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
    print(len(consumables_id_and_name))
    await context.bot.send_message(chat_id=update.message.from_user.id,
                                   text=f"Выберите предмет из доступных: ",
                                   reply_markup=consumable_markup)
    return CONSUMABLE_CHOOSING


async def apply_consumable_effect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    consumable_name = update.message.text
    duel_id = context.bot_data['duel_id' + str(update.message.from_user.id)]
    consumable_id = db.get_consumable_id_from_name(consumable_name)
    opponent_id = int(db.get_duel_opponent(duel_id, update.message.from_user.id))

    opponent = duels_ongoing_dict[duel_id].get_player_in_game(opponent_id)
    me = duels_ongoing_dict[duel_id].get_player_in_game(update.message.from_user.id)

    duels_ongoing_dict[duel_id].process_turn(
        Turn(update.message.from_user.id, TurnType.CONSUME, opponent_id,
             None, Consumable(consumable_id, opponent_id)))

    if opponent.is_stuned:
        opponent.is_stuned = False
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=opponent_id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=attacks_markup)
    else:
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=ReplyKeyboardRemove())
        await context.bot.send_message(chat_id=opponent_id,
                                       text=duels_ongoing_dict[duel_id].get_visible_logs_as_str_last_turn(),
                                       reply_markup=attacks_markup)

    if opponent.is_dead() and me.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Ничья! Вы убили друг друга...",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Ничья! Вы убили друг друга...",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    elif opponent.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Оппонент пал! Вы победили!",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Вы проиграли! В этот раз соперник оказался сильнее!",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    elif me.is_dead():
        await context.bot.send_message(chat_id=update.message.from_user.id,
                                       text="Вы проиграли! В этот раз соперник оказался сильнее!",
                                       reply_markup=back_markup)
        await context.bot.send_message(chat_id=opponent_id,
                                       text="Оппонент пал! Вы победили!",
                                       reply_markup=back_markup)

        kill_duel(duel_id)

    return ConversationHandler.END


magic_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Использовать способность$"), magic_attack)],
    states={
        ABILITY_CHOOSING: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), receive_magic_attack, )
        ]
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
)

consumable_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Использовать предмет$"), choose_consumable_to_use)],
    states={
        CONSUMABLE_CHOOSING: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), apply_consumable_effect, )
        ]
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
)


inventory_handler = ConversationHandler(
    entry_points=[CommandHandler("inventory", inventory),
                  MessageHandler(filters.Regex("^Инвентарь$"), inventory)],
    states={
        INVENTORY_CHOOSING: [
            MessageHandler(filters.Regex("^Посмотреть инвентарь$"), show_inventory),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
)

game_handler = ConversationHandler(
    entry_points=[CommandHandler("game", game_menu),
                  MessageHandler(filters.Regex("^Игра$"), game_menu)],
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
            MessageHandler(filters.Regex("^Арена$"), arena),
        ],
        CHRONOS_CHOOSING: [
            MessageHandler(filters.Regex("^Улучшить персонажа$"), upgrade_champ),
            MessageHandler(filters.Regex("^Изменить подкласс$"), change_subclass),
            MessageHandler(filters.Regex("^Назад$"), game_menu),
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
            MessageHandler(filters.Regex("^Назад$"), game_menu),
        ],
        ALONE_TASK_CHOOSING: [
            # ADD MORE FUNCTIONS
            MessageHandler(filters.Regex("^Назад$"), assignments),
        ],
        MULTIPLAYER_TASK_CHOOSING: [
            MessageHandler(filters.Regex("^Дело особой важности$"), get_special_task),
            MessageHandler(filters.Regex("^Сбор ресурсов$"), get_random_task),
            MessageHandler(filters.Regex("^Назад$"), assignments),
        ],
        ARENA_CHOOSING: [
            MessageHandler(filters.Regex("^Вызвать на дуэль$"), challenge_to_duel),
            MessageHandler(filters.Regex("^Создать открытую дуэль$"), create_open_duel),
            MessageHandler(filters.Regex("^Назад$"), game_menu),
        ],
        GET_USER_TO_DUEL_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_user_duel_id),
            MessageHandler(filters.Regex("^Назад$"), arena),
        ],
        GET_CHAT_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_chat_id),
            MessageHandler(filters.Regex("^Назад$"), arena),
        ],
        GET_USER_FOR_SPECIAL_MULTIPLAYER_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")),
                           get_ids_for_special_multiplayer_task),
            MessageHandler(filters.Regex("^Назад$"), assignments),
        ],
        GET_USER_FOR_RANDOM_MULTIPLAYER_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")),
                           get_ids_for_random_multiplayer_task),
            MessageHandler(filters.Regex("^Назад$"), assignments),
        ],
        LAB_CHOOSING: [
            MessageHandler(filters.Regex("^Создать расходники$"), craft_choosing),
            MessageHandler(filters.Regex("^Посмотреть ресурсы$"), show_items),
            MessageHandler(filters.Regex("^Назад$"), game_menu),
        ],
        GETTING_ITEM_ID: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), craft),
            MessageHandler(filters.Regex("^Назад$"), lab),
        ],
        GUILD_CHOOSING: [
            MessageHandler(filters.Regex("^Запросить ресурсы$"), res_request),
            MessageHandler(filters.Regex("^Поделиться ресурсами$"), res_share),
            MessageHandler(filters.Regex("^Назад$"), game_menu),
        ],
        GUILD_REQUEST: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), create_res_request),
            MessageHandler(filters.Regex("^Назад$"), guild_house),
        ],
        GUILD_ID_GETTING: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), request_id_getting),
            MessageHandler(filters.Regex("^Назад$"), guild_house),
        ],
        FORGE_CHOOSING: [
            MessageHandler(filters.Regex("^Оружие$"), weapon_creating),
            MessageHandler(filters.Regex("^Броня$"), armor_creating),
            MessageHandler(filters.Regex("^Назад$"), game_menu),
        ],
        ITEM_INPUT: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), get_item_id),
            MessageHandler(filters.Regex("^Назад$"), forge),
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
)
