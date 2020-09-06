import requests
from dotenv import load_dotenv
import os
from urllib.parse import urljoin

access_token_url = 'https://api.moltin.com/oauth/access_token'
cart_url = 'https://api.moltin.com/v2/carts/'
products_url = 'https://api.moltin.com/v2/products/'
operation_cart_url = 'https://api.moltin.com/v2/carts/reference/items'
file_url = 'https://api.moltin.com/v2/files/'
delete_item_cart_url = 'https://api.moltin.com/v2/carts/reference/items/'
customer_url = 'https://api.moltin.com/v2/customers/'


def get_cart(cart_url, chat_id, headers):
    cart_chat_id_url = urljoin(cart_url, chat_id)
    response = requests.get(cart_chat_id_url, headers=headers)
    response.raise_for_status()


def get_access_token(access_token_url, data):
    response = requests.post(access_token_url, data=data)
    response.raise_for_status()
    return response.json()['access_token']


def get_products(products_url, headers):
    response = requests.get(products_url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(products_url, headers, products_id):
    url = urljoin(products_url, products_id)
    print(url)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def replace_url_parameter(url, chat_id):
    chat_id_url = url.replace('reference', str(chat_id))
    return chat_id_url


def add_product_to_cart(cart_url, headers, payload_cart, chat_id):
    url = replace_url_parameter(cart_url, chat_id)
    response = requests.post(url, headers=headers, json=payload_cart)
    response.raise_for_status()


def get_cart_items(cart_url, headers, chat_id):
    url = replace_url_parameter(cart_url, chat_id)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_image_href(file_url, headers, file_id):
    get_image_url = file_url + file_id
    response = requests.get(get_image_url, headers=headers)
    response.raise_for_status()
    href = response.json()['data']['link']['href']
    return href


def create_file(file_url, headers, data_files):
    response = requests.post(file_url, headers=headers, files=data_files)
    response.raise_for_status()
    return response.json()['data']['id']


def band_main_image(image_relationship_url, headers, data_image):
    response = requests.post(image_relationship_url, headers=headers, json=data_image)
    response.raise_for_status()
    return response.json()


def get_cart_total(cart_url, headers, chat_id):
    url = cart_url + str(chat_id)
    response = requests.get(url, headers=headers)
    return response.json()


def delete_item(delete_item_cart_url, headers, chat_id, cart_item):
    url = replace_url_parameter(delete_item_cart_url, chat_id) + cart_item
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def create_customer(customer_url, headers, customer_data):
    response = requests.post(customer_url, headers=headers, json=customer_data)
    response.raise_for_status()
    return response.json()


def get_customer(customer_url, headers, customer_id):
    url = customer_url + str(customer_id)
    response = requests.get(url, headers=headers)
    return response.json()


def delete_customer(customer_url, headers, customer_id):
    url = customer_url + customer_id
    response = requests.delete(url, headers=headers)
    return response


def get_all_customers(customer_url, headers):
    response = requests.get(customer_url, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    pics_directory = 'pics'
    os.makedirs(pics_directory, exist_ok=True)
    load_dotenv()


if __name__ == '__main__':
    main()
