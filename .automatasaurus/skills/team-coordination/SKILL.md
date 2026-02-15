---
name: team-coordination
description: Patterns for using Claude Code agent teams (experimental). Load when the orchestrator decides to use teams instead of subagents for a workflow step.
---

# Team Coordination Skill

This skill provides patterns for using Claude Code's experimental agent teams feature. Teams enable multiple independent Claude Code sessions that coordinate via shared task lists and peer-to-peer messaging.

## When to Load This Skill

Load this skill when:
- The orchestrator decides to use teams for reviews or implementation
- `teamPreferForReviews` or `teamPreferForImplementation` is `true` in settings
- You're about to spawn multiple agents that would benefit from real-time coordination

## Teams vs Subagents

| Aspect | Subagents (Task tool) | Agent Teams |
|--------|----------------------|-------------|
| **Communication** | Report to orchestrator only | Message each other directly |
| **Context** | Fresh context per spawn | Fresh context, but shared task list |
| **Coordination** | Sequential briefing/report chain | Real-time peer collaboration |
| **Best for** | Single-role tasks, linear workflows | Multi-role tasks, cross-pollination |
| **Audit trail** | BRIEFING/REPORT files | BRIEFING/REPORT files + shared task list |
| **Cost** | One session per agent | Multiple concurrent sessions |
| **Reliability** | Stable | Experimental — may need fallback |

## Team Creation

Teams are created using natural language prompts. The orchestrator creates a team by describing the goal and teammates.

**Key principle:** The orchestrator acts as team **lead** in delegate mode — it coordinates but does not implement.

### Delegate Mode

When leading a team, the orchestrator should:
1. Create the team with clear goals and teammate roles
2. Set up shared tasks describing what needs to be done
3. Let teammates claim and complete tasks independently
4. Monitor progress via the shared task list
5. Synthesize results when the team completes

**Do NOT** implement work yourself when leading a team. Your role is coordination.

---

## Team Patterns

### Review Team

**When to use:** PR reviews where cross-pollination of findings adds value. The architect might flag a concern that the tester should verify, or the designer might notice an accessibility issue that affects the architect's assessment.

**Teammates:** Architect, Tester, Designer (if UI changes)

**Prompt template:**

```
Create a team to review PR #{pr_number} for issue #{issue_number}: {title}.

Teammates needed:
- Architect: Review for technical quality, architecture alignment, and code correctness
- Tester: Verify the PR meets acceptance criteria using Playwright MCP for E2E testing
- Designer: Review UI/UX quality and accessibility (only if PR has UI changes)

Team goal: All teammates review the PR and post standardized review comments.
Each teammate should:
1. Read their briefing file from orchestration/issues/{issue_number}-{slug}/
2. Perform their review
3. Post their review comment on the PR
4. Write their report to orchestration/issues/{issue_number}-{slug}/
5. If they find something another teammate should look at, message them directly

Review comment format:
- ✅ APPROVED - {Role}
- ❌ CHANGES REQUESTED - {Role}

All teammates must complete their reviews before the team is done.
```

**Before creating the team:**
1. Write all BRIEFING files (same as subagent approach)
2. Include briefing paths in the team creation prompt
3. Each teammate reads their own briefing as first action

**After team completes:**
1. Read all REPORT files from the orchestration folder
2. Check PR comments for review results
3. Write a synthesized REPORT-team-review.md summarizing all findings

### Implementation Team

**When to use:** Complex issues requiring real-time collaboration between roles. For example, a UI feature where the developer needs immediate designer feedback on implementation decisions.

**Teammates:** Developer, Designer (if UI work)

**Prompt template:**

```
Create a team to implement issue #{issue_number}: {title}.

Teammates needed:
- Developer: Implement the feature, write tests, create PR
- Designer: Provide real-time UI feedback and review implementation as it progresses

Team goal: Implement the issue with integrated design review.
Each teammate should:
1. Read their briefing file from orchestration/issues/{issue_number}-{slug}/
2. Developer: Implement the feature, sharing progress with Designer for UI elements
3. Designer: Review component implementations as Developer shares them, provide feedback
4. Developer: Create PR with "Closes #{issue_number}"
5. Both write reports to orchestration/issues/{issue_number}-{slug}/

Developer should message Designer when:
- Starting a new UI component
- Making a design decision that wasn't in specs
- Unsure about responsive behavior or accessibility

Designer should message Developer when:
- Implementation doesn't match specs
- Suggesting improvements to current approach
- Providing accessibility guidance
```

