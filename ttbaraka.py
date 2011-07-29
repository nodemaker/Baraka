import sys,string,pdb,re,os,imp,pickle

dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"


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
				
				
class DictionaryInitializationBlock(CodeBlock):
				
		def __init__(self,objcclass,baseEntities,blockHeader,entryName,superblock=None,propertiesReadOnly=False):
				
				super(DictionaryInitializationBlock,self).__init__(blockHeader,superblock)
				
				self.append("")
				
				outputSubEntity = objcclass.entity.getSubEntityByName("output")
							
				hasDateSubObject = False
				
				for baseEntity in baseEntities:
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
											
						if not (len(keys) == 1 and keys[0] == "ROOT"):												
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
						
						params = {'objectname':baseEntity.name,'dictionary':lastEntryName,'key':objectkey,'subtype':baseEntity.subType,'vartype':vartype.objCType()}
						
						if objectkey == "ROOT":
								params['initializer'] = lastEntryName
						else:
								params['initializer'] = "[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params

								
						if vartype.isBaseType():
								if vartype.objCType() is "NSString": 
										initializer = "[NSString stringWithString:%(initializer)s]"%params
								elif vartype.objCType() is "NSDictionary":
										initializer = "[NSDictionary dictionaryWithDictionary:%(initializer)s]"%params
								elif vartype.objCType() is "NSDate": 
										initializer = "[dateFormatter dateFromString:%(initializer)s]"%params
								elif vartype.objCType() is "NSNumber":
										initializer = "[NSNumber numberWithInt:[%(initializer)s intValue]]"%params
								elif vartype.objCType() is "NSArray":
										lastBlock.append("")
										lastBlock.appendStatement("NSMutableArray* %(objectname)s = [NSMutableArray arrayWithCapacity:[%(dictionary)s count]]"%params)
										
										objcclass.implImports.add(ObjCType(baseEntity.subType))
										
										forblock = CodeBlock("for (NSDictionary* entry in %(dictionary)s)"%params)
										forblock.appendStatement("[%(objectname)s addObject:[%(subtype)s objectWithEntry:entry]]"%params)
										
										lastBlock.extend(forblock)
										initializer = "%(objectname)s"%params
								else:
										initializer = "I dont fucking know"
						else:
								initializer = "[%(vartype)s objectWithEntry:%(initializer)s]"%params
						
						
						if not propertiesReadOnly:		
								lastBlock.appendStatement("self.%(objectname)s = %(initializer)s"%{'objectname':baseEntity.name,'initializer':initializer})
						else:	
								if vartype.isCopyable():
										attribute = "copy"
								else:	
										attribute = "retain"
										
								lastBlock.appendStatement("_%(objectname)s = [%(initializer)s %(attribute)s]"%{'objectname':baseEntity.name,'initializer':initializer,'attribute':attribute})
						
						while lastBlock and lastBlock is not self:
								lastBlock.superBlock.extend(lastBlock);
								lastBlock.superBlock.append("")
								lastBlock = lastBlock.superBlock;							
													