#!/usr/bin/env python
# encoding: utf-8
# Created by Sumeru Chatterjee on one of those long nights

import sys,string,pdb,re

class BaseEntity(object):
		def __init__(self,baseEntityString):
				self.description = baseEntityString
				
				self.type = ""
				self.subType = ""
				self.name = ""
				self.subName = ""
				
				self.parseBaseEntity()
				
		def description(self):
				return self.description
				
		def parseBaseEntity(self):
				
						
						
		


class Parser(object):
		
		def __init__(self,filename):
				self.text = open(filename, 'r').read()		
				
		def parseGlobalSetting (self,varname):
				varnameMatch = re.search(r'%(var)s[\t= ]+(.+)\n'%{'var':varname},self.text,re.IGNORECASE)
				if varnameMatch:
						return varnameMatch.group(1)
						
		def parseSections(self,sectionName):
				return re.findall(r"[\n\A](%(section)s[\t: \n].*?)(?:(?:\nEnd))"%{'section':sectionName},self.text,re.DOTALL|re.IGNORECASE)
							
							
		def parseSubSection(self,section,sub):
				
				#look for a single line subsection first
				singleLineMatch = re.search(r'\n+?\t*?(%(sub)s[:\t= ]+?)(.+?)\t*\n+'%{'sub':sub},section,re.IGNORECASE)
				if singleLineMatch and singleLineMatch.group(2):
						return [singleLineMatch.group(2)]
				
				#look for a single line subsection that is the last subsection
				singleLineLastMatch = re.search(r'\n+?\t*?(%(sub)s[:\t= ]+?)(.+)'%{'sub':sub},section,re.IGNORECASE)
				if singleLineLastMatch and singleLineLastMatch.group(2):
						return [singleLineLastMatch.group(2)]
				
				#Now look for multiline entries that finish with an End Statement
				multiLineMatch = re.search(r'(\n+\t*Output[:\t=\n ]+(.*?)(?:(?:\n+\t*EndOutput)))',section,re.DOTALL|re.IGNORECASE)
				if multiLineMatch and multiLineMatch.group(2):	
						return 	re.split(r'[\n\t^$]+',multiLineMatch.group(2))		

				return []		