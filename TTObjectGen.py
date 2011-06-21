import sys,string,pdb

from TTModelParser import *

def main():
		
		if len(sys.argv)==1:
				print "Usage T20ModelObject.py <input-source-file-name>"
		
		filename = sys.argv[1];
		
		parser = ModelParser(filename)
		
		project = parser.projectName()
		hacker =  parser.parseVariable('hacker')
		
		if not project:
				print 'WARNING:Project Name not found\n'				
		
		if hacker:
				print 'Wassup '+hacker+' T20Gen will now generate code for you...\n'
		else:
				print 'Who are you Mr.Hacker?'
		
		for modelObject in parser.objects():
				mClass = ModelObjectClass(modelObject)
		
		
		

## Standard boilerplate to call the main() function to begin
## the program. 
if __name__ == '__main__':
  main()
  	
