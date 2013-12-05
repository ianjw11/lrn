from suds.client import Client
import logging
from mongo.models import Tn,TxnId
from mongoengine import connect
connect("LNP_new",host="localhost")



class Wsdl(object):
    url = "https://156.154.17.82/sipix_si_lnp/services/LNPDownload"
    maxrecords=10000
    LAST_TXN=195114
    Context="test"
    nosql = True
    fields = ["LRN","SVType","SPID","LNPType","ActivationTimestamp"]
 
    def __init__(self,**kwargs):
        self.results=[]
        self.client = Client(self.url+"?wsdl",location=self.url)
        for k, v in kwargs.iteritems():  
            setattr(self, k, v) # set obj attributes to kwargs
    def send(self,batches=3):
        for i in xrange(batches):
            result = self.client.service.LNPDownload(Context=self.Context,# execute remote RPC call to pull down events
                                                     LastTransactionID=self.LAST_TXN,MaxNumberOfRecords=self.maxrecords) 
            self.LAST_TXN=result.NextTransactionID
            self.proc(result.LNPData)
            self.results.extend(result.LNPData) # add on events to results list

    def proc(self,events):
        for event in events:
            if 'DeleteSV' in event:
                try:
                    if self.nosql:
                        Tn.objects.get(TN=event.DeleteSV.TN).delete()
                    else:
                        pass
                except:
                    print "\n number doesnt exist " + str(event.DeleteSV.TN)
            elif any(x in event for x in ['CreateSV','UpdateSV']):
                if 'CreateSV' in event:
                    dataelem=event.CreateSV # contains the fields we want
                    if self.nosql:
                        record, created = Tn.objects.get_or_create(TN=dataelem.TN)
                    else:
                        pass
                elif 'UpdateSV' in event:
                    dataelem=event.UpdateSV
                    if self.nosql:
                        
                        record,created = Tn.objects.get_or_create(TN=dataelem.TN)
                    else:
                        pass
                for field in self.fields: # loop through fields
                    try:
                        value = getattr(dataelem,field) # get field from event xml obj
                        setattr(record,field,value) # set mongo object to val
                    except:
                        print "\n failed for field " + str(field) + "\n"
                        print(dataelem)
                        print(record)
                record.save()
           
        

w = Wsdl()
w.send()




