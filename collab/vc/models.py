from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class cred(models.Model):
    email=models.CharField(max_length=50, null=False)
    invcode=models.CharField(max_length=50, null=False)

class commit_table(models.Model):
    code=models.CharField(max_length=50 , null=False)
    email=models.CharField(max_length=50, null=False)
    linenum=models.IntegerField()
    key = ArrayField(
        ArrayField(
            models.CharField(max_length=50, blank=True, default="null"),
            size=1000,
        ),
        size=1000,
    )
    
class sha_table(models.Model):
    sha=models.CharField(max_length=50 , primary_key=True)
    string=models.TextField(null=False)

class headt(models.Model):
    code=models.CharField(max_length=50, primary_key=True)
    head=models.IntegerField(null=False)
    nextcommit=models.IntegerField(null=False)
