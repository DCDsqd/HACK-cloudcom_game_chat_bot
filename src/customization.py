from database import *
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

from PIL import Image


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['/custom', '/game'], ['/fight', '/help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Выберите команду:",
                                   reply_markup=reply_markup)
    return ConversationHandler.END


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY, CUSTOM_AVATAR_CHOICE = range(5)


async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return CHOOSING


async def custom_name_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text("Введите новое имя:")
    return TYPING_REPLY


async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    text = update.message.text
    context.user_data["name"] = text
    user_id = update.message.from_user.id
    inserter('personal_username', text, user_id)
    await update.message.reply_text(f"Имя изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed personal name on {text}")
    return CHOOSING


async def custom_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить волосы", "Изменить лицо", "Изменить тело"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить в аватаре?",
        reply_markup=markup,
    )
    return CHOOSING_AVATAR


def merge_image(img1, img2, img3, user_id):
    background = Image.open(os.path.abspath(f'../res/avatars/hair/Вариант {img1}.png')).convert("RGBA")
    foreground = Image.open(os.path.abspath(f'../res/avatars/face/Вариант {img2}.png')).convert("RGBA")
    mid = Image.open(os.path.abspath(f'../res/avatars/body/Вариант {img3}.png')).convert("RGBA")
    mid.paste(foreground, (0, 0), foreground)
    mid.paste(background, (0, 0), background)
    nsize = (mid.size[0]*5, mid.size[1]*5)
    mid = mid.resize(nsize, Image.NEAREST)
    mid.save(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'))


def regen_avatar(user_id):
    ids = get_avatar_ids(user_id)
    merge_image(ids[0], ids[1], ids[2], user_id)


def get_reply_keyboard(list_of_all):
    reply_keyboard = []
    for index in range(1, len(list_of_all)):
        if index % 2 == 1:
            reply_keyboard.append([str(list_of_all[index - 1][1]), str(list_of_all[index][1])])

    if len(list_of_all) % 2 == 1:
        reply_keyboard.append([str(list_of_all[len(list_of_all) - 1][1])])

    reply_keyboard.append(["Подтвердить"])
    return reply_keyboard


async def custom_avatar_hair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_hair = select_all_hair()
    reply_keyboard = get_reply_keyboard(all_hair)
    hair_list = []
    for i in range(len(all_hair)):
        hair_list.append(InputMediaPhoto(open(os.path.abspath(f'../res/avatars/hair/{all_hair[i][1]}.png'), 'rb')))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите один из вариантов волос:",
        reply_markup=markup,
    )
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=hair_list)
    return TYPING_HAIR


async def custom_avatar_face(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_face = select_all_face()
    reply_keyboard = get_reply_keyboard(all_face)
    face_list = []
    for i in range(len(all_face)):
        face_list.append(InputMediaPhoto(open(os.path.abspath(f'../res/avatars/face/{all_face[i][1]}.png'), 'rb')))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите один из вариантов лица:",
        reply_markup=markup,
    )
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=face_list)
    return TYPING_FACE


async def custom_avatar_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_shoulders = select_all_shoulders()
    reply_keyboard = get_reply_keyboard(all_shoulders)
    shoulders_list = []
    for i in range(len(all_shoulders)):
        shoulders_list.append(
            InputMediaPhoto(open(os.path.abspath(f'../res/avatars/body/{all_shoulders[i][1]}.png'), 'rb')))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Выберите один из вариантов тела:",
        reply_markup=markup,
    )
    await context.bot.send_media_group(chat_id=update.effective_chat.id, media=shoulders_list)
    return TYPING_BODY


async def received_hair_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = get_reply_keyboard(select_all_hair())
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["hair_id"] = text
    user_id = update.message.from_user.id
    inserter('hair_id', body_type_name_to_id('hair', text), user_id)
    await update.message.reply_text(f"Волосы изменены на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed hair to {text}")
    regen_avatar(user_id)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    return TYPING_HAIR


async def received_face_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = get_reply_keyboard(select_all_face())
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["face_id"] = text
    user_id = update.message.from_user.id
    inserter('face_id', body_type_name_to_id('face', text), user_id)
    await update.message.reply_text(f"Лицо изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed face to {text}")
    regen_avatar(user_id)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    return TYPING_FACE


async def received_body_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = get_reply_keyboard(select_all_shoulders())
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["shoulders_id"] = text
    user_id = update.message.from_user.id
    inserter('shoulders_id', body_type_name_to_id('shoulders', text), user_id)
    await update.message.reply_text(f"Тело изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed body to {text}")
    regen_avatar(user_id)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    return TYPING_BODY


async def enter_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Отмена"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return ConversationHandler.END


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
