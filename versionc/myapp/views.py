from django.http import HttpResponse
from django.shortcuts import render
from .models import commit_table,head_table,sha_table
from django.db import connection
from django.http import HttpResponseRedirect
from .forms import commitform

import hashlib

def cleartable(request):
    with connection.cursor() as cursor:
        for i in range(1,100):
            num="c"+str(i)
            try:
                cursor.execute("ALTER TABLE myapp_commit_table drop COLUMN {0};".format(num))
            except:
                pass
        cursor.execute("delete from myapp_sha_table;")
        cursor.execute("delete from myapp_commit_table;")
        cursor.execute("delete from myapp_head_table;")
        cursor.execute("insert into myapp_head_table (head,nextcommit) values (1,1);")
        
    form = commitform()
    return render(request, 'myapp/editor.html', {'form': form})

#def add(request):
#    if request.method == 'POST':
#        form = inform(request.POST)
#        return HttpResponseRedirect('/thanks/')
#    else:
#        return HttpResponse("OK")
#    num="c"+"3"
#    with connection.cursor() as cursor:
#        cursor.execute("ALTER TABLE myapp_commit_table ADD COLUMN {0} varchar(50) NOT NULL;".format(num))
#    return HttpResponse("OK")

def editor(request):
    if request.method == 'POST':
        form = commitform(request.POST)
        if form.is_valid():
            pass
        text = form['TextFile'].value()
        head=head_table.objects.all()[0]
        hh=head.nextcommit
        num="c"+str(hh)
        text=text.splitlines()
        line=1
        with connection.cursor() as cursor:
            try:
                cursor.execute("ALTER TABLE myapp_commit_table ADD COLUMN {0} varchar(50);".format(num))
            except:
                pass
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
                    cursor.execute("UPDATE myapp_commit_table SET {0} = {1} where id =  {2} ;".format(num,result,line))
            else:
                with connection.cursor() as cursor:
                    cursor.execute("insert into myapp_commit_table (id,{0}) values( {1} ,{2} );".format(num,line,result))
            line=line+1
        
        head.head=head.nextcommit
        head.nextcommit+=1
        head.save()
        messages.add_message(request, messages.INFO, 'Hello world.')
    else:
        form = commitform()
    return render(request, 'myapp/editor.html', {'form': form})
