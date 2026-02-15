---
name: agent-coordination
description: Patterns for invoking and coordinating Automatasaurus agents. Use when delegating tasks to specialist agents.
---

# Agent Coordination Skill

This skill provides patterns for invoking the Automatasaurus agents and managing bidirectional context flow.

## Coordination Modes

Automatasaurus supports two modes for coordinating agent work:

| Mode | Mechanism | Communication | Best For |
|------|-----------|---------------|----------|
| **Subagents** (default) | Task tool | Report to orchestrator only | Single-role tasks, linear workflows |
| **Agent Teams** (experimental) | Team creation | Peer-to-peer messaging + shared tasks | Multi-role reviews, real-time collaboration |

**Decision criteria:**
- Use **subagents** when tasks are independent and don't benefit from real-time coordination
- Use **teams** when agents should share findings and coordinate in real-time (e.g., review cycles)
- Check `teamPreferForReviews` and `teamPreferForImplementation` in settings for project defaults
- Always have a **fallback to subagents** — teams are experimental

For detailed team patterns, load the `team-coordination` skill.

## Available Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `developer` | Implements issues, creates PRs | When code needs to be written |
| `architect` | Technical reviews, analysis | For PR reviews, discovery reviews, stuck issues |
| `designer` | UI/UX reviews, design specs | For PR reviews, discovery reviews, design specs |
| `researcher` | Deep research, technology evaluation | When any agent needs thorough research on a topic |
| `tester` | Testing, verification | For PR verification, running tests |

---

## Bidirectional Context Flow

Sub-agents start with fresh context (no conversation history). Use briefing and report files to communicate context and capture results.

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

### Before Spawning a Sub-agent

1. **Determine folder path:**
   - For issues: `orchestration/issues/{issue-number}-{slug}/`
   - For discovery: `orchestration/discovery/{date}-{feature}/`
   - For planning: `orchestration/planning/{date}-{plan}/`

2. **Create folder if needed:**
   ```bash
   mkdir -p orchestration/issues/{issue-number}-{slug}
   ```

3. **Read prior reports in folder** (if any) to understand what previous agents did.

4. **Write BRIEFING-{step}.md** with context for the sub-agent.

5. **Include briefing path in Task prompt:**
   ```
   Read orchestration/issues/42-auth/BRIEFING-implement.md first, then proceed with implementation.
   ```

### After Sub-agent Returns

1. **Derive report path** from briefing path (same folder, REPORT- prefix).

2. **Read the report file** to understand what the agent did.

3. **When creating next briefing**, include summary under "Prior Agent Activity".

---

## Briefing Format (Parent→Child)

```markdown
# Agent Briefing: {step-name}
Generated: {timestamp}

## Your Task
{What the sub-agent should do - be specific and actionable}

## Context
{Why this task exists, constraints, decisions made}
{Summarized recent activity if relevant}

## Prior Agent Activity
{Summaries from previous agents' reports - if any}

## Resources (Read as Needed)
- `discovery.md` - Project requirements
- `src/auth/middleware.ts` - Existing auth pattern
- Issue #42 comments - Designer specs
```

### Briefing Template

```markdown
# Agent Briefing: {step}
Generated: {timestamp}

## Your Task
{Clear, actionable description of what to do}

## Context
{Background information the agent needs}
- Issue/PR: #{number}
- Goal: {what success looks like}
- Constraints: {any limitations or requirements}

## Prior Agent Activity
{If previous agents worked on this, summarize their reports:}
- **Designer**: Created specs for login form, specified error states
- **Developer**: Implemented login endpoint, tests passing

## Resources (Read as Needed)
- {path} - {what it contains}
- {path} - {what it contains}

## Expected Output
{What the agent should produce/report}
```

---

## Report Format (Child→Parent)

Sub-agents write a report before completing. This captures what happened for audit and context chaining.

```markdown
# Agent Report: {step-name}
Completed: {timestamp}
Agent: {role}

## What Was Done
{Summary of actions taken}

## Key Decisions Made
{Any choices the agent made during work}

## Files Changed
- `src/auth/login.ts` - Added login endpoint
- `src/auth/middleware.ts` - Updated JWT validation

## Issues Encountered
{Problems hit, workarounds used}

## Notes for Next Agent
{Context that would help follow-up work}
```

### Report Template

```markdown
# Agent Report: {step}
Completed: {timestamp}
Agent: {role}

## What Was Done
{Bullet points of completed actions}

## Key Decisions Made
{Choices made and rationale}

## Files Changed
- `{path}` - {change description}

## Issues Encountered
{Problems and how they were resolved, or if still open}

## Notes for Next Agent
{Anything the next agent should know}
```

---

## Invocation Patterns

### Developer - Implement an Issue

