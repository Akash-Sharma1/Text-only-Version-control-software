from django.db import models

# Create your models here.
class commit_table(models.Model):
    cc=models.TextField()
    
class sha_table(models.Model):
    sha=models.CharField(max_length=50)
    string=models.TextField(primary_key=True)

class head_table(models.Model):
    head=models.IntegerField()
    nextcommit=models.IntegerField()
