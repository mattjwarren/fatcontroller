import FC_entity
###########
# START OF CLASS DUMB
# a dumb entity

class DUMB(FC_entity.entity):
    '''implementation of a very simple entity.'''
    def __init__(self,name):
        self.Name=name

    ###########
    # Start of interface ENTITY 
    #


    Opts={} #for holding settable entity options

    def execute(self,CmdList):
        '''Generic method.
    
        CmdList should be parsed and executed against the given entity (self).
        The return value should be a list of output elements readable by
        entity.display()'''
        CmdList.insert(0,'I would have executed this\n')
        return CmdList # List of lines readable by display() method

    def display(self,LineList,OutputCtrl):
        '''Generic method for displaying output from entity.execute().
    
        This method should be implmented by the subclasser and translate
        the given LineList to human-readable output.
    
            OutputCtrl is wx.TextCtrl to display onto
        '''

        for line in LineList:
            try:
                OutputCtrl.insert("end", line.rstrip()+"\n")
            except:
                pass
        return # print LineList, LineList is (minimally) output from execute() method
    
    def getparameterdefs(self):
        '''Should return a dict of parm:parmtype pairs for the GUI
        to build a config box. 'parm' will be displayed name for input boxes'''
        return ["Name"]
    

    def getname(self):
        '''Convenience method for getting entity name.
    
        should return a string representing the entity uniquely'''
        return self.Name # string that is entity name

    def getparameterstring(self):
        '''Method to determine how the entity was defined.
    
        Should return a string that can be fed to FatController.processcommand()
        that will re-define this entity in its entirety'''
        return ''

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        parmstring=self.getparameterstring()
        list=parmstring.split()
        return list


    def getentitytype(self):
        '''Get the type of entity.
    
        Should return qa string indicating the entities type (TELNET , TSM , BROCADE etc..)'''
        return 'DUMB'

    def gettype(self):
        '''Return the kind of instance of a given entity.
    
        For example, TSM entities have an entitytype of 'TSM'
        but a type of single or configmanger. This should
        return a string indicating the kind of entity this is'''
        return 'simple'

    def setoption(self,option,value):
        '''Set a global option.
    
        this method should take option and value pair and report on them
        as requried. (IE: TELNET.setoption(self,ShowRawTelnet,yes instructs
        the TELNET entities to begin displaying their raw telnet dialogues)'''
        DUMB.Opts[option]=value
        return

    def getoptions(self):
        '''Get a list of set options.
    
        Should return a list of the format
        class (entity) option (option) (value) '''
        optlist=[]
        for opt in DUMB.Opts:
            optlist.append('DUMB '+opt+' '+DUMB.Opts[opt])
        return optlist

    #
    # END OF INTERFACE Entity
    ###########

#
# END OF CLASS DUMB
###########
