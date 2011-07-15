import string,re, pdb
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
				
Mutable_Classes = {'NSDictionary':'NSMutableDictionary',
				   'NSArray':'NSMutableArray',
				   'NSString':'NSMutableString',
				   'NSSet':'NSMutableSet',
				  }				  				
BaseTypes = ['Generic','None','BOOL']

def add_base_type(type):
		global BaseTypes
		BaseTypes.append(type)


class ObjCType (object):

		def __init__(self,typename,mutable=False):
				self.name=typename
				self.mutable = mutable
			
		def isBaseType(self):
				if self.name in ObjC_Classes:
						return True
 				else:
						return False			
		
		def objCType(self,mute=True):
				if self.isBaseType():
						if not self.mutable or not mute:
								return ObjC_Classes[self.name]
						elif ObjC_Classes[self.name] in Mutable_Classes:
								return Mutable_Classes[ObjC_Classes[self.name]]
						else:
								return ObjC_Classes[self.name]
								print "\nWARNING:Type '%s' has no Objective C Mutable class"%self.name				
				else:
						return self.name
						
		def objCPointer(self):
				if self.name not in BaseTypes:
						return self.objCType()+"*"
				else:					
						return self.objCType()
					
		def description(self):
				if self.mutable:
						return self.name + " (mutable)"		
				else:
						return self.name
class ObjCVar(object):
		
		def __init__(self,type,name,mutable=False):
				self.type = ObjCType(type,mutable)
				self.name = name
		
		def ivarname(self):
				return "_"+self.name
		
		def ivarString(self):
				return self.type.objCType() + "* "+ self.ivarname() 
				
		def synthesizerString(self):
				return "@synthesize "+self.name()+" = "+self.ivarname() 
				 
		def description(self):
				return self.type.description() + "  "+self.name			  	


class ObjCProperty(object):
		def __init__(self,attributes,objcvar):
				self.attributes = attributes
				self.objcvar = objcvar		
		
		def declaration(self):
				if "readonly" in self.attributes:
						return  "@property(" + string.join(self.attributes,",") + ") " + self.objcvar.type.objCType(False) + "* " + self.objcvar.name+";" 
				else:
						return  "@property(" + string.join(self.attributes,",") + ") " + self.objcvar.type.objCType() + "* " + self.objcvar.name+";" 
				
		def synthesizer (self):
				return  "@synthesize "+self.objcvar.name+"="+self.objcvar.ivarname()+";"		 				

class ObjCMethodType:
		staticMethod=1
		instanceMethod=2

class ObjCMethod (object):
	
		def __init__(self,objcclass,returnType,variables,methodname,methodType=ObjCMethodType.instanceMethod):
				self.name=methodname
				self.returnType=ObjCType(returnType)
				self.variables=variables
				self.objcclass=objcclass
				self.methodType = methodType
		
		def callString(self,variablenames):
				if not variablenames:
						return self.name
				else:		
						methodparts = re.findall(r'.+?:',self.name)
						if not methodparts:
								fullname = self.name
						else:
							fullname = ""		
							variable_index=0
							for part in methodparts:
								if variable_index>len(variablenames)-1:
									break
								variablename = variablenames[variable_index]
								if(variable_index>0):
									fullname+=" "
								fullname+= part+ variablename
								variable_index = variable_index+1
						return fullname				
								
								
		def fullname(self):
				if not self.variables:
						fullname = self.name
				else:
						methodparts = re.findall(r'.+?:',self.name)
						if not methodparts:
								fullname = self.name
						else:
							fullname = ""		
							variable_index=0
							for part in methodparts:
								if variable_index>len(self.variables)-1:
									break
								variable = self.variables[variable_index]
								fullname+= part+"("+variable.type.objCPointer()+")"+variable.name+" "
								variable_index = variable_index+1
				return fullname				
		
		def methodTypeIdentifier(self):
				if self.methodType is ObjCMethodType.instanceMethod:
					return "-"
				else:
					return "+"
				
		def declaration (self):
				return self.methodTypeIdentifier() +"("+self.returnType.objCPointer()+") "+self.fullname()+";"
		
		def definition	(self):	
				definition = CodeBlock(self.methodTypeIdentifier()+"("+self.returnType.objCPointer()+") "+self.fullname())
				return definition
				
		def description (self):
				description = CodeList()
				description.extend(["Objective C Method","-----------------"])
				description.indent()
				description.append("Name: "+self.name)
				description.append("ReturnType" + self.returnType.description())
				if self.methodType == ObjCMethodType.staticMethod:
					description.append("Type : static");
				else:
					description.append("Type:  instance");
				description.append("Variables:")
				description.indent()
				
				for variable in self.variables:
					description.append(variable.description())
					
				return ("\n").join(description)					
				
