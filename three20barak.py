import sys,string,pdb,re

from ttmodelbarak import *

def main():
		
		if len(sys.argv)==1:
				print "Usage three20barak.py <input_file>"
		
		filename = sys.argv[1];
		parser = Three20Parser(filename)
		
		project = parser.projectName
		hacker =  parser.hackerName
							
if __name__ == '__main__':
	main()
			