import sys,string,pdb,re,os,imp,pickle

from baraka import Baraka
from ttobjectbaraka import TTObjectBaraka
from ttitembaraka import TTItemBaraka
#from ttmodelbaraka import TTModelBaraka
from optparse import OptionParser

modeldir = "DataModels"
modelobjectdir = "DataObjects"
itemdir = "TableItems"
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
		optparser.add_option("-i", "--item", dest="item",
						help="Only generate or print or describe item files",
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
		baraka = Three20Baraka(args[0],options);
		
		#Parse required variables from file
		global modelobjectdir
		value = check_variable(baraka,"model_object_dir","model objects destination Directory",None,modelobjectdir)
		if value:
				modelobjectdir = value	
		
		global modeldir
		value = check_variable(baraka,"model_dir","models destination directory",None,modeldir)
		if value:
				modeldir = value
				
		global itemdir
		value = check_variable(baraka,"item_dir","Items Destination directory",None,itemdir)
		if value:
				itemdir = value		
		
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
		baraka.itemdir = itemdir
		baraka.modelurlmacro = modelurlmacro
		baraka.project = project
		baraka.three20path = three20path
		baraka.hacker = hacker
		baraka.inputfilename = os.path.basename(args[0])
			
 		baraka.passOnSettings()
 		
 		if options.__dict__['parse']:
 				print "\nSuccessfully Parsed file %s"%os.path.basename(args[0])
				sys.exit()
 		elif options.__dict__['debug']:
 				print baraka.description()
 		elif options.__dict__['verbose']:
 				baraka.printToConsole()		
 		else:
 				baraka.generate()	

class Three20Baraka(Baraka):
		
		def __init__(self,filename,options):
		
				self.itembaraka = None
				self.objectbaraka = None
				self.modelbaraka = None

				
				if options.__dict__['item']:
						self.itembaraka = TTItemBaraka(filename)
				#elif options.__dict__['model']:
						#self.modelbaraka = TTModelBaraka(filename)
				elif options.__dict__['object']:
						self.objectbaraka = TTObjectBaraka(filename)
				else:
						self.itembaraka = TTItemBaraka(filename) 		
						#self.modelbaraka = TTModelBaraka(filename)
						self.objectbaraka = TTObjectBaraka(filename)
				
				super(Three20Baraka,self).__init__(filename)			
					
		def passOnSettings(self):			
						
				if self.itembaraka:
						#set the required variables on the baraka		
						self.itembaraka.rootpath = self.rootpath
						self.itembaraka.modelobjectdir = self.modelobjectdir
						self.itembaraka.modeldir = self.modeldir
						self.itembaraka.itemdir = self.itemdir
						self.itembaraka.modelurlmacro = self.modelurlmacro
						self.itembaraka.project = self.project
						self.itembaraka.three20path = self.three20path
						self.itembaraka.hacker = self.hacker
						self.itembaraka.inputfilename = self.inputfilename
				
				if self.objectbaraka:
						#set the required variables on the baraka		
						self.objectbaraka.rootpath = self.rootpath
						self.objectbaraka.modelobjectdir = self.modelobjectdir
						self.objectbaraka.modeldir = self.modeldir
						self.objectbaraka.itemdir = self.itemdir
						self.objectbaraka.modelurlmacro = self.modelurlmacro
						self.objectbaraka.project = self.project
						self.objectbaraka.three20path = self.three20path
						self.objectbaraka.hacker = self.hacker
						self.objectbaraka.inputfilename = self.inputfilename
						
				if self.modelbaraka:
						#set the required variables on the baraka		
						modelbaraka.rootpath = self.rootpath
						modelbaraka.modelobjectdir = self.modelobjectdir
						modelbaraka.modeldir = self.modeldir
						modelbaraka.itemdir = self.itemdir
						modelbaraka.modelurlmacro = self.modelurlmacro
						modelbaraka.project = self.project
						modelbaraka.three20path = self.three20path
						modelbaraka.hacker = self.hacker
						modelbaraka.inputfilename = self.inputfilename				
							
		def description(self):
				description = super(Three20Baraka,self).description()
					
				if self.itembaraka:
						description += self.itembaraka.description()
				
				if self.modelbaraka:
						description += self.modelbaraka.description()
						
				if self.objectbaraka:
						description += self.objectbaraka.description()
						
				return description						
						
		def printToConsole(self):
				if self.itembaraka:
						self.itembaraka.printToConsole()
				
				if self.modelbaraka:
						self.modelbaraka.printToConsole()
						
				if self.objectbaraka:
						self.objectbaraka.printToConsole()
		
		def generate():						
				if self.itembaraka:
						self.itembaraka.generate()
				
				if self.modelbaraka:
						self.modelbaraka.generate()
						
				if self.objectbaraka:
						self.objectbaraka.generate()
			
						
			
			
		
if __name__ == '__main__':
	main()