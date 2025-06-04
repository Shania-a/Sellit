from bottle import route, run, template, static_file, request, redirect
from bottle import Bottle
import os
import psycopg2
import json
from dotenv import load_dotenv
from beaker.middleware import SessionMiddleware  #För session hantering för inloggningen

session_opts = {  #Hör till beaker
    'session.type': 'file',
    'session.cookie_expires': 3000,
    'session.data_dir': './data',
    'session.auto': True
}

app = Bottle()

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

@app.route('/book_list')
def book_list():
    """
    Visar en lista med böcker från databasen. Användaren kan:
      - Söka på titel eller författare (parameter: q)
      - Filtrera på kursnamn (parameter: course)
      - Filtrera på programnamn (parameter: program)

    Funktionen gör tre saker:
    - Hämtar filtrerningsparametrar från URL:en (det som användaren har matat in) 
    - Bygger en sql-fråga baserat på vilka filter som är ifyllda 
    - kör frågan, behandlar resultatet och skickar det till html-mallen   
    """
    # Hämtar sökfras och filtreringsparametrar från URL:en, tar bort blanktecken
    q = request.query.q.strip() if request.query.q else ""
    course = request.query.course.strip() if request.query.course else ""
    program = request.query.program.strip() if request.query.program else ""

    try:
        cur = DB.cursor()
        
        # Bas-SQL: Hämta info om alla böcker, inklusive relaterad kurs och program (om det finns).
        # LEFT JOIN används för att även visa böcker som inte har någon koppling till kurs/program.
        sql = """
            select distinct b.id, b.title, b.author, b.publication_year, b.isbn, a.price
            from books b
            left join ads a on b.id = a.book_id 
            left join courses c on a.course_id = c.id
            left join program_courses pc on c.id = pc.course_id 
            left join programs p on pc.program_id = p.id
            where 1=1
        """

        # Förbereder en lista som ska innehålla alla värden som skickas till SQL-frågan
        params = []

        # om användaren har skrivit något i sökfältet så läggs det till i sql-frågan
        # ILIKE används istället för LIKE för att matchningen ska vara skiftlägesoberoende
        if q:
            sql += " and (b.title ILIKE %s or b.author ILIKE %s)"
            like_q = f"%{q}%"
            params.extend([like_q, like_q])

        # om användaren angett kurs så läggs det till i sql-frågan
        if course:  
            sql += " and c.name ILIKE %s"
            params.append(f"%{course}%")

        # om användaren har valt program så läggs det till i sql-frågan
        if program:
            sql += " and p.name ILIKE %s"
            params.append(f"%{program}%")

        sql += " order by b.title"

        # kör sql-frågan med parametrarna
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        cur.close() 

        books = [dict(zip(cols, row)) for row in rows]

    except Exception as e:
        print("Fel vid sökning", e)
        books = []
        q, course, program = "", "", ""
    
    return template('book_list', books=books, q=q, course=course, program=program)

@app.route('/route_add_book')
def add_book_ad():
    s = request.environ.get('beaker.session')
    username = s.get('user', None)

    cur = DB.cursor()
    cur.execute('select id, name from courses order by name')  
    courses = cur.fetchall()
    cur.close()

    return template("add_book", title="", content="", username=username, courses=courses)

@app.route('/save_book', method='POST')
def save_book():
    s = request.environ.get('beaker.session')
    username = s.get('user', None)
    if not username:
        redirect('/login')

    title = request.forms.get('title')
    author = request.forms.get('author')
    year = request.forms.get('publication_year')
    isbn = request.forms.get('isbn')
    price = request.forms.get('price')
    course_id = request.forms.get('course_id') or None

    try: 
        cur = DB.cursor()
    
        cur.execute("""
            INSERT INTO public.books (title, author, publication_year, isbn)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (title, author, year, isbn))
        book_id = cur.fetchone()[0]
        # Sparar annons i ads-tabellen, med koppling till kurs om vald
        cur.execute("""
            INSERT INTO ads (book_id, username, price, course_id)
            VALUES (%s, %s, %s, %s);
        """, (book_id, username, price, course_id))

        DB.commit()
        cur.close()

    except Exception as e:
        print("Ett fel uppstod när boken skulle sparas")
        DB.rollback()

    redirect('/book_list')


@app.route('/guide')
def guide():
    return template('guide')

@app.route('/')  #Ändrade denna för att den ska funka med de olika sessionerna
def index():
    s = request.environ.get('beaker.session')
    username = s.get('user', None)
    return template('index', username=username)


@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@app.route('/contact')
def contact():
    return template('contact')

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
        print("users.json sparad!")
    except Exception as e:
        print("Kunde inte spara users.json:", e)

from bottle import request, response

@app.route('/login', method=['GET', 'POST'])
def login():
    s = request.environ.get('beaker.session')
    if request.method == 'POST':
        username = request.forms.get('username')
        password = request.forms.get('password')
        users_data = read_users()
        user = next((user for user in users_data['users'] if user['username'] == username), None)
        if user and user['password'] == password:
            s['user'] = username
            s.save()
            redirect('/')
        else:
            return template('login_failed')
    return template('login')


@app.route('/register', method=['GET', 'POST'])
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

@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@app.route('/logout')
def logout():
    s = request.environ.get('beaker.session')
    s.delete()
    redirect('/')
    
#En route för att lägga till böckerna MEN det är sparat i sessions för profilen
#Uppdatering 3 juni(Nellie): lagt till hämtning av courses och title/content för att undvika krash, när programmet körs körs bara denna vers av routen som är längst ner och inte den ovanför
#tror denna route är överflödig nu (eftersom jag redigerat den ovan), men väntar med att ta bort
@app.route('/route_add_book') 
def add_book_ad():
    s = request.environ.get('beaker.session')
    username = s.get('user', None)

    cur = DB.cursor()
    cur.execute('select id, name from courses order by name')
    courses = cur.fetchall()
    cur.close()
    
    return template("add_book", username=username, courses=courses, title="", content="")

wrapped_app = SessionMiddleware(app, session_opts)

if __name__ == '__main__':
    run(app=wrapped_app, host='localhost', port=8080, debug=True, reloader=True)

