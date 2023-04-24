from database import *
import os
import io
from telegram import ReplyKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from menu_chain import main_menu

from PIL import Image

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
CHOOSING_AVATAR, TYPING_HAIR, TYPING_FACE, TYPING_BODY, CUSTOM_AVATAR_CHOICE = range(5)


# This is a function that sends a message with a keyboard to let users choose what they want to modify in their
# account. The available options are "Изменить имя" (change name), "Изменить аватар" (change avatar), and "Отмена" (
# cancel). After sending the message, the function returns the next state of the conversation (CHOOSING).
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return CHOOSING


# This function handles the user's choice of changing their name and prompts them to enter a new name by replying
# with a message. The function returns the TYPING_REPLY state to indicate that the bot is waiting for the user to
# enter a new name.
async def custom_name_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text("Введите новое имя:")
    return TYPING_REPLY


# This function handles the user input for their new custom name, and updates it in the database. It then sends a
# message confirming the change and prompts the user to choose what to change next.
async def received_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["name"] = text
    user_id = update.message.from_user.id
    db.update_users('personal_username', text, user_id)
    await update.message.reply_text(f"Имя изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed personal name on {text}")
    return CHOOSING


# This function displays a keyboard to allow the user to choose which aspect of their avatar they want to change (
# hair, face, or body). The function is called when the "Изменить аватара" button is pressed.
async def custom_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Изменить волосы", "Изменить лицо", "Изменить тело"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить в аватаре?",
        reply_markup=markup,
    )
    return CHOOSING_AVATAR


# This function merges three images (hair, face, and body) together to create an avatar image for a user with the
# specified user ID. The images are located in three separate folders, and the function uses the Pillow library to
# open and manipulate the images. The resulting image is saved to a file in a specific directory.
def merge_image(img1, img2, img3, user_id) -> None:
    hair = Image.open(os.path.abspath(f'../res/avatars/hair/Вариант {img1}.png')).convert("RGBA")
    face = Image.open(os.path.abspath(f'../res/avatars/face/Вариант {img2}.png')).convert("RGBA")
    body = Image.open(os.path.abspath(f'../res/avatars/body/Вариант {img3}.png')).convert("RGBA")
    body.paste(face, (0, 0), face)
    body.paste(hair, (0, 0), hair)
    nsize = (body.size[0] * 5, body.size[1] * 5)
    body = body.resize(nsize, Image.NEAREST)
    body.save(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'))


# This function is used to regenerate the user's avatar by calling the merge_image function with the avatar_id values
# obtained from get_avatar_ids function for the given user_id. The resulting image is saved to the corresponding file
# in the user's avatar folder.
def regen_avatar(user_id) -> None:
    ids = db.get_avatar_ids(user_id)
    merge_image(ids[0], ids[1], ids[2], user_id)


# This function generates a reply keyboard for displaying options to the user based on the given list of all
# available options. It arranges the options in pairs and returns a list of lists, with each inner list representing
# a row of options, and the last row containing a confirmation button.
def get_reply_keyboard(list_of_all) -> list:
    reply_keyboard = []
    for index in range(1, len(list_of_all)):
        if index % 2 == 1:
            reply_keyboard.append([str(list_of_all[index - 1][1]), str(list_of_all[index][1])])
    if len(list_of_all) % 2 == 1:
        reply_keyboard.append([str(list_of_all[len(list_of_all) - 1][1])])
    reply_keyboard.append(["Подтвердить"])
    return reply_keyboard


# This is function that allows users to customize their avatar's hair by selecting from a list of available options.
# It first retrieves all available hair options using the select_all_hair() function and generates a media group of
# images for each hair option. It then sends a message to the user with the available hair options and the generated
# reply keyboard, and sends the media group of hair images.
async def custom_avatar_hair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    all_hair = db.select_all_body_parts_by_type('hair')
    reply_keyboard = get_reply_keyboard(all_hair)
    hair_list = []
    for hair in all_hair:
        with Image.open(os.path.abspath(f'../res/avatars/hair/{hair[1]}.png')) as img:
            new_size = (img.size[0] * 5, img.size[1] * 5)
            resized_img = img.resize(new_size, resample=Image.NEAREST)
        with io.BytesIO() as buffer:
            resized_img.save(buffer, format="PNG")
            buffer.seek(0)
            hair_list.append(InputMediaPhoto(buffer))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    with open(os.path.abspath(f'../res/avatars/hair/{all_hair[0][1]}.png'), 'rb'):
        await update.message.reply_text(
            "Выберите один из вариантов волос:",
            reply_markup=markup,
        )
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=hair_list)
    return TYPING_HAIR


