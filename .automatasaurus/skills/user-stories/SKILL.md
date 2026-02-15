---
name: user-stories
description: Guidelines for writing effective user stories with clear acceptance criteria. Use when creating issues from discovery findings.
---

# User Stories Skill

This skill provides guidance for writing well-formed user stories with clear acceptance criteria.

## User Story Format

```markdown
As a [type of user],
I want [goal/desire],
So that [benefit/value].
```

### Examples

**Good:**
```
As a registered user,
I want to reset my password via email,
So that I can regain access to my account if I forget my password.
```

**Bad:**
```
Add password reset feature.
```

The good example captures WHO needs it, WHAT they need, and WHY.

---

## INVEST Criteria

Good user stories are:

| Criteria | Description |
|----------|-------------|
| **I**ndependent | Can be developed separately from other stories |
| **N**egotiable | Details can be discussed and refined |
| **V**aluable | Delivers clear value to the user |
| **E**stimable | Can be sized (fits in a single PR) |
| **S**mall | Implementable in one PR, not weeks of work |
| **T**estable | Has clear acceptance criteria to verify |

### Checking Your Stories

- **Independent**: Does this require other stories to be done first? If so, document the dependency.
- **Negotiable**: Is there flexibility in HOW this is implemented?
- **Valuable**: Can you explain the user benefit?
- **Estimable**: Is it clear enough to implement?
- **Small**: Could this be done in 1-3 days? If not, break it down.
- **Testable**: Can you write acceptance criteria?

---

## Acceptance Criteria

Acceptance criteria define WHEN a story is complete. They should be:

- **Specific**: Clear, unambiguous conditions
- **Measurable**: Can be verified as pass/fail
- **Complete**: Cover the happy path AND edge cases

### Format

Use checkbox format for easy verification:

```markdown
## Acceptance Criteria
- [ ] User can request password reset with their email
- [ ] Reset link is sent to registered email only
- [ ] Reset link expires after 1 hour
- [ ] User sees error message for unregistered email
- [ ] User can set new password via reset link
- [ ] Old password no longer works after reset
```

### Writing Good Criteria

**Good criteria:**
- [ ] Login form shows error for incorrect password
- [ ] Error message says "Invalid email or password" (not which is wrong)
- [ ] Account locks after 5 failed attempts

**Bad criteria:**
- [ ] Login works correctly (too vague)
- [ ] Errors are handled (not specific)
- [ ] Good UX (not measurable)

---

## Breaking Down Large Features

Large features should be broken into stories sized for a single PR.

### Splitting Strategies

1. **By User Flow Step**
   - Registration → Login → Password Reset → Session Management

2. **By Data Entity**
   - User Model → User API → User UI

3. **By User Type**
   - End-user features → Admin features

4. **By Complexity Layer**
   - Backend API → Frontend UI → Integration

### Example: "User Authentication" Feature

Break into:

| Issue | Story | Dependencies |
|-------|-------|--------------|
| #1 | Database schema for users | None |
| #2 | User registration endpoint | #1 |
| #3 | User login endpoint | #1 |
| #4 | Session management | #3 |
| #5 | Password reset flow | #2, #3 |

Each issue is one PR's worth of work.

---

## Issue Template

```markdown
## User Story
As a [type of user],
I want [goal/desire],
So that [benefit/value].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
[Architecture decisions, approach, or constraints]

## UI/UX Requirements
[Design specs, wireframes, or "None - backend only"]

## Dependencies
[List as "Depends on #X" or "None - can be worked independently"]

## Out of Scope
[Explicitly list what is NOT included to avoid scope creep]
```

---

## Common Mistakes

### Too Big
**Bad:** "As a user, I want a complete authentication system"
**Better:** Split into registration, login, password reset, etc.

### No User Value
**Bad:** "Refactor the database layer"
**Better:** "As a developer, I want a normalized user schema so that queries are faster"

### Vague Criteria
**Bad:** "Login should work well"
**Better:** "User is redirected to dashboard after successful login"

### Missing Edge Cases
**Bad:** Only happy path criteria
**Better:** Include error states, empty states, boundary conditions

### Hidden Dependencies
**Bad:** No mention of required prior work
**Better:** "Depends on #1 (User model must exist first)"

---

## Verification

Before finalizing a story, verify:

1. **Is the user clear?** Who specifically benefits?
2. **Is the goal actionable?** What exactly will they do?
3. **Is the value stated?** Why does this matter?
4. **Are criteria testable?** Can each be verified pass/fail?
5. **Is it sized right?** One PR, not a week of work?
6. **Are dependencies explicit?** What must exist first?
7. **Is scope bounded?** What's explicitly excluded?
