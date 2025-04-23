from bottle import route, run, template, static_file, request, redirect
from os import listdir #denna 
import os #denna kan man använda för att göra en funktion som tar bort böcker och för att spara filer i mappen 

save_folder = "book_ads" #mappen där böckerna sparas

if not os.path.exists(save_folder): #kollar om mappen finns, om inte så skapas den
    os.makedirs(save_folder)

#sparar böckerna i mappen book_ads, tar emot en titel och innehåll och sparar det i en textfil
def save_file(title, content):
    file = f"book_ads/{title}.txt"
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)
        f.close()
    
@route('/route_add_book') 
def add_book_ad():
    return template("add_book", title="", content="")

@route("/save_book_ad", method="POST")
def save_book_ad():
    title = request.forms.get("title")
    content = request.forms.get("content")    
    
    save_file(title, content)
    return redirect("/")

@route('/') #startsida
def index():
    return template('index')

@route('/static/<filename>') #css-filer
def server_static(filename):
    return static_file(filename, root='static') 

@route('/login')
def login():
    return template('login')

run(host='localhost', port=8080, debug=True, reloader=True)