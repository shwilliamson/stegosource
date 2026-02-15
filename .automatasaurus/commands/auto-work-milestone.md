# Work Milestone - Process All Issues in a Milestone

Process all open issues in a specific GitHub milestone using context-isolated subagents.

## Usage

```
/auto-work-milestone {milestone_number}
```

## Workflow Mode

```
WORKFLOW_MODE: milestone
AUTO_MERGE: true (handled by this orchestrator after /auto-work-issue completes)
```

---

## Instructions

You are the **Milestone Implementation Orchestrator**. You:
1. Validate the milestone exists and get its details
2. List all open issues in the milestone
3. Select issues based on dependencies and priority
4. Spawn `/auto-work-issue {n}` as a subagent for each issue (context isolation)
5. Parse subagent output to determine result
6. Merge successful PRs
7. Enforce circuit breaker limits
8. Report milestone-specific progress

---

## Load Context

1. Load the `workflow-orchestration` skill
2. Load the `github-workflow` skill
3. Check for `implementation-plan.md` (if exists, filter to milestone issues and follow order)
4. Read circuit breaker limits from `.claude/settings.json` under `automatasaurus.limits`

---

## Validate Milestone

Before starting, validate the milestone exists:

```bash
# Get milestone info
gh api repos/:owner/:repo/milestones/$ARGUMENTS --jq '{title: .title, open_issues: .open_issues, description: .description}'
```

If milestone doesn't exist or has no open issues, report and exit:
- Invalid milestone number → Error: "Milestone #X not found"
- No open issues → Success: "Milestone #X ({title}) has no open issues"

Store milestone info:
```
MILESTONE_NUMBER = $ARGUMENTS
MILESTONE_TITLE = [from API response]
MILESTONE_TOTAL = [open_issues from API response]
```

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
successCount = 0
blockedCount = 0
```

---

## Main Loop

```
LOOP:
  1. CHECK LIMITS
     - If issuesProcessed >= maxIssuesPerRun → Stop (limit reached)
     - If escalationCount >= maxEscalationsBeforeStop → Stop (escalation limit)
     - If consecutiveFailures >= maxConsecutiveFailures → Stop (failure limit)

  2. LIST MILESTONE ISSUES
     - Use: gh issue list --state open --milestone $ARGUMENTS --json number,title,labels
     - If no open issues remain → Notify milestone complete, exit

  3. SELECT NEXT ISSUE
     - If implementation-plan.md exists: filter to milestone issues, follow plan order
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
     - SUCCESS: Merge PR, reset consecutiveFailures, increment issuesProcessed, successCount
     - BLOCKED: Increment blockedCount, skip issue, continue to next
     - ESCALATED: Increment escalationCount, consecutiveFailures

  7. REPORT PROGRESS
     - Show milestone-specific stats
     - Loop back to step 1

END LOOP
```

---

## Issue Selection Criteria

### Primary: Follow Implementation Plan

If `implementation-plan.md` exists:
1. Read the plan
2. Filter entries to only issues in this milestone (cross-reference with milestone issue list)
3. Process in plan order

### Fallback: Priority-Based Selection

If no plan exists, select issues by:

#### 1. Dependencies
- Issues with no open dependencies first
- Issues that unblock others prioritized

#### 2. Priority Labels
- `priority:high` → `priority:medium` → `priority:low`

#### 3. Logical Order
- Foundation (schemas, models) before features
- Backend before frontend if applicable

---

## Listing Milestone Issues

```bash
# List all open issues in the milestone
gh issue list --state open --milestone $ARGUMENTS --json number,title,labels,body

# Check for dependencies in issue body (looks for "depends on #X" or "blocked by #X")
# Parse each issue to build dependency graph
```

---

## Spawning Work Subagent

For each selected issue, spawn a subagent that loads and follows the `work-issue` skill.

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

Milestone #{MILESTONE_NUMBER}: {MILESTONE_TITLE}
Issue {issuesProcessed + 1} of {MILESTONE_TOTAL} in milestone"

# Merge
gh pr merge {PR_NUMBER} --squash --delete-branch

# Verify issue closed
gh issue view {issue_number} --json state --jq '.state'
```

---

## Progress Reporting

After each issue:

```
## Milestone #{MILESTONE_NUMBER}: {MILESTONE_TITLE}

Issue #{number}: [SUCCESS/BLOCKED/ESCALATED]
Progress: {successCount}/{MILESTONE_TOTAL} issues in milestone complete
Issues processed this run: {issuesProcessed}/{maxIssuesPerRun}
Escalations: {escalationCount}/{maxEscalationsBeforeStop}
```

---

## Stopping Conditions

Stop the loop when ANY of these occur:

1. **Milestone complete** → All issues in milestone processed successfully
2. **Limit reached** (`maxIssuesPerRun`) → Report progress, suggest continuing later
3. **Escalation limit** (`maxEscalationsBeforeStop`) → Notify human intervention needed
4. **Failure limit** (`maxConsecutiveFailures`) → Notify something is wrong
5. **All remaining issues blocked** → Notify circular dependency or external blocker

---

## Completion Notifications

**Milestone complete:**
```bash
.claude/hooks/request-attention.sh complete "Milestone #{MILESTONE_NUMBER} ({MILESTONE_TITLE}) complete! All {MILESTONE_TOTAL} issues merged."
```

**Limit reached:**
```bash
.claude/hooks/request-attention.sh info "Processed {n} issues in milestone #{MILESTONE_NUMBER}. Run /auto-work-milestone {MILESTONE_NUMBER} again to continue."
```

**Escalation/Failure limit:**
```bash
.claude/hooks/request-attention.sh stuck "Stopped after {n} escalations in milestone #{MILESTONE_NUMBER}. Human intervention needed."
```

---

## Final Summary

When stopping for any reason:

```
## Work-Milestone Summary

**Milestone:** #{MILESTONE_NUMBER} - {MILESTONE_TITLE}
**Status:** [Complete / Limit Reached / Stopped - Human Needed]

**Milestone Progress:** {successCount}/{MILESTONE_TOTAL} issues complete
**Issues Processed This Run:** {issuesProcessed}
**Successful Merges:** {successCount}
**Blocked:** {blockedCount}
**Escalated:** {escalatedCount}

**Remaining in Milestone:** {remaining_count}

[If applicable: Suggest next steps]
```

---

Begin by validating the milestone number from `$ARGUMENTS`, loading skills, reading limits from settings, then listing all open issues in the milestone.
