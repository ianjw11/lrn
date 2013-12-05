from mongoengine import *
from django.db import models


connect("LNP_new",host="localhost")


class Tn(models.Model):
    ID = models.IntegerField(primary_key=True)
    TN = models.IntegerField()
    LRN = models.IntegerField()
    SVType = models.IntegerField()
    SPID=models.CharField(max_length=25)
    LNPType=models.CharField(max_length=25)
    ActivationTS = models.DateField()
    #ActivationTimestamp = models.DateTimeField(db_column="ActivationTS")
    TxnId = models.IntegerField(db_column="TXN_ID",default=195114) # set default to TX id of BDD dumps
    RegionId = models.CharField(max_length=3,default="ma")
    class Meta:
        db_table = 'SUBSCRIPTIONVERSION'
    
class LastTxn(models.Model):
    LAST_TXN_ID = models.IntegerField()
    TXN_TIMESTAMP = models.DateTimeField()
    
    
from django.contrib import admin
admin.site.register(LastTxn)
admin.site.register(Tn)
