import FC_entity,os,subprocess,shutil
import logging
import asyncio

###########
# Some POSIX / winos setups ((this needs to be moved out of here. FC should
# provide 'environment' services to entities.
#
# Sets up disk 'root', point where all filenames
# for collector output etc.. are generated from.
# will make configurable option at some point...

if os.name=='posix':
    system='UNIX'
    installroot='/opt/yab/FatController/'
    copycmd='cp'
    driveroot=installroot
else:
    system='WINDOWS'
    installroot='c:\\program files\\yab\\FatController\\'
    copycmd='copy'
    driveroot='c:\\'
#
#
#####################

###########
# START OF CLASS TSM
# implements entity()
#

class TSM(FC_entity.entity):


    ConfigManagers={} #{'name':'group'}
    
    # Static initialization logic
    tsmroot = ''
    optroot = ''
    tsmadmincmd = ''
    tsmcleanadmincmd = ''

    if os.name=='posix':
        try:
            p = subprocess.Popen('uname -a | awk \'{print $1}\'', shell=True, stdout=subprocess.PIPE, text=True)
            output, _ = p.communicate()
            output = output.strip()
            if output=='AIX':
                tsmroot='/usr/tivoli/tsm/client/ba/bin/'
            else:
                tsmroot='/opt/tivoli/tsm/client/ba/bin/'
            optroot='FC_OPT/'
            tsmadmincmd='dsmadmc'
            tsmcleanadmincmd='dsmadmc -dataonly=yes'
        except Exception:
            pass 
    else:
        tsmroot='c:\\program files\\tivoli\\tsm\\baclient\\'
        optroot='FC_OPT\\'
        tsmadmincmd='dsmadmc.exe'
        tsmcleanadmincmd='dsmadmc.exe -dataonly=yes'

    def __init__(self,Name,Type,LL,HL,AdminUser,AdminPass):
        self.Name=Name
        self.Type=Type
        self.LL=LL
        self.HL=HL
        self.AdminUser=AdminUser
        self.AdminPass=AdminPass
        if self.Type=='single':
            self.dosingleserversetup()
        else:
            #type is configmanager()
            self.doconfigmanagersetup()   # automatically sets up a group of TSM server entities
                            # of disocvered servers.
                            #  with configmanager as group primary.

    def dosingleserversetup(self):
        return

    def doconfigmanagersetup(self):
        TSM.ConfigManagers[self.Name]=self.Name+'_ConfigManager'
        #find other servers
        #define 'em as entities
        #group 'em up here for excecute shennanigans later
        return

    ###########
    #Begin Interface entity()
    #

    Opts={}

    async def execute(self,CmdList, trace_id=None):
        loop = asyncio.get_event_loop()
        
        def blocking_tsm_execute():
            #Original synchronous logic wrapped here
            
            src_opt = os.path.join(TSM.tsmroot, TSM.optroot, self.Name + '.opt')
            dst_opt = os.path.join(TSM.tsmroot, 'dsm.opt')
            src_sys = os.path.join(TSM.tsmroot, TSM.optroot, self.Name + '.sys')
            dst_sys = os.path.join(TSM.tsmroot, 'dsm.sys')
            
            try:
                # Use shell copy for robustness as per original code preference
                subprocess.run(f'{copycmd} "{src_opt}" "{dst_opt}"', shell=True, check=False)
                if os.name=='posix':
                    subprocess.run(f'{copycmd} "{src_sys}" "{dst_sys}"', shell=True, check=False)
            except Exception as e:
                logging.error('ERROR: System error on copying TSM optfile - Have you created your FC_OPT dir and .opt files? ' + str(e))
                

            #PROCESS CLASS OPTIONS SPECIFIC TO EXECUTION
            if 'DATAONLY' in TSM.Opts and TSM.Opts['DATAONLY']=='yes':
                runcmd=TSM.tsmcleanadmincmd
            else:
                runcmd=TSM.tsmadmincmd
            
            CmdString=runcmd+' -id='+self.AdminUser+' -pa='+self.AdminPass+' '+' '.join(CmdList)
            if os.name!='posix':
                CmdString=CmdString.replace('\\','')
                
            outputlines = []
            try:
                # Don't change CWD globally, use cwd arg
                p = subprocess.Popen(CmdString, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=TSM.tsmroot, text=True)
                CmdOut, CmdErr = p.communicate()
                
                outputlines = CmdOut.splitlines()
                errorlines = CmdErr.splitlines()
                
                for line in errorlines:
                    logging.error(line)
            except OSError:
                logging.warning('Warning: System error on subprocess, TSM entity '+self.Name+' failed command.')
                return ['']
            return outputlines

        return await loop.run_in_executor(None, blocking_tsm_execute)
    
    def getparameterdefs(self):
        '''Should return a dict of parm:parmtype pairs for the GUI
        to build a config box'''
        #tsm parms are name,type,host,port,user,pwd
        return ["Name","Type","Host","Port","User","Pwd"]
    

    def display(self,LineList,OutputCtrl):
        for line in LineList:
            try:
                OutputCtrl.insert("end", line.rstrip()+"\n")
            except:
                pass

    def getname(self):
        return self.Name

    def getparameterstring(self):
        return self.Type+' '+self.LL+' '+self.HL+' '+self.AdminUser+' '+self.AdminPass

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        parmstring=self.getparameterstring()
        lst=parmstring.split()
        return lst


    def getentitytype(self):
        return 'TSM'

    def gettype(self):
        return self.Type

    def setoption(self,option,value):
        DBGBN='tsmsetoption'
        #dbg('setting option '+option+' to '+value,DBGBN)
        TSM.Opts[option]=value

    def getoptions(self):
        DBGBN='tsmgetoptions'
        OptList=[]
        for o in TSM.Opts:
            #dbg('Found option '+o+' with value :'+TSM.Opts[o]+': in class TSM',DBGBN)
            OptList.append(o+' '+TSM.Opts[o])
        return OptList

    #
    #End Interface Entity
    ###########
#
# END OF CLASS TSM(entity)
###########
