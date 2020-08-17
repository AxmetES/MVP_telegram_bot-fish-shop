import os
from urllib.parse import urljoin
import redis
from more_itertools import first
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import moltin
from moltin import *
from moltin import get_products, get_access_token
from functools import partial

_database = None


def serialized(_data):
    return {'name': _data['name'],
            'price': _data['meta']['display_price']['with_tax']['formatted'],
            'currency': _data['meta']['display_price']['with_tax']['currency'],
            'stock': _data['meta']['display_price']['with_tax']['amount'],
            'description': _data['description'],
            }


def start(bot, update):
    products = get_products(products_url, headers)
    products_names = [[InlineKeyboardButton(f"{_data['name']}", callback_data=f"{_data['id']}")] for _data in
                      products['data']]
    reply_markup = InlineKeyboardMarkup(products_names)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(bot, update):
    menu_btn = [[InlineKeyboardButton("back to menu", callback_data='/start')]]
    reply_markup = InlineKeyboardMarkup(menu_btn)
    callback_query = update.callback_query
    product = get_product(products_url, headers, callback_query.data)['data']
    main_image_id = product['relationships']['main_image']['data']['id']
    image_href = get_image_href(file_url, headers, main_image_id)

    bot.delete_message(chat_id=callback_query.message.chat_id,
                       message_id=callback_query.message.message_id)

    chat_id = update.callback_query.message.chat_id

    bot.send_photo(chat_id=chat_id, photo=image_href,
                   caption=f"{product['name']}\n\n{product['meta']['display_price']['with_tax']['formatted']} per kg\n"
                           f"{product['meta']['display_price']['with_tax']['amount']}kg on stock\n\n"
                           f"{product['description']}", reply_markup=reply_markup)

    return "HANDLE_DESCRIPTION"


# def button(bot, update):
#     query = update.callback_query
#     bot.send_message(update.message.chat.id, text=query)


# def echo(bot, update):
#     """
#     Хэндлер для состояния ECHO.
#
#     Бот отвечает пользователю тем же, что пользователь ему написал.
#     Оставляет пользователя в состоянии ECHO.
#     """
#     users_reply = update.message.text
#     update.message.reply_text(users_reply)
#     return "ECHO"
#
def handle_description(bot, update):
    callback = update.callback_query.data
    if callback == 'back_to_menu':
        return 'START'


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(chat_id, next_state)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        database_password = os.getenv("DATABASE_PASSWORD")
        database_host = os.getenv("DATABASE_HOST")
        database_port = os.getenv("DATABASE_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


if __name__ == '__main__':
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret_key = os.getenv('CLIENT_SECRET')
    token = os.getenv("TG_TOKEN")
    updater = Updater(token)

    data = {
        'User-Agent': 'curl',
        'client_id': client_id,
        'grant_type': 'implicit',
    }

    access_token = get_access_token(access_token_url, data)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # p_start = partial(start, headers)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_description))

    updater.start_polling()
