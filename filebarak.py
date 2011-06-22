divider = "///////////////////////////////////////////////////////////////////////////////////////////////////\n"


class File(object):
		
		def __init__(self,tab="\t"):
				self.code = []
				self.level=0
				self.tab=tab
		
		def write(self,line):
				self.code.append(self.tab*self.level+line)
		


class CodeList(list):
		def __init__(self, tab="\t"):
				self.tab = tab;
				self.level = 0;

		def append(self, item):
				errormsg = "Appended objects to CodeList must be String.Cannot append type %s"
				
				if isinstance(item,str):
						super(CodeList, self).append(self.tab*self.level+item)
				else:
						raise TypeError,errormsg % item.type
				
		def dedent(self):
				if self.level > 0:
						self.level=self.level-1
				
		def indent(self):
				self.level=self.level+1  	