import sys,string,pdb,re

from ttmodelbarak import *

modelobjectdir = "DataObjects"
				
def main():
		usage = '''%prog <options> <inputfilename>
		
		The Three20 Barak.
		Generate Three20 Files.'''

		optparser = OptionParser(usage = usage)
		optparser.add_option("-p", "--print", dest="print",
						help="Just Display Generated Source Files (for debugging purposes)",
						action="store_true")
		optparser.add_option("-d", "--debug", dest="debug",
						help="Dont do anything..Just Parse (for debugging purposes)",
						action="store_true")          
		
		(options, args) = optparser.parse_args()
		
		if len(args)==0:
				print usage
				sys.exit()
					
		if not os.path.exists(args[0]):
				print "\nERROR: File %s does not exist"%args[0]
				print "EXITING..."
				sys.exit()			
					
		global parser
		parser = ModelParser(args[0])
		
		abspath = os.path.abspath(args[0])
		rootpath =  os.path.dirname(abspath)
 				
 		global modelobjectdir
		if parser.parseVariable('MODEL_OBJECT_DIR'):
				modelobjectdir =  parser.parseVariable('MODEL_OBJECT_DIR')
				modelobjectdirpath =rootpath +"/"+modelobjectdir
		else:
				modelobjectdirpath = rootpath +"/"+modelobjectdir
				print "\nWARNING: Model Objects Destination Directory not found...Use Key \"MODEL_OBJECT_DIR\" to specify Model Objects Destination Directory "	
				print "WARNING: Using %s as Model Objects Destination Directory"%modelobjectdirpath					
		
		if not os.path.exists(modelobjectdirpath):
				print "\nCreating Directory %s"%modelobjectdirpath
				os.makedirs(modelobjectdirpath)	
 		
 		if options.__dict__['print']:	
 				parser.printOutputFiles()
 		elif not options.__dict__['debug']:
 				parser.generateOutputFiles(rootpath,modelobjectdirpath)
		
if __name__ == '__main__':
	main()