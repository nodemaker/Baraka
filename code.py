
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