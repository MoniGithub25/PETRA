import speech_recognition as sr
import subprocess as sub
import pyttsx3
import pywhatkit
import datetime
import wikipedia
from pygame import mixer
import keyboard
import colors
import os
from tkinter import *
from PIL import Image, ImageTk
import threading as tr
import whatsapp
import database
from chatterbot import ChatBot
from chatterbot import preprocessors
from chatterbot.trainers import ListTrainer

main_window = Tk()
main_window.title("PETRA IA")


main_window.geometry("1180x750")#anchoxalto
main_window.resizable(0,0)
main_window.configure(bg='#f64f59')

comandos = """          
            Comandos que puedes usar:
                -Reproduce...(canción deseada)
                -Busca...(algo)
                -Abre...(página web/app)
                -Alarma...(hora en 24H)
                -Archivo...(nombre)
                -Colores(rojo, amarillo, azul)
                -Escribe...(esperar indicaciones)
                -Termina
"""

label_title = Label(main_window, text = "PETRA IA", bg="#c471ed", fg="#2c3e50", font=('Coming soon',18, 'bold'))
label_title.place(x=600, y=10)

canvas_comandos = Canvas(bg="#aa4b6b", height = 200, width=300)
canvas_comandos.place(x=30, y=60)
canvas_comandos.create_text(130,100,text=comandos, fill="white", font=('Arial',13))

text_info=Text(main_window, bg="#aa4b6b", fg="#200122")
text_info.place(x=30, y=280, height= 280, width=300)


petra_photo= ImageTk.PhotoImage(Image.open("asistente22.png"))
window_photo = Label(main_window, image = petra_photo)
window_photo.place(x=380, y=60)


def voz_español():
    change_voice(0)
def voz_ingles():
    change_voice(1)

def change_voice(id):
    engine.setProperty('voice', voices[id].id)
    engine.setProperty('rate', 145)
    talk("Hola soy Petra")



name = 'PETRA'
listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 145)

#DICCIONARIO
def charge_data(name_dict, name_file):
    try:
        with open(name_file) as f:
            for line in f:
                (key, val) = line.split(",")
                val = val.rstrip('\n')
                name_dict[key] = val
    except FileNotFoundError as e:
        pass


sites =dict()
charge_data(sites, "pages.txt")
files=dict()
charge_data(files, "archivos.txt")
programs= dict()
charge_data(programs, "apps.txt")
contacts = dict()
charge_data(contacts, "contacts.txt")



def talk(text):
    engine.say(text)
    engine.runAndWait()

def read_and_talk():
    text=text_info.get("1.0", "end")
    talk(text)

def write_text(text_wiki):
    text_info.insert(INSERT, text_wiki)


def listen(phrase=None):
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
        talk(phrase)
        pc = listener.listen(source)
    try:
        rec = listener.recognize_google(pc, language="es")
        rec = rec.lower()
    except sr.UnknownValueError:
        print("No te entendí, intenta de nuevo")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return rec


#Funciones asociadas a las palabras claves
def reproduce(rec):
    song = rec.replace('reproduce', '')
    print("Reproduciendo: " + song)
    talk('Reproduciendo ' + song)
    pywhatkit.playonyt(song)

def busca(rec):
    search = rec.replace('busca', '')
    wikipedia.set_lang("es")
    wiki = wikipedia.summary(search, 1)
    talk(wiki)
    write_text(search + ": " + wiki)

def thread_alarma(rec):
    t = tr.Thread(target=reloj , args=(rec,))
    t.start()

def colores(rec):
    talk("Enseguida")
    colors.capture()

def abre(rec):
    task = rec.replace('abre','').strip()

    if task in sites:
        for task in sites:
            if task in rec:
                sub.call(f'start chrome.exe {sites[task]}', shell= True)
                talk(f'Abriendo {task}')
    elif task in programs:
        for task in programs:
            if task in rec:
                talk(f'Abriendo {task}')
                os.startfile(programs[task])
    else:
        talk("Lo siento, parece que aún no has agregado esa app o pagina web, \
            usa los botones de agregar") 

