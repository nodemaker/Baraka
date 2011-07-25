#!/usr/bin/env python
# encoding: utf-8
# Created by Sumeru Chatterjee on one of those long nights

import sys,string,pdb,re,os

from file import *
from objc import *
from code import *

class Baraka(object):
		
		def __init__(self,inputfile,entityNames=[],subEntityNames=[]):
				self.rawString = open(inputfile, 'r').read()		
				self.inputfile = inputfile
				self.fileName = os.path.basename(inputfile)
				
				self.entityNames = entityNames
				self.subEntityNames = subEntityNames
				
				self.entities = []
				self.globalSettings = {}
				self.classes = []
				self.generatedFiles = []
				
				self.parse()	
				self.create()
				
		def parse(self):
				#calculate the rootpath and abspath		
				self.abspath = os.path.abspath(self.inputfile)
				self.rootpath =  os.path.dirname(self.abspath)
				self.dirpath = self.rootpath +"/"+self.dirname
				
				self.hacker = self.checkGlobalSetting("hacker","Name of hacker","No hacker name will be written on the files")
				self.project = self.checkGlobalSetting("project","project name","No project name will be written in files")
				
				for entityName in self.entityNames:
						self.entities.extend(self.parseEntities(entityName))
				
				
		def parseEntities(self,entityName):
			 	entities = []
			 	rawEntities	= re.findall(r'[\n\A](%(section)s[\t: \n].*?)(?:(?:\nEnd))'%{'section':entityName},self.rawString,re.DOTALL|re.IGNORECASE)
			 	for rawEntity in rawEntities:
			 			entities.append(Entity(rawEntity,entityName,self.subEntityNames))
			 	return entities	 	
			 	
		def checkGlobalSetting(self,variablekey,keydescription,warnmessage,defaultvalue=None):
				value = self.parseGlobalSetting(variablekey)
				if value:
						return value		
				else:
						print "\nWARNING: "+keydescription+" not found...Use Key \""+variablekey+"\" to specify "+keydescription
						if defaultvalue:
								print "\nWARNING: Using "+defaultvalue+" as "+keydescription
						elif warnmessage:
								print "WARNING: "+warnmessage
						return defaultvalue				
				
		def parseGlobalSetting (self,varname):
				varnameMatch = re.search(r'%(var)s[\t= ]+(.+)\n'%{'var':varname},self.rawString,re.IGNORECASE)
				if varnameMatch:
						return varnameMatch.group(1)
				else:
						return None		
		
		def rawDescription(self):
				return self.rawString
				
		def getEntitiesWithTypeName(self,name):
				entities = []
				
				for entity in self.entities:
						if name == entity.typeBaseEntity.name:
								entities.append(entity)
			
				return entities				
				
		def description(self):
				description =  "\n\nParse Results\n"
				description += "-----------------\n"
				
				
				if self.globalSettings:
					description += "\n\n<Global Settings>" 
				
				for key in self.globalSettings:
					description += "\n\t"+ key +" : " + self.globalSettings[key]
				
				if self.entities:
					description += "\n\n<Entities>" 	
					for entity in self.entities:
						description += "\t"+entity.description().replace('\n','\n\t')
				
				return description



