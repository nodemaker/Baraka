import sys,string,pdb,re

class BarakaParser(object):
		
		def __init__(self,filename):
				self.text = open(filename, 'r').read()
				self.projectName = self.parseVariable('PROJECT')
				self.hackerName = self.parseVariable('HACKER')
				
				if not self.projectName:
					print 'WARNING: project name not found.Use Key \"PROJECT\" to specify project name'	
					
				if not self.hackerName:
					print 'WARNING: hacker name not found.Use Key \"HACKER\" to specify hacker name'		
				
		def parseVariable (self,varname):
				varnameMatch = re.search(r'('+varname+')\s(.+)',self.text,re.IGNORECASE)
				if varnameMatch:
						return varnameMatch.group(2)
				else:
						return None
		
		def description(self):
				return "This is project %(projectname)s by Hacker %(hackername)s"%{'projectname':self.projectname,'hackername':self.hackername}
			