def archivo(rec):
    file = rec.replace('archivo', '').strip()
    
    if file in files:
        for file in files:
            if file in rec:
                sub.Popen([files[file]], shell=True)
                talk(f'Abriendo {file}')
    else:
        talk("Lo siento, parece que aún no has agregado ese archivo, \
            usa los botones de agregar")

def escribe(rec):
    try:
        with open("nota.txt", 'a') as f:
            write(f)
    except FileNotFoundError as e:
        file = open("nota.txt", 'a')
        write(file)


def reloj(rec):
    num = rec.replace('alarma', '')
    num = num.strip()
    talk("Alarma activada a las "+ num + " horas")
    if num[0] != '0' and len(num) < 5:
        num = '0' + num
    print(num)
    while True:
        if datetime.datetime.now().strftime('%H:%M') == num:
            print("DESPIERTA!!!")
            mixer.init()
            mixer.music.load("scarlet-witch.mp3")#Pendeja, el archivo funciona si se convierte en esta página en especifico -> https://en.onlymp3.to/22/
            mixer.music.play()
        else:
            continue
        if keyboard.read_key() == 's':
            mixer.music.stop()
            break

def enviar_mensaje(rec):
    talk("¿A quien quieres enviar el mensaje?")
    contact = listen("Te escucho")
    contact = contact.strip()

    if contact in contacts:
        for cont in contacts:
            if cont == contact:
                contact = contacts[cont]
                talk("¿Qué mensaje quieres enviarle?")
                message = listen("")#Esperar 1 segundo
                talk("Enviando mensaje")
                whatsapp.send_message(contact, message)
    else:
        talk("Parece que aun no has agregado a ese contacto, usa el boton de agregar")


#Diccionario con palabras claves
key_words={'reproduce': reproduce, 'busca': busca, 'alarma': thread_alarma, 'colores': colores, 'abre': abre, 'archivo': archivo, 'escribe': escribe, 'mensaje': enviar_mensaje}


def run_petra():
    chat = ChatBot("petra", database_uri=None)
    trainer = ListTrainer(chat)
    trainer.train(database.get_questions_answers())
    talk("Te escucho")
    while True:
        try:
            rec = listen("")
        except UnboundLocalError:
            talk("No te entendi, intentalo de nuevo")
            continue
        #EMPIEZA AQUI
        if 'busca' in rec:
            key_words['busca'](rec)
            break
        elif rec.split()[0] in key_words:
            key = rec.split()[0]
            key_words[key](rec)
        else:
            print("Tu: ", rec)
            answer = chat.get_response(rec)
            print("Petra: ", answer)
            talk(answer)
            if 'termina' in rec:
                talk("Adios")
                break
    main_window.update()


def write(f):
    talk("¿Qué quieres que escriba?")
    rec_write = listen("Te escucho")
    f.write(rec_write+ os.linesep)
    f.close()
    talk("Listo, puedes revisarlo")
    sub.Popen("nota.txt", shell=True)

