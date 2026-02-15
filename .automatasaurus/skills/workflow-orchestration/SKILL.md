---
name: workflow-orchestration
description: Defines the autonomous development workflow. Use when orchestrating work between agents, managing issue lifecycles, or understanding the development loop.
---

# Workflow Orchestration

This skill defines how the Automatasaurus workflow operates.

## Architecture Overview

### Slash Commands (Orchestration)

Commands run in the main conversation and orchestrate agents:

| Command | Purpose | Produces |
|---------|---------|----------|
| `/auto-discovery` | Requirements gathering | `discovery.md` (or `discovery-{N}.md` on re-runs), issues |
| `/auto-plan` | Implementation planning | `implementation-plan.md` (or `implementation-plan-{N}.md` on re-runs) |
| `/auto-evolve` | Generate agent context | `PROJECT.md` files (fully regenerated each run) |
| `/auto-clear` | Remove all generated planning files | Clean slate |
| `/auto-work-issue {n}` | Single issue | PR (user merges) |
| `/auto-work-all` | All issues | PRs merged, issues closed |

### Agents (Autonomous Workers)

Agents perform discrete tasks without user dialogue:

| Agent | Tasks |
|-------|-------|
| `developer` | Implements issues, creates PRs |
| `architect` | Reviews discovery plans, reviews PRs, helps stuck developers |
| `designer` | Reviews discovery plans, reviews PRs, adds design specs |
| `tester` | Runs tests, manual verification with Playwright |

---

## Workflow Modes

The system operates in different modes:

| Mode | Command | Merge Behavior |
|------|---------|----------------|
| `discovery` | `/auto-discovery` | N/A - creates issues |
| `planning` | `/auto-plan` | N/A - creates plan |
| `single-issue` | `/auto-work-issue {n}` | **Notify only** - user merges |
| `all-issues` | `/auto-work-all` | **Auto-merge** and continue |

### Mode Context Passing

When delegating to agents, include mode context:

```
# Single-issue mode
"This is SINGLE-ISSUE mode. Do NOT auto-merge. Notify when PR is approved."

# All-issues mode
"This is ALL-ISSUES mode. Auto-merge after approvals and continue to next issue."
```

**Default:** If mode unclear, default to single-issue (safer).

---

## Coordination Modes

The orchestrator can use two modes for delegating work to agents:

| Mode | Mechanism | Communication | Best For |
|------|-----------|---------------|----------|
| **Subagents** (default) | Task tool spawns agent | Report to orchestrator only via briefing/report files | Independent tasks, linear workflows |
| **Agent Teams** (experimental) | Team of concurrent sessions | Peer-to-peer messaging + shared task list | Multi-role reviews, real-time collaboration |

### Decision Criteria

| Workflow Step | Default | Team Alternative | When to Use Team |
|--------------|---------|-----------------|-----------------|
| Design specs | Subagent | N/A | Always subagent |
| Implementation | Subagent | Developer + Designer team | UI work needing real-time designer feedback |
| Reviews | Subagent (parallel) | Review team | Cross-pollination of findings adds value |
| Feedback fixes | Subagent | N/A | Always subagent |

Settings control defaults:
- `teamPreferForReviews: true` — default to review teams
- `teamPreferForImplementation: false` — default to solo developer subagent
- `teamMaxTeammates: 4` — cap concurrent team members

Teams are experimental. Always fall back to subagents if team creation fails.

---

## Two-Phase Workflow

### Phase 1: Discovery (Interactive)

```
User: /auto-discovery "feature description"
           ↓
    Main conversation facilitates requirements gathering
    (loads requirements-gathering, user-stories skills)
           ↓
    Produces discovery.md (or discovery-{N}.md on re-runs)
           ↓
    Spawns Architect → reviews technical feasibility
    Spawns Designer → reviews UI/UX considerations
           ↓
    User approves → Creates milestones and issues
```

### Phase 2: Implementation (Autonomous)

```
User: /auto-plan (optional)
           ↓
    Analyzes issues, creates implementation-plan.md (or implementation-plan-{N}.md on re-runs)
           ↓
User: /auto-work-all
           ↓
    LOOP for each issue:
      - Setup orchestration folder
      - Check dependencies
      - Choose coordination mode (teams vs subagents per step)
      - Spawn Designer → specs (if UI)
      - Implementation:
          Subagent path: Spawn Developer → implements, creates PR
          Team path:     Developer + Designer team → real-time iteration, PR
      - Reviews:
          Subagent path: Spawn Architect, Designer, Tester in parallel
          Team path:     Review team → coordinated findings
      - Check PR Done Criteria
      - Merge (if all-issues mode)
      - Continue to next
           ↓
    All complete → Notify user
```

---

## Bidirectional Context Flow

Sub-agents start with fresh context (no conversation history). The orchestration layer uses **briefings** and **reports** to communicate context and capture results.

### Orchestration Folder Structure

