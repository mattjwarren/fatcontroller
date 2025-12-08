import time

###########
# START OF CLASS daemonalert
#
class daemonalert:
    def __init__(self,minval,maxval,alertmessage,alertmanager,pass_script,fail_script):
        self.minimum=float(minval)
        self.maximum=float(maxval)
        self.message=alertmessage # @ is xlated as field label/value
        self.set=0
        self.AlertManager=alertmanager
        self.pass_script=pass_script
        self.fail_script=fail_script
        #print "pass_Script=",pass_script,"fail_script=",fail_script#list of cmdlines

    def setmin(self,min):
        self.minimum=float(min)
        self.set=1

    def setmax(self,max):
        self.maximum=float(max)
        self.set=1

    def setmessage(self,alertmessage):
        self.message=alertmessage
        self.set=1

    def getmessage(self):
        return self.message

    def check(self,value,daemon,task,collector,entity):
        value=float(value)
        if self.set:
            if(value<self.minimum or value>self.maximum):
                thetime=time.strftime("%Y-%m-%d %H:%M:%S")
                self.AlertManager.post(thetime+" | "+daemon.name+"-"+task.name+"-"+collector.name+", \'"+entity+"\' "+self.message+" VALUE="+str(value),entity)
                if self.fail_script!='NoScript':
                    self.AlertManager.ExecuteScript(self.fail_script,entity)
            else:
                if self.pass_script!='NoScript':
                    self.AlertManager.ExecuteScript(self.pass_script,entity)
        pass

    def getalert(self):
        return [str(self.minimum),str(self.maximum),self.message,self.pass_script,self.fail_script]

    def isset(self):
        return self.set

    def setmanager(self,alertmanager):
        self.AlertManager=alertmanager

    def setpass_script(self,pscript):
        self.pass_script=pscript

    def setfail_script(self,fscript):
        self.fail_script=fscript

#
#END OF CLASS daemonalert
###########
