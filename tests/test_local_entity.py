import pytest
import subprocess
from FC_LOCAL import LOCAL
from unittest.mock import MagicMock, patch

class TestEntityLocal:
    @pytest.fixture
    def entity(self):
        return LOCAL("TestLocal")

    def test_initialization(self, entity):
        assert entity.getname() == "TestLocal"
        assert entity.getentitytype() == "LOCAL"

    @patch('subprocess.Popen')
    def test_execute_success(self, mock_popen, entity):
        # Mock subprocess
        process_mock = MagicMock()
        process_mock.stdout.readlines.return_value = ["Output line 1\n", "Output line 2"]
        process_mock.stderr.readlines.return_value = []
        mock_popen.return_value = process_mock

        result = entity.execute(["ls", "-l"])
        
        mock_popen.assert_called_once()
        # Verify result contains stdout
        assert "Output line 1\n" in result
        assert "Output line 2" in result

    @patch('subprocess.Popen')
    def test_execute_error(self, mock_popen, entity):
        process_mock = MagicMock()
        process_mock.stdout.readlines.return_value = []
        process_mock.stderr.readlines.return_value = ["Error happened"]
        mock_popen.return_value = process_mock

        result = entity.execute(["bad_command"])
        
        assert "Error happened" in result

    @patch('subprocess.Popen')
    def test_execute_exception(self, mock_popen, entity):
        mock_popen.side_effect = Exception("Subprocess failed")
        
        result = entity.execute(["cmd"])
        assert len(result) == 1
        assert "Error executing command: Subprocess failed" in result[0]
