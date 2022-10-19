from django.urls import path
from . import views


urlpatterns = [
    path('blobHandle',views.generateDetectionLog),
    path('loadPeople/', views.loadPeopleToRecog, name="loadPeople"),
]
