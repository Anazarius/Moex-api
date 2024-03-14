from flask import Flask, render_template, request, redirect, url_for, session
from data_processing import process_data_dynamic
from auth import login, register, logout_user, get_current_user, login_required, get_user_by_username, update_user_profile, get_share, get_share_by_id
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
global_df = None


@app.route("/login", methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if login(name, password):
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

@app.route("/profile")
@login_required
def profile():
    current_user = get_current_user()
    user_data = get_user_by_username(current_user)
    return render_template('profile.html', user=user_data)

@app.route("/share_list")
@login_required
def share_list():
    share_data = get_share()
    return render_template('share_list.html', share_data=share_data)

@app.route("/share/<int:share_id>")
@login_required
def share_detail(share_id):
    all_share_data = get_share()

    share_data = get_share_by_id(share_id)

    if share_data is not None:
        return render_template('share_detail.html', share_data=share_data)
    else:
        return render_template('share_list.html', share_data=all_share_data)

@app.route("/update_profile", methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        name = get_current_user()
        new_name = request.form['name']
        last_name = request.form['last_name']
        password = request.form['password']

        update_success = update_user_profile(name, new_name, last_name, password)
        if update_success:
            return redirect(url_for('profile'))
        else:
            return render_template('profile.html', user=get_user_by_username(name), error='Failed to update profile')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login_route'))

if __name__ == "__main__":
    app.run(debug=True)
