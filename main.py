from bottle import route, run, template, static_file, request, redirect
import os
import json
import psycopg2
from dotenv import load_dotenv

# --- DB-anslutning ---
load_dotenv()

DB = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT')
)

@route('/book_list')
def book_list():
    cur = DB.cursor()
    cur.execute("""
        SELECT id, title, author, publication_year, isbn
          FROM public.books
         ORDER BY title;
    """)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    books = [dict(zip(cols, row)) for row in rows]
    return template('book_list', books=books)

# --- Resterande routes, funktionen save_file osv. oförändrade ---
save_folder = "book_ads"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

def save_file(title, content):
    path = f"{save_folder}/{title}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

@route('/route_add_book')
def add_book_ad():
    return template("add_book", title="", content="")

@route("/save_book_ad", method="POST")
def save_book_ad():
    title = request.forms.get("title")
    content = request.forms.get("content")
    save_file(title, content)
    return template("uploaded_book_ad")

@route('/')
def index():
    return template('index')

#login
def read_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # Återställ till tom lista om filen är trasig eller tom
                return {'users': []}
    return {'users': []}


def save_users(data):
    try:
        with open('users.json', 'w') as file:
            json.dump(data, file)
        print("✔ users.json sparad!")
    except Exception as e:
        print("❌ Kunde inte spara users.json:", e)

@route('/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        users_data = read_users()
        user = next((user for user in users_data['users'] if user['username'] == username), None)
        if user and user['password'] == password:
            return template('login_success', username=username)
        else:
            return template('login_failed')
    return template('login')

@route('/register', method=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        users_data = read_users()
        if any(user['username'] == username for user in users_data['users']):
            return template('register_failed', error="Användarnamnet är redan upptaget.")
        users_data['users'].append({
            'username': username,
            'password': password
        })
        save_users(users_data)
        return redirect('/login')
    return template('register')

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)