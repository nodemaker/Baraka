#!/usr/bin/env python
# encoding: utf-8
# Created and perfected by Sumeru Chatterjee on many long nights


import sys,string,pdb,re,os,imp, pickle

from objc import *
from ttbaraka import *
from baraka import *
from code import *

dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"

class TTObjectBaraka(TTBaraka):
		
		def __init__(self,fileName):
				super(TTObjectBaraka,self).__init__(fileName,["object"],["input","output"])
				
		def parse(self):
				self.dirname = self.checkGlobalSetting("model_object_dir","Model objects destination Directory",None,"DataObjects")
				super(TTObjectBaraka,self).parse()
				
		def create(self):
				for entity in self.entities:
						self.classes.append(ModelObjectClass(entity,self))	
		
		def generate(self,n=-1,header=True,source=True):
				print "\nGenerating Model Objects from file %s...\n"%self.fileName
				super(TTObjectBaraka,self).generate(n,header,source)	


class ModelObjectClass(ObjCClass):

		def __init__(self,objectEntity,baraka):
								
				self.objectEntity = objectEntity
				super(ModelObjectClass,self).__init__(objectEntity,baraka)
				
				#add the instance variables from the output subentity
				outputSubEntity = self.entity.getSubEntityByName("output")
				
				for baseEntity in outputSubEntity.baseEntities:
						variable = ObjCVar(baseEntity.type,baseEntity.name)
						attributes = ["nonatomic"]
						if variable.type.isCopyable():
								attributes.append("copy")
						else:	
								attributes.append("retain")
							
						self.addInstanceVariable(variable,True,attributes)
				
				
				#add the init methods from the input subentity
				inputVariables = []
				inputSubEntity = self.entity.getSubEntityByName("input")
				
				for baseEntity in inputSubEntity.baseEntities:
				
						inputtype = ObjCType(baseEntity.type)
						
						if not inputtype.isBaseType():
							self.headerImports.add(inputtype)
				
						inputVariables.append(ObjCVar(baseEntity.type,baseEntity.name))
				
				self.staticInitMethod = TTStaticInitMethod(self,inputVariables)
				self.initMethod = DictionaryInitMethod(self,inputVariables)
				
				#add the dealloc and description methods
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))

						
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
										
										objcclass.implImports.add(ObjCType(baseEntity.subType))
										
										forblock = CodeBlock("for (NSDictionary* entry in %(dictionary)s)"%params)
										forblock.appendStatement("[%(objectname)s addObject:[[[%(subtype)s alloc] initWithEntry:entry] autorelease]]"%params)
										
										lastBlock.extend(forblock)
										lastBlock.appendStatement("self.%(objectname)s = %(objectname)s"%params)
								else:
										lastBlock.append("I dont fucking know")
						else:
								lastBlock.appendStatement("self."+baseEntity.name+" = [[["+vartype.objCType()+" alloc] initWithEntry:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]] autorelease]")
						while lastBlock and lastBlock is not self:
								lastBlock.superBlock.extend(lastBlock);
								lastBlock.superBlock.append("")
								lastBlock = lastBlock.superBlock;							
