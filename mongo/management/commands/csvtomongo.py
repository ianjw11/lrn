from django.core.management.base import BaseCommand, CommandError
# from app.database.models import Subscriptionversion
from mongo.models import Tn,TxnId
import csv
import multiprocessing
from multiprocessing import Process, Value, Lock
import math

from os import listdir
from os.path import isfile, join


class Command(BaseCommand):
    args = ''
    help = 'import jobs to mongo'
    csvfile = "/opt/app/lnp/100.bdd"
    path = "/opt/app/lnp/files/"
  

    def Parse(self, f=""):
        c = csv.reader(open(f), delimiter="|")
        for row in c:
            try:
                Tn(TN=row[1], LRN=row[2]).save()
            except:
                print "\n failed for "
                print row
        
    def handle(self, *args, **options):
        
        self.procs = []
       
        
        for f in listdir(self.path):
            filepath = self.path + str(f)
            p = multiprocessing.Process(
                target=self.Parse,
                kwargs={'f':filepath})
            self.procs.append(p)
            p.start()
        
        for p in self.procs:
            p.join()

        
        
