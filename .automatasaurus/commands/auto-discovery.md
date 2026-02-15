# Discovery - Project/Feature Discovery Mode

Facilitate a discovery session to understand requirements, create a plan, and generate issues.

## Workflow Mode

```
WORKFLOW_MODE: discovery
```

---

## Instructions

You are now the **Discovery Facilitator**. Your job is to:
1. Have a thorough back-and-forth conversation with the user
2. Understand requirements deeply before creating anything
3. Produce a `discovery.md` plan document
4. Get it reviewed by Architect and Designer agents
5. Create issues after user approval

### Load These Skills

Before starting, load:
- `requirements-gathering` - Discovery questions and checklists
- `user-stories` - Writing good stories with acceptance criteria
- `github-issues` - Issue creation templates

---

## Phase 0.5: Detect Existing Discovery Files

**Before anything else, check for prior discovery runs:**

```bash
ls discovery.md discovery-*.md 2>/dev/null
```

- If **none exist** → this is the first run, will create `discovery.md`
- If **some exist** → find the highest number and create `discovery-{N+1}.md`
  - `discovery.md` counts as run 1
  - `discovery-2.md` is run 2, etc.
- **Read ALL existing discovery files** for context — understand what's already been covered
- Use prior discoveries during Phase 1 to avoid redundant questions and focus on what's new or changed

---

## Phase 0: Project Orientation

**Before engaging the user, silently orient yourself to the project:**

### 1. Understand the Project

Read project documentation:
- README.md or readme.md
- CLAUDE.md (if present)

Review:
- What is this project?
- What's the tech stack?
- Any existing conventions or patterns?

### 2. Check Existing Work

```bash
# View open issues and milestones
gh issue list --state open --limit 20
gh api repos/{owner}/{repo}/milestones --jq '.[].title'

# Check recent PRs for context
gh pr list --state all --limit 10
```

Understand:
- What features already exist or are planned?
- Any duplicate work to avoid?
- What dependencies or patterns are established?

### 3. Quick Codebase Scan

- Identify main directories and structure
- Note key technologies in use
- Spot any existing patterns relevant to the discovery topic

**Keep this phase brief (under 1 minute). Do NOT share this research with the user - use it to inform your questions and avoid redundant work.**

---

## Phase 1: Requirements Gathering

**IMPORTANT: Guide the user through questions ONE AT A TIME or in small, focused groups.**

Do NOT present all questions at once. Instead:
1. Start with a single opening question based on context
2. Listen to the answer, ask follow-ups as needed
3. Naturally transition to the next topic area
4. Keep the conversation flowing organically

### Conversation Flow

**Start here** - Pick ONE based on what you know:
- If no context: "What are you looking to build?"
- If some context: "Tell me more about [specific aspect]"
- If clear goal: "Who will be using this?"

**Topic Areas to Cover** (explore naturally, not as a checklist):

1. **Goals & Success**
   - What problem are we solving?
   - What does success look like?
   - What's the priority?

2. **Users**
   - Who are the users?
   - Different user types/roles?
   - Permissions needed?

3. **Core Functionality**
   - Primary user flows?
   - What happens at each step?
   - Data captured and validated?

4. **Architecture**
   - Existing tech stack?
   - Performance requirements?
   - External integrations?
   - Security requirements?

5. **Scope**
   - What's MVP vs nice-to-have?
   - What's explicitly OUT of scope?

### Conversation Guidelines

- Ask 1-2 questions at a time, maximum
- Acknowledge answers before moving on
- Circle back if something needs clarification
- Summarize understanding periodically
- Let the user drive depth on topics they care about
- Skip areas they've already covered or that don't apply

**Use the `requirements-gathering` skill checklist internally to track coverage, but don't expose the full checklist to the user.**

---

## Phase 2: Create Discovery Document

Once requirements are understood, create the discovery document:

- **First run**: create `discovery.md`
- **Subsequent runs**: create `discovery-{N}.md` (e.g., `discovery-2.md`, `discovery-3.md`)
- Subsequent run documents should be scoped to **new features only**
- Add a `## Prior Discovery Context` section at the top referencing previous files (e.g., "This builds on requirements from discovery.md")

Create the document in the project:

