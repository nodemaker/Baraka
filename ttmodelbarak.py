import sys,string,pdb,re,os,imp
import pickle

dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"

from optparse import OptionParser
from objcbarak import *
from parser import *



class dotdict(dict):
    	def __getattr__(self, attr):
        	return self.get(attr, None)
    	__setattr__= dict.__setitem__
    	__delattr__= dict.__delitem__


class ModelObjectClass(ObjCClass):

		def __init__(self,modelobject,parser):
				
				self.parser = parser
				self.modelobject = modelobject
				super(ModelObjectClass,self).__init__(modelobject.name,modelobject.type)
		
				for subObject in modelobject.subObjects:
						
						variable = ObjCVar(subObject.type,subObject.name)
						
						attributes = ["nonatomic"]
						
						if variable.type.objCType() is 'NSString':
								attributes.append("copy")
						else:	
								attributes.append("retain")
							
						self.addInstanceVariable(variable,True,attributes)
				
				self.addMethod(ModelObjectStaticInitMethod(self,parser))
				self.addMethod(ModelObjectInitMethod(self))
				self.addMethod(ModelObjectDeallocMethod(self))
				self.addMethod(ModelObjectDescriptionMethod(self))
		
		def hasDateSubObject (self):
				for variable in self.variables:
						if variable.type.objCType() is "NSDate":
								return True
				return False											
	

