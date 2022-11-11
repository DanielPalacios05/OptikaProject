from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template #para poder renderizar el HTML del correo
from django.core.mail import EmailMultiAlternatives #Funcion que tiene Django para mandar correos
from django.conf import settings #para traer la informacion del correo
import os, sys
import threading
from OptikaWeb.bdconnect import *
from facialRecog.facialrecognition import *
from .forms import FileFormset,PersonForm
from .workers import loadFacesToFirebase


def home(request):
    return render(request, 'home.html')

def peopleToRecog(request):
    people_ref = db.collection(u'KnownPeople')
    people = people_ref.stream()
    people_to_recog = []
    for person in people:
        people_dict = person.to_dict()
        people_dict['id'] = person.id
        people_to_recog.append(people_dict)
    return render(request, 'peopleToRecog.html', {'people_to_recog': people_to_recog})

def deletePerson(request, id):
     delKnownPerson(id)
     return redirect('/peopleToRecog/')    

def mainPage(request):  
    return render(request, 'mainPage.html')

def addPerson(request):

    if request.method == 'GET':
        nameform = PersonForm()
        fileForm = FileFormset()
    elif request.method == 'POST':
        
        nameform = PersonForm(request.POST)
        fileForms = FileFormset(request.POST,request.FILES)

        fileList = []


        if nameform.is_valid():

            for form in fileForms:

                if form.is_valid() and form.has_changed():
                    
                    fileList.append(form.cleaned_data["image"])
          
        loadFacesToFirebase(fileList,nameform.cleaned_data["name"])
            
        return redirect("/")




    return render(request, 'addPerson.html',{'nameForm':nameform,'fileForms':fileForm})

def liveCam(request):
    return render(request, 'liveCam.html')

#funcion para enviar el correo
def send_email(mail, nombre, conocido, imagen):
    
    context = {'mail': mail, 'name': nombre, 'conocido': conocido, 'imagen': imagen}

    template = get_template('correoB.html')
    content = template.render(context)

    if(conocido == "conocida"):
        print("voy a mandar un correo de conocido")

        email = EmailMultiAlternatives( # estructura del correo
            'Se ha detectado a ' + nombre, #titulo del correo
            'God Bless', #parametro necesario
            settings.EMAIL_HOST_USER,
            [mail]
        )
    if(conocido == "desconocida"):
        print("voy a mandar un correo de desconocido")

        email = EmailMultiAlternatives( 
            'Se ha detectado a una persona desconocida!',
            'God Bless',
            settings.EMAIL_HOST_USER,
            [mail]
        )

    email.attach_alternative(content, 'text/html')
   
    email.send() 

def detections(request):
    detections_ref = db.collection(u'Detections')

    # Create an Event for notifying main thread.
    delete_done = threading.Event()
    # Create a callback on_snapshot function to capture changes
    def on_snapshot(col_snapshot, changes, read_time):

        cantidad = len(changes)
        contador = 0

        print(u'Callback received query snapshot.')
        for change in changes:
            contador = contador + 1
            if change.type.name == 'ADDED':
                print(f'Added: {change.document.id}')
                
                #para que solo envie alertas por cada registro nuevo, y no por los varios que se cargan
                if(contador == cantidad and cantidad < 2): 

                    idDetecion = change.document.id

                    doc_ref = db.collection(u'Detections').document(idDetecion)
                    doc = doc_ref.get() #obtener el documento de la persona detectada

                    nombre = doc.to_dict()["name"]
                    conocidoTrueFalse = doc.to_dict()["known"]
                    imagen = doc.to_dict()["img_url"]

                    print(conocidoTrueFalse) #test
                    if(conocidoTrueFalse is True):
                        conocido = "conocida"
                        print("soy conocida")
                    else:
                        conocido = "desconocida"
                        print("soy desconocida")

                    send_email('optikaeafit@gmail.com', nombre, conocido, imagen)

    col_query = db.collection(u'Detections')
    # Watch the collection query
    query_watch = col_query.on_snapshot(on_snapshot)
    docs = detections_ref.stream() 

    detections = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id
        detections.append(doc_dict)
    return render(request, 'detections.html', {'detections': detections})    
                            

#--------------------------------------------------------------------------------------------------------
#existe dos formas de mandar informacion al servidor. Post y get.
#post es para cosas que son secretas, como la password. Porque sino, otras personas podrian verla 

#el get se hace para recibir informacion
