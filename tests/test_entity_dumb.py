import pytest
from FC_DUMB import DUMB
from unittest.mock import MagicMock

class TestEntityDumb:
    @pytest.fixture
    def entity(self):
        return DUMB("TestDumb")

    def test_initialization(self, entity):
        assert entity.getname() == "TestDumb"
        assert entity.getentitytype() == "DUMB"
        assert entity.gettype() == "simple"

    @pytest.mark.asyncio
    async def test_execute(self, entity):
        cmd_list = ["some", "command"]
        result = await entity.execute(cmd_list)
        # Verify it inserts the "I would have executed this" line
        assert "I would have executed this" in result[0] 
        assert "some" in result
        assert "command" in result

    def test_display(self, entity):
        mock_ctrl = MagicMock()
        lines = ["line1", "line2"]
        entity.display(lines, mock_ctrl)
        
        assert mock_ctrl.insert.call_count == 2
        # Check call args
        mock_ctrl.insert.assert_any_call("end", "line1\n")
        mock_ctrl.insert.assert_any_call("end", "line2\n")

    def test_options(self, entity):
        entity.setoption("TestOpt", "yes")
        opts = entity.getoptions()
        assert "DUMB TestOpt yes" in opts
