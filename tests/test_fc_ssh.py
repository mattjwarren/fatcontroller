import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import FC_SSH

class TestFCStackSSH(unittest.TestCase):
    
    def setUp(self):
        # We patch 'FC_SSH.Connection' object directly on the imported module
        self.mock_fabric_connection = MagicMock()
        self.patcher_conn = patch.object(FC_SSH, 'Connection', self.mock_fabric_connection)
        self.patcher_conn.start()
        
        self.mock_fabric_config = MagicMock()
        self.patcher_conf = patch.object(FC_SSH, 'Config', self.mock_fabric_config)
        self.patcher_conf.start()
        
        self.name = "TestSSH"
        self.host = "192.168.1.100"
        self.user = "testuser"
        self.password = "password123"
        self.keyfile = "None"
        
        self.ssh_entity = FC_SSH.SSH(self.name, self.host, self.user, self.password, self.keyfile)

    def tearDown(self):
        self.patcher_conn.stop()
        self.patcher_conf.stop()

    def test_init_connection_success(self):
        """Test that __init__ creates a connection object with correct config"""
        # Connection(...) should have been called
        self.mock_fabric_connection.assert_called()
        self.assertIsNotNone(self.ssh_entity.Connection)
        
        # Verify kwargs
        call_args = self.mock_fabric_connection.call_args
        kwargs = call_args[1]
        self.assertEqual(kwargs['host'], self.host)
        self.assertEqual(kwargs['user'], self.user)
        self.assertEqual(kwargs['connect_kwargs']['password'], self.password)
        self.assertEqual(kwargs['connect_kwargs']['timeout'], 10)
        self.assertEqual(kwargs['connect_kwargs']['look_for_keys'], False)
        
        # Verify Config was used
        self.mock_fabric_config.assert_called()
        config_args = self.mock_fabric_config.call_args[1]
        self.assertEqual(config_args['overrides']['ssh_config']['StrictHostKeyChecking'], 'no')
        self.assertEqual(config_args['overrides']['ssh_config']['NumberOfPasswordPrompts'], '0')
        # Ensure UserKnownHostsFile is NOT set (it was /dev/null before)
        self.assertNotIn('UserKnownHostsFile', config_args['overrides']['ssh_config'])
        self.assertIn('config', kwargs)

    def test_execute_success(self):
        """Test successful command execution"""
        mock_result = MagicMock()
        mock_result.stdout = "Output Line 1\nOutput Line 2"
        mock_result.stderr = ""
        mock_result.exited = 0
        
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.run.return_value = mock_result
        # Simulate connected state
        mock_connection_instance.is_connected = True
        
        output = self.ssh_entity.execute(["ls", "-la"])
        
        mock_connection_instance.run.assert_called_with("ls -la", hide=True, warn=True)
        expected_output = ["Output Line 1", "Output Line 2"]
        self.assertEqual(output, expected_output)

    def test_execute_retry_success(self):
        """Test that execute retries on failure and succeeds"""
        mock_connection_instance = self.ssh_entity.Connection
        
        # First call raises Exception, second succeeds
        mock_result = MagicMock()
        mock_result.stdout = "Success after retry"
        mock_result.stderr = ""
        
        mock_connection_instance.run.side_effect = [Exception("First Try Fail"), mock_result]
        
        output = self.ssh_entity.execute(["echo", "retry"])
        
        # Check that run was called twice
        self.assertEqual(mock_connection_instance.run.call_count, 2)
        
        # Check that close was called (part of retry logic)
        mock_connection_instance.close.assert_called()
        
        # Check output
        self.assertIn("Success after retry", output)

    def test_execute_with_stderr(self):
        """Test command execution with stderr"""
        mock_result = MagicMock()
        mock_result.stdout = "Standard Output"
        mock_result.stderr = "Error Output"
        
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.run.return_value = mock_result
        
        output = self.ssh_entity.execute(["bad_command"])
        
        self.assertIn("Standard Output", output)
        self.assertIn("--- STDERR ---", output)
        self.assertIn("Error Output", output)

    def test_execute_exception_handling(self):
        """Test that execute handles exceptions"""
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.run.side_effect = Exception("Connection Failed")
        
        output = self.ssh_entity.execute(["echo", "crash"])
        
        # Should return error in output list
        self.assertTrue(any("Error" in line for line in output))

    def test_getparameterdefs(self):
        defs = self.ssh_entity.getparameterdefs()
        self.assertEqual(defs, ["Name","Host","User","Pass","KeyFile"])

    def test_parameter_reconstruction(self):
        param_str = self.ssh_entity.getparameterstring()
        # Name is handled by entitymanager, so getparameterstring should only return params
        expected = f"{self.host} {self.user} {self.password} {self.keyfile}"
        self.assertEqual(param_str, expected)

if __name__ == '__main__':
    unittest.main()
