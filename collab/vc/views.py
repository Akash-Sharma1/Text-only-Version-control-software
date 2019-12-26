from django.http import HttpResponse
from django.shortcuts import render
from .models import headt,commit_table,sha_table,cred,commit_info,code_info
from django.db import connection
from django.http import HttpResponseRedirect
import datetime
import hashlib

def cleartable(request):
    with connection.cursor() as cursor:
        cursor.execute("delete from vc_sha_table;")
        cursor.execute("delete from vc_commit_table;")
        cursor.execute("delete from vc_headt;")
        cursor.execute("delete from vc_commit_info;")
    return HttpResponseRedirect('/')

def get_text(lastinv,hh):
    num=str(hh)
    strg=""
    dic={}
    for line in commit_table.objects.filter(code=lastinv).all():
        shas=line.key[hh-1]
        shas=shas[1:-1]
        text=sha_table.objects.filter(pk=shas).values('string')
        if(text.count()==0):
            continue
        text=text[0]["string"]
        if(text=="null"):
            continue
        dic[line.linenum]=str(text)+"\r\n"
    for i in sorted(dic):
        strg+=str(dic[i])
    return strg

def editor(request):
    if request.method == 'POST':
        essay=request.POST['text']
        fixedcode=request.session['code']
        fixedemail=request.session['email']
        text=essay.splitlines()
        head=headt.objects.get(pk=fixedcode)
        hh=head.nextcommit
        num=str(hh)
        line=1
        q=commit_info.objects.filter(code=fixedcode)
        if q.count()==0:
            q=commit_info(code=str(fixedcode),commit_email=["null"])
            q.save()
        q=commit_info.objects.filter(code=fixedcode)
        q=q[0]
        q.commit_email.append(str(fixedemail))
        q.last_commit_time=datetime.datetime.now()
        q.last_commit_date=datetime.date.today()
        q.save()
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
                #q.save()
                #q=commit_table.objects.filter(code=fixedcode)
                #q=q.filter(linenum=line)
                #q=q[0]
                q.key[hh-1]=result
                q.save()
            line=line+1
        head.head=head.nextcommit
        head.nextcommit+=1
        head.save()
        return HttpResponseRedirect("/edit")
    else:
        lastemail=request.session['email']
        lastinv=request.session['code']
        head=headt.objects.filter(pk=lastinv)
        if head.count()==0:
            q=headt(code=lastinv,head=1,nextcommit=1)
            q.save()
        head=headt.objects.get(pk=lastinv)
        hh=head.head
        strg=get_text(lastinv,hh)
        return render(request, 'vc/editor.html',{'savedtext':strg , 'code': lastinv , 'email' : lastemail})
    

def index(request):
    if request.method=='POST':
        q=cred.objects.get(pk=request.POST['email'])
        if q.password==request.POST['pass1']:
            request.session['email']=request.POST['email']
            return HttpResponseRedirect('/codes')
        return HttpResponseRedirect("/")
    return render(request,'vc/index.html')

def codes(request):
    if request.method=='POST':
        flag=0
        q=code_info.objects.filter(code=request.POST['code'])
        if q.count()==0:
            return HttpResponseRedirect('/codes')
        q=q[0]
        for data in q.email:
            if data==request.session['email']:
                flag=1
                request.session['code']=request.POST['code']
        if flag==1:
            return HttpResponseRedirect('/edit')
    return render(request,'vc/codes.html')

def createcode(request):
    if request.method=='POST':
        q=code_info.objects.filter(code=request.POST['code2'])
        if q.count()==0:
            q=code_info(code=request.POST['code2'], email=[])
            q.email.append(request.session['email'])
            q.save()
    return HttpResponseRedirect("/codes")

