import FC_ScheduledTask,FC_daemonschedule,FC_daemontask,os,time
import config
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

####################
# START OF CLASS daemon
#
class daemon(FC_ScheduledTask.ScheduledTask):
    '''A top level object holding info for scheduled commands.

	A daemon consists of a schedule and a group of tasks. each
	task is a group of entities and collectors and a command. Each
	collector is a set of rules for extracting data from the results
	of cmd run against each entity, and an optional alert set on that data.'''

    def __init__(self,entitymanager,alertmanager,name):
        FC_ScheduledTask.ScheduledTask.__init__(self)
        '''Parms.

        entitymanager is an entitymanager object the daemon can ask to execute the command
        using the scheduledexecute(EntityName,Cmd) method
        scheduler is the scheduler handling the executions, needed so
        daemon can rescheule itself for period units in the future'''
        self.name=name
        self.processor=entitymanager
        self.tasks={}
        self.schedule=FC_daemonschedule.daemonschedule()
        self.AlertManager=alertmanager

    async def run(adaemon): #adaemon
        import logging
        import asyncio
        import time
        import os
        
        # dbg('Starting run for >|'+adaemon.name+'|<',DBGBN)
        for task_name, task in list(adaemon.tasks.items()):
            # dbg('Doing task >|'+task_name+'|<',DBGBN)
            
            # The original code seemingly had a variable naming issue with 'tsk'. 
            # We assume tsk meant task_name.
            
            entities = list(task.entities.items())
            for entity_name, entity in entities:
                try:
                    # execute is now async
                    cmd_output = await entity.execute(task.command)
                    
                    collectors = list(task.collectors.items())
                    for collector_name, collector in collectors:
                        # collector.read logic seems synchronous and cpu bound mostly (parsing).
                        # We can run it directly or wrap it if very expensive.
                        # Assuming fast enough for now.
                        collector.read(cmd_output, adaemon, task, collector, entity)
                        
                        collectorfile = collector.data_filename
                        if collectorfile is not None:
                            outfile_path = os.path.join(config.data_path, collectorfile)
                            # Append extra info to filename specific to this run context?
                            # Original: outfile_path=outfile_path+("_%s_%s_%s_%s" % (adaemon.name,tsk,ent,collector.name))
                            # Fixing var names:
                            outfile_path = outfile_path + ("_%s_%s_%s_%s" % (adaemon.name, task_name, entity_name, collector.name)) 
                            
                            try:
                                with open(outfile_path, 'a') as outfile:
                                    timestamp = str(time.ctime(float(time.time())))
                                    outfile.write(timestamp + ',' + collector.lastoutline + '\n')
                            except Exception as e:
                                logging.error(f"Error writing collector output: {e}")
                                
                except Exception as e:
                    logging.error(f"Error executing task {task_name} on entity {entity_name}: {e}")

    def setschedule(self,start,end,period):
        self.schedule.updateschedule(start,end,period)

    def getschedule(self):
        return self.schedule

    def addtask(self,name,command):
        self.tasks[name]=FC_daemontask.daemontask(name,command)

    def gettasks(self):
        return self.tasks #returns dict of tasks

    def gettask(self,name):
        return self.tasks[name] #returns single task

    def removetask(self,name):
        del self.tasks[name]

    def addtaskcollector(self,taskname,collectorname,tag,skip,format,file):
        self.tasks[taskname].addcollector(collectorname,tag,skip,format,file)

    def addtaskcollectoralert(self,taskname,collectorname,minval,maxval,alertmessage,pass_script,fail_script):
        self.tasks[taskname].addcollectoralert(collectorname,minval,maxval,alertmessage,self.AlertManager,pass_script,fail_script)

    def removetaskcollector(self,taskname,collectorname):
        self.tasks[taskname].removecollector(collectorname)

    def addtaskentity(self,taskname,entity):
        self.tasks[taskname].addentity(entity)

    def removetaskentity(self,taskname,entity):
        self.tasks[taskname].removeentity(entity)

    def getnumtasks(self):
        return len(self.tasks)

#
# END OF CLASS DAEMON
###########