### Discovery Review Team

**When to use:** Discovery plan reviews where architect and designer perspectives should inform each other.

**Teammates:** Architect, Designer

**Prompt template:**

```
Create a team to review the discovery plan at {discovery_path}.

Teammates needed:
- Architect: Review for technical feasibility, architecture fit, scalability
- Designer: Review for UI/UX considerations, user flows, accessibility

Team goal: Review the discovery plan and provide coordinated feedback.
Each teammate should:
1. Read the discovery plan
2. Perform their review
3. Share findings with the other teammate for cross-review
4. Post their review as a combined response

Architect should flag to Designer:
- Technical constraints that affect UI possibilities
- Performance concerns with proposed UI patterns

Designer should flag to Architect:
- UX requirements that have architectural implications
- Accessibility needs that affect technical approach
```

---

## Team Briefing Format

Even with teams, write BRIEFING files for the audit trail. The briefing format is the same as for subagents (see `agent-coordination` skill), but add a team context section:

```markdown
# Agent Briefing: {step}
Generated: {timestamp}

## Your Task
{What this teammate should do}

## Team Context
You are part of a team. Your teammates are:
- {Role}: {What they are doing}
- {Role}: {What they are doing}

Coordinate via messages when you find something relevant to another teammate.

## Context
{Standard briefing context}

## Prior Agent Activity
{Standard prior activity section}

## Resources (Read as Needed)
{Standard resources section}

## Expected Output
{Standard expected output section}
```

## Team Report Format

After a team completes, the lead writes a synthesized report:

```markdown
# Team Report: {step}
Completed: {timestamp}
Mode: Agent Team

## Team Composition
- {Role}: {What they did}
- {Role}: {What they did}

## Results
{Synthesized findings from all teammates}

## Cross-Pollination
{Findings that emerged from teammate collaboration — things that wouldn't have been caught by individual subagent reviews}

## Individual Reports
- REPORT-{role-1}-review.md: {summary}
- REPORT-{role-2}-review.md: {summary}

## Notes for Next Agent
{Context for follow-up work}
```

---

## Fallback Protocol

Agent teams are experimental. If team creation fails, fall back to the subagent approach:

```
1. Attempt to create team
2. If team creation fails (error, timeout, feature not available):
   a. Log: "Team creation failed, falling back to subagents"
   b. Use standard subagent invocation from agent-coordination skill
   c. Continue workflow normally
3. If team completes but results are incomplete:
   a. Check which teammates didn't complete
   b. Spawn those as individual subagents to finish
   c. Synthesize combined results
```

**Important:** A team failure should never block the workflow. The subagent approach is always available as a fallback.

---

## Cost Awareness

Teams use more tokens than subagents because multiple sessions run concurrently and may communicate.

| Scenario | Subagent Cost | Team Cost | When Team is Worth It |
|----------|--------------|-----------|----------------------|
| 3 parallel reviews | 3 sessions | 3 sessions + messaging | When reviewers should coordinate findings |
| Dev + Designer | 2 sequential sessions | 2 concurrent sessions + messaging | When real-time iteration saves rework cycles |
| 2 parallel reviews | 2 sessions | 2 sessions + messaging | Rarely — subagents are sufficient |

**Guidelines:**
- Use teams when **cross-pollination** of findings adds value
- Use subagents when tasks are **truly independent**
- The `teamMaxTeammates` limit (default: 4) prevents runaway costs
- Monitor team session duration — long-running teams should be investigated

---

## Quality Gates (Team Mode)

| Gate | How to Verify |
|------|--------------|
| All teammates completed | Check shared task list — all tasks resolved |
| Reports written | REPORT files exist in orchestration folder |
| Review comments posted | Check PR comments for standardized format |
| Team synthesized | Lead wrote REPORT-team-{step}.md |
| No unresolved cross-findings | Teammate messages addressed |
