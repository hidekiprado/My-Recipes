from crypt import methods
from datetime import date
import os
import random
import flask
import psycopg2
import hash
import recipe_service

from flask import Flask, redirect, session

# object used at add_recipe_action and recipe_list
# this is to avoid fetching
recipe_list_object = []

DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=recipes_db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'some-key')

app = Flask(__name__)
app.secret_key = SECRET_KEY.encode()

# signup page


@app.route('/sign_up')
def sign_up():
    return flask.render_template('sign_up.html')

# signup page - inserting user in recipes_db


@app.route('/sign_up_action', methods=['POST'])
def sign_up_action():
    # parameters requests
    email = flask.request.form.get('email')
    name = flask.request.form.get('name')
    password = flask.request.form.get('password')

    # insert user into users database
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute(
        """SELECT u_id,u_name, u_email, u_pass
        FROM users
        WHERE u_email = %s""",
        [email]
    )
    results = cursor.fetchall()
    if results:
        return flask.render_template('sign_up.html', email_error='email already exists, please try it again')
    else:
        cursor.execute("""
            INSERT INTO users(u_name, u_email, u_pass)
            VALUES (%s, %s, %s)
        """, [name, email, hash.hash(password)])
        connection.commit()
        connection.close()
        return flask.redirect("/login")


#  login page


@app.route('/login')
def login():
    return flask.render_template('login.html')

#  login page - checking user account


@app.route('/login_action', methods=['POST'])
def login_action():
    email = flask.request.form.get('email')
    password = flask.request.form.get('password')
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """SELECT u_id,u_name, u_email, u_pass
        FROM users
        WHERE u_email = %s""",
        [email]
    )
    results = cur.fetchall()

    # checking password and recording session/cookie
    if results:
        if hash.check(password, results[0][3]) == True:
            session['user_id'] = str(results[0][0])
            return flask.redirect('/')

        else:
            return flask.render_template('login.html', user_error='user not found, please try it again')

# logout page


@ app.route('/logout_action')
def logout():
    session.pop("user_id", None)
    return flask.redirect('/')

# index page only loads if session/cookie exists


@app.route('/', methods=['POST', 'GET'])
def index():
    # checking password and recording session/cookie
    user_id_from_encrypted_cookie = session.get("user_id")
    # # clearing object before searching for 20 more - object used at add_recipe_action
    # # this is to avoid fetching again
    recipe_list_object.clear()
    # fetching using input search and populating recipe_list_object
    recipe_search = flask.request.form.get('recipe_search')
    if recipe_search:
        recipe_list = recipe_service.fetch_recipe_list(recipe_search)
        for recipe in recipe_list:
            recipe_list_object.append(recipe)

        #  if recipe search exists access DB get recipe - else: get the recipe_list_object and send to recipe_list

        if user_id_from_encrypted_cookie:
            user_name = recipe_service.get_user_name(
                user_id_from_encrypted_cookie)

            return flask.render_template('recipe_list.html', recipe_search=recipe_search, recipe_list=recipe_list, user_name=user_name)
    else:
        recipe_searchX = random.choice(
            ['bread', 'egg', 'garlic', 'salad', 'blueberry', 'muffins', 'chicken', 'banana'])

        # recipe_searchX = 'bread'
        recipe_list = recipe_service.fetch_recipe_list(recipe_searchX)
        for recipe in recipe_list:
            recipe_list_object.append(recipe)

        #  if recipe search exists access DB get recipe - else: get the recipe_list_object and send to recipe_list

        if user_id_from_encrypted_cookie:
            user_name = recipe_service.get_user_name(
                user_id_from_encrypted_cookie)

            return flask.render_template('recipe_list.html', recipe_searchX=recipe_searchX, recipe_list=recipe_list_object, user_name=user_name)

    return flask.render_template('recipe_list.html', recipe_search=recipe_search, recipe_list=recipe_list)


# add recipes to DB based on recipe_id


