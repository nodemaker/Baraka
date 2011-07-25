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
				super(TTItemBaraka,self).parse()
		
		def create(self):
				for entity in self.entities:
						self.classes.append(ItemClass(entity,self))				
		
		def generate(self):
				print "\nGenerating Table Items from file %s...\n"%self.fileName
				super(TTItemBaraka,self).generate()		
				

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
								