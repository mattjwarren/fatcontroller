# FatController GUI Acceptance Tests

## Purpose
This document provides a manual testing checklist for critical GUI workflows that cannot be automated in a headless environment. Run these tests before major releases or when significant GUI changes are made.

## Prerequisites
- FatController application running with GUI
- Test environment with access to sample entities/daemons
- At least one each of: Entity, Daemon, Alias, Script configured

---

## RHS Panel - Entity Management

### Entity List Display
- [ ] Launch FatController
- [ ] Verify RHS panel shows "Entities" dropdown selected
- [ ] Verify entity listbox populates with existing entities
- [ ] Verify entities are sorted alphabetically

### Entity Type Filtering
- [ ] Ensure at least 2 different entity types exist (e.g., SSH and TSM)
- [ ] Select "Entities" from Object Type dropdown
- [ ] Verify "Type:" sub-dropdown appears
- [ ] Select a specific entity type (e.g., "SSH")
- [ ] Verify listbox shows only entities of that type
- [ ] Change to different entity type
- [ ] Verify listbox updates to show only new type

### Entity Selection and Config Display
- [ ] Select an entity from the listbox
- [ ] Verify config panel shows entity details in a tab
- [ ] Verify tab name matches entity name
- [ ] Verify all entity parameters are displayed
- [ ] Select multiple entities (Ctrl+Click)
- [ ] Verify multiple tabs appear, one for each selection

### Create New Entity
- [ ] Deselect all entities (click in empty space)
- [ ] Verify "New Entity" tab appears in config panel
- [ ] Select entity type from dropdown
- [ ] Verify parameter fields appear for selected type
- [ ] Fill in all required fields (Name + type-specific params)
- [ ] Click "+" (Add) button
- [ ] Verify success message appears
- [ ] Verify new entity appears in listbox
- [ ] Verify new entity is sorted correctly in list

### Delete Entity
- [ ] Select entity from listbox
- [ ] Click "-" (Remove) button
- [ ] Verify confirmation dialog appears
- [ ] Click "Yes" on confirmation
- [ ] Verify entity disappears from listbox
- [ ] Verify entity tab closes

---

## RHS Panel - Daemon Management

### Daemon List Display
- [ ] Select "Daemons" from Object Type dropdown
- [ ] Verify listbox populates with existing daemons
- [ ] Verify daemons are sorted alphabetically
- [ ] Verify no entity type filter appears (specific to entities)

### Create New Daemon
- [ ] Ensure no daemon selected
- [ ] Verify "New Daemon" tab appears
- [ ] Enter daemon name
- [ ] Click "+" button
- [ ] Verify success message
- [ ] Verify daemon appears in listbox

### Daemon Schedule Configuration
- [ ] Select existing daemon
- [ ] Verify daemon config tab shows schedule fields (Start, Period)
- [ ] Modify Start time
- [ ] Modify Period value
- [ ] Click "+" button to save changes
- [ ] Verify success message
- [ ] Re-select daemon to verify changes persisted

### Delete Daemon
- [ ] Select daemon from listbox
- [ ] Click "-" button
- [ ] Verify confirmation dialog
- [ ] Confirm deletion
- [ ] Verify daemon removed from list

---

## RHS Panel - Alias Management

### Alias Display and Creation
- [ ] Select "Aliases" from Object Type dropdown
- [ ] Verify existing aliases appear in listbox
- [ ] Deselect all to show "New Alias" tab
- [ ] Enter alias name and content
- [ ] Click "+" to create
- [ ] Verify alias appears in list

### Edit Alias
- [ ] Select existing alias
- [ ] Verify "Alias Content" field shows current value
- [ ] Modify content
- [ ] Click "+" to save
- [ ] Verify success message

### Delete Alias
- [ ] Select alias
- [ ] Click "-" button
- [ ] Confirm deletion
- [ ] Verify alias removed

---

## RHS Panel - Script Management

### Script Display  
- [ ] Select "Scripts" from Object Type dropdown
- [ ] Verify existing scripts appear in listbox
- [ ] Select a script
- [ ] Verify script content displays (if implemented)

### Delete Script
- [ ] Select script
- [ ] Click "-" button
- [ ] Confirm deletion
- [ ] Verify script removed

---

## RHS Panel - Substitution Management

### Substitution Display and Management
- [ ] Select "Substitutions" from Object Type dropdown
- [ ] Verify existing substitutions appear
- [ ] Create new substitution with name and value
- [ ] Verify creation succeeds
- [ ] Edit existing substitution
- [ ] Delete substitution

---

## Multi-Select Operations

### Delete Multiple Items
- [ ] Select "Entities" (or any object type)
- [ ] Select multiple items (Ctrl+Click or Shift+Click)
- [ ] Verify multiple config tabs appear
- [ ] Click "-" button
- [ ] Verify confirmation shows count (e.g., "Delete 3 Entities?")
- [ ] Confirm
- [ ] Verify all selected items removed

---

## Error Handling

### Invalid Entity Creation
- [ ] Attempt to create entity with empty name
- [ ] Verify error message appears
- [ ] Attempt to create entity with missing required parameters
- [ ] Verify appropriate error handling

### Delete Non-Existent Item (Edge Case)
- [ ] Verify graceful handling if item deleted elsewhere
- [ ] Refresh list and verify consistency

---

## Integration with Main Shell

### Entity Creation Reflects in Shell
- [ ] Create new entity via RHS panel
- [ ] Execute the entity from shell: `execute <entity_name>`
- [ ] Verify execution works correctly
- [ ] Check entity appears in shell completions/suggestions (if applicable)

### Entity Deletion Reflects in Shell
- [ ] Delete entity via RHS panel
- [ ] Attempt to execute deleted entity from shell
- [ ] Verify appropriate "entity not found" error

---

## Notes
- Mark each item as ✅ pass or ❌ fail
- Document any failures with steps to reproduce
- Test after significant refactoring or before releases
- Consider automating parts of this with GUI testing frameworks if growing complex
