#!/usr/bin/env python
# encoding: utf-8
# Created and perfected by Sumeru Chatterjee on many long nights


import sys,string,pdb,re,os,imp, pickle

from objc import *
from ttbaraka import *
from baraka import *
from code import *

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
				if self.entities:
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

				outputSubEntity = self.objcclass.entity.getSubEntityByName("output")
				baseEntities = outputSubEntity.baseEntities
				
				
				if self.objcclass.supertype.objCType() is "NSObject":
					initializationBlock = DictionaryInitializationBlock(self.objcclass,baseEntities,"if(self = [super init])","entry",definition)
				else:
					initializationBlock = DictionaryInitializationBlock(self.objcclass,baseEntities,"if(self = [super initWithEntry:entry])","entry",definition)
				
				definition.append("")
				definition.extend(initializationBlock)
				definition.append("")
				definition.appendStatement("return self")
				return definition	
		
