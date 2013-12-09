from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sqldb.models import Tn
import math
import multiprocessing
import redis



def QsIt(queryset,pk,r,chunksize=10000):
    print("\n at pk # " + str(pk))
    p = r.pipeline(transaction=False)
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            p.set(row.TN,row.LRN)
            #yield row
    p.execute()


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        args = ''
        help = 'import sql tns to redis'
        self.count=Tn.objects.count()
        procs = []
        #self.theads = 4
        threads = 216957344 # speed up for now
        chunksize = int(math.ceil(self.count) / float(threads))
        for i in range(threads):
            min = chunksize * i
            max = chunksize * (i + 1)
            qs = Tn.objects.filter(pk__gt=min,pk_lte=max).only("TN","LRN")
            p = multiprocessing.Process(target=self.proc,args=(qs,min,i,))
            procs.append(p)
            p.start()
        for p in procs:
            p.join()
            
    def proc(self,qs,minpk,i):
        print(" \n thread # " + str(i) + " with min pk " + str(minpk))
        r = redis.Redis("localhost")
        QsIt(qs,minpk,r) # execute redis pipelines in chunks 
            
        
        
        
        
        