# The same with face
async def custom_avatar_face(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    all_face = db.select_all_body_parts_by_type('face')
    reply_keyboard = get_reply_keyboard(all_face)
    face_list = []
    for face in all_face:
        with Image.open(os.path.abspath(f'../res/avatars/face/{face[1]}.png')) as img:
            new_size = (img.size[0] * 5, img.size[1] * 5)
            resized_img = img.resize(new_size, resample=Image.NEAREST)
        with io.BytesIO() as buffer:
            resized_img.save(buffer, format="PNG")
            buffer.seek(0)
            face_list.append(InputMediaPhoto(buffer))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    with open(os.path.abspath(f'../res/avatars/face/{all_face[0][1]}.png'), 'rb'):
        await update.message.reply_text(
            "Выберите один из вариантов лица:",
            reply_markup=markup,
        )
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=face_list)
    return TYPING_FACE


# The same with body
async def custom_avatar_body(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    all_shoulders = db.select_all_body_parts_by_type('shoulders')
    reply_keyboard = get_reply_keyboard(all_shoulders)
    shoulders_list = []
    for shoulder in all_shoulders:
        with Image.open(os.path.abspath(f'../res/avatars/body/{shoulder[1]}.png')) as img:
            new_size = (img.size[0] * 5, img.size[1] * 5)
            resized_img = img.resize(new_size, resample=Image.NEAREST)
        with io.BytesIO() as buffer:
            resized_img.save(buffer, format="PNG")
            buffer.seek(0)
            shoulders_list.append(InputMediaPhoto(buffer))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    with open(os.path.abspath(f'../res/avatars/body/{all_shoulders[0][1]}.png'), 'rb'):
        await update.message.reply_text(
            "Выберите один из вариантов тела:",
            reply_markup=markup,
        )
        await context.bot.send_media_group(chat_id=update.effective_chat.id, media=shoulders_list)
    return TYPING_BODY


# This function handles the user's choice of hair for their custom avatar, updates the database and generates a new
# avatar image. It then sends a message to the user with the new avatar image and returns to the "TYPING HAIR" state.
async def received_hair_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = get_reply_keyboard(db.select_all_body_parts_by_type('hair'))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["hair_id"] = text
    user_id = update.message.from_user.id
    db.update_users('hair_id', db.body_type_name_to_id('hair', text), user_id)
    await update.message.reply_text(f"Волосы изменены на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed hair to {text}")
    regen_avatar(user_id)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    return TYPING_HAIR


# The same with face
async def received_face_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = get_reply_keyboard(db.select_all_body_parts_by_type('face'))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["face_id"] = text
    user_id = update.message.from_user.id
    db.update_users('face_id', db.body_type_name_to_id('face', text), user_id)
    await update.message.reply_text(f"Лицо изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed face to {text}")
    regen_avatar(user_id)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    return TYPING_FACE


# The same with body
async def received_body_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = get_reply_keyboard(db.select_all_body_parts_by_type('shoulders'))
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = update.message.text
    context.user_data["shoulders_id"] = text
    user_id = update.message.from_user.id
    db.update_users('shoulders_id', db.body_type_name_to_id('shoulders', text), user_id)
    await update.message.reply_text(f"Тело изменено на {text}.", reply_markup=markup)
    logging.info(f"User with ID {user_id} changed body to {text}")
    regen_avatar(user_id)
    await context.bot.send_photo(chat_id=update.effective_chat.id,
                                 photo=open(os.path.abspath(f'../res/avatars/metadata/user_avatars/{user_id}.png'),
                                            'rb'))
    return TYPING_BODY


# This function displays a reply keyboard with the options "Изменить имя", "Изменить аватара", and "Отмена". It is
# part of a larger conversation handler for managing user profile settings.
async def enter_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Изменить имя", "Изменить аватара"], ["Назад"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Что бы Вы хотели изменить?",
        reply_markup=markup,
    )
    return ConversationHandler.END


custom_name_handler = ConversationHandler(
    entry_points=[CommandHandler("custom", custom),
                  MessageHandler(filters.Regex("^Кастомизация$"), custom)],
    states={
        CHOOSING: [
            MessageHandler(filters.Regex("^Изменить имя$"), custom_name_choice),
        ],
        TYPING_REPLY: [
            MessageHandler(
                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Назад$")), received_name, )
        ],
    },
    fallbacks=[MessageHandler(filters.Regex("^Назад$"), main_menu)],
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
