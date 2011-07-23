import sys,string,pdb,re,os,imp, pickle

from objcbaraka import *
from baraka import *
from code import *

dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"


class TTObjectBaraka(Baraka):
		
		def __init__(self,fileName):
				self.classes = []
				super(TTObjectBaraka,self).__init__(fileName,["object"],["input","output"])
				self.create()
		
		def create(self):
				for entity in self.entities:
						self.classes.append(ModelObjectClass(entity,self))	
					
		def printToConsole(self):
				for objcclass in self.classes:
						HeaderFile = ObjCHeaderFile(objcclass,self.project)
						HeaderFile.printout()
						
						ImplementationFile = ObjCImplFile(objcclass,self.project)
						ImplementationFile.printout()
		
		def generate(self):
				modelobjectdirpath = self.rootpath +"/"+self.modelobjectdir
				if not os.path.exists(modelobjectdirpath):
						print "\nCreating Directory %s"%modelobjectdirpath
						os.makedirs(modelobjectdirpath)	
				
				print "\nGenerating Models from file %s...\n"%self.inputfilename
				
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
						HeaderFile.generateFile(modelobjectdirpath)
						if delint is True:
								lint_mod.lint(HeaderFile.filePath(modelobjectdirpath),dotdict({'delint': True}))
						
						ImplementationFile = ObjCImplFile(objcclass,self.project)
						ImplementationFile.generateFile(modelobjectdirpath)
						if delint is True:
								lint_mod.lint(ImplementationFile.filePath(modelobjectdirpath),dotdict({'delint': True}))




class ModelObjectClass(ObjCClass):

		def __init__(self,objectEntity,baraka):
								
				self.objectEntity = objectEntity
				super(ModelObjectClass,self).__init__(objectEntity,baraka)
				
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
				
				self.staticInitMethod = ModelObjectStaticInitMethod(self,inputVariables)
				self.initMethod = DictionaryInitMethod(self,inputVariables)
				
				#add the dealloc and description methods
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))

class ModelObjectStaticInitMethod(StaticInitMethod):				
		
		def definition(self):
				definition = super(ModelObjectStaticInitMethod,self).definition()
				
				subClassEntities = self.objcclass.baraka.getEntitiesWithTypeName(self.objcclass.name)
				
				for entity in subClassEntities:
						qualification = ObjectQualification(entity.typeBaseEntity.subName)
						params = {'field':qualification.field,'qualifier':qualification.qualifier}
						ifblock = CodeBlock("if([[entry objectForKey:@\"%(field)s\"] isEqualToString:@\"%(qualifier)s\"])"%params)
						
						mClass = ModelObjectClass(entity,self.objcclass.baraka)
						ifblock.appendStatement("return %s"%mClass.callStaticMethodString(mClass.staticInitMethod,self.variables))
						
						definition.extend(ifblock)
						self.objcclass.implImports.add(ObjCType(entity.typeBaseEntity.type))
										
				definition.appendStatement("return [[[%(class)s alloc] %(initMethod)s] autorelease]"%{'class':self.objcclass.name,'initMethod':self.objcclass.initMethod.callString(self.variables)})
				return definition
	
class ObjectQualification(object):
		def __init__(self,qualificationString):
				split = re.split(r'=',qualificationString)
				self.field = split[0]
				self.qualifier = split[1] 
				self.qualificationString = qualificationString	

						
class DictionaryInitMethod(InitMethod):
				
		def definition(self):
				definition = CodeBlock(self.fullname())
				definition.append("")
				
				nullcheckBlock = CodeBlock("if([entry isKindOfClass:[NSNull class]])")
				nullcheckBlock.appendStatement("return nil")
				definition.extend(nullcheckBlock)

				if self.objcclass.supertype.objCType() is "NSObject":
					initializationBlock = DictionaryInitializationBlock(self.objcclass,"if(self = [super init])","entry",definition)
				else:
					initializationBlock = DictionaryInitializationBlock(self.objcclass,"if(self = [super initWithEntry:entry])","entry",definition)
				
				definition.append("")
				definition.extend(initializationBlock)
				definition.append("")
				definition.appendStatement("return self")
				return definition	
		
