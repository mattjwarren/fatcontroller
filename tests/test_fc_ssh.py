import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import FC_SSH

class TestFCStackSSH(unittest.TestCase):
    
    def setUp(self):
        # Mock paramiko at the start of each test
        self.mock_paramiko = MagicMock()
        # We need to patch the global paramiko in FC_SSH if it was imported successfully
        # or mock it if it wasn't.
        # Since we can't easily control the import inside the module once loaded, 
        # we will patch 'FC_SSH.paramiko'
        
        self.patcher = patch('FC_SSH.paramiko', self.mock_paramiko)
        self.patcher.start()
        
        # Define a real exception class for the mock to use
        class MockSSHException(Exception):
            pass
        self.mock_paramiko.ssh_exception.SSHException = MockSSHException
        self.mock_paramiko.SSHException = MockSSHException # Just in case it's accessed directly
        
        # Setup common test data
        self.name = "TestSSH"
        self.host = "192.168.1.100"
        self.user = "testuser"
        self.password = "password123"
        self.keyfile = "None"
        
        self.ssh_entity = FC_SSH.SSH(self.name, self.host, self.user, self.password, self.keyfile)

    def tearDown(self):
        self.patcher.stop()

    def test_init_connection_success(self):
        """Test that __init__ attempts to open a connection"""
        self.mock_paramiko.SSHClient.return_value.connect.assert_called()
        self.assertIsNotNone(self.ssh_entity.Connection)

    def test_execute_success(self):
        """Test successful command execution"""
        # Setup mock return values
        mock_client = self.ssh_entity.Connection
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        
        mock_stdout.read.return_value = b"Output Line 1\nOutput Line 2"
        mock_stderr.read.return_value = b""
        
        # mock_client.exec_command returns (stdin, stdout, stderr)
        mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        output = self.ssh_entity.execute(["ls", "-la"])
        
        # Check if exec_command was called with joined string
        mock_client.exec_command.assert_called_with("ls -la")
        
        # Check output parsing
        expected_output = ["Output Line 1", "Output Line 2"]
        self.assertEqual(output, expected_output)

    def test_execute_failure_reconnect(self):
        """Test that execute attempts reconnect on SSHException"""
        mock_client = self.ssh_entity.Connection
        
        # First call raises SSHException
        mock_client.exec_command.side_effect = [
            self.mock_paramiko.ssh_exception.SSHException("Connection Lost"), # First attempt fails
            (None, MagicMock(read=lambda: b"Success after retry"), MagicMock(read=lambda: b"")) # Second attempt succeeds
        ]
        
        output = self.ssh_entity.execute(["echo", "retry"])
        
        # Should have called exec_command twice (or at least called connect again)
        # We can check if connect was called more than once (init + reconnect)
        print(self.mock_paramiko.SSHClient.return_value.connect.call_count)
        self.assertTrue(self.mock_paramiko.SSHClient.return_value.connect.call_count >= 2)
        
        self.assertIn("Success after retry", output)

    def test_getparameterdefs(self):
        """Test parameter definitions for GUI"""
        defs = self.ssh_entity.getparameterdefs()
        self.assertEqual(defs, ["Name","Host","User","Pass","KeyFile"])

    def test_parameter_reconstruction(self):
        """Test getparameterstring logic"""
        param_str = self.ssh_entity.getparameterstring()
        # Should allow reconstruction: name host user pass keyfile
        expected = f"{self.name} {self.host} {self.user} {self.password} {self.keyfile}"
        self.assertEqual(param_str, expected)

if __name__ == '__main__':
    unittest.main()