def open_w_files():
    global namefiles_entry, pathf_entry
    window_files = Toplevel()
    window_files.title("Agregar archivos")
    window_files.configure(bg="#0F2027")
    window_files.geometry("300x200")
    window_files.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_files)} center')

    title_label=Label(window_files,text="Agregar archivo", fg="white", bg="#0F2027", font=('Arial',15, "bold"))
    title_label.pack(pady=3)
    name_label = Label(window_files,text="Nombre del archivo", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    name_label.pack(pady=2)

    namefiles_entry=Entry(window_files)
    namefiles_entry.pack(pady=1)

    path_label=Label(window_files,text="Ruta del archivo", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    path_label.pack(pady=3)
    
    pathf_entry=Entry(window_files, width=35)
    pathf_entry.pack(pady=1)

    save_button = Button(window_files, text = 'Guardar', bg='#0F2027', fg="white", width=10, command= add_files)
    save_button.pack(pady=4)


def open_w_apps():
    global nameapp_entry, patha_entry
    window_apps = Toplevel()
    window_apps.title("Agregar apps")
    window_apps.configure(bg="#0F2027")
    window_apps.geometry("300x200")
    window_apps.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_apps)} center')

    title_label=Label(window_apps,text="Agregar app", fg="white", bg="#0F2027", font=('Arial',15, "bold"))
    title_label.pack(pady=3)
    name_label = Label(window_apps,text="Nombre de la app", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    name_label.pack(pady=2)

    nameapp_entry=Entry(window_apps)
    nameapp_entry.pack(pady=1)

    path_label=Label(window_apps,text="Ruta de la app", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    path_label.pack(pady=3)
    
    patha_entry=Entry(window_apps, width=35)
    patha_entry.pack(pady=1)

    save_button = Button(window_apps, text = 'Guardar', bg='#0F2027', fg="white", width=10, command= add_apps)
    save_button.pack(pady=4)

def open_w_pages():
    global namepage_entry, pathp_entry
    window_pages = Toplevel()
    window_pages.title("Agregar paginas web")
    window_pages.configure(bg="#0F2027")
    window_pages.geometry("300x200")
    window_pages.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_pages)} center')

    title_label=Label(window_pages,text="Agregar una pagina", fg="white", bg="#0F2027", font=('Arial',15, "bold"))
    title_label.pack(pady=3)
    name_label = Label(window_pages,text="Nombre de la pagina", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    name_label.pack(pady=2)

    namepage_entry=Entry(window_pages)
    namepage_entry.pack(pady=1)

    path_label=Label(window_pages,text="URL de la pagina web", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    path_label.pack(pady=3)
    
    pathp_entry=Entry(window_pages, width=35)
    pathp_entry.pack(pady=1)

    save_button = Button(window_pages, text = 'Guardar', bg='#0F2027', fg="white", width=10, command= add_pages)
    save_button.pack(pady=4)

def open_w_contacts():
    global namecontacts_entry, pathc_entry
    window_contacts = Toplevel()
    window_contacts.title("Agregar un contacto")
    window_contacts.configure(bg="#0F2027")
    window_contacts.geometry("300x200")
    window_contacts.resizable(0,0)
    main_window.eval(f'tk::PlaceWindow {str(window_contacts)} center')

    title_label=Label(window_contacts,text="Agregar un contacto", fg="white", bg="#0F2027", font=('Arial',15, "bold"))
    title_label.pack(pady=3)
    name_label = Label(window_contacts,text="Nombre del contacto", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    name_label.pack(pady=2)

    namecontacts_entry=Entry(window_contacts)
    namecontacts_entry.pack(pady=1)

    path_label=Label(window_contacts,text="Numero del contacto(con codigo del pais)", fg="white", bg="#0F2027", font=('Arial',10, "bold"))
    path_label.pack(pady=3)
    
    pathc_entry=Entry(window_contacts, width=35)
    pathc_entry.pack(pady=1)

    save_button = Button(window_contacts, text = 'Guardar', bg='#0F2027', fg="white", width=10, command= add_contacts)
    save_button.pack(pady=4)

def add_files():
    name_file= namefiles_entry.get().strip()
    path_file = pathf_entry.get().strip()

    files[name_file] = path_file
    save_data(name_file, path_file, "archivos.txt")
    namefiles_entry.delete(0, "end")
    pathf_entry.delete(0, "end")


def add_apps():
    name_file= nameapp_entry.get().strip()
    path_file = patha_entry.get().strip()

    programs[name_file] = path_file
    save_data(name_file, path_file, "apps.txt")
    nameapp_entry.delete(0, "end")
    patha_entry.delete(0, "end")

def add_pages():
    name_page= namepage_entry.get().strip()
    url_page = pathp_entry.get().strip()

    sites[name_page] = url_page
    save_data(name_page, url_page, "pages.txt")
    namepage_entry.delete(0, "end")
    pathp_entry.delete(0, "end")

def add_contacts():
    name_contact= namecontacts_entry.get().strip()
    phone = pathc_entry.get().strip()

    contacts[name_contact] = phone
    save_data(name_contact, phone, "contacts.txt")
    namecontacts_entry.delete(0, "end")
    pathc_entry.delete(0, "end")

def save_data(key, value, file_name):
    try:
        with open(file_name, 'a') as f:
            f.write(key + ','+ value + "\n")
    except FileNotFoundError:
        file = open(file_name, 'a')
        file.write(key + ',' + value + "\n")

def talk_pages():
    if bool(sites) == True:
        talk("Has agregado las siguientes paginas web")
        for site in sites:
            talk(site)
    else:
        talk("Aun no has agregado paginas web")

def talk_apps():
    if bool(programs) == True:
        talk("Has agregado las siguientes apps")
        for app in programs:
            talk(app)
    else:
        talk("Aun no has agregado apps")

def talk_files():
    if bool(files) == True:
        talk("Has agregado los siguientes archivos")
        for file in files:
            talk(file)
    else:
        talk("Aun no has agregado archivo")

def talk_contacts():
    if bool(contacts) == True:
        talk("Has agregado los siguientes contactos")
        for cont in contacts:
            talk(cont)
    else:
        talk("Aun no has agregado contactos")

def give_me_name():
    talk("Hola, ¿como te llamas?")
    name = listen("Te escucho")
    name = name.strip()
    talk(f"Bienvenida {name}")

    try:
        with open("name.txt", "w") as f:
            f.write(name)
    except FileNotFoundError:
        file = open("name.txt", "w")
        file.write(name)

def say_hello():

    if os.path.exists("name.txt"):
        with open("name.txt") as f:
            for name in f:
                talk(f"Hola, bienvenida {name}")
    else:
        give_me_name()

def thread_hello():
    t= tr.Thread(target=say_hello)
    t.start()

thread_hello()


button_voice_es = Button(main_window, text="Voz Español", fg = "white", bg="#4776E6", font=('Arial', 10, "bold"), command= voz_español)
button_voice_es.place(x=950, y=60, width =100, height=30)

button_voice_us = Button(main_window, text="Voz Ingles", fg = "white", bg="#4776E6", font=('Arial', 10, "bold"), command= voz_ingles)
button_voice_us.place(x=950, y=110, width =100, height=30)

#ESCUCHAR
button_listen = Button(main_window, text="Escuchar", fg = "white", bg="#1565C0", font=('Arial', 15, "bold"),width=42, height=2, command= run_petra)
button_listen.place(x=380, y=680)
#button_listen.pack(side = BOTTOM, pady=10)

button_speak = Button(main_window, text="Hablar", fg = "white", bg="#4776E6", font=('Arial', 10, "bold"),width=20, height=2, command= read_and_talk)
button_speak.place(x=950, y=160, width =100, height=30)

button_add_files = Button(main_window, text="Agregar archivos", fg = "white", bg="#4776E6", font=('Arial', 10, "bold"),width=20, height=2, command= open_w_files)
button_add_files.place(x=940, y=210, width =120, height=30)

button_add_apps = Button(main_window, text="Agregar apps", fg = "white", bg="#4776E6", font=('Arial', 10, "bold"),width=20, height=2, command= open_w_apps)
button_add_apps.place(x=940, y=260, width =120, height=30)

button_add_pages = Button(main_window, text="Agregar paginas", fg = "white", bg="#4776E6", font=('Arial', 10, "bold"),width=20, height=2, command= open_w_pages)
button_add_pages.place(x=940, y=310, width =120, height=30)

button_tell_pages = Button(main_window, text="Paginas agregadas", fg = "white", bg="#556270", font=('Arial', 8, "bold"),width=20, height=2, command= talk_pages)
button_tell_pages.place(x=380, y=580, width =125, height=30)

button_tell_apps = Button(main_window, text="Apps agregadas", fg = "white", bg="#556270", font=('Arial', 8, "bold"),width=20, height=2, command= talk_apps)
button_tell_apps.place(x=570, y=580, width =125, height=30)

button_tell_files = Button(main_window, text="Archivos agregadas", fg = "white", bg="#556270", font=('Arial', 8, "bold"),width=20, height=2, command= talk_files)
button_tell_files.place(x=760, y=580, width =125, height=30)

button_add_contacts = Button(main_window, text="Agregar contactos", fg = "white", bg="#4776E6", font=('Arial', 9, "bold"),width=20, height=2, command= open_w_contacts)
button_add_contacts.place(x=940, y=360, width =125, height=31)

button_tell_contacts = Button(main_window, text="Contactos agregados", fg = "white", bg="#556270", font=('Arial', 8, "bold"),width=20, height=2, command= talk_contacts)
button_tell_contacts.place(x=570, y=630, width =125, height=30)



main_window.mainloop()