import pytest
from unittest.mock import MagicMock, patch

class TestRHSPanelBusinessLogic:
    """Tests for RHS Panel business logic (headless-compatible)."""

    def test_refresh_object_data_entities_no_filter(self, app):
        """Test getting all entities without type filter"""
        # Setup
        e1 = MagicMock()
        e2 = MagicMock()
        app.EntityManager.getentitylist = MagicMock(return_value={'Entity1': e1, 'Entity2': e2})
        
        # Action
        result = app.refresh_object_data('Entities')
        
        # Assert - should return sorted list
        assert result == ['Entity1', 'Entity2']
        app.EntityManager.getentitylist.assert_called_once()

    def test_refresh_object_data_entities_with_filter(self, app):
        """Test filtering entities by type"""
        # Setup  
        e1 = MagicMock()
        e1.getentitytype.return_value = 'TSM'
        e2 = MagicMock()
        e2.getentitytype.return_value = 'SSH'
        app.EntityManager.getentitylist = MagicMock(return_value={'E1': e1, 'E2': e2})
        
        # Action
        result = app.refresh_object_data('Entities', entity_type_filter='TSM')
        
        # Assert - should only return TSM entity
        assert result == ['E1']

    def test_refresh_object_data_daemons(self, app):
        """Test getting daemon list"""
        # Setup
        app.DaemonManager.getDaemons = MagicMock(return_value={'Daemon1': MagicMock(), 'Daemon2': MagicMock()})
        
        # Action
        result = app.refresh_object_data('Daemons')
        
        # Assert
        assert result == ['Daemon1', 'Daemon2']

    def test_refresh_object_data_aliases(self, app):
        """Test getting alias list"""
        # Setup
        app.aliases = {'Alias1': ['cmd1'], 'Alias2': ['cmd2']}
        
        # Action
        result = app.refresh_object_data('Aliases')
        
        # Assert
        assert result == ['Alias1', 'Alias2']

    def test_refresh_object_data_scripts(self, app):
        """Test getting script list"""
        # Setup
        app.scripts = {'Script1': ['line1'], 'Script2': ['line2']}
        
        # Action
        result = app.refresh_object_data('Scripts')
        
        # Assert
        assert result == ['Script1', 'Script2']

    def test_refresh_object_data_substitutions(self, app):
        """Test getting substitutions list"""
        # Setup
        app.substitutions = {'Sub1': ['val1'], 'Sub2': ['val2']}
        
        # Action
        result = app.refresh_object_data('Substitutions')
        
        # Assert
        assert result == ['Sub1', 'Sub2']

    def test_get_filtered_entities_no_filter(self, app):
        """Test getting all entities without filter"""
        # Setup
        entities = {'E1': MagicMock(), 'E2': MagicMock()}
        app.EntityManager.getentitylist = MagicMock(return_value=entities)
        
        # Action
        result = app.get_filtered_entities()
        
        # Assert
        assert result == entities

    def test_get_filtered_entities_with_filter(self, app):
        """Test filtering entities by type"""
        # Setup
        e1 = MagicMock()
        e1.getentitytype.return_value = 'TSM'
        e2 = MagicMock()
        e2.getentitytype.return_value = 'SSH'
        app.EntityManager.getentitylist = MagicMock(return_value={'E1': e1, 'E2': e2})
        
        # Action
        result = app.get_filtered_entities('TSM')
        
        # Assert
        assert 'E1' in result
        assert 'E2' not in result
        assert len(result) == 1

    def test_remove_object_logic_entity(self, app):
        """Test removing an entity"""
        # Setup
        app.EntityManager.delete = MagicMock()
        
        # Action
        result = app.remove_object_logic('Entities', 'MyEntity')
        
        # Assert
        assert result is True
        app.EntityManager.delete.assert_called_once_with('MyEntity')

    def test_remove_object_logic_daemon(self, app):
        """Test removing a daemon"""
        # Setup
        app.DaemonManager.deleteDaemon = MagicMock()
        
        # Action
        result = app.remove_object_logic('Daemons', 'MyDaemon')
        
        # Assert
        assert result is True
        app.DaemonManager.deleteDaemon.assert_called_once_with('MyDaemon')

    def test_remove_object_logic_alias(self, app):
        """Test removing an alias"""
        # Setup
        app.aliases = {'MyAlias': ['ls']}
        
        # Action
        result = app.remove_object_logic('Aliases', 'MyAlias')
        
        # Assert
        assert result is True
        assert 'MyAlias' not in app.aliases

    def test_remove_object_logic_script(self, app):
        """Test removing a script"""
        # Setup
        app.scripts = {'MyScript': ['line1']}
        
        # Action
        result = app.remove_object_logic('Scripts', 'MyScript')
        
        # Assert
        assert result is True
        assert 'MyScript' not in app.scripts

    def test_remove_object_logic_substitution(self, app):
        """Test removing a substitution"""
        # Setup
        app.substitutions = {'MySub': ['value']}
        
        # Action
        result = app.remove_object_logic('Substitutions', 'MySub')
        
        # Assert
        assert result is True
        assert 'MySub' not in app.substitutions

    def test_remove_object_logic_handles_error(self, app):
        """Test that remove_object_logic returns False on error"""
        # Setup - make delete raise an exception
        app.EntityManager.delete = MagicMock(side_effect=Exception("Delete failed"))
        
        # Action
        result = app.remove_object_logic('Entities', 'BadEntity')
        
        # Assert
        assert result is False



