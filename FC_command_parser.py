
import re
import sys
import logging
from typing import List, Dict, Any, Tuple, Optional

class CommandParser:
    def __init__(self, app: Any) -> None:
        self.app = app # The FatController instance

    def parse_command_defs(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses the command definitions file and returns a list of command structures.
        """
        commands: List[Dict[str, Any]] = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line == 'ENDCOMMANDDEFS':
                        continue
                        
                    parts = line.split()
                    command_def: Dict[str, Any] = {
                        'matchers': []
                    }
                    
                    for part in parts:
                        if part.startswith('input:'):
                            expr = part[len('input:'):]
                            command_def['matchers'].append({'type': 'input', 'expr': expr})
                        elif part.startswith('create:'):
                            expr = part[len('create:'):]
                            command_def['matchers'].append({'type': 'create', 'expr': expr})
                        elif part == '+*':
                            command_def['matchers'].append({'type': 'wildcard'})
                        else:
                            command_def['matchers'].append({'type': 'literal', 'value': part})
                    
                    commands.append(command_def)
        except Exception as e:
            logging.error(f"Error loading command defs: {e}")
            
        return commands

    def match_and_execute(self, command_def: Dict[str, Any], split_cmd: List[str]) -> Tuple[bool, bool]:
        """
        Matches a split command against a definition and executes if successful.
        Returns (Success, ActionExecuted) tuple.
        """
        ctr = 0
        create_expr = None
        split_len = len(split_cmd)
        
        for matcher in command_def['matchers']:
            mtype = matcher['type']
            
            if mtype == 'create':
                create_expr = matcher['expr']
                ctr += 1
                continue
            
            if mtype == 'input':
                if ctr >= split_len:
                    return False, False # Missing required input
                
                token = split_cmd[ctr]
                if not self.validate_expression(matcher['expr'], token, split_cmd):
                    return False, False
                ctr += 1
                
            elif mtype == 'literal':
                if ctr >= split_len:
                    return False, False
                
                if split_cmd[ctr] != matcher['value']:
                    return False, False
                ctr += 1
                
            elif mtype == 'wildcard':
                ctr += 1
                
        if create_expr:
            self.execute_action(create_expr, split_cmd)
            return True, True
            
        return True, False 


    def validate_expression(self, expr: str, token: str, split_cmd: List[str]) -> bool:
        """
        Safely evaluates validation expressions.
        """
        expr = expr.replace('::SPACE::', ' ')
        
        # Simple non-empty check
        if expr == "'<<'!=''":
            return token != ''
        
        if expr == "'<<'==('all')":
             return token == 'all'
             
        if expr == "not(00)": 
            return True

        # Negation handling
        if expr.startswith('not(') and expr.endswith(')'):
            inner_expr = expr[4:-1]
            return not self.validate_expression(inner_expr, token, split_cmd)

        # Method calls on App or subsystems
        if expr.startswith("self.EntityManager.isEntity"):
             return self.app.EntityManager.isEntity(token) == 1
             
        if expr.startswith("self.is_alias"):
             return self.app.is_alias(token) == 1
        
        if expr.startswith("self.is_daemon"):
             return self.app.is_daemon(token) == 1
             
        if expr.startswith("self.isScript"):
             return self.app.isScript(token) == 1
             
        if expr.startswith("self.issubstitute"):
             return self.app.issubstitute(token) == 1
             
        return False

    def execute_action(self, action_expr: str, split_cmd: List[str]) -> None:
        """
        Safely executes the 'create:' action.
        """
        action_expr = action_expr.replace('::SPACE::', ' ')
        
        try:
             # 1. Sys exit
             if action_expr.startswith("sys.exit"):
                 sys.exit(0)
             
             # 2. Method call parsing
             # Pattern: self[.attr].method(args)
             
             match = re.match(r"self(\.([a-zA-Z0-9_]+))?\.([a-zA-Z0-9_]+)\((.*)\)", action_expr)
             if not match:
                 logging.error(f"Cannot parse action: {action_expr}")
                 return
                 
             attr = match.group(2) # e.g. EntityManager
             method_name = match.group(3) # e.g. define
             args_str = match.group(4) # arguments
             
             # Resolve target object
             target = self.app
             if attr:
                 target = getattr(self.app, attr, None)
                 
             if not target:
                 logging.error(f"Target object not found for {action_expr}")
                 return
                 
             method = getattr(target, method_name, None)
             if not method:
                 logging.error(f"Method {method_name} not found")
                 return
                 
             # Resolve arguments
             raw_args = self._split_args(args_str)
             resolved_args = []
             for raw_arg in raw_args:
                 if raw_arg: 
                    resolved_args.append(self._resolve_arg(raw_arg, split_cmd))
                 
             # Execute
             method(*resolved_args)
                 
        except Exception as e:
            logging.error(f"Error executing action {action_expr}: {e}")

    def _split_args(self, args_str: str) -> List[str]:
        if not args_str.strip():
            return []
        args = []
        current = ''
        depth = 0
        for char in args_str:
            if char == ',' and depth == 0:
                args.append(current.strip())
                current = ''
            else:
                if char == '(': depth += 1
                elif char == ')': depth -= 1
                current += char
        args.append(current.strip())
        return args

    def _resolve_arg(self, arg_str: str, split_cmd: List[str]) -> Any:
        arg_str = arg_str.strip()
        
        # Literal string
        if arg_str.startswith("'") and arg_str.endswith("'"):
            return arg_str[1:-1]
            
        # SplitCmd access
        match = re.match(r"SplitCmd\[(-?\d+)\]", arg_str)
        if match:
            idx = int(match.group(1))
            return split_cmd[idx] if -len(split_cmd) <= idx < len(split_cmd) else ""
            
        match = re.match(r"SplitCmd\[(-?\d+):\]", arg_str)
        if match:
             idx = int(match.group(1))
             return split_cmd[idx:]
        
        match = re.match(r"SplitCmd\[(-?\d+):(-?\d+)\]", arg_str)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            return split_cmd[start:end]

        match = re.match(r"int\((.*)\)", arg_str)
        if match:
            inner = match.group(1)
            val = self._resolve_arg(inner, split_cmd)
            try: return int(val)
            except: return 0

        match = re.match(r"['\"](.*)['\"]\.(join)\((.*)\)", arg_str)
        if match:
            sep = match.group(1)
            target = match.group(3)
            val = self._resolve_arg(target, split_cmd)
            if isinstance(val, list):
                return sep.join(val)
            return str(val)
            
        return arg_str
