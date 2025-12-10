# Code Change Summary and Status

## Overall Status
The codebase is stable. Major bug fixes for the 'save all' functionality have been implemented, UI logic for entity deletion has been verified, and `ENTITYGROUP` support has been added to the UI.

- **Branch**: `ag_object_pane`
- **Test Status**: PASSED (All tests passing)

## Changes Since Last Commit

### Modified Files
-   `FC_daemoncollector.py`: Fixed `AttributeError: 'daemoncollector' object has no attribute 'outfile'` by correcting it to `data_filename` in the `tostring` method.
-   `FC_daemonmanager.py`: Fixed `AttributeError: 'daemontask' object has no attribute 'tentities'` by correcting the typo to `entities`.
-   `FC_entitymanager.py`: 
    -   Updated `delete` method to automatically close the corresponding notebook tab when an entity is deleted.
    -   Enabled `ENTITYGROUP` metadata in `get_entity_types_metadata`.
-   `FatController.py`:
    -   Updated `create_config_pane` to preserve whitespace-separated members list when loading `ENTITYGROUP` config.
    -   Updated `save_entity_changes` and `add_object_dialog` to split whitespace-separated members list into a list when saving/creating `ENTITYGROUP`.

### New Files
-   `tests/test_rhs_panel.py`: Added comprehensive unit tests for the Right-Hand Side (RHS) / Object Pane functionality.

### Deleted Files
-   `unixsetup.sh`: Removed legacy setup script.
-   `winsetup.bat`: Removed legacy setup script.

## Technical Notes
-   **SSH Testing**: The `FC_SSH` module now uses `fabric` and is tested with `unittest.mock`.
-   **Dependencies**: Added `fabric` to project dependencies.
-   **Bug Fix**: `FC_SSH.py` now includes:
    -   `StrictHostKeyChecking='no'` to prevent passing on new hosts.
    -   Removed `UserKnownHostsFile` override (was `/dev/null`) to fix Windows compatibility.
    -   `NumberOfPasswordPrompts='0'` to prevent UI hangs on authentication failure.
    -   Explicit `open()` call to catch authentication errors before command execution.
    -   Connection timeouts (10s).
    -   Retry logic to handle "No existing session" or transient connection drops.
    -   Fixed `getparameterstring` to prevent duplicate entity name in `save` files.
    -   Added detailed debug logging for diagnostics.
    -   Implemented lazy connection initialization (connect on demand) to avoid stale objects.
    -   Disabled GSSAPI and SSH Agent (`allow_agent=False`, `gss_auth=False`) for Windows stability.
    -   Removed GUI "LOGS" tab and `TextHandler` to prevent threading crashes; logs now go only to `logs.txt`.
