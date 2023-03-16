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
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties

IOTHUB_CONNECTION_STRING = os.environ.get("DEVICE_CONN")
DEVICE_ID = os.environ.get("DEVICE_ID")
iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)


def home(request):
    return render(request, 'home.html')

def peopleToRecog(request):
    people_ref = db.collection(u'KnownPeople')
    people = people_ref.stream()
    people_to_recog = []
    for person in people:
        people_dict = person.to_dict()
        people_dict["id"] = person.id
        people_to_recog.append(people_dict)

    if request.method == 'POST':
        files = request.FILES
        file_key = list(files.keys())[0]
        print(file_key)
        uid = file_key[8:]
        payload = files.getlist(file_key)

        loadFacesToFirebase(payload, uid,True)

        return redirect('/peopleToRecog')

    return render(request, 'peopleToRecog.html', {'people_to_recog': people_to_recog})

def deletePerson(request, id):
    delKnownPerson(id)
    return redirect('/peopleToRecog/')    

def deleteImage(request, name, index):
    removePersonImage(name,index)
    return redirect('/peopleToRecog')

def deleteDetections(request):
    delDetections()
    return redirect('/detections/')

def deletePersonImage(request,id,index):
    removePersonImage(id,index)
    return redirect("/peopleToRecog")

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

            name = nameform.cleaned_data["name"]
            loadFacesToFirebase(fileList, name,False)
        return redirect("/peopleToRecog")
    return render(request, 'addPerson.html',{'nameForm':nameform,'fileForms':fileForm})


def addPersonImage(request,name,id):
    return redirect("/peopleToRecog")

def liveCam(request):
    twin = iothub_registry_manager.get_twin(DEVICE_ID)
    twin_patch = Twin(properties= TwinProperties(desired={'readyToSend' : False}))
    twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)

    return render(request, 'liveCam.html')

def exitLive(request):
    twin = iothub_registry_manager.get_twin(DEVICE_ID)
    twin_patch = Twin(properties= TwinProperties(desired={'readyToSend' : True}))
    twin = iothub_registry_manager.update_twin(DEVICE_ID, twin_patch, twin.etag)
    return redirect("/mainPage")

#funcion para enviar el correo
def detections(request):
    detections_ref = db.collection(u'Detections').order_by(u'datetime', direction=firestore.Query.DESCENDING)
    
    col_query = db.collection(u'Detections')
    # Watch the collection query
    docs = detections_ref.stream() 

    detections = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id
        detections.append(doc_dict)
    return render(request, 'detections.html', {'detections': detections})    
                            
#--------------------------------------------------------------------------------------------------------