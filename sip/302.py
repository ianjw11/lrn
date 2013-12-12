#!/usr/bin/env python
from twisted.internet import reactor
from twisted.python import log
from twisted.protocols import sip
from twisted.internet.protocol import ServerFactory
from twisted.application import internet, service
from pprint import pprint
import txredisapi as redis 
from twisted.internet import defer
import re
myIP = '199.19.120.51'
# port to bind this redirect server to
myport = 5060

UserAgent = "amazingness"

class SipProxy(sip.Proxy):

    def connect(self):
        self.pool = redis.lazyConnectionPool(host="localhost",port=6379,poolsize=5,reconnect=True)
        #print self.pool
        #l = yield self.pool.get("14124173907")
        #print l
    def __init__(self):
        self.connect()
        self.findtn = re.compile('(?<=sip:)(.*?)(?=@)')
        sip.Proxy.__init__(self, host=myIP, port=myport) 
        
    # generate a SIP redirection response to every SIP request and send it to the originator of the request 
    
    @defer.inlineCallbacks
    def handle_request(self, message, addr):
        if message.method not in  ['INVITE']:return
        #print("to header :")
        #print sip.parseAddress(message.headers)
        
        """
        To = message.headers["to"][0] # get "to" line
        at = To.find("@")  # get position of @ sign, or -1 if no @
        start = To.find("sip:") + 4 # position of to header to start parsing at
        if at != -1: TN = To[start:at]
        else: TN = To[start:]
        """
        TN = self.findtn.search(message.headers["to"][0]).group(1) # use regex to pull out number
        #print ("\n TN IS: " + str(TN))
        """ Yielding the redis results should allow the reactor to continue processing other 
        requests while waiting for response
        """
        if len(TN) == 11: LRN = yield self.pool.get(TN[1:]) 
        else: LRN = yield self.pool.get(TN)
        r = self.responseFromRequest(302, message)
        r.addHeader("Contact", "<sip:" + str(TN) + ";rn=+1" + str(LRN) + ">")
        r.addHeader("User-Agent",UserAgent)
        r.creationFinished()
        self.deliverResponse(r)
        

# wrapper factory for our SipProxy
class sipfactory(ServerFactory):
    protocol = SipProxy

reactor.listenUDP(myport, SipProxy())
reactor.run()
