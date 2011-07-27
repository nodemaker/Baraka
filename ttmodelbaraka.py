#!/usr/bin/env python
# encoding: utf-8
# Created by Sumeru Chatterjee by writing some motherfucking code!


import sys,string,pdb,re,os,imp, pickle

from objc import *
from ttbaraka import *
from baraka import *
from code import *

class TTModelBaraka(TTBaraka):
		
		def __init__(self,fileName):
				super(TTModelBaraka,self).__init__(fileName,["object"],["input","output"])
				
		def parse(self):
				self.dirname = self.checkGlobalSetting("model_dir","Model objects destination Directory",None,"DataModels")
				self.defaultsuperclass = self.checkGlobalSetting("model_super","Default Model Super Class",None,"TTURLRequestModel")
				super(TTModelBaraka,self).parse()
				
		def create(self):
				print "Cant create shit!!"
				#for entity in self.entities:
				#self.classes.append(ModelClass(entity,self))	
		
		def generate(self,n=-1,header=True,source=True):
				print "\nGenerating Models from file %s...\n"%self.fileName
				super(TTModelBaraka,self).generate(n,header,source)	



class ModelClass(ObjCClass):

		def __init__(self,model,parser):
				add_base_type("TTURLRequestCachePolicy")
				
				self.parser = parser
				self.model = model
				super(ModelClass,self).__init__(model.name,model.type)
				
				for input in model.inputs:
						if input.type == "CustomURL":
								for variablename in input.get_variables():
										variable = ObjCVar('String',variablename)
									
								attributes = ["nonatomic"]
								
								if variable.type.objCType() is 'NSString' or variable.type.objCType() is 'NSDate' or variable.type.objcType:
										attributes.append("copy")
								else:	
										attributes.append("retain")
								
								self.addInstanceVariable(variable,True,attributes)		
								
								self.addMethod(InitMethod(self,[variable]))
				
				for output in model.outputs:
						
						variable = ObjCVar(output.type,output.name,True)
										
						attributes = ["nonatomic","readonly"]
							
						self.addInstanceVariable(variable,True,attributes)
						
						if self.isOutputInFilters(output.name):
								allvariable = ObjCVar(output.type,"all"+firstuppercase(output.name),True)
								self.addInstanceVariable(allvariable,False,None)
				
				self.addMethod(DeallocMethod(self))	
				self.addMethod(ModelLoadMoreMethod(self))
				self.addMethod(ModelDidFinishLoadMethod(self))		
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
				definition.appendStatement("NSString* url = nil")
				return definition		

class ModelDidFinishLoadMethod(ObjCMethod):				
				
		def __init__(self,modelclass):
				self.modelclass = modelclass
				self.model = modelclass.model
				super(ModelDidFinishLoadMethod,self).__init__(modelclass,"None",[ObjCVar("Dictionary","result")],"requestDidFinishLoadJSON:")
		
		def declaration(self):
				return None;
		
		def definition(self):
				definition = super(ModelDidFinishLoadMethod,self).definition()
				for output in self.model.outputs:
						variable = ObjCVar(output.type,output.name,True)
						definition.appendStatement("TT_RELEASE_SAFELY(%s)"%variable.ivarname())
						
						'''
						if not ObjCType(output.type).isBaseType():
								modelobject = self.modelclass.parser.getModelObjectWithModelObjectName(output.type)
								objClass = ModelObjectClass(modelobject,self.modelclass.parser)
								callInitMethodString = objClass.callStaticMethodString(objClass.primaryInitMethod,["result"])
								definition.appendStatement("%(ivar)s=[%(methodcall)s retain]"%{'ivar':variable.ivarname(),'methodcall':callInitMethodString})
						elif output.type == "Dictionary":
								callInitMethodString = "[NSDictionary dictionaryWithDictionary:result]"
								definition.appendStatement("%(ivar)s=[%(methodcall)s retain]"%{'ivar':variable.ivarname(),'methodcall':callInitMethodString})
						elif output.type == "Array":
								initializationBlock = SubObjectInitializationBlock(self.objcclass,[output],"if(result)","result",definition)
								definition.extend(initializationBlock)	
						'''
				initializationBlock = SubObjectInitializationBlock(self.objcclass,self.model.outputs,"if(result)","result",definition)
				definition.extend(initializationBlock)	
				
						#definition.append("")
				
				
				definition.appendStatement("[super requestDidFinishLoadJSON:result]")
				return definition			
				
class Model(object):
	
		def __init__(self,modelname,modelsuper):
				self.name = modelname
				self.type = modelsuper
				self.outputs = []
				self.inputs = []
				self.filters = [] 
				
		def description(self):
				description = "<Model>" + " " + self.name +" Type:"+ self.type
				
				if(len(self.inputs)>0):
						description += "\n\t<Input>"
				
				for input in self.inputs:
						description += "\n\t\t"+input.description()
				
				if(len(self.outputs)>0):
						description += "\n\t<Output>"		
						
				for output in self.outputs:
						description += "\n\t\t"+output.description()
						
				
				if(len(self.filters)>0):
						description += "\n\t<Filter>"		
								
						
				for filter in self.filters:
						description += "\n\t\t"+filter.description()
				return description				
									
				
class ModelInput(object):
		
		def __init__(self,inputtype,inputstring):
				self.type = inputtype
				self.string = inputstring
				
		def description(self):
				return "<%(inputtype)s> %(inputstring)s"%{'inputtype':self.type,'inputstring':self.string}
				
		def get_variables(self):
				if not self.type == "CustomURL":
						return []
				
				return re.findall(r'\'(\w+)\'',self.string)
				
						
				
						
				

							