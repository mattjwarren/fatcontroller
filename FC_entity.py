###########
# START OF INTERFACE Entity
#

class entity:
    '''This is a dummy class intended for subclassing by entities.

        An entity is defined with class entitytype(entity):
        It must implement the following functions:-'''
    Opts={} #for holding settable entity options

    def __init__(self):
        pass

    async def execute(self,CmdList):
        '''Generic method.

        CmdList should be parsed and executed against the given entity (self).
        The return value should be a list of output elements readable by
        entity.display()'''    
        return # List of lines readable by display() method

    def getparameterdefs(self):
        '''Should return a list of parms for the GUI
        to build a config box, should be in same order as list and strings returned by
        getparameterstring/list '''
        return

    def display(self,LineList,OutputCtrl):
        '''Generic method for displaying output from entity.execute().

        This method should be implmented by the subclasser and translate
        the given LineList to human-readable output.

        OutputCtrl will be a multiline wx.TextCtrl instance
        '''
        return # print LineList, LineList is (minimally) output from execute() method

    def getname(self):
        '''Convenience method for getting entity name.

        should return a string representing the entity uniquely'''
        return # string that is entity name

    def getparameterstring(self):
        '''Method to determine how the entity was defined.

        Should return a string that can be prepended with \'def entity (entity) \' and
        fed to FatController.processcommand()
        that will re-define this entity in its entirety'''
        return

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        parmstring=self.getparameterstring()
        list=parmstring.split()
        return list

    def getentitytype(self):
        '''Get the type of entity.

        Should return qa string indicating the entities type (TELNET , TSM , BROCADE etc..)'''
        return

    def gettype(self):
        '''Return the kind of instance of a given entity.

        For example, TSM entities have an entitytype of 'TSM'
        but a type of single or configmanger. This should
        return a string indicating the kind of entity this is'''
        return

    def setoption(self,option,value):
        '''Set a global option.

        this method should take option and value pair and report on them
        as requried. (IE: TELNET.setoption(self,ShowRawTelnet,yes instructs
        the TELNET entities to begin displaying their raw telnet dialogues)'''
        return

    def getoptions(self):
        '''Get a list of set options.

        Should return a list of the format
        CLASS OPTION VALUE'''
        return

#
# END OF INTERFACE Entity
###########
