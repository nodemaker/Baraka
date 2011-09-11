#!/usr/bin/env python
# encoding: utf-8
# Created by Sumeru Chatterjee by writing some motherfucking code!


import sys,string,pdb,re,os,imp, pickle

from objc import *
from ttbaraka import *
from baraka import *
from code import *
from ttobjectbaraka import *

class TTModelBaraka(TTBaraka):
		
		def __init__(self,fileName):
				super(TTModelBaraka,self).__init__(fileName,["model"],["input","output","url","paging","filter","response"])
				
		def parse(self):
				self.dirname = self.checkGlobalSetting("model_dir","Model objects destination Directory",None,"DataModels")
				self.defaultsuperclass = self.checkGlobalSetting("model_super","Default Model Super Class",None,"TTURLRequestModel")
				super(TTModelBaraka,self).parse()
				
		def create(self):
				for entity in self.entities:
					self.classes.append(ModelClass(entity,self))	
		
		def generate(self,n=-1,header=True,source=True):
				if self.entities:
						print "\nGenerating Models from file %s...\n"%self.fileName
						super(TTModelBaraka,self).generate(n,header,source)	



class ModelClass(ObjCClass):

		def __init__(self,modelEntity,baraka):
				add_base_type("TTURLRequestCachePolicy")
				
				self.modelEntity = modelEntity
				super(ModelClass,self).__init__(modelEntity,baraka)
				
				inputVariables = []
				inputSubEntity = self.entity.getSubEntityByName("input")
				
				#add the input variables from the input subentity
				for baseEntity in inputSubEntity.baseEntities:
						inputtype = ObjCType(baseEntity.type)
						
						if not inputtype.isBaseType():
							self.headerImports.add(inputtype)
				
						variable = ObjCVar(baseEntity.type,baseEntity.name)
												
						attributes = ["nonatomic"]
						if variable.type.isCopyable():
								attributes.append("copy")
						else:	
								attributes.append("retain")
						
						inputVariables.append(variable)
						self.addInstanceVariable(variable,True,attributes)
				
				#add the instance variables from the output subentity
				outputSubEntity = self.entity.getSubEntityByName("output")
				
				for baseEntity in outputSubEntity.baseEntities:
						variable = ObjCVar(baseEntity.type,baseEntity.name)
						attributes = ["nonatomic","readonly"]
						self.addInstanceVariable(variable,True,attributes)
			
				#add the init methods from the input subentity
				self.initMethod = InitMethod(self,inputVariables)
				
				#add the modelLoadMoreMethod
				self.addMethod(ModelLoadMoreMethod(self))
				
				#add the modelDidFinishLoad method
				self.addMethod(ModelDidFinishLoadMethod(self))
				
				#add the dealloc and description methods
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))
										
		def isOutputInFilters(self,outputname):
				for filter in self.model.filters:
						if filter.name == outputname:
								return True;
				return False;

class ModelLoadMoreMethod(ObjCMethod):
		
		def __init__(self,modelclass):
				super(ModelLoadMoreMethod,self).__init__(modelclass,"None",[ObjCVar("TTURLRequestCachePolicy","cachePolicy"),ObjCVar("BOOL","more")],"load:more:")		
		
		def declaration(self):
				return None;
		
		def definition(self):
				definition = super(ModelLoadMoreMethod,self).definition()
				
				urlSubEntity = self.objcclass.entity.getSubEntityByName("url")
				
				urlBaseEntity = urlSubEntity.baseEntities[0]
				
				keystrings = re.findall('\'(.+?)\'',urlBaseEntity.type)
				
				vars = []
				conditions = []
				
				for keystring in keystrings:
						keysplit = re.findall(r'\w+',keystring)
						
						vars.append(keysplit[0])
						
						if len(keysplit)>1:
							default = "@\"%s\""%keysplit[1]
						else:
							default = "nil"	
						
						definition.appendStatement("NSString* %(var)s = TTIsStringWithAnyText(self.%(var)s)?self.%(var)s:%(default)s"%{'var':keysplit[0],'default':default})
						
						definition.append("")
						
						conditions.append("TTIsStringWithAnyText(%s)"%keysplit[0])
		
				if conditions:		
						urlblock = CodeBlock ("if(%s)"%"&&".join(conditions))
				else:
						urlblock = definition				
																
				formatstring =re.sub('\'(.+?)\'','%@',urlBaseEntity.type)
				
				if vars:
						urlblock.appendStatement("NSString* shortURL = [NSString stringWithFormat:@\"%(format)s\",%(vars)s]"
															%{'format':formatstring,'vars':",".join(vars)})
				else:
						urlblock.appendStatement("NSString* shortURL = [NSString stringWithString:@\"%(format)s\"]"%{'format':formatstring})											
															
				urlblock.appendStatement("NSString* url = !more?%s(shortURL):URLEscapeString(self.nextURL)"%self.objcclass.baraka.urlmacro)	
				
				responseSubEntity = self.objcclass.entity.getSubEntityByName("response")
				if responseSubEntity.baseEntities:
						responseType = responseSubEntity.baseEntities[0].type;
						urlblock.appendStatement("[super loadJSON:TTURLRequestCachePolicyNoCache more:more url:url response:[%s class]]"%responseType)
						self.objcclass.implImports.add(ObjCType(responseType))
				else:
						urlblock.appendStatement("[super loadJSON:TTURLRequestCachePolicyNoCache more:more url:url]")
				
				if not urlblock is definition:
						definition.extend(urlblock)
				
				return definition		

class ModelDidFinishLoadMethod(ObjCMethod):				
				
		def __init__(self,modelclass):
				self.modelclass = modelclass
				super(ModelDidFinishLoadMethod,self).__init__(modelclass,"None",[ObjCVar("Dictionary","result")],"requestDidFinishLoadJSON:")
		
		def declaration(self):
				return None;
		
		def definition(self):
				definition = super(ModelDidFinishLoadMethod,self).definition()
				
				outputSubEntity = self.objcclass.entity.getSubEntityByName("output")
				
				outputs = []
				
				for baseEntity in outputSubEntity.baseEntities:
						variable = ObjCVar(baseEntity.type,baseEntity.name,True)
						definition.appendStatement("TT_RELEASE_SAFELY(%s)"%variable.ivarname())
						outputs.append(variable)
						
				outputSubEntity = self.objcclass.entity.getSubEntityByName("output")
				baseEntities = outputSubEntity.baseEntities		
				
				pagingSubEntity = self.objcclass.entity.getSubEntityByName("paging")
				if pagingSubEntity.baseEntities:
						baseEntities.extend(pagingSubEntity.baseEntities)
						
				initializationBlock = DictionaryInitializationBlock(self.objcclass,baseEntities,"if(result)","result",definition,True)
				definition.extend(initializationBlock)	
				
				definition.append("")
				
				definition.appendStatement("[super requestDidFinishLoadJSON:result]")
				return definition					
						
				
						
				

							