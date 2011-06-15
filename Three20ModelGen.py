import struct, string ,sys, re, pdb 
from sets import Set	
		
ObjC_Classes = { 'String':'NSString',
				 'Number':'NSNumber',
				 'Date':'NSDate',
				 'Object':'NSObject',
				 'Array' :'NSArray',	
			   }		

class ModelObject(object):

	def __init__ (self,objectName,objectType):
		self.name = objectName
		self.type = objectType
		self.subObjects = []		

	def addObject(self,subObject):
		self.subObjects.append(subObject)
		
	def description (self):
		description = "<ModelObject>" + " " + self.name +" Type:"+ self.type	
		
		for subObject in self.subObjects:
			description += "\n\t" + subObject.description;
			
		return description
		
	def interface(self):	
		
		interface = "@interface "+self.name+" : "+self.type + " {"
		
		for subObject in self.subObjects:
			interface+= "\n\t"+subObject.ivar();
			
		interface+="\n}\n"
		
		for subObject in self.subObjects:
			interface+= "\n"+subObject.property();
			
		interface+="\n\n@end"	
			
		return interface
		
	def nonBaseTypes(self):
		
		nonBaseTypes = Set()
		
		for subObject in self.subObjects:
			if not subObject.is_base_type():
				nonBaseTypes.add(subObject.objCType())
			
		return nonBaseTypes
		
	def headerFile(self,projectName):
		
		headerFile = "\\\\\n"
		headerFile +="\\\\\t"+ self.name+".h\n"
		if projectName:
			headerFile +="\\\\\t"+ projectName+"\n"
		headerFile +="\\\\\n"
		
		headerFile +="\n\n"
		
		for type in self.nonBaseTypes():
			headerFile += "@class "+type+";\n"
	
		headerFile +="\n"	
			
		headerFile += self.interface()	
		
		return headerFile	
		
class BaseObject(object):

	def __init__ (self,baseObjectName,baseObjectType):
		self.name = baseObjectName
		self.type = baseObjectType
		
	def description (self):
		
		return "<BaseObject>" + " " + self.name +" Type:"+ self.type
		
	def ivar (self):
			
		return self.objCType() +"*" + " "+ "_" + self.name	
		
	def property (self):
	
		if self.objCType() == 'NSString':
			retainer = 'copy'
		else: 
			retainer = 'retain'
		
		return '@property (nonatomic, '+retainer+') '+ self.objCType() +"*" + " "+ self.name
	
	def objCType(self):
	
		if self.is_base_type():
			type = ObjC_Classes[self.type]
		else:
			type = self.type
		
		return type	
		
	def is_base_type(self):
		
		if self.type in ObjC_Classes:
			return True
		else:
			return False		
							

def main():
	if len(sys.argv)==1:
		print "Usage T20ModelObject.py <input-source-file-name>"

	filename = sys.argv[1];

	model = open(filename, 'r').read()

	hacker = parse_variable(model,'hacker')

	if hacker:
		print 'Wassup '+hacker+' T20Gen will now generate code for you...\n'
	else:
		print 'Who are you Mr.Hacker?'
		
	project = parse_variable(model,'project')
	
	if not project:
		print 'WARNING:Project Name not found\n'		

	objects = parse_model_objects(model)

	for object in objects:
		print object.headerFile(project)

def parse_variable (data,varname):

	## parse variable from data 
	varnameMatch = re.search(r'('+varname+')\s(.+)',data,re.IGNORECASE)
	
	if varnameMatch:
		return varnameMatch.group(2)
	else:
		return None	

		
def parse_model_objects (data):

	## parse model objects from data
	allObjects = []
	
	objects = re.findall(r"Object\s([\w ]*)\s+(.*?)(?:(?:\nEnd\s*\n)|\Z)",data,re.DOTALL)

	if not objects:
		print "No objects were found in your model File"
	else:
		print "Parsing Objects..."
		
		for object in objects:
			interfaces = re.split(r'\W+',object[0])
			
			objectclass = interfaces[0]
			
			if(len(interfaces)<2):
				superclass = "Object"
			else:
				superclass = interfaces[1]	
		
			modelObject = ModelObject(objectclass,superclass)
			
			subobjects = re.split(r'[\n\t]+',object[1])
			
			for subobject in subobjects:
				
				subobjectsplit = re.split(r'\W+',subobject)
					
				modelObject.addObject(BaseObject(subobjectsplit[1],subobjectsplit[0]))
			
			allObjects.append(modelObject)
		
	return allObjects	
		
		

## Standard boilerplate to call the main() function to begin
## the program. 
if __name__ == '__main__':
  main()
      
