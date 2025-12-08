import logging
class AlertManager:
    def __init__(self,EntityManager,processcommander):
        self.AlertQueue=[] # append message,id tuples
        self.EntityManager=EntityManager
        self.processcommander=processcommander

    def post(self,message,entityname):
        self.AlertQueue.append((message,entityname))
        self.EntityManager.SetAlertStatus(entityname)
        if len(self.AlertQueue)>0:
            self.processcommander.indicate_alert_state()
                        
    def remove(self,start,end=None):
        #get set of all entities with alerts
        ents=[]
        for alert in self.AlertQueue:
            ents.append(alert[1])
        entset=set(ents)
        if end==None:
            end=start
        try:
            del self.AlertQueue[start:end]
        except:
            logging.error(f"Problem handling alert range {start}-{end-1}")
        ents=[]
        for alert in self.AlertQueue:
            ents.append(alert[1])
        entsetB=set(ents)
        clearedents=entset-entsetB
        for ent in clearedents:
            self.EntityManager.ClearAlertStatus(ent)
        if len(self.AlertQueue)==0:
            self.processcommander.reset_alert_indicator()

    def ExecuteScript(self,script,entityname): # EXECS 'ENTITY' based scripts, NOT FC scripts
        #setup substitution scriptname_AlertEntity
        #make substitution ~ALERT_ENTITY=entityname
        self.processcommander.processcommand('sub ALERT_ENTITY '+entityname)
        self.processcommander.processcommand('run '+script)
        self.processcommander.processcommand('del sub ALERT_ENTITY')
                

    def getOutstandingAlerts(self):
        alerts=[]
        for items in self.AlertQueue:
            alerts.append(items[0])
        return alerts

