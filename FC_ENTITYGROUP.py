import FC_entity
##########
# START OF CLASS ENTITYGROUP

class ENTITYGROUP(FC_entity.entity):
    '''Implentation of a 'meta' entity, which is groups of other entites'''
    def __init__(self,name,EntityNameList,EntityManagerInstance):
        
    #def __init__(name,EntityNameList,EntityManagerInstance):
        self.Name=name
        self.Entities=EntityNameList
        self.EntityManager=EntityManagerInstance

    ##########
    # START OF INTERFACE ENTITY
    #

    Opts={}

    def execute(self,CmdList):
        for Entity in self.Entities:
            self.EntityManager.execute(Entity,CmdList)
        return ['\nEntityGroup executed command.\n']

    def display(self,LineList,OutputCtrl):
        for line in LineList:
            try:
                OutputCtrl.insert("end", line.rstrip()+"\n")
            except:
                pass
        return

    def getparameterdefs(self):
        EntityParmFields=["Name"]
        for Entity in self.Entities:
            EntityParmFields.append(Entity)
        return EntityParmFields

    def getname(self):
        return self.Name

    
    def getparameterstring(self):
        parmstring=''
        for Entity in self.Entities:
            if parmstring=='':
                parmstring=Entity
            else:
                parmstring=parmstring+" "+Entity
        return parmstring
    
    def getparameterlist(self):
        parmstring=self.getparameterstring()
        lst=parmstring.split()
        return lst

    def getentitytype(self):
        return 'ENTITYGROUP'

    def gettype(self):
        return 'simple'

    def setoption(self,option,value):
        ENTITYGROUP.Opts[option]=value
        return
    
    def getoptions(self):
        OptList=[]
        for o in ENTITYGROUP.Opts:
            OptList.append(o+' '+LOCAL.Opts[o])
        return OptList
    
    #
    # END OF INTERFACE ENTITY
    ##########
#
# END OF CLASS ENTITYGROUP
###########
