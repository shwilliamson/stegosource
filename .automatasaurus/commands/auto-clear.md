# Clear - Remove Generated Planning Files

Remove all generated planning and context files to start fresh.

## Workflow Mode

```
WORKFLOW_MODE: clear
```

---

## Instructions

You are the **Cleanup Assistant**. Your job is to:
1. Find all generated planning files
2. Show the user what will be removed
3. Offer backup or direct deletion
4. Clean up and confirm

---

## Phase 1: Find Generated Files

Glob for all generated planning and context files:

```bash
# Discovery files
ls discovery.md discovery-*.md 2>/dev/null

# Implementation plan files
ls implementation-plan.md implementation-plan-*.md 2>/dev/null

# Design system
ls design-system.md 2>/dev/null

# Agent PROJECT.md files
ls .claude/agents/*/PROJECT.md 2>/dev/null
```

If no files are found, inform the user:
```
No generated planning files found. Nothing to clear.
```

---

## Phase 2: Present Files to User

List all found files with sizes:

```
## Generated Planning Files Found

| File | Size |
|------|------|
| discovery.md | X KB |
| discovery-2.md | X KB |
| implementation-plan.md | X KB |
| design-system.md | X KB |
| .claude/agents/developer/PROJECT.md | X KB |
| .claude/agents/architect/PROJECT.md | X KB |
| .claude/agents/designer/PROJECT.md | X KB |
| .claude/agents/tester/PROJECT.md | X KB |

What would you like to do?
1. **Delete all** - Remove all generated files
2. **Backup then delete** - Copy to `.automatasaurus/backups/` first, then remove
3. **Cancel** - Keep everything
```

---

## Phase 3: Execute Chosen Action

### Option 1: Delete All

```bash
rm -f discovery.md discovery-*.md
rm -f implementation-plan.md implementation-plan-*.md
rm -f design-system.md
rm -f .claude/agents/*/PROJECT.md
```

### Option 2: Backup Then Delete

```bash
# Create timestamped backup directory
BACKUP_DIR=".automatasaurus/backups/planning-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Copy all generated files preserving structure
cp discovery.md discovery-*.md "$BACKUP_DIR/" 2>/dev/null
cp implementation-plan.md implementation-plan-*.md "$BACKUP_DIR/" 2>/dev/null
cp design-system.md "$BACKUP_DIR/" 2>/dev/null
mkdir -p "$BACKUP_DIR/agents"
for agent_dir in .claude/agents/*/; do
  agent_name=$(basename "$agent_dir")
  if [ -f "$agent_dir/PROJECT.md" ]; then
    mkdir -p "$BACKUP_DIR/agents/$agent_name"
    cp "$agent_dir/PROJECT.md" "$BACKUP_DIR/agents/$agent_name/"
  fi
done

# Then delete
rm -f discovery.md discovery-*.md
rm -f implementation-plan.md implementation-plan-*.md
rm -f design-system.md
rm -f .claude/agents/*/PROJECT.md
```

### Option 3: Cancel

Do nothing.

---

## Phase 4: Verify and Report

After deletion, verify clean state:

```bash
ls discovery.md discovery-*.md implementation-plan.md implementation-plan-*.md design-system.md .claude/agents/*/PROJECT.md 2>/dev/null
```

Report to user:

```
All generated planning files have been removed.

To start a fresh planning cycle, run:

/auto-discovery
```

If backup was chosen, also report:
```
Backup saved to: .automatasaurus/backups/planning-{timestamp}/
```

---

## Your Request

$ARGUMENTS

---

Begin by searching for generated planning files.