class Entity(object):
		def __init__(self,rawEntity,entityName,subEntityNames):				
				self.rawString = rawEntity	
				self.name = entityName
				self.subEntityNames = subEntityNames
				
				#parse the type of entity
				entityTypeMatch = re.search(r'%s[\t ]+(.*)'%self.name,self.rawString,re.IGNORECASE)
				if entityTypeMatch and entityTypeMatch.group(1):
						self.typeBaseEntity = BaseEntity(entityTypeMatch.group(1))
				
				self.subEntities = []
		
				self.parse()
				
		
		def parse(self):
				for subEntityName in self.subEntityNames:
						rawSubEntity = self.parseSubEntity(subEntityName)
						subEntity = SubEntity(rawSubEntity,subEntityName)
						self.subEntities.append(subEntity)	
		
		def parseSubEntity(self,subEntityName):
				#look for a single line subsection first
				singleLineMatch = re.search(r'\n+?\t*?(%(sub)s[:\t= ]+?.+?)\t*\n+'%{'sub':subEntityName},self.rawString,re.IGNORECASE)
				if singleLineMatch and singleLineMatch.group(1):
						return singleLineMatch.group(1)
				
				#look for a single line subsection that is the last subsection
				singleLineLastMatch = re.search(r'\n+?\t*?(%(sub)s[:\t= ]+?.+)'%{'sub':subEntityName},self.rawString,re.IGNORECASE)
				if singleLineLastMatch and singleLineLastMatch.group(1):
						return singleLineLastMatch.group(1)
				
				#Now look for multiline entries that finish with an End Statement
				multiLineMatch = re.search(r'(\n+\t*(%(sub)s[:\t=\n ]+.*?)(?:(?:\n+\t*End%(sub)s)))'%{'sub':subEntityName},self.rawString,re.DOTALL|re.IGNORECASE)
				if multiLineMatch and multiLineMatch.group(1):	
						return multiLineMatch.group(1)					
		
		def rawDescription(self):
				return self.rawString
				
		def getSubEntityByName(self,name):
				for subEntity in self.subEntities:
						if subEntity.name.lower() == name.lower():
								return subEntity
				return 	None			
						
		
		def description(self):
				description = "\n<Entity> Name:"+self.name.title() +" Type:"+self.typeBaseEntity.description() 
				description += "\n<SubEntities>"
				for subEntity in self.subEntities:
						description += "\n\t"+subEntity.description().replace('\n','\n\t')
				return description	


class SubEntity(object):
		def __init__(self,rawSubEntity,subEntityName):
				self.rawString = rawSubEntity
				self.name = subEntityName
		
				self.baseEntities = []
		
				self.parse()
				
				
		
		def description(self):
				description = "<SubEntity> Name:"+self.name.title() +"\n<BaseEntities>"
				for baseEntity in self.baseEntities:
						description += "\n\t"+baseEntity.description().replace("\n","\n\t")
				return description
				
		def rawDescription(self):
				return self.rawString
						
		def parse(self):
				#for single line subentities
				singlelinematch = re.search(r'%s[:\t= ]+(.*)'%self.name,self.rawString,re.IGNORECASE)
				
				if singlelinematch and singlelinematch.group(1):
						self.baseEntities.append(BaseEntity(singlelinematch.group(1)))
				
				#for multilinematches	
				multilinematches = re.search(r'\n+\t*%(sub)s[:\t= ]+(.*)(?:(?:\n+\t*End%(sub)s))'%{'sub':self.name},self.rawString,re.DOTALL|re.IGNORECASE)
				
				if multilinematches and multilinematches.group(1):
						for rawBaseEntity in re.split(r'[\t\r\n^$]+',multilinematches.group(1)):
								if rawBaseEntity:
										self.baseEntities.append(BaseEntity(rawBaseEntity))
										
										
			
class BaseEntity(object):
		def __init__(self,baseEntityString):
				self.rawString = baseEntityString
				
				self.type = ""
				self.subType = ""
				self.name = ""
				self.subName = ""
				
				self.parse()
				
		def rawDescription(self):
				return self.rawString
		
		def description(self):
				return "<BaseEntity> %(type)s<%(subtype)s> %(name)s(%(subname)s)"%{'type':self.type,'subtype':self.subType,'name':self.name,'subname':self.subName}
				
		def parse(self):
				
				parts = re.split('[\t ]',self.rawString)
				
				typeParts = re.split('[<>]',parts[0])
				
				self.type = typeParts[0]
				
				if len(typeParts)>1:
						self.subType = typeParts[1]
				
				if not len(parts)>1:
						return
				
				nameParts = re.split('[\(\)]',parts[1])
				self.name = nameParts[0]
				if len(nameParts)>1:
						self.subName = nameParts[1]

class dotdict(dict):
    	def __getattr__(self, attr):
        	return self.get(attr, None)
    	__setattr__= dict.__setitem__
    	__delattr__= dict.__delitem__								
