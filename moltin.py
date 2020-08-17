from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
import os
import pprint

access_token_url = 'https://api.moltin.com/oauth/access_token'
cart_url = 'https://api.moltin.com/v2/carts/:abc'
products_url = 'https://api.moltin.com/v2/products'
product_to_cart_url = 'https://api.moltin.com/v2/carts/:abc/items'
operation_cart_url = 'https://api.moltin.com/v2/carts/:abc/items'
file_url = 'https://api.moltin.com/v2/files/'


def get_cart(cart_url, headers):
    response = requests.get(cart_url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_access_token(access_token_url, data):
    response = requests.post(access_token_url, data=data)
    response.raise_for_status()
    return response.json()['access_token']


def get_products(products_url, headers):
    response = requests.get(products_url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_product(products_url, headers, products_id):
    product_url = products_url + '/' + products_id
    response = requests.get(product_url, headers=headers)
    response.raise_for_status()
    return response.json()


def add_product_to_cart(add_to_cart_url, payload_cart, headers):
    response = requests.post(add_to_cart_url, headers=headers, json=payload_cart)
    response.raise_for_status()
    return response.json()


def get_cart_items(operation_cart_url, headers):
    response = requests.get(operation_cart_url, headers=headers)
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


def main():
    pics_directory = 'pics'
    os.makedirs(pics_directory, exist_ok=True)
    load_dotenv()

    client_id = os.getenv('CLIENT_ID')
    client_secret_key = os.getenv('CLIENT_SECRET')

    data = {
        'client_id': client_id,
        'client_secret': client_secret_key,
        'grant_type': 'client_credentials'
    }
    access_token = get_access_token(access_token_url, data)
    print(access_token)

    headers = {
        '\'Content-Type\'': '\'multipart/form-data\'',
        'Authorization': f'Bearer {access_token}'
    }
    fish_file = os.path.join(pics_directory, 'red_fish.jpg')
    data_files = {
        'file': (fish_file, open(fish_file, 'rb')),
        'public': 'true',
    }
    file_created = create_file(file_url, headers, data_files)
    print(file_created)
    print('--------------------------------------------------')

    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': f'Bearer {access_token}',
    # }
    # data_image = {"data": {"type": "main_image", "id": f"{file_created}"}}
    # product_id = "6714c43c-5723-4224-acb2-ee9db96b8ab3"
    # image_relationship_url = f'https://api.moltin.com/v2/products/{product_id}/relationships/main-image'
    # main_image = band_main_image(image_relationship_url, headers, data_image)
    # print(main_image)
    # print('-----------------------------------------------------')

    # headers.update({'Content-Type': 'application/json'})
    #
    # products = get_products(products_url, headers=headers)
    # print('------------------------------------------------------------------')
    # pprint.pprint(products)
    # print('------------------------------------------------------------------')

    # slug = 'black-fish'
    # product_id = get_product(products, slug)
    # # print('-------------------------------------------------------------------')
    # # pprint.pprint(product_id)
    # # print('-------------------------------------------------------------------')
    #
    # payload_cart = {"data": {"id": product_id,
    #                          "type": "cart_item",
    #                          "quantity": 3}}
    #
    # added_product = add_product_to_cart(product_to_cart_url, payload_cart, headers)
    # print('-------------------------------------------------------------------')
    # pprint.pprint(added_product)
    # print('-------------------------------------------------------------------')

    # pprint.pprint(cart)
    # print('-------------------------------------------------------------------')

    # pprint.pprint(product)
    # print('-------------------------------------------------------------------')

    file_id = "7b8beae0-434a-43d1-ac91-6b4f562b8508"
    image_href = get_image_href(file_url, headers, file_id)
    print('----------------------------------------------------------')
    print(image_href)
    print('----------------------------------------------------------')

    # pprint.pprint(added_product)
    # print('-------------------------------------------------------------------')

    # pprint.pprint(cart_items)
    # print('-------------------------------------------------------------------')


if __name__ == '__main__':
    main()
