import pytest
from FC_command_parser import CommandParser
from unittest.mock import MagicMock

class TestCommandParser:
    @pytest.fixture
    def parser(self):
        mock_app = MagicMock()
        return CommandParser(mock_app)

    def test_validate_expression_literals(self, parser):
        # Test basic literal checks if any logic uses them manually, 
        # though validate_expression usually handles special exprs.
        assert parser.validate_expression("'<<'!=''", "something", []) == True
        assert parser.validate_expression("'<<'!=''", "", []) == False

    def test_validate_expression_all(self, parser):
        assert parser.validate_expression("'<<'==('all')", "all", []) == True
        assert parser.validate_expression("'<<'==('all')", "something", []) == False

    def test_validate_expression_app_methods(self, parser):
        parser.app.EntityManager.isEntity.return_value = 1
        assert parser.validate_expression("self.EntityManager.isEntity", "some_entity", []) == True
        parser.app.EntityManager.isEntity.assert_called_with("some_entity")

        parser.app.EntityManager.isEntity.return_value = 0
        assert parser.validate_expression("self.EntityManager.isEntity", "bad_entity", []) == False
        
    def test_resolve_arg_literals(self, parser):
        assert parser._resolve_arg("'hello'", []) == "hello"
        
    def test_resolve_arg_splitcmd(self, parser):
        split_cmd = ["cmd", "arg1", "arg2"]
        assert parser._resolve_arg("SplitCmd[1]", split_cmd) == "arg1"
        assert parser._resolve_arg("SplitCmd[0]", split_cmd) == "cmd"
        
    def test_match_and_execute_literal_match(self, parser):
        cmd_def = {
            'matchers': [
                {'type': 'literal', 'value': 'show'},
                {'type': 'literal', 'value': 'stuff'}
            ]
        }
        matched, executed = parser.match_and_execute(cmd_def, ['show', 'stuff'])
        assert matched is True
        assert executed is False # No create action defined

    def test_match_and_execute_mismatch(self, parser):
        cmd_def = {
            'matchers': [
                {'type': 'literal', 'value': 'show'},
                {'type': 'literal', 'value': 'stuff'}
            ]
        }
        matched, executed = parser.match_and_execute(cmd_def, ['show', 'other'])
        assert matched is False
        assert executed is False

    def test_match_and_execute_with_create(self, parser):
        cmd_def = {
            'matchers': [
                {'type': 'literal', 'value': 'do'},
                {'type': 'create', 'expr': "self.do_something('test')"}
            ]
        }
        
        parser.app.do_something = MagicMock()
        
        matched, executed = parser.match_and_execute(cmd_def, ['do'])
        assert matched is True
        assert executed is True
        parser.app.do_something.assert_called_with('test')
