from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sqldb.models import Tn,Block
import math
import multiprocessing
import redis
import itertools
from optparse import make_option
from django.db import connection
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
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
        make_option(
            "-c", 
            "--chunksize", 
            dest = "chunksize",
            help = "specify chunksize", 
            metavar = "10000"
        ),
                                             )
    chunksize = 200000
    def handle(self, *args, **options):
        args = ''
        help = 'import sql tns to redis'
        if options['chunksize']: self.chunksize=options['chunksize']
        if options['block']:
            self.doproc("NUMBERPOOLBLOCK")
        elif options['sv']:
            self.doproc("SUBSCRIPTIONVERSION")
            
    def doproc(self,table):
        q = multiprocessing.Queue()
        for b in itertools.count():
            min = self.chunksize * b 
            max = self.chunksize * (b + 1)
            p = multiprocessing.Process(target=self.proc,args=(min,max,table,q))
            p.start()
            p.join()
            if q.get()==0:
                print "finished!"
                break
           
    def proc(self,min,max,table,q):
        if table=="SUBSCRIPTIONVERSION":
            obj = Tn
            field = "TN"
        elif table=="NUMBERPOOLBLOCK":
            obj = Block
            field = "NPANXXX"
        else:
            raise("no table specified")
        print(" with min pk " + str(min))
        cursor = connection.cursor()
        r = redis.Redis("localhost")
        #qs = obj.objects.filter(pk__gte=min,pk__lte=max).only(field,"LRN").order_by('pk')

        query = """SELECT {field},LRN FROM {table} WHERE ID between {min} AND {max};""".format(field=field,table=table,min=min,max=max)
        cursor.execute(query)
        #results = dictfetchall(cursor)
        
        p = r.pipeline(transaction=False)
        results = cursor.fetchall()
        q.put(len(results))
        print "found " + str(len(results)) + " results"
        #for row in results:
        for row in results:
            #p.set(getattr(row,field),row.LRN)
            #p.set(row[field],row['LRN'])
            p.set(row[0],row[1])
        p.execute()
        
        
   
        
        
        
        
        