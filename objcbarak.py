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
				'None': 'void',
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
				if self.name is not 'Generic' and self.name is not 'None':
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
				self.objcvar = objcvar		
		
		def declaration(self):
				return  "@property(" + string.join(self.attributes,",") + ") " + self.objcvar.type.objCType() + "* " + self.objcvar.name+";" 
				
		def synthesizer (self):
				return  "@synthesize "+self.objcvar.name+"="+self.objcvar.ivarname()+";"		 				


class ObjCMethod (object):
	
		def __init__(self,objcclass,returnType,variables,methodname):
				self.name=methodname
				self.returnType=ObjCType(returnType)
				self.variables=variables
				self.objcclass=objcclass
		
		def fullname(self):
				if not self.variables:
						fullname = self.name
				else:
						methodparts = re.findall(r'.+:',self.name)
						if not methodparts:
								fullname = self.name
						else:
							fullname = ""		
							variable_index=0
							for part in methodparts:
								variable = self.variables[variable_index]
								fullname+= part+"("+variable.type.objCPointer()+")"+variable.name
								
				return fullname				
				
		def declaration (self):
				return "-("+self.returnType.objCPointer()+") "+self.fullname()+";"
		
		def definition	(self):	
				definition = CodeList() 
				definition.append("-("+self.returnType.objCPointer()+") "+self.fullname()+" {")
				definition.indent()
				definition.extend(self.methodBody())
				definition.dedent()
				definition.append("}")
				return definition
				
		def methodBody (self):
				return []		
				

class InitMethod (ObjCMethod):
		
		def __init__(self,objcclass,variables=[],methodname="init"):
				super(InitMethod,self).__init__(objcclass,"Generic",variables,methodname)	

class DeallocMethod (ObjCMethod):

		def __init__(self,objcclass):
				super(DeallocMethod,self).__init__(objcclass,"None",[],"dealloc")
				
		def methodBody(self):
				methodBody = CodeList()
				methodBody.extend(["","[super dealloc]",""])
				
				return methodBody
						


class ObjCClass(object):
	
		def __init__(self,classname,superclassname="Object"):
				self.name = classname
				self.supertype = ObjCType(superclassname)
				self.variables = []
				self.properties = []
				self.methods = []
				self.initMethod = InitMethod(self)
				
		def addInstanceVariable(self,objcvar,isProperty=True,attributes=None):
				self.variables.append(objcvar)
				
				if(isProperty):
					self.addProperty(ObjCProperty(attributes,objcvar))
					
		def addProperty(self,property):
		
				self.properties.append(property)
				
				
		def addMethod(self,method):
		
				self.methods.append(method)			
				
		def headerfilename(self):
				return	self.name+".h"
				
		def implfilename(self):
				return	self.name+".m"							

class ObjCFile (File):
		
		def __init__(self,objcclass,projectname):
				self.objcclass=objcclass
				self.projectname=projectname	
		
		def fileHeader(self):
				return ["//","//\t"+self.filename(),"//\t"+self.projectname,"//"]	
		
		def printout(self):
				print "\n\n\nFile:"+self.filename()
				print "--------------------"
				print "\n".join(["%s" % (line) for line in self.lines()])			


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
				
				interface.append(self.objcclass.initMethod.declaration())
																				
				for method in self.objcclass.methods:			
					interface.extend(["",method.declaration()])	
					
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
		
		def filename(self):
			return self.objcclass.headerfilename()


class ObjCImplFile(ObjCFile):
		
		def implementation(self):
				implementation = CodeList()
				implementation.append ("@implementation "+self.objcclass.name)
				implementation.append ("")
				implementation.extend (self.synthesizers())
				implementation.extend (["",divider])
				implementation.extend (self.objcclass.initMethod.definition())
				implementation.extend (["",divider])
				implementation.extend (self.objcclass.deallocMethod.definition())
				
				for method in self.objcclass.methods:
					implementation.extend(["",divider])			
					implementation.extend(method.definition())	
				
				implementation.append ("@end")	
				return implementation
				
		def lines(self):
				lines = CodeList()
				
				lines = self.fileHeader()
				lines.append("")
				lines.extend(self.imports())		
				lines.append("")
				lines.extend([divider,divider,divider])
				lines.extend(self.implementation())
				
				return lines
		
		def imports(self):
				imports = set()
				
				imports.add("#import \""+self.objcclass.headerfilename()+"\"") 
								
				return imports
				
		def synthesizers(self):
				
				synthesizers = CodeList()
				for property in self.objcclass.properties:
					synthesizers.append(property.synthesizer())
				
				return synthesizers	 		
		
		def filename(self):
				return self.objcclass.implfilename()
		


