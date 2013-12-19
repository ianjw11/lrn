from suds.client import Client
import logging
from sqldb.models import Tn,Block,LastTxn
from mongoengine import connect
from django.db import transaction
from django.db.models import Max
connect("LNP_new",host="localhost")



class Wsdl(object):
    url = "https://156.154.17.82/sipix_si_lnp/services/LNPDownload"
    LAST_TXN=195114 # defaults for testing
    
    Context="test"
    maxrecords=20000
    fields = ["LRN","SVType","SPID","LNPType","ActivationTS"]
 
    def __init__(self,**kwargs):
        self.results=[]
        self.client = Client(self.url+"?wsdl",location=self.url)
        for k, v in kwargs.iteritems():  
            setattr(self, k, v) # set obj attributes to kwargs
        try:
            self.LAST_TXN = LastTxn.objects.all().aggregate(Max('LAST_TXN_ID'))['LAST_TXN_ID__max']
        except:
            print "error unable to get last transaction ID"
            raise Exception('TXN_ID')
          
    @transaction.commit_manually
    def send(self):
        while True:
            result = self.client.service.LNPDownload(Context=self.Context,# execute remote RPC call to pull down events
                                                     LastTransactionID=self.LAST_TXN,MaxNumberOfRecords=self.maxrecords) 
            if result.NextTransactionID == self.LAST_TXN:
                print "No new transactions to process"
                break
            # add on events to results list
            try:
                self.proc(result.LNPData)
                self.results.extend(result.LNPData)
                LastTxn(LAST_TXN_ID=result.NextTransactionID).save()
                self.LAST_TXN=result.NextTransactionID
            except:
                transaction.rollback()
                break
            else:
                transaction.commit()

             

    def proc(self,events):
        for event in events:
            if 'DeleteSV' in event:
                try:
                    Tn.objects.filter(TN=event.DeleteSV.TN).delete()
                except:
                    print "\n number doesnt exist " + str(event.DeleteSV.TN)
            elif any(x in event for x in ['CreateSV','UpdateSV']):
                if 'CreateSV' in event:
                    dataelem=event.CreateSV # contains the fields we want
                    record, created = Tn.objects.get_or_create(TN=dataelem.TN)
                elif 'UpdateSV' in event:
                    dataelem=event.UpdateSV
                    record,created = Tn.objects.get_or_create(TN=dataelem.TN)
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




