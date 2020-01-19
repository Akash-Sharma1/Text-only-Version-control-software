from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe
import json


# Create your views here.
import pymongo
from pymongo import MongoClient

#db = cluster["docs"]
#collection = db["document"]
#post = {"_line":0,"_string":"abcd"}
#collection.insert_one(post)
#collection.insert_many(post)
#result = collection.find({"_line":1,"_string":""}) #find_one # find_many 
# {}means everything
#print(result) #gives object
#for res in result:
#   print(res)
#   print(res["_string"])
#results=collection.delete_many({"_id":0})
#results=collection.update_many({"_id":5},{"$set":{"name":"tim"}})
#post_count=collection.count_documents({})
#print(post_count)

def extra(request):
    cluster = MongoClient("mongodb+srv://Akash:@cluster0-7trci.mongodb.net/test?retryWrites=true&w=majority")
    db = cluster["Docs"]
    collection = db["Document"]
    post_count=collection.count()
    #post = {"_line":post_count+1,"_string":"abcd"}
    #collection.insert_one(post)
    val=collection.find({})
    string=""
    for i in val:
        string+=i["_string"]+"\r\n"
    return render(request, 'docapp/edit.html',{"para":string})


def index(request):
    return render(request, 'docapp/index.html', {})

def main(request, room_name,c_name):
    return render(request, 'docapp/edit.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'name_json': mark_safe(json.dumps(c_name))
    })