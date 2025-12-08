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
    class MockTk:
        def __init__(self, *args, **kwargs):
            pass
        
        def geometry(self, *args): pass
        def title(self, *args): pass
        def mainloop(self): pass
        def pack(self, *args, **kwargs): pass
        def add(self, *args, **kwargs): pass
        def protocol(self, *args, **kwargs): pass
        def destroy(self): pass
        def after(self, *args, **kwargs): pass
        
        # Add attributes accessed by FatController
        
    mock_tk_module = MagicMock()
    mock_tk_module.Tk = MockTk
    
    # Define a factory that swallows arguments and returns a MagicMock
    def MockWidgetFactory(*args, **kwargs):
        return MagicMock()

    # Mock other widgets using the factory
    mock_tk_module.PanedWindow = MockWidgetFactory
    mock_tk_module.Frame = MockWidgetFactory
    mock_tk_module.Text = MockWidgetFactory
    mock_tk_module.Scrollbar = MockWidgetFactory
    mock_tk_module.Entry = MockWidgetFactory
    
    # Constants
    mock_tk_module.END = 'end'
    mock_tk_module.BOTH = 'both'
    mock_tk_module.X = 'x'
    mock_tk_module.Y = 'y'
    mock_tk_module.LEFT = 'left'
    mock_tk_module.RIGHT = 'right'
    mock_tk_module.BOTTOM = 'bottom'
    mock_tk_module.HORIZONTAL = 'horizontal'
    mock_tk_module.VERTICAL = 'vertical'
    mock_tk_module.WORD = 'word'
    mock_tk_module.NONE = 'none'
    mock_tk_module.RAISED = 'raised'
    
    monkeypatch.setitem(sys.modules, 'tkinter', mock_tk_module)
    
    mock_ttk = MagicMock()
    mock_ttk.Notebook = MockWidgetFactory
    mock_ttk.Frame = MockWidgetFactory
    mock_ttk.Scrollbar = MockWidgetFactory
    mock_ttk.Treeview = MockWidgetFactory
    
    monkeypatch.setitem(sys.modules, 'tkinter.ttk', mock_ttk)
    monkeypatch.setitem(sys.modules, 'ttk', mock_ttk)

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
