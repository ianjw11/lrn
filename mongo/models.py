from mongoengine import *
from mongoengine import fields

connect("LNP_new",host="localhost")

class Tn(Document):
    TN = fields.IntField(primary_key=True)
    LRN = fields.IntField()
    TXN_ID = fields.IntField()
    SVType = fields.IntField()
    SPID=fields.StringField()
    LNPType=fields.StringField()
    ActivationTimestamp = fields.DateTimeField()
    
    
class TxnId(Document):
    
    
    LAST_TXN_ID = fields.IntField()
    TXN_TIMESTAM = fields.DateTimeField()