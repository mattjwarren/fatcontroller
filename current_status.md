# Current Status & Developer Handover Guide

## Project Overview
FatController has been modernized from a legacy Python 2 / wxPython application to a **Python 3.13 / Tkinter** application. This migration addressed critical compatibility issues (removal of `telnetlib`), security vulnerabilities (removal of `eval()`), and code quality (logging, type hints).

## Key Changes
1.  **Python 3.13 Migration**:
    *   Updated syntax (print functions, exception handling).
    *   Replaced `file()` with `open()`.
    *   Handled removal of `telnetlib` (now an optional dependency stub).
    *   Stubbed `paramiko` for SSH to allow startup without dependencies.
2.  **GUI Replacement**:
    *   Removed all `wxPython` dependencies.
    *   Rebuilt the GUI using `tkinter` and `ttk` (Themed Tkinter).
    *   Main window uses `tk.PanedWindow` for layout, `ttk.Notebook` for tabs, and `ttk.Treeview` for object lists.
3.  **Security Refactoring**:
    *   **Removed `eval()`**: The command processor no longer executes arbitrary Python strings.
    *   **`FC_command_parser.py`**: A new parser strictly matches user input against `FatControllerCommands.sav` and executes specific, whitelisted methods.
4.  **Logging**:
    *   Replaced custom `dbg` print statements with the standard `logging` library.
    *   Logs are routed to the GUI (General Tab) via a custom `GuiHandler`.

## Architecture for Juniors

### Core Components
*   **`FatController.py`**: The heart of the application. It inherits from `tk.Tk` and creates the main window. It initializes the managers and the scheduler. It also acts as the central command dispatcher (`processcommand`).
*   **`FC_entitymanager.py`**: Manages "Entities" (connections to systems like TSM, Telnet, SSH). It handles creating their GUI tabs and executing commands on them.
*   **`FC_daemonmanager.py`**: Manages background tasks ("Daemons") that run on a schedule.
*   **`FC_ThreadedScheduler.py`**: A custom scheduler that runs tasks in background threads so the GUI doesn't freeze.
*   **`FC_command_parser.py`**: The security gatekeeper. It parses the command definitions file and matches user input to executable actions.

### Data Flow
1.  **User Input**: User types a command in the bottom text entry.
2.  **Parsing**: `FatController.processcommand` passes the string to `CommandParser`.
3.  **Matching**: The parser checks `FatControllerCommands.sav` for a matching pattern.
4.  **Execution**: If matched, the parser calls a specific Python method (e.g., `self.create_daemon("foo")`) defined in the `create:` directive.

## How to Add New CLI Commands

The application uses a data-driven command system defined in `FatControllerCommands.sav`. Here is how to extend it.

### 1. Understand the Syntax (`FatControllerCommands.sav`)
Each line defines a command pattern and an action.
*   `literal`: Updates the parser state. Must match exactly.
*   `input:validation_expression`: Captures a user variable. The expression checks validitiy.
    *   Example: `input:'<<'!=''` means "Input must not be empty".
    *   Example: `input:self.is_daemon('<<')` means "Input must be a known daemon name".
*   `+*`: Wildcard. Matches everything else to the end of the line.
*   `create:action_expression`: The Python code to execute if the match is successful.

### 2. The Golden Rule
**You cannot write arbitrary Python code in the `create:` directive anymore.**
The new security parser only allows calls to existing methods on `self` (FatController) or its attributes (e.g., `self.EntityManager`).

**To add a new command, you must first write the Python method that performs the action.**

### 3. Step-by-Step Example
**Goal**: Add a command `greet user <name>` that prints "Hello <name>".

**Step A: Implement the Logic**
Open `FatController.py` and add a method to the `FatController` class:

```python
# In FatController.py
def greet_user(self, name: str) -> None:
    self.display.infodisplay(f"Hello, {name}!")
```

**Step B: Define the Command**
Open `FatControllerCommands.sav` and add the definition line:

```text
greet user input:'<<'!='' create:self.greet_user(SplitCmd[2])
```

*   `greet`: Literal keyword 1.
*   `user`: Literal keyword 2.
*   `input:'<<'!=''`: The 3rd token (index 2) is captured if it's not empty.
*   `create:self.greet_user(SplitCmd[2])`: Calls your new method, passing the 3rd token (`SplitCmd` is 0-indexed).

**Important**: 
*   `SplitCmd` is the list of words the user typed (`['greet', 'user', 'Matthew']`).
*   `SplitCmd[2]` is "Matthew".

### 4. Advanced: Using Managers
If your command relates to Entities, implement the method in `FC_entitymanager.py`, then bridge it or call it directly if exposed.
Example file entry:
```text
delete thing input:self.EntityManager.isThing('<<') create:self.EntityManager.delete_thing(SplitCmd[2])
```
*Note: `self.EntityManager` is accessible because the parser resolves `self` to the FatController instance, which has `self.EntityManager`.*
