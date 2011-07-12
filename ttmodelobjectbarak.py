import sys,string,pdb,re,os,imp, pickle

dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"

from objcbarak import *

class dotdict(dict):
    	def __getattr__(self, attr):
        	return self.get(attr, None)
    	__setattr__= dict.__setitem__
    	__delattr__= dict.__delitem__


class ModelObjectClass(ObjCClass):

		def __init__(self,modelobject,parser):
				
				self.parser = parser
				self.modelobject = modelobject
				super(ModelObjectClass,self).__init__(modelobject.name,modelobject.type)
		
				for subObject in modelobject.subObjects:
						
						variable = ObjCVar(subObject.type,subObject.name)
						
						attributes = ["nonatomic"]
						
						if variable.type.objCType() is 'NSString' or variable.type.objCType() is 'NSDate':
								attributes.append("copy")
						else:	
								attributes.append("retain")
							
						self.addInstanceVariable(variable,True,attributes)
						self.addMethod(InitMethod())
				
				self.addMethod(ModelObjectStaticInitMethod(self,parser))
				self.addMethod(ModelObjectInitMethod(self))
				self.addMethod(DeallocMethod(self))
				self.addMethod(DescriptionMethod(self))
		
		def hasDateSubObject (self):
				for variable in self.variables:
						if variable.type.objCType() is "NSDate":
								return True
				return False											
	