class InitMethod (ObjCMethod):
		def __init__(self,objcclass,variables=[],methodname="init"):
				
				if methodname == "init":
					if(len(variables)>0):
							methodname+="With"
					for variable in variables:
							methodname+=firstuppercase(variable.name)+":"	
							
				super(InitMethod,self).__init__(objcclass,"Generic",variables,methodname)
				
		def definition(self):	
				definition = super(InitMethod,self).definition()		
				ifblock = CodeBlock("if (self = [super init])")
				
				for variable in self.variables:
						ifblock.appendStatement("self.%(var)s = %(var)s"%{'var':variable.name})				
				definition.extend(ifblock)
				return definition

class DeallocMethod (ObjCMethod):

		def __init__(self,objcclass):
				super(DeallocMethod,self).__init__(objcclass,"None",[],"dealloc")
				
		def definition(self):
				definition = CodeBlock("-("+self.returnType.objCPointer()+") "+self.fullname())
				
				for variable in self.objcclass.variables:
						definition.appendStatement("TT_RELEASE_SAFELY(%s)"%variable.ivarname())
				definition.extend(["","[super dealloc];"])

				return definition
		
		def declaration (self):
				return None				

class DescriptionMethod(ObjCMethod):
		
		def __init__(self,modelclass):
				super(DescriptionMethod,self).__init__(modelclass,"String",[],"description")					
				
		def definition(self):
				definition = super(DescriptionMethod,self).definition()
				descriptionString = "[NSString stringWithFormat:@\"\\n"
			
				for variable in self.objcclass.variables:
						descriptionString += variable.name+" - %@\\n"
				
				descriptionString += "\""
				
				for variable in self.objcclass.variables:
						descriptionString += "," +variable.ivarname()
				
				
				descriptionString += "]"
			
				definition.appendStatement("return "+descriptionString)
				return definition
		
		def declaration(self):
				return None

class ObjCClass(object):
	
		def __init__(self,classname,superclassname="Object"):
				self.name = classname
				self.supertype = ObjCType(superclassname)
				self.variables = []
				self.properties = []
				self.methods = []
				
				self.implImports = set([ObjCType(self.name)])
				self.headerImports = set()
				if not self.supertype.isBaseType():
						self.headerImports.add(self.supertype)
						
		def addInstanceVariable(self,objcvar,isProperty=True,attributes=None):
				self.variables.append(objcvar)
				
				if(isProperty):
					self.addProperty(ObjCProperty(attributes,objcvar))
				
				if not objcvar.type.isBaseType():
					self.headerImports.add(objcvar.type) 
					
		def addProperty(self,property):
		
				self.properties.append(property)
				
				
		def addMethod(self,method):
		
				self.methods.append(method)			
				
		def headerfilename(self):
				return	self.name+".h"
				
		def implfilename(self):
				return	self.name+".m"
				
		def callStaticMethodString(self,method,variables):
				return "[%(class)s %(method)s]"%{'class':self.name,'method':method.callString(variables)}									

class ObjCFile (File):
		
		def __init__(self,objcclass,projectname):
				self.objcclass=objcclass
				self.projectname=projectname	
		
		def fileHeader(self):
				return ["//","//\t"+self.filename(),"//\t"+self.projectname,"//"]	
					

class ObjCHeaderFile (ObjCFile):

				
		def interface(self):
				interface = CodeList()
				
				interface.extend(["@interface "+self.objcclass.name+" : "+self.objcclass.supertype.objCType() + " {",""])
					
				interface.indent()	
					
				for variable in self.objcclass.variables:
					interface.append(variable.ivarString()+";")
					
				interface.dedent()
					
				interface.append("}")
				interface.append("")
				
				for property in self.objcclass.properties:
					interface.append(property.declaration())
				
				interface.append("")
				
				for method in self.objcclass.methods:			
					interface.extend(["",method.declaration()])	
					
				interface.extend(["@end"])
				
				return interface
				
		def imports(self):
				imports = set()
				
				for importType in self.objcclass.headerImports:
					imports.add("#import \"%s.h\""%importType.objCType())
				
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
				
				for method in self.objcclass.methods:
					implementation.extend(["",divider])			
					implementation.extend(method.definition())	
				
				implementation.append ("@end")	
				return implementation
				
		def lines(self):
				lines = CodeList()
				
				implementation = self.implementation()
				
				lines = self.fileHeader()
				lines.append("")
				lines.extend(self.imports())		
				lines.append("")
				lines.extend([divider,divider,divider])
				lines.extend(implementation)
				
				return lines
		
		def imports(self):
				imports = set()
				
				for importType in self.objcclass.implImports:
					imports.add("#import \"%s.h\""%importType.objCType())
				
				return imports	
					
				
		def synthesizers(self):
				
				synthesizers = CodeList()
				for property in self.objcclass.properties:
					synthesizers.append(property.synthesizer())
				
				return synthesizers	 		
		
		def filename(self):
				return self.objcclass.implfilename()
		


