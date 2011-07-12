import os

divider = "///////////////////////////////////////////////////////////////////////////////////////////////////"

def firstuppercase(string):
	if string:
			return string[0].upper()+string[1:]
	else:
			return None			

				

class File(object):
		
		def __init__(self,tab="\t"):
				self.code = []
				self.level=0
				self.tab=tab
		
		def write(self,line):
				self.code.append(self.tab*self.level+line)
				
		def printout(self):
				print "\n\n\nFile:"+self.filename()
				print "--------------------"
				print "\n".join(["%s" % (line) for line in self.lines()])		
		
		def filePath(self,rootdir):
				return rootdir + "/" + self.filename()
				
		def generateFile(self,rootdir):					
 				if os.path.exists(self.filePath(rootdir)):
 					mode = "OVERWRITE"
				else:
					mode = "NEW"
					
				print "Generating File %(filename)s (%(mode)s)"%{'filename':self.filename(),'mode':mode}
				
				outputfile = open(self.filePath(rootdir),'w')
				outputfile.write("\n".join(["%s" % (line) for line in self.lines()])	)		
		
		def lines(self):
				return []
				
		def filename(self):
				return None		 


class CodeList(list):
		def __init__(self, tab="\t"):
				self.tab = tab;
				self.level = 0;

		def append(self, item):
				if item is None:
							return
				
				errormsg = "Appended objects to CodeList must be String.Cannot append type %s"
				
				if isinstance(item,str):
						super(CodeList, self).append(self.tab*self.level+item)
				else:
						raise TypeError,errormsg % item.type
		
		def extend(self, item):
				errormsg = "Extending objects to CodeList must be Lists or Sets.Cannot append type %s"
				
				if isinstance(item,list) or isinstance(item,set):
						for listitem in item:
								self.append(listitem)
				else:
						raise TypeError,errormsg % item.type
		
				
		def dedent(self):
				if self.level > 0:
						self.level=self.level-1
				
		def indent(self):
				self.level=self.level+1  	
		
		
		
class CodeBlock(CodeList):
		def __init__(self,blockHeader,superBlock=None):
				super(CodeBlock,self).__init__()
				super(CodeBlock,self).append(blockHeader + " {");
				super(CodeBlock,self).append("}");
				self.superBlock = superBlock
				self.extending = False
				
		def append(self,item):
				if self.extending is True:
						super(CodeBlock,self).append(item)
						return
				
				super(CodeBlock,self).pop()
				super(CodeBlock,self).indent()
				super(CodeBlock,self).append(item)
				super(CodeBlock,self).dedent()
				super(CodeBlock,self).append("}")
				
		def extend(self,item):
				self.extending = True
				super(CodeBlock,self).pop()
				super(CodeBlock,self).indent()
				super(CodeBlock,self).extend(item)
				super(CodeBlock,self).dedent()
				super(CodeBlock,self).append("}")
				self.extending = False
		
		def appendStatement(self,statement):
				self.append(statement+";")
				