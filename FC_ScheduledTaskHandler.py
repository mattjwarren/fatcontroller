###########
# START OF CLASS SCHEDULEDTASKHANDLER
#

import time
from threading import Event, Thread


class ScheduledTaskHandler:
    """
    While the Task class only knows what task to perform with the run()-method, 
    the TaskHandler has all the knowledge about the periodicity of the task.
    Instances of this class are managed by the Scheduler in the
    scheduled, running and onDemand dictionaries.
    """

    ## Init ##

    def __init__(self, scheduler, start, period, task, name):
        DBGBN='scheduledtaskhandler__init__'
        #dbg('Entering... start is '+str(start)+' period '+str(period)+' task '+str(task)+' name '+str(name),DBGBN)
        self._scheduler = scheduler
        self._task = task
        self._name = name
        self._thread = None
        self._isRunning = 0
        self._suspend = 0
        self._lastTime = None
        self._startTime = start
        self._registerTime = time.time()
        self._reregister = 1
        self._rerun = 0
        self._period = abs(period)

    
    ## Scheduling ##
    
    def reset(self, start, period, task, reregister):
        self._startTime = start
        self._period = abs(period)
        self._task = task
        self._reregister = reregister

    def runTask(self):
        """
        Runs this task in the asyncio loop defined in scheduler.
        """
        import asyncio
        if self._suspend:
            self._scheduler.notifyCompletion(self)
            return
        
        self._rerurn = 0
        self._isRunning = 1

        # We need the loop.
        if hasattr(self._scheduler, 'loop') and self._scheduler.loop:
             # Schedule correct coroutine
             asyncio.run_coroutine_threadsafe(self._task._run(self), self._scheduler.loop)
        else:
             # Fallback or Error?
             # Without loop we can't run async daemon.
             print("ERROR: Scheduler has no asyncio loop attached!")
             self._isRunning = 0
             
        # self._thread = Thread(None, self._task._run, self.name(), (self,))
        # self._thread.start()

    def reschedule(self):
        """
        Method to determine whether this task should be rescheduled. Increments the 
        startTime and returns 1 if this is a periodically executed task.
        """
        if self._period == 0:
            return 0
        else:
            if self._lastTime - self._startTime > self._period:  #if the time taken to run the task exceeds the period
                self._startTime = self._lastTime + self._period
            else:
                self._startTime = self._startTime + self._period
            return 1

    def notifyCompletion(self):
        self._isRunning = 0
        self._lastTime =time.time()
        self._scheduler.notifyCompletion(self)
        
        
    ## Attributes ##
    
    def isRunning(self):
        return self._isRunning
    
    def runAgain(self):
        """
        This method lets the Scheduler check to see whether this task should be 
        re-run when it terminates
        """
        return self._rerun

    def isOnDemand(self):
        """
        Returns 1 if this task is not scheduled for periodic execution.
        """
        return self._period == 1

    def runOnCompletion(self):
        """
        Method to request that this task be re-run after its current completion. 
        Intended for on-demand tasks that are requested by the Scheduler while 
        they are already running.
        """
        self._rerun = 1

    def unregister(self):
        """
        Method to request that this task not be kept after its current completion. 
        Used to remove a task from the scheduler
        """
        self._reregister = 0
        self._rerun = 0

    def disable(self):
        """
        Method to disable future invocations of this task.
        """
        self._suspend = 1

    def enable(self):
        """
        Method to enable future invocations of this task.
        """
        self._suspend = 0

    def period(self):
        """
        Returns the period of this task.
        """
        return self._period

    def setPeriod(self, period):
        """
        Mmethod to change the period for this task.
        """
        self._period = period

    def stop(self):
        self._isRunning = 0

    def name(self):
        return self._name

    def startTime(self, newTime=None):
        if newTime:
            self._startTime = newTime
        return self._startTime

#
# END OF CLASS SCHEDULEDTASKMANAGER
###########
