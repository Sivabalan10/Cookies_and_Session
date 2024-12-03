from flask import Flask, request, make_response, session, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for sessions

# SQLite setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Home route
@app.route('/')
def home():
    username = request.cookies.get('username')
    if 'user_id' in session:
        return f"Hello, {session['username']}! You're logged in."
    return render_template('login.html', username=username)

# Login route
@app.route('/login', methods=['POST'])
def login():
    # added
    username = request.form['username']
    password = request.form['password']

    # Validate against the database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        # Store session and cookie
        session['user_id'] = user[0]
        session['username'] = username
        response = make_response(redirect(url_for('home')))
        response.set_cookie('username', username, max_age=60*60*24*30)  # Expires in 30 days
        return response
    return "Invalid credentials. Please try again."

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    response = make_response(redirect(url_for('home')))
    response.set_cookie('username', '', expires=0)  # Clear the cookie
    return response


@app.route('/register_new', methods=['GET'])
def register_new():
    return render_template('register.html')
# Register route
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Username already exists. Please try another."
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
