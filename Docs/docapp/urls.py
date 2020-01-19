from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^chat/(?P<c_name>[^/]+)/(?P<room_name>[^/]+)/$', views.main, name='main'),
]