@app.route('/add_recipe_action/<id>', methods=['GET'])
def add_recipe_action(id):
    recipe_id_to_add = id
    user_id_from_encrypted_cookie = session.get("user_id")
    if user_id_from_encrypted_cookie:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        # populating recipes
        for recipe_object in recipe_list_object:
            cursor.execute("""
            SELECT r_id
            FROM recipes
            WHERE r_id = %s
            """, [recipe_id_to_add])
            results = cursor.fetchall()
            # checking for duplicates before inserting - if not results
            if not results:
                if recipe_object['recipe_id'] == recipe_id_to_add:
                    recipe_id = recipe_object['recipe_id']
                    recipe_name = recipe_object['recipe_name']
                    recipe_description = recipe_object['recipe_description']
                    recipe_image = recipe_object['recipe_image']

                    cursor.execute("""
                        INSERT INTO recipes(r_id, r_name, r_description, r_image)
                        VALUES (%s, %s, %s, %s)""", (recipe_id, recipe_name, recipe_description, recipe_image))
                    connection.commit()

        # populating favorites table
        for recipe_object in recipe_list_object:
            cursor.execute("""
            SELECT r_id
            FROM favorites
            WHERE r_id = %s
            """, [recipe_id_to_add])
            results = cursor.fetchall()
            # checking for duplicates before inserting - if not results
            if not results:
                if recipe_object['recipe_id'] == recipe_id_to_add:

                    today = date.today()
                    cursor.execute("""
                        INSERT INTO favorites(u_id, r_id, f_added)
                        VALUES (%s, %s, %s)
                        """, (user_id_from_encrypted_cookie, recipe_id_to_add, today))
                    connection.commit()

        return redirect('/favorites')
    else:
        return redirect('/')

# favorites list page


@app.route('/favorites', methods=['POST', 'GET'])
def favorites_list():
    user_id_from_encrypted_cookie = session.get("user_id")
    if user_id_from_encrypted_cookie:
        # passing username to favorites.html
        user_name = recipe_service.get_user_name(user_id_from_encrypted_cookie)

        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT recipes.r_id, recipes.r_name, recipes.r_description, recipes.r_image
            FROM recipes
            INNER JOIN favorites ON favorites.r_id=recipes.r_id
            WHERE favorites.u_id = %s
            ORDER BY favorites.id DESC;
        """, [user_id_from_encrypted_cookie])

        results = cursor.fetchall()
        row = results[0]
        # populating object and sending to favorite.html
        recipe_favorite_list = []
        for row in results:
            recipe_favorite_list.append({
                'recipe_id': row[0],
                'recipe_name': row[1],
                'recipe_description': row[2],
                'recipe_image': row[3],

            })

        connection.close()
        return flask.render_template('favorites.html', recipe_favorite_list=recipe_favorite_list, user_name=user_name)
    else:
        return redirect('/')

# delete recipe


@app.route('/recipe_delete_action/<id>')
def recipe_delete_action(id):
    recipe_id_to_delete = id
    user_id_from_encrypted_cookie = session.get("user_id")
    if user_id_from_encrypted_cookie:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM favorites WHERE r_id = %s AND u_id= %s
        """, [recipe_id_to_delete, user_id_from_encrypted_cookie])
        connection.commit()

        # return str(recipe_favorite_list)
        return redirect('/favorites')


recipe_information_updated = []


@ app.route('/show_recipe/<id>', methods=['GET'])
def show_recipe(id):

    user_id_from_encrypted_cookie = session.get("user_id")
    recipe_id = id
    recipe_information = recipe_service.fetch_recipe_information(
        recipe_id)

    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT key_changed, value_changed
        FROM changed_recipes
        WHERE u_id = %s AND r_id = %s
    """, [user_id_from_encrypted_cookie, recipe_id])

    results = cursor.fetchall()

    if results:
        for change in results:
            recipe_information[change[0]] = change[1]
    connection.close()
    recipe_information_updated.append(recipe_information)

    if user_id_from_encrypted_cookie:
        user_name = recipe_service.get_user_name(
            user_id_from_encrypted_cookie)
        return flask.render_template('recipe_information.html', recipe=recipe_information, user_name=user_name)

    return flask.render_template('recipe_information.html', recipe=recipe_information)


@app.route('/recipe_edit_information/<id>', methods=['GET'])
def recipe_edit_information(id):
    recipe_id = id
    recipe_information = recipe_information_updated[0]

    return flask.render_template('recipe_edit_information.html', recipe=recipe_information)


@app.route('/recipe_edit_information_action', methods=['GET'])
def recipe_edit_information_action():
    recipe_name = flask.request.args('recipe_name')
    recipe_description = flask.request.args('recipe_description')

    return flask.render_template('recipe_information.html')


if __name__ == "main":
    app.run(debug=True)
