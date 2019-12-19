from django.http import HttpResponse
from django.shortcuts import render
from .models import headt,commit_table,sha_table,cred
from django.db import connection
from django.http import HttpResponseRedirect

import hashlib

def cleartable(request):
    with connection.cursor() as cursor:
        cursor.execute("delete from vc_sha_table;")
        cursor.execute("delete from vc_commit_table;")
        cursor.execute("update vc_headt set head =1 ,nextcommit=1;")
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
            head=headt.objects.filter(pk=request.GET['email'])
            if head.count()==0:
                q=headt(email=request.GET['email'],head=1,nextcommit=1)
                q.save()
            head=headt.objects.get(pk=request.GET['email'])
            hh=head.head
            num=str(hh)
            strg=""
            con=""
            lastemail=request.GET['email']
            lastinv=request.GET['code']
            for line in commit_table.objects.filter(code=request.GET['code']).all():
                shas=line.key[hh-2]
                shas=shas[1:-1]
                con+=str(shas)+" " 
                text=sha_table.objects.filter(pk=shas).values('string')
                if(text.count()==0):
                    continue
                text=text[0]["string"]
                if(text=="null"):
                    continue
                strg=strg+str(text)+"\n"
            #return HttpResponse(lastinv)
            return render(request, 'vc/editor.html',{'savedtext':strg , 'code': lastinv , 'email' : lastemail})
    if request.method == 'POST':
        essay=request.POST['text']
        fixedcode=request.POST['code']
        fixedemail=request.POST['email']
        text=essay.splitlines()
        head=headt.objects.get(pk=fixedemail)
        hh=head.head
        num=str(hh)
        line=1
        for strg in text:
            result = hashlib.sha1(strg.encode())
            result = result.hexdigest()
            result=str(result)
            if sha_table.objects.filter(sha=result).count()==0:
                q=sha_table(sha=result,string=strg)
                q.save()
            result = "\'"+result+"\'"
            if line<=commit_table.objects.filter(code=fixedcode).count():
                q=commit_table.objects.filter(code=fixedcode)
                q=q.filter(linenum=line)
                q=q[0]
                q.key[hh-1]=result
                q.save()
            else:
                arr=[]
                for i in range(0,1000):
                    arr.append('null')
                q=commit_table(code=fixedcode,linenum=line,key=arr)
                q.save()
                q=commit_table.objects.filter(code=fixedcode)
                q=q.filter(linenum=line)
                q=q[0]
                q.key[hh-1]=result
                q.save()
                
            line=line+1
        head.head=head.nextcommit
        head.nextcommit+=1
        head.save()
        return render(request, 'vc/editor.html',{'savedtext':essay , 'code':fixedcode ,'email': fixedemail})
    else:
        return render(request, 'vc/index.html')

def index(request):
    return render(request, 'vc/index.html')

def signup(request):
    if request.method=='POST':
        q=cred(email=request.POST['email2'], invcode=request.POST['code2'])
        q.save()
    return render(request, 'vc/index.html')


