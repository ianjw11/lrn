from bdd.helpers import *
from sqldb.models import Tn,Block
import csv
from django.core.management.base import BaseCommand, CommandError
import multiprocessing
from multiprocessing import Process, Value, Lock
import math,datetime
from django.db import transaction
import subprocess
import os
from multiprocessing import Process

class Command(BaseCommand):
  regions = ["ma","mw","ne","se","sw","wc","we"]
  path = "/opt/lrn/"
  SvFields = ["ID-ignore","TN","LRN","SPID","ActivationTS","CLASS_DPC","CLASS_SSN","LIDB_DPC",
       "LIDB_SSN","ISVM_DPC","ISVM_SSN","CNAM_DPC","CNAM_SSN","EndUserLocation",
       "EndUserLocationType","BillingId","LNPType","DownloadReason","WSMSC_DPC",
       "WSMSC_SSN","SVType","ALTSPID","VOICEURI","MMSURI","POCURI"," PRESURI",
       "SMSURI","ALTEULV","ALTEULT","ALTBID","Last Alt SPID","SPCustom 1",
       "SPCustom 2","SPCustom 3"]
  BddFields = ["ID-ignore","NPA_NXX_X","LRN","SPID","ActivationTS","CLASS_DPC","CLASS_SSN",
       "LIDB_DPC","LIDB_SSN"," ISVM_DPC","ISVN_SSN","CNAM_DPC","CNAM_SSN",
       "WSMSC_DPC","WSMSC_SSN","DownloadReason","SVTYPE","ALTSPID","VOICEURI",
       "MMSURI"," POCURI","PRESURI","SMSURI","ALTEULV","ALTEULT","ALTBID","Last",
       "Alt SPID","SPCustom 1","SPCustom 2","SPCustom 3"]

  def handle(self, *args, **options):
    args = 'sv or block'
    help = 'import sv or block data to sql'
    self.procs=[]
    self.generatepaths()
    self.txnid=195114
    self.run()
  def startgz(self,svfile,region,pipefile):
    print("starting zcat")
    subprocess.call(["mkfifo",pipefile]) # makes pipe
    self.svpipes[region] = subprocess.call('zcat ' + svfile + ' > ' + pipefile,shell=True)
    
  def generatepaths(self,path=path):
    self.svpipes = {}
    self.svfiles = {}
    self.blockfiles = {}
    for region in self.regions:
      filelist = [self.path + region + "/" + filename for filename in listdir(self.path + region)] # get fully qualified paths to files
      svfile = next(x for x in filelist if "sv_BDD" in x)
      
      if svfile.split(".")[-1]=="gz": # if we have a gz file create pipes
        
        pipefile = svfile[:-3] + ".pipe"
        print("running mkfifo ")
        
        
        p = multiprocessing.Process(target=self.startgz,args=(svfile,region,pipefile))
        self.procs.append(p)
        p.start()
        #self.svpipes[region] = subprocess.Popen(['zcat',svfile],stdout=open(pipefile,"wb")) # spawn proccess to zcat file to pipe
        #self.svpipes[region] = subprocess.Popen("zcat " + svfile + " > " + pipefile,shell=True)
        self.svfiles[region] = pipefile # set imported file to pipe
      else:
        self.svfiles[region] = svfile
      
      self.blockfiles[region] = next(x for x in filelist if "block_BDD" in x)
  
  def mksvfields(self):
    names = [f.name for f in Tn._meta.fields]
    self.svfields = [field if field in names else "@dummy" for field in self.SvFields ] # generate list of fields for csv import
  def mkblockfields(self):
    names = [f.name for f in Block._meta.fields]
    self.blockfields = [field if field in names else "@dummy" for field in self.BddFields ] # generate list of fields for csv import
  
 
  def run(self,table="sv"):
    self.queries = []
    #try:
    if table == "sv":
      self.mksvfields()
      for region,filename in self.svfiles.iteritems():
        sqlcmd = self.generatesql(self.svfields,"SUBSCRIPTIONVERSION",filename,region)
        print "starting query " + sqlcmd
        print subprocess.call(sqlcmd,shell=True)
        
    #[p.wait() for p in self.queries]
    #except:
      #[p.kill for p in self.svpipes.values()]
  
  def generatesql(self,fields,table,filename,regionid):
    fieldstext = ",".join(fields)
    sql = """mysql -e "load data local infile '{filename}' into table {table} fields terminated by '|' enclosed by '' lines terminated by '\\n'
    ({fields}) SET TXN_ID={txnid}, RegionId='{regionid}' ;" -u{user} -p{passwd} {db}
    
    """.format(filename=filename,table=table,
               fields=fieldstext,txnid=self.txnid,regionid=regionid,
               user="ian",passwd="LNP-dev",db="lnp_new"
               )
    return sql
    
    
    