class ModelObjectInitMethod(InitMethod):

		def __init__(self,modelclass):
				super(ModelObjectInitMethod,self).__init__(modelclass,[ObjCVar("Dictionary","entry")],"initWithDictionary:")
				
		def definition(self):
				definition = super(ModelObjectInitMethod,self).definition()
				
				definition.append("")
				
				nullcheckBlock = CodeBlock("if([entry isKindOfClass:[NSNull class]])")
				nullcheckBlock.appendStatement("return nil")
				definition.extend(nullcheckBlock)
				
				
				if self.objcclass.supertype.objCType() is "NSObject":
					initializationBlock = CodeBlock("if(self = [super init])")
				else:
					initializationBlock = CodeBlock("if(self = [super initWithDictionary:entry])")
				
				initializationBlock.append("")
				
				if self.objcclass.hasDateSubObject():
						initializationBlock.appendStatement("NSDateFormatter* dateFormatter = [[[NSDateFormatter alloc] init] autorelease]")
						initializationBlock.appendStatement("[dateFormatter setTimeStyle:NSDateFormatterFullStyle]")
						initializationBlock.appendStatement("[dateFormatter setDateFormat:@\"%s\"]"%dateFormat)
						initializationBlock.append("")
				
				for subObject in self.objcclass.modelobject.subObjects:

						lastEntryName = "entry"
						lastBlock = initializationBlock
						
						for key in subObject.key:
								ifblock = CodeBlock("if([%(dictionary)s objectForKey:@\"%(key)s\"])"%{'dictionary':lastEntryName,'key':key},lastBlock)	
								params = {'newDictName':key+"Entry",'newArrayName':key+"Entries",'lastDictName':lastEntryName,'key':key}
								
								if key is not subObject.key[-1]:
										ifblock.appendStatement("NSDictionary* %(newDictName)s = [%(lastDictName)s objectForKey:@\"%(key)s\"]"%params)
										lastEntryName = params["newDictName"]
								elif subObject.objCType() is "NSArray":
										ifblock.appendStatement("NSArray* %(newArrayName)s = [%(lastDictName)s objectForKey:@\"%(key)s\"]"%params)
										lastEntryName = params["newArrayName"]
								
								lastBlock = ifblock		
						
						count = len(subObject.key)   	
						objectkey = subObject.key[count-1]
														
						params = {'objectname':subObject.name,'dictionary':lastEntryName,'key':objectkey,'subtype':subObject.subtype}
						if subObject.isBaseType():
								if subObject.objCType() is "NSString": 
										lastBlock.appendStatement("self.%(objectname)s = [NSString stringWithString:[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params)
								elif subObject.objCType() is "NSDate": 
										lastBlock.appendStatement("self.%(objectname)s = [dateFormatter dateFromString:[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params)
								elif subObject.objCType() is "NSNumber":
										lastBlock.appendStatement("self.%(objectname)s = [NSNumber numberWithInt:[[%(dictionary)s objectForKey:@\"%(key)s\"] intValue]]"%params)
								elif subObject.objCType() is "NSArray":
										lastBlock.append("")
										lastBlock.appendStatement("NSMutableArray* %(objectname)s = [NSMutableArray arrayWithCapacity:[%(dictionary)s count]]"%params)
										
										self.objcclass.implImports.add(ObjCType(subObject.subtype))
										
										forblock = CodeBlock("for (NSDictionary* entry in %(dictionary)s)"%params)
										forblock.appendStatement("[%(objectname)s addObject:[[[%(subtype)s alloc] initWithDictionary:entry] autorelease]]"%params)
										
										lastBlock.extend(forblock)
										lastBlock.appendStatement("self.%(objectname)s = %(objectname)s"%params)
								else:
										lastBlock.append("I dont fucking know")
						else:
								lastBlock.appendStatement("self."+subObject.name+" = [[["+subObject.objCType()+" alloc] initWithDictionary:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]] autorelease]")
						while lastBlock and lastBlock is not initializationBlock:
								lastBlock.superBlock.extend(lastBlock);
								lastBlock.superBlock.append("")
								lastBlock = lastBlock.superBlock;
						
				definition.append("")
				definition.extend(initializationBlock)
				definition.append("")
				definition.appendStatement("return self")
				return definition
				
class ModelObjectDeallocMethod(DeallocMethod):

		def __init__(self,modelclass):
				super(ModelObjectDeallocMethod,self).__init__(modelclass)
				
		def definition	(self):	
				definition = CodeBlock("-("+self.returnType.objCPointer()+") "+self.fullname())
				
				for variable in self.objcclass.variables:
						definition.appendStatement("TT_RELEASE_SAFELY(%s)"%variable.ivarname())
				definition.extend(["","[super dealloc];"])

				return definition
				


class ModelObjectDescriptionMethod(ObjCMethod):
		
		def __init__(self,modelclass):
				super(ModelObjectDescriptionMethod,self).__init__(modelclass,"String",[],"description")					
				
		def definition(self):
				definition = super(ModelObjectDescriptionMethod,self).definition()
				descriptionString = "[NSString stringWithFormat:@\"\\n"
			
				for variable in self.objcclass.variables:
						descriptionString += variable.name+" - %@\\n"
				
				descriptionString += "\""
				
				for variable in self.objcclass.variables:
						descriptionString += "," +variable.ivarname()
				
				
				descriptionString += "]"
			
				definition.appendStatement("return "+descriptionString)
				return definition
		
		def declaration(self):
				return None

class ModelObjectStaticInitMethod(ObjCMethod):
		
		def __init__(self,modelclass,parser):
				super(ModelObjectStaticInitMethod,self).__init__(modelclass,modelclass.name,[ObjCVar("Dictionary","entry")],"objectWithDictionary:",ObjCMethodType.staticMethod)
				self.parser = parser
		
		def definition(self):
				definition = super(ModelObjectStaticInitMethod,self).definition()
				
				submodelobjects = self.parser.getModelObjectsWithSuperModelObject(self.objcclass.modelobject)
				
				for modelObject in submodelobjects:
						params = {'field':modelObject.qualification.field,'qualifier':modelObject.qualification.qualifier}
						ifblock = CodeBlock("if([[entry objectForKey:@\"%(field)s\"] isEqualToString:@\"%(qualifier)s\"])"%params)
						ifblock.appendStatement("return [%s objectWithDictionary:entry]"%modelObject.name)
						definition.extend(ifblock)
						self.objcclass.implImports.add(ObjCType(modelObject.name))
										
				definition.appendStatement("return [[[%s alloc] initWithDictionary:entry] autorelease]"%self.objcclass.name)
				
				return definition
				
class ModelObject(object):
		
		def __init__ (self,objectName,objectType,qualification):
				self.name = objectName
				self.type = objectType
				self.subObjects = []
				self.qualification = qualification	
		
		def addObject(self,subObject):
				self.subObjects.append(subObject)
		
		def description(self):
				description = "<ModelObject>" + " " + self.name +" Type:"+ self.type
				for subObject in self.subObjects:
						description+="\n"+subObject.description()
				return description

class ObjectQualification(object):
		def __init__(self,qualificationString):
				split = re.split(r'=',qualificationString)
				self.field = split[0]
				self.qualifier = split[1] 
				self.qualificationString = qualificationString

class Model(object):
	
		def __init__(self,modelname,modelsuper,modeltype,input,output):
				self.modelname = modelname
				self.modeltype = modeltype
				self.modelsuper = modelsuper
				
class ModelInput(object):
		
		def __init__(self,inputtype,inputstring):
				self.inputtype = inputtype
				self.inputstring = inputstring				

class BaseObject(object):
		
		def __init__ (self,baseObjectType,baseObjectSubType,baseObjectName,baseObjectKey):
				self.name = baseObjectName
				self.type = baseObjectType
				self.subtype = baseObjectSubType
				self.key = baseObjectKey	
		
		def description (self):
				return "\t<BaseObject>" + " " + self.name +" Type:"+ self.type
		
		def isBaseType(self):
				return ObjCType(self.type).isBaseType()
				
		def objCType(self):
				return ObjCType(self.type).objCType()
		


class ModelParser(BarakaParser):
		
		def __init__(self,filename):
				super(ModelParser,self).__init__(filename)
				
				self.modelObjects = []
				
				self.models = []
				
				self.parseObjects()	
				
				self.parseModels()		
		
		def parseModels  (self):
				
				rawModels = re.findall(r"[\n\A](Model.*?)(?:(?:\nEnd))",self.text,re.DOTALL)
				
				for rawModel in rawModels:
					
						lines = re.split(r'[\n\t\r]+',rawModel)
						
						modeldeclaration = re.split(r'[\s+\t+^$]',lines[0])
						
						if len(modeldeclaration)>2:
								superclass = modeldeclaration[2]
						else:
								superclass = "TTURLRequestModel"
						
						modelclasssplit = re.split(r'[<>]',modeldeclaration[1])
						
						modelclass = modelclasssplit[0]

						if len(modelclasssplit)>1:
								modeltype = modelclasssplit[1]
						else:
								modeltype = None
						
						model = Model(modelclass,superclass,modeltype)
			
								 
						
		def parseObjects (self):
		
				rawObjects = re.findall(r"[\n\A](Object.*?)(?:(?:\nEnd))",self.text,re.DOTALL)
				
				for object in rawObjects:
						
						lines = re.split(r'[\n\t\r]+',object)
						
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
								
						self.modelObjects.append(modelObject)
						
		def getModelObjectsWithSuperModelObject(self,superObject):
				
				objectlist = []
				
				for modelObject in self.modelObjects:
						if modelObject.type == superObject.name:
								objectlist.append(modelObject)
								
				return objectlist
		
		def generateOutputFiles(self,rootpath,modelobjectdirpath):
				
				print "\nGenerating Models from file %s..."%os.path.basename(sys.argv[1])
				
				project=self.projectName
				delint = False		
				if self.parseVariable('THREE20_PATH'):
						lintscriptrootdir =rootpath+"/"+self.parseVariable('THREE20_PATH')+"/"+"src/scripts"
						
						if os.path.exists(lintscriptrootdir):
								sys.path.append(lintscriptrootdir)
								lint_mod = imp.load_source("lint",lintscriptrootdir+"/lint")
								lint_mod.maxlinelength = 1000
								delint = True						
						else:
								print "\nWARNING: lint script not found at path %s/lint"%lintscriptrootdir
								print "WARNING: Wont be able to delint files"
				else:
						print "\nWARNING: Three20 Path Not Found...Use Key \"THREE20_PATH\" to specify Three20 Path"
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
											
		def printOutputFiles(self):
				
				project=self.projectName
				for modelObject in self.modelObjects:
						
						mClass = ModelObjectClass(modelObject,self)
						mHeaderFile = ObjCHeaderFile(mClass,project)
						mHeaderFile.printout()
						
						mImplementationFile = ObjCImplFile(mClass,project)
						mImplementationFile.printout()
				
		
		
		def description(self):
				description = ""
				for modelObject in self.modelObjects:
						description+="\n"+modelObject.description()
				return description
			
