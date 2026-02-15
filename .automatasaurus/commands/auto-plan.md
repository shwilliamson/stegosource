# Work Plan - Create Implementation Plan

Analyze open issues and create a sequenced implementation plan.

## Workflow Mode

```
WORKFLOW_MODE: planning
```

---

## Instructions

You are now the **Implementation Planner**. Your job is to:
1. Read all open issues from GitHub
2. Analyze dependencies and priorities
3. Create an `implementation-plan.md` document
4. Present to user for approval

---

## Phase 0.5: Detect Existing Plan Files

**Before gathering issues, check for prior plan runs:**

```bash
ls implementation-plan.md implementation-plan-*.md 2>/dev/null
```

- If **none exist** → this is the first run, will create `implementation-plan.md`
- If **some exist** → find the highest number and create `implementation-plan-{N+1}.md`
  - `implementation-plan.md` counts as run 1
  - `implementation-plan-2.md` is run 2, etc.
- **Read ALL existing plan files** for context — understand the current dependency graph and what's already been sequenced

---

## Phase 1: Gather Issues

### Read All Discovery Files

```bash
ls discovery.md discovery-*.md 2>/dev/null
```

Read all discovery files (glob `discovery*.md`) for full requirements context.

### List All Open Issues

```bash
gh issue list --state open --json number,title,labels,milestone,body --jq '.[] | "### #\(.number): \(.title)\nMilestone: \(.milestone.title // "None")\nLabels: \(.labels | map(.name) | join(", "))\n"'
```

### Check Milestones

```bash
gh api repos/{owner}/{repo}/milestones --jq '.[] | "#\(.number): \(.title) - \(.open_issues) open, \(.closed_issues) closed"'
```

---

## Phase 2: Analyze Dependencies

For each issue, extract dependencies:

```bash
# Get issue body and find dependencies
gh issue view {number} --json body --jq '.body' | grep -oE 'Depends on #[0-9]+'
```

Build a dependency graph:
- Which issues have no dependencies? (Can start immediately)
- Which issues are blocked by others?
- Which issues unblock the most other work?

---

## Phase 3: Design Language & Style Guide

Before implementation begins, spawn the Designer agent to establish the visual foundation:

```
Use the Task tool with:
  subagent_type: "designer"
  model: "opus"
  description: "Create design language"
  prompt: |
    Establish the design language and style guide for this project.

    1. Check for existing design documentation:
       - Look for `design-system.md`, `DESIGN.md`, `style-guide.md`, or similar
       - Check for design tokens in the codebase (CSS variables, theme files)
       - Look in `/docs`, `/design`, or project root
    2. Review the open issues to understand the scope and UI needs
    3. Analyze the existing codebase for current patterns and styling
    4. If design docs exist: review and extend them as needed
       If no design docs exist: create `design-system.md` with:

    ## Color Palette
    - Primary colors (brand identity, CTAs)
    - Secondary colors (accents, highlights)
    - Neutral colors (backgrounds, text, borders)
    - Semantic colors (success, warning, error, info)
    - Include hex values and CSS custom properties

    ## Typography
    - Font families (headings, body, monospace)
    - Type scale (sizes, line heights, weights)
    - Text styles for each context

    ## Spacing & Layout
    - Spacing scale (4px, 8px, 16px, etc.)
    - Container widths and breakpoints
    - Grid system (if applicable)

    ## Components
    - Button styles (primary, secondary, ghost, sizes)
    - Form inputs (text, select, checkbox, radio)
    - Cards and containers
    - Navigation patterns
    - Feedback elements (alerts, toasts, modals)

    ## Interaction Patterns
    - Hover, focus, and active states
    - Transitions and animations (subtle, responsive, not decorative)
    - Loading states
    - Empty states

    ## Accessibility Standards
    - Minimum contrast ratios (4.5:1 text, 3:1 UI)
    - Focus indicators (visible, consistent)
    - Touch target sizes (minimum 44x44px)

    ## Design Quality Criteria

    Apply these principles when making design decisions:

    **Visual Hierarchy:** Important actions should be prominent. Users should know
    where to look and what to do within 3 seconds.

    **Simplicity:** Every element should earn its place. When something feels
    complex, question whether the complexity is necessary.

    **Consistency:** Reuse patterns. Novel UI should only exist when it meaningfully
    improves the experience.

    **Restraint:** Default to fewer colors, more whitespace, and simpler solutions.
    A design that does less but does it well beats one that does more poorly.

    **Project Personality:** Consider:
    - Is this playful or professional?
    - Minimal or feature-rich?
    - Technical or consumer-facing?
    Let the answers inform aesthetic choices.

    The goal is an intuitive, polished user experience where colors work
    harmoniously, typography creates clear hierarchy, spacing feels balanced,
    and the overall aesthetic feels intentional rather than assembled from
    random choices.

    Output: Write the design system to `design-system.md` (or update existing).
    Return the path to the design document when complete.
```

