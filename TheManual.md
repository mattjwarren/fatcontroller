# The FatController Manual

**Version:** 1.11.1
**Copyright:** (c) 2005 Matthew Warren

## Overview
FatController is a daemon management and automation tool designed to help system administrators automate tasks across various systems. It uses a command-line interface (CLI) style input within a GUI to manage "Entities", "Daemons", and "Tasks".

## Core Concepts

### Entities
Entities are the objects that FatController interacts with. They can be local systems, remote servers (SSH/Telnet), or abstract groups of other entities.
- **LOCAL**: Executes commands on the local machine.
- **SSH/TELNET**: Executes commands on remote servers.
- **ENTITYGROUP**: Groups multiple entities together to execute commands on all of them simultaneously.
- **TSM**: Tivoli Storage Manager specific entity (legacy).

### Daemons
Daemons are internal schedulers that run background tasks. A daemon can have multiple "Tasks" associated with it, ensuring they run periodically according to a defined schedule.

### Tasks
Tasks are specific commands assigned to a daemon. They can be simple commands or "Collectors" that gather data and potentially trigger alerts.

## Command Reference

### General Commands
| Command | Description | Example |
| :--- | :--- | :--- |
| `help` | Display help information. | `help` |
| `exit` / `quit` | Exit the application. | `exit` |
| `load <profile>` | Load a saved profile (set of definitions). | `load general` |
| `save <profile>` | Save current configuration to a profile. | `save myprofile` |
| `clear` | Clear the current output panel. | `clear` |
| `readfile <filename>` | Execute commands from a text file. | `readfile setup.txt` |
| `message <text>` | Display a message in the output. | `message "Hello World"` |

### Entity Management
| Command | Description | Example |
| :--- | :--- | :--- |
| `define entity <type> <name> <params>` | Define a new entity. | `define entity LOCAL myserver` |
| `show entities` | List all defined entities. | `show entities` |
| `delete entity <name>` | Delete an entity. | `delete entity myserver` |
| `<entity> <command>` | Execute a command on an entity. | `myserver ls -la` |

**Entity Specific Examples:**
- **LOCAL**: `define entity LOCAL <name>`
- **SSH**: `define entity SSH <name> <hostname> <user> <password> <keyfile>`
- **ENTITYGROUP**: `define entity ENTITYGROUP <name> <member1> <member2> ...`

### Aliases & Substitutions
Aliases are shortcuts for long commands, and substitutions are text variables.

| Command | Description | Example |
| :--- | :--- | :--- |
| `alias <name> <command>` | Create an alias. | `alias ll ls -la` |
| `show aliases` | List all aliases. | `show aliases` |
| `delete alias <name>` | Delete an alias. | `delete alias ll` |
| `substitute <name> <value>` | Define a text substitution (`^name`). | `substitute MYDIR /tmp/data` |
| `show substitutions` | List all substitutions. | `show substitutions` |
| `delete substitution <name>` | Delete a substitution. | `delete substitution MYDIR` |

### Daemon & Task Management
Daemons run tasks on a schedule. Tasks can be generic commands or specific collectors.

| Command | Description | Example |
| :--- | :--- | :--- |
| `define daemon <name>` | Create a new daemon. | `define daemon Monitor` |
| `define schedule <daemon> <start> <end> <period>` | Set schedule for a daemon. | `define schedule Monitor 08:00 18:00 300` |
| `activate daemon <name>` | Start a daemon. | `activate daemon Monitor` |
| `deactivate daemon <name>` | Stop a daemon. | `deactivate daemon Monitor` |
| `show active daemons` | detailed list of running daemons. | `show active daemons` |
| `show daemons` | List all configured daemons. | `show daemons` |
| `delete daemon <name>` | Delete a daemon. | `delete daemon Monitor` |

**Daemon Tasks:**
| Command | Description | Example |
| :--- | :--- | :--- |
| `define task <daemon> <name> <cmd>` | Add a task to a daemon. | `define task Monitor CheckDisk df -h` |
| `update task <daemon> <name> <cmd>` | Update an existing task. | `update task Monitor CheckDisk df -k` |
| `delete task <daemon> <name>` | Remove a task. | `delete task Monitor CheckDisk` |

**Task Subscriptions:**
You can subscribe specific entities to a daemon task, allowing the task to run against them.
| Command | Description | Example |
| :--- | :--- | :--- |
| `subscribe entity <daemon> <task> <entity>` | Add entity to task scope. | `subscribe entity Monitor CheckDisk myserver` |
| `unsubscribe entity <daemon> <task> <entity>` | Remove entity from task scope. | `unsubscribe entity Monitor CheckDisk myserver` |

