# An example on how to use https://platform.fatsecret.com/api

import requests

import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=recipes_db')

# grab these keys after signup on https://platform.fatsecret.com
oauth_credentials = {
    'v1': {
        'consumer_key': '51eff776bb2045ec91d98e3bd4b6c672',
        'consumer_secret': 'ecdfe1a2ade6483c849cb9047c012bcf'
    },
    'v2': {
        'client_id': '51eff776bb2045ec91d98e3bd4b6c672',
        'client_secret': '10a103156ae04499a1ca4f7f2d908d60'
    }
}

# ---------------
# OAuth 2 flow
# read more at https://platform.fatsecret.com/api/Default.aspx?screen=rapiauth2

# request access token
# curl
# -u <YOUR_CLIENT_ID>:<YOUR_CLIENT_SECRET>
# -d "grant_type=client_credentials&scope=basic"
# -X POST https://oauth.fatsecret.com/connect/token
url = 'https://oauth.fatsecret.com/connect/token'
username = oauth_credentials['v2']['client_id']
password = oauth_credentials['v2']['client_secret']
payload = {
    "grant_type": "client_credentials",
    "scope": "basic"
}
response = requests.post(url, auth=(username, password), data=payload)
# print(response.text)
# print(response.json()['access_token'])

# use access token to make API calls
# POST https://platform.fatsecret.com/rest/server.api
# Content-Type: application/json
# Header: Authorization: Bearer <Access Token>
# Parameters: method=foods.search&search_expression=toast&format=json
url = 'https://platform.fatsecret.com/rest/server.api'
access_token = response.json()['access_token']
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}'
}
payload = {
    'method': 'recipes.search',
    'format': 'json'
}
payload_get_values_from_recipes_id = {
    'method': 'recipe.get',
    'format': 'json'
}

recipe_list_object = []


def fetch_recipe_list(name):
    payload['search_expression'] = name
    response = requests.post(url, headers=headers, params=payload)

    recipes_list = response.json()['recipes']['recipe']
    # for recipe in recipes_list:

    #     print(recipe['recipe_id'])
    #     print(recipe['recipe_name'])
    #     print(recipe['recipe_description'])
    #     print(recipe['recipe_image'])
    return recipes_list


def fetch_recipe_information(recipe_id):
    payload_get_values_from_recipes_id['recipe_id'] = recipe_id
    response = requests.post(url, headers=headers,
                             params=payload_get_values_from_recipes_id)

    recipe = response.json()['recipe']

    # print(recipe['recipe_name'])
    # print(recipe['number_of_servings'])
    # print(recipe['preparation_time_min'])
    # print(recipe['cooking_time_min'])
    # print(recipe['recipe_description'])
    # print(recipe['recipe_id'])
    # print(recipe['recipe_images']['recipe_image'])

    # recipe_directions = recipe['directions']['direction']
    # for direction in recipe_directions:
    #     print(direction['direction_number'])
    #     print(direction['direction_description'])

    # recipe_ingredients = recipe['ingredients']['ingredient']
    # for ingredient in recipe_ingredients:

    #     print(ingredient['food_name'])
    #     print(ingredient['ingredient_description'])
    #     print(ingredient['number_of_units'])
    return recipe


def get_user_name(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""SELECT u_id,u_name 
                    FROM users 
                    WHERE u_id = %s""",
                [user_id]
                )
    user_result = cur.fetchall()
    user_name = user_result[0][1]
    conn.close()
    return user_name
