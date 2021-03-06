from bdd.helpers import *
from sqldb.models import Tn
import csv
from django.core.management.base import BaseCommand, CommandError
import multiprocessing
from multiprocessing import Process, Value, Lock
import math,datetime
from django.db import transaction



class Command(BaseCommand):
  def handle(self, *args, **options):
    args = 'sv or block'
    help = 'import sv or block data to sql'
    f = files()
    self.svhandles = f.sv() 
    #self.f.block()
    self.readers()
    self.proccess()
  
  SvFields = ["ID","TN","LRN","SPID","ActivationTS","CLASS_DPC","CLASS_SSN","LIDB_DPC",
       "LIDB_SSN","ISVM_DPC","ISVM_SSN","CNAM_DPC","CNAM_SSN","EndUserLocation",
       "EndUserLocationType","BillingId","LNPType","DownloadReason","WSMSC_DPC",
       "WSMSC_SSN","SVType","ALTSPID","VOICEURI","MMSURI","POCURI"," PRESURI",
       "SMSURI","ALTEULV","ALTEULT","ALTBID","Last Alt SPID","SPCustom 1",
       "SPCustom 2","SPCustom 3"]
  BddFields = ["ID","NPA_NXX_X","LRN","SPID","ActivationTS","CLASS_DPC","CLASS_SSN",
       "LIDB_DPC","LIDB_SSN"," ISVM_DPC","ISVN_SSN","CNAM_DPC","CNAM_SSN",
       "WSMSC_DPC","WSMSC_SSN","DownloadReason","SVTYPE","ALTSPID","VOICEURI",
       "MMSURI"," POCURI","PRESURI","SMSURI","ALTEULV","ALTEULT","ALTBID","Last",
       "Alt SPID","SPCustom 1","SPCustom 2","SPCustom 3"]

    
    
  def readers(self):
    "generates iteratable dictreaders for all file handles"
    self.svreaders = [csv.reader(f,delimiter="|") for f in self.svhandles] 
    #self.bddreaders = [csv.DictReader(f, fieldnames=self.BddFields,delimiter="|") for f in self.f.blockhandles]
  @transaction.commit_manually
  def parsesv(self,reader):
    count=0
    for record in reader:
      #create date obj with format year,month,day
      activationts = record[self.SvFields.index("ActivationTS")]
      ts = datetime.datetime( int(activationts[:4]), int(activationts[4:6]), int(activationts[6:8]) )
      t = Tn(TN=record[self.SvFields.index("TN")],
             LRN=record[self.SvFields.index("LRN")],
             SVType=record[self.SvFields.index("SVType")],
             SPID=record[self.SvFields.index("SPID")],
             LNPType=record[self.SvFields.index("LNPType")],ActivationTS=ts)
      t.save()
      del t
      del ts
      del record
      count+=1
      if count >= 15000:
        count=0
        transaction.commit()
  def proccess(self,Type="sv"):
    self.procs = []
    for reader in self.svreaders:
        p = multiprocessing.Process(target=self.parsesv,args=(reader,))
        self.procs.append(p)
        p.start()
    
    for p in self.procs:
        p.join()
        
