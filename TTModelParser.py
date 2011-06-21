import re

from ObjCGen import *

class ModelObjectClass(ObjCClass):

		def __init__(self,modelobject):
		
				super(ModelObjectClass,self).__init__(modelobject.name,modelobject.type)
		
				for subObject in modelobject.subObjects:
						attributes = ['nonatomic','retain']
						self.addInstanceVariable(ObjCVar(subObject.name,subObject.type),True,attributes)
			
						
				

class ModelObject(object):
		
		def __init__ (self,objectName,objectType):
				self.name = objectName
				self.type = objectType
				self.subObjects = []	
		
		def addObject(self,subObject):
				self.subObjects.append(subObject)
		
		def description(self):
				description = "<ModelObject>" + " " + self.name +" Type:"+ self.type
				for subObject in self.subObjects:
						description+="\n"+subObject.description()
				return description


class BaseObject(object):
		
		def __init__ (self,baseObjectType,baseObjectSubType,baseObjectName,baseObjectKey):
				self.name = baseObjectName
				self.type = baseObjectType
				self.subtype = baseObjectSubType
				self.key = baseObjectKey	
		
		def description (self):
				return "\t<BaseObject>" + " " + self.name +" Type:"+ self.type		
		
		


class ModelParser(object):
		
		def __init__(self,filename):
				
				self.text = open(filename, 'r').read()
				self.projectname = self.parseVariable('project')
				self.modelObjects = []
				self.parseObjects()
				
		def objects (self):
				return self.modelObjects		
		
		def projectName (self):
				
				return self.projectName	 	
		
		def parseVariable (self,varname):
		
				varnameMatch = re.search(r'('+varname+')\s(.+)',self.text,re.IGNORECASE)
				if varnameMatch:
						return varnameMatch.group(2)
				else:
						return None
		
		def parseObjects (self):
				rawObjects = re.findall(r"Object\s([\w ]*)\s+(.*?)(?:(?:\nEnd\s*\n)|\Z)",self.text,re.DOTALL)
				
				for object in rawObjects:
						
						interfaces = re.split(r'\W+',object[0])
						objectclass = interfaces[0]
						
						if(len(interfaces)<2):
								superclass = "Object"
						else:
								superclass = interfaces[1]  	
						
						modelObject = ModelObject(objectclass,superclass)
						
						subobjects = re.split(r'[\n\t]+',object[1])
						
						for subobject in subobjects:
								
								split = re.findall(r'[\w<>\(\):]+',subobject)
								
								if(len(split)<2):
									print "ERROR: could not parse subobject declaration -> "+subobject+" in Object "+objectclass
								
								objecttypesplit = re.findall(r'\w+',split[0])
								
								objecttype = objecttypesplit[0]
								
								if (len(objecttypesplit)>1):
										objectsubtype = objecttypesplit[1]
								else:	
										objectsubtype = "Base"
								
								objectnamesplit = re.findall(r'\w+',split[1])
								
								objectname = objectnamesplit[0]
								
								if (len(objectnamesplit)<2):
										objectkey = [objectname]
								else:
										objectkey = [key for key in objectnamesplit[1:] if key]
								
								modelObject.addObject(BaseObject(objecttype,objectsubtype,objectname,objectkey))
								
								
						self.modelObjects.append(modelObject)		
		
		def description(self):
				description = ""
				for modelObject in self.modelObjects:
						description+="\n"+modelObject.description()
				return description
				
		
