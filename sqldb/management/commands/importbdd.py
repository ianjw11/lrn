from sqldb.models import Tn,Block,LastTxn
import csv
from django.core.management.base import BaseCommand, CommandError
import multiprocessing
from multiprocessing import Process, Value, Lock
import math,datetime
from django.db import transaction
from django import db
import subprocess
import os
from multiprocessing import Process
from optparse import make_option
from pprint import pprint
from os import listdir
import time
class Command(BaseCommand):
    regions = ["ma","mw","ne","se","sw","wc","we"]
    path = "/opt/lrn/"
    db = db.settings.DATABASES['default']['NAME']
    SvFields = ["ID-ignore","TN","LRN","SPID","ActivationTS","CLASS_DPC","CLASS_SSN","LIDB_DPC",
         "LIDB_SSN","ISVM_DPC","ISVM_SSN","CNAM_DPC","CNAM_SSN","EndUserLocation",
         "EndUserLocationType","BillingId","LNPType","DownloadReason","WSMSC_DPC",
         "WSMSC_SSN","SVType","ALTSPID","VOICEURI","MMSURI","POCURI"," PRESURI",
         "SMSURI","ALTEULV","ALTEULT","ALTBID","Last Alt SPID","SPCustom 1",
         "SPCustom 2","SPCustom 3"]
    BddFields = ["ID-ignore","NPANXXX","LRN","SPID","ActivationTimestamp","CLASS_DPC","CLASS_SSN",
         "LIDB_DPC","LIDB_SSN"," ISVM_DPC","ISVN_SSN","CNAM_DPC","CNAM_SSN",
         "WSMSC_DPC","WSMSC_SSN","DownloadReason","SVType","ALTSPID","VOICEURI",
         "MMSURI"," POCURI","PRESURI","SMSURI","ALTEULV","ALTEULT","ALTBID","Last",
         "Alt SPID","SPCustom 1","SPCustom 2","SPCustom 3"]
    args = 'specify "sv" to also import sv data'
    help = 'import sv and block data into sql db. '
    option_list = BaseCommand.option_list + (
        make_option(
            "-t", 
            "--txnid", 
            dest = "txnid",
            help = "specify last transactionid", 
            metavar = "TXN_ID"
        ),
        make_option(
            "-d", 
            "--database", 
            dest = "db",
            help = "specify last database name(optional)", 
            metavar = "DB"
        ),
        make_option(
            "-b", 
            "--bdd", 
            dest = "path",
            help = "specify path to extracted bdd file tree(the directory with ma, mw, etc...", 
            metavar = "/path/to/extracted/bdds"
        ),
        make_option(
            "-s", 
            "--sv", 
            dest = "sv",
            action="store_true",
            help = "specify if you want to load sv bdd files as well as block", 
            metavar = ""
        ),
    )

    def handle(self, *args, **options):
        print self.db
        #check and parse all options first
        if options['txnid'] == None :
                raise CommandError("Option '--txn=...' is required.") # exit if no txn_id specified....we need this
        else:
            self.txnid = options['txnid']
        
        if options['db'] == None:
            print """ no database specified, using {default}
             note:  if not using default Database specified in settings.py({default}), you must create the table schema manually in sql
             """.format(default=self.db)
        else:
            self.db=options['db']
            
        if options['path'] == None:
            print "no path specified using default of " + self.path
        else:
            self.path=options['path']
        
        self.procs=[]
        self.sv = False # flag to create handles for SV files if enabled SV files will have special pipes created so they can be read as GZ
        #if "sv" in args:
        #    sv = True
        if options['sv'] != None:
            self.sv = True
        self.generatepaths()
        self.run() 
    def startgz(self,svfile,region,pipefile):
        
        print("starting zcat")
        subprocess.call(["mkfifo",pipefile]) # makes pipe
        
        self.svpipes[region] = subprocess.call("zcat " + svfile + " > " + pipefile,shell=True)
        
    def generatepaths(self,path=path):
        self.svpipes = {}
        self.svfiles = {}
        self.blockfiles = {}
        for region in self.regions:
            filelist = [self.path + region + "/" + filename for filename in listdir(self.path + region)] # get fully qualified paths to files
            if self.sv:
                svfile = next(x for x in filelist if "sv_BDD" in x and "pipe" not in x)
                print svfile
                if svfile.split(".")[-1]=="gz": # if we have a gz file create pipes
                    pipefile = svfile[:-3] + ".pipe"
                    print("running mkfifo for " + pipefile)
                    #self.startgz(svfile,region,pipefile)
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

    def run(self):
        self.queries = []
        if self.sv:
            time.sleep(3)
            pprint(self.svfiles)
            self.mksvfields()
            for region,filename in self.svfiles.iteritems():
                sqlcmd = self.generatesql(self.svfields,Tn._meta.db_table,filename,region)
                print "starting query " + sqlcmd
                print subprocess.call(sqlcmd,shell=True)
        
        pprint(self.blockfiles)
        self.mkblockfields()
        for region,filename in self.blockfiles.iteritems():
            sqlcmd = self.generatesql(self.blockfields,Block._meta.db_table,filename,region)
            print "starting query " + sqlcmd
            print subprocess.call(sqlcmd,shell=True)
        # set last txn_id properly
      
        LastTxn.objects.all().delete()
        LastTxn(LAST_TXN_ID=self.txnid).save()
    

    def generatesql(self,fields,table,filename,regionid):
        fieldstext = ",".join(fields)
        sql = """mysql -e "load data local infile '{filename}' into table {table} fields terminated by '|' enclosed by '' lines terminated by '\\n'
        ({fields}) SET TXN_ID={txnid}, RegionId='{regionid}' ;" -u{user} -p{passwd} {db}

        """.format(filename=filename,table=table,
                   fields=fieldstext,txnid=self.txnid,regionid=regionid,
                   user="ian",passwd="LNP-dev",db=self.db
                   )
        return sql
