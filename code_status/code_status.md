# Code Change Summary and Status

## Overall Status
The codebase is currently in a stable state. All unit tests, including new tests for the Object Pane and SSH entity, are passing.

- **Branch**: `ag_object_pane`
- **Test Status**: PASSED (All tests passing)

## Changes Since Last Commit

### Modified Files
-   `tests/conftest.py`: Updates to test configuration.
-   `tests/test_fc_ssh.py`: Fixed mocking strategy for `paramiko` to ensure tests run correctly in environments where `paramiko` mock patching was previously ineffective. Switched from `patch('FC_SSH.paramiko')` to `patch.object(FC_SSH, 'paramiko')`.

### New Files
-   `tests/test_rhs_panel.py`: Added comprehensive unit tests for the Right-Hand Side (RHS) / Object Pane functionality, covering:
    -   Refreshing object lists (Entities, Daemons).
    -   Object type filtering.
    -   Creating new entities.
    -   Removing objects.

### Deleted Files
-   `unixsetup.sh`: Removed legacy setup script.
-   `winsetup.bat`: Removed legacy setup script.

## Technical Notes
-   **SSH Testing**: The `FC_SSH` module's dependency on `paramiko` is now safely mocked in tests using `patch.object`, preventing test failures due to timeouts or environment mismatches.