## Advanced Features

### Scripts
Scripts allow you to bundle commands together and execute them sequentially.

| Command | Description | Example |
| :--- | :--- | :--- |
| `run <script> <args>` | Execute a script. | `run myscript` |
| `show scripts` | List all scripts. | `show scripts` |
| `show script <name>` | Display content of a script. | `show script myscript` |
| `delete script <name>` | Delete a script. | `delete script myscript` |

**Editing Scripts:**
- `addline <script> <command>`: Append a line to the end of a script.
- `insline <script> <lineNum> <command>`: Insert a line at a specific position.
- `delline <script> <lineNum>`: Delete a specific line.

### Global Options & Debugging
| Command | Description | Example |
| :--- | :--- | :--- |
| `set <Class> <Option> <Value>` | Set a global option for an entity class. | `set TELNET ShowRawTelnet yes` |
| `show options` | Show all set options. | `show options` |
| `trace <module>` | Toggle debug tracing for a module. | `trace FatController` |

### Checking for Alerts
- `alerts`: Show current alert queue.
- `handle <id>` | `handle <start> <end>`: Acknowledge/clear alert(s) by ID or range.

## Monitoring & Alerts
FatController allows you to extract specific data from your tasks (Collectors) and trigger alerts based on that data.

### 1. Defining Collectors
Collectors parse the output of a Daemon Task and extract values.

**Syntax:**
`define collector <DaemonName> <TaskName> <CollectorName> <Tag> <SkipLines> <Format> <OutputFile>`

-   **Tag**: A regex pattern or string identifier to locate relevant lines in the output.
-   **SkipLines**: Number of lines to skip before reading data (e.g., headers).
-   **Format**: Data format descriptor (implementation specific).
-   **OutputFile**: Path to a file where collected data will be appended.

**Example:**
`define collector SystemMonitor CheckDisk DiskUsage ^/dev/sda1 0 usage_pct data/disk_usage.txt`

### 2. Defining Alerts
Alerts monitor the values gathered by a Collector and check if they fall within a specified range.

**Syntax:**
`define alert <DaemonName> <TaskName> <CollectorName> <MinVal> <MaxVal> <Message> <PassScript> <FailScript>`

-   **MinVal / MaxVal**: The acceptable range for the collected value.
-   **Message**: The text to display/log if the alert triggers (value outside range).
-   **PassScript**: Name of a script to run if the check PASSES (or `NoScript`).
-   **FailScript**: Name of a script to run if the check FAILS (or `NoScript`).

**Example:**
`define alert SystemMonitor CheckDisk DiskUsage 0 90 "WARNING: Disk usage high!" NoScript cleanup_logs`

---

## Creating New Entities (Developer Guide)

FatController is designed to be extensible. New entity types can be added by creating a new Python module (e.g., `FC_NEWTYPE.py`) and a class that inherits from the abstract `entity` base class.

### 1. File Structure
Create a file named `FC_<TYPENAME>.py` in the application directory.

### 2. Implementation
Your class must inherit from `FC_entity.entity` and implement the following interface methods:

```python
import FC_entity

class NEWTYPE(FC_entity.entity):
    '''Documentation for your new entity'''
    
    def __init__(self, name, param1):
        self.Name = name
        self.Param1 = param1
        
    def execute(self, CmdList):
        '''
        Execute the command.
        CmdList: List of command strings (e.g., ['ls', '-la'])
        Returns: List of strings (output lines)
        '''
        # Implementation here
        return ["Output Line 1", "Output Line 2"]

    def display(self, LineList, OutputCtrl):
        '''
        Display output to the GUI.
        LineList: The return value from execute()
        OutputCtrl: The wx/tk Text widget instance
        '''
        for line in LineList:
            try:
                OutputCtrl.insert("end", line.rstrip() + "\n")
            except:
                pass

    def getparameterdefs(self):
        '''Return list of parameter names for GUI config'''
        return ["Name", "Param1"]
        
    def getentitytype(self):
        '''Return the unique type name'''
        return 'NEWTYPE'
        
    def getparameterstring(self):
        '''Return string to reconstruct this entity command'''
        return f"{self.Param1}"
```

### 3. Registration
To make the new entity available:
1.  Import your new module in `FC_entitymanager.py`.
2.  Update `FC_entitymanager.define()` to handle the new `type` string and instantiate your class.
