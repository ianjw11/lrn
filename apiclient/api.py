from suds.client import Client
import logging
from sqldb.models import Tn,Block,LastTxn
from django.db import transaction
from django.db.models import Max
from optparse import make_option
from pprint import pprint
from os import listdir
from pprint import pprint
class ApiClient(object):
    #url = "https://156.154.17.82/sipix_si_lnp/services/LNPDownload"
    url = "https://156.154.19.197:9091/sipix_si_lnp/services/LNPDownload"
    #LAST_TXN=195114 # defaults for testing
    
    Context="test"
    maxrecords=20000
    fields = ["LRN","SVType","SPID","LNPType","ActivationTimestamp"]
    blockfields = ["LRN","SVType","SPID","ActivationTimestamp"]
    def __init__(self,**kwargs):
        self.results=[]
        print "connecting to url"
        self.client = Client(self.url+"?wsdl",location=self.url)
        
        for k, v in kwargs.iteritems():  
            setattr(self, k, v) # set obj attributes to kwargs
        try:
            self.LAST_TXN = LastTxn.objects.all().aggregate(Max('LAST_TXN_ID'))['LAST_TXN_ID__max']
            print "Last sucessful transaction id was " + str(self.LAST_TXN)
        except Exception,err:
            print "error unable to get last transaction ID"
            print str(Exception) + str(err)
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
                print "next txn id is: " + str(result.NextTransactionID)
                self.proc(result.LNPData)
                #self.results.extend(result.LNPData)
                LastTxn(LAST_TXN_ID=result.NextTransactionID).save()
                self.LAST_TXN=result.NextTransactionID
            except Exception, err:
                print Exception, err
                transaction.rollback()
                break
            else:
                transaction.commit()

             

    def proc(self,events):
        #pprint(events)
        for event in events:
            if 'DeleteSV' in event:
                try:
                    Tn.objects.filter(TN=event.DeleteSV.TN).delete()
                except:
                    print "\n number doesnt exist " + str(event.DeleteSV.TN)
            
            elif any(x in event for x in ['CreateSV','UpdateSV']):
                try:
                    if 'CreateSV' in event:
                        dataelem=event.CreateSV # contains the fields we want
                        record = Tn(TN=dataelem.TN)
           
                    elif 'UpdateSV' in event:
                    
                        dataelem=event.UpdateSV
                        record,created = Tn.objects.get_or_create(TN=dataelem.TN)
                    record.TxnId=event.TransactionID # set record txnid to xml request txnid
                    for field in self.fields: # loop through fields
                        try:
                            value = getattr(dataelem,field) # get field from event xml obj
                            if value:
                                setattr(record,field,value) # set  object to val
                        except:
                            print "\n failed for field " + str(field) + "\n"
                            print(dataelem)
                            print(record)
                    record.save()
                except Exception, err:
                    if 'CreateSV' in event:
                        t="Create"
                    elif 'UpdateSV' in event:
                        t="Update"
                    print Exception, err 
                    print " for sv method " + t
                    print(event)
                    raise
          
            
            elif 'DeleteBlock' in event:
                Block.objects.filter(NPANXXX=event.DeleteBlock.NPANXXX).delete()
                
            elif any(x in event for x in ['UpdateBlock','CreateBlock']):
                try:
                    if 'CreateBlock' in event:
                        dataelem=event.CreateBlock # contains the fields we want
                        #record, created = Block.objects.get_or_create(NPANXXX=dataelem.NPANXXX)
                        record = Block(NPANXXX=dataelem.NPANXXX)
                    elif 'UpdateBlock' in event:
                        dataelem=event.UpdateBlock
                        record,created = Block.objects.get_or_create(NPANXXX=dataelem.NPANXXX)
                    record.TxnId=event.TransactionID # set record txnid to xml request txnid
                    for field in self.blockfields: # loop through fields
                        try:
                            value = getattr(dataelem,field) # get field from event xml obj
                            if value:
                                setattr(record,field,value) # set  object to val
                        except:
                            print "\n failed for field " + str(field) + "\n"
                            print(dataelem)
                            print(record)
                    record.save()
                except Exception, err:
                    if 'CreateBlock' in event:
                        t="Create"
                    elif 'UpdateBlock' in event:
                        t="Update"
                    print Exception, err 
                    print " for block method " + t
                    print(event)
                    raise
              