```
orchestration/
├── discovery/
│   └── {date}-{feature-slug}/
│       ├── BRIEFING-architect-review.md
│       ├── REPORT-architect-review.md
│       └── ...
├── planning/
│   └── {date}-{plan-name}/
│       └── ...
└── issues/
    └── {issue-number}-{slug}/
        ├── BRIEFING-design-specs.md
        ├── REPORT-design-specs.md
        ├── BRIEFING-implement.md
        ├── REPORT-implement.md
        ├── BRIEFING-architect-review.md
        ├── REPORT-architect-review.md
        ├── BRIEFING-designer-review.md
        ├── REPORT-designer-review.md
        ├── BRIEFING-test.md
        └── REPORT-test.md
```

### How It Works

**Parent agent** (orchestrating workflow):
1. Creates briefing file in `orchestration/{type}/{id}/BRIEFING-{step}.md`
2. Includes briefing path in Task prompt when spawning sub-agent
3. After Task returns, reads `REPORT-{step}.md` from same folder
4. Includes report summary in next agent's briefing

**Sub-agent** (following AGENT.md protocol):
1. Reads briefing file path from task prompt
2. Reads briefing as first action
3. Does work
4. Writes report to `REPORT-{step}.md` in same folder before completing

### Context Chain

Each agent receives context about what previous agents did:

```
1. Designer creates specs → writes REPORT-design-specs.md
2. Developer briefing includes designer's report summary
3. Developer implements → writes REPORT-implement.md
4. Reviewer briefings include developer's report summary
5. ...and so on
```

This enables informed decisions throughout the workflow.

### Benefits

- **Audit trail**: Full history of agent communication per issue
- **Debugging**: Can review what context each agent received
- **No collisions**: Each spawn gets unique files
- **Context chain**: Parent aggregates prior work into new briefings

---

## PR Done Criteria

Both `/auto-work-issue` and `/auto-work-all` use these criteria to determine when a PR is ready:

### Required Approvals

| Review | When Required |
|--------|---------------|
| `✅ APPROVED - Architect` | Always |
| `✅ APPROVED - Designer` | If PR has UI changes |
| `✅ APPROVED - Tester` | Always |

### Criteria Checklist

- [ ] All required approval comments present
- [ ] No outstanding `❌ CHANGES REQUESTED`
- [ ] CI/automated tests passing

### Then What?

| Mode | Action |
|------|--------|
| `single-issue` | Post verification comment, **notify user**, stop |
| `all-issues` | Post verification, **merge**, continue to next issue |

---

## Issue State Labels

Track issue progress:

| Label | Description |
|-------|-------------|
| `ready` | No blocking dependencies, can be worked |
| `in-progress` | Currently being implemented |
| `blocked` | Waiting on dependencies or input |
| `needs-review` | PR open, awaiting reviews |

### State Flow

```
[new] → ready (if no deps) OR blocked (if deps)
  ↓
ready → in-progress (when selected)
  ↓
in-progress → needs-review (when PR opened)
  ↓
needs-review → [closed] (when merged)
```

---

## Dependency Parsing

Issues declare dependencies in their body:

```markdown
## Dependencies
Depends on #12
Depends on #15
```

An issue is "ready" when all dependencies are closed.

---

## Review Flow

### Standardized Review Comments

Since all agents share the same GitHub identity, reviews use standardized comments:

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

### Review Process

```
1. Developer creates PR

2. Architect reviews (REQUIRED)
   Posts: ✅ APPROVED - Architect
   Or: ❌ CHANGES REQUESTED - Architect

3. Designer reviews (if UI)
   Posts: ✅ APPROVED - Designer
   Or: N/A - no UI changes

4. Tester verifies (REQUIRED)
   Posts: ✅ APPROVED - Tester
   Or: ❌ CHANGES REQUESTED - Tester

5. If changes requested:
   Developer fixes
   Re-request relevant review

6. When all approved:
   Orchestration checks mode
   → single-issue: notify user
   → all-issues: merge and continue
```

---

## Escalation Procedures

### Developer → Architect

After 5 failed attempts:
```
Use the architect agent to analyze issue #{number}.
Developer has tried: [list]
Error: [description]
```

### Architect → Human

If Architect also stuck:
```bash
.claude/hooks/request-attention.sh stuck "Unable to resolve issue #{number}"
```

Mark issue as blocked, continue to next issue.

---

## Artifact Files

The workflow produces these artifacts:

| File | Command | Purpose |
|------|---------|---------|
| `discovery.md`, `discovery-{N}.md` | `/auto-discovery` | Requirements, flows, architecture (numbered on re-runs) |
| `implementation-plan.md`, `implementation-plan-{N}.md` | `/auto-plan` | Sequenced work order (numbered on re-runs) |
| `design-system.md` | `/auto-plan` | Design language (updated in place) |
| `.claude/agents/*/PROJECT.md` | `/auto-evolve` | Role-specific context (fully regenerated each run) |
| `orchestration/issues/*/` | `/auto-work-issue`, `/auto-work-all` | Briefings and reports per issue |

---

## GitHub Commands Reference

```bash
# List open issues
gh issue list --state open --json number,title,labels

# Check issue dependencies
gh issue view {n} --json body --jq '.body' | grep -oE 'Depends on #[0-9]+'

# View PR comments for approvals
gh pr view {n} --comments

# Post orchestration comment
gh pr comment {n} --body "**[Product Owner]** ..."

# Merge PR
gh pr merge {n} --squash --delete-branch

# Check issue state
gh issue view {n} --json state --jq '.state'
```
