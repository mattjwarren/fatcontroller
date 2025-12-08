
import os
import pytest
from unittest.mock import MagicMock

class TestReadFileCommand:
    
    def test_readfile_success(self, app, tmp_path):
        # Create a temporary file with commands
        d = tmp_path / "subdir"
        d.mkdir()
        p = d / "commands.txt"
        p.write_text("show entities\nmessage 'hello world'\n")
        
        # Mock processcommand to verify it gets called
        app.processcommand = MagicMock(wraps=app.processcommand)
        
        # Call read_command_file
        app.read_command_file(str(p))
        
        # Verify calls
        # Note: read_command_file calls processcommand for each line
        # but processcommand is also recursive if it hits aliases etc.
        # Here we just want to ensure it was called for our lines.
        
        # We expect 2 calls for the lines in the file
        # Check that it was called with stripped lines
        assert app.processcommand.call_count == 2
        app.processcommand.assert_any_call("show entities")
        app.processcommand.assert_any_call("message 'hello world'")

    def test_readfile_file_not_found(self, app):
        app.display.infodisplay = MagicMock()
        
        app.read_command_file("non_existent_file.txt")
        
        # Should log an error to display
        app.display.infodisplay.assert_any_call("Error: File 'non_existent_file.txt' not found.")
        
    def test_readfile_empty(self, app, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("")
        
        app.processcommand = MagicMock()
        
        app.read_command_file(str(p))
        
        assert app.processcommand.call_count == 0

    def test_readfile_comments(self, app, tmp_path):
        p = tmp_path / "comments.txt"
        p.write_text("# This is a comment\nshow entities\n   # Indented comment\n")
        
        app.processcommand = MagicMock()
        
        app.read_command_file(str(p))
        
        assert app.processcommand.call_count == 1
        app.processcommand.assert_called_with("show entities")

