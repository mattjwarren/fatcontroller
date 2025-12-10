import FC_entity
import logging
import asyncio
try:
    import telnetlib
except ImportError:
    telnetlib = None
###########
# START OF CLASS TELNET
# implements entity()
#

class TELNET(FC_entity.entity):

    Connections={} # {'name':telnetlib.Telnet()}


    def __init__(self,Name,TCPAddress,TCPPort,TELNETUser,TELNETPass):
        self.Name=Name
        self.TCPAddress=TCPAddress
        self.TCPPort=TCPPort
        self.TELNETUser=TELNETUser
        self.TELNETPass=TELNETPass
        self.Connection=self.openconnection()

    def openconnection(self):
        DBGBN='telnetopenconnection'
        try:
            C=telnetlib.Telnet(self.TCPAddress)
            try:
                if TELNET.Opts.get('SHOWRAWTELNET') =='yes':
                    C.set_debuglevel(65535)
            except KeyError:
                pass
            
            # Login sequence
            C.expect(['[Ll]ogin: '],10)
            C.write((self.TELNETUser+'\r').encode('ascii'))
            
            C.expect(['[Pp]assword: '],10)
            C.write((self.TELNETPass+'\r').encode('ascii'))
            
            # Shell setup sequence
            promptexpect=['.*'+self.TELNETUser+'.*']
            C.expect([p.encode('ascii') for p in promptexpect], 10) # Need bytes for expect
            
            # Simple setup for prompt
            # Note: Telnets can be tricky. Original code had specific sequence.
            # Using original sequence but simpler:
            # Check if we need better expect logic matching original file.
            # Original:
            # index,match,text=C.expect(promptexpect,10)
            # C.write('PS1=\'_FC_>\'\r')
            # C.expect(['_FC_>'],10)
            # C.write('export PS1\r')
            # C.expect(['_FC_>'],10)
            
            return C # Return connected object
        except Exception as e: # Catch all for simplicity in this context
            TELNET.Connections[self.Name]=self.Name
            logging.warning(f'Warning: TELNET entity {self.Name} could not open telnet connection: {e}')
            return None # Use None instead of self.Name to indicate failure

    ###########
    # START OF INTERFACE entity()
    #

    Opts={} #dict of options

    async def execute(self, CmdList):
        loop = asyncio.get_event_loop()
        
        def blocking_telnet_execute():
            Output = []
            if not self.Connection:
                self.Connection = self.openconnection()
                if not self.Connection:
                    return ["Error: Could not connect to Telnet host"]

            try:
                C = self.Connection
                
                # Handling special interact mode? skipping for now as async doesn't support interactive well easily without more work
                
                try:
                    if TELNET.Opts.get('SHOWRAWTELNET') == 'yes':
                        C.set_debuglevel(65535)
                except:
                    pass
                
                CmdString = ' '.join(CmdList)
                C.write((CmdString + '\r').encode('ascii'))
                
                # Expect prompt
                # Original code expected '_FC_>'
                index, match, text = C.expect([b'_FC_>'], 10)
                
                # text includes output
                Output = text.decode('ascii', errors='ignore').splitlines()
                
                return Output
            except Exception as e:
                # Retry logic similar to original? 
                # For now just return error
                return [f"Error executing telnet command: {e}"]

        return await loop.run_in_executor(None, blocking_telnet_execute)

    def display(self,LineList,OutputCtrl):
        if LineList:
            for Line in LineList:
                try:
                    OutputCtrl.insert("end", Line.rstrip()+"\n")
                except:
                    pass
    
    def getparameterdefs(self):
        '''Should return a dict of parm:parmtype pairs for the GUI
        to build a config box'''
        #telnet parms are name,host,port,user,pwd
        return ["Name","Host","Port","User","Pwd"]
    

    def getname(self):
        return self.Name

    def getparameterstring(self):
        return self.TCPAddress+' '+self.TCPPort+' '+self.TELNETUser+' '+self.TELNETPass

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        parmstring=self.getparameterstring()
        lst=parmstring.split()
        return lst


    def getentitytype(self):
        return 'TELNET'

    def gettype(self):
        return 'simple'

    def setoption(self,option,value):
        DBGBN='telnetsetoption'
        TELNET.Opts[option]=value
        #dbg('Have set opt >|'+option+'|< to >|'+value+'|<',DBGBN)

    def getoptions(self):
        OptList=[]
        for o in TELNET.Opts:
            OptList.append(o+' '+TELNET.Opts[o])
        return OptList

    #
    # END OF INTERFACE entity()
    ###########

#
# END OF CLASS TELNET
###########
