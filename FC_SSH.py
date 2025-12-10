import FC_entity
import logging
import asyncio
try:
    from fabric import Connection, Config
    from invoke.exceptions import UnexpectedExit
except ImportError:
    Connection = None
    Config = None
    logging.error("Fabric not installed. SSH entity will not function.")

###########
# START OF CLASS SSH
# implements entity()
#

class SSH(FC_entity.entity):

    Opts={} 
    
    def __init__(self,Name,TCPAddress,SSHUser,SSHPass,SSHKeyfile):
        self.Name=Name
        self.TCPAddress=TCPAddress
        self.SSHUser=SSHUser
        self.SSHPass=SSHPass
        self.SSHKeyfile=SSHKeyfile
        if self.SSHKeyfile == 'none':
             self.SSHKeyfile = None
             
        # Lazy initialization - create connection only when needed to avoid stale objects
        self.Connection = None

    def _create_connection(self):
        logging.debug(f"FC_SSH [{self.Name}]: Creating connection to {self.TCPAddress} as {self.SSHUser}")
        if Connection is None:
            logging.error("FC_SSH: Fabric Connection class is None.")
            return None
            
        connect_kwargs = {}

        # Timeout for connection (10 seconds)
        connect_kwargs['timeout'] = 10
        # banner_timeout also helps with some slow servers
        connect_kwargs['banner_timeout'] = 10
        # Disable looking for keys in ~/.ssh etc
        connect_kwargs['look_for_keys'] = False
        # Disable agent usage to prevent hanging/errors on Windows if agent is flaky
        connect_kwargs['allow_agent'] = False
        # Disable GSSAPI to prevent delays/errors on Windows
        connect_kwargs['gss_auth'] = False
        connect_kwargs['gss_kex'] = False
        
        try:
            import paramiko
            logging.debug(f"FC_SSH: Paramiko Version: {paramiko.__version__}")
        except:
            pass

        # Handle Password
        if self.SSHPass and self.SSHPass.lower() != 'none':
            logging.debug(f"FC_SSH [{self.Name}]: Password provided (length {len(self.SSHPass)})")
            connect_kwargs['password'] = self.SSHPass
        else:
            logging.debug(f"FC_SSH [{self.Name}]: No password provided.")
            
        # Handle Keyfile
        if self.SSHKeyfile and self.SSHKeyfile.lower() != 'none':
             logging.debug(f"FC_SSH [{self.Name}]: Using keyfile {self.SSHKeyfile}")
             connect_kwargs['key_filename'] = self.SSHKeyfile
        else:
             logging.debug(f"FC_SSH [{self.Name}]: No keyfile provided.")
             
        # Configure to accept new keys automatically (mimic paramiko AutoAddPolicy)
        # We use the 'ssh_config' overrides for this.
        # NOTE: UserKnownHostsFile should likely be None or platform specific NUL.
        # Setting StrictHostKeyChecking=no is the primary fix for "Host key not found" issues.
        # NumberOfPasswordPrompts=0 prevents hanging on auth failure.
        config = Config(overrides={
            'run': {'warn': True}, 
            'ssh_config': {
                'StrictHostKeyChecking': 'no',
                'NumberOfPasswordPrompts': '0'
            }
        })
        
        try:
            conn = Connection(
                host=self.TCPAddress,
                user=self.SSHUser,
                config=config,
                connect_kwargs=connect_kwargs
            )
            logging.debug(f"FC_SSH [{self.Name}]: Connection object created: {conn}")
            return conn
        except Exception as e:
            logging.error(f"FC_SSH [{self.Name}]: Error creating Connection object: {e}")
            return None

    async def execute(self, CmdList):
        logging.debug(f"FC_SSH [{self.Name}]: execute called with {CmdList}")
        Output = []
        
        # Connection logic must be thread-safe or run in executor if it blocks
        # Fabric connection creation is fast/lazy, but open() blocks.
        if self.Connection is None:
            logging.warning(f"FC_SSH [{self.Name}]: Connection was None, attempting to create.")
            self.Connection = self._create_connection()
            if self.Connection is None:
                return ["Error: Fabric library not found or initialization failed"]

        cmd_str = ' '.join(CmdList)
        logging.debug(f"FC_SSH [{self.Name}]: Preparing to run '{cmd_str}'")
        
        loop = asyncio.get_event_loop()
        
        # Retry loop logic
        retries = 1
        for attempt in range(1, retries + 2):
            logging.debug(f"FC_SSH [{self.Name}]: Attempt {attempt} of {retries+1}")
            try:
                # Run blocking Fabric calls in executor
                def blocking_ssh_run():
                    if not self.Connection.is_connected:
                         self.Connection.open()
                    return self.Connection.run(cmd_str, hide=True, warn=True)

                result = await loop.run_in_executor(None, blocking_ssh_run)
                
                logging.debug(f"FC_SSH [{self.Name}]: Run returned. Exited: {result.exited}")
                
                if result.stdout:
                    logging.debug(f"FC_SSH [{self.Name}]: Got stdout ({len(result.stdout)} chars)")
                    Output.extend(result.stdout.splitlines())
                
                if result.stderr:
                    logging.debug(f"FC_SSH [{self.Name}]: Got stderr ({len(result.stderr)} chars)")
                    if Output: 
                        Output.append("--- STDERR ---")
                    Output.extend(result.stderr.splitlines())
                
                # Success
                break
                
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                logging.warning(f"FC_SSH [{self.Name}]: Exception during execution attempt {attempt}: {e}\n{tb}")
                
                if attempt <= retries:
                    logging.warning(f"SSH Execution failed for {self.Name}: {e}. Retrying...")
                    # Force close and retry - in executor? close() might block?
                    try: 
                        await loop.run_in_executor(None, self.Connection.close)
                    except: 
                        pass
                    # Recreate connection object
                    self.Connection = self._create_connection()
                else:
                    logging.error(f"SSH Execution failed for {self.Name}: {e}")
                    Output.append(f"Error executing command: {e}")

        logging.debug(f"FC_SSH [{self.Name}]: Returning output ({len(Output)} lines)")
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
        return f"{self.TCPAddress} {self.SSHUser} {self.SSHPass} {self.SSHKeyfile}"

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
