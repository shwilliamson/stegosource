# Work - Process a Specific Issue

Work on a specific GitHub issue by number.

## Workflow Mode

```
WORKFLOW_MODE: single-issue
AUTO_MERGE: false
```

**IMPORTANT:** In single-issue mode, do NOT auto-merge. Notify the user when the PR is ready for their review and merge.

---

## Instructions

Load and follow the `work-issue` skill with ISSUE_NUMBER = $ARGUMENTS.

### 1. Load the Skill

Load the `work-issue` skill which contains the full implementation workflow.

If agent teams are enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings), also load the `team-coordination` skill for team patterns.

### 2. Execute the Workflow

Follow the work-issue skill steps:
1. Get issue details for issue #$ARGUMENTS
2. Check dependencies
3. Get design specs if UI work
4. Implement via developer agent
5. Coordinate reviews (Architect, Designer if UI, Tester)
6. Handle any change requests

### 3. Report Result (Do NOT Merge)

When the skill workflow completes with SUCCESS:

```bash
gh pr comment {pr_number} --body "**[Product Owner]**

All required reviews complete:
- ✅ Architect
- ✅ Tester
[- ✅ Designer (if applicable)]

PR is ready for merge. Awaiting user action."
```

**Report to user:**

```
PR #{pr_number} is ready for your review and merge.

All approvals received:
- ✅ Architect
- ✅ Tester

Link: {pr_url}

When you're ready, merge the PR to complete issue #$ARGUMENTS.
```

**STOP HERE** - Do NOT merge in single-issue mode. The user will merge manually.

---

## Issue Number

$ARGUMENTS

---

Begin by loading the work-issue skill, then start with Step 1: Get Issue Details.
