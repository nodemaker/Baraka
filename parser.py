import sys,string,pdb,re

class BarakaParser(object):
		
		def __init__(self,filename):
				self.text = open(filename, 'r').read()		
				
		def parseVariable (self,varname):
				varnameMatch = re.search(r'('+varname+')\s(.+)',self.text,re.IGNORECASE)
				if varnameMatch:
						return varnameMatch.group(2)
				else:
						return None
			