import string,re
from filebarak import *

ObjC_Classes = {'Dictionary':'NSDictionary',
				'String':'NSString',
				'Number':'NSNumber',
				'Date':'NSDate',
				'Object':'NSObject',
				'Array' :'NSArray',
				'Object':'NSObject',
				'Generic':'id',
				}
				
class ObjCType (object):

		def __init__(self,typename):
			self.name=typename
			
			
		def isBaseType(self):
				if self.name in ObjC_Classes:
						return True
 				else:
						return False			
		
		def objCType(self):
				if self.isBaseType():
						return ObjC_Classes[self.name]
				else:
						return self.name
						
		def objCPointer(self):
				if self.name is not 'Generic':
					return self.objCType()+"*"
				else:					
					return self.objCType()
					
class ObjCVar(object):
		
		def __init__(self,type,name):
				self.type = ObjCType(type)
				self.name = name
		
		def ivarname(self):
				return "_"+self.name
		
		def ivarString(self):
				return self.type.objCType() + "* "+ self.ivarname() 
				
		def synthesizerString(self):
				 return "@synthesize "+self.name()+" = "+self.ivarname()  	


class ObjCProperty(object):
		def __init__(self,attributes,objcvar):
				self.attributes = attributes
				self.name = objcvar.name
				self.type = objcvar.type		
		
		def declaration(self):
				return  "@property(" + string.join(self.attributes,",") + ") " + self.type.objCType() + "* " + self.name+";"  				


class ObjCMethod (object):
	
		def __init__(self,returnType,variables,methodname):
				self.name=methodname
				self.returnType=ObjCType(returnType)
				self.variables=variables
				
		def declaration (self):
				declaration = "-("+self.returnType.objCType()+") "
				
				if not self.variables:
						declaration += self.name+";"
				else:
						methodparts = re.findall(r'.+:',self.name)
						if not methodparts:
								declaration += self.name+";"
						else:		
							variable_index=0
							for part in methodparts:
								variable = self.variables[variable_index]
								declaration+= part+"("+variable.type.objCPointer()+")"+variable.name+";"
				
				return declaration
				
				


class InitMethod (ObjCMethod):
		
		def __init__(self,variables=[],methodname="init"):
				super(InitMethod,self).__init__("Generic",variables,methodname)	


class ObjCClass(object):
	
		def __init__(self,classname,superclassname):
				self.name = classname
				self.supertype = ObjCType(superclassname)
				self.variables = []
				self.properties = []
				self.methods = []
				
		def addInstanceVariable(self,objcvar,isProperty=True,attributes=None):
				self.variables.append(objcvar)
				
				if(isProperty):
					self.addProperty(ObjCProperty(attributes,objcvar))
					
		def addProperty(self,property):
		
				self.properties.append(property)
				
				
		def addMethod(self,method):
		
				self.methods.append(method)					

class ObjCFile (File):
		
		def __init__(self,objcclass,projectname):
				self.objcclass=objcclass
				self.projectname=projectname
			
		def filename(self):
				return	self.objcclass.name+".h"
		
		def fileHeader(self):
				return ["//","//\t"+self.filename(),"//\t"+self.projectname,"//"]	


class ObjCHeaderFile (ObjCFile):

				
		def interface(self):
				interface = CodeList()
				
				interface.extend(["@interface "+self.objcclass.name+" : "+self.objcclass.supertype.objCType() + " {",""])
					
				interface.indent()	
					
				for variable in self.objcclass.variables:
					interface.append(variable.ivarString())
					
				interface.dedent()
					
				interface.append("}")
				interface.append("")
				
				for property in self.objcclass.properties:
					interface.append(property.declaration())
				
				interface.append("")
									
				for method in self.objcclass.methods:			
					interface.append(method.declaration())	
					
				interface.extend(["@end"])
				
				return interface
				
		def imports(self):
				imports = set()
				
				if not self.objcclass.supertype.isBaseType():
						imports.add("#import \""+self.objcclass.supertype.objCType()+".h\"") 
				
				for variable in self.objcclass.variables:
						if not variable.type.isBaseType():
								imports.add("#import \""+variable.type.objCType()+".h\"") 
								
				return imports							
									
		def lines(self):
				lines = CodeList()
				lines.extend(self.fileHeader())
				lines.append("")
				lines.extend(self.imports())
				lines.append("")
				lines.extend(self.interface())
				
				return lines
		
		def printout(self):
				print "\n\n\nFile:"+self.filename()
				print "--------------------"
				print "\n".join(["%s" % (line) for line in self.lines()])


class ObjCImplFile(File):
		
		def implementation(self):
			return "blah - blah"		
		
		def lines(self):
				lines = self.fileHeader()
				lines.extend(self.implementation)
				
				return lines
		
		def printout(self):
			print string.join(self.lines,'\n')		
		


