from flask import Flask, render_template, request, redirect, url_for, session
from data_processing import process_data_dynamic
from auth import login, register, logout_user, get_current_user, login_required
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
            return redirect(url_for('home'))
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
def home():
    global global_df
    if global_df is not None:
        current_user = get_current_user()
        return render_template('home.html', username=current_user, table=global_df.to_html())
    df = process_data_dynamic()
    global_df = df
    current_user = get_current_user()
    return render_template('home.html', username=current_user, table=df.to_html())

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login_route'))

if __name__ == "__main__":
    app.run(debug=True)
