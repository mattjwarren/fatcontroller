
import FC_LOCAL,FC_TSM,FC_TELNET,FC_DUMB,FC_ENTITYGROUP, FC_SSH
import FC_formatter
import tkinter as tk
from tkinter import ttk

###########
# START OF CLASS entitymanager
#

imageroot='./' # simplified for now

class entitymanager:

#
#Method functions
#
    def __init__(self, OutputNotebook, FocusReturnCtrl):
        self.Entities={} #dict of entity objects
        self.OutBook = OutputNotebook # This is now a ttk.Notebook
        self.OutPages={} #entity name keyed, value is dict or list info
        
        # We will skip image loading for now or implement it later with Pillow if needed
        # For alerts we will stick to text indicators in tab titles
        
        self.ReturnFocus=FocusReturnCtrl
                
        self.LastExecutedEntity=''
        
        # In Tkinter, we assume OutputNotebook is already set up.
        # The 'GENERAL' tab is index 0.
        # We need to find the text widget in it.
        # Let's assume FatController sets up the GENERAL tab and passes the Text widget via the Formatter,
        # or we find it.
        # But wait, self.display uses OutputFormatter.
        # OutputFormatter now expects a set_text_widget call or we pass it.
        
        pass # We will rely on define() to create tabs
        
        # self.GeneralPage=OutputNotebook.GetPage(0).GetChildren()[0] # Old generic way
        # In new FatController, we will pass the "General" text widget or formatter will know it.
        
        self.HighestPageNumber=1 #post increment. first is 1
        self.display=FC_formatter.OutputFormatter(OutputNotebook, self.ReturnFocus)
        # We need to hook up the general tab text widget to the formatter
        # We'll assume the caller (FatController) handles the initial set_text_widget for the general tab?
        # Or we can find it.
        try:
             # Assuming the first tab is General and has a Text frame
             frame = self.OutBook.nametowidget(self.OutBook.tabs()[0])
             text_widget = frame.winfo_children()[0]
             self.display.set_text_widget(text_widget)
        except Exception:
             pass

    def SetAlertStatus(self, EntityName):
        # self.OutBook.SetPageImage(self.OutPages[EntityName][3]-1,0)
        # Change tab title to indicate alert
        try:
            tab_id = self.OutPages[EntityName]['tab_id']
            # current_text = self.OutBook.tab(tab_id, "text")
            self.OutBook.tab(tab_id, text="[!] " + EntityName)
        except:
            pass

    def ClearAlertStatus(self, EntityName):
        # self.OutBook.SetPageImage(self.OutPages[EntityName][3]-1,2)
        try:
            tab_id = self.OutPages[EntityName]['tab_id']
            self.OutBook.tab(tab_id, text=EntityName)
        except:
            pass


    def getentitytype(self, EntityName: str) -> str:
        return self.Entities[EntityName].getentitytype()
        
    def getentitylist(self) -> dict:
        return self.Entities
        
    def getentityparms(self,EntityName):
        return self.Entities[EntityName].getparameterstring()

    # # Need to change this, coupling between entitymanager and entities. Shouldnt need to know numb of parms needed
    def define(self, type: str, typeparms: list) -> None:                                #TSMServer tpyeparms;    ['name','adminuser','adminpass']
        EntityName = None
        if type=='TSM':                                 #becomes Entites{'name',['adminuser','adminpass']}
            if len(typeparms)==6:
                EntityName=typeparms[0]
                self.Entities[EntityName]=FC_TSM.TSM(EntityName,typeparms[1],typeparms[2],typeparms[3],typeparms[4],typeparms[5]) # {'name',<TSM object>}
                self.display.infodisplay('Entity: TSM '+self.Entities[EntityName].getname()+" "+self.Entities[EntityName].getparameterstring()+" defined.")
            else:
                self.display.infodisplay('Error: Wrong number parameters for TSM entity.')
        elif type=='TELNET':
            if len(typeparms)==5:
                EntityName=typeparms[0]
                self.Entities[EntityName]=FC_TELNET.TELNET(EntityName,typeparms[1],typeparms[2],typeparms[3],typeparms[4])
                self.display.infodisplay('Entity: TELNET '+self.Entities[EntityName].getname()+" "+self.Entities[EntityName].getparameterstring()+" defined.")
            else:
                self.display.infodisplay('Error: Wrong number of parameters for TELNET entity.')
        elif type=='DUMB':
            if len(typeparms)==1:
                EntityName=typeparms[0]
                self.Entities[EntityName]=FC_DUMB.DUMB(EntityName)
                self.display.infodisplay('Entity: DUMB '+self.Entities[EntityName].getname()+" "+self.Entities[EntityName].getparameterstring()+" defined.")
            else:
                self.display.infodisplay('Error: Wrong number of parameters for DUMB entity.')
        elif type=='LOCAL':
            if len(typeparms)==1:
                EntityName=typeparms[0]
                self.Entities[EntityName]=FC_LOCAL.LOCAL(EntityName)
                self.display.infodisplay('Entity: LOCAL '+self.Entities[EntityName].getname()+" "+self.Entities[EntityName].getparameterstring()+" defined.")
            else:
                self.display.infodisplay('Error: Wrong number of parameters for LOCAL entity.')
        elif type=='SSH':
            if len(typeparms)==5:
                EntityName=typeparms[0]
                self.Entities[EntityName]=FC_SSH.SSH(*typeparms)
                self.display.infodisplay('Entity: SSH '+self.Entities[EntityName].getname()+" "+self.Entities[EntityName].getparameterstring()+"         defined.")
            else:
                self.display.infodisplay('Error: Wrong number of parameters for SSH entity.')
        elif type=='ENTITYGROUP':
            EntityName=typeparms[0]
            self.Entities[EntityName]=FC_ENTITYGROUP.ENTITYGROUP(EntityName,typeparms[1:],self)
            self.display.infodisplay('Entity: ENTITYGROUP '+self.Entities[EntityName].getname()+" "+self.Entities[EntityName].getparameterstring()+" defined.")
        else:
            self.display.infodisplay('Error: Don\'t know how to define '+type+' entities.')
            
        #Now attach an output page
        try:
            if EntityName:
                # Create a frame for the tab
                tab_frame = ttk.Frame(self.OutBook)
                self.OutBook.add(tab_frame, text=EntityName)
                
                # Create text widget
                text_widget = tk.Text(tab_frame, wrap=tk.WORD, width=80, height=24)
                text_widget.pack(expand=True, fill='both')
                
                text_widget.insert(tk.END, 'Entity Defined.\n')
                
                # Store info
                # We need to store logic to access this.
                # Old code used list: [panel, textctrl, sizer, number]
                # We'll use a dict
                self.OutPages[EntityName] = {
                    'frame': tab_frame,
                    'text': text_widget,
                    'tab_id': self.HighestPageNumber # Index
                }
                
                self.HighestPageNumber+=1
                
        except Exception as e:
            self.display.infodisplay('Exception caught in entitymanager define: ' + str(e))
            pass


    def execute(self, EntityName: str, CmdList: list) -> None:
        DBGBN='entitymanagerexecute'
        try:
            EntityType=self.Entities[EntityName].getentitytype()
            output=self.Entities[EntityName].execute(CmdList) #list of output returned
            
            # Select the tab
            try:
                self.OutBook.select(self.OutPages[EntityName]['tab_id'])
            except:
                pass
                
            self.Entities[EntityName].display(output, self.OutPages[EntityName]['text'])
            self.OutPages[EntityName]['text'].see(tk.END)
            self.ReturnFocus.focus_set()
            self.LastExecutedEntity=EntityName
        except KeyError:
            self.display.infodisplay('Error:    Don\'t know how to execute commands for '+EntityName+'.')

    def scheduledexecute(self,entity,cmd_list):
        EntityType=entity.getentitytype()
        output=entity.execute(cmd_list) #list of output returned
        return output

    def display(self,EntityName,OutputList):
        #self.display.infodisplay('Changing page selected index to '+str(self.OutPages[EntityName][3]))
        try:
            self.OutBook.select(self.OutPages[EntityName]['tab_id'])
            self.Entities[EntityName].display(OutputList, self.OutPages[EntityName]['text'])
            self.OutPages[EntityName]['text'].see(tk.END)
            self.ReturnFocus.focus_set()
        except:
             pass

    def show(self):
        for e in self.Entities:
            self.display.infodisplay(''+self.Entities[e].getentitytype()+'\t'+e+'\t'+self.Entities[e].getparameterstring())
        self.display.infodisplay('')

    def getdefines(self): #Returns a list of strings, each string returned is the define command for the entity
        DBGBN='entitymanagergetdefines'
        DefineList=[]
        #dbg('starting to loop through self.entities',DBGBN)
        for e in self.Entities:
            #dbg('doing entity '+self.Entities[e].getname(),DBGBN)
            EntityType=self.Entities[e].getentitytype()
            ParmList=self.Entities[e].getparameterstring()
            DefineList.append('define entity '+EntityType+' '+e+' '+ParmList)
        #dbg('leaving entitymanagergetdefines',DBGBN)
        return DefineList

    def delete(self,EntityName):
        del self.Entities[EntityName]

    def isEntity(self, EntityName: str) -> int:
        try:
            self.Entities[EntityName]
            return 1
        except KeyError:
            return 0

    def getEntity(self,EntityName):
        return self.Entities[EntityName]

    def SetClassOption(self,EntityClass,option,value):
        DBGBN='entitymanagersetclassoption'
        #dbg('option '+option+' value '+value+' for entity class '+EntityClass,DBGBN)
        for e in self.Entities:
            if self.Entities[e].getentitytype()==EntityClass: #CHANGED INCIDENTALLY FRMO gettype() WARNING!!!!!!!!!
                #dbg('setting option >|'+option+'|< to value >|'+value+'|< for entity class >|'+EntityClass+'|<',DBGBN)
                self.Entities[e].setoption(option,value)
                break #only do one ## New!: should set classlvel attribute instead? (monkeypatch)

    def getentitytypes(self):
        types=[]
        for e in self.Entities:
            etype=self.Entities[e].getentitytype()
            if etype not in types:
                types.append(etype)
        return types

    def displayclassoptions(self):
        doneclasses={}
        for e in self.Entities:
            try:
                if doneclasses[self.Entities[e].getentitytype()]:
                    pass
            except KeyError:
                doneclasses[self.Entities[e].getentitytype()]='done'
            for option in self.Entities[e].getoptions():
                    self.display.infodisplay(self.Entities[e].getentitytype()+' '+option)

    def getclassoptiondefines(self):
        DBGBN='entitymanagergetclassoptiondefines'
        doneclasses={}
        OptList=[]
        formattedlist=[]
        for e in self.Entities:
            try:
                #dbg 'Checking if have got classoptiondefines for entitytype '+self.Entities[e].getentitytype(),DBGBN)
                if doneclasses[self.Entities[e].getentitytype()]:
                    #dbg('key found in doneclasses, I Have!',DBGBN)
                    pass
            except KeyError:
                #dbg('Havent got them for this entity type yet. Getting....',DBGBN)
                #dbg('setting doneclasses[self.Entities[e].getentitytype() {'+self.Entities[e].getentitytype()+'} to done',DBGBN)
                doneclasses[self.Entities[e].getentitytype()]='done'
            rawlist=self.Entities[e].getoptions()
            if len(rawlist)>0:
                #dbg('formatting the rawlist options',DBGBN)
                for l in rawlist:
                    #dbg('l is '+l,DBGBN)
                    #dbg('adding \'set '+self.Entities[e].getentitytype()+' '+l+'\'',DBGBN)
                    formattedlist.append('set '+self.Entities[e].getentitytype()+' '+l)
                    #dbg('appending formatted list to optlist',DBGBN)
                OptList.append(formattedlist)
                formattedlist=[]
        return OptList # list of lists


#
# END OF CLASS entitymanager
###########
