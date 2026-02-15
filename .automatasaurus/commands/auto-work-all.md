# Work All - Process All Open Issues

Autonomously work through all open GitHub issues using context-isolated subagents.

## Workflow Mode

```
WORKFLOW_MODE: all-issues
AUTO_MERGE: true (handled by this orchestrator (aka Product Owner) after /auto-work-issue completes)
```

---

## Instructions

You are the **Autonomous Implementation Orchestrator**. You:
1. Select issues based on dependencies and priority
2. Spawn `/auto-work-issue {n}` as a subagent for each issue (context isolation)
3. Parse subagent output to determine result
4. Merge successful PRs
5. Enforce circuit breaker limits

---

## Load Context

1. Load the `workflow-orchestration` skill
2. Load the `github-workflow` skill
2b. If agent teams are enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings), also load the `team-coordination` skill
3. Check for implementation plan files (`implementation-plan*.md`). If multiple exist, use the **highest-numbered** one (e.g., `implementation-plan-3.md` over `implementation-plan.md`)
4. Read circuit breaker limits from `.claude/settings.json` under `automatasaurus.limits`

---

## Circuit Breaker Limits

Before each iteration, check limits from settings:

| Limit | Default | Action When Exceeded |
|-------|---------|---------------------|
| `maxIssuesPerRun` | 20 | Stop, report progress |
| `maxEscalationsBeforeStop` | 3 | Stop, notify human |
| `maxConsecutiveFailures` | 3 | Stop, notify human |

Initialize counters:
```
issuesProcessed = 0
escalationCount = 0
consecutiveFailures = 0
```

---

## Main Loop

```
LOOP:
  1. CHECK LIMITS
     - If issuesProcessed >= maxIssuesPerRun → Stop (limit reached)
     - If escalationCount >= maxEscalationsBeforeStop → Stop (escalation limit)
     - If consecutiveFailures >= maxConsecutiveFailures → Stop (failure limit)

  2. LIST OPEN ISSUES
     - Check milestones and priorities
     - If no open issues → Notify complete, exit

  3. SELECT NEXT ISSUE
     - Follow latest implementation-plan file if exists
     - Otherwise use selection criteria (see below)
     - Check dependencies (skip if blocked)

  4. SPAWN /auto-work-issue SUBAGENT
     - Use Task tool to spawn: "Run /auto-work-issue {issue_number}"
     - Wait for completion
     - Parse output for result

  5. PARSE RESULT
     - SUCCESS: Output contains "PR #X is ready" or "All required reviews complete"
     - BLOCKED: Output contains "blocked" or "dependency"
     - ESCALATED: Output contains "Escalating" or "stuck"

  6. HANDLE RESULT
     - SUCCESS: Merge PR, reset consecutiveFailures, increment issuesProcessed
     - BLOCKED: Skip issue, continue to next
     - ESCALATED: Increment escalationCount, consecutiveFailures

  7. CONTINUE
     - Report progress
     - Loop back to step 1

END LOOP
```

---

## Issue Selection Criteria

If no implementation plan files exist, select issues by:

### 1. Milestone First
- Complete current milestone before next
- Milestones in order (v1.0 before v1.1)

### 2. Dependencies
- Issues with no open dependencies first
- Issues that unblock others prioritized

### 3. Priority Labels
- `priority:high` → `priority:medium` → `priority:low`

### 4. Logical Order
- Foundation (schemas, models) before features
- Backend before frontend if applicable

---

## Spawning Work Subagent

For each selected issue, spawn a subagent that loads and follows the `work-issue` skill.

This ensures the subagent executes the **exact same logic** as the `/auto-work-issue` command.

### Task Tool Parameters

```
subagent_type: "general-purpose"
description: "Work on issue #{issue_number}"
prompt: |
  Work on GitHub issue #{issue_number}.

  1. Load the `work-issue` skill from .claude/skills/work-issue/SKILL.md
  2. Follow the skill workflow with ISSUE_NUMBER = {issue_number}
  3. Execute all steps: dependencies, implementation, reviews
  4. Report result using the skill's exit state format:
     - SUCCESS: "PR #X is ready for merge"
     - BLOCKED: "Issue #{issue_number} is blocked on #Y"
     - ESCALATED: "Issue #{issue_number} requires human intervention"
```

### Example Invocation

```
Use the Task tool with subagent_type "general-purpose" to work on issue #42:

"Work on GitHub issue #42.

Load the work-issue skill from .claude/skills/work-issue/SKILL.md and follow
the workflow with ISSUE_NUMBER = 42.

Execute all steps: check dependencies, get design specs if UI, implement via
developer agent, coordinate reviews (Architect, Tester, Designer if UI), handle
any change requests.

Report result clearly:
- SUCCESS: 'PR #X is ready for merge'
- BLOCKED: 'Issue #42 is blocked on #Y'
- ESCALATED: 'Issue #42 requires human intervention'"
```

The subagent loads the same skill that `/auto-work-issue` uses, ensuring identical behavior with isolated context.

---

## Result Parsing

After subagent completes, check output for:

**SUCCESS indicators:**
- "PR #X is ready"
- "All required reviews complete"
- "ready for merge"

**BLOCKED indicators:**
- "blocked"
- "dependency"
- "cannot proceed"

**ESCALATED indicators:**
- "Escalating"
- "stuck"
- "requires human"
- "unable to resolve"

---

## Merge on Success

When result is SUCCESS:

```bash
# Get PR number from subagent output
PR_NUMBER=[parsed from output]

# Post verification
gh pr comment {PR_NUMBER} --body "**[Product Owner]**

All required reviews complete. Proceeding with merge.

Issue processed: {issuesProcessed + 1} of max {maxIssuesPerRun}"

# Merge
gh pr merge {PR_NUMBER} --squash --delete-branch

# Verify issue closed
gh issue view {issue_number} --json state --jq '.state'
```

---

## Progress Reporting

After each issue:

```
Issue #{number}: [SUCCESS/BLOCKED/ESCALATED]
Progress: {issuesProcessed}/{maxIssuesPerRun} issues
Escalations: {escalationCount}/{maxEscalationsBeforeStop}
Current milestone: [name] - [x/y] complete
```

---

## Stopping Conditions

Stop the loop when ANY of these occur:

1. **All issues complete** → Notify success
2. **Limit reached** (`maxIssuesPerRun`) → Report progress, suggest continuing later
3. **Escalation limit** (`maxEscalationsBeforeStop`) → Notify human intervention needed
4. **Failure limit** (`maxConsecutiveFailures`) → Notify something is wrong
5. **All remaining issues blocked** → Notify circular dependency or external blocker

---

## Completion Notifications

**All complete:**
```bash
.claude/hooks/request-attention.sh complete "All issues implemented and merged!"
```

**Limit reached:**
```bash
.claude/hooks/request-attention.sh info "Processed {n} issues. Run /auto-work-all again to continue."
```

**Escalation/Failure limit:**
```bash
.claude/hooks/request-attention.sh stuck "Stopped after {n} escalations. Human intervention needed."
```

---

## Final Summary

When stopping for any reason:

```
## Work-All Summary

**Status:** [Complete / Limit Reached / Stopped - Human Needed]

**Issues Processed:** {issuesProcessed}
**Successful Merges:** {successCount}
**Blocked:** {blockedCount}
**Escalated:** {escalatedCount}

**Remaining Open Issues:** {count}

[If applicable: Suggest next steps]
```

---

Begin by loading skills, reading limits from settings, then listing all open issues.
