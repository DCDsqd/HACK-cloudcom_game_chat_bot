from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    PollAnswerHandler,
)

from common_func import start, profile, help_me, del_keyboard, \
    get_events, receive_poll_answer, poll_handler, rating
from friends import friends_handler
from customization import custom_name_handler, avatar_handler
from admin import admin_handler
from game import game_handler


if __name__ == '__main__':
    token_file = open("../tokens/tg_app_token.txt", "r")
    application = ApplicationBuilder().token(token_file.read()).build()
    token_file.close()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(poll_handler)
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_handler(CommandHandler('help', help_me))
    application.add_handler(CommandHandler('rating', rating))
    application.add_handler(CommandHandler('events', get_events))
    application.add_handler(CommandHandler('del', del_keyboard))
    application.add_handler(CommandHandler('profile', profile))
    application.add_handler(admin_handler)
    application.add_handler(avatar_handler)
    application.add_handler(custom_name_handler)
    application.add_handler(game_handler)
    application.add_handler(friends_handler)
    application.run_polling()
