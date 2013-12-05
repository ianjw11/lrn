import gzip
from os import listdir

def gethandle(filepath):
  if filepath.split(".")[-1] == "gz":
    return gzip.open(filepath,'r')
  else:
    return open(filepath,'r')

class files(object):
  "Generate lists of file objects, supporting reading gzipped files directly"
  regions = ["ma","mw","ne","se","sw","wc","we"]
  path = "/opt/lrn/"

  def __init__(self,path=path):
    self.files = []
    for region in self.regions:
      filelist = [self.path + region + "/" + filename for filename in listdir(self.path + region)] # get fully qualified paths to files
      self.files.extend(filelist) # create flat list of all bdd files
      
  def sv(self):
    """ get list of filehandles for sv bdd files"""
    self.svhandles = []
    for filepath in self.files:
      if "sv_BDD_PSTN" in filepath:
        self.svhandles.append(gethandle(filepath))
    return self.svhandles
  
  def block(self):
    """ get list of filehandles for block bdd files"""
    self.blockhandles = []
    for filepath in self.files:
      if "block_BDD_PSTN" in filepath:
        self.blockhandles.append(gethandle(filepath))
    return self.blockhandles