```
1. Create briefing folder:
   mkdir -p orchestration/issues/{number}-{slug}

2. Write BRIEFING-implement.md:
   # Agent Briefing: implement
   Generated: {timestamp}

   ## Your Task
   Implement issue #{number}: {title}

   ## Context
   - Acceptance criteria: {from issue body}
   - Design specs: {if applicable, from designer comment}
   - Mode: {single-issue/all-issues}

   ## Prior Agent Activity
   {If designer created specs, summarize here}

   ## Resources (Read as Needed)
   - Issue #{number}: gh issue view {number}
   - design-system.md: Available design tokens
   - Designer specs in issue comments

   ## Expected Output
   - Working implementation
   - Tests passing
   - PR created with "Closes #{number}"

3. Use Task tool with:
   subagent_type: "developer"
   prompt: |
     Read orchestration/issues/{number}-{slug}/BRIEFING-implement.md first.

     After completing your work, write your report to:
     orchestration/issues/{number}-{slug}/REPORT-implement.md

4. After Task returns, read REPORT-implement.md
```

### Architect - Review PR

```
1. Write BRIEFING-architect-review.md:
   # Agent Briefing: architect-review
   Generated: {timestamp}

   ## Your Task
   Review PR #{pr_number} for technical quality.

   ## Context
   - Issue: #{issue_number} - {title}
   - Developer completed implementation

   ## Prior Agent Activity
   - **Developer**: {summary from REPORT-implement.md}

   ## Resources (Read as Needed)
   - PR #{pr_number}: gh pr view {pr_number}
   - PR diff: gh pr diff {pr_number}

   ## Expected Output
   Post standardized review comment:
   - ✅ APPROVED - Architect
   - OR ❌ CHANGES REQUESTED - Architect

2. Use Task tool with:
   subagent_type: "architect"
   prompt: |
     Read orchestration/issues/{number}-{slug}/BRIEFING-architect-review.md first.

     After completing your review, write your report to:
     orchestration/issues/{number}-{slug}/REPORT-architect-review.md
```

### Designer - Add Specs to Issue

```
1. Write BRIEFING-design-specs.md:
   # Agent Briefing: design-specs
   Generated: {timestamp}

   ## Your Task
   Add UI/UX specifications to issue #{number}.

   ## Context
   - Issue involves UI work: {description}
   - No existing design specs found

   ## Resources (Read as Needed)
   - Issue #{number}: gh issue view {number}
   - design-system.md: Available design tokens
   - Existing components for patterns

   ## Expected Output
   Post design specifications as issue comment following AGENT.md template.

2. Use Task tool with:
   subagent_type: "designer"
   prompt: |
     Read orchestration/issues/{number}-{slug}/BRIEFING-design-specs.md first.

     After completing your specs, write your report to:
     orchestration/issues/{number}-{slug}/REPORT-design-specs.md
```

### Designer - Review PR

```
1. Write BRIEFING-designer-review.md:
   # Agent Briefing: designer-review
   Generated: {timestamp}

   ## Your Task
   Review PR #{pr_number} for UI/UX quality.

   ## Context
   - Issue: #{issue_number}
   - Design specs were provided earlier

   ## Prior Agent Activity
   - **Developer**: {summary from REPORT-implement.md}
   - **Architect**: {summary from REPORT-architect-review.md}

   ## Resources (Read as Needed)
   - PR #{pr_number}: gh pr view {pr_number}
   - Original design specs in issue comments

   ## Expected Output
   Post standardized review comment:
   - ✅ APPROVED - Designer
   - OR ❌ CHANGES REQUESTED - Designer
   - OR N/A - No UI changes

2. Use Task tool with:
   subagent_type: "designer"
   prompt: |
     Read orchestration/issues/{number}-{slug}/BRIEFING-designer-review.md first.

     After completing your review, write your report to:
     orchestration/issues/{number}-{slug}/REPORT-designer-review.md
```

### Tester - Verify PR

```
1. Write BRIEFING-test.md:
   # Agent Briefing: test
   Generated: {timestamp}

   ## Your Task
   Verify PR #{pr_number}.

   ## Context
   - Issue: #{issue_number}
   - Reviews completed by Architect and Designer

   ## Prior Agent Activity
   - **Developer**: {summary}
   - **Architect**: {review result}
   - **Designer**: {review result}

   ## Resources (Read as Needed)
   - PR #{pr_number}: gh pr view {pr_number}
   - Acceptance criteria in issue #{issue_number}

   ## Expected Output
   Post standardized review comment:
   - ✅ APPROVED - Tester
   - OR ❌ CHANGES REQUESTED - Tester

2. Use Task tool with:
   subagent_type: "tester"
   prompt: |
     Read orchestration/issues/{number}-{slug}/BRIEFING-test.md first.

     After completing verification, write your report to:
     orchestration/issues/{number}-{slug}/REPORT-test.md
```

### Architect - Analyze Stuck Issue

```
1. Write BRIEFING-analysis.md in the issue folder:
   # Agent Briefing: analysis
   Generated: {timestamp}

   ## Your Task
   Analyze issue #{number} - Developer is stuck.

   ## Context
   Developer has tried 5 times and cannot resolve the issue.

   ## Prior Agent Activity
   - **Developer**: {from REPORT-implement.md, including attempts and errors}

   ## Resources (Read as Needed)
   - Issue #{number}
   - PR #{pr_number} (if exists)
   - Error logs/output from developer attempts

   ## Expected Output
   Provide guidance with:
   - Root cause analysis
   - Recommended approach
   - Code example if helpful

2. Use Task tool with Architect agent, including briefing path.
```