def share(request):
    if request.method=='POST':
        flag=0
        q=code_info.objects.filter(code=request.session['code'])
        if q.count()==0:
            return HttpResponseRedirect('/share')
        q=q[0]
        ll=cred.objects.filter(email=request.POST['email'])
        if ll.count()==0 or request.session['email']!=q.email[0]:
            return HttpResponseRedirect('/share')
        for data in q.email:
            if data==request.POST['email']:
                flag=1
        if flag==0:
            q.email.append(request.POST['email'])
            q.save()
            return HttpResponseRedirect('/edit')
        else:
            return HttpResponseRedirect('/share')
    return render(request,'vc/shares.html')


def signup(request):
    if request.method=='POST':
        q=cred.objects.filter(email=request.POST['email2'])
        q.filter(password=request.POST['pass2'])
        if q.count()==0:
            q=cred(email=request.POST['email2'], password=request.POST['pass2'])
            q.save()
    return HttpResponseRedirect("/")

def rollback(request):
    if request.method=='POST':
        newh=int(request.POST['head'])
        head=headt.objects.get(pk=request.session['code'])
        head.head=min(head.nextcommit-1,newh)
        head.save()
        return HttpResponseRedirect("/edit")
    else:
        ll=headt.objects.get(pk=request.session['code'])
        head=ll.head
        arr=[]
        for i in range(ll.nextcommit-1,0,-1):
            eml=commit_info.objects.get(pk=request.session['code'])
            eml=eml.commit_email[i]
            temp={}
            temp['id']=i
            temp['email']=eml
            temp['text']=get_text(request.session['code'],i)
            arr.append(temp)
        return render(request,'vc/roll.html',{'arr':arr,'email':request.session['email'],'code':request.session['code']})

def makechng(m1,a,var):
    stra=""
    j=0
    i=0
    if m1[0]==0:
        stra="Modified:."
    elif m1[0]==1:
        if var==1:
            stra="Added:>>>>"
        else:
            stra="Removed:>>"
    else:
        stra="Same:>>>>>"
    while i<len(a):
        if a[i:i+2]=="\r\n":
            stra+="\r\n"
            i+=1
            if i==len(a) or a[i:]=="\r\n" or a[i:]=="\n" or a[i:]=="\r":
                break
            j+=1
            if i<len(a) and j<len(m1) and m1[j]==0:
                stra+="Modified:."
            elif i<len(a)  and j<len(m1) and m1[j]==1:
                if var==1:
                    stra+="Added:>>>>"
                else:
                    stra+="Removed>>>"
            elif  i<len(a) and j<len(m1):
                stra+="Same:>>>>>"
        else:
            stra+=a[i]
        i+=1
    return stra
    
def comp(request):
    if request.method=='POST':
        a=int(request.POST['one'])
        b=int(request.POST['two'])
        a=get_text(request.session['code'],a)
        b=get_text(request.session['code'],b)
        dic= lcs(a,b)
        m1=dic[0]
        m2=dic[1]
        #return HttpResponse(m1)
        stra=a
        strb=b
        stra=makechng(m1,a,1)
        strb=makechng(m2,b,0)
        return render(request,'vc/showside.html',{'m1':stra,'m2':strb,'c1':request.POST['one'],'c2':request.POST['two']})
    else:
        ll=headt.objects.get(pk=request.session['code'])
        head=ll.head
        arr=[]
        for i in range(ll.nextcommit-1,0,-1):
            eml=commit_info.objects.get(pk=request.session['code'])
            eml=eml.commit_email[i]
            temp={}
            temp['id']=i
            temp['email']=eml
            temp['text']=get_text(request.session['code'],i)
            arr.append(temp)
        return render(request,'vc/compare.html',{'arr':arr,'email':request.session['email'],'code':request.session['code']})


