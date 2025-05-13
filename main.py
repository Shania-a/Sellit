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
 #Tror vi kan ta bort den här och save_file som är under nu när vi har databas
save_folder = "book_ads"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

def save_file(title, content):
    path = f"{save_folder}/{title}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

@route('/book_list')
def book_list():
    """
    Visar en lista med böcker från databasen. Användaren kan:
      - Söka på titel eller författare (parameter: q)
      - Filtrera på kursnamn (parameter: course)
      - Filtrera på programnamn (parameter: program)

    Funktionen gör tre saker:
    - Hämtar filtrerningsparametrar från URLL:en (det som användaren har matat in) 
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
            select distinct b.id, b.title, b.author, b.publication_year, b.isbn
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

@route('/route_add_book')
def add_book_ad():
    return template("add_book", title="", content="")

@route('/save_book', method='POST')
def save_book():
    title = request.forms.title
    author = request.forms.author
    year = request.forms.publication_year
    isbn = request.forms.isbn

    cur = DB.cursor()
    cur.execute("""
        INSERT INTO public.books (title, author, publication_year, isbn)
        VALUES (%s, %s, %s, %s);
    """, (title, author, year, isbn))
    DB.commit()
    cur.close()

    redirect('/book_list')

@route('/guide')
def guide():
    return template('guide')

@route('/')
def index():
    return template('index')

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

@route('/login')
def login():
    return template('login')

@route('/contact')
def contact():
    return template('contact')

if __name__ == '__main__':
    run(host='localhost', port=8080, debug=True, reloader=True)
