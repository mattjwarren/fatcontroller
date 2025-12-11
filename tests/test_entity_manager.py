
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_entitymanager
import FC_LOCAL
import FC_DUMB

class TestEntityManager(unittest.TestCase):
    
    def setUp(self):
        # We need to clean up sys.modules to force reload or just reload
        import importlib
        
        self.mock_notebook = MagicMock()
        self.mock_focus_return = MagicMock()
        
        # Patch modules globally for the reload
        self.ttk_patcher = patch.dict('sys.modules', {
            'ttkbootstrap': MagicMock(),
            'ttkbootstrap.constants': MagicMock(),
            'tkinter': MagicMock(), 
            'FC_formatter': MagicMock()
        })
        self.ttk_patcher.start()
        
        # Mock ttkbootstrap attributes specifically
        sys.modules['ttkbootstrap'].Frame = MagicMock()
        sys.modules['ttkbootstrap'].Notebook = MagicMock()
        
        # Reload FC_entitymanager so it picks up the mocked modules
        importlib.reload(FC_entitymanager)
        
        # Re-mock formatter return value on the reloaded module or just pass it in
        # The manager init takes arguments, so we can pass mocks there.
        # But 'FC_formatter.OutputFormatter' is used inside init? 
        # No, line 45: self.display=FC_formatter.OutputFormatter(...)
        
        # Setup the manager
        self.manager = FC_entitymanager.entitymanager(self.mock_notebook, self.mock_focus_return)
        
        # Ensure display is a mock
        self.manager.display = MagicMock()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.ttk_patcher.stop()
        self.loop.close()

    def test_define_dumb_entity(self):
        # define(type, typeparms)
        # For DUMB: ['Name']
        args = ['TestDumb']
        self.manager.define('DUMB', args)
        
        self.assertTrue(self.manager.isEntity('TestDumb'))
        entity = self.manager.getEntity('TestDumb')
        self.assertIsInstance(entity, FC_DUMB.DUMB)
        self.assertEqual(entity.getname(), 'TestDumb')
        
        # Check tab creation
        try:
            self.mock_notebook.add.assert_called()
        except AssertionError:
            print(f"DEBUG info: {self.manager.display.infodisplay.call_args_list}")
            raise
        self.assertIn('TestDumb', self.manager.OutPages)

    def test_define_local_entity(self):
        # For LOCAL: ['Name']
        args = ['TestLocal']
        self.manager.define('LOCAL', args)
        
        self.assertTrue(self.manager.isEntity('TestLocal'))
        self.assertIsInstance(self.manager.getEntity('TestLocal'), FC_LOCAL.LOCAL)

    def test_define_unknown_type(self):
        self.manager.define('UNKNOWN_TYPE', ['Name'])
        self.assertFalse(self.manager.isEntity('Name'))
        # Should call display with error
        self.manager.display.infodisplay.assert_called_with(unittest.mock.ANY)

    def test_delete_entity(self):
        self.manager.define('DUMB', ['ToDelete'])
        self.assertTrue(self.manager.isEntity('ToDelete'))
        
        self.manager.delete('ToDelete')
        self.assertFalse(self.manager.isEntity('ToDelete'))
        self.assertNotIn('ToDelete', self.manager.OutPages)
        # Should forget mock frame
        self.mock_notebook.forget.assert_called()

    def test_execute_entity_success(self):
        self.manager.define('DUMB', ['ExecTarget'])
        
        # Mock the entity's execute method to return immediately
        entity = self.manager.getEntity('ExecTarget')
        entity.execute = AsyncMock(return_value=['Output Line 1'])
        
        cmd = ['echo', 'test']
        # Calling manager.execute
        # Note: manager.execute is async
        result = self.loop.run_until_complete(self.manager.execute('ExecTarget', cmd, trace_id='test_trace'))
        
        entity.execute.assert_called_with(cmd, trace_id='test_trace')
        self.assertEqual(result, ['Output Line 1'])
        
        # GUI update is scheduled via after. Mocks check:
        self.mock_notebook.after.assert_called()

    def test_execute_unknown_entity(self):
        result = self.loop.run_until_complete(self.manager.execute('NonExistent', ['cmd']))
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
