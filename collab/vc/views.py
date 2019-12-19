from django.http import HttpResponse
from django.shortcuts import render
from .models import head_table,sha_table,cred
from django.db import connection
from django.http import HttpResponseRedirect

import hashlib

def cleartable(request):
    with connection.cursor() as cursor:
        for i in range(1,100):
            num="c"+str(i)
            try:
                cursor.execute("ALTER TABLE vc_commit_table drop COLUMN {0};".format(num))
            except:
                pass
        cursor.execute("delete from vc_sha_table;")
        cursor.execute("delete from vc_commit_table;")
        cursor.execute("delete from vc_head_table;")
        cursor.execute("insert into vc_head_table (head,nextcommit) values (1,1);")
    return HttpResponseRedirect('/')

def editor(request):
    if request.method == 'GET':
        flag=0
        for codes in cred.objects.filter(email=request.GET['email']):
            if request.GET['code']==codes.invcode:
                flag=1
                break
        if flag==0: 
            return HttpResponseRedirect('/')
        else:
            head=head_table.objects.all()[0]
            hh=head.head
            num=str(hh)
            strg=""
            for line in commit_table.objects.get(codes=request.GET['code']).all():
                shas=line.objects.values(keys)[hh]
                return HttpResponse(shas)
                text=sha_table.object.get(pk=shas)
                strg=strg+text
            return render(request, 'vc/editor.html',{'savedtext':strg , 'code': request.GET['code'] }) 
    if request.method == 'POST':
        text=request.POST['text']
        text=text.splitlines()
        head=head_table.objects.all()[0]
        hh=head.nextcommit
        num=str(hh)
        line=1
        for strg in text:
            result = hashlib.sha1(strg.encode())
            result = result.hexdigest()
            result=str(result)
            try:
                q=sha_table(sha=result,string=strg)
                q.save()
            except:
                pass
            result = "\'"+result+"\'"
            if line<=commit_table.objects.count():
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE vc_commit_table SET key[{0}] = {1} where id =  {2} ;".format(num,result,line))
            else:
                with connection.cursor() as cursor:
                    cursor.execute("insert into vc_commit_table (id,key{0}) values( {1} ,{2} );".format(num,line,result))
            line=line+1
        head.head=head.nextcommit
        head.nextcommit+=1
        head.save()
        return render(request, 'vc/editor.html',{'savedtext':strg , 'code':code})
    else:
        return render(request, 'vc/index.html')

def index(request):
    return render(request, 'vc/index.html')

def signup(request):
    if request.method=='POST':
        q=cred(email=request.POST['email2'], invcode=request.POST['code2'])
        q.save()
    return render(request, 'vc/index.html')


