from django.contrib import admin
from django.db import models


class FixedCharField(models.Field):
    def __init__(self, max_length, *args, **kwargs):
        self.max_length = max_length
        super(FixedCharField, self).__init__(max_length=max_length, *args, **kwargs)
    def db_type(self,**kwargs):
        return 'char(%s)' % self.max_length
class TinyIntField(models.Field):
    def __init__(self, *args, **kwargs):
        super(TinyIntField, self).__init__( *args, **kwargs)
    def db_type(self,**kwargs):
        return 'tinyint(3)' 


class Tn(models.Model):
    ID = models.AutoField(primary_key=True)
    TN = models.BigIntegerField(unique=True,db_index=True)
    LRN = models.BigIntegerField()
    SVType = TinyIntField()
    SPID=FixedCharField(max_length=4)
    LNPType=FixedCharField(max_length=5)
    ActivationTimestamp = models.DateTimeField()#db_column="ActivationTS")
    TxnId = models.BigIntegerField(db_column="TXN_ID",db_index=True) # set default to TX id of BDD dumps
    RegionId = FixedCharField(max_length=2,default="")
    class Meta:
        db_table = 'SUBSCRIPTIONVERSION'
    
class Block(models.Model):
    ID = models.AutoField(primary_key=True)
    NPANXXX = models.BigIntegerField(db_index=True,unique=True)#,db_column="NPA_NXX_X")
    LRN = models.BigIntegerField()
    #SVType = models.PositiveSmallIntegerField(default=0,null=True)
    SVType = TinyIntField()
    SPID= FixedCharField(max_length=4)
    ActivationTimestamp = models.DateTimeField()#db_column="ActivationTS")
    TxnId = models.BigIntegerField(db_column="TXN_ID",db_index=True) # set default to TX id of BDD dumps
    RegionId = FixedCharField(max_length=2,default="")
    class Meta:
        db_table = 'NUMBERPOOLBLOCK'
class LastTxn(models.Model):
    LAST_TXN_ID = models.BigIntegerField(primary_key=True)
    TXN_TIMESTAMP = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'LAST_TXN'
    

admin.site.register(LastTxn)
admin.site.register(Tn)
admin.site.register(Block)
