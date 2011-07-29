import string,re, pdb

from baraka import *
from file import *

#TODO: Store a list of all defined classes and their primary init methods.In fact have a default list already.This list would be very useful

ObjC_Classes = {'Dictionary':'NSDictionary',
				'String':'NSString',
				'Number':'NSNumber',
				'Date':'NSDate',
				'Object':'NSObject',
				'URL':'NSURL',
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

ObjC_InitMethods = {
					'Dictionary':'dictionaryWithDictionary:',
					'Array':'arrayWithCapacity:',
					'Number':'numberWithInt',
					'Date':'dateWithString',
					'URL':'urlWithString',
				   }


def add_base_type(type):
		global BaseTypes
		BaseTypes.append(type)

class ObjCClass(object):
	
		def __init__(self,entity,baraka):
				self.entity = entity
				self.baraka = baraka
			
				self.name = entity.typeBaseEntity.type
				if entity.typeBaseEntity.name:
					self.supertype = ObjCType(entity.typeBaseEntity.name)
				elif baraka.defaultsuperclass:
					self.supertype = ObjCType(baraka.defaultsuperclass)
				else:
					self.supertype = ObjCType("Object")	
						
				self.variables = []
				self.properties = []
				self.staticInitMethod = None
				self.initMethod = None
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
					
		def implementCoding(self):
				self.addMethod(CodingDecodeMethod(self))
				self.addMethod(CodingEncodeMethod(self))			
					
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
				
		def allMethods(self):
				allMethods = []
				
				if self.staticInitMethod:
					allMethods.append(self.staticInitMethod)	
				
				if self.initMethod:
					allMethods.append(self.initMethod)			
				
				allMethods.extend(self.methods)
				
				return allMethods

class ObjCType (object):

		def __init__(self,typename,mutable=False):
				if not typename:
					typename = "Object"
				
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
						
		def isCopyable(self):
				if self.objCType() in ['NSString','NSDate','NSURL']:
						return True
				else:
						return False			
							
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
				self.name=self.createMethodName(methodname,variables)
				self.returnType=ObjCType(returnType)
				self.variables=variables
				self.objcclass=objcclass
				self.methodType = methodType
				
		def createMethodName(self,methodname,variables):
				
				if(len(variables)>0):
						methodname+="With"
				for index,variable in enumerate(variables):
						if index is 0:
								methodname+=firstuppercase(variable.name)+":"
						else:
								methodname+=variable.name+":"
				return methodname
										
		
		def callString(self,variables):
				if not variables:
						return self.name
				else:		
						methodparts = re.findall(r'.+?:',self.name)
						if not methodparts:
								fullname = self.name
						else:
							fullname = ""		
							variable_index=0
							for part in methodparts:
								if variable_index>len(variables)-1:
									break
								variable = variables[variable_index]
								if(variable_index>0):
									fullname+=" "
								fullname+= part+ variable.name
								variable_index = variable_index+1
						return fullname				
								
								
		def fullname(self):
				prefix = self.methodTypeIdentifier() +"("+self.returnType.objCPointer()+") "
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
								fullname+= part+"("+variable.type.objCPointer()+")"+variable.name
								
								if not variable_index == len(self.variables)-1:
										fullname+=" "
								
								variable_index = variable_index+1
				return prefix + fullname				
		
		def methodTypeIdentifier(self):
				if self.methodType is ObjCMethodType.instanceMethod:
					return "-"
				else:
					return "+"
				
		def declaration (self):
				return self.fullname()+";"
		
		def definition	(self):	
				definition = CodeBlock(self.fullname())
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
				
class InitMethod(ObjCMethod):
		def __init__(self,objcclass,variables=[],methodname="init"):
				super(InitMethod,self).__init__(objcclass,"Generic",variables,methodname)
				
		def definition(self):	
				definition = super(InitMethod,self).definition()		
				ifblock = CodeBlock("if (self = [super init])")
				
				for variable in self.variables:
						ifblock.appendStatement("self.%(var)s = %(var)s"%{'var':variable.name})				
				definition.extend(ifblock)
				definition.appendStatement("return self")
				return definition

class CodingDecodeMethod(ObjCMethod):
		def __init__(self,objcclass):
				variables = [ObjCVar("NSCoder","decoder")]
				methodname = "init"
				super(CodingDecodeMethod,self).__init__(objcclass,"Generic",variables,methodname)
		
		def createMethodName(self,methodname,variables):
				return methodname + "WithCoder:"
				
		def definition(self):	
				definition = super(CodingDecodeMethod,self).definition()		
				ifblock = CodeBlock("if (self = [super initWithCoder:decoder])")
							
				for variable in self.objcclass.variables:
						ifblock.appendStatement("self.%(var)s = [decoder decodeObjectForKey:@\"%(var)s\"]"%{'var':variable.name})				
				definition.extend(ifblock)
				definition.appendStatement("return self")
				return definition
				
		def declaration (self):
				return None	
				
class CodingEncodeMethod(ObjCMethod):
		def __init__(self,objcclass):
				variables = [ObjCVar("NSCoder","encoder")]
				methodname = "enocde"
				super(CodingEncodeMethod,self).__init__(objcclass,"None",variables,methodname)
		
		def createMethodName(self,methodname,variables):
				return methodname + "WithCoder:"
				
		def definition(self):	
				definition = super(CodingEncodeMethod,self).definition()		
				
				definition.appendStatement("[super encodeWithCoder:encoder]")
				
				definition.append("")
							
				for variable in self.objcclass.variables:
						ifblock = CodeBlock("if (self.%s)"%variable.name)
						ifblock.appendStatement("[encoder encodeObject:self.%(var)s forKey:@\"%(var)s\"]"%{'var':variable.name})
						definition.extend(ifblock)
				
				return definition	
												
		def declaration (self):
				return None	

class StaticInitMethod(ObjCMethod):
		
		def __init__(self,objcclass,variables=[],methodname="object",initMethod = None):
				if not initMethod:
						self.initMethod = objcclass.initMethod
				else:
						self.initMethod = initMethod		
				super(StaticInitMethod,self).__init__(objcclass,"Generic",variables,methodname,ObjCMethodType.staticMethod)
				
		def definition(self):
				definition = super(StaticInitMethod,self).definition()
				if self.initMethod:
						methodCall = self.initMethod.callString(self.variables)
						definition.appendStatement("return [[[self alloc] %s] autorelease]"%methodCall)
				return definition

class DeallocMethod (ObjCMethod):

		def __init__(self,objcclass):
				super(DeallocMethod,self).__init__(objcclass,"None",[],"dealloc")
				
		def definition(self):
				definition = CodeBlock(self.fullname())
				
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
							

class ObjCFile (File):
		
		def __init__(self,objcclass,projectname,hackername="Baraka"):
				self.objcclass=objcclass
				self.projectname=projectname
				self.hackername = hackername	
		
		def fileHeader(self):
				return ["//","//\t"+self.filename(),"//\t"+self.projectname,"//","//\tCreated by "+self.hackername,"//"]	
					

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
				
				for method in self.objcclass.allMethods():			
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
								
				for method in self.objcclass.allMethods():
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