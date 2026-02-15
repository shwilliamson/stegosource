---
name: github-workflow
description: Manages GitHub workflow including issues, PRs, labels, and reviews. Use when working with GitHub issues, creating PRs, or coordinating reviews.
---

# GitHub Workflow Skill

Guidance for managing the development workflow through GitHub.

## Issue State Labels

| Label | Description | When to Apply |
|-------|-------------|---------------|
| `ready` | No blocking dependencies | Issue can be picked up |
| `in-progress` | Currently being implemented | Developer starts work |
| `blocked` | Waiting on dependencies | Has unresolved blockers |
| `needs-review` | PR open, awaiting reviews | PR created |

```bash
gh issue edit {n} --add-label "in-progress" --remove-label "ready"
gh issue edit {n} --add-label "needs-review" --remove-label "in-progress"
```

## Dependency Tracking

In issue body:
```markdown
## Dependencies
Depends on #12 (User authentication)
Depends on #15 (Database schema)
```

Parse dependencies:
```bash
gh issue view {n} --json body --jq '.body' | grep -oE "Depends on #[0-9]+" | grep -oE "[0-9]+"
gh issue view {dep} --json state --jq '.state'
```

## Agent Identification

**All GitHub interactions must include an agent identifier header.**

Format: `**[Agent Name]**` at the start of every issue body, PR description, and comment.

## Standardized Review Comments

Since all agents share the same GitHub user, reviews use standardized comments:

**Approval:**
```
✅ APPROVED - [Role]
[Summary]
```

**Changes Requested:**
```
❌ CHANGES REQUESTED - [Role]
[Issues to address]
```

## Required Reviews Per PR

| Review | When Required |
|--------|---------------|
| Architect | Always |
| Designer | If UI changes |
| Tester | Always |

## Review Templates

### Architect
```bash
gh pr comment {n} --body "**[Architect]**

✅ APPROVED - Architect

Clean architecture. LGTM."
```

### Designer
```bash
gh pr comment {n} --body "**[Designer]**

✅ APPROVED - Designer

UI looks good. Accessibility met."

# Or if not applicable:
gh pr comment {n} --body "**[Designer]** N/A - No UI changes."
```

### Tester
```bash
gh pr comment {n} --body "**[Tester]**

✅ APPROVED - Tester

**Tests:** All passing
**Manual:** Completed

Ready for merge."
```

### Product Owner (Merge)
```bash
gh pr comment {n} --body "**[Product Owner]**

All required reviews complete:
- ✅ Architect
- ✅ Tester

Proceeding with merge."

gh pr merge {n} --squash --delete-branch
```

## PR Approval Verification

Before merge:
1. `✅ APPROVED - Architect` present
2. `✅ APPROVED - Tester` present
3. `✅ APPROVED - Designer` present (if UI)
4. No outstanding `❌ CHANGES REQUESTED`
5. CI/tests passing

```bash
gh pr view {n} --comments  # Check for approval comments
```

## Labels

### Priority
| Label | Description |
|-------|-------------|
| `priority:high` | Work first |
| `priority:medium` | Normal |
| `priority:low` | Work last |

### Type
| Label | Description |
|-------|-------------|
| `feature` | New functionality |
| `bug` | Bug fix |
| `enhancement` | Improvement |

## Common Commands

```bash
# Issues
gh issue list --state open --label "ready"
gh issue view {n}
gh issue edit {n} --add-label "in-progress"

# PRs
gh pr create --title "..." --body "..."
gh pr view {n} --comments
gh pr merge {n} --squash --delete-branch

# Milestones
gh issue edit {n} --milestone "v1.0"
```
