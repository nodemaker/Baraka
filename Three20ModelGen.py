import struct, string ,sys, re

if len(sys.argv)==1:
	print "Usage T20ModelObject.py <input-source-file-name>"

filename = sys.argv[1];

model = open(filename, 'r').read()

## Search for hacker name
hackerMatch = re.search(r'(hacker)\s(.+)',model,re.IGNORECASE)

if hackerMatch:
    hacker = hackerMatch.group(2)
    print 'Hello '+hacker+' T20Gen will now generate code for you..'
else:
    print 'Hacker name not found,using \'samyzee\' as Hacker Name'
    hacker = 'samyzee'


## Search for objects and generate object files

objects = re.findall(r'Object\s.*',model,re.IGNORECASE)

if not objects:
        print "No objects were found in your model File"
else:
        for object in objects:
                
                

## Search for models and generate model files    



object
    
