#!/usr/bin/env python
# encoding: utf-8
# Created by Sumeru Chatterjee by copying stuff from TTObjectBaraka lol!

import sys,string,pdb,re,os,imp, pickle

from objc import *
from ttbaraka import *
from baraka import *
from code import *

class TTItemBaraka(TTBaraka):
		
		def __init__(self,fileName):
				super(TTItemBaraka,self).__init__(fileName,["item"],["input","output"])
		
		def parse(self):
				self.dirname = self.checkGlobalSetting("item_dir","Items Destination directory",None,"TableItems")
				self.defaultsuperclass = self.checkGlobalSetting("default_item_super","Default Item Super Class",None,"TTTableLinkedItem")
				super(TTItemBaraka,self).parse()
		
		def create(self):
				for entity in self.entities:
						self.classes.append(ItemClass(entity,self))				
		
		def generate(self,n=-1,header=True,source=True):
				print "\nGenerating Table Items from file %s...\n"%self.fileName
				super(TTItemBaraka,self).generate(n,header,source)		
				

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
						inputtype = ObjCType(baseEntity.type)
						
						if not inputtype.isBaseType():
							self.headerImports.add(inputtype)
						
						inputVariables.append(ObjCVar(baseEntity.type,baseEntity.name))
				
				self.initMethod = InitMethod(self,inputVariables)
				self.staticInitMethod = StaticInitMethod(self,inputVariables,"item",self.initMethod)
				
				#add the secondary init method and static init method
				secondaryInitMethod = InitMethod(self,self.variables)
				self.addMethod(StaticInitMethod(self,self.variables,"item",secondaryInitMethod))
				self.addMethod(secondaryInitMethod)
				
				
				#add the dealloc and description methods
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))
				
				self.implementCoding()
	
	
class ItemInitMethod(InitMethod):
		def definition(self):
				definition = (ItemInitMethod,self).definition()
				return definition
										
				
				
								