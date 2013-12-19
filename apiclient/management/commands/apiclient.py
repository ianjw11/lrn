from suds.client import Client
import logging
from sqldb.models import Tn,Block,LastTxn
from django.db import transaction
from django.db.models import Max
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from pprint import pprint
from os import listdir
from pprint import pprint
class Command(BaseCommand):
    args = 'specify "sv" to also import sv data'
    help = 'import sv and block data into sql db. '
    option_list = BaseCommand.option_list + (
        make_option(
            "-b", 
            "--batch", 
            dest = "batchsize",
            help = "specify the batchsize", 
            metavar = "1000"
        ),
                                             )
    batchsize=20000
    def handle(self, *args, **options):
        if options['batchsize'] !=None:
            self.batchsize=options['batchsize']
        w = Wsdl()
        w.maxrecords = self.batchsize
        w.send()

class Wsdl(object):
    url = "https://156.154.17.82/sipix_si_lnp/services/LNPDownload"
    #LAST_TXN=195114 # defaults for testing
    
    Context="test"
    maxrecords=20000
    fields = ["LRN","SVType","SPID","LNPType","ActivationTS"]
    blockfields = ["LRN","SVType","SPID","ActivationTS"]
 
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
                if 'CreateSV' in event:
                    dataelem=event.CreateSV # contains the fields we want
                    record, created = Tn.objects.get_or_create(TN=dataelem.TN)
                elif 'UpdateSV' in event:
                    dataelem=event.UpdateSV
                    record,created = Tn.objects.get_or_create(TN=dataelem.TN)
                record.TxnId=event.TransactionID # set record txnid to xml request txnid
                for field in self.fields: # loop through fields
                    try:
                        value = getattr(dataelem,field) # get field from event xml obj
                        setattr(record,field,value) # set  object to val
                    except:
                        print "\n failed for field " + str(field) + "\n"
                        print(dataelem)
                        print(record)
                record.save()
          
            
            elif 'DeleteBlock' in event:
                Block.objects.filter(NPANXXX=event.DeleteBlock.NPANXXX).delete()
                
            elif any(x in event for x in ['UpdateBlock','CreateBlock']):
                if 'CreateBlock' in event:
                    dataelem=event.CreateBlock # contains the fields we want
                    record, created = Block.objects.get_or_create(NPANXXX=dataelem.NPANXXX)
                elif 'UpdateBlock' in event:
                    dataelem=event.UpdateBlock
                    record,created = Block.objects.get_or_create(NPANXXX=dataelem.NPANXXX)
                record.TxnId=event.TransactionID # set record txnid to xml request txnid
                for field in self.blockfields: # loop through fields
                    try:
                        value = getattr(dataelem,field) # get field from event xml obj
                        setattr(record,field,value) # set  object to val
                    except:
                        print "\n failed for field " + str(field) + "\n"
                        print(dataelem)
                        print(record)
                record.save()
          