def lcs(a,b):
    dp=[[0 for i in range(len(b)+1)] for j in range(len(a)+1)]
    resa=[0]*len(a)
    resb=[0]*len(b)
    for i in range(1,len(a)+1):
        for j in range(1,len(b)+1):
            dp[i][j]=max(dp[i-1][j],dp[i][j-1])
            if a[i-1]==b[j-1]:
                dp[i][j]=max(dp[i][j],dp[i-1][j-1]+1)
    ans=""
    i=len(a)
    j=len(b)
    while dp[i][j]!=0:
        if i>=0 and j>=0 and dp[i][j]>dp[i-1][j] and dp[i][j]!=dp[i][j-1]:
            resa[i-1]=1
            ans+=a[i-1]
            resb[j-1]=1
            i-=1
            j-=1
        if i>=0 and dp[i][j]==dp[i-1][j]:
            i-=1
        if j>=0 and dp[i][j]==dp[i][j-1]:
            j-=1
    ans=ans[::-1]
    
    
    modifyA=[]
    modifyB=[]
    linea=1
    lineb=1
    counta=countb=0
    i=0
    j=0
    # 0 changed
    # 1 removed / added
    # 2 same
    c1=c2=matcha=matchb=0
    dica=[0 for i in range(len(a))]
    dicb=[0 for i in range(len(b))]
    cna=[0 for i in range(len(a))]
    cnb=[0 for i in range(len(b))]
    
    while i<len(a) or j<len(b):
        while i<len(a) and j<len(b) and a[i:i+2]!="\r\n" and b[j:j+2]!="\r\n":
            if(cna[i]==0):
                counta+=1
            cna[i]=1
            if(cnb[j]==0):
                countb+=1
            cnb[j]=1
            if(resa[i]==1 and resb[j]==1):
                matcha+=1
                matchb+=1
                if(dica[i]==0):
                    c1+=1
                dica[i]=1
                if(dicb[j]==0):
                    c2+=1
                dicb[j]=1
                i+=1
                j+=1
            elif(resa[i]==0 and resb[j]==0):
                i+=1
                j+=1
            elif(resb[j]==0):
                j+=1
                if(dica[i]==0):
                    c1+=1
                dica[i]=1
            elif(resa[i]==0):
                i+=1
                if(dicb[j]==0):
                    c2+=1
                dicb[j]=1
        flag=1
        if counta==countb and c1==c2 and counta==c1 and linea==1 and lineb==1:
            if  i==len(a) and j==len(b) :
                flag=0
            if i==len(a) and  b[j:j+2]=="\r\n":
                flag=0
            if j==len(b) and  a[i:i+2]=="\r\n":
                flag=0
            if a[i:i+2]=="\r\n" and b[j:j+2]=="\r\n":
                flag=0
            if flag ==0:
                modifyB.append(2) #same
                modifyA.append(2) #same
                flag=0
        if c1==0:
            if i==len(a) or a[i:i+2]=="\r\n":
                modifyA.append(1) #add
        if c2==0:
            if j==len(b) or b[j:j+2]=="\r\n":
                modifyB.append(1) #remove
        if c1>0 and flag==1 and a[i:i+2]=="\r\n":
                modifyA.append(0) #change
        if c2>0 and flag==1 and b[j:j+2]=="\r\n":
                modifyB.append(0) #change    
        if i<len(a) and a[i:i+2]=="\r\n":
            i+=2 
            c1=0
            linea=1
            matcha=0
            counta=0
        elif matcha>0:
            linea+=1
        if j<len(b) and b[j:j+2]=="\r\n":
            j+=2
            c2=0
            lineb=1
            countb=0
            matchb=0
        elif matchb>0:
            lineb+=1
        if i==len(a):
            while j<len(b):
                if b[j:j+2]=="\r\n":
                    modifyB.append(1) #remove
                j+=1
            modifyB.append(1) #remove
        if j==len(b):
            while i<len(a):
                if a[i:i+2]=="\r\n":
                    modifyA.append(1) #adds
                i+=1
            modifyA.append(1) #add
    dict={0:modifyA,1:modifyB,3:resa,4:resb}
    return dict
    
#lcs("abc\r\ndefgh\r\nijklmnopq\r\nrstuvw\r\nxyz","abc\r\ndefgh\r\nhrs\r\nstuv\r\nabcdefgh")
                   