The design system lives in its own file (`design-system.md`), separate from the implementation plan. It is always updated in place (not numbered). On incremental runs, only spawn the Designer if new issues require UI work — the Designer adds new components/updates with version annotations.

---

## Phase 4: Determine Sequence

Apply these criteria to determine work order:

### Priority 1: Milestone First
- Complete current milestone before moving to next
- Milestones should be done in order (v1.0 before v1.1)

### Priority 2: Dependencies
- Issues with no dependencies come first
- Issues that unblock others come before those that don't

### Priority 3: Labels
- `priority:high` before `priority:medium` before `priority:low`

### Priority 4: Logical Order
- Foundation (models, schemas) before features
- Backend before frontend (if applicable)
- Core flows before edge cases

---

## Phase 5: Create Implementation Plan

Create the plan document:

- **First run**: create `implementation-plan.md`
- **Subsequent runs**: create `implementation-plan-{N}.md` (e.g., `implementation-plan-2.md`)
- Subsequent run documents should contain:
  - Summary of ALL milestones/issues (complete current state)
  - Work sequence for NEW issues only (not in prior plans)
  - Updated dependency graph covering all issues (new and old)
  - `## Prior Plan Context` section referencing previous files
  - `## Progress Since Last Plan` section noting completed issues

Write the plan document:

```markdown
# Implementation Plan

Generated: [date]
Based on: [N] open issues across [M] milestones

## Summary

| Milestone | Issues | Status |
|-----------|--------|--------|
| [Milestone 1] | [count] | [x complete / y total] |
| [Milestone 2] | [count] | [x complete / y total] |

## Work Sequence

### Phase 1: [Current Milestone Name]

#### 1. Issue #[N]: [Title]
- **Why first**: [No dependencies / Foundation / etc.]
- **Unblocks**: #X, #Y
- **Estimated complexity**: Low / Medium / High
- **Key work**: [Brief description]

#### 2. Issue #[M]: [Title]
- **Why now**: [Dependency #N complete]
- **Unblocks**: #Z
- **Estimated complexity**: Medium
- **Key work**: [Brief description]

[Continue for all issues in milestone...]

### Phase 2: [Next Milestone Name]

[Continue pattern...]

## Dependency Graph

```
#1 (Schema)
  └── #2 (Registration)
        └── #4 (Password Reset)
  └── #3 (Login)
        └── #5 (Session Mgmt)
```

## Design Foundation

**Design System:** [link to design-system.md]

All UI implementations must follow the design system for a cohesive user experience.

## Blockers & Risks

- [Any issues that seem risky or unclear]
- [External dependencies]
- [Technical uncertainties]

## Notes

- [Any implementation notes]
- [Suggested approaches]
```

---

## Phase 6: Present to User

Show the plan summary:

```
I've analyzed [N] open issues and created an implementation plan.

**Design System:**
- Style guide created in `design-system.md`
- Color palette, typography, and component patterns defined
- Accessibility standards documented

**Milestones:**
- [Milestone 1]: [X] issues
- [Milestone 2]: [Y] issues

**Recommended sequence:**
1. #[N]: [Title] (no deps, foundation)
2. #[M]: [Title] (unblocks 3 others)
3. ...

The full plan is in `implementation-plan.md`.

**Optional Next Step:**

If you want to generate project-specific context for each agent, run:

`/auto-evolve`

This creates PROJECT.md files in each agent folder with tailored guidance based on discovery and the implementation plan. Recommended for complex projects.

Otherwise, proceed directly to `/auto-work-all`.
```

---

## Your Request

$ARGUMENTS

---

Begin by fetching the open issues and milestones from GitHub.
