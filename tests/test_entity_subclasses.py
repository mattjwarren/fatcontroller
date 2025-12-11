
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_entity
import FC_LOCAL
import FC_DUMB


import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import asyncio

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_entity
import FC_LOCAL
import FC_DUMB

class TestEntitySubclasses(unittest.TestCase):
    
    def setUp(self):
        # We need an event loop for async tests if not using pytest-asyncio
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_dumb_entity(self):
        entity = FC_DUMB.DUMB("TestDumb")
        cmd = ["echo", "test"]
        
        # Execute async method
        result = self.loop.run_until_complete(entity.execute(cmd, trace_id="12345678"))
        
        self.assertIn('I would have executed this', result)
        self.assertIn('echo', result)
        self.assertIn('test', result)

    def test_local_entity(self):
        # Mock asyncio.create_subprocess_shell
        with patch('asyncio.create_subprocess_shell', new_callable=AsyncMock) as mock_shell:
             entity = FC_LOCAL.LOCAL("TestLocal")
             
             # Setup mock process
             mock_process = AsyncMock()
             mock_process.communicate.return_value = (b"stdout_line1\nstdout_line2\n", b"stderr_line1\n")
             mock_shell.return_value = mock_process
             
             cmd = ["echo", "hello"]
             result = self.loop.run_until_complete(entity.execute(cmd, trace_id="aabbccdd"))
             
             # Verify call
             mock_shell.assert_called_once()
             args, _ = mock_shell.call_args
             self.assertIn("echo hello", args[0])
             
             # Verify output
             self.assertIn("stdout_line1", result)
             self.assertIn("stdout_line2", result)
             self.assertIn("stderr_line1", result)

if __name__ == '__main__':
    unittest.main()

