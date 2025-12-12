
import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import importlib

# Ensure local modules can be found
sys.path.append(os.getcwd())

import FatController

@pytest.fixture
def clean_imports():
    # Force reload of FatController to pick up mocked modules from conftest
    importlib.reload(FatController)
    yield
    importlib.reload(FatController)

