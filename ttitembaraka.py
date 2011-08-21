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
				self.defaultsuperclass = self.checkGlobalSetting("item_super","Default Item Super Class",None,"TTTableLinkedItem")
				super(TTItemBaraka,self).parse()
		
		def create(self):
				for entity in self.entities:
						self.classes.append(ItemClass(entity,self))				
		
		def generate(self,n=-1,header=True,source=True):
				if self.entities:
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
						
						if baseEntity.subType.lower() == "super":
								continue
						
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
				
				self.initMethod = ItemInitMethod(self,inputVariables)
				self.staticInitMethod = TTStaticInitMethod(self,inputVariables,"item")
				
			
				#add the dealloc and description methods
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))
				
				self.implementCoding()
	
	
class ItemInitMethod(InitMethod):
		def definition(self):
				definition = CodeBlock(self.fullname())
				
				if self.objcclass.supertype.name == self.objcclass.baraka.defaultsuperclass:
						ifblock = CodeBlock("if (self = [super init])")
				else:		
						superEntity = self.objcclass.baraka.getEntityWithType(self.objcclass.entity.typeBaseEntity.name)
						
						superEntityInput = superEntity.getSubEntityByName("input")
						
						inputSubEntity = self.objcclass.entity.getSubEntityByName("input")
						
						if superEntityInput and inputSubEntity.isEquivalent(superEntityInput): 								
								mClass = ItemClass(superEntity,self.objcclass.baraka)
								superCallString = mClass.initMethod.callString(self.variables)
								ifblock = CodeBlock("if (self = [super %s])"%superCallString)
						else:		
								ifblock = CodeBlock("if (self = [super init])")		
				
				outputSubEntity = self.objcclass.entity.getSubEntityByName("output")
						
				for baseEntity in outputSubEntity.baseEntities:
						if baseEntity.type == 'URL':
								keystrings = re.findall('\'(.+?)\'',baseEntity.subName)
								
								vars = []
								for keystring in keystrings:
										keysplit = re.findall(r'\w+',keystring)
										if not keysplit:
												keys = [keystring]
										else:	
												keys = [key for key in keysplit if key]
										vars.append(self.getKeyString(keys))		
								
								formatstring =re.sub('\'(.+?)\'','%@',baseEntity.subName)
								
								ifblock.append("")
								
								if vars:
										ifblock.appendStatement("NSString* shortURL = [NSString stringWithFormat:@\"%(format)s\",%(vars)s]"
															%{'format':formatstring,'vars':",".join(vars)})
								else:
										ifblock.appendStatement("NSString* shortURL = [NSString stringWithString:@\"%(format)s\"]"%{'format':formatstring})
								
								if self.objcclass.baraka.urlmacro:
										urlString = "%s(shortURL)"%self.objcclass.baraka.urlmacro
								else:
										urlString = "shortURL"
										
								ifblock.appendStatement("self.%(var)s = [NSURL URLWithString:%(url)s]"%{'var':baseEntity.name,'url':urlString})				
															
								ifblock.append("")
						else:
								keysplit = re.findall(r'\w+',baseEntity.subName)
								if not keysplit:
										keys = [baseEntity.name]
								else:	
										keys = [key for key in keysplit if key] 
								keyjoin = self.getKeyString(keys)
								ifblock.appendStatement("self.%(var)s = %(input)s"%{'var':baseEntity.name,'input':keyjoin})
				
				
				definition.extend(ifblock)
				definition.appendStatement("return self")
				return definition
				
		def getKeyString(self,keys):
				keyString = keys[0]
				for key in keys[1:]:
						if key.isdigit():
								keyString = "["+keyString+" objectAtIndex:"+key+"]"
						else:	
								keyString = "["+keyString+" "+key+"]"
				return keyString		 			
										
				
				
								