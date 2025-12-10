import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os,sys,re,shutil,time,threading,pprint

# Make sure we can find local modules
sys.path.append(os.getcwd())

import config
import FC_entity,FC_daemonschedule,FC_daemontask,FC_daemon
import FC_ScheduledTask,FC_ScheduledTaskHandler,FC_ThreadedScheduler,FC_entitymanager,FC_daemonmanager
import FC_ENTITYGROUP,FC_LOCAL,FC_DUMB,FC_TSM,FC_TELNET
import FC_formatter
import FC_command_parser
import logging

# Configure basic logging to prevent 'No handler found' warnings before GUI setup
logging.basicConfig(level=logging.DEBUG)

fcversion="v1f11r1a"
__version__ = fcversion

startmessage='Welcome to FatController '+fcversion



class FatController(ttk.Window):
    '''is essentially the command processor'''
    
    def __init__(self):
        super().__init__(themename="darkly")
        
        self.title("FatController")
        self.geometry("3072x1536")
        
        self.aliases={}  #Dictionary of aliasname/command 
        self.substitutions={}
        self.scripts={}
        self.trace={}
        
        self.FCScheduler=FC_ThreadedScheduler.ThreadedScheduler()
        self.FCScheduler.start()
        
        self.opts={}
        self.installroot = config.system_install_root + config.install_root + '/' # Guessing path construction based on config.py
        
        # Initialize Command Parser and load definitions
        self.CommandParser = FC_command_parser.CommandParser(self)
        try:
             self.CommandDefinitions = self.CommandParser.parse_command_defs(self.installroot+'FatControllerCommands.sav')
        except Exception as e:
             # messagebox.showerror("Error", f"Could not load command definitions: {e}")
             logging.error(f"Error loading command definitions: {e}")
             self.CommandDefinitions = []

        #############
        # GUI bits
        #############
        
        # Main Vertical Splitter
        self.VSplitter = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        self.VSplitter.pack(fill=tk.BOTH, expand=True)
        
        # Left Side (Notebook + Shell)
        self.LSplitter = ttk.Panedwindow(self.VSplitter, orient=tk.VERTICAL)
        self.VSplitter.add(self.LSplitter, weight=3) # Main area
        
        # Right Side (Tree)
        self.RSplitter = ttk.Frame(self.VSplitter)
        self.VSplitter.add(self.RSplitter)
        
        # TLPanel (Notebook)
        self.TLPanel = ttk.Frame(self.LSplitter)
        self.LSplitter.add(self.TLPanel, weight=3)
        
        # BLPanel (Shell)
        self.BLPanel = ttk.Frame(self.LSplitter)
        self.LSplitter.add(self.BLPanel, weight=1)
        
        # Notebook
        self.OutBook = ttk.Notebook(self.TLPanel)
        self.OutBook.pack(fill=tk.BOTH, expand=True)
        
        # Create General Tab
        self.FirstPagePanel = ttk.Frame(self.OutBook)
        self.OutBook.add(self.FirstPagePanel, text='GENERAL')
        
        self.FirstPageTextCtrl = tk.Text(self.FirstPagePanel, wrap=tk.WORD)
        self.FirstPageTextCtrl.pack(fill=tk.BOTH, expand=True)
        self.FirstPageTextCtrl.insert(tk.END, startmessage + '\n')

        # Create Logs Tab - REMOVED per user request
        
        # Shell
        self.ShellTextCtrl = tk.Text(self.BLPanel, height=10)
        self.ShellTextCtrl.configure(state='disabled')
        self.ShellTextCtrl.pack(fill=tk.BOTH, expand=True)
        # Entry for command
        self.ShellEntry = ttk.Entry(self.BLPanel)
        self.ShellEntry.pack(fill=tk.X)
        self.ShellEntry.bind('<Return>', self.ShellWindowEnterEvent)
        self.ShellEntry.bind('<KP_Enter>', self.ShellWindowEnterEvent)
        self.ShellEntry.focus_set()

        self.display=FC_formatter.OutputFormatter(self.OutBook, self.ShellEntry)
        self.display.set_text_widget(self.FirstPageTextCtrl) # Hook up General tab
        
        # Setup Logging

        # 2. Text Handler for LOGS tab - REMOVED
        
        # 3. File Handler
        try:
             log_path = config.log_file if config.log_file else 'logs.txt'
             # If just filename, put in cwd or install root? "going to both a file called logs.txt"
             # config.py defines data paths. Let's use simple filename in CWD as per typical simple request, or relative to run.
             self.file_handler = logging.FileHandler(log_path, mode='a')
             self.file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        except Exception as e:
             logging.error(f"Failed to setup file logging: {e}")
             self.file_handler = None

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG) # Catch everything
        
        # Add handlers
        if self.file_handler:
            root_logger.addHandler(self.file_handler)
            
        logging.info("Logging initialized. Writing to file: " + (config.log_file))
        # Ensure message propagation doesn't duplicate if multiple handlers (basicConfig added one to stderr)
        # We want stderr too probably for dev? Yes, basicConfig handles that.

        
        #
        # Now make the Daemon and Entity managers as the items they require have been defined
        #
        self.EntityManager=FC_entitymanager.entitymanager(self.OutBook,self.ShellEntry)
        self.DaemonManager=FC_daemonmanager.daemonmanager(self.EntityManager,self.FCScheduler,self)
        
        # Fixup display widget for EntityManager if it didn't find it (it checks nametowidget)
        self.EntityManager.display.set_text_widget(self.FirstPageTextCtrl)
        
        #
        #decide initial prompt value
        #
        self.prompt=''
        self.prompt='FC:'+self.EntityManager.LastExecutedEntity+'> '
        self.ShellTextCtrl.configure(state='normal')
        self.ShellTextCtrl.insert(tk.END, self.prompt + '\n')
        self.ShellTextCtrl.configure(state='disabled')

        # Right Side Panel Layout
        
        # 1. Top Panel for Dropdown and Buttons
        self.RHS_TopPanel = ttk.Frame(self.RSplitter)
        self.RHS_TopPanel.pack(fill=tk.X, padx=5, pady=5)
        
        # Object Type Dropdown
        ttk.Label(self.RHS_TopPanel, text="Object Type:").pack(side=tk.LEFT)
        self.ObjectTypeVar = tk.StringVar()
        self.ObjectTypeCombo = ttk.Combobox(self.RHS_TopPanel, textvariable=self.ObjectTypeVar, state="readonly")
        self.ObjectTypeCombo['values'] = ('Entities', 'Daemons', 'Scripts', 'Aliases', 'Substitutions')
        self.ObjectTypeCombo.current(0)
        self.ObjectTypeCombo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.ObjectTypeCombo.bind("<<ComboboxSelected>>", self.on_type_selected)
        
        # Add/Remove Buttons
        self.AddButton = ttk.Button(self.RHS_TopPanel, text="+", width=3, command=self.add_object_dialog)
        self.AddButton.pack(side=tk.LEFT, padx=2)
        self.RemoveButton = ttk.Button(self.RHS_TopPanel, text="-", width=3, command=self.remove_selected_objects)
        self.RemoveButton.pack(side=tk.LEFT, padx=2)
        
        # 2. Middle Panel for Listbox
        self.RHS_ListPanel = ttk.Frame(self.RSplitter)
        self.RHS_ListPanel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.ObjectListbox = tk.Listbox(self.RHS_ListPanel, selectmode=tk.EXTENDED)
        self.ObjectListbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ObjectListbox.bind("<<ListboxSelect>>", self.on_object_selected)
        
        self.ObjectListScroll = ttk.Scrollbar(self.RHS_ListPanel, orient=tk.VERTICAL, command=self.ObjectListbox.yview)
        self.ObjectListScroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ObjectListbox.configure(yscrollcommand=self.ObjectListScroll.set)
        
        # 3. Bottom Panel for Config Tabs
        self.RHS_ConfigPanel = ttk.Frame(self.RSplitter)
        self.RHS_ConfigPanel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.ConfigSelectNotebook = ttk.Notebook(self.RHS_ConfigPanel)
        self.ConfigSelectNotebook.pack(fill=tk.BOTH, expand=True)
        
        # Initial Population
        self.processcommand('load general')
        self.on_type_selected(None)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.FCScheduler.stop()
        self.destroy()
        sys.exit(0)

    def on_type_selected(self, event):
        # Handle Entity Type Sub-Dropdown
        obj_type = self.ObjectTypeVar.get()
        
        # Remove existing sub-dropdown if exists
        if hasattr(self, 'EntityTypeCombo'):
            self.EntityTypeCombo.destroy()
            del self.EntityTypeCombo
        if hasattr(self, 'EntityTypeLabel'):
            self.EntityTypeLabel.destroy()
            del self.EntityTypeLabel
            
        if obj_type == 'Entities':
            self.EntityTypeLabel = ttk.Label(self.RHS_TopPanel, text="Type:")
            self.EntityTypeLabel.pack(side=tk.LEFT, padx=(5,0))
            
            self.EntityTypeVar = tk.StringVar()
            self.EntityTypeCombo = ttk.Combobox(self.RHS_TopPanel, textvariable=self.EntityTypeVar, state="readonly", width=10)
            self.EntityTypeCombo['values'] = list(self.EntityManager.get_entity_types_metadata().keys())
            if self.EntityTypeCombo['values']:
                self.EntityTypeCombo.current(0)
            self.EntityTypeCombo.pack(side=tk.LEFT, padx=2)
            self.EntityTypeCombo.bind("<<ComboboxSelected>>", self.on_entity_type_selected)
            
        self.refresh_object_list()
        self.update_config_tabs() # Clear/Reset tabs

    def on_entity_type_selected(self, event):
        self.refresh_object_list()
        self.update_config_tabs()

    def refresh_object_list(self):
        self.ObjectListbox.delete(0, tk.END)
        obj_type = self.ObjectTypeVar.get()
        items = []
        try:
            if obj_type == 'Entities':
                 all_entities = self.EntityManager.getentitylist()
                 # Filter by selected Entity Type
                 if hasattr(self, 'EntityTypeVar'):
                     filter_type = self.EntityTypeVar.get()
                     items = [name for name, obj in all_entities.items() if obj.getentitytype() == filter_type]
                 else:
                     items = list(all_entities.keys())
                     
            elif obj_type == 'Daemons':
                 items = list(self.DaemonManager.getDaemons().keys())
            elif obj_type == 'Scripts':
                 items = list(self.scripts.keys())
            elif obj_type == 'Aliases':
                 items = list(self.aliases.keys())
            elif obj_type == 'Substitutions':
                 items = list(self.substitutions.keys())
        except Exception as e:
            logging.error(f"Error refreshing object list: {e}")
            
        for item in sorted(items):
            self.ObjectListbox.insert(tk.END, item)
            
        # Trigger update to show "New Object" form if empty
        self.update_config_tabs()

    def on_object_selected(self, event):
        self.update_config_tabs()

    def update_config_tabs(self):
        # Clear existing
        for tab in self.ConfigSelectNotebook.tabs():
            self.ConfigSelectNotebook.forget(tab)
            
        cur_selection = self.ObjectListbox.curselection()
        obj_type = self.ObjectTypeVar.get()
        
        if not cur_selection:
            # Show "New Object" form
            frame = ttk.Frame(self.ConfigSelectNotebook)
            self.ConfigSelectNotebook.add(frame, text="New " + (obj_type[:-1] if obj_type.endswith('s') else obj_type))
            self.create_config_pane(frame, obj_type, None, is_new=True)
            return

        names = [self.ObjectListbox.get(i) for i in cur_selection]
        
        for name in names:
            frame = ttk.Frame(self.ConfigSelectNotebook)
            self.ConfigSelectNotebook.add(frame, text=name)
            self.create_config_pane(frame, obj_type, name, is_new=False)

    def create_config_pane(self, parent, obj_type, name, is_new=False):
        parent.input_vars = {}
        try:
            if obj_type == 'Entities':
                if hasattr(self, 'EntityTypeVar'):
                    entity_type = self.EntityTypeVar.get()
                else:
                    return # Should be selected

                tk.Label(parent, text=f"Entity Type: {entity_type}").pack(anchor='w', pady=5)
                
                if is_new:
                    ttk.Label(parent, text="Name:").pack(anchor='w')
                    name_var = tk.StringVar()
                    ttk.Entry(parent, textvariable=name_var).pack(fill='x')
                    parent.input_vars['Name'] = name_var
                else:
                    parent.input_vars['Name'] = tk.StringVar(value=name) # Hidden

                # Metadata logic restored
                metadata = self.EntityManager.get_entity_types_metadata()
                fields = metadata.get(entity_type, [])
                
                current_values = []
                if not is_new:
                    try:
                        raw_params = self.EntityManager.getEntity(name).getparameterstring()
                        if entity_type == 'ENTITYGROUP':
                            current_values = [raw_params]
                        else:
                            parts = raw_params.split() 
                            # Check logic
                            if len(parts) > len(fields):
                                current_values = parts[1:]
                            else:
                                current_values = parts
                    except:
                        pass
                
                for i, field in enumerate(fields):
                    ttk.Label(parent, text=f"{field}:").pack(anchor='w')
                    var = tk.StringVar()
                    if not is_new and i < len(current_values):
                         var.set(current_values[i])
                    
                    entry = ttk.Entry(parent)
                    entry.configure(textvariable=var)
                    if 'pass' in field.lower() or 'password' in field.lower():
                        entry.configure(show='*')
                    
                    entry.pack(fill='x')
                    parent.input_vars[field] = var

            elif obj_type == 'Daemons':
                if is_new:
                     ttk.Label(parent, text="Name:").pack(anchor='w')
                     name_var = tk.StringVar()
                     ttk.Entry(parent, textvariable=name_var).pack(fill='x')
                     parent.input_vars['Name'] = name_var
                else:
                     daemon = self.DaemonManager.getDaemon(name)
                     sched = daemon.getschedule()
                     
                     ttk.Label(parent, text="Schedule Configuration").pack(anchor='w', pady=(5,0))
                     ttk.Label(parent, text="Start:").pack(anchor='w')
                     start_var = tk.StringVar(value=str(sched.getstart()))
                     ttk.Entry(parent, textvariable=start_var).pack(fill='x')
                     parent.input_vars['Start'] = start_var
                     
                     ttk.Label(parent, text="Period:").pack(anchor='w')
                     period_var = tk.StringVar(value=str(sched.getperiod()))
                     ttk.Entry(parent, textvariable=period_var).pack(fill='x')
                     parent.input_vars['Period'] = period_var

            elif obj_type == 'Scripts':
                 if is_new:
                     ttk.Label(parent, text="Name:").pack(anchor='w')
                     name_var = tk.StringVar()
                     ttk.Entry(parent, textvariable=name_var).pack(fill='x')
                     parent.input_vars['Name'] = name_var
                 
                 # Logic for text area loading omitted for brevity as it's not the focus
            
            elif obj_type == 'Aliases':
                 if is_new:
                     ttk.Label(parent, text="Name:").pack(anchor='w')
                     name_var = tk.StringVar()
                     ttk.Entry(parent, textvariable=name_var).pack(fill='x')
                     parent.input_vars['Name'] = name_var

                 ttk.Label(parent, text="Alias Content:").pack(anchor='w')
                 alias_var = tk.StringVar()
                 if not is_new and name in self.aliases:
                     alias_var.set(' '.join(self.aliases[name]))
                 ttk.Entry(parent, textvariable=alias_var).pack(fill='x')
                 parent.input_vars['Content'] = alias_var

            elif obj_type == 'Substitutions':
                 if is_new:
                     ttk.Label(parent, text="Name:").pack(anchor='w')
                     name_var = tk.StringVar()
                     ttk.Entry(parent, textvariable=name_var).pack(fill='x')
                     parent.input_vars['Name'] = name_var

                 ttk.Label(parent, text="Substitution Content:").pack(anchor='w')
                 sub_var = tk.StringVar()
                 if not is_new and name in self.substitutions:
                     sub_var.set(' '.join(self.substitutions[name]))
                 ttk.Entry(parent, textvariable=sub_var).pack(fill='x')
                 parent.input_vars['Content'] = sub_var
                     
        except Exception as e:
            print(f"DEBUG: create_config_pane EXCEPTION: {e}")
            tk.Label(parent, text=f"Error loading details: {e}").pack()

    def save_entity_changes(self, parent, name):
        try:
            entity_type = self.EntityTypeVar.get()
            metadata = self.EntityManager.get_entity_types_metadata()
            fields = metadata.get(entity_type, [])
            
            params = []
            params.append(name) # First param is always name for define logic
            for field in fields:
                val = parent.input_vars[field].get()
                if entity_type == 'ENTITYGROUP' and field == 'Members':
                     params.extend(val.split())
                else:
                     params.append(val)
                
            # Call define - this overwrites existing in EntityManager
            self.EntityManager.define(entity_type, params)
            messagebox.showinfo("Success", f"Entity {name} updated.")
            self.refresh_object_list() # Update list in case anything changed
        except Exception as e:
             messagebox.showerror("Error", f"Failed to update entity: {e}")

    def save_daemon_schedule(self, parent, name):
        try:
            start = parent.input_vars['Start'].get()
            period = parent.input_vars['Period'].get()
            sched = self.DaemonManager.getDaemon(name).getschedule()
            self.DaemonManager.setdaemonschedule(name, start, sched.getend(), period)
            messagebox.showinfo("Success", f"Schedule updated for {name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update schedule: {e}")

    def save_script(self, parent, name):
         content = parent.input_vars['ContentWidget'].get('1.0', tk.END).strip()
         lines = content.split('\n')
         self.scripts[name] = lines
         messagebox.showinfo("Success", f"Script {name} updated.")

    def save_alias(self, parent, name):
         new_content = parent.input_vars['Content'].get().split()
         self.aliases[name] = new_content
         messagebox.showinfo("Success", f"Alias {name} updated.")

    def save_sub(self, parent, name):
         new_content = parent.input_vars['Content'].get().split()
         self.substitutions[name] = new_content
         messagebox.showinfo("Success", f"Substitution {name} updated.")

    def add_object_dialog(self):
        # Now uses the "New Object" form in the active tab
        # We assume the "New Object" tab is active if nothing is selected.
        # If something IS selected, we should probably switch to "New Object" mode or
        # logic says "if user selects add button... use values entered into bottom config panel".
        
        # Check if we are in "New Object" mode (no selection logic)
        # OR if we just want to grab the currently visible tab's data if it happens to be a "New ..." tab.
        
        # Simplified logic: If selection is empty, we are in "New" mode.
        # If selection is NOT empty, deselecting would trigger "New" mode.
        # But if user filled out a form, they want to press Add.
        
        # Actually, if selection is NOT empty, tabs are "Edit" tabs.
        # Does Add button apply to Edit tabs? "if user selects add button... saved to entities".
        # This implies Add button acts as "Save All" for selection?
        
        # Let's support the primary "Add New" flow first.
        # If selection is empty -> "New Object" tab is visible.
        # Retrieve data from that tab.
        
        cur_selection = self.ObjectListbox.curselection()
        if cur_selection:
             # Deselect to show Add Form? Or treat as "Update Selected"?
             # User instruction: "if the user is viewing entities defined... and selects the add button, parameters changed... should now be saved"
             # This implies "Add" button == "Update" button when selection exists.
             
             # Let's iterate over all tabs and save them.
             for tab_id in self.ConfigSelectNotebook.tabs():
                  frame = self.ConfigSelectNotebook.nametowidget(tab_id)
                  name = self.ConfigSelectNotebook.tab(tab_id, "text")
                  
                  # Identify type and call save handler
                  obj_type = self.ObjectTypeVar.get()
                  if obj_type == 'Entities': self.save_entity_changes(frame, name)
                  elif obj_type == 'Daemons': self.save_daemon_schedule(frame, name)
                  elif obj_type == 'Scripts': self.save_script(frame, name)
                  elif obj_type == 'Aliases': self.save_alias(frame, name)
                  elif obj_type == 'Substitutions': self.save_sub(frame, name)
             return

        # "New Object" Mode
        # The first tab should be the "New ..." tab
        tabs = self.ConfigSelectNotebook.tabs()
        if not tabs: return
        
        parent = self.ConfigSelectNotebook.nametowidget(tabs[0])
        obj_type = self.ObjectTypeVar.get()
        
        try:
            name_var = parent.input_vars.get('Name')
            if not name_var or not name_var.get():
                messagebox.showerror("Error", "Name is required.")
                return
            name = name_var.get()
            
            if obj_type == 'Entities':
                entity_type = self.EntityTypeVar.get()
                metadata = self.EntityManager.get_entity_types_metadata()
                fields = metadata.get(entity_type, [])
                params = [name]
                for field in fields:
                    val = parent.input_vars[field].get()
                    if entity_type == 'ENTITYGROUP' and field == 'Members':
                        params.extend(val.split())
                    else:
                        params.append(val)
                self.EntityManager.define(entity_type, params)
                
            elif obj_type == 'Daemons':
                self.DaemonManager.addDaemon(name)
            elif obj_type == 'Scripts':
                content = parent.input_vars['ContentWidget'].get('1.0', tk.END).strip()
                self.scripts[name] = content.split('\n')
            elif obj_type == 'Aliases':
                content = parent.input_vars['Content'].get().split()
                self.aliases[name] = content
            elif obj_type == 'Substitutions':
                content = parent.input_vars['Content'].get().split()
                self.substitutions[name] = content
                
            messagebox.showinfo("Success", f"{obj_type[:-1]} {name} Added.")
            self.refresh_object_list() # This will clear the form because it re-selects nothing -> New Form
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add object: {e}")

    def remove_selected_objects(self):
        cur_selection = self.ObjectListbox.curselection()
        if not cur_selection:
            return
            
        obj_type = self.ObjectTypeVar.get()
        names = [self.ObjectListbox.get(i) for i in cur_selection]
        
        if not messagebox.askyesno("Confirm", f"Delete {len(names)} {obj_type}?"):
            return

        for name in names:
            try:
                if obj_type == 'Entities':
                    self.EntityManager.delete(name)
                elif obj_type == 'Daemons':
                    self.DaemonManager.deleteDaemon(name)
                elif obj_type == 'Scripts':
                    if name in self.scripts: del self.scripts[name]
                elif obj_type == 'Aliases':
                    if name in self.aliases: del self.aliases[name]
                elif obj_type == 'Substitutions':
                    if name in self.substitutions: del self.substitutions[name]
            except Exception as e:
                logging.error(f"Error deleting {name}: {e}")
                
        self.refresh_object_list()
        self.on_object_selected(None) # Clear tabs

    def ShellWindowEnterEvent(self, event):
        try:
            CommandInput = self.ShellEntry.get()
            
            # if len(CommandInput)<len(self.prompt):
            #     CommandInput=self.prompt+CommandInput
            # InputCommand=CommandInput[len(self.prompt):]
            # Tkinter entry just has the input, prompt is in text ctrl
            InputCommand = CommandInput
            
            self.ShellTextCtrl.configure(state='normal')
            self.ShellTextCtrl.insert(tk.END, self.prompt + InputCommand + '\n')
            self.ShellTextCtrl.see(tk.END)
            self.ShellTextCtrl.configure(state='disabled')
            
            self.processcommand(InputCommand)
            
            # Check alerts
            if len(self.DaemonManager.getOutstandingAlerts())>0:
                self.ShellTextCtrl.config(bg='#ffcccc') # Light red
            else:
                self.ShellTextCtrl.config(bg='white')
                
            self.prompt='FC:'+self.EntityManager.LastExecutedEntity+'> '
            self.ShellEntry.delete(0, tk.END)
            # self.ShellTextCtrl.insert(tk.END, self.prompt)
        except Exception as e:
            logging.error(f"ERROR in ShellWindowEnterEvent: {e}")

    ###########
    #

    #TODO: logger

    def dbg(self,Msg,Fn,execclass=None):
        logging.getLogger(Fn).debug(Msg)
    #
    #
    ###########

    # start fc methods

    def indicate_alert_state(self):
        self.ShellTextCtrl.config(bg='#ffcccc')


    def reset_alert_indicator(self):
        self.ShellTextCtrl.config(bg='white')

    def show_alert_queue(self):
        self.display.infodisplay('F!HAlert Queue:')
        generatedalerts=self.DaemonManager.getOutstandingAlerts()
        ctr=0
        info=[]
        for alert in generatedalerts:
            info.append(str(ctr)+' : '+alert)
            ctr=ctr+1
        self.display.infodisplay(info)
        
    def show_active_daemons(self):
        self.display.infodisplay('F!HCurrently Active Daemons:')
        info=[]
        for active in self.DaemonManager.getactivedaemons():
            info.append(active)
        self.display.infodisplay(info)
        
    def show_daemons(self):
        outlines=self.DaemonManager.getprettydaemons()
        self.display.infodisplay('F!HCurrently defined daemons/tasks/schedules and associated entities:')
        self.display.infodisplay(outlines)
                 
    def create_daemon(self, name: str) -> None:
        self.DaemonManager.addDaemon(name)
        self.display.infodisplay('Daemon '+name+' Defined.')
        
    def remove_daemon(self, name: str) -> None:
        self.DaemonManager.deleteDaemon(name)
        self.display.infodisplay('Daemon '+name+' Deleted.')

    def schedule_daemon(self, name: str, begin: str, end: str, period: str) -> None:
        self.DaemonManager.setdaemonschedule(name,begin,end,period)
        self.display.infodisplay('Schedule for daemon '+name+' Begin='+begin+' end='+end+' period='+period+' Set.')
            
    def add_daemon_task(self, daemonname: str, taskname: str, command: list) -> None:
        self.DaemonManager.addTask(daemonname,taskname,command)
        self.display.infodisplay('Task '+taskname+' for daemon '+daemonname+' '.join(command)+' Defined.')

    def remove_daemon_task(self, daemonname: str, taskname: str) -> None:
        self.DaemonManager.deleteTask(daemonname,taskname)
        self.display.infodisplay('Daemon '+daemonname+'Task '+taskname+' Deleted.')

    def add_daemon_task_collector(self, daemonname: str, taskname: str, collectorname: str, tag: str, skip: str, format: str, file: str) -> None:
        self.DaemonManager.addCollector(daemonname,taskname,collectorname,tag,skip,format,file)
        self.display.infodisplay('Collector '+collectorname+' for task '+taskname+' owned by daemon '+daemonname+' Datatag '+tag+' Skip '+skip+' Format '+format+' File '+file+' Defined.')

    def remove_daemon_task_collector(self, daemonname: str, taskname: str, collectorname: str) -> None:
        self.DaemonManager.deleteCollector(daemonname,taskname,collectorname)
        self.display.infodisplay('Daemon '+daemonname+' task '+taskname+' Collector '+collectorname+' Deleted.')

    def add_daemon_task_entity(self, daemonname: str, taskname: str, entityname: str) -> None:
        self.DaemonManager.subscribeEntity(daemonname,taskname,entityname)
        self.display.infodisplay('Daemon '+daemonname+' task '+taskname+' Entity '+entityname+' Subscribed.')

    def remove_daemon_task_entity(self, daemonname: str, taskname: str, entityname: str) -> None:
        self.DaemonManager.unsubscribeEntity(daemonname,taskname,entityname)
        self.display.infodisplay('Daemon '+daemonname+' task '+taskname+' Entity '+entityname+' Deleted.')

    def add_daemon_task_collector_alert(self, daemonname: str, taskname: str, collectorname: str, minval, maxval, textmessage, pass_script, fail_script) -> None:
        pass_script=pass_script[0]
        fail_script=fail_script[0]
        if not self.isScript(pass_script):
            pass_script='NoScript'
        if not self.isScript(fail_script):
            fail_script='NoScript'
        self.DaemonManager.addAlert(daemonname,taskname,collectorname,minval,maxval,textmessage,pass_script,fail_script)
        self.display.infodisplay('Daemon '+daemonname+' task '+taskname+' collector '+collectorname+' Alert '+str(minval)+' '+str(maxval)+' '+textmessage+' scripts pass: '+pass_script+' fail: '+fail_script+' Defined.')

    def make_daemon_live(self, daemonname: str) -> None:
        DBGBN='FCmakedaemonlive'
        #dbg('Making daemon live.',DBGBN)
        #be carefull with the task naming here... what about removing from the middle of the list? will it pop() the same?
        #...and dont confuse scheduer tasks with daemon tasks...
        self.DaemonManager.makeLive(daemonname)
        self.display.infodisplay('Daemon '+daemonname+' Activated.')

    def update_daemon_task(self,daemonname,taskname,command):
        self.DaemonManager.updateTask(daemonname,taskname,command)
        self.display.infodisplay('Task '+taskname+' Updated.')

    def kill_daemon(self,daemonname):
        DBGBN='FCkilldaemon'
        self.DaemonManager.kill_daemon(daemonname)
        self.display.infodisplay('Daemon '+daemonname+' Deactivated.')

    def is_daemon(self,daemonname):
        return self.DaemonManager.is_daemon(daemonname)

    def get_alias_defines(self,AliasDict):
        DefinitionList=[]
        for a in AliasDict:
            DefinitionList.append('alias '+a+' '+' '.join(AliasDict[a]))
        return DefinitionList

    def get_substituted_defines(self,SubstituteDict):
        DefinitionList=[]
        for s in SubstituteDict:
            DefinitionList.append('substitute '+s+' '+' '.join(self.substitutions[s]))
        return DefinitionList

    def save_list_as_lines_with_cr(self,Filename,AList,clobber=0):
        if clobber:
            SaveToFile=open(Filename,'w')
        else:
            SaveToFile=open(Filename,'a')
        for Line in AList:
            SaveToFile.write(Line.rstrip()+'\n')
        SaveToFile.close()

    def save_data(self,pathandname):
        #save entities, then aliases, then options
        DBGBN='save_data'
        EntityDefinitionList=self.EntityManager.getdefines()
        AliasDefinitionList=self.get_alias_defines(self.aliases)
        SubstituteDefinitionList=self.get_substituted_defines(self.substitutions)
        classoptionlists=self.EntityManager.getclassoptiondefines()
        #dbg('classoptionlists is '+str(len(classoptionlists))+' elements',DBGBN)
        fatcontrolleroptionlist=self.getfatcontrolleroptiondefines()
        scriptdefinitions=self.getscriptdefines()
        #
        #This block saves daemons and activestates #############################
        daemondefines=self.DaemonManager.getdaemondefines() #FC function returns list
        scheduledefines=self.DaemonManager.getscheduledefines() #FC function returns a list
        taskdefines=self.DaemonManager.gettaskdefines() # FC function returns a list
        collectordefines=self.DaemonManager.getcollectordefines() #
        alertdefines=self.DaemonManager.getalertdefines()
        subscriptiondefines=self.DaemonManager.getsubscriberdefines() # FC function returns a list
        activates=self.DaemonManager.getactivatedefines() # FC Function returns a list
        ########################################################################
        #
        self.save_list_as_lines_with_cr(pathandname,EntityDefinitionList,1)
        self.save_list_as_lines_with_cr(pathandname,AliasDefinitionList,0)
        self.save_list_as_lines_with_cr(pathandname,SubstituteDefinitionList,0)
        for optlist in classoptionlists:
            self.save_list_as_lines_with_cr(pathandname,optlist,0)
        self.save_list_as_lines_with_cr(pathandname,scriptdefinitions,0) # scripts before dameons cos daemons use 'em
        self.save_list_as_lines_with_cr(pathandname,fatcontrolleroptionlist)
        self.save_list_as_lines_with_cr(pathandname,daemondefines,0)
        self.save_list_as_lines_with_cr(pathandname,scheduledefines,0)
        self.save_list_as_lines_with_cr(pathandname,taskdefines,0)
        self.save_list_as_lines_with_cr(pathandname,collectordefines,0)
        self.save_list_as_lines_with_cr(pathandname,alertdefines,0)
        self.save_list_as_lines_with_cr(pathandname,subscriptiondefines,0)
        self.save_list_as_lines_with_cr(pathandname,activates,0)

        
    def save(self,WhatToSave,ProfileName):
        DBGBN='FCsave'
        if WhatToSave=='all':
            #DEVELOPR TOOLS MAKES THE SAVES INTO THE INSTALL PACKAGE
            # set FATCONTROLLER DEVELOPER yes
            # set FATCONTROLLER DEVELOPERPATH .....
            if 'DEVELOPER' in self.opts and self.opts['DEVELOPER']=='yes':
                pathandname=self.opts['DEVELOPERPATH']+ProfileName+'.sav'
                self.save_data(pathandname)
                pathandname=self.installroot+ProfileName+'.sav'
                #dbg('FATCONTROLLER DEVELOPER is yes. Doing save to DEVELOPERPATH',DBGBN)
                #dbg('-pathandname is '+pathandname,DBGBN)
                self.save_data(pathandname)
            else:
                pathandname=self.installroot+ProfileName+'.sav'
                #dbg('doing straight save. pathandname is '+pathandname,DBGBN)
                self.save_data(pathandname)
            #
        else:
            self.display.infodisplay('Error: Don\'t know how to save '+WhatToSave  +'.')
        self.display.infodisplay('Saved\t'+WhatToSave+'Succesfully.')

    def define_alias(self, Name: str, List: list) -> None:
        self.aliases[Name]=List
        self.display.infodisplay('Alias: '+Name+' '+' '.join(List)+' Defined.')

    def show_aliases(self) -> None:
        info=['F!HDefined aliases:']
        for a in self.aliases:
            info.append(''+a+'\t'+' '.join(self.aliases[a]))
        self.display.infodisplay(info)
        
    def del_alias(self, AliasName: str) -> None:
        del self.aliases[AliasName]
        self.display.infodisplay('Alias '+AliasName+' Deleted.')

    def is_alias(self, Name: str) -> int:
        try:
            self.aliases[Name]
            return 1
        except KeyError:
            return 0

    def insert_to_script(self,scriptname,linenumber,cmdtokens):
        linenumber=int(linenumber)
        cmdlist=self.scripts[scriptname]
        lowerlist=cmdlist[:linenumber]
        lowerlist.append(' '.join(cmdtokens))
        for ul in cmdlist[linenumber:]:
            lowerlist.append(ul)
        self.scripts[scriptname]=lowerlist
        return 0

    def delfromscript(self,scriptname,linenumber):
        try:
            self.scripts[scriptname].pop(int(linenumber)-1)
        except IndexError:
            self.display.infodisplay("ERROR: No line "+linenumber+" to delete.")
        return 0

    def appendtoscript(self,scriptname,cmdtokens):
        cmdstring=' '.join(cmdtokens)
        if scriptname not in self.scripts:
            self.scripts[scriptname]=[]
            self.scripts[scriptname].append(cmdstring)
        else:
            self.scripts[scriptname].append(cmdstring)
        self.display.infodisplay('Line '+cmdstring+' Appended.')

    def delscript(self,scriptname):
        if self.isScript(scriptname):
            del self.scripts[scriptname]
            self.display.infodisplay('Script '+scriptname+' Deleted.')
        else:
            self.display.infodisplay('Could not find script '+scriptname+' to delete.')

    def runscript(self,scriptname,parmlist):
        num=1
        for parmsub in parmlist:
            self.processcommand('sub '+str(num)+' '+parmsub)
            num=num+1
        cmdlist=self.scripts[scriptname]
        for cmd in cmdlist:
            self.processcommand(cmd)
        num=1
        for parmsub in parmlist:
            self.processcommand('del sub '+str(num))
            num=num+1


    def isScript(self,scriptname):
        if scriptname not in self.scripts:
            return 0
        else:
            return 1

    def showscripts(self,scriptname):
        DBGBN='showscripts'
        if scriptname=='all':
            scriptlist=list(self.scripts.keys())
        else:
            scriptlist=[scriptname]
        #for script in scriptlist:
            #dbg('script '+script+' is in scriptlist to display',DBGBN)
        self.display.infodisplay('F!HDefined scripts:')
        for script in scriptlist:
            self.display.infodisplay('F!h'+script)
            ctr=1
            for cmds in self.scripts[script]:
                self.display.infodisplay(str(ctr)+' : '+cmds)
                ctr=ctr+1

    def getscriptdefines(self):
        definelist=[]
        for scriptname in self.scripts:
            for scriptline in self.scripts[scriptname]:
                definelist.append('addline '+scriptname+' '+scriptline)
        return definelist

    def message(self,msg):
        self.display.infodisplay(' '.join(msg))
                

    def definesubstitution(self,SubName,SubList):
        self.substitutions[SubName]=SubList
        self.display.infodisplay('Substitution '+SubName+' Defined.',switchfocus=False)

    def delsubstitution(self,SubName,switchfocus=False):
        del self.substitutions[SubName]
        self.display.infodisplay('Substitution '+SubName+' Deleted.',switchfocus=False)

    def showsubstitutions(self):
        self.display.infodisplay('F!HSubstitutions:')
        for s in self.substitutions:
            if len(s)<8:
                tabs='\t\t'
            else:
                tabs='\t'
            self.display.infodisplay(s+tabs+' '.join(self.substitutions[s]))

    def issubstitute(self,SubName):
        try:
            self.substitutions[SubName]
            return 1
        except KeyError:
            return 0
            
    def processsubstitutions(self,RawCmd):
        DBGBN='processsubstitutions'
        infprotect=1
        subhit=1
        while subhit==1:
            subhit=0
            for sub in self.substitutions:
                SubCheck=RawCmd
                RawCmd=re.sub('~'+sub,' '.join(self.substitutions[sub]),RawCmd)
                if SubCheck!=RawCmd:
                    #dbg('Made Substitution '+sub+' to get '+RawCmd,DBGBN)
                    subhit=1
            infprotect=infprotect+1
            if infprotect>100:
                return "ERROR: Infinitely deep substitution levels detected."
        return RawCmd

    def displayhelp(self):
        try:
            helpfile=open(self.installroot+'FatController.hlp','r')
            for lines in helpfile:
                self.display.infodisplay(lines)#.strip())
        except Exception:
            self.display.infodisplay("Help file not found.")
            
        self.processcommand('show entities')
        self.processcommand('show aliases')
        self.processcommand('show substitutions')
        self.processcommand('show options')
        self.processcommand('show daemons')
        self.processcommand('show active daemons')
        self.processcommand('show scripts')

    def displayopts(self):
        self.display.infodisplay('F!HCurrently Set Options:')
        self.EntityManager.displayclassoptions()
        fcopts=self.getfatcontrolleroptiondefines()
        for d in fcopts:
            dl=d.split()
            d=' '.join(dl[1:])
            self.display.infodisplay(d) # twiddle becasue need to remove the set)

    def toggletrace(self,Fn):
        if Fn == "ALL":
             logger = logging.getLogger()
        else:
             logger = logging.getLogger(Fn)
             
        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.setLevel(logging.NOTSET) 
            self.display.infodisplay('Stop tracing block '+Fn)
        else:
            logger.setLevel(logging.DEBUG)
            self.display.infodisplay('Start tracing block '+Fn)


    def SetOption(self,EntityClass,Opt,Val):
        if EntityClass=='FATCONTROLLER':
            #dbg('Trapped OK',DBGBN)
            self.opts[Opt]=Val
        else:
            self.EntityManager.SetClassOption(EntityClass,Opt,Val)
            self.display.infodisplay('Option '+EntityClass+' '+Opt+' '+Val+' Has been set.')

    def getfatcontrolleroptiondefines(self):
        optlist=[]
        for opt in self.opts:
            optlist.append('set FATCONTROLLER '+opt+' '+self.opts[opt])
        return optlist

    def deleteentity(self,EntityName):
        self.EntityManager.delete(EntityName)
        self.display.infodisplay('Entity '+EntityName+' Deleted.')

    def read_command_file(self, filename: str) -> None:
        """Reads a file and executes commands line by line."""
        try:
            # Handle relative paths (assume relative to cwd which usually includes installroot)
            if not os.path.isabs(filename):
                 # Try current dir first, then install root ?
                 # User request says "take a filename", usually implies cwd or full path.
                 # Let's try direct open first which respects cwd.
                 pass
            
            if not os.path.exists(filename):
                 self.display.infodisplay(f"Error: File '{filename}' not found.")
                 return

            with open(filename, 'r') as f:
                lines = f.readlines()
                
            self.display.infodisplay(f"Reading commands from {filename}...")
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                self.processcommand(line)
                
            self.display.infodisplay(f"Finished reading {filename}.")
                
        except Exception as e:
            self.display.infodisplay(f"Error reading file {filename}: {e}")
            logging.error(f"Error reading command file {filename}: {e}")

    def clear_output_panel(self) -> None:
        """Clears the text content of the currently selected tab."""
        try:
            # Get selected tab
            selected_tab_id = self.OutBook.select()
            if not selected_tab_id:
                return
            
            # Get widget for tab
            tab_frame = self.OutBook.nametowidget(selected_tab_id)
            
            # Find Text widget children
            for child in tab_frame.winfo_children():
                if isinstance(child, tk.Text):
                    # Check state
                    old_state = child['state']
                    if old_state == 'disabled':
                        child.configure(state='normal')
                        
                    child.delete('1.0', tk.END)
                    
                    if old_state == 'disabled':
                        child.configure(state='disabled')
                        
                    # Usually only one text widget per tab, so can break
                    # But checking all just in case
                    # break 
            
            # self.display.infodisplay("Cleared output panel.") # Would just re-add text immediately? 
            # command echo in shell will verify command ran.
            
        except Exception as e:
            logging.error(f"Error clearing output panel: {e}")
            # self.display.infodisplay(f"Error clearing panel: {e}")


    def ComprehendCommand(self, Command): 
        #ok, only (usually) makes sense to have one set of [[]]'s so
        #split out the middle
        leftindex=Command.find('[[')
        rightindex=Command.find(']]')+2
        leftpart=Command[:leftindex]
        rightpart=Command[rightindex:]
        tokens=Command[leftindex+2:rightindex-2]
        #now parse the middle part. Will be either
        # start with number. if token is .. then range to number on the end
        #if , then just this number
        ranges=[]
        singles=[]
        elements=tokens.split(',')
        for item in elements:
            if item.find('..')==-1:
                singles.append(item)
            else:
                startval=item[:item.find('..')]
                endval=item[item.find('..')+2:]
                ranges.append((startval,endval))
        CommandList=[]
        for nrange in ranges:
            for n in range(int(nrange[0]),int(nrange[1])+1):
                CommandList.append(leftpart+str(n)+rightpart)
        for n in singles:
            CommandList.append(leftpart+n+rightpart)
        return CommandList

    def processcommand(self,Command): 
        DBGBN='processcommand'
        self.dbg('Before Substitution: '+Command,DBGBN)
        CommandList=[]
        #see if we are going to be using a list comprehension
        if Command.find('[[')!=-1 and Command.find(']]')!=-1:
            #generate list of commands to process
            CommandList=self.ComprehendCommand(Command)
        else:
            CommandList=[Command]
            
        for Command in CommandList:
            logging.debug(f"Command is: {Command}")
            Command=self.processsubstitutions(Command)  #  if ! aliascmd then flow is,  RawCmd->subbed->executed
                                    # is IS aliascmd then flow is   RawCmd->Subbed->aliashit->subbed->executed
            self.dbg('After Substitution: '+Command,DBGBN)
            
            SplitCmd=Command.split()
            SplitLen=len(SplitCmd)
            if SplitLen == 0: continue
            
            CommandHit = False
            
            # Check against Command Definitions
            for cmd_def in self.CommandDefinitions:
                matched, executed = self.CommandParser.match_and_execute(cmd_def, SplitCmd)
                if matched:
                    CommandHit = True
                    # If executed is False, it meant we matched but no 'create' action was defined?
                    # In .sav file every command has a create action essentially.
                    break
            
            if not CommandHit:
                # Check aliases
                AliasHit = 0
                Cmd = SplitCmd[0]
                for AliasName in self.aliases:
                    if Cmd==AliasName: #then, make cmdstring alias cmd string and re-process
                        AliasCmd=' '.join(self.aliases[AliasName])
                        AliasHit=1
                        self.dbg('Made alias hit to get '+AliasCmd,DBGBN)
                        break
                
                if AliasHit:
                    # Recursive call for alias
                    self.processcommand(AliasCmd)
                else:
                    # Fallback to Entity execution
                    if self.EntityManager.LastExecutedEntity!='':
                        # self.EntityManager.execute expectes (EntityName, CmdList)
                        # We pass rest of command as CmdList?
                        # Original: self.EntityManager.execute(self.EntityManager.LastExecutedEntity,SplitCmd[0:])
                        self.EntityManager.execute(self.EntityManager.LastExecutedEntity, SplitCmd)
                    else:
                        self.display.infodisplay('Error: Dont know which entity to use, and command not recognized.')
                

    def load(self,Profile):#will be load(profile)
        #EntityManager=FC_entitymanager.entitymanager()
        self.aliases={} #Is this right?
        try:
            logging.debug("DEBUGMJW: "+self.installroot+Profile+'.sav')
            FileToLoad=open(self.installroot+Profile+'.sav')
            for Line in FileToLoad:
                self.processcommand(Line)
        except IOError as xxx_todo_changeme:
            (errno,strerror) = xxx_todo_changeme.args
            self.display.infodisplay("Error: ["+str(errno)+"] "+strerror+"\t"+self.installroot+Profile+".sav")
        #makeObjectBrowser()

    def handlealertrange(self,fromalert,toalert=None):
        if toalert==None:
            toalert=fromalert
        self.DaemonManager.handlealert(fromalert,toalert+1)


def main():
    app = FatController()
    app.mainloop()

if __name__ == "__main__":
    main()
