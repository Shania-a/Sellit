from bottle import route, run, template, static_file, request, redirect
from os import listdir #denna 
import os #denna kan man använda för att göra en funktion som tar bort böcker


@route('/add_book_ad') 
#detta är del 1 och efter detta läggs det till en till del som sparar boken. 
#funkar inte just nu med bara detta och felkoderna visas fortfarande på html-filen.
#behöver antagligen skriva fler funktioner innan det bröjar funka, funktioner som sparar filer etc
#behöver också kolla om det är någon variabel som saknas i koden som gör att felkoderna visas i html

def add_book_ad():
    return template("add_book", title="", content="", errors={'title': None, 'content': None})


@route("/save_book_ad", method="POST")
def save_book_ad():
    title = request.forms.get("title")
    content = request.forms.get("content")    

    errors = {}

    if not title:
        errors["title"] = "Fyll i artikelns titel"
    if not content:
        errors["content"] = "Fyll i artikelns innehåll"

    if errors:
        return template("add_book", title=title or "", content=content or "", errors=errors)
    
    save_file(title, content)
    return redirect("/")

@route('/') #startsida
def index():
    return template('index')

@route('/static/<filename>') #css-filer
def server_static(filename):
    return static_file(filename, root='static') 



run(host='localhost', port=8080, debug=True, reloader=True)