import bcrypt
import psycopg2


# hash is used when creating the user


def hash(string):

    return bcrypt.hashpw(string.encode(), bcrypt.gensalt()).decode()

# check is used when user tries to log in


def check(string, hashed_string):
    return bcrypt.checkpw(string.encode(), hashed_string.encode())


if __name__ == '__main__':
    password = '1234'
    hashed_string_password = hash(password)
    print(hashed_string_password)
    is_the_same = check(password, hashed_string_password)
    print(is_the_same)

    password = hash('123456')
    print(password)


# We work with strings
# bcrypt works with bytes(numbers)

# What checkpw does:
# 1. get salt from the 2nd parameter/argument
# 2. call hashpw with the plain string as the 1st argument and salt as the 2nd argument
# 3. compare result from step 2 with the 2nd parameter in the checkpw function call
