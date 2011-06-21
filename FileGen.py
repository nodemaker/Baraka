divider = "///////////////////////////////////////////////////////////////////////////////////////////////////\n"

class FileGen(object):
		
		def __init__(self,tab="\t"):
				self.code = []
				self.level=0
				self.tav=tab
		
		def description(self):
				return string.join(self.data,"")
		
		def write(self,line):
				self.code.append(self.tab*self.level+line)
		
		def indent(self):
				if self.tablevel > 0:
						self.level=self.level-1
						
		def dedent(self):
				self.level=self.level+1
									