from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe
import json


def index(request):
    return render(request, 'docapp/index.html', {})

def main(request, room_name,c_name):
    return render(request, 'docapp/edit.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'name_json': mark_safe(json.dumps(c_name))
    })