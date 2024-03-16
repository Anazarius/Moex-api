from flask import session, redirect, url_for
from database import mycursor, mydb
from functools import wraps
from datetime import date

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

def update_user_profile(old_name, name, last_name, password):
    try:
        query = "UPDATE Users SET name = %s, last_name = %s, password = %s WHERE name = %s"
        values = (name, last_name, password, old_name)
        mycursor.execute(query, values)
        mydb.commit()
        return True
    except Exception as e:
        print(f"Error during profile update: {e}")
        return False

def get_share():
    try:
        query = "SELECT id, tag, name, close FROM Data"
        mycursor.execute(query)
        shares = mycursor.fetchall()
        return shares
    except Exception as e:
        print(f"Error fetching shares: {e}")
        return None

def get_share_by_id(share_id):
    try:
        query = "SELECT id, tag, name, close FROM Data WHERE id = %s"
        values = (share_id,)
        mycursor.execute(query, values)
        share_data = mycursor.fetchone()

        if share_data:
            share = {
                'id': share_data[0],
                'tag': share_data[1],
                'name': share_data[2],
                'close': share_data[3]
            }
            return share
        else:
            return None
    except Exception as e:
        print(f"Error fetching share by ID {share_id}: {e}")
        return None

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

def buy_current_share(user, share_data, quantity):
    total_price = float(share_data['close']) * quantity
    if user['balance'] >= total_price and quantity > 0:
        user['balance'] -= total_price
        share_id = share_data['id']
        today = date.today().isoformat()

        # Проверяем, существует ли уже запись о данной акции у пользователя
        query = "SELECT count FROM User_share WHERE user_id = %s AND share_id = %s"
        values = (user['id'], share_id)
        mycursor.execute(query, values)
        existing_quantity = mycursor.fetchone()

        if existing_quantity:
            # Если запись уже существует, обновляем количество акций
            new_quantity = existing_quantity[0] + quantity
            update_query = "UPDATE User_share SET count = %s WHERE user_id = %s AND share_id = %s"
            update_values = (new_quantity, user['id'], share_id)
            mycursor.execute(update_query, update_values)
        else:
            # Если записи не существует и количество не равно 0, добавляем новую запись о покупке акций
            insert_query = """
            INSERT INTO User_share (user_id, share_id, count, price_purchase, data_purchase)
            VALUES (%s, %s, %s, %s, %s)
            """
            insert_values = (user['id'], share_id, quantity, float(share_data['close']), today)
            mycursor.execute(insert_query, insert_values)


        # Обновляем баланс пользователя
        update_balance_query = "UPDATE Users SET balance = balance - %s WHERE id = %s"
        update_balance_values = (total_price, user['id'])
        mycursor.execute(update_balance_query, update_balance_values)

        mydb.commit()

        return True, f'Successfully bought {quantity} shares and added to your portfolio!'
    else:
        return False, 'Invalid quantity or insufficient funds to complete the purchase!'

def sell_current_share(user, share_data, quantity):
    # Проверяем, есть ли у пользователя достаточно акций для продажи
    query = "SELECT count FROM User_share WHERE user_id = %s AND share_id = %s"
    values = (user['id'], share_data['id'])
    mycursor.execute(query, values)
    existing_quantity = mycursor.fetchone()

    if existing_quantity and existing_quantity[0] >= quantity:
        # Получаем цену закрытия акции
        close_price = share_data['close']
        total_price = close_price * quantity
        
        # Обновляем баланс пользователя в базе данных
        new_balance = user['balance'] + total_price
        query_update_balance = "UPDATE Users SET balance = %s WHERE id = %s"
        values_update_balance = (new_balance, user['id'])
        mycursor.execute(query_update_balance, values_update_balance)
        
        # Обновляем количество акций в портфеле пользователя
        new_quantity = existing_quantity[0] - quantity
        if new_quantity == 0:
            # Если количество акций после продажи становится нулевым, удаляем запись о данной акции из портфеля
            query_delete_share = "DELETE FROM User_share WHERE user_id = %s AND share_id = %s"
            mycursor.execute(query_delete_share, values)
        else:
            # В противном случае обновляем количество акций
            query_update_quantity = "UPDATE User_share SET count = %s WHERE user_id = %s AND share_id = %s"
            values_update_quantity = (new_quantity, user['id'], share_data['id'])
            mycursor.execute(query_update_quantity, values_update_quantity)
        
        mydb.commit()
        
        return True, f'Successfully sold {quantity} shares'
    else:
        return False, 'Insufficient shares to complete the sale'

