from django.urls import path
from . import views

urlpatterns = [
    path('', views.editor, name='editor'),
    path('clear', views.cleartable, name='clear'),
]