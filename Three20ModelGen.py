import struct, string ,sys, re

if len(sys.argv)==1:
	print "Usage T20ModelObject.py <input-source-file-name>"

filename = sys.argv[1];

model = open(filename, 'r').read()

## Search for hacker name
hackerMatch = re.search(r'(hacker)\s(.+)',model,re.IGNORECASE)

if hackerMatch:
    hacker = hackerMatch.group(2)
    print 'Hello '+hacker+' T20Gen will now generate code for you...\n'
else:
    print 'Hacker name not found,using \'samyzee\' as Hacker Name'
    hacker = 'samyzee'


## Search for objects and generate object files

objects = re.findall(r"Object\s([\w ]*)\s+(.*?)(?:(?:\nEnd\s*\n)|\Z)",model,re.DOTALL)

if not objects:
        print "No objects were found in your model File"
else:
        print "Parsing Objects..."
        for object in objects:
                interfaces = re.split(r'\W+',object[0])
                
                objectclass = interfaces[0]

                if(len(interfaces)<2):
                   superclass = 'NSObject'
                else:
                   superclass = interfaces[1]

                print objectclass+':'+superclass
                
                subobjects = re.split(r'[\n\t]+',object[1])

                for subobject in subobjects:
                        
                        subobjectsplit = re.split(r'\W+',subobject)        

                        subobjectclass = subobjectsplit[0]
                        subobjectname = ''
                                
                        if (len(subobjectsplit)<2):
                                print "Error:No subobjectname found with type "+subobjectsplit[0]+"in object "+objectclass
                        else:
                                subobjectname = subobjectsplit[1]

                        print '\t'+subobjectclass+' '+subobjectname        

                
                
        
                
        
## Search for models and generate model files    

    
