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

    @pytest.mark.asyncio
    async def test_execute_success(self, entity):
        import asyncio
        # Mock asyncio.create_subprocess_shell
        with patch('asyncio.create_subprocess_shell') as mock_create:
             mock_process = MagicMock()
             
             # communicate must be awaitable
             f = asyncio.Future()
             f.set_result((b"Output line 1\nOutput line 2", b""))
             mock_process.communicate.return_value = f
             
             # create_subprocess_shell returns awaitable process
             async def get_mock_process(*args, **kwargs):
                  return mock_process
             
             mock_create.side_effect = get_mock_process
             
             result = await entity.execute(["ls", "-l"])
             
             mock_create.assert_called_once()
             assert "Output line 1" in result
             assert "Output line 2" in result

    @pytest.mark.asyncio
    async def test_execute_error(self, entity):
        import asyncio
        with patch('asyncio.create_subprocess_shell') as mock_create:
             mock_process = MagicMock()
             
             f = asyncio.Future()
             f.set_result((b"", b"Error happened"))
             mock_process.communicate.return_value = f
             
             async def get_mock_process(*args, **kwargs):
                  return mock_process
             
             mock_create.side_effect = get_mock_process
             
             result = await entity.execute(["bad_command"])
             
             assert "Error happened" in result

    @pytest.mark.asyncio
    async def test_execute_exception(self, entity):
        # We can simulate exception in creation
        with patch('asyncio.create_subprocess_shell', side_effect=Exception("Subprocess failed")) as mock_create:
             result = await entity.execute(["cmd"])
             assert len(result) == 1
             assert "Error executing command: Subprocess failed" in result[0]
