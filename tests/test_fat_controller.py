import pytest
from unittest.mock import MagicMock, patch

class TestFatController:
    
    def test_initialization(self, app):
        assert app.installroot is not None
        assert app.CommandParser is not None
        assert app.EntityManager is not None
        assert app.DaemonManager is not None

    def test_aliases(self, app):
        app.define_alias("ll", ["ls", "-l"])
        assert app.is_alias("ll") == 1
        
        app.del_alias("ll")
        assert app.is_alias("ll") == 0

    def test_substitutions(self, app):
        app.definesubstitution("FOO", ["bar"])
        assert app.issubstitute("FOO") == 1
        
        assert app.processsubstitutions("echo ~FOO") == "echo bar"
        
        app.delsubstitution("FOO")
        assert app.issubstitute("FOO") == 0

    def test_process_command_basic(self, app):
        # Mock specific command handling if needed, or rely on mocking EntityManager
        # Mock specific command handling if needed, or rely on mocking EntityManager
        async def mock_execute(*args, **kwargs): pass
        app.EntityManager.execute = MagicMock(side_effect=mock_execute)
        app.EntityManager.LastExecutedEntity = "TestEntity"
        app.loop = MagicMock() # Mock the loop to bypass check
        
        # Test a command that falls through to entity
        app.processcommand("some_command arg1")
        
        app.EntityManager.execute.assert_called()
        
    def test_comprehend_command(self, app):
        # Test list comprehension logic
        cmds = app.ComprehendCommand("show [[1..3]]")
        assert len(cmds) == 3
        assert "show 1" in cmds
        assert "show 3" in cmds
        
        cmds = app.ComprehendCommand("show [[A,B]]")
        assert len(cmds) == 2
        assert "show A" in cmds
        assert "show B" in cmds

    def test_scripts(self, app):
        app.appendtoscript("myscript", ["echo hello"])
        assert app.isScript("myscript") == 1
        
        app.delscript("myscript")
        assert app.isScript("myscript") == 0
