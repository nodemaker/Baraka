import sys,string,pdb,re,os,imp,pickle

from parser import *
from objcbarak import *
from ttmodelbarak import *
from ttmodelobjectbarak import *

def print_sub_section(parser,section,sub):
		print sub.title()+"\n\t"+"\n\t".join(parser.parseSubSection(section,sub))

class Three20Parser(Parser):
		
		def __init__(self,filename):
				super(Three20Parser,self).__init__(filename)
				self.parseObjects()	
				#self.parseModels()	
		
		
		def parseObjects (self):
		
				objects = self.parseSections("object")
				for object in objects:
					print_sub_section(self,object,"input")
					print_sub_section(self,object,"output")
					
		
		def parseModels(self):
				
				rawModels = re.findall(r"[\n\A](Model.*?)(?:(?:\nEnd))",self.text,re.DOTALL)
				
				for rawModel in rawModels:
							
						lines = re.split(r'[\n\t\r]+',rawModel)
						
						modeldeclaration = re.split(r'[\s+\t+^$]',lines[0])
						
						modelclass = modeldeclaration[1]
						
						if len(modeldeclaration)>2:
								superclass = modeldeclaration[2]
						else:
								superclass = "TTURLRequestModel"
						
						model = Model(modelclass,superclass)
						
						for line in lines[1:]:
								
								modelparamdeclaration = re.split(r'[\s+\t+^$,]',line)
								modelparamtype = modelparamdeclaration[0]
								if modelparamtype.lower() == "input":
										for inputdeclaration in modelparamdeclaration[1:]:
												inputdeclarationsplit = re.split(r'[\(\)]',inputdeclaration)
												model.inputs.append(ModelInput(inputdeclarationsplit[0],inputdeclarationsplit[1]))
												
								elif modelparamtype.lower() == "output":
								 		for (objecttype,objectname) in zip(modelparamdeclaration[1::2],modelparamdeclaration[2::2]):
								 				objecttypesplit = re.findall(r'\w+',objecttype)
												objecttype = objecttypesplit[0]
												if (len(objecttypesplit)>1):
														objectsubtype = objecttypesplit[1]
												else:	
														objectsubtype = "Base"
												
												objectnamesplit = re.findall(r'\w+',objectname)
												objectname = objectnamesplit[0]
												if (len(objectnamesplit)<2):
														objectkey = [objectname]
												else:
														objectkey = [key for key in objectnamesplit[1:] if key]
								
												model.outputs.append(BaseObject(objecttype,objectsubtype,objectname,objectkey))		
								elif modelparamtype.lower() == "filter":
										for (filtertype,filtername) in zip(modelparamdeclaration[1::2],modelparamdeclaration[2::2]):
									
												filternamesplit = re.findall(r'\w+',filtername)
												filtername = filternamesplit[0]
												if (len(filternamesplit)<2):
														filterkey = [filtername]
												else:
														filterkey = [key for key in filternamesplit[1:] if key]
												model.filters.append(BaseObject(filtertype,None,filtername,filterkey))	
						self.models.append(model)					
						
		def getModelObjectsWithSuperModelObject(self,superObject):
				
				objectlist = []
				
				for modelObject in self.modelObjects:
						if modelObject.type == superObject.name:
								objectlist.append(modelObject)
								
				return objectlist
				
		def getModelObjectWithModelObjectName(self,name):
	
				for modelObject in self.modelObjects:
						if modelObject.name == name:
								return modelObject
						
				return None				
		
		def generateObjectFiles(self):
				
				modelobjectdirpath = self.rootpath +"/"+self.modelobjectdir
				if not os.path.exists(modelobjectdirpath):
						print "\nCreating Directory %s"%modelobjectdirpath
						os.makedirs(modelobjectdirpath)	
				
				print "\nGenerating Models from file %s..."%self.inputfilename
				
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
				
				for modelObject in self.modelObjects:
						
						mClass = ModelObjectClass(modelObject,self)
						print ""
						
						mHeaderFile = ObjCHeaderFile(mClass,project)
						mHeaderFile.generateFile(modelobjectdirpath)
						if delint is True:
								lint_mod.lint(mHeaderFile.filePath(modelobjectdirpath),dotdict({'delint': True}))
						
						mImplementationFile = ObjCImplFile(mClass,project)
						mImplementationFile.generateFile(modelobjectdirpath)				
						if delint is True:
								lint_mod.lint(mImplementationFile.filePath(modelobjectdirpath),dotdict({'delint': True}))
								
								
											
		def printObjectFiles(self):
				
				for modelObject in self.modelObjects:
						
						mClass = ModelObjectClass(modelObject,self)
						
						mHeaderFile = ObjCHeaderFile(mClass,self.project)
						mHeaderFile.printout()
						
						mImplementationFile = ObjCImplFile(mClass,self.project)
						mImplementationFile.printout()
				
		def printModelFiles(self):
				
				
				for model in self.models:
						
						mClass = ModelClass(model,self)
						
						mHeaderFile = ObjCHeaderFile(mClass,self.project)
						mHeaderFile.printout()
						
						mImplementationFile = ObjCImplFile(mClass,self.project)
						mImplementationFile.printout()

		
		def modelDescription(self):
				description = "Models"
				description += "\n------"
				for model in self.models:
						description+="\n"+model.description()		
				return description
				
		def objectDescription(self):
				description = "Model Objects:"
				description += "\n-------------"
				for modelObject in self.modelObjects:
						description+="\n"+modelObject.description()
				return description
				
				
				
	
'''						lines = re.split(r'[\n\t\r]+',object)
						
						objectdeclaration = re.split(r'[\s+\t+^$\(\)]',lines[0])
						
						objectclass = objectdeclaration[1]
						
						if len(objectdeclaration)>2:
								superclass = objectdeclaration[2] 
						else:
								superclass = "Object"
						
						if len(objectdeclaration)>3:
								qualification = ObjectQualification(objectdeclaration[3]) 
						else:
								qualification = None
								
						if not qualification and superclass is not "Object":
								print "\nERROR: error parsing object %s.An object with a non object superclass must have a qualification"%objectclass
								sys.exit(0) 		
												
						modelObject = ModelObject(objectclass,superclass,qualification)
						
						subobjects = re.split(r'[\n\t]+',object[1])
						
						for subobject in lines[1:]:
								
								split = re.findall(r'[\w<>\(\):]+',subobject)
								
								if(len(split)<2):
									print "ERROR: could not parse subobject declaration -> "+subobject+" in Object "+objectclass
									sys.exit()
								
								objecttypesplit = re.findall(r'\w+',split[0])
								
								objecttype = objecttypesplit[0]
								
								if (len(objecttypesplit)>1):
										objectsubtype = objecttypesplit[1]
								else:	
										objectsubtype = "Base"
								
								objectnamesplit = re.findall(r'\w+',split[1])
								
								objectname = objectnamesplit[0]
								
								if (len(objectnamesplit)<2):
										objectkey = [objectname]
								else:
										objectkey = [key for key in objectnamesplit[1:] if key]
								
								modelObject.addObject(BaseObject(objecttype,objectsubtype,objectname,objectkey))
								
						self.modelObjects.append(modelObject)'''