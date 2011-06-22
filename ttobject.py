import sys,string,pdb

from ttmodelbarak import *

def main():
		
		if len(sys.argv)==1:
				print "Usage T20ModelObject.py <input-source-file-name>"
		
		filename = sys.argv[1];
		
		parser = ModelParser(filename)
		
		project = parser.projectname
		hacker =  parser.parseVariable('hacker')
		
		if not project:
				print 'WARNING:Project Name not found\n'				
		
		if hacker:
				print 'Wassup '+hacker+' Baraka will now generate code for you...\n'
		else:
				print 'Who are you Mr.Hacker?'

		#modelObject = parser.modelObjects[1]
		
		for modelObject in parser.modelObjects:
				mClass = ModelObjectClass(modelObject)
				mHeaderFile = ObjCHeaderFile(mClass,project)
				mHeaderFile.printout()	
					
		
		

## Standard boilerplate to call the main() function to begin
## the program. 
if __name__ == '__main__':
  main()
  	
