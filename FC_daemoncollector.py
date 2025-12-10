import re,FC_daemonalert,time
import logging

###########
# START OF CLASS daemoncollector
#
class daemoncollector:
    '''Data structure defining how to collect and an alert level.

    A daemoncollector is passed the output of a scheduled execution
    of a command against an entity. tag/skip/format/file define
    how to identify which piece of data, data is written to file
    and optionally tested against an alert.'''
    
    def __init__(self,tag,skip,format,data_filename):
        self.datatag=re.compile(tag)
        self.texttag=tag
        self.skipforward=skip
        self.outformat=format
        self.data_filename=data_filename
        self.alert=FC_daemonalert.daemonalert(0,0,'Alert Not Set',None,'NoScript','NoScript')
        self.lastoutline=''

    def gettag(self):
        return self.texttag

    def getskip(self):
        return self.skipforward

    def getformat(self):
        return self.outformat

    def getalert(self):
        return ' '.join(self.alert.getalert())

    def read(self,DataList,daemon,task,collector,entity):
        #
        #uses tsm_watchme style approach
        #
        # tag - identifies 'hitline(s)' can be regexp
        # skip - lines to skip forward from hitline before collecting data
        #           or COUNT to count number of taged lines instead
        #           skip context of multiline hit's will miss the first x lines
        #
        #   in general multiline hits collect data from each line and test for it
        #
        matchtag=self.datatag
        hitcount=0
        skiplines=self.skipforward
        switchmode=0
        alertedvalue=0
        outline=''
        generatealert=0
        for line in DataList:
            if switchmode>0:
                switchmode=switchmode-1
            else:
                logging.debug(f"MJW: line from scheduled tast is {line}")
            if re.search(self.datatag,line):
                #we have a hit, shall I count it?
                if str(skiplines)=='COUNT':
                    hitcount=hitcount+1
                    #
                else:#not counting it.
                    #if skiplines=0 then collect data, otherwise switch to skip mode
                    if int(skiplines)==0:
                    #
                    # split the line into fields, use format to order and concatenate
                    #
                        outline=''
                        formatfields=self.outformat.split()
                        linefields=line.split()
                        for fieldtoken in formatfields:
                            tokens=str.split(fieldtoken,'^')
                            lbl=tokens[0]
                            label=lbl.replace('_',' ')
                            fieldnum=tokens[1]
                            value=linefields[int(fieldnum)-1]
                        
                            if self.alert.isset():
                                self.alert.check(value,daemon,task,collector,entity)
                                
                            outline=outline+label+str(value)
                    #
                    else:
                        switchmode=skiplines
                        skiplines=0
        if hitcount>0:
            formattokens=str.split(self.outformat,'^')
            label=formattokens[0]
            outline=label+str(hitcount)
            if self.alert.isset():
                self.alert.check(hitcount,daemon,task,collector,entity)
        self.lastoutline=outline
        return None

    def addalert(self,min,max,alertmessage,alertmanager,pass_script,fail_script):
        self.alert.setmin(min)
        self.alert.setmax(max)
        self.alert.setmessage(alertmessage)
        self.alert.setmanager(alertmanager)
        self.alert.setpass_script(pass_script)
        self.alert.setfail_script(fail_script)

    def tostring(self):
        return str(self.texttag)+' '+str(self.skipforward)+' '+str(self.outformat)+' '+str(self.data_filename)
#
# END OF CLASS daemoncollector
###########
