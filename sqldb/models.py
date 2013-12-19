from django.contrib import admin
from django.db import models


class FixedCharField(models.Field):
    def __init__(self, max_length, *args, **kwargs):
        self.max_length = max_length
        super(FixedCharField, self).__init__(max_length=max_length, *args, **kwargs)
    def db_type(self):
        return 'char(%s)' % self.max_length


class Tn(models.Model):
    ID = models.AutoField(primary_key=True)
    TN = models.BigIntegerField()
    LRN = models.BigIntegerField()
    SVType = models.PositiveSmallIntegerField(default=0)
    SPID=FixedCharField(max_length=5)
    LNPType=FixedCharField(max_length=5)
    #ActivationTS = models.DateField()
    ActivationTimestamp = models.DateTimeField(db_column="ActivationTS")
    TxnId = models.BigIntegerField(db_column="TXN_ID") # set default to TX id of BDD dumps
    RegionId = FixedCharField(max_length=2)
    class Meta:
        db_table = 'SUBSCRIPTIONVERSION'
    
class Block(models.Model):
    ID = models.AutoField(primary_key=True)
    NPANXXX = models.BigIntegerField(db_column="NPA_NXX_X")
    LRN = models.BigIntegerField(null=True)
    SVType = models.IntegerField(null=True)
    SPID=models.CharField(max_length=25)
    #LNPType=models.CharField(max_length=25)
    ActivationTimestamp = models.DateField(db_column="ActivationTS")
    #ActivationTimestamp = models.DateTimeField(db_column="ActivationTS")
    TxnId = models.BigIntegerField(db_column="TXN_ID") # set default to TX id of BDD dumps
    RegionId = models.CharField(max_length=3,default="")
    class Meta:
        db_table = 'NUMBERPOOLBLOCK'
class LastTxn(models.Model):
    LAST_TXN_ID = models.BigIntegerField(primary_key=True)
    TXN_TIMESTAMP = models.DateField(auto_now_add=True)
    class Meta:
        db_table = 'LAST_TXN'
    

admin.site.register(LastTxn)
admin.site.register(Tn)
admin.site.register(Block)
