from bdd.helpers import *
from sqldb.models import Tn
import csv
from django.core.management.base import BaseCommand, CommandError
import multiprocessing
from multiprocessing import Process, Value, Lock
import math,datetime


class Command(BaseCommand):
    args = 'sv or block'
    help = 'import sv or block data to sql'

    def handle(self, *args, **options):
      reader = Readers()
      reader.proccess()



class Readers(object):
  
  SvFields = ["ID","TN","LRN","SPID","ActivationTS","CLASS_DPC","CLASS_SSN","LIDB_DPC",
       "LIDB_SSN","ISVM_DPC","ISVM_SSN","CNAM_DPC","CNAM_SSN","EndUserLocation",
       "EndUserLocationType","BillingId","LNPType","DownloadReason","WSMSC_DPC",
       "WSMSC_SSN","SVType","ALTSPID","VOICEURI","MMSURI","POCURI"," PRESURI",
       "SMSURI","ALTEULV","ALTEULT","ALTBID","Last Alt SPID","SPCustom 1",
       "SPCustom 2","SPCustom 3"]
  
  def __init__(self):
    """ set up file handles and create csvreader objects"""
    self.f = files()
    self.f.sv() 
    self.f.block()
    self.readers()
    
  def readers(self):
    "generates iteratable dictreaders for all file handles"
    self.svreaders = [csv.DictReader(f, fieldnames=self.SvFields,delimiter="|") for f in self.f.svhandles] 
    #self.bddreaders = [csv.DictReader(f, fieldnames=self.BddFields,delimiter="|") for f in self.f.blockhandles]
    
    
  def parsesv(self,reader,counter,thread):
    batch=[]
    count=0
    for record in reader:
      #create date obj with format year,month,day
      ts = datetime.datetime(int(record["ActivationTS"][:4]),int(record["ActivationTS"][4:6]),int(record["ActivationTS"][6:8]))
      
      #ensure primary keys dont collide on bulk insert
      ID = int(counter.val) + 1 + int(thread)
      t = Tn(ID=ID,TN=record["TN"],LRN=record["LRN"],SVType=record["SVType"],
         SPID=record["SPID"],LNPType=record["LNPType"],ActivationTS=ts)
      counter.increment()
      if len(batch) <= 5000:
        batch.append(t)
      else:
        Tn.objects.bulk_create(batch)
        batch = []
        count+=5000
        print(str(count) + "\n")
        
        
        
  def proccess(self,Type="sv"):
    self.procs = []
    counter = Counter()
    for idx,reader in enumerate(self.svreaders):
        p = multiprocessing.Process(target=self.parsesv,args=(reader,counter,idx))
        self.procs.append(p)
        p.start()
    
    for p in self.procs:
        p.join()
        
class Counter(object):
    def __init__(self):
        self.val = Value('i',0)
        self.lock = Lock()
    def increment(self):
        with self.lock:
            self.val.value += 1
    def value(self):
        with self.lock:
            return self.val.value
        
        