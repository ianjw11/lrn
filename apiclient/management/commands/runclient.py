from suds.client import Client
import logging
import time
from apiclient.api import ApiClient
from sqldb.models import Tn,Block,LastTxn
from django.db import transaction
from django.db.models import Max
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from pprint import pprint
from os import listdir
from pprint import pprint
class Command(BaseCommand):
    args = ''
    help = 'run api client interactively'
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
        print "starting"
        api = ApiClient()
        api.maxrecords = self.batchsize
        while True:
            try:
                print "starting loop"
                api.send()
                print "sleeping for 200 seconds"
                time.sleep(200)
            except Exception, err:
                print "error" + str(err) + " occured, sleeping .... "
                time.sleep(100)
                continue
            

