import sys,string,pdb,re,os,imp, pickle

from ttmodelobjectbarak import BaseObject
from objcbarak import *

class ModelClass(ObjCClass):

		def __init__(self,model,parser):
				
				self.parser = parser
				self.model = model
				super(ModelClass,self).__init__(model.name,model.type)
				
				for input in model.inputs:
						if input.type == "CustomURL":
								for variablename in input.get_variables():
										variable = ObjCVar('String',variablename)
									
								attributes = ["nonatomic"]
								if variable.type.objCType() is 'NSString' or variable.type.objCType() is 'NSDate':
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
				self.addMethod(DescriptionMethod(self))			
						
		def isOutputInFilters(self,outputname):
				for filter in self.model.filters:
						if filter.name == outputname:
								return True;
				return False;
		
				
							

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
				
						
				
						
				

							