from mongoengine import *
from django.db import models


connect("LNP_new",host="localhost")


class Tn(models.Model):
    TN = models.IntegerField(primary_key=True)
    LRN = models.IntegerField()
    TXN_ID = models.IntegerField()
    SVType = models.IntegerField()
    SPID=models.CharField()
    LNPType=models.CharField()
    ActivationTimestamp = models.DateTimeField()

    
class LastTxn(models.Model):
    LAST_TXN_ID = models.IntegerField()
    TXN_TIMESTAMP = models.DateTimeField()