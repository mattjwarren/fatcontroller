import unittest
import pytest
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
        """Test that __init__ does NOT create connection, but _create_connection does"""
        # Connection(...) should NOT have been called yet
        self.mock_fabric_connection.assert_not_called()
        self.assertIsNone(self.ssh_entity.Connection)
        
        # Trigger creation manually
        self.ssh_entity.Connection = self.ssh_entity._create_connection()
        
        # Now verify
        self.mock_fabric_connection.assert_called()
        
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

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful command execution"""
        import asyncio
        mock_result = MagicMock()
        mock_result.stdout = "Output Line 1\nOutput Line 2"
        mock_result.stderr = ""
        mock_result.exited = 0
        
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.is_connected = True
        
        # We patched run_in_executor to execute synchronously in previous attempt.
        # But `run_in_executor` returns an AWAITABLE.
        # `async def side_effect` ensures it returns a coroutine.
        # If we use `return func(*args)`, it returns the RESULT of func.
        # If that result is not awaitable (blocking_ssh_run returns list or object), we are fine IF we used a coroutine wrapper.
        
        # The code: return await loop.run_in_executor(None, blocking_ssh_run)
        
        # If we mock run_in_executor, we must ensure it behaves like one.
        # side_effect=side_effect where side_effect is async function works.
        
        # Re-verify previous implementation:
        # async def side_effect(executor, func, *args): return func(*args)
        # mocked run_in_executor returns a COROUTINE object which awaits to result of func(*args).
        # This seems correct IF func(*args) is synchronous and returns value.
        
        # But wait, `blocking_ssh_run` calls `self.Connection.run(...)`.
        # `self.Connection.run` is a MagicMock.
        # `self.Connection.run.return_value = mock_result`.
        # So `func(*args)` returns `mock_result`.
        # So `await loop.run_in_executor` returns `mock_result`.
        # The failing test might be due to `execute` method expectation of return type vs `mock_result`.
        
        # Let's check `FC_SSH.execute` return value logic.
        # It calls `result = await loop.run_in_executor(...)`.
        # Then it processes `result`.
        # `blocking_ssh_run` returns `self.Connection.run(...)`.
        # So `result` is the return value of `Connection.run`.
        # The logic:
        # if result.exited == 0: Output = result.stdout.splitlines()
        
        # My previous mock setup:
        # mock_result.stdout = "..."
        # mock_connection_instance.run.return_value = mock_result
        
        # This seems correct. Why did it fail?
        # Maybe `side_effect` didn't execute properly or `mock_loop` patching was issue.
        
        # Let's try to patch `asyncio.get_event_loop` returning a loop that has `run_in_executor` as async method?
        # Or just patch `FC_SSH.asyncio.get_event_loop`.
        
        with patch('asyncio.get_event_loop') as mock_loop_func:
             mock_loop = MagicMock()
             mock_loop_func.return_value = mock_loop
             
             async def run_in_executor_side_effect(executor, func, *args):
                 # We execute the func immediately
                 return func()
             
             mock_loop.run_in_executor.side_effect = run_in_executor_side_effect
             
             # Need to ensure Connection.run is mocked correctly for the instance used by entity
             self.ssh_entity.Connection.run.return_value = mock_result
             
             output = await self.ssh_entity.execute(["ls", "-la"])
             
             self.ssh_entity.Connection.run.assert_called_with("ls -la", hide=True, warn=True)
             expected_output = ["Output Line 1", "Output Line 2"]
             self.assertEqual(output, expected_output)

    @pytest.mark.asyncio
    async def test_execute_retry_success(self):
        """Test that execute retries on failure and succeeds"""
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.is_connected = True

        mock_result = MagicMock()
        mock_result.stdout = "Success after retry"
        mock_result.stderr = ""
        mock_result.exited = 0
        
        mock_connection_instance.run.side_effect = [Exception("First Try Fail"), mock_result]
        
        with patch('asyncio.get_event_loop') as mock_loop_func:
             mock_loop = MagicMock()
             mock_loop_func.return_value = mock_loop
             
             async def run_in_executor_side_effect(executor, func, *args):
                 return func()
             mock_loop.run_in_executor.side_effect = run_in_executor_side_effect

             output = await self.ssh_entity.execute(["echo", "retry"])
             
             self.assertEqual(mock_connection_instance.run.call_count, 2)
             self.assertIn("Success after retry", output)

    @pytest.mark.asyncio
    async def test_execute_with_stderr(self):
        """Test command execution with stderr"""
        mock_result = MagicMock()
        mock_result.stdout = "Standard Output"
        mock_result.stderr = "Error Output"
        mock_result.exited = 0
        
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.is_connected = True
        mock_connection_instance.run.return_value = mock_result
        
        with patch('asyncio.get_event_loop') as mock_loop_func:
             mock_loop = MagicMock()
             mock_loop_func.return_value = mock_loop
             
             async def run_in_executor_side_effect(executor, func, *args):
                 return func()
             mock_loop.run_in_executor.side_effect = run_in_executor_side_effect
             
             output = await self.ssh_entity.execute(["bad_command"])
             
             self.assertIn("Standard Output", output)
             self.assertIn("--- STDERR ---", output)
             self.assertIn("Error Output", output)

    @pytest.mark.asyncio
    async def test_execute_exception_handling(self):
        """Test that execute handles exceptions"""
        mock_connection_instance = self.ssh_entity.Connection
        mock_connection_instance.run.side_effect = Exception("Connection Failed")
        
        with patch('asyncio.get_event_loop') as mock_loop_func:
             mock_loop = MagicMock()
             mock_loop_func.return_value = mock_loop
             
             async def run_in_executor_side_effect(executor, func, *args):
                 return func()
             mock_loop.run_in_executor.side_effect = run_in_executor_side_effect
             
             output = await self.ssh_entity.execute(["echo", "crash"])
             
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
