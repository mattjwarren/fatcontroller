
import unittest
import logging
import asyncio
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_ScheduledTask
import FC_daemon
import FC_entity
import FC_entitymanager

class TestLoggingVerification(unittest.TestCase):
    def setUp(self):
        # Configure logging to capture output
        self.log_capture = io.StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(self.handler)
        
    def tearDown(self):
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.handler)

    async def test_trace_id_propagation(self):
        """Verify that Trace ID is generated and propagated in logs."""
        
        # Setup mocks
        mock_entity_manager = MagicMock()
        mock_alert_manager = MagicMock()
        
        # Create a daemon
        daemon = FC_daemon.daemon(mock_entity_manager, mock_alert_manager, "TestDaemon")
        
        # Create a mock entity
        mock_entity = MagicMock()
        # Mock execute to return some output and log something to verify trace id inside
        async def mock_execute(cmd_list, trace_id=None):
            logging.debug(f"[{trace_id}] MockEntity executing")
            return ["Output line 1"]
            
        mock_entity.execute = mock_execute
        
        # Add task to daemon
        daemon.addtask("TestTask", ["echo", "test"])
        # Add entity to task - manually since addtaskentity uses EntityManager string lookup usually?
        # No, daemon.addtaskentity(taskname, entity_instance)
        
        # We need to bypass the lookup if we passed a mock.
        # But daemontask.addentity expects an object.
        daemon.tasks["TestTask"].addentity(mock_entity)
        
        # Run daemon
        # run is async static method? No, I changed it to `async def run(adaemon):`
        # Wait, the signature in FC_daemon.py is `async def run(adaemon):`
        # And it is called... how? `await FC_daemon.run(daemon_instance)`?
        # Or `await daemon_instance.run(daemon_instance)`?
        # `ScheduledTask._run` calls `self.run(self)`.
        
        # Let's verify `ScheduledTask.run` signature in `FC_daemon`.
        # `async def run(adaemon):`
        # So `daemon.run(daemon)` is how it's called if called directly.
        
        await daemon.run(daemon)
        
        # Check logs
        logs = self.log_capture.getvalue()
        print("Captured Logs:\n", logs)
        
        # Verify Trace ID presence
        # We expect [xxxxxxxx] pattern.
        import re
        trace_id_pattern = re.compile(r'\[([a-f0-9\-]{8})\]')
        match = trace_id_pattern.search(logs)
        self.assertTrue(match, "Trace ID not found in logs")
        
        trace_id = match.group(1)
        self.assertIn(f"[{trace_id}] Daemon TestDaemon starting run cycle", logs)
        self.assertIn(f"[{trace_id}] MockEntity executing", logs)
        self.assertIn(f"[{trace_id}] Daemon TestDaemon finished run cycle", logs)

import io
if __name__ == '__main__':
    unittest.main()
