import struct, string ,sys, re, pdb	

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
			description += "\n\t" + subObject.description()
			
		return description	
		
class BaseObject(object):

	def __init__ (self,baseObjectName,baseObjectType):
		self.name = baseObjectName
		self.type = baseObjectType
		
	def description (self):
		
		return "<BaseObject>" + " " + self.name +" Type:"+ self.type

def parse_hacker_name (data):

	## parse hacker name from data 
	hackerMatch = re.search(r'(hacker)\s(.+)',data,re.IGNORECASE)
	
	if hackerMatch:
		hacker = hackerMatch.group(2)
	else:
		print 'Hacker name not found,using \'samyzee\' as Hacker Name'
		hacker = 'samyzee'
	
	return hacker		

		
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
							
				

# Gather our code in a main() function
def main():
	if len(sys.argv)==1:
		print "Usage T20ModelObject.py <input-source-file-name>"

	filename = sys.argv[1];

	model = open(filename, 'r').read()

	hacker = parse_hacker_name(model)

	print 'Hello '+hacker+' T20Gen will now generate code for you...\n'

	objects = parse_model_objects(model)

	for object in objects:
		print object.description()
		
		

## Standard boilerplate to call the main() function to begin
## the program. 
if __name__ == '__main__':
  main()
      
