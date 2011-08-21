import os
from code import *

divider = "///////////////////////////////////////////////////////////////////////////////////////////////////"

def firstuppercase(string):
	if string:
			return string[0].upper()+string[1:]
	else:
			return None			

				

class File(object):
		
		def __init__(self,tab="\t"):
				self.code = []
				self.level=0
				self.tab=tab
		
		def write(self,line):
				self.code.append(self.tab*self.level+line)
				
		def printout(self):
				print "\n\n\nFile:"+self.filename()
				print "--------------------"
				print "\n".join(["%s" % (line) for line in self.lines()])		
		
		def filePath(self,rootdir):
				return rootdir + "/" + self.filename()
				
		def generateFile(self,rootdir):
				if not os.path.exists(rootdir):
					os.makedirs(rootdir)
					print "Creating Directory %s"+rootdir
						
 				if os.path.exists(self.filePath(rootdir)):
 					mode = "OVERWRITE"
				else:
					mode = "NEW"
					
				print "Generating File %(filename)s (%(mode)s)"%{'filename':self.filename(),'mode':mode}
				
				outputfile = open(self.filePath(rootdir),'w')
				outputfile.write("\n".join(["%s" % (line) for line in self.lines()])	)		
		
		def lines(self):
				return []
				
		def filename(self):
				return None		 
				