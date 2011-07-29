import sys,string,pdb,re,os,imp,pickle

from ttobjectbaraka import *
from ttitembaraka import *
from ttmodelbaraka import *
from optparse import OptionParser	

def main():
		#Add options and usage
		usage = '''%prog <options> <inputinputfile>
		
		The Three20 Barak.
		Generate Three20 inputfiles.'''
		
		optparser = OptionParser(usage = usage)
		optparser.add_option("-v", "--verbose", dest="verbose",
						help="Just print the generated source inputfiles to console",
						action="store_true")
		optparser.add_option("-d", "--debug", dest="debug",
						help="Dont print or generate anything..Just Parse and print description(for debugging purposes)",
						action="store_true") 
		optparser.add_option("-o", "--object", dest="object",
						help="Only generate or print or describe object inputfiles",
						action="store_true")
		optparser.add_option("-m", "--model", dest="model",
						help="Only generate or print or describe model inputfiles",
						action="store_true")
		optparser.add_option("-i", "--item", dest="item",
						help="Only generate or print or describe item inputfiles",
						action="store_true")				
		optparser.add_option("-p", "--parse", dest="parse",
						help="Just Parse...Dont print,generate or even print description",
						action="store_true")
		optparser.add_option("-n", "--nonly", dest="nonly",
						help="Print or Generate or describe the nth entity only",type="int",
						action="store")
		optparser.add_option("-k", "--header", dest="header",
						help="Print or Generate the Header file only",
						action="store_true")
		optparser.add_option("-s", "--source", dest="source",
						help="Print or Generate the Source file only",
						action="store_true")
		
		(options, args) = optparser.parse_args()
		
		#check if inputfile was given
		if len(args)==0:
				print usage
				sys.exit()
					
		#Check if input inputfile exists
		if not os.path.exists(args[0]):
				print "\nERROR: inputfile %s does not exist"%args[0]
				print "EXITING..."
				sys.exit()	
						
		baraks = []
		inputfile = args[0]
		
		#create the necessary baraks
		if options.__dict__['item']:
				baraks.append(TTItemBaraka(inputfile))
		
		if options.__dict__['model']:
				baraks.append(TTModelBaraka(inputfile))
		
		if options.__dict__['object']:
				baraks.append(TTObjectBaraka(inputfile))
		
		if not baraks:
				baraks.append(TTItemBaraka(inputfile)) 		
				baraks.append(TTModelBaraka(inputfile))
				baraks.append(TTObjectBaraka(inputfile))
		
		n = 0
		#check for the nonly header and source option
		if options.__dict__['nonly']:
				n = options.__dict__['nonly']
		
		
		header = False
		source = False
		if options.__dict__['header']:
				header = True
		elif options.__dict__['source']:
				source = True
		else:
				header = True
				source = True
		
		#ask the baraks to perform the necessary operations	
		if options.__dict__['parse']:
				print "\nSuccessfully Parsed inputfile %s"%os.path.basename(args[0])
				sys.exit()
		elif options.__dict__['debug']:
				for baraka  in baraks:
						print baraka.description(n)
		elif options.__dict__['verbose']:
				for baraka  in baraks:
						baraka.printToConsole(n,header,source)
		else:	
				for baraka  in baraks:
						baraka.generate(n,header,source)
						
if __name__ == '__main__':
	main()