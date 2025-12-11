
import unittest
from unittest.mock import MagicMock, call
import sys
import os
import tkinter as tk

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FC_formatter

class TestOutputFormatter(unittest.TestCase):
    def setUp(self):
        self.mock_notebook = MagicMock()
        self.mock_focus_return = MagicMock()
        self.mock_text_widget = MagicMock()
        
        # Configure mock text widget to behave like a dict for item access (config)
        self.mock_text_widget.__getitem__.return_value = 'normal'
        
        self.formatter = FC_formatter.OutputFormatter(self.mock_notebook, self.mock_focus_return)
        self.formatter.set_text_widget(self.mock_text_widget)

    def test_infodisplay_simple_string(self):
        msg = "Hello World"
        self.formatter.infodisplay(msg)
        
        # Verify notebook tab selection (default switchfocus=True)
        self.mock_notebook.select.assert_called_with(0)
        
        # Verify text insertion
        self.mock_text_widget.insert.assert_called_with(tk.END, "Hello World\n")
        self.mock_text_widget.see.assert_called_with(tk.END)
        
        # Verify focus return
        self.mock_focus_return.focus_set.assert_called()

    def test_infodisplay_list(self):
        msg = ["Line 1", "Line 2"]
        self.formatter.infodisplay(msg)
        
        calls = [
            call(tk.END, "Line 1\n"),
            call(tk.END, "Line 2\n")
        ]
        self.mock_text_widget.insert.assert_has_calls(calls, any_order=False)

    def test_formatting_headers(self):
        msg = ["F!HHeader", "F!hSubHeader"]
        self.formatter.infodisplay(msg)
        
        # F!H -> \n\n\t * Header\n\n\n
        expected_H = "\n\n\t * Header\n\n\n"
        # F!h -> \n * SubHeader\n\n
        expected_h = "\n * SubHeader\n\n"
        
        calls = [
            call(tk.END, expected_H),
            call(tk.END, expected_h)
        ]
        self.mock_text_widget.insert.assert_has_calls(calls)

    def test_disabled_widget_handling(self):
        # Simulate disabled widget
        self.mock_text_widget.__getitem__.side_effect = lambda key: 'disabled' if key == 'state' else None
        
        self.formatter.infodisplay("Test")
        
        # Verify it was enabled then disabled
        # Note: MagicMock calls are recorded. We check if configure was called with normal then disabled.
        
        calls = [
            call(state='normal'),
            call(state='disabled')
        ]
        self.mock_text_widget.configure.assert_has_calls(calls)

if __name__ == '__main__':
    unittest.main()
