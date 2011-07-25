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
		
		
		def generate(self,n=-1,header=True,source=True):
				
				self.generatedFiles = []
				
				if n>0:
						classes = [self.classes[n-1]]
				else:		
						classes = self.classes
						
				for objcclass in classes:
						if header:
								HeaderFile = ObjCHeaderFile(objcclass,self.project,self.hacker)
								HeaderFile.generateFile(self.dirpath)
								self.generatedFiles.append(HeaderFile.filePath(self.dirpath))						
						if source:						
								ImplementationFile = ObjCImplFile(objcclass,self.project,self.hacker)
								ImplementationFile.generateFile(self.dirpath)
								self.generatedFiles.append(ImplementationFile.filePath(self.dirpath))	
				
				if self.delint:
						for generatedFile in self.generatedFiles:				
								self.lint_mod.lint(generatedFile,dotdict({'delint': True}))	
						
								#cleanup the lintc file
								lintcfile = self.lintscriptrootdir+"/lintc"
								if(os.path.exists(lintcfile)):
										os.remove(lintcfile)														
				
													
								
		def printToConsole(self,n=-1,header=True,source=True):
		
				if n>0:
						classes = [self.classes[n-1]]
				else:		
						classes = self.classes
		
				for objcclass in classes:
						if header:
								HeaderFile = ObjCHeaderFile(objcclass,self.project,self.hacker)
								HeaderFile.printout()
						
						if source:
								ImplementationFile = ObjCImplFile(objcclass,self.project,self.hacker)
								ImplementationFile.printout()	