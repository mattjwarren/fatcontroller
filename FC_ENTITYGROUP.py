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

    async def execute(self,CmdList, trace_id=None):
        import asyncio
        import logging
        import uuid
        
        if trace_id is None:
             trace_id = str(uuid.uuid4())[:8]
             logging.debug(f"[{trace_id}] ENTITYGROUP.execute initiated for group {self.Name} (new trace)")
        else:
             logging.debug(f"[{trace_id}] ENTITYGROUP.execute starting for group {self.Name}")
             
        OutputList=[]
        OutputList.append('Executing command against group '+self.Name)
        
        # We want to execute against all members in parallel?
        # The user requested "all entity command executions asynchronously".
        # Parallel execution for groups makes sense.
        
        tasks = []
        for entity in self.Entities:
            # We call the EntityManager.execute, which handles UI and calling entity.execute
            # Wait, EntityManager.execute is now async too.
            tasks.append(self.EntityManager.execute(entity, CmdList, trace_id=trace_id))
            
        if tasks:
             await asyncio.gather(*tasks)
             
        OutputList.append('Group execution initiated.')
        logging.debug(f"[{trace_id}] ENTITYGROUP.execute finished for group {self.Name}")
        return OutputList

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