### Researcher - Investigate a Topic

```
1. Write BRIEFING-research.md:
   # Agent Briefing: research
   Generated: {timestamp}

   ## Your Task
   Research {topic} for issue #{number}.

   ## Context
   - Why this research is needed: {explanation}
   - What's already known: {existing knowledge}

   ## Research Questions
   1. {Specific question to answer}
   2. {Specific question to answer}

   ## Resources (Read as Needed)
   - Issue #{number}: gh issue view {number}
   - Relevant code: {paths if known}

   ## Expected Output
   Structured research report with findings, confidence levels, and sources.

2. Use Task tool with:
   subagent_type: "researcher"
   prompt: |
     Read orchestration/issues/{number}-{slug}/BRIEFING-research.md first.

     After completing your research, write your report to:
     orchestration/issues/{number}-{slug}/REPORT-research.md
```

---

## Parallel Invocation

When reviews are independent, invoke agents in parallel. Each gets its own briefing:

```
# Create all briefings first
Write BRIEFING-architect-review.md
Write BRIEFING-designer-review.md
Write BRIEFING-test.md

# Then invoke in parallel (single message, multiple tool calls)
Use the architect agent with BRIEFING-architect-review.md
Use the designer agent with BRIEFING-designer-review.md
Use the tester agent with BRIEFING-test.md

# After all return, read all reports
Read REPORT-architect-review.md
Read REPORT-designer-review.md
Read REPORT-test.md
```

---

## Team Invocation Patterns

When using agent teams instead of subagents, the orchestrator creates a team and acts as lead in delegate mode.

### Review Team (Alternative to Parallel Subagent Reviews)

Instead of spawning architect, designer, and tester as separate subagents:

```
1. Write all BRIEFING files (same as subagent approach)

2. Create team:
   "Create a team to review PR #{pr_number} for issue #{issue_number}.

   Teammates:
   - Architect: Read BRIEFING-architect-review.md, review PR for technical quality
   - Tester: Read BRIEFING-test.md, verify PR with E2E testing
   - Designer: Read BRIEFING-designer-review.md, review UI/UX (if applicable)

   Each teammate: read briefing, perform review, post comment, write report."

3. After team completes, read all REPORT files
4. Write REPORT-team-review.md synthesizing findings
```

### Implementation Team (Alternative to Sequential Designer → Developer)

Instead of spawning designer first, then developer:

```
1. Write BRIEFING files for both roles

2. Create team:
   "Create a team to implement issue #{issue_number}.

   Teammates:
   - Developer: Read BRIEFING-implement.md, implement feature, create PR
   - Designer: Read BRIEFING-design-specs.md, provide real-time UI feedback

   Developer messages Designer for UI decisions.
   Designer messages Developer when implementation doesn't match specs."

3. After team completes, read REPORT files
```

### Team Briefing Format

Team briefings use the same format as subagent briefings (see templates above), with an added "Team Context" section:

```markdown
## Team Context
You are part of a team. Your teammates are:
- {Role}: {their task}
Message teammates when you find something relevant to their review.
```

### Fallback

If team creation fails, fall back to standard subagent invocation. See `team-coordination` skill for the full fallback protocol.

---

## Quality Gates

Each agent has quality gates:

| Agent | Gate (Subagent) | Gate (Team) |
|-------|------|------|
| Developer | Tests passing, PR created | Same + shared UI progress with designer |
| Architect | Technical review complete | Same + cross-findings shared with teammates |
| Designer | Design review complete | Same + real-time feedback provided |
| Researcher | Structured report written with findings and sources | N/A (typically subagent only) |
| Tester | All tests pass, verification complete | Same + verified architect-flagged concerns |

---

## Escalation Flow

```
Developer stuck (5 attempts)
    ↓
Create BRIEFING-analysis.md with developer's report
    ↓
Architect analyzes
    ↓
If still stuck → Human escalation
    .claude/hooks/request-attention.sh stuck "..."
```

---

## Context Chain Example

For issue #42 user authentication:

```
1. BRIEFING-design-specs.md created → Designer spawned
   ← REPORT-design-specs.md written

2. BRIEFING-implement.md created (includes designer's report summary)
   → Developer spawned
   ← REPORT-implement.md written

3. BRIEFING-architect-review.md created (includes developer's report)
   → Architect spawned
   ← REPORT-architect-review.md written

4. BRIEFING-designer-review.md created (includes dev + arch reports)
   → Designer spawned
   ← REPORT-designer-review.md written

5. BRIEFING-test.md created (includes all prior reports)
   → Tester spawned
   ← REPORT-test.md written
```

Each agent receives context about what previous agents did, enabling informed decisions.
