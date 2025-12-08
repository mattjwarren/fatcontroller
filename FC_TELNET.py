import FC_entity
import logging
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
                if TELNET.Opts['SHOWRAWTELNET'] =='yes':
                    C.set_debuglevel(65535)
            except KeyError:
                pass
            #dbg('expecting [lL]ogin: ',DBGBN)
            index,match,text=C.expect(['[Ll]ogin: '],10)
            #if index != -1:
                #dbg('gotit',DBGBN)
            #else:
                #dbg('missed',DBGBN)
            #dbg('writing self.TELNETUser\\r',DBGBN)
            C.write(self.TELNETUser+'\r')
            #dbg('expecting [pP]assword: ',DBGBN)
            index,match,text=C.expect(['[Pp]assword: '],10)
            #if index != -1:
                #dbg('gotit',DBGBN)
            #else:
                #dbg('missed',DBGBN)
            promptexpect=['.*'+self.TELNETUser+'.*']
            #dbg('writing self.TELNETPass\\r',DBGBN)
            C.write(self.TELNETPass+'\r')
            #dbg('expecting '+' '.join(promptexpect),DBGBN)
            index,match,text=C.expect(promptexpect,10)
            #if index != -1:
                #dbg('gotit',DBGBN)
            #else:
                #dbg('missed',DBGBN)
            #dbg('writing PS1=\'_FC_>\'\\r',DBGBN)
            C.write('PS1=\'_FC_>\'\r')
            #dbg('expecting _FC_>',DBGBN)
            index,match,text=C.expect(['_FC_>'],10)
            #if index != -1:
                #dbg('gotit',DBGBN)
            #else:
                #dbg('missed',DBGBN)
            #dbg('writing export PS1\\r',DBGBN)
            C.write('export PS1\r')
            #dbg('expecting _FC_>',DBGBN)
            index,match,text=C.expect(['_FC_>'],10)
            #if index != -1:
                #dbg('gotit',DBGBN)
            #else:
                #dbg('missed',DBGBN)
            try:
                if TELNET.Opts['ShowRawTelnet'] =='yes':
                    C.set_debuglevel(0)
            except KeyError:
                pass
            return C
        except (telnetlib.socket.gaierror, telnetlib.socket.error):
            TELNET.Connections[self.Name]=self.Name
            logging.warning('Warning: TELNET entity '+self.Name+' could not open telnet connection to '+self.TCPAddress+':'+self.TCPPort)
            return self.Name
        
    ###########
    # START OF INTERFACE entity()
    #

    Opts={} #dict of options

    def execute(self,CmdList):
        if CmdList:
            #C=TELNET.Connections[self.Name]
            C=self.Connection
            if C!=self.Name:
                #special bit here to handle telnetlib's 'INTERACT' ability
                if ' '.join(CmdList)=='__interact':
                    retkey=''
                    global system
                    if system=='UNIX':
                        retkey='^D'
                    else:
                        retkey='^Z'
                    logging.info('\nTELNET entity '+self.Name+' entering INTERACT mode. Use '+retkey+' to come back\n')
                    C.mt_interact()
                    return ['']
                else:
                    try:
                        #dbg('checking for Opt SHOWRAWTELNET got '+TELNET.Opts['SHOWRAWTELNET'],DBGBN)
                        if TELNET.Opts['SHOWRAWTELNET'] =='yes':
                            C.set_debuglevel(65535)
                    except KeyError:
                        pass
                    Abort=0
                    while Abort<2:
                        try:
                            C.write(' '.join(CmdList)+'\r')
                            #dbg('expecting _FC_> ',DBGBN)
                            index,match,text=C.expect(['_FC_>'],10)
                            #if index != -1:
                                #dbg('gotit',DBGBN)
                            #else:
                                #dbg('missed',DBGBN)
                            Abort=2
                        except (telnetlib.socket.error, EOFError):
                            logging.info('Info: TELNET entity '+self.Name+' had trouble. Reseting connection.')
                            if Abort:
                                logging.warning('Warning: TELNET entity '+self.Name+' connection aborted.')
                                C=self.Name
                                return ['']
                            C=TELNET.Connections[self.Name]=self.openconnection()
                            Abort+=1
                    Output=text.split('\n')
                    return  Output
                if TELNET.Opts['ShowRawTelnet'] =='yes':
                    C.set_debuglevel(0)
            else:
                logging.info('Info: Entity failed to initialise telnet; retrying')
            try:
                #dbg('making connection...',DBGBN)
                C=TELNET.Connections[self.Name]=telnetlib.Telnet(self.TCPAddress)
                #dbg('expecting [lL]ogin: ',DBGBN)
                index,match,text=C.expect(['[lL]ogin: '],10)
                #if index != -1:
                    #dbg('gotit',DBGBN)
                #else:
                    #dbg('missed',DBGBN)
                C.write(self.TELNETUser+'\r')
                #dbg('expecting [pP]assword: ',DBGBN)
                index,match,text=C.expect(['[pP]assword: '],10)
                #if index != -1:
                    #dbg('gotit',DBGBN)
                #else:
                    #dbg('missed',DBGBN)
                C.write(self.TELNETPass+'\r')
                #dbg('expecting \\r\\n[a-eA-E]:\\\\\\\\.*> ',DBGBN)
                index,match,text=C.expect(['\r\n[a-eA-E]:\\\\.*>'],10)
                #if index != -1:
                    #dbg('gotit',DBGBN)
                #else:
                    #dbg('missed',DBGBN)
                C.write('PS1=\'_FC_>\'\r')
                #dbg('expecting _FC_> ',DBGBN)
                index,match,text=C.expect(['_FC_>'],10)
                #if index != -1:
                    #dbg('gotit',DBGBN)
                #else:
                    #dbg('missed',DBGBN)
                C.write('export PS1\r')
                #dbg('expecting _FC_> ',DBGBN)
                index,match,text=C.expect(['_FC_>'],10)
                #if index != -1:
                    #dbg('gotit',DBGBN)
                #else:
                    #dbg('missed',DBGBN)
                C.write(' '.join(CmdList)+'\r')
                #dbg('expecting _FC_> ',DBGBN)
                index,match,text=C.expect(['_FC_>'],30)
                #if index != -1:
                    #dbg('gotit',DBGBN)
                #else:
                    #dbg('missed',DBGBN)
                Output=text.split('\n')
                try:
                    if TELNET.Opts['ShowRawTelnet'] =='yes':
                        C.set_debuglevel(0)
                except KeyError:
                    pass
                return  Output
            except (telnetlib.socket.gaierror, telnetlib.socket.error):
                TELNET.Connections[self.Name]=self.Name
                logging.warning('Warning: TELNET entity '+self.Name+' could not open telnet connection to '+self.TCPAddress+':'+self.TCPPort)
                return ['']
            
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
        list=parmstring.split()
        return list


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
