  

        def ivarname (self):
                return "_"+self.name
                
        def ivar (self):
                        
                return self.objCType() +"*" + " "+ self.ivarname()      

        def objectkey (self):

                return self.key

        def objectname (self):

                return self.name
                
        def property (self):
        
                if self.objCType() == 'NSString':
                        retainer = 'copy'
                else: 
                        retainer = 'retain'
                
                return '@property (nonatomic, '+retainer+') '+ self.objCType() +"*" + " "+ self.name

        def synthesizer (self):

                return "@synthesize "+self.objectname()+" = "+self.ivarname()   
                
        def objCType(self):
        
                if self.is_base_type():
                        type = ObjC_Classes[self.type]
                else:
                        type = self.type
                
                return type
        
                
        def is_base_type(self):
                
                if self.type in ObjC_Classes:
                        return True
                else:
                        return False       