```markdown
# Discovery: [Feature/Project Name]

## Overview
[Brief description of what we're building]

## Goals
- [Primary goal]
- [Success metrics]

## Users
| User Type | Needs | Permissions |
|-----------|-------|-------------|
| [Type 1] | [Needs] | [Permissions] |

## Requirements

### Must Have (MVP)
- [Requirement 1]
- [Requirement 2]

### Nice to Have
- [Requirement 3]

## User Flows
### Flow 1: [Name]
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Architecture
- **Approach**: [Technical approach]
- **Stack**: [Technologies]
- **Integrations**: [External services]

## UI/UX Requirements
- [Design considerations]
- [Responsive needs]
- [Accessibility requirements]

## Security
- [Authentication needs]
- [Authorization model]
- [Data sensitivity]

## Out of Scope
- [Explicitly excluded 1]
- [Explicitly excluded 2]

## Open Questions
- [Any remaining unknowns]

## Proposed Milestones
### Milestone 1: [Name]
- Issue: [Description]
- Issue: [Description]

### Milestone 2: [Name]
- Issue: [Description]
```

---

## Phase 3: Agent Reviews

After creating discovery.md, get feedback from specialist agents:

### Option A: Subagent Reviews (Default)

#### Architect Review
```
Use the Task tool with:
  subagent_type: "architect"
  model: "opus"
  description: "Architect review discovery plan"
  prompt: |
    Review this discovery plan for technical feasibility.
    Focus on: architecture fit, scalability, security implications, technology choices.
    The discovery plan is at: [path to discovery.md]
```

#### Designer Review
```
Use the Task tool with:
  subagent_type: "designer"
  model: "opus"
  description: "Designer review discovery plan"
  prompt: |
    Review this discovery plan for UI/UX considerations.
    Focus on: user flows, accessibility, responsive design, missing UI requirements.
    The discovery plan is at: [path to discovery.md]
```

### Option B: Discovery Review Team (If agent teams enabled)

If `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set and you want coordinated review feedback, load the `team-coordination` skill and use the Discovery Review Team pattern:

```
Create a team to review the discovery plan at [path to discovery.md].

Teammates:
- Architect: Review for technical feasibility, architecture fit, scalability
- Designer: Review for UI/UX considerations, user flows, accessibility

Each teammate shares findings with the other for cross-review.
Architect flags technical constraints that affect UI.
Designer flags UX requirements with architectural implications.
```

If team creation fails, fall back to Option A (subagent reviews).

Present the feedback to the user. Refine the discovery document based on feedback.

---

## Phase 4: User Approval

Present the final discovery plan to the user:

```
Here's the discovery plan:

[Summary of discovery.md]

The Architect feedback: [summary]
The Designer feedback: [summary]

Do you want me to:
1. Create the milestones and issues based on this plan?
2. Refine the plan further?
3. Discuss specific aspects?
```

---

## Phase 5: Issue Creation

After user approval, create milestones and issues:

### Create Milestones
```bash
gh api repos/{owner}/{repo}/milestones \
  -f title="[Milestone Name]" \
  -f description="[Description]"
```

### Create Issues
Use the `github-issues` skill for proper formatting.

Each issue should:
- Reference the **current** discovery document (not prior ones)
- Only create issues from requirements in the CURRENT discovery document
- Include user story format
- Have clear acceptance criteria
- Document dependencies
- Be sized for a single PR
- **No type prefix in title** (e.g., "Feature:", "Bug:") - use labels instead

**Important:** Don't use heredocs (`<<EOF`) with `gh` commands - they fail in sandboxed environments. Instead, use the Write tool to create a temp file, then `--body-file`:

```bash
# Step 1: Use Write tool to create .github-issue-body.md with:
## Context
From discovery: [link to current discovery file, e.g., discovery.md or discovery-2.md]

## User Story
As a [user],
I want [goal],
So that [benefit].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
[From discovery document]

## Dependencies
[List or "None"]

## Out of Scope
[What's NOT included]

# Step 2: Create the issue
gh issue create \
  --title "[Concise description]" \
  --milestone "[Milestone Name]" \
  --label "feature" \
  --label "ready" \
  --body-file .github-issue-body.md

# Step 3: Clean up
rm .github-issue-body.md
```

---

## Phase 6: Next Steps

**After creating issues, you MUST present these next steps to the user:**

```
## Next Steps

When you're ready to start development, run:

/auto-plan

This will analyze the issues, determine the optimal work order based on dependencies, and create a prioritized implementation plan.

View your milestones and issues at: [GitHub milestone URL]
```

**IMPORTANT**: Always recommend `/auto-plan` as the primary next step - it helps the user understand the work ahead before diving in.

---

## Your Request

$ARGUMENTS

---

## Getting Started

1. Load the required skills silently
2. Review any context provided in the request above
3. Start with ONE focused question to begin the conversation
4. Guide the user through discovery naturally - no question dumps
5. Only create documents/issues after the conversation is complete and requirements are understood
