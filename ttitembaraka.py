import sys,string,pdb,re,os,imp, pickle

from objcbaraka import *
from baraka import *
from code import *

class TTItemBaraka(Baraka):
		
		def __init__(self,fileName):
				self.classes = []
				super(TTItemBaraka,self).__init__(fileName,["item"],["input","output"])
				self.create()
		
		def create(self):
				for entity in self.entities:
						self.classes.append(ItemClass(entity,self))	
					
		def printToConsole(self):
				for objcclass in self.classes:
						HeaderFile = ObjCHeaderFile(objcclass,self.project)
						HeaderFile.printout()
						
						ImplementationFile = ObjCImplFile(objcclass,self.project)
						ImplementationFile.printout()
		
		def generate(self):
				itemdirpath = self.rootpath +"/"+self.itemdir
				if not os.path.exists(itemdirpath):
						print "\nCreating Directory %s"%itemdirpath
						os.makedirs(itemdirpath)	
				
				print "\nGenerating Items from file %s...\n"%self.inputfilename
				
				project=self.project
				delint = False		
				if self.three20path:
						lintscriptrootdir =self.rootpath+"/"+self.three20path+"/"+"src/scripts"
						if os.path.exists(lintscriptrootdir):
								sys.path.append(lintscriptrootdir)
								lint_mod = imp.load_source("lint",lintscriptrootdir+"/lint")
								lint_mod.maxlinelength = 1000
								delint = True						
						else:
								print "\nWARNING: lint script not found at path %s/lint"%lintscriptrootdir
								print "WARNING: Wont be able to delint files"
				
				for objcclass in self.classes:
						HeaderFile = ObjCHeaderFile(objcclass,self.project)
						HeaderFile.generateFile(itemdirpath)
						if delint is True:
								lint_mod.lint(HeaderFile.filePath(itemdirpath),dotdict({'delint': True}))
						
						ImplementationFile = ObjCImplFile(objcclass,self.project)
						ImplementationFile.generateFile(itemdirpath)
						if delint is True:
								lint_mod.lint(ImplementationFile.filePath(itemdirpath),dotdict({'delint': True}))

class ItemClass(ObjCClass):

		
		def __init__(self,itemEntity,baraka):
								
				self.itemEntity = itemEntity
				super(ItemClass,self).__init__(itemEntity,baraka)
				
				#add the instance variables from the output subentity
				outputSubEntity = self.entity.getSubEntityByName("output")
				
				for baseEntity in outputSubEntity.baseEntities:
						variable = ObjCVar(baseEntity.type,baseEntity.name)
						attributes = ["nonatomic"]
						if variable.type.objCType() is 'NSString' or variable.type.objCType() is 'NSDate':
								attributes.append("copy")
						else:	
								attributes.append("retain")
							
						self.addInstanceVariable(variable,True,attributes)
				
				
				#add the init methods from the input subentity
				inputVariables = []
				inputSubEntity = self.entity.getSubEntityByName("input")
				
				for baseEntity in inputSubEntity.baseEntities:
						inputVariables.append(ObjCVar(baseEntity.type,baseEntity.name))
				
				self.initMethod = InitMethod(self,inputVariables)
				
				#add the dealloc and description methods
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))
								