class DictionaryInitializationBlock(CodeBlock):
				
		def __init__(self,objcclass,blockHeader,entryName,superblock=None):
				
				super(DictionaryInitializationBlock,self).__init__(blockHeader,superblock)
				
				self.append("")
				
				outputSubEntity = objcclass.entity.getSubEntityByName("output")
							
				hasDateSubObject = False
				
				for baseEntity in outputSubEntity.baseEntities:
						if baseEntity.type == "Date":
								hasDateSubObject = True													
				
				if hasDateSubObject:
						self.appendStatement("NSDateFormatter* dateFormatter = [[[NSDateFormatter alloc] init] autorelease]")
						self.appendStatement("[dateFormatter setTimeStyle:NSDateFormatterFullStyle]")
						self.appendStatement("[dateFormatter setDateFormat:@\"%s\"]"%dateFormat)
						self.append("")
				
				for baseEntity in outputSubEntity.baseEntities:
											
						lastEntryName = entryName	
						lastBlock = self
												
						keysplit = re.findall(r'\w+',baseEntity.subName)
						if not keysplit:
							keys = [baseEntity.name]
						else:	
							keys = [key for key in keysplit if key]
						
						vartype = ObjCType(baseEntity.type)
												
						for key in keys:
								ifblock = CodeBlock("if([%(dictionary)s objectForKey:@\"%(key)s\"])"%{'dictionary':lastEntryName,'key':key},lastBlock)	
								params = {'newDictName':key+"Entry",'newArrayName':key+"Entries",'lastDictName':lastEntryName,'key':key}
								
								if key is not keys[-1]:
										ifblock.appendStatement("NSDictionary* %(newDictName)s = [%(lastDictName)s objectForKey:@\"%(key)s\"]"%params)
										lastEntryName = params["newDictName"]
								elif vartype.objCType() == "NSArray":
										ifblock.appendStatement("NSArray* %(newArrayName)s = [%(lastDictName)s objectForKey:@\"%(key)s\"]"%params)
										lastEntryName = params["newArrayName"]
								
								lastBlock = ifblock		
						
						count = len(keys)   	
						objectkey = keys[count-1]
														
						params = {'objectname':baseEntity.name,'dictionary':lastEntryName,'key':objectkey,'subtype':baseEntity.subType}
						if vartype.isBaseType():
								if vartype.objCType() is "NSString": 
										lastBlock.appendStatement("self.%(objectname)s = [NSString stringWithString:[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params)
								elif vartype.objCType() is "NSDate": 
										lastBlock.appendStatement("self.%(objectname)s = [dateFormatter dateFromString:[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params)
								elif vartype.objCType() is "NSNumber":
										lastBlock.appendStatement("self.%(objectname)s = [NSNumber numberWithInt:[[%(dictionary)s objectForKey:@\"%(key)s\"] intValue]]"%params)
								elif vartype.objCType() is "NSArray":
										lastBlock.append("")
										lastBlock.appendStatement("NSMutableArray* %(objectname)s = [NSMutableArray arrayWithCapacity:[%(dictionary)s count]]"%params)
										
										objcclass.implImports.add(vartype)
										
										forblock = CodeBlock("for (NSDictionary* entry in %(dictionary)s)"%params)
										forblock.appendStatement("[%(objectname)s addObject:[[[%(subtype)s alloc] initWithDictionary:entry] autorelease]]"%params)
										
										lastBlock.extend(forblock)
										lastBlock.appendStatement("self.%(objectname)s = %(objectname)s"%params)
								else:
										lastBlock.append("I dont fucking know")
						else:
								lastBlock.appendStatement("self."+baseEntity.name+" = [[["+vartype.objCType()+" alloc] initWithDictionary:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]] autorelease]")
						while lastBlock and lastBlock is not self:
								lastBlock.superBlock.extend(lastBlock);
								lastBlock.superBlock.append("")
								lastBlock = lastBlock.superBlock;							
