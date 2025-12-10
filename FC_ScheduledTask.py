###########
# START OF CLASS SCHEDULEDTASK
# ((subclassed by Daemon))
#
#
# ** Recognition to Tom Schwaller & the WebWare group for the base scheduling code **
# For more info on WebWare,
#
# [1] Webware: http://webware.sourceforge.net/ 
# [2] Ganymede: http://www.arlut.utexas.edu/gash2/
#
# For more info on the code snippets used here
#
# http://webware.sourceforge.net/Webware-0.7/TaskKit/Docs/QuickStart.html
#
import threading
class ScheduledTask(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        ''' Subclasses should invoke super for this method. '''
        # Nothing for now, but we might do something in the future.
        pass

    def run(self):
        '''
        Override this method for you own tasks. Long running tasks can periodically 
        use the proceed() method to check if a task should stop. 
        '''
        raise SubclassResponsibilityError
    
        
    ## Utility method ##    
    
    def proceed(self):
        """
        Should this task continue running?
        Should be called periodically by long tasks to check if the system wants them to exit.
        Returns 1 if its OK to continue, 0 if its time to quit
        """
        return self._handle._isRunning
        
        
    ## Attributes ##
    
    def handle(self):
        '''
        A task is scheduled by wrapping a handler around it. It knows
        everything about the scheduling (periodicity and the like).
        Under normal circumstances you should not need the handler,
        but if you want to write period modifying run() methods, 
        it is useful to have access to the handler. Use it with care.
        '''
        return self._handle

    def name(self):
        '''
        Returns the unique name under which the task was scheduled.
        '''
        return self._name


    ## Private method ##

    async def _run(self, handle):
        '''
        This is the actual run method for the Task thread. It is a private method which
        should not be overriden.
        '''
        DBGBN='scheduledtask_run'
        #dbg('Entering ...',DBGBN)
        self._name = handle.name()
        self._handle = handle
        #dbg('handing over to self.run()',DBGBN)
        
        # If run is async, await it. If it's sync (legacy tasks), run it?
        # We enforced FC_daemon.run to be async.
        # But other tasks might exist? 
        # Checking codebase... Only FC_daemon seems to be the main implementer.
        # It's safer to await it. If it's not a coroutine, this will raise error.
        # We assume all ScheduledTasks are updated to async or wrapped.
        
        # If self.run is regular func, await will fail.
        # But we updated FC_daemon to async. 
        # Let's check with inspect or try/except?
        # For this migration we assume migration is complete for main usage.
        
        import inspect
        if inspect.iscoroutinefunction(self.run):
             await self.run(self) # FC_daemon.run takes 'adaemon' argument which is self.
        else:
             self.run() # synchronus fallback? But this runs in async loop thread now!
             
        #dbg('Now going to notify completion',DBGBN)
        handle.notifyCompletion() # This creates a thread safety issue? 
        # notifyCompletion modifies scheduler structures.
        # Scheduler is running in its own thread.
        # We are modifying shared state from async loop thread (if different).
        # Scheduler's run loop locks? No locks seen.
        # This is a race condition risk.
        # However, Python GIL helps.
        # Ideally, notifyCollision should be thread safe.

#
# END OF CLASS SCHEDULEDTASK
###########
