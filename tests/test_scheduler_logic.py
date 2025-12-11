
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_ThreadedScheduler

class TestSchedulerLogic(unittest.TestCase):
    def setUp(self):
        # We initialized scheduler with daemon=1 by default
        self.scheduler = FC_ThreadedScheduler.ThreadedScheduler()

    def tearDown(self):
        # Ensure we don't leave threads running if start() was called (it shouldn't be in these logic tests)
        if self.scheduler.is_alive():
             self.scheduler.stop()

    def test_initialization(self):
        self.assertEqual(self.scheduler._running, {})
        self.assertEqual(self.scheduler._scheduled, {})
        self.assertEqual(self.scheduler._onDemand, {})

    def test_add_periodic_action(self):
        task = MagicMock()
        task.name.return_value = "TestTask"
        
        start_time = time.time() + 100
        period = 60
        
        self.scheduler.addPeriodicAction(start_time, period, task, "TestTask")
        
        self.assertTrue(self.scheduler.hasScheduled("TestTask"))
        
        scheduled_task = self.scheduler.scheduled("TestTask")
        self.assertIsNotNone(scheduled_task)
        # Verify handler logic (internal but key)
        # The scheduler wraps task in a handler. 
        # We can't access check exact wrapper type easily without import, 
        # but we can check if it's there.
        
    def test_add_remove_action(self):
        task = MagicMock()
        task.name.return_value = "TestTask"
        
        self.scheduler.addPeriodicAction(time.time(), 60, task, "TestTask")
        self.assertTrue(self.scheduler.hasScheduled("TestTask"))
        
        self.scheduler.unregisterTask("TestTask")
        
        self.assertFalse(self.scheduler.hasScheduled("TestTask"))
        self.assertFalse(self.scheduler.hasRunning("TestTask")) 

    def test_state_management(self):
        # Test basic list retrieval
        self.assertEqual(self.scheduler.scheduledTasks(), {})
        
        task = MagicMock()
        task.name.return_value = "TestTask"
        self.scheduler.addPeriodicAction(time.time(), 60, task, "TestTask")
        
        tasks_map = self.scheduler.scheduledTasks()
        self.assertEqual(len(tasks_map), 1)
        self.assertIn("TestTask", tasks_map)
        self.assertEqual(tasks_map["TestTask"].name(), "TestTask")

if __name__ == '__main__':
    unittest.main()
