from FileGen import *

ObjC_Classes = {'String':'NSString',
				'Number':'NSNumber',
				'Date':'NSDate',
				'Object':'NSObject',
				'Array' :'NSArray',
				}


class ObjCClass(object):
	
		def __init__(self,classname,superclassname):
				self.name = classname
				self.supername = superclassname
				self.variables = []
				self.properties = []
				self.methods = []
				
		def addInstanceVariable(self,objcvar,isProperty=True,attributes=None):
				self.variables.append(objcvar)
				
				if(isProperty):
					self.addProperty(ObjCProperty(attributes,objcvar))
					
		def addProperty(self,property):
		
				self.properties.append(property)
				
				
		def addMethod(method):
		
				self.methods.append(method)					


class ObjCVar(object):
		
		def __init__(self,type,name):
				self.type = type
				self.name = name
		
				
		def isBaseType(self):
				if self.type in ObjC_Classes:
						return True
 				else:
						return False			
		
		def objCType(self):
				if self.isBaseType():
						return ObjC_Classes[self.type]
				else:
						return self.type
		
		def ivarname(self):
				return "_"+self.name
		
		def ivarString(self):
				return self.objCType() + "* "+ self.ivarname() 
				
		def synthesizerString(self):
				 return "@synthesize "+self.name()+" = "+self.ivarname()  


class ObjCProperty(object):
		def __init__(self,attributes,objcvar):
				self.attributes = attributes
				self.name = objcvar.name
				self.type = objcvar.objCType()		
		
		def declaration(self):
				return  "@property(" + String.join(attributes,",") + ")" + self.type + "* " + self.name  				


class ObjCMethod (object):
	
		def __init__(self):
				self.name="method"
				


class ObjCFileGen (FileGen):
		
		def __init__(self,ojcclass,projectname):
				self.objcclass=objcclass
				self.projectname=projectname
			
		def filename(self):
				return	self.objcclass.name()+".h"
		
		def fileHeader():
				return ["//","//\t"+self.filename(),"//\t"+self.projectname+"//"];	


class ObjCHeaderFileGen (ObjCFileGen):

				
		def interface():
				interface = ["@interface "+objcclass.name()+" : "+objcclass.supername() + " {",""]
					
				for variable in objcclass.variables:
					interface.append(variable.ivarString())
					
				interface.append("")
				interface.append("}")
				interface.append("")
				
				for property in objcclass.properties():
					interface.append(property.declaration())
					
				for method in objcclass.methods():
					interface.append(method.declaration())	
					
				interface.extend(["","@end"])
				
				return interface					
		
		def lines(self):
				lines = self.fileHeader()
				lines.extend(self.interface())
				
				return lines
			
									
		def printout(self):
				print String.join(self.lines,"\n")


class ObjCImplFileGen (FileGen):
		
		def implementation(self):
			return "blah - blah"		
		
		def lines(self):
				lines = self.fileHeader()
				lines.extend(self.implementation)
				
				return lines
		
		def printout(self):
			print String.join(self.lines,"\n")		
				
		

