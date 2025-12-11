import FC_entity,subprocess,tkinter

class LOCAL(FC_entity.entity):
    '''Implementation of an entity that executes commands on the local machine'''
    def __init__(self,name):
        self.Name=name
        pass

    ##########
    # START OF INTERFACE ENTITY
    #

    Opts={}

    async def execute(self,CmdList, trace_id=None):
        import asyncio
        import shlex
        import logging
        
        log_prefix = f"[{trace_id}]" if trace_id else ""
        logging.debug(f"{log_prefix} LOCAL.execute: {' '.join(CmdList)}")
        
        # din,dout,derr=os.popen3(' '.join(CmdList))
        try:
            cmd = ' '.join(CmdList)
            # Use create_subprocess_shell for shell=True equivalent
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            output = []
            if stdout:
                output.extend(stdout.decode().splitlines())
            if stderr:
                output.extend(stderr.decode().splitlines())
                
        except Exception as e:
            output = [f"Error executing command: {e}"]
        return output# List of lines readable by display() method

    def display(self,LineList,OutputCtrl):
        '''Generic method for displaying output from entity.execute().

        This method should be implmented by the subclasser and translate
        the given LineList to human-readable output.'''
        for line in LineList:
            # OutputCtrl.AppendText(line.rstrip()+"\n")
            try:
                OutputCtrl.insert("end", line.rstrip()+"\n")
            except:
                pass # Fallback or ignore if not a text widget
        return # print LineList, LineList is (minimally) output from execute() method
    
    def getparameterdefs(self):
        '''Should return a dict of parm:parmtype pairs for the GUI
        to build a config box'''
        return ["Name"]
    
    def getname(self):
        '''Convenience method for getting entity name.

        should return a string representing the entity uniquely'''
        return self.Name # string that is entity name

    def getparameterstring(self):
        DBGBN='localgetparameterstring'
        '''Method to determine how the entity was defined.

        Should return a string that can be fed to FatController.processcommand()#outdate see aboce
        that will re-define this entity in its entirety'''
        #dbg('returning define entity LOCAL '+self.Name,DBGBN)
        return ''

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        parmstring=self.getparameterstring()
        lst=parmstring.split()
        return lst

    def getentitytype(self):
        '''Get the type of entity.

        Should return qa string indicating the entities type (TELNET , TSM , BROCADE etc..)'''
        return 'LOCAL'

    def gettype(self):
        '''Return the kind of instance of a given entity.

        For example, TSM entities have an entitytype of 'TSM'
        but a type of single or configmanger. This should
        return a string indicating the kind of entity this is'''
        return 'simple'

    def setoption(self,option,value):
        '''Set a global option.

        this method should take option and value pair and set them
        as requried. (IE: TELNET.setoption(self,ShowRawTelnet,yes instructs
        the TELNET entities to begin displaying their raw telnet dialogues)'''
        LOCAL.Opts[option]=value
        return

    def getoptions(self):
        '''Get a list of set options.

        Should return a list of the format
        CLASS OPTION VALUE'''
        OptList=[]
        for o in LOCAL.Opts:
            OptList.append(o+' '+LOCAL.Opts[o])
        return OptList

    #
    # END OF INTERFACE Entity
    ###########
#
# END OF CLASS LOCAL
############
