import sys
import os
import pytest
from unittest.mock import MagicMock

# Add project root to sys.path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def mock_tkinter(monkeypatch):
    """
    Mock tkinter to prevent GUI from opening during tests.
    We use a custom class for Tk instead of MagicMock to avoid 
    issues with subclassing MagicMock (which expects __init__ to accept kwargs).
    """
    import types
    
    # Create clean mock modules
    mock_tk_module = types.ModuleType('tkinter')
    
    class MockTk:
        def __init__(self, *args, **kwargs): pass
        def geometry(self, *args): pass
        def title(self, *args): pass
        def mainloop(self): pass
        def pack(self, *args, **kwargs): pass
        def add(self, *args, **kwargs): pass
        def protocol(self, *args, **kwargs): pass
        def destroy(self): pass
        def after(self, *args, **kwargs): pass
        def winfo_children(self): return []
        def nametowidget(self, name): return MagicMock()
        def select(self, *args): pass
        def forget(self, *args): pass
        def tab(self, *args, **kwargs): return ""
        def index(self, *args): return 0
    
    mock_tk_module.Tk = MockTk
    
    def MockWidgetFactory(*args, **kwargs):
        m = MagicMock()
        m.get.return_value = ""
        m.tabs.return_value = []
        return m

    # Standard widgets
    for w in ['PanedWindow', 'Frame', 'Text', 'Scrollbar', 'Entry', 'Label', 'Button', 'Listbox', 'PanedWindow']:
        setattr(mock_tk_module, w, MockWidgetFactory)

    class MockStringVar:
        def __init__(self, value='', *args, **kwargs): self._value = value
        def get(self): return self._value
        def set(self, value): self._value = value
    
    mock_tk_module.StringVar = MockStringVar
    mock_tk_module.messagebox = MagicMock()
    
    # Constants
    constants = {
        'END': 'end', 'BOTH': 'both', 'X': 'x', 'Y': 'y', 'LEFT': 'left', 'RIGHT': 'right', 
        'BOTTOM': 'bottom', 'HORIZONTAL': 'horizontal', 'VERTICAL': 'vertical', 
        'WORD': 'word', 'NONE': 'none', 'RAISED': 'raised', 'EXTENDED': 'extended',
        'ACTIVE': 'active', 'NORMAL': 'normal', 'DISABLED': 'disabled'
    }
    for k, v in constants.items():
        setattr(mock_tk_module, k, v)
        
    monkeypatch.setitem(sys.modules, 'tkinter', mock_tk_module)
    monkeypatch.setitem(sys.modules, 'tkinter.messagebox', mock_tk_module.messagebox)
    
    # Mock tkinter.ttk
    mock_ttk = types.ModuleType('tkinter.ttk')
    for w in ['Notebook', 'Frame', 'Scrollbar', 'Treeview', 'Combobox', 'PanedWindow', 'Label', 'Entry', 'Button']:
        setattr(mock_ttk, w, MockWidgetFactory)
        
    monkeypatch.setitem(sys.modules, 'tkinter.ttk', mock_ttk)
    monkeypatch.setitem(sys.modules, 'ttk', mock_ttk)
    
    # Mock ttkbootstrap
    mock_ttkbootstrap = types.ModuleType('ttkbootstrap')
    mock_ttkbootstrap.Window = MockTk
    for w in ['Frame', 'Label', 'Entry', 'Button', 'PanedWindow', 'Notebook', 'Combobox', 'Scrollbar']:
        setattr(mock_ttkbootstrap, w, MockWidgetFactory)
    
    # Mock ttkbootstrap.constants
    mock_bst_constants = types.ModuleType('ttkbootstrap.constants')
    for k, v in constants.items():
        setattr(mock_bst_constants, k, v)
    # Also inject constants directly into ttkbootstrap if necessary, but typical usage is from .constants
    
    mock_ttkbootstrap.constants = mock_bst_constants
    
    monkeypatch.setitem(sys.modules, 'ttkbootstrap', mock_ttkbootstrap)
    monkeypatch.setitem(sys.modules, 'ttkbootstrap.constants', mock_bst_constants)
    
    # Mock FC_SSH
    mock_ssh = MagicMock()
    monkeypatch.setitem(sys.modules, 'FC_SSH', mock_ssh)
    
    # Mock FC_command_parser
    mock_cp = MagicMock()
    mock_cp_instance = MagicMock()
    mock_cp_instance.parse_command_defs.return_value = {}
    mock_cp.CommandParser.return_value = mock_cp_instance
    monkeypatch.setitem(sys.modules, 'FC_command_parser', mock_cp)

@pytest.fixture
def app(mock_tkinter):
    """
    Create a FatController instance for testing.
    """
    import FatController
    
    # Mock methods that might interfere or are slow
    # We mock the ThreadedScheduler class itself to return a mock
    if isinstance(FatController.FC_ThreadedScheduler.ThreadedScheduler, type):
        original_scheduler = FatController.FC_ThreadedScheduler.ThreadedScheduler
        FatController.FC_ThreadedScheduler.ThreadedScheduler = MagicMock()
    
    app = FatController.FatController()
    
    # Mock specific attributes that are complex
    app.FCScheduler = MagicMock()
    
    yield app
    
    # Teardown logic
    if hasattr(app, 'FCScheduler'):
         try:
             app.FCScheduler.stop()
         except:
             pass
