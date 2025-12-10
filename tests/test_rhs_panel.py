
import pytest
from unittest.mock import MagicMock, patch

class TestRHSPanel:


    def test_refresh_object_list_entities(self, app):
        # Setup
        app.ObjectTypeVar.set('Entities')
        app.EntityManager.getentitylist = MagicMock(return_value={'Entity1': MagicMock(), 'Entity2': MagicMock()})
        
        # Action
        app.refresh_object_list()
        
        # Assert
        app.ObjectListbox.delete.assert_called_with(0, 'end')
        # Insert called for each item
        # Since items are sorted, Entity1 then Entity2
        calls = app.ObjectListbox.insert.call_args_list
        assert len(calls) == 2
        assert calls[0][0][1] == 'Entity1'
        assert calls[1][0][1] == 'Entity2'

    def test_refresh_object_list_daemons(self, app):
        app.ObjectTypeVar.set('Daemons')
        app.DaemonManager.getDaemons = MagicMock(return_value={'Daemon1': MagicMock()})
        
        app.refresh_object_list()
        
        app.ObjectListbox.insert.assert_called_with('end', 'Daemon1')

    def test_on_type_selected_entities_creates_subdropdown(self, app):
        app.ObjectTypeVar.set('Entities')
        app.EntityManager.get_entity_types_metadata = MagicMock(return_value={'TSM': [], 'TELNET': []})
        
        app.on_type_selected(None)
        
        assert hasattr(app, 'EntityTypeCombo')
        # Check values
        app.EntityManager.get_entity_types_metadata.assert_called()

    def test_filter_entities(self, app):
        app.ObjectTypeVar.set('Entities')
        # Setup entities with types
        e1 = MagicMock()
        e1.getentitytype.return_value = 'TSM'
        e2 = MagicMock()
        e2.getentitytype.return_value = 'TELNET'
        app.EntityManager.getentitylist = MagicMock(return_value={'E1': e1, 'E2': e2})
        
        # Trigger creation of EntityTypeVar
        # We need get_entity_types_metadata to return keys for the dropdown
        app.EntityManager.get_entity_types_metadata = MagicMock(return_value={'TSM': [], 'TELNET': []})
        
        app.on_type_selected(None)
        
        # Set filter
        app.EntityTypeVar.set('TSM')
        
        app.refresh_object_list()
        
        # Should only insert E1
        args_list = app.ObjectListbox.insert.call_args_list
        # Note: insert calls might accumulate if mock not reset? No, refresh calls delete first.
        inserted = [call[0][1] for call in args_list]
        assert 'E1' in inserted
        assert 'E2' not in inserted

    def test_create_new_entity(self, app):
        import tkinter.ttk as ttk
        
        # Setup "New" mode
        app.ObjectTypeVar.set('Entities')
        app.ObjectListbox.curselection.return_value = [] # No selection
        
        # Explicitly set EntityTypeVar
        app.EntityTypeVar = MagicMock()
        app.EntityTypeVar.get.return_value = 'TSM'
        
        # Prepare the mock frame
        config_frame = MagicMock()
        config_frame.input_vars = {}
        
        # Mocks for EntityManager
        app.EntityManager.get_entity_types_metadata = MagicMock(return_value={'TSM': ['Port']})
        app.EntityManager.define = MagicMock()
        
        # Use patch.object on the module instance found in sys.modules
        # But since we can't easily reach that instance's attribute from here if it is dynamic,
        # we try patching 'FatController.ttk.Frame'.
        with patch('FatController.ttk.Frame', return_value=config_frame):
            # Action
            app.update_config_tabs()
        
            # Debug / Assertion
            assert config_frame.input_vars, "input_vars is empty. create_config_pane didn't populate it."
            assert 'Name' in config_frame.input_vars
            assert 'Port' in config_frame.input_vars
            
            # Simulate user input
            config_frame.input_vars['Name'].set('NewTSM')
            config_frame.input_vars['Port'].set('1234')
            
            # Setup for add_object_dialog
            app.ConfigSelectNotebook.tabs.return_value = ['tab1']
            app.ConfigSelectNotebook.nametowidget.return_value = config_frame
            
            app.add_object_dialog()
            
            # Verify define was called
            app.EntityManager.define.assert_called_with('TSM', ['NewTSM', '1234'])

    def test_remove_object(self, app):
        app.ObjectTypeVar.set('Aliases')
        app.ObjectListbox.curselection.return_value = [0]
        app.ObjectListbox.get.return_value = 'MyAlias'
        
        app.aliases = {'MyAlias': ['ls']}
        
        with patch('tkinter.messagebox.askyesno', return_value=True):
            app.remove_selected_objects()
            
        assert 'MyAlias' not in app.aliases


