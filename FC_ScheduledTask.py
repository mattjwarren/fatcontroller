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
import logging
import uuid
import inspect

class ScheduledTask(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        ''' Subclasses should invoke super for this method. '''
        self.current_trace_id = None
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
        self.current_trace_id = str(uuid.uuid4())[:8] # Short trace ID
        log_prefix = f"[{self.current_trace_id}]"
        
        logging.debug(f"{log_prefix} ScheduledTask _run starting for {handle.name()}")
        
        self._name = handle.name()
        self._handle = handle
        
        try:
            if inspect.iscoroutinefunction(self.run):
                 await self.run(self) # FC_daemon.run takes 'adaemon' argument which is self.
            else:
                 logging.warning(f"{log_prefix} Executing synchronous run method in async loop!")
                 self.run() 
        except Exception as e:
            logging.error(f"{log_prefix} Error in ScheduledTask _run: {e}", exc_info=True)
             
        logging.debug(f"{log_prefix} ScheduledTask _run completed for {handle.name()}")
        handle.notifyCompletion()

#
# END OF CLASS SCHEDULEDTASK
###########