def get_max_share_quantity(user_data, share_id):
    query = "SELECT count FROM User_share WHERE user_id = %s AND share_id = %s"
    values = (user_data['id'], share_id)
    mycursor.execute(query, values)
    existing_quantity = mycursor.fetchone()

    if existing_quantity:
        return existing_quantity[0]
    else:
        return 0

def is_in_favorites(user_id, share_id):
    query = "SELECT * FROM favorites WHERE user_id = %s AND share_id = %s"
    values = (user_id, share_id)
    mycursor.execute(query, values)
    return mycursor.fetchone() is not None

def add_share_to_favorites(user_id, share_id):
    if is_in_favorites(user_id, share_id):
        query = "DELETE FROM favorites WHERE user_id = %s AND share_id = %s"
        values = (user_id, share_id)
        mycursor.execute(query, values)
        mydb.commit()
        return True, "Removed from favorites successfully."
    else:
        # Иначе добавляем акцию в избранное
        query = "INSERT INTO favorites (user_id, share_id) VALUES (%s, %s)"
        values = (user_id, share_id)
        mycursor.execute(query, values)
        mydb.commit()
        return False, "Added to favorites successfully."
    
def get_user_balance(username):
    user = get_user_by_username(username)
    if user:
        return user['balance']
    else:
        return None

def deposit(username, amount):
    user = get_user_by_username(username)
    if user:
        new_balance = user['balance'] + amount
        query = "UPDATE Users SET balance = %s WHERE name = %s"
        values = (new_balance, username)
        mycursor.execute(query, values)
        mydb.commit()
        return True
    else:
        return False

def update_user_status(user_id, new_status):
    try:
        query = "UPDATE Users SET status_id = %s WHERE id = %s"
        values = (new_status, user_id)
        mycursor.execute(query, values)
        mydb.commit()
        print("User status updated successfully")
    except Exception as e:
        print(f"Error updating user status: {e}")

def get_user_portfolio(user_id):
    try:
        query = """
            SELECT
                d.tag,
                d.name,
                us.count AS quantity,
                d.close AS current_price,
                (us.price_purchase * us.count) - (d.close * us.count) AS profit
            FROM
                User_share AS us
            JOIN
                Data AS d ON us.share_id = d.id
            WHERE
                us.user_id = %s
        """
        values = (user_id,)
        mycursor.execute(query, values)
        portfolio = mycursor.fetchall()
        return portfolio
    except Exception as e:
        print(f"Error fetching user portfolio: {e}")
        return []

def update_user_balance(user_id, new_balance):
    update_query = "UPDATE Users SET balance = %s WHERE id = %s"
    mycursor.execute(update_query, (new_balance, user_id))
    mydb.commit()


def process_additive_purchase(user_id, user_balance, additive_price):
    if user_balance >= additive_price:
        update_user_status(user_id, 2)
        update_user_balance(user_id, user_balance - additive_price)
        return True
    else:
        return False

def get_favorite_shares_with_details(user_id):
    query = """
    SELECT s.tag, s.name, s.close 
    FROM favorites f 
    JOIN data s ON f.share_id = s.id 
    WHERE f.user_id = %s
    """
    values = (user_id,)
    mycursor.execute(query, values)
    favorite_shares = mycursor.fetchall()
    return favorite_shares
