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
    return render(request, 'peopleToRecog.html') 

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

#ASI ES COMO TENIA DETECTIONS JUAN
# def detections(request): 
#     return render(request, 'detections.html', {'detections': app.getDetections()})

#funcion para emviar el correo
def send_email(mail):
    context = {'mail': mail}

    template = get_template('correo.html')
    content = template.render(context)

    email = EmailMultiAlternatives( # estructura del correo
        'Se ha detectado a una persona',
        'God Bless',
        settings.EMAIL_HOST_USER,
        [mail]
    )

    email.attach_alternative(content, 'text/html')
    email.send()


    print(mail)

def about(request):
    if request.method == 'POST':
        mail = request.POST.get('mail')
        send_email(mail)


    return render(request, 'about.html', {})

def detections(request):



    detections_ref = db.collection(u'Detections')

    
    # Create an Event for notifying main thread.
    delete_done = threading.Event()
    # Create a callback on_snapshot function to capture changes
    def on_snapshot(col_snapshot, changes, read_time):

        cantidad = len(changes)
        contador = 0

        #print(cantidad)
        print(u'Callback received query snapshot.')
        for change in changes:
            contador = contador + 1
            #print(contador)
            if change.type.name == 'ADDED':
                print(f'Added: {change.document.id}')
                # print(f'se llama: {change.document.name}')
                #para que solo envie alertas por cada registro nuevo, y no por los varios que se cargan
                if(contador == cantidad and cantidad < 2): 
                    print("BRO MOMENTO")
                    send_email('optikaeafit@gmail.com')
                    #escribir el correo aqui 

            elif change.type.name == 'MODIFIED':
                print(f'Modified: {change.document.id}')
            elif change.type.name == 'REMOVED':
                print(f'Removed: {change.document.id}')
                delete_done.set()

    col_query = db.collection(u'Detections')
    # Watch the collection query
    query_watch = col_query.on_snapshot(on_snapshot)


    docs = detections_ref.stream() #juan
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