from django.contrib import admin
from django.urls import path
from webApp import views as optViews
from django.urls import include
from facialRecog import urls as facialRecogUrls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', optViews.home, name="home"), 
    path('mainPage/', optViews.mainPage,name="mainPage"),
    path('liveCam', optViews.liveCam,name="liveCam"),
    path('detections/', optViews.detections, name="detections"),
    path('exitCamera', optViews.exitLive, name="exitLiveCamera"),
    path('peopleToRecog/', optViews.peopleToRecog,name="peopleToRecog"), #Gente a reconocer 
    path('peopleToRecog/addPerson/', optViews.addPerson,name="addPerson"), #Gente a reconocer 
    path('api/',include(facialRecogUrls)),
    path('deleteKnown/<slug:id>', optViews.deletePerson, name="delete-known-person"),
    path('deleteDetections/', optViews.deleteDetections, name="delete-detections"),
    path('deletePersonImage/<str:id>/<int:index>',optViews.deletePersonImage,name="delete-image"),
    path('addPersonImage/<str:id>/<int:index>',optViews.addPersonImage,name="addPersonImage"),
]
