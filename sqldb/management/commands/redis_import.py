from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sqldb.models import Tn,Block
import math
import multiprocessing
import redis
import itertools
from optparse import make_option
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            "-s", 
            "--sv", 
            dest = "sv",
            action="store_true",
            help = "load sv table", 
            metavar = ""
        ),
        make_option(
            "-b", 
            "--block", 
            dest = "block",
            action="store_true",
            help = "load block table", 
            metavar = ""
        ),
                                             )
    chunksize = 1000
    def handle(self, *args, **options):
        args = ''
        help = 'import sql tns to redis'
        
        if options['block']:
            self.doproc("block")
        elif options['sv']:
            self.doproc("sv")
            
    def doproc(self,table):
        for b in itertools.count():
            min = self.chunksize * b 
            max = self.chunksize * (b + 1)
            p = multiprocessing.Process(target=self.proc,args=(min,max,table))
            p.start()
            p.join()
           
    def proc(self,min,max,table):
        if table=="sv":
            obj = Tn
            field = "TN"
        elif table=="block":
            obj = Block
            field = "NPANXXX"
        else:
            raise("no table specified")
        print(" with min pk " + str(min))
        r = redis.Redis("localhost")
        qs = obj.objects.filter(pk__gte=min,pk__lte=max).only(field,"LRN").order_by('pk')
        p = r.pipeline(transaction=False)
        for row in qs:
            p.set(getattr(row,field),row.LRN)
        p.execute()
        
   
        
        
        
        
        