import os
import redis
from dotenv import load_dotenv
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from moltin import get_products, get_access_token, create_customer, delete_item, get_cart_total, get_cart_items, \
    operation_cart_url, add_product_to_cart, cart_url, get_cart, file_url, get_image_href, products_url, get_product, \
    access_token_url, customer_url, delete_item_cart_url, get_customer
import re

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
    if update.message:
        bot.delete_message(update.message.chat_id, update.message.message_id)
    if update.callback_query:
        bot.delete_message(update.callback_query.message.chat_id, update.callback_query.message.message_id)
    if update.message:
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id=update.callback_query.message.chat_id, text='Please choose:', reply_markup=reply_markup)

    return "HANDLE_MENU"


def handle_menu(bot, update):
    callback_query = update.callback_query
    bot.delete_message(chat_id=callback_query.message.chat_id,
                       message_id=callback_query.message.message_id)

    product = get_product(products_url, headers, callback_query.data)['data']
    main_image_id = product['relationships']['main_image']['data']['id']
    image_href = get_image_href(file_url, headers, main_image_id)
    kilograms = [1, 5, 10]
    menu_btn = [
        [InlineKeyboardButton(f'{kilo} kg', callback_data=f"{product['id']},{product['name']},{kilo}") for kilo in
         kilograms],
        [InlineKeyboardButton("go to cart", callback_data='to_сart'),
         InlineKeyboardButton("back to menu", callback_data='/start')]
    ]
    reply_markup = InlineKeyboardMarkup(menu_btn)

    bot.send_photo(chat_id=update.callback_query.message.chat_id, photo=image_href,
                   caption=f"{product['name']}\n\n{product['meta']['display_price']['with_tax']['formatted']} per kg\n"
                           f"{product['meta']['display_price']['with_tax']['amount']}kg on stock\n\n"
                           f"{product['description']}", reply_markup=reply_markup)

    return "HANDLE_DESCRIPTION"


def handle_description(bot, update):
    call_back = update.callback_query.data
    chat_id = str(update.callback_query.message.chat_id)
    _id, name, quantity = call_back.split(',')
    get_cart(cart_url, chat_id, headers)
    payload_cart = {"data": {"id": _id,
                             "type": "cart_item",
                             "quantity": int(quantity)}}
    headers.update({'Content-Type': 'application/json'})
    add_product_to_cart(operation_cart_url, headers, payload_cart, chat_id)

    return 'HANDLE_DESCRIPTION'


def handle_cart(bot, update):
    items_message = "Cart is empty."
    callback_query = update.callback_query
    bot.delete_message(chat_id=callback_query.message.chat_id,
                       message_id=callback_query.message.message_id)

    cart_items = get_cart_items(operation_cart_url, headers, chat_id=update.callback_query.message.chat_id)
    itmes = []
    for i in cart_items['data']:
        itmes.append(i['name'])
        itmes.append(i['description'])
        itmes.append(f"{i['meta']['display_price']['without_tax']['unit']['formatted']} per kg")
        itmes.append(
            f"{i['quantity']} kg in cart for {i['meta']['display_price']['without_tax']['value']['formatted']}")
        itmes.append(' ')
        items_message = '\n'.join(itmes)
    total = get_cart_total(cart_url, headers, chat_id=update.callback_query.message.chat_id)
    total_cost = total['data']['meta']['display_price']['without_tax']['formatted']

    menu_btn = []
    for product in cart_items['data']:
        menu_btn.append([InlineKeyboardButton(f"remove from cart {product['name']}",
                                              callback_data=f"{product['name'], product['id']}")])

    menu_btn.append([InlineKeyboardButton(f"payment", callback_data="to_payment")])
    menu_btn.append([InlineKeyboardButton(f"back to menu", callback_data="/start")])
    reply_markup = InlineKeyboardMarkup(menu_btn)

    bot.sendMessage(chat_id=update.callback_query.message.chat_id, text=f'{items_message}\nTotal: {total_cost}',
                    reply_markup=reply_markup)
    return 'HANDLE_DELETE'


def get_name_id(callback_query_data):
    text = re.sub('''[)'("]''', '', callback_query_data)
    product_name, cart_item = text.split(',')
    return product_name.strip(), cart_item.strip()


def handle_delete(bot, update):
    callback_query_data = update.callback_query.data

    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)

    product_name, cart_item = get_name_id(callback_query_data)
    chat_id = update.callback_query.message.chat_id
    delete_item(delete_item_cart_url, headers, chat_id, cart_item)
    btn_back = [[InlineKeyboardButton('back to Cart', callback_data='to_cart')]]
    reply_markup = InlineKeyboardMarkup(btn_back)
    bot.sendMessage(chat_id=update.callback_query.message.chat_id, text=f" Product {product_name} deleted.",
                    reply_markup=reply_markup)
    return "HANDLE_CART"


def send_email(bot, update):
    callback_data = update.callback_query.data
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    if callback_data == 'to_payment':
        bot.sendMessage(chat_id=update.callback_query.message.chat_id, text='please send your email address!')
    return 'WAITING_EMAIL'


def waiting_email(bot, update):
    customer_id = None
    db = get_database_connection()
    users_email = update.message.text
    user_name = update.message.chat.username
    email = str(users_email)
    customer_data = {'data': {
        'type': 'customer',
        'name': user_name,
        'email': email,
    }}
    try:
        customer_id = db.get(email).decode('utf-8')
    except AttributeError:
        pass
    if customer_id:
        customer = get_customer(customer_url, headers, customer_id)
    else:
        customer_id = create_customer(customer_url, headers, customer_data)['data']['id']
        db.set(email, customer_id)

    update.message.reply_text(f"you send me that email address? : {users_email}")

    return 'WAITING_EMAIL'


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
    elif user_reply == 'to_сart':
        user_state = 'HANDLE_CART'
    elif user_reply == 'to_payment':
        user_state = 'SEND_EMAIL'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'HANDLE_DELETE': handle_delete,
        'WAITING_EMAIL': waiting_email,
        'SEND_EMAIL': send_email,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(bot, update)
    db.set(chat_id, next_state)


def get_database_connection():
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
        'client_id': client_id,
        'client_secret': client_secret_key,
        'grant_type': 'client_credentials'
    }
    access_token = get_access_token(access_token_url, data)

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, waiting_email))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
