import FC_entity
import logging
import base64
try:
    import paramiko
except ImportError:
    paramiko = None

###########
# START OF CLASS SSH
# implements entity()
#

class SSH(FC_entity.entity):

    Connections={} # {'name':paramiko.SSHClient()}
    
    def __init__(self,Name,TCPAddress,SSHUser,SSHPass,SSHKeyfile):
        self.Name=Name
        self.TCPAddress=TCPAddress
        self.SSHUser=SSHUser
        self.SSHPass=SSHPass
        self.SSHKeyfile=SSHKeyfile
        self.Connection=self.openconnection()

    def openconnection(self):
        if paramiko is None:
            logging.error("Paramiko not installed. SSH entity cannot function.")
            return None
            
        C=paramiko.SSHClient()
        C.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        pkey = None
        if self.SSHKeyfile and self.SSHKeyfile.lower() != 'none':
             try:
                 # Try loading as RSA key first, can extend logic for others if needed
                 # Or just rely on paramiko's ability to handle it via connect params if strictly keyfile path
                 # But FatController seems to want to load it. 
                 # Let's try to load it if file exists.
                 pkey = paramiko.RSAKey.from_private_key_file(self.SSHKeyfile)
             except Exception as e:
                 logging.warning(f"Could not load key file {self.SSHKeyfile}: {e}")
        
        try:
            # Prefer key if available, else password
            C.connect(self.TCPAddress, username=self.SSHUser, password=self.SSHPass, pkey=pkey, look_for_keys=False)
            logging.info(f"SSH Connected to {self.TCPAddress}")
            return C
        except Exception as e:
            logging.error(f"SSH Connection failed to {self.TCPAddress}: {e}")
            return None

    def execute(self, CmdList):
        Output = []
        if not self.Connection:
            self.Connection = self.openconnection()
            if not self.Connection:
                return ["Error: No SSH Connection"]

        cmd_str = ' '.join(CmdList)
        
        try:
            stdin, stdout, stderr = self.Connection.exec_command(cmd_str)
            # Paramiko exec_command is non-blocking on the channel execution but returning streams
            # We need to read from stdout/stderr
            
            # Simple blocking read for now. For long running commands, this might block the GUI
            # but that's a known limitation of the current architecture (FatController seems synchronous in execute)
            
            out_bytes = stdout.read()
            err_bytes = stderr.read()
            
            if out_bytes:
                Output.extend(out_bytes.decode('utf-8', errors='replace').splitlines())
            if err_bytes:
                Output.append("STDERR:")
                Output.extend(err_bytes.decode('utf-8', errors='replace').splitlines())
                
        except paramiko.SSHException as e:
            logging.warning(f"SSH Exception: {e}. Attempting reconnect...")
            self.Connection = self.openconnection()
            if self.Connection:
                 # Retry once
                 try:
                    stdin, stdout, stderr = self.Connection.exec_command(cmd_str)
                    out_bytes = stdout.read()
                    if out_bytes:
                        Output.extend(out_bytes.decode('utf-8', errors='replace').splitlines())
                 except Exception as e2:
                     Output.append(f"Error executing command after reconnect: {e2}")
            else:
                Output.append("Error: Connection lost and could not reconnect.")
        except Exception as e:
             Output.append(f"Error executing command: {e}")

        return Output
    
    def display(self,LineList,OutputCtrl):
        if LineList:
            for Line in LineList:
                try:
                    OutputCtrl.insert("end", Line.rstrip()+"\n")
                except:
                    pass
    
    def getparameterdefs(self):
        '''Should return a list of parms for the GUI
        to build a config box'''
        return ["Name","Host","User","Pass","KeyFile"]
    
    def getname(self):
        return self.Name

    def getparameterstring(self):
        return f"{self.Name} {self.TCPAddress} {self.SSHUser} {self.SSHPass} {self.SSHKeyfile}"

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        return [self.Name, self.TCPAddress, self.SSHUser, self.SSHPass, self.SSHKeyfile]

    def getentitytype(self):
        return 'SSH'

    def gettype(self):
        return 'simple'

    def setoption(self,option,value):
        SSH.Opts[option]=value

    def getoptions(self):
        OptList=[]
        for o in SSH.Opts:
            OptList.append(o+' '+SSH.Opts[o])
        return OptList

###########
# END OF CLASS SSH
