from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from sqldb.models import Tn
import math
import multiprocessing
import redis



def QsIt(queryset,pk,r,chunksize=100000):
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
        count=Tn.objects.count()
        procs = []
        threads=4
        batches = 20
        
        for e in range(batches):
            chunksize = int(math.ceil(count) / float(threads) / float(batches))
            for i in range(threads):
                min = chunksize * i
                max = chunksize * (i + 1)
                #qs = Tn.objects.filter(pk__gt=min,pk__lte=max).only("TN","LRN")
                #p = multiprocessing.Process(target=self.proc,args=(qs,min,i))
                p = multiprocessing.Process(target=self.proc,args=(min,max,i))
                procs.append(p)
                p.start()
            for p in procs:
                p.join()
            
    #def proc(self,qs,minpk,i):
    def proc(self,min,max,i):
        print(" \n thread # " + str(i) + " with min pk " + str(min))
        r = redis.Redis("localhost")
        qs = Tn.objects.filter(pk__gte=min,pk__lte=max).only("TN","LRN").order_by('pk')
        #QsIt(qs,min,r) # execute redis pipelines in chunks 
        pk = min
        #while pk < max:
        p = r.pipeline(transaction=False)
        for row in qs:#.filter(pk__gt=pk,pk__lte=max)[:50000]:
            #pk = row.pk
            p.set(row.TN,row.LRN)
            #yield row
        p.execute()
        
        
        
        
        