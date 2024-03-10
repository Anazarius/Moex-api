# auth.py
from flask import session, redirect, url_for
from database import mycursor, mydb
from functools import wraps

def register_user(username, last_name, password, balance=0, status_id=1):
    try:
        query = "INSERT INTO Users (name, last_name, password, balance, status_id) VALUES (%s, %s, %s, %s, %s)"
        values = (username, last_name, password, balance, status_id)
        mycursor.execute(query, values)
        mydb.commit()
        return True
    except Exception as e:
        print(f"Error during registration: {e}")
        return False


def get_user_by_username(name):
    query = "SELECT * FROM Users WHERE name = %s"
    values = (name,)
    mycursor.execute(query, values)
    user_data = mycursor.fetchone()

    if user_data:
        user = {
            'id': user_data[0],
            'name': user_data[1],
            'last_name': user_data[2],
            'password': user_data[3],
            'balance': user_data[4],
            'status_id': user_data[5]
        }
        return user
    else:
        return None

def register(name, last_name, password):
    if get_user_by_username(name):
        return False
    return register_user(name, last_name, password)

def login(name, password):
    user = get_user_by_username(name)

    if user and user['password'] == password:
        session['name'] = name
        return True
    else:
        return False

def logout_user():
    session.pop('name', None)

def get_current_user():
    return session.get('name', None)

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if 'name' in session:
            return view(*args, **kwargs)
        else:
            return redirect(url_for('login_route'))
    return wrapper