class ModelObjectInitMethod(InitMethod):

		def __init__(self,modelclass):
				super(ModelObjectInitMethod,self).__init__(modelclass,[ObjCVar("Dictionary","entry")],"initWithDictionary:")
				
		def definition(self):
				definition = super(ModelObjectInitMethod,self).definition()
				
				definition.append("")
				
				nullcheckBlock = CodeBlock("if([entry isKindOfClass:[NSNull class]])")
				nullcheckBlock.appendStatement("return nil")
				definition.extend(nullcheckBlock)
				
				
				if self.objcclass.supertype.objCType() is "NSObject":
					initializationBlock = CodeBlock("if(self = [super init])")
				else:
					initializationBlock = CodeBlock("if(self = [super initWithDictionary:entry])")
				
				initializationBlock.append("")
				
				if self.objcclass.hasDateSubObject():
						initializationBlock.appendStatement("NSDateFormatter* dateFormatter = [[[NSDateFormatter alloc] init] autorelease]")
						initializationBlock.appendStatement("[dateFormatter setTimeStyle:NSDateFormatterFullStyle]")
						initializationBlock.appendStatement("[dateFormatter setDateFormat:@\"%s\"]"%dateFormat)
						initializationBlock.append("")
				
				for subObject in self.objcclass.modelobject.subObjects:

						lastEntryName = "entry"
						lastBlock = initializationBlock
						
						for key in subObject.key:
								ifblock = CodeBlock("if([%(dictionary)s objectForKey:@\"%(key)s\"])"%{'dictionary':lastEntryName,'key':key},lastBlock)	
								params = {'newDictName':key+"Entry",'newArrayName':key+"Entries",'lastDictName':lastEntryName,'key':key}
								
								if key is not subObject.key[-1]:
										ifblock.appendStatement("NSDictionary* %(newDictName)s = [%(lastDictName)s objectForKey:@\"%(key)s\"]"%params)
										lastEntryName = params["newDictName"]
								elif subObject.objCType() is "NSArray":
										ifblock.appendStatement("NSArray* %(newArrayName)s = [%(lastDictName)s objectForKey:@\"%(key)s\"]"%params)
										lastEntryName = params["newArrayName"]
								
								lastBlock = ifblock		
						
						count = len(subObject.key)   	
						objectkey = subObject.key[count-1]
														
						params = {'objectname':subObject.name,'dictionary':lastEntryName,'key':objectkey,'subtype':subObject.subtype}
						if subObject.isBaseType():
								if subObject.objCType() is "NSString": 
										lastBlock.appendStatement("self.%(objectname)s = [NSString stringWithString:[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params)
								elif subObject.objCType() is "NSDate": 
										lastBlock.appendStatement("self.%(objectname)s = [dateFormatter dateFromString:[%(dictionary)s objectForKey:@\"%(key)s\"]]"%params)
								elif subObject.objCType() is "NSNumber":
										lastBlock.appendStatement("self.%(objectname)s = [NSNumber numberWithInt:[[%(dictionary)s objectForKey:@\"%(key)s\"] intValue]]"%params)
								elif subObject.objCType() is "NSArray":
										lastBlock.append("")
										lastBlock.appendStatement("NSMutableArray* %(objectname)s = [NSMutableArray arrayWithCapacity:[%(dictionary)s count]]"%params)
										
										self.objcclass.implImports.add(ObjCType(subObject.subtype))
										
										forblock = CodeBlock("for (NSDictionary* entry in %(dictionary)s)"%params)
										forblock.appendStatement("[%(objectname)s addObject:[[[%(subtype)s alloc] initWithDictionary:entry] autorelease]]"%params)
										
										lastBlock.extend(forblock)
										lastBlock.appendStatement("self.%(objectname)s = %(objectname)s"%params)
								else:
										lastBlock.append("I dont fucking know")
						else:
								lastBlock.appendStatement("self."+subObject.name+" = [[["+subObject.objCType()+" alloc] initWithDictionary:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]] autorelease]")
						while lastBlock and lastBlock is not initializationBlock:
								lastBlock.superBlock.extend(lastBlock);
								lastBlock.superBlock.append("")
								lastBlock = lastBlock.superBlock;
						
				definition.append("")
				definition.extend(initializationBlock)
				definition.append("")
				definition.appendStatement("return self")
				return definition

class ModelObjectStaticInitMethod(ObjCMethod):
		
		def __init__(self,modelclass,parser):
				super(ModelObjectStaticInitMethod,self).__init__(modelclass,modelclass.name,[ObjCVar("Dictionary","entry")],"objectWithDictionary:",ObjCMethodType.staticMethod)
				self.parser = parser
		
		def definition(self):
				definition = super(ModelObjectStaticInitMethod,self).definition()
				
				submodelobjects = self.parser.getModelObjectsWithSuperModelObject(self.objcclass.modelobject)
				
				for modelObject in submodelobjects:
						params = {'field':modelObject.qualification.field,'qualifier':modelObject.qualification.qualifier}
						ifblock = CodeBlock("if([[entry objectForKey:@\"%(field)s\"] isEqualToString:@\"%(qualifier)s\"])"%params)
						ifblock.appendStatement("return [%s objectWithDictionary:entry]"%modelObject.name)
						definition.extend(ifblock)
						self.objcclass.implImports.add(ObjCType(modelObject.name))
										
				definition.appendStatement("return [[[%s alloc] initWithDictionary:entry] autorelease]"%self.objcclass.name)
				
				return definition
				
class ModelObject(object):
		
		def __init__ (self,objectName,objectType,qualification):
				self.name = objectName
				self.type = objectType
				self.subObjects = []
				self.qualification = qualification	
		
		def addObject(self,subObject):
				self.subObjects.append(subObject)
		
		def description(self):
				description = "<ModelObject>" + " " + self.name +" Type:"+ self.type
				for subObject in self.subObjects:
						description+="\n\t"+subObject.description()
				return description

class ObjectQualification(object):
		def __init__(self,qualificationString):
				split = re.split(r'=',qualificationString)
				self.field = split[0]
				self.qualifier = split[1] 
				self.qualificationString = qualificationString								

class BaseObject(object):
		
		def __init__ (self,baseObjectType,baseObjectSubType,baseObjectName,baseObjectKey):
				self.name = baseObjectName
				self.type = baseObjectType
				self.subtype = baseObjectSubType
				self.key = baseObjectKey	
		
		def description (self):
				description =  "<BaseObject>" + " " + self.name +" (Type):"+ self.type
				if self.subtype and self.subtype is not "Base":
						description+=" (SubType):"+self.subtype
				if self.key:		
						description+=" (Key):"+ ("-").join(self.key)
				return description		
						
		def isBaseType(self):
				return ObjCType(self.type).isBaseType()
				
		def objCType(self):
				return ObjCType(self.type).objCType()
		



