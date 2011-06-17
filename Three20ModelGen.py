import struct, string ,sys, re, pdb 
from sets import Set    

divider = "///////////////////////////////////////////////////////////////////////////////////////////////////\n"

dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"
                
ObjC_Classes = { 'String':'NSString',
                                 'Number':'NSNumber',
                                 'Date':'NSDate',
                                 'Object':'NSObject',
                                 'Array' :'NSArray',    
                           }
def tabs(n):
        return "\t"*n

def nextlineandtabs(n):
        return "\n"+tabs(n)


class ModelObject(object):

        def __init__ (self,objectName,objectType):
                self.name = objectName
                self.type = objectType
                self.subObjects = []            

        def addObject(self,subObject):
                self.subObjects.append(subObject)
                
        def description (self):
                
                description = "-(NSString*) description {"

                description += "\n\n\treturn [NSString stringWithFormat:@\"\\n"
                
                for subObject in self.subObjects:
                        description += subObject.objectname()+" - %@\\n"

                description += "\""

                for subObject in self.subObjects:
                        description += "," +subObject.ivarname()
                

                description += "];\n}\n"
                        
                return description
        

        def dealloc (self):

                dealloc = "-(void) dealloc {\n"

                for subObject in self.subObjects:        
                        dealloc += "\n\tTT_RELEASE_SAFELY("+subObject.ivarname()+");"

                dealloc += "\n\n\t[super dealloc];\n}\n"

                return dealloc                
                

        def implementation (self):

                implementation = "@implementation "+self.name+"\n\n"
                
                for subObject in self.subObjects:
                        implementation+=subObject.synthesizer()+";"+"\n"

                implementation += "\n"+divider+self.initMethod()+"\n"
        
                implementation += "\n"+divider+self.dealloc()+"\n"

                implementation += "\n"+divider+self.description()+"\n"

                implementation += "\n@end"

                return implementation
                
        def interface(self):    
                
                interface = "@interface "+self.name+" : "+self.type + " {"
                
                for subObject in self.subObjects:
                        interface+= "\n\t"+subObject.ivar()+";"
                        
                interface+="\n}\n"
                
                for subObject in self.subObjects:
                        interface+= "\n"+subObject.property()+";"

                interface+= "\n\n"+self.initMethodDeclaration()+";"
                        
                interface+="\n@end"     
                        
                return interface
                
        def nonBaseTypes(self):
                
                nonBaseTypes = Set()
                
                for subObject in self.subObjects:
                        if not subObject.is_base_type():
                                nonBaseTypes.add(subObject.objCType())
                        
                return nonBaseTypes
        
        def headerFileName (self):
                return self.name+".h"

        def implFileName (self):
                return self.name+".m"

        def implFile (self,projectName):
                implFile = "//\n"
                implFile +="//\t"+ self.name+".m\n"
                if projectName:
                        implFile +="//\t"+ projectName+"\n"
                implFile +="//\n"
                
                implFile +="\n\n"

                implFile += "@import \""+self.headerFileName()+"\n"

                for type in self.nonBaseTypes():
                        implFile += "\n@import \""+type+".h\""

                implFile +="\n\n"  

                implFile +=divider+divider+divider

                implFile +=self.implementation()

                return implFile

        def hasDateSubObject (self):
                result = False
                        
                for subObject in self.subObjects:
                        if subObject.objCType() is "NSDate":
                                result = True
                                break

                return result       
                
                
                                
        def headerFile(self,projectName):
                
                headerFile = "//\n"
                headerFile +="//\t"+ self.name+".h\n"
                if projectName:
                        headerFile +="//\t"+ projectName+"\n"
                headerFile +="//\n"
                
                headerFile +="\n\n"
                
                for type in self.nonBaseTypes():
                        headerFile += "@class "+type+";\n"
        
                headerFile +="\n"       
                        
                headerFile += self.interface()  
                
                return headerFile

        def fulldescription (self,project):
                description = "--------------------\n"+self.headerFileName()+"\n--------------------\n"       
                description += self.headerFile(project)+"\n"
                description += "--------------------\n"+self.implFileName()+"\n--------------------\n"
                description += self.implFile(project)+"\n"
                return description

        def initMethodDeclaration (self):

                return "-(id) initWithDictionary:(NSDictionary*)entry"

        def initMethod (self):
                indentation = 1;
                
                definition = self.initMethodDeclaration()+" {\n"
                definition += nextlineandtabs(indentation) + "if([entry isKindOfClass:[NSNull class]])"
                definition += nextlineandtabs(indentation) + "return nil;\n"
                
                if self.type is "NSObject":
                    definition += nextlineandtabs(indentation) + "if(self = [super init]) {\n"
                else:
                    definition += nextlineandtabs(indentation) + "if(self = [super initWithDictionary:entry]) {\n"
                
                indentation +=1
                        
                if self.hasDateSubObject():
                        definition +=nextlineandtabs(indentation) + "NSDateFormatter* dateFormatter = [[[NSDateFormatter alloc] init] autorelease];"
                        definition +=nextlineandtabs(indentation) + "[dateFormatter setTimeStyle:NSDateFormatterFullStyle];"
                        definition +=nextlineandtabs(indentation) + "[dateFormatter setDateFormat:@\""+dateFormat+"\"];\n"
                

                for subObject in self.subObjects:

                        lastEntryName = "entry"
                              
                        for key in subObject.objectkey():
                                        
                                definition +=nextlineandtabs(indentation)+ "if(["+lastEntryName+" objectForKey:@\""+key+"\"]) {"
                                indentation +=1

                                if key is not subObject.objectkey()[-1]:
                                        definition +="\n"+nextlineandtabs(indentation)+"NSDictionary* "+ key+"Entry"+" = "+"["+lastEntryName+" objectForKey:@\""+key+"\"];"
                                        lastEntryName = key+"Entry"
                                elif subObject.objCType() is "NSArray":
                                        definition +="\n"+nextlineandtabs(indentation)+"NSArray* "+key+"Entries"+" = "+"["+lastEntryName+" objectForKey:@\""+key+"\"];"
                                        lastEntryName = key+"Entry"
                                        

                        count = len(subObject.objectkey())       
                        objectkey = subObject.objectkey()[count-1]
                        
                        if subObject.is_base_type():
                                if subObject.objCType() is "NSString": 
                                        definition += nextlineandtabs(indentation)+ "self."+subObject.objectname()+" = "
                                        definition += "[NSString stringWithString:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]];"
                                elif subObject.objCType() is "NSDate": 
                                        definition += nextlineandtabs(indentation)+ "self."+subObject.objectname()+" = "
                                        definition += "[dateFormatter dateFromString:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]];"
                                elif subObject.objCType() is "NSNumber":
                                        definition += nextlineandtabs(indentation)+ "self."+subObject.objectname()+" = "
                                        definition += "[NSNumber numberWithInt:[["+lastEntryName+" objectForKey:@\""+objectkey+"\"] intValue]];"
                                elif subObject.objCType() is "NSArray":
                                        definition += nextlineandtabs(indentation)+ "NSMutableArray* "+subObject.objectname()
                                        definition += " = [NSMutableArray arrayWithCapacity:["+lastEntryName+" count]];"
                                        definition += nextlineandtabs(indentation)+ "for (NSDictionary* entry in "+lastEntryName+")"
                                        definition += nextlineandtabs(indentation)+ "\t["+subObject.objectname()
                                        definition += " addObject:[[[FacebookLike alloc] initWithDictionary:entry] autorelease]];"
                                        definition += nextlineandtabs(indentation)+ "self."+subObject.objectname()+" = "+subObject.objectname()+";"
                                else:
                                        definition += "I dont fucking know"
                        else:
                                definition += nextlineandtabs(indentation)+ "self."+subObject.objectname()+" = "
                                definition+= "[[["+subObject.objCType()+" alloc] initWithDictionary:["+lastEntryName+" objectForKey:@\""+objectkey+"\"]] autorelease];"
        

                        for key in subObject.objectkey():
                                indentation-=1
                                definition+=nextlineandtabs(indentation)+"}"
                                

                        definition+="\n"        

                indentation-=1
                definition += nextlineandtabs(indentation)+ "}"

                
                indentation-=1
                definition += nextlineandtabs(indentation)+ "}"

                return definition
                
class BaseObject(object):

        def __init__ (self,baseObjectType,baseObjectSubType,baseObjectName,baseObjectKey):
                self.name = baseObjectName
                self.type = baseObjectType
                self.subtype = baseObjectSubType
                self.key = baseObjectKey
                
        def description (self):
                
                return "<BaseObject>" + " " + self.name +" Type:"+ self.type

        def ivarname (self):
                return "_"+self.name
                
        def ivar (self):
                        
                return self.objCType() +"*" + " "+ self.ivarname()      

        def objectkey (self):

                return self.key

        def objectname (self):

                return self.name
                
        def property (self):
        
                if self.objCType() == 'NSString':
                        retainer = 'copy'
                else: 
                        retainer = 'retain'
                
                return '@property (nonatomic, '+retainer+') '+ self.objCType() +"*" + " "+ self.name

        def synthesizer (self):

                return "@synthesize "+self.objectname()+" = "+self.ivarname()   
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

        print "Generating Files...."
                
        for object in objects:
            print object.fulldescription(project)

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

                    
                        allObjects.append(modelObject)
            
        return allObjects       
                
                

## Standard boilerplate to call the main() function to begin
## the program. 
if __name__ == '__main__':
  main()
      
