CREATE DATABASE recipes_db;

CREATE TABLE users(
    u_id SERIAL PRIMARY KEY ,
    u_name TEXT NOT NULL,
    u_email TEXT NOT NULL,
    u_pass TEXT NOT NULL    
);
CREATE TABLE recipes(
    r_id SERIAL PRIMARY KEY ,
    r_name TEXT NOT NULL,
    r_description TEXT NOT NULL,
    r_image TEXT NOT NULL
);
CREATE TABLE favorites(
    id SERIAL PRIMARY KEY ,
    u_id INTEGER REFERENCES users(u_id),
    r_id INTEGER REFERENCES recipes(r_id),
    f_added DATE NOT NULL
);
CREATE TABLE changed_recipes(
    id SERIAL PRIMARY KEY ,
    u_id INTEGER REFERENCES users(u_id),
    r_id INTEGER REFERENCES recipes(r_id),
    key_changed TEXT NOT NULL,
    value_changed TEXT NOT NULL,
    r_changed_at DATE NOT NULL
);

INSERT INTO changed_recipes( u_id, r_id, key_changed, value_changed, r_changed_at)
VALUES(1,7103155,'recipe_description', 'testing the update', DATE '2015-12-17');
