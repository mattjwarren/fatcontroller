import FC_entity
import base64
try:
    import paramiko
except ImportError:
    paramiko = None

"""import base64
import paramiko
key = paramiko.RSAKey(data=base64.b64decode(b'AAA...'))
client = paramiko.SSHClient()
client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
client.connect('ssh.example.com', username='strongbad', password='thecheat')
stdin, stdout, stderr = client.exec_command('ls')
for line in stdout:
    print('... ' + line.strip('\n'))
    client.close()"""

###########
# START OF CLASS SSH
# implements entity()
#

class SSH(FC_entity.entity):

    Connections={} # {'name':telnetlib.Telnet()}
    valid_def_parmcount=4 # number of parameters expected for definition
                         # including name


    def __init__(self,Name,TCPAddress,SSHUser,SSHPass,SSHKeyfile):
        self.Name=Name
        self.TCPAddress=TCPAddress
        self.SSHUser=SSHUser
        self.SSHPass=SSHPass
        self.SSHKey=None
        self.SSHKey_raw=None
        self.SSHKeyfile=SSHKeyfile
        self.Connection=self.openconnection()

    def openconnection(self):
        DBGBN='telnetopenconnection'
        C=paramiko.SSHClient()
        self.SSHKey_raw=self.get_key()
        self.SSHKey=paramiko.RSAKey(data=base64.b64decode(self.SSHKey_raw))
        C.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        #C.get_host_keys().add(self.TCPAddress,'ssh-rsa',self.SSHKey)
        C.connect(self.TCPAddress,username=self.SSHUser,password=self.SSHPass,look_for_keys=False)
        return C

    def get_key(self):
        #look by default in ~/.ssh/id_rsa.pub
        #for first line starting ssh-rsa
        key=''
        keyfile=self.SSHKeyfile
        with open(keyfile,'r') as kf:
            for line in kf:
                if line.startswith('ssh-rsa'):
                    key=line.split()[1]
                    break
        return key

            
    
    ###########
    # START OF INTERFACE entity()
    #

    Opts={} #dict of options

    def execute(self,CmdList):
        alldata=''
        if CmdList:
            good=False
            while not good:
                try:
                    stdin,stdout,stderr=self.Connection.exec_command(' '.join(CmdList))
                    good=True
                except paramiko.ssh_exception.SSHException as e:
                    print("SSH exception executing command. Trying conn_reset")
                    self.Connection=self.openconnection()
            while not stdout.channel.exit_status_ready():
                # Print stdout data when available
                if stdout.channel.recv_ready():
                    # Retrieve the first 1024 bytes
                    alldata = stdout.channel.recv(1024)
                    while stdout.channel.recv_ready():
                        # Retrieve the next 1024 bytes
                        alldata += stdout.channel.recv(1024)
        Output=alldata.split('\n')
        #[ s.close() for s in [sin,sout,serr] ]
        return  Output
    
    def display(self,LineList,OutputCtrl):
        if LineList:
            for Line in LineList:
                try:
                    OutputCtrl.insert("end", Line.rstrip()+"\n")
                except:
                    pass
    
    def getparameterdefs(self):
        '''Should return a dict of parm:parmtype pairs for the GUI
        to build a config box'''
        #telnet parms are name,host,port,user,pwd
        return ["Name","Host","User","Pass","Key"]
    

    def getname(self):
        return self.Name

    def getparameterstring(self):
        return self.TCPAddress+' '+self.SSHUser+' '+self.SSHPass+' '+self.SSHKeyfile

    def getparameterlist(self):
        '''returns a list of the value given as string by getparameterstring'''
        parmstring=self.getparameterstring()
        list=parmstring.split()
        return list


    def getentitytype(self):
        return 'SSH'

    def gettype(self):
        return 'simple'

    def setoption(self,option,value):
        DBGBN='sshsetoption'
        SSH.Opts[option]=value
        #dbg('Have set opt >|'+option+'|< to >|'+value+'|<',DBGBN)

    def getoptions(self):
        OptList=[]
        for o in SSH.Opts:
            OptList.append(o+' '+SSH.Opts[o])
        return OptList

    #
    # END OF INTERFACE entity()
    ###########

#
# END OF CLASS SSH
###########
