---
name: github-issues
description: Best practices for breaking down work into GitHub issues, proper sizing, and milestone organization. Use during discovery/planning phases.
---

# GitHub Issue Creation Skill

Guidelines for creating well-structured GitHub issues that enable efficient autonomous development.

## Core Principles

1. **One PR Per Issue** - Each issue completable in a single pull request
2. **Vertical Slices** - Prefer end-to-end functionality over horizontal layers
3. **Testable Criteria** - Every issue must have objectively verifiable acceptance criteria

## Issue Sizing

### Right-Sized
- Completable in 1-4 hours
- Single, clear objective
- 3-7 acceptance criteria

### Too Large (Split It)
- More than 7 acceptance criteria
- Touches more than 3-4 files significantly
- Requires "and" to describe
- Split by: user action, data entity, happy path vs error handling

### Too Small (Combine It)
- Less than 15 minutes of work
- No meaningful acceptance criteria

## Issue Template

```markdown
**[Product Owner]**

## User Story
As a [user type],
I want [action],
So that [benefit].

## Acceptance Criteria
- [ ] Primary happy path works
- [ ] Key error case handled
- [ ] Edge case covered

## Dependencies
Depends on #X (reason)
-- OR --
None - can be worked independently

## Out of Scope
- Explicitly list what this does NOT cover
```

### Do NOT Include
- Implementation details (let Developer decide)
- Specific file names or code structure
- Time estimates

## Dependency Management

```markdown
## Dependencies
Depends on #12 (database schema must exist)
Depends on #15 (auth middleware required)
```

An issue is "ready" when all dependencies are closed.

## Milestone Organization

- **3-10 issues per milestone** - Small enough to feel achievable
- **Ordered by value** - Earlier milestones = higher value/lower risk
- **Clear definition of done** - What can users do when complete?

### Creating Milestones

```bash
gh api repos/{owner}/{repo}/milestones \
  -f title="v1.0 - Basic Cart" \
  -f description="Users can add items to cart and modify quantities"

gh issue edit {number} --milestone "v1.0 - Basic Cart"
```

## Issue Commands

### Sandbox Compatibility (Important)

**Don't use heredocs (`<<EOF`) with `gh` commands** - they fail in sandboxed environments because the shell can't create temp files for the heredoc content.

Instead, use the Write tool + `--body-file` pattern:

```bash
# 1. Use Write tool to create .github-issue-body.md with the issue body
# 2. Create the issue with --body-file
gh issue create --title "..." --body-file .github-issue-body.md
# 3. Clean up
rm .github-issue-body.md
```

### Before Creating an Issue

**Always check for duplicates first:**

```bash
# Search for existing issues with similar keywords
gh issue list --state all --search "keyword1 keyword2"

# Check open issues
gh issue list --state open --json number,title,body | jq '.[] | "\(.number): \(.title)"'
```

If a similar issue exists:
- Reference it instead of creating a duplicate
- Add a comment to the existing issue if you have new context
- Consider if the scope should be expanded vs. new issue

### Creating Issues

**Don't prefix titles with type** (e.g., "Feature:", "Bug:") - labels handle that and are more functional for filtering.

```bash
# Feature issue
gh issue create \
  --title "{Concise description of capability}" \
  --label "feature" --label "ready" \
  --milestone "v1.0" \
  --body "..."

# Bug issue
gh issue create \
  --title "{What's broken}" \
  --label "bug" --label "ready" \
  --body "..."

# Assign labels
gh issue edit {number} --add-label "priority:high"
```

## Breaking Down Features

1. **Identify core user journey** - What's the minimum path?
2. **Extract foundation work** - Database, APIs, shared utilities
3. **Split by user action** - Each action = potential issue
4. **Map dependencies** - What must come first?
5. **Group into milestones** - What's usable together?

## Common Anti-Patterns

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| "User experience is good" | "Form shows validation errors within 100ms" |
| Missing error cases | Include error handling in acceptance criteria |
| Hidden dependencies | Always note "Depends on #X" |
| Too much detail | Define what, not how |
