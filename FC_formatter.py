import tkinter as tk

class OutputFormatter(object):
    def __init__(self, notebook, focus_return):
        self.notebook = notebook
        # In Tkinter, accessing children is different. 
        # We'll assume the notebook's first tab frame has a text widget as its first child
        # But to be safer, FatController should pass the text widget directly if possible.
        # For now, let's assume the structure is maintained or passed correctly.
        # Actually, in FatController.py I will pass the Text widget directly to this class instead of the notebook if I can.
        # But let's stick to the current signature for now and adapt.
        # notebook.tabs() returns list of tab ids.
        # This is getting messy if we try to inspect Tkinter widget hierarchy blindly.
        # Let's assume textctrl is passed in simpler way or we fix it in FatController.py.
        # The original code did: self.textctrl=notebook.GetPage(0).GetChildren()[0]
        # In Tkinter: frame = notebook.nametowidget(notebook.tabs()[0])
        # text = frame.winfo_children()[0]
        self.text_widget = None # Will be set by FatController or discovered
        self.focus_return = focus_return

    def set_text_widget(self, widget):
        self.text_widget = widget

    def infodisplay(self, msg, switchfocus=True):
        if isinstance(msg, (str, bytes)):
            msg = [msg]
        
        if switchfocus:
            try:
                # logging.info("DEBUG_MJW: Switching tab input focus")
                self.notebook.select(0) 
            except Exception as e:
                # logging.error(f"DEBUG_MJW: Failed to switch tab: {e}")
                pass 

        bullet = ' * '
        for line in msg:
            if not isinstance(line, str):
                line = str(line)
                
            linestyle = 'N'
            if line.startswith('F!'):
                linestyle = line[2:3]
                line = line[3:]
            
            if linestyle == 'H':
                fline = '\n\n\t' + bullet + line + '\n\n\n'
            elif linestyle == 'h':
                fline = '\n' + bullet + line + '\n\n'
            else:
                fline = line.rstrip() + '\n'
            
            if self.text_widget:
                old_state = self.text_widget['state']
                message_matches_shell = False
                
                # Check if this widget is the ShellTextCtrl (which we might have disabled)
                # FC_formatter doesn't 'know' which widget it is, but we can just force enable/disable if needed
                # However, FirstPageTextCtrl is typically NOT disabled. ShellTextCtrl IS.
                # Currently self.text_widget is set to FirstPageTextCtrl (General Tab).
                # But wait, does ShellTextCtrl get written to via this?
                # No, ShellTextCtrl is only for command history echo in this app version.
                # BUT, let's be safe.
                if old_state == 'disabled':
                     self.text_widget.configure(state='normal')
                     
                self.text_widget.insert(tk.END, fline)
                self.text_widget.see(tk.END)
                
                if old_state == 'disabled':
                     self.text_widget.configure(state='disabled')
        
        if self.focus_return:
            self.focus_return.focus_set()

