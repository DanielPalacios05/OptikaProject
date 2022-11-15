"""optika URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webApp import views as optViews
from django.urls import include
from facialRecog import urls as facialRecogUrls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', optViews.home, name="home"), 
    path('exitCamera', optViews.exitLive, name="exitLiveCamera"),
    path('peopleToRecog/', optViews.peopleToRecog,name="peopleToRecog"), #Gente a reconocer 
    path('peopleToRecog/addPerson/', optViews.addPerson,name="addPerson"), #Gente a reconocer 
    path('mainPage/', optViews.mainPage,name="mainPage"),
    path('liveCam', optViews.liveCam,name="liveCam"),
    path('detections/', optViews.detections, name="detections"),
    path('api/',include(facialRecogUrls)),
    path('deleteKnown/<slug:id>', optViews.deletePerson, name="delete-known-person"),
    path('deleteDetections/', optViews.deleteDetections, name="delete-detections"),
    path('deletePersonImage/<str:id>/<int:index>',optViews.deletePersonImage,name="deletePersonImage"),
    path('addPersonImage/<str:id>/<int:index>',optViews.addPersonImage,name="addPersonImage"),
]
