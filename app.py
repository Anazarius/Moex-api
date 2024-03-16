from flask import Flask, render_template, request, redirect, url_for
from data_processing import process_data_dynamic
from auth import login, register, logout_user, get_current_user, login_required, get_user_by_username, update_user_profile, get_share, get_share_by_id, buy_current_share, sell_current_share, get_max_share_quantity, add_share_to_favorites, is_in_favorites, get_user_balance, deposit, update_user_status, get_user_portfolio, process_additive_purchase, get_favorite_shares_with_details
from graph import fetch_price_history, plot_price_history, parse_price_history
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
global_df = None


@app.route("/login", methods=['GET', 'POST'])
def login_route():
    global global_df
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if login(name, password):
            df = process_data_dynamic()
            global_df = df
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        password = request.form['password']

        if register(name, last_name, password):
            return redirect(url_for('login_route'))
        else:
            return render_template('register.html', error='Registration failed')

    return render_template('register.html')

@app.route("/")
@login_required
def additive():
    global global_df
    if global_df is not None:
        current_user = get_current_user()
        return render_template('additive.html', username=current_user, table=global_df.to_html())
    df = process_data_dynamic()
    global_df = df
    current_user = get_current_user()
    return render_template('additive.html', username=current_user, table=df.to_html())

@app.route("/buy_additive", methods=['POST'])
@login_required
def buy_additive():
    share_data = get_share()
    current_user = get_current_user()
    user_data = get_user_by_username(current_user)
    user_id = user_data['id']
    user_status = user_data['status_id']
    user_balance = get_user_balance(current_user)
    additive_price = 50000

    if process_additive_purchase(user_id, user_balance, additive_price):
        update_user_status(user_id, 2)
        return redirect(url_for('additive'))
    else:
        return redirect(url_for('balance'))

@app.route("/profile")
@login_required
def profile():
    current_user = get_current_user()
    user_data = get_user_by_username(current_user)
    print(user_data)
    user_status= user_data['status_id']
    return render_template('profile.html', user=user_data, user_status=user_status)

@app.route("/share_list")
@login_required
def share_list():
    current_user = get_current_user()
    user_data = get_user_by_username(current_user)
    user_status= user_data['status_id']
    share_data = get_share()
    return render_template('share_list.html', share_data=share_data, user_status=user_status)

from flask import render_template

@app.route("/share/<int:share_id>")
@login_required
def share_detail(share_id):
    all_share_data = get_share()
    share_data = get_share_by_id(share_id)
    error = request.args.get('error')
    print("Error:", error)

    if share_data is not None:
        tag = share_data['tag']
        price_history_xml = fetch_price_history(tag)
        dates, prices = parse_price_history(price_history_xml)
        price_history_base64 = plot_price_history(dates, prices)
        current_user = get_current_user()
        user_data = get_user_by_username(current_user)
        user_id= user_data['id']
        user_status= user_data['status_id']
        max_value = get_max_share_quantity(user_data, share_id)
        is_favorite = is_in_favorites(user_id, share_id)

        return render_template('share_detail.html', share_data=share_data, price_history=price_history_base64, max_value=max_value, is_favorite=is_favorite, user_status=user_status, error=error)
    else:
        return render_template('share_list.html', share_data=all_share_data)



@app.route("/buy_share/<int:share_id>", methods=['POST'])
@login_required
def buy_share(share_id):
    if request.method == 'POST':
        count = int(request.form['count'])
        user = get_user_by_username(get_current_user())
        share_data = get_share_by_id(share_id)
        success, message = buy_current_share(user, share_data, count)
        if success:
            return redirect(url_for('share_detail', share_id=share_id))
        else:
            return redirect(url_for('share_detail', share_id=share_id, error=message))


@app.route("/sell_share/<int:share_id>", methods=['POST'])
@login_required
def sell_share(share_id):
    if request.method == 'POST':
        count = int(request.form['count'])
        user = get_user_by_username(get_current_user())
        share_data = get_share_by_id(share_id)
        success, message = buy_current_share(user, share_data, count)
        if success:
            return redirect(url_for('share_detail', share_id=share_id))
        else:
            return redirect(url_for('share_detail', share_id=share_id, error=message))


@app.route("/add_to_favorites/<int:share_id>", methods=['POST'])
@login_required
def add_to_favorites(share_id):
    user = get_user_by_username(get_current_user())
    user_id = user['id']
    is_favorite = is_in_favorites(user_id, share_id)
    
    if is_favorite:
        success = True
        add_share_to_favorites(user_id, share_id)
    else:
        success = False
        add_share_to_favorites(user_id, share_id)

    return redirect(url_for('share_detail', share_id=share_id, is_favorite=is_favorite, success=success))

@app.route("/update_profile", methods=['POST'])
@login_required
def update_profile():
    old_name = get_current_user()
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        password = request.form['password']
        update_success = update_user_profile(old_name, name, last_name, password)
        if update_success:
            user = get_user_by_username(name)
            login(user['name'], user['password'])
            return redirect(url_for('profile'))
        else:
            return render_template('profile.html', user=get_user_by_username(old_name), error='Failed to update profile')


@app.route("/balance")
@login_required
def balance():
    name = get_current_user()
    user_data = get_user_by_username(name)
    user_balance = get_user_balance(name)
    user_status= user_data['status_id']
    return render_template('balance.html', user_balance=user_balance, user_status=user_status)

@app.route("/deposit_route", methods=['POST'])
@login_required
def deposit_route():
    if request.method == 'POST':
        amount = int(request.form['amount'])
        name = get_current_user()
        deposit(name, amount)
        user_balance = get_user_balance(name)
        return render_template('balance.html', user_balance=user_balance)

@app.route("/portfolio")
@login_required
def portfolio():
    name = get_current_user()
    user = get_user_by_username(name)
    user_id = user['id']
    current_user = get_current_user()
    user_data = get_user_by_username(current_user)
    user_status= user_data['status_id']
    user_balance = get_user_balance(name)
    user_portfolio = get_user_portfolio(user_id)
    return render_template('portfolio.html', shares=user_portfolio, balance=user_balance, user_status=user_status)

@app.route("/favorites")
@login_required
def favorites():
    name = get_current_user()
    user = get_user_by_username(name)
    user_id = user['id']
    current_user = get_current_user()
    user_data = get_user_by_username(current_user)
    user_status= user_data['status_id']
    user_favorites = get_favorite_shares_with_details(user_id)
    return render_template('favorites.html', shares=user_favorites, user_status=user_status)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login_route'))

if __name__ == "__main__":
    app.run(debug=True)