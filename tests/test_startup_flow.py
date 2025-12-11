
import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import asyncio

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FatController


import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import asyncio
import importlib

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FatController

@pytest.fixture
def clean_imports():
    # Force reload of FatController to pick up mocked modules from conftest
    importlib.reload(FatController)
    yield
    importlib.reload(FatController)

def test_load_general_integration(mock_tkinter, clean_imports):
    """
    Functional test for startup flow:
    1. Mock filesystem for .sav files
    2. Instantiate FatController
    3. Verify EntityManager.define is called
    """
    
    # Define file content
    general_sav_content = "define entity SSH pi1 192.168.1.101 matt matt None\n"
    commands_sav_content = "define entity input:not(self.EntityManager.isEntity('<<')) input:'<<'!='' +* create:self.EntityManager.define(SplitCmd[2],SplitCmd[3:])\nload input:'<<'!='' create:self.load(SplitCmd[1])\nENDCOMMANDDEFS"

    mock_open_func = mock_open()
    
    def side_effect(filename, *args, **kwargs):
        # Normalize
        filename = filename.replace('\\', '/')
        print(f"DEBUG: Opening file: {filename}")
        if 'general.sav' in filename:
            return mock_open(read_data=general_sav_content).return_value
        elif 'FatControllerCommands.sav' in filename:
             return mock_open(read_data=commands_sav_content).return_value
        return mock_open(read_data="").return_value

    mock_open_func.side_effect = side_effect

    with patch('builtins.open', mock_open_func):
        # We also need to patch FatController's GUI parts because mock_tkinter fixture 
        # patches the MODULES (tkinter/ttk) but FatController might have imported objects directly 
        # if using `from tkinter import X`.
        # FatController uses `import tkinter as tk` and `import ttkbootstrap as ttk`.
        # So module patching in conftest should work IF FatController is reloaded.
        # clean_imports fixture does that.
        
        # Instantiate App
        app = FatController.FatController()
        
        # Verify mock_open was called
        print(f"DEBUG: mock_open called: {mock_open_func.called}")
        if mock_open_func.called:
             print(f"DEBUG: Input args: {mock_open_func.call_args_list}")
        
        assert mock_open_func.called, "open() was not called! Patching failed or logic skipped open."
        
        # DEBUG
        print(f"DEBUG: CommandDefinitions loaded: {len(app.CommandDefinitions)}")
        print(f"DEBUG: Entities: {app.EntityManager.Entities}")
        
        # Check if 'define entity' command is present
        define_cmds = [c for c in app.CommandDefinitions if c['matchers'][0]['value'] == 'define']
        print(f"DEBUG: Define commands: {len(define_cmds)}")
        
        # Mock EntityManager.define to verify calls
        # Note: EntityManager is instantiated inside __init__. 
        # We can't mock it *before* __init__ easily without patching the class `FC_entitymanager.entitymanager`.
        
        # Wait, if we want to verify `define` was called *during* Init (via processcommand -> load general),
        # we have a race condition: we need to spy on `EntityManager` *as it is created* or *before* `processcommand` runs.
        # But `processcommand` is called at the end of `__init__`.
        # So we should patch `FC_entitymanager.entitymanager` class to return a Mock, 
        # OR let it create the real one and rely on the fact that defining an entity 
        # calls `display.infodisplay` or modifies `app.EntityManager.Entities`.
        
        # Let's inspect `app.GetEntity('pi1')` to see if it exists.
        # That's a better "functional" check.
        
        assert app.EntityManager.isEntity('pi1'), f"Entity pi1 not found. Entities: {app.EntityManager.Entities}"
        entity = app.EntityManager.getEntity('pi1')
        assert entity.getname() == 'pi1'
        assert entity.getentitytype() == 'SSH'

if __name__ == '__main__':
    unittest.main()
