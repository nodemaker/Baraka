import sys,string,pdb,re,os,imp,pickle

from baraka import Baraka
from file import *
from objc import *


class TTBaraka(Baraka):		
								
		def parse(self):
				super(TTBaraka,self).parse()
				self.three20path = self.checkGlobalSetting("three20_path","path to Three20 project","The files wont be delinted",None)
				if self.three20path:
						self.lintscriptrootdir =self.rootpath+"/"+self.three20path+"/"+"src/scripts"
						if os.path.exists(self.lintscriptrootdir):
								sys.path.append(self.lintscriptrootdir)
								self.lint_mod = imp.load_source("lint",self.lintscriptrootdir+"/lint")
								self.lint_mod.maxlinelength = 1000
								self.delint = True						
						else:
								print "\nWARNING: lint script not found at path %s/lint"%lintscriptrootdir
								print "WARNING: Wont be able to delint files"
								self.delint = False								
								
		def printToConsole(self):
				for objcclass in self.classes:
						HeaderFile = ObjCHeaderFile(objcclass,self.project)
						HeaderFile.printout()
						
						ImplementationFile = ObjCImplFile(objcclass,self.project)
						ImplementationFile.printout()	
			
		def generate(self):
				self.generatedFiles = []
				
				for objcclass in self.classes:
						HeaderFile = ObjCHeaderFile(objcclass,self.project)
						HeaderFile.generateFile(self.dirpath)
						self.generatedFiles.append(HeaderFile.filePath(self.dirpath))
												
						ImplementationFile = ObjCImplFile(objcclass,self.project)
						ImplementationFile.generateFile(self.dirpath)
						self.generatedFiles.append(ImplementationFile.filePath(self.dirpath))	
				
				if self.delint:
						for generatedFile in self.generatedFiles:				
								self.lint_mod.lint(generatedFile,dotdict({'delint': True}))	
						
						#cleanup the lintc file
								lintcfile = self.lintscriptrootdir+"/lintc"
								if(os.path.exists(lintcfile)):
										os.remove(lintcfile)														
				
