# Evolve - Generate Agent Project Context

Generate project-specific context files for each agent based on discovery and planning outputs.

## Workflow Mode

```
WORKFLOW_MODE: evolve
```

---

## Instructions

You are now the **Evolver**. Your job is to:
1. Read the discovery and planning outputs
2. Generate tailored PROJECT.md files for each agent
3. Report what was generated

### Load Agent Role

Load your role from `.claude/agents/evolver/AGENT.md`

---

## Prerequisites

Before running, verify planning files exist:

```bash
ls discovery.md discovery-*.md 2>/dev/null
ls implementation-plan.md implementation-plan-*.md 2>/dev/null
```

If no discovery or plan files are found, inform the user:
```
The evolve step requires:
- At least one discovery file (run /auto-discovery first)
- At least one implementation plan file (run /auto-plan first)

Which step would you like to run?
```

---

## Execution

Follow the workflow in your AGENT.md:
1. Read ALL discovery files (`discovery.md`, `discovery-*.md`) and ALL plan files (`implementation-plan.md`, `implementation-plan-*.md`)
2. Check for design-system.md
3. Fully regenerate PROJECT.md for each agent folder (always a complete regeneration, not incremental)
4. Add a `## Recent Changes` section at top summarizing what changed since last generation
5. Generate PROJECT.md for each agent folder:
   - `.claude/agents/developer/PROJECT.md`
   - `.claude/agents/architect/PROJECT.md`
   - `.claude/agents/designer/PROJECT.md`
   - `.claude/agents/tester/PROJECT.md`
4. Report completion

---

## Output

Report to user:

```
**[Evolver]** Project context generated for all agents:

- .claude/agents/developer/PROJECT.md
- .claude/agents/architect/PROJECT.md
- .claude/agents/designer/PROJECT.md
- .claude/agents/tester/PROJECT.md

Agents will now have project-specific guidance when invoked.

Ready to start implementation with `/auto-work-all`.
```

---

## Your Request

$ARGUMENTS

---

Begin by loading the evolver agent role, then check for required input files.
