 from sets import Set    
dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZ"
        
 
  def description (self):
                
                description = "-(NSString*) description {
                "

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
                