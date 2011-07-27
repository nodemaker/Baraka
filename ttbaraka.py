import sys,string,pdb,re,os,imp,pickle

from baraka import Baraka
from file import *
from objc import *

class ObjectQualification(object):
		def __init__(self,qualificationString):
				split = re.split(r'=',qualificationString)
				self.field = split[0]
				self.qualifier = split[1] 
				self.qualificationString = qualificationString	

class TTBaraka(Baraka):
								
		def parse(self):
				super(TTBaraka,self).parse()
				self.urlmacro =  self.checkGlobalSetting("url_macro","macro for converting shortURLs","URLs wont be converted",None)
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
								
								
								
class TTStaticInitMethod(StaticInitMethod):				
		
		def definition(self):
				definition = CodeBlock(self.fullname())
				
				subClassEntities = self.objcclass.baraka.getSubEntities(self.objcclass.name)
				
				var = self.variables[0]
				
				for entity in subClassEntities:
						inputSubEntity = entity.getSubEntityByName("input")

						condition = None

						for baseEntity in inputSubEntity.baseEntities:
								if not baseEntity.subName:
										continue
														
								qualification = ObjectQualification(baseEntity.subName)
								
								if not condition:
										condition = ""
								else:
										condition += "&&"	
								
								params = {'field':qualification.field,'qualifier':qualification.qualifier,'var':var.name,'class':baseEntity.type}
								
								if baseEntity.type.lower() == "Dictionary".lower():
										condition+="[[%(var)s objectForKey:@\"%(field)s\"] isEqualToString:@\"%(qualifier)s\"]"%params
								else:
										condition+="[[%(var)s %(field)s] isEqualToString:@\"%(qualifier)s\"]"%params
										
						
						if condition:
				
								ifblock = CodeBlock("if(%s)"%condition)
														
								mClass = self.objcclass.__class__(entity,self.objcclass.baraka)
								
								castCondition = None
								
								methodInputVariables = mClass.staticInitMethod.variables
								
								outputVariables = []
								
								for index,var in enumerate(self.variables): 
										inputVar = methodInputVariables[index]
										if not var.type.name.lower() == inputVar.type.name.lower():
												params = {'var':var.name,'class':inputVar.type.name}
												if not castCondition:
														castCondition="[%(var)s isKindOfClass:[%(class)s class]]"%params
												else:	
														castCondition+="&&[%(var)s isKindOfClass:[%(class)s class]]"%params
												outputVariables.append(ObjCVar(var.type.name,"(%(type)s*)%(name)s"%{'type':inputVar.type.name,'name':var.name}))
										else:
												outputVariables.append(ObjCVar(var.type.name,var.name))		
											
								if castCondition:
										castBlock = CodeBlock("if(%s)"%castCondition)
										castBlock.appendStatement("return %s"%mClass.callStaticMethodString(mClass.staticInitMethod,outputVariables))
										ifblock.extend(castBlock)
								else:
										ifblock.appendStatement("return %s"%mClass.callStaticMethodString(mClass.staticInitMethod,outputVariables))
								
								definition.extend(ifblock)
								
								self.objcclass.implImports.add(ObjCType(entity.typeBaseEntity.type))
										
				definition.appendStatement("return [[[%(class)s alloc] %(initMethod)s] autorelease]"%{'class':self.objcclass.name,'initMethod':self.objcclass.initMethod.callString(self.variables)})
				return definition									