import FC_daemon,FC_AlertManager
###########
#START OF CLASS daemonmanager
#

class daemonmanager:

    
    def __init__(self,entitymanager,scheduler,processcommander):
        self.daemons={}
        self.activedaemons={}
        self.EntityManager=entitymanager
        self.Scheduler=scheduler
        self.AlertManager=FC_AlertManager.AlertManager(self.EntityManager,processcommander)

    def getactivedaemons(self):
        """ return a list of active daemon names"""
        return list(self.activedaemons.keys())

    def getprettydaemons(self):
        """ return a list of lines, formatted daemon definitions """
        prettydaemons=[]
        for daemon in self.daemons:
            daemontasks=self.daemons[daemon].gettasks()
            prettydaemons.append('\nDaemon:\t'+daemon+'\n\n\t'+self.daemons[daemon].getschedule().todatestring())
            for task in daemontasks:
                prettydaemons.append('\n\tTask:-')
                taskentities=daemontasks[task].entities
                prettydaemons.append( '\t\t'+task+'\t'+daemontasks[task].tostring()+'\n')
                prettydaemons.append( '\t\tEntities:-')
                entitystring='\t\t'
                for entity in taskentities:
                    entitystring=entitystring+taskentities[entity].getname()+", "
                entitystring=entitystring[:-2]
                prettydaemons.append(entitystring)
                prettydaemons.append( '\n\t\tCollectors:-\t')
                taskcollectors=daemontasks[task].collectors
                for collector in taskcollectors:
                    prettydaemons.append( '\t\t\t'+collector+'->\n\t\t\t\tTAG '+taskcollectors[collector].gettag()+'\n\t\t\t\tSKIP '+taskcollectors[collector].getskip()+'\n\t\t\t\tFORMAT '+taskcollectors[collector].getformat()+'\n\t\t\t\tFILE '+taskcollectors[collector].getfile()+'\n\t\t\t\tALERT '+taskcollectors[collector].getalert())
        return prettydaemons

    def addDaemon(self,name):
        self.daemons[name]=FC_daemon.daemon(self.EntityManager,self.AlertManager,name)
        
    def is_daemon(self,name):
        try:
            self.daemons[name]
            return 1
        except KeyError:
            return 0

    def setdaemonschedule(self,name,begin,end,period):
        self.daemons[name].setschedule(begin,end,period)

    def deleteDaemon(self,name):
        del self.daemons[name]

    def addTask(self,daemon,task,command):
        self.daemons[daemon].addtask(task,command)

    def updateTask(self,daemon,task,command):
        self.daemons[daemon].gettask(task).setcommand(command)

    def deleteTask(self,daemon,task):
        self.daemons[daemon].removetask(task)

    def addCollector(self,daemon,task,collector,tag,skip,format,file):
        self.daemons[daemon].addtaskcollector(task,collector,tag,skip,format,file)

    def deleteCollector(self,daemon,task,collector):
        self.daemons[daemon].removetaskcollector(task,collector)

    def subscribeEntity(self,daemon,task,entity):
        self.daemons[daemon].addtaskentity(task,self.EntityManager.getEntity(entity))

    def unsubscribeEntity(self,daemon,task,entity):
        self.daemons[daemon].removetaskentity(task,self.EntityManager.getEntity(entity))

    def addAlert(self,daemon,task,collector,minval,maxval,message,pass_script,fail_script):
        self.daemons[daemon].addtaskcollectoralert(task,collector,minval,maxval,message,pass_script,fail_script)

    def makeLive(self,daemon):
        self.Scheduler.addPeriodicAction(float(self.daemons[daemon].getschedule().getstart()),int(self.daemons[daemon].getschedule().getperiod()),self.daemons[daemon],daemon)
        self.activedaemons[daemon]='Active'

    def kill_daemon(self,daemon):
        del self.activedaemons[daemon]
        self.Scheduler.unregisterTask(daemon)

    def getdaemondefines(self):
        definelist=[]
        for daemon in self.daemons:
            definelist.append('define daemon '+daemon)
        return definelist

    def getscheduledefines(self):
        definelist=[]
        for daemon in self.daemons:
            schedule=self.daemons[daemon].getschedule()
            definelist.append('define schedule '+daemon+' '+str(schedule.getstart())+' '+str(schedule.getend())+' '+str(schedule.getperiod()))
        return definelist

    def gettaskdefines(self):
        definelist=[]
        for daemon in self.daemons:
            tasks=self.daemons[daemon].gettasks()
            for task in tasks:
                command=tasks[task].command
                definelist.append('define task '+daemon+' '+task+' '+' '.join(command))
        return definelist

    def getcollectordefines(self):
        definelist=[]
        for daemon in self.daemons:
            tasks=self.daemons[daemon].gettasks()
            for task in tasks:
                collectors=tasks[task].collectors
                for collector in collectors:
                    definelist.append('define collector '+daemon+' '+task+' '+collector+' '+collectors[collector].tostring())
        return definelist

    def getalertdefines(self):
        definelist=[]
        for daemon in self.daemons:
            tasks=self.daemons[daemon].gettasks()
            for task in tasks:
                collectors=tasks[task].collectors
                for collector in collectors:
                    definelist.append('define alert '+daemon+' '+task+' '+collector+' '+collectors[collector].getalert())
        return definelist
            

    def getsubscriberdefines(self):
        definelist=[]
        for daemon in self.daemons:
            tasks=self.daemons[daemon].gettasks()
            for task in tasks:
                entities=tasks[task].tentities
                for entity in entities:
                    definelist.append('subscribe entity '+daemon+' '+task+' '+entity)
        return definelist

    def getactivatedefines(self):
        definelist=[]
        for active in self.activedaemons:
            definelist.append('activate daemon '+active)
        return definelist

    def getDaemons(self):
        return self.daemons

    def getDaemon(self,name):
        return self.daemons[name]

    def getOutstandingAlerts(self):
        return self.AlertManager.getOutstandingAlerts()

    def handlealert(self,startindex,endindex):
        self.AlertManager.remove(startindex,endindex)

