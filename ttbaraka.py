import sys,string,pdb,re,os,imp,pickle

from ttobjectbaraka import TTObjectBaraka
from optparse import OptionParser

modeldir = "DataModels"
modelobjectdir = "DataObjects"
modelurlmacro = "URL"
project = None
three20path = None
hacker = None
		
def check_variable(baraka,variablekey,keydescription,warnmessage,defaultvalue):
		value = None
		if baraka.getGlobalSetting(variablekey):
				value =  baraka.getGlobalSetting(variablekey)
		else:
				print "\nWARNING: "+keydescription+" not found...Use Key \""+variablekey+"\" to specify "+keydescription
				if defaultvalue:
						print "\nWARNING: Using "+defaultvalue+" as "+keydescription
				elif warnmessage:
						print "WARNING: "+warnmessage		
		return value					
				
def main():
		#Add options and usage
		usage = '''%prog <options> <inputfilename>
		
		The Three20 Barak.
		Generate Three20 Files.'''
		
		optparser = OptionParser(usage = usage)
		optparser.add_option("-v", "--verbose", dest="verbose",
						help="Just print the generated source files to console",
						action="store_true")
		optparser.add_option("-d", "--debug", dest="debug",
						help="Dont print or generate anything..Just Parse and print description(for debugging purposes)",
						action="store_true") 
		optparser.add_option("-o", "--object", dest="object",
						help="Only generate or print or describe object files",
						action="store_true")
		optparser.add_option("-m", "--model", dest="model",
						help="Only generate or print or describe model files",
						action="store_true")
		optparser.add_option("-p", "--parse", dest="parse",
						help="Just Parse...Dont print,generate or even print description",
						action="store_true")								
		(options, args) = optparser.parse_args()
		
		#check if input file was given
		if len(args)==0:
				print usage
				sys.exit()
					
		#Check if input file exists
		if not os.path.exists(args[0]):
				print "\nERROR: File %s does not exist"%args[0]
				print "EXITING..."
				sys.exit()			
		
		#calculate the root path		
		abspath = os.path.abspath(args[0])
		rootpath =  os.path.dirname(abspath)
		
		#initialize the baraka 
		baraka = TTObjectBaraka(args[0]);
		
		#Parse required variables from file
		global modelobjectdir
		value = check_variable(baraka,"model_object_dir","model objects destination Directory",None,modelobjectdir)
		if value:
				modelobjectdir = value	
		
		global modeldir
		value = check_variable(baraka,"model_dir","models destination directory",None,modeldir)
		if value:
				modeldir = value
		
		global modelurlmacro
		value = check_variable(baraka,"model_url","macro for creating model URLs",None,modelurlmacro)
		if value:
				modelurlmacro = value
				
		global project
		value = check_variable(baraka,"project","project name","No project name will be written in files",project)
		if value:
				project = value		
		
		global three20path
		value = check_variable(baraka,"three20_path","path to Three20 project","The files wont be delinted",three20path)
		if value:
				three20path = value
		
		global hacker
		value = check_variable(baraka,"hacker","Name of hacker","No hacker name will be written on the files",hacker)
		if value:
				hacker = value
		
		#set the required variables on the baraka		
		baraka.rootpath = rootpath
		baraka.modelobjectdir = modelobjectdir
		baraka.modeldir = modeldir
		baraka.modelurlmacro = modelurlmacro
		baraka.project = project
		baraka.three20path = three20path
		baraka.hacker = hacker
		baraka.inputfilename = os.path.basename(args[0])
	
		modeldirpath = rootpath + "/"+modeldir 		
		if not os.path.exists(modeldirpath):
				print "\nCreating Directory %s"%modeldirpath
				os.makedirs(modeldirpath)			
 		
 		
 		if options.__dict__['parse']:
 				print "\nSuccessfully Parsed file %s"%os.path.basename(args[0])
				sys.exit()
 		elif options.__dict__['debug']:
 				if options.__dict__['model']:
 					print baraka.description(['model'])
 				elif options.__dict__['object']:			
 					print baraka.description(['object'])
 				else:
					print baraka.description()
 		elif options.__dict__['verbose']:
 				baraka.printToConsole()		
 		else:
 				baraka.generate()	
		
if __name__ == '__main__':
	main()