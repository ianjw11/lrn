from mongoengine import *
from django.db import models


connect("LNP_new",host="localhost")


class Tn(models.Model):
    TN = models.IntegerField(primary_key=True)
    LRN = models.IntegerField()
    #TXN_ID = models.IntegerField()
    SVType = models.IntegerField()
    SPID=models.CharField(max_length=25)
    LNPType=models.CharField(max_length=25)
    ActivationTS = models.DateTimeField()
    #ActivationTimestamp = models.DateTimeField()
    class Meta:
        db_table = 'SUBSCRIPTIONVERSION'
    
class LastTxn(models.Model):
    LAST_TXN_ID = models.IntegerField()
    TXN_TIMESTAMP = models.DateTimeField()
    
    
from django.contrib import admin
admin.site.register(LastTxn)
admin.site.register(Tn)
