from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from OptikaWeb.bdconnect import FirebaseManager


app = FirebaseManager()

def home(request):
    return render(request, 'home.html')

def peopleToRecog(request):
    return render(request, 'peopleToRecog.html') 

def mainPage(request):  
    return render(request, 'mainPage.html')

def addPerson(request):
    return render(request, 'addPerson.html')

def liveCam(request):
    return render(request, 'liveCam.html')

def detections(request):
    return render(request, 'detections.html', {'detections': app.getDetections()})
                            

#--------------------------------------------------------------------------------------------------------
#existe dos formas de mandar informacion al servidor. Post y get.
#post es para cosas que son secretas, como la password. Porque sino, otras personas podrian verla 

#el get se hace para recibir informacion