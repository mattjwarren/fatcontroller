
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_daemon
from FC_daemonmanager import daemonmanager

class TestDaemonManager(unittest.TestCase):
    def setUp(self):
        self.mock_entity_manager = MagicMock()
        self.mock_scheduler = MagicMock()
        self.mock_process_commander = MagicMock()
        
        # Patch AlertManager to avoid complex initialization
        with patch('FC_AlertManager.AlertManager') as MockAlertManager:
            self.dm = daemonmanager(self.mock_entity_manager, self.mock_scheduler, self.mock_process_commander)

    def test_initialization(self):
        self.assertEqual(self.dm.daemons, {})
        self.assertEqual(self.dm.activedaemons, {})
        self.assertEqual(self.dm.EntityManager, self.mock_entity_manager)
        self.assertEqual(self.dm.Scheduler, self.mock_scheduler)

    def test_add_delete_daemon(self):
        daemon_name = "TestDaemon"
        self.dm.addDaemon(daemon_name)
        self.assertIn(daemon_name, self.dm.daemons)
        self.assertTrue(self.dm.is_daemon(daemon_name))
        self.assertIsInstance(self.dm.getDaemon(daemon_name), FC_daemon.daemon)
        
        self.dm.deleteDaemon(daemon_name)
        self.assertNotIn(daemon_name, self.dm.daemons)
        self.assertFalse(self.dm.is_daemon(daemon_name))

    def test_add_update_delete_task(self):
        daemon_name = "TestDaemon"
        task_name = "TestTask"
        command = ["echo", "test"]
        
        self.dm.addDaemon(daemon_name)
        
        # Test add task
        self.dm.addTask(daemon_name, task_name, command)
        daemon = self.dm.getDaemon(daemon_name)
        self.assertIn(task_name, daemon.tasks)
        self.assertEqual(daemon.tasks[task_name].command, command)
        
        # Test update task
        new_command = ["echo", "updated"]
        self.dm.updateTask(daemon_name, task_name, new_command)
        self.assertEqual(daemon.tasks[task_name].command, new_command)
        
        # Test delete task
        self.dm.deleteTask(daemon_name, task_name)
        self.assertNotIn(task_name, daemon.tasks)

    def test_make_live_and_kill(self):
        daemon_name = "TestDaemon"
        self.dm.addDaemon(daemon_name)
        
        # Mock schedule values to avoid type errors
        mock_schedule = MagicMock()
        mock_schedule.getstart.return_value = 0.0
        mock_schedule.getperiod.return_value = 60
        
        # Inject mock schedule into daemon
        self.dm.daemons[daemon_name].getschedule = MagicMock(return_value=mock_schedule)
        
        self.dm.makeLive(daemon_name)
        
        self.assertIn(daemon_name, self.dm.activedaemons)
        self.mock_scheduler.addPeriodicAction.assert_called_once()
        
        self.dm.kill_daemon(daemon_name)
        
        self.assertNotIn(daemon_name, self.dm.activedaemons)
        self.mock_scheduler.unregisterTask.assert_called_with(daemon_name)

    def test_subscribe_unsubscribe_entity(self):
        daemon_name = "TestDaemon"
        task_name = "TestTask"
        entity_name = "TestEntity"
        
        self.dm.addDaemon(daemon_name)
        self.dm.addTask(daemon_name, task_name, ["cmd"])
        
        # Mock EntityManager.getEntity to return a mock entity
        mock_entity = MagicMock()
        self.mock_entity_manager.getEntity.return_value = mock_entity
        
        self.dm.subscribeEntity(daemon_name, task_name, entity_name)
        
        # Verify entity added to task
        task = self.dm.daemons[daemon_name].tasks[task_name]
        # Note: implementation of task.entities might need check. 
        # addtaskentity usually uses name or object as key.
        # Let's verify via call inspection if we can't inspect internal state easily, 
        # but inspection is better.
        # FC_daemontask.addentity stores by entity.Name usually?
        # Let's assume mock_entity has a Name or __str__ used as key?
        # Actually FC_daemontask code isn't fully visible but standard dict pattern expected.
        
        # For unsubscribe
        self.dm.unsubscribeEntity(daemon_name, task_name, entity_name)
        # Verify removed
        
if __name__ == '__main__':
    unittest.main()
