from bottle import route, run, template, static_file, request, redirect
import os
import json #la til denna för tillfället för login och registrering, men kan ta bort när vi sparar det i databasen i stället
import psycopg2
from dotenv import load_dotenv

# --- DB‐anslutning ---
# Ladda .env
load_dotenv()

DB = psycopg2.connect(
    host     = os.getenv('DB_HOST'),
    dbname   = os.getenv('DB_NAME'),
    user     = os.getenv('DB_USER'),
    password = os.getenv('DB_PASSWORD'),
    port     = os.getenv('DB_PORT')
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
    # hämta kolumnnamnen
    cols = [desc[0] for desc in cur.description]
    cur.close()

    # konvertera varje rad till dict, t.ex. {'id':1,'title':'Learn Python',...}
    books = [ dict(zip(cols, row)) for row in rows ]

    return template('book_list', books=books)

# --- resterande routes, funktionen save_file osv. oförändrade ---
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

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')


#Den som läser från JSON-fil
def read_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            return json.load(file)
    return {'users': []}

#sparar användardatan
def save_users(data):
    with open('users.json', 'w') as file:
        json.dump(data, file)

@route('/login', method=['GET', 'POST']) #Ni fattar att det är en route för login, vat inte vad jag ska kommentera på allt
def login():
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')

        # Läser användardatan från JSON-fil
        users_data = read_users()

        # Hittar användaren
        user = next((user for user in users_data['users'] if user['username'] == username), None)

        # Kontrollera om användaren finns och lösenordet stämmer
        if user and user['password'] == password:
            return template('login_success.html', username=username)
        else:
            return template('login_failed.html')


    return template('login_register_popup.html')


@route('/register', method=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')

        # Läser användardata från JSON-filen
        users_data = read_users()

        #kollar om användaren redan finns
        if any(user['username'] == username for user in users_data['users']):
            return template('register_failed.html', error="Användarnamnet är redan upptaget.")

        #Lägger till den nya användaren
        users_data['users'].append({
            'username': username,
            'password': password
        })

        save_users(users_data)

        return redirect('/login')

    return template('login_register_popup.html')

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')