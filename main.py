from bottle import route, run, template, static_file, request, redirect
import os
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

@route('/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Logiken för att hantera login
        pass  # Här skulle du lägga till logik för att validera användaren
    return template('views/login.html')  # Om du har login.html i en mapp som heter 'views'





if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)
