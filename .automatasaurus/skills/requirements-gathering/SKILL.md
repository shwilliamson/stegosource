---
name: requirements-gathering
description: Discovery questions, checklists, and techniques for gathering requirements. Use during discovery to ensure thorough understanding before creating issues.
---

# Requirements Gathering Skill

This skill provides guidance for thorough requirements gathering during discovery.

## Core Principle

**The more we nail down upfront, the better the results.** Don't assume - ASK.

## Your Job During Discovery

- Be thorough and inquisitive
- Ask clarifying questions before creating any issues
- Uncover hidden assumptions
- Define the desired end state clearly
- Identify edge cases early
- Document what's in scope AND out of scope

---

## Questions to Ask for Every Feature

### Goals & Success

- What problem are we solving?
- What does success look like? How will we measure it?
- What's the priority relative to other work?

### Users & Personas

- Who are the users of this feature?
- Are there different user types with different needs?
- What permissions/roles are involved?

### Core Functionality

- What is the primary goal?
- Walk me through the ideal user flow step by step
- What happens at each step?

### Data & State

- What data needs to be captured/stored?
- What are the required fields vs optional?
- Are there validation rules? (formats, lengths, ranges)
- What's the initial/default state?

### Edge Cases & Errors

- What happens if [X] fails?
- What if the user enters invalid data?
- What about empty states? (no data yet)
- What about concurrent access?
- Rate limiting needed?

### UI/UX (if applicable)

- Is there a specific design or layout in mind?
- Mobile responsive?
- Accessibility requirements?
- Loading states? Progress indicators?
- Success/error feedback to user?

### Integration

- Does this connect to external services?
- Are there existing patterns to follow?
- API format preferences?

### Security & Privacy

- Is this data sensitive?
- Authentication required?
- Who can see/edit this data?

### Architecture & Technical

- What's the existing tech stack?
- Are there performance requirements? (latency, throughput, scale)
- What's the deployment environment?
- Are there budget constraints?
- What external services or APIs are involved?

### Scope Boundaries

- What is explicitly NOT included?
- Are there future phases we should plan for but not build now?
- What's the MVP vs nice-to-have?
- What can we cut if we run short?

---

## Red Flags to Probe

When the user says something vague, dig deeper:

| User Says | Ask About |
|-----------|-----------|
| "Simple login" | What's simple? OAuth? Email/password? Magic links? |
| "Just like [X site]" | Which specific features? They have many |
| "Standard CRUD" | What fields? Validation? Permissions? |
| "Users can edit" | Edit what exactly? All fields? Their own only? |
| "Normal validation" | What's normal? Email format? Required fields? |
| "Handle errors" | Which errors? How? Messages? Retry? |
| "Make it secure" | What threats? Auth? Encryption? Rate limiting? |
| "Real-time updates" | WebSockets? SSE? Polling? How fresh? |
| "Good performance" | What's good? <100ms? <1s? Specific benchmarks? |

---

## Discovery Readiness Checklist

**Don't move to issue creation until:**

- [ ] You understand the complete user flow
- [ ] You've identified all user types involved
- [ ] You know what data is captured and validated
- [ ] Edge cases and error handling are defined
- [ ] Security/permission requirements are clear
- [ ] You know what's explicitly OUT of scope
- [ ] The user has confirmed your understanding
- [ ] Architecture approach is validated
- [ ] UI/UX requirements are captured (if applicable)

---

## Example: Requirements Interview

**User says:** "Add user authentication"

**Good discovery response:**

```
Before we design this, let me make sure I understand the full scope:

**Users:**
1. Is this for end-users, admins, or both?
2. Will there be different roles/permissions?

**Registration:**
3. What fields are required? (email, password, name, etc.)
4. Email verification required?
5. Password requirements? (length, complexity)
6. Terms of service acceptance?

**Login:**
7. Remember me / stay logged in option?
8. Session timeout duration?
9. Multiple device login allowed?

**Password:**
10. Password reset flow - email link or security questions?
11. Password change when logged in?
12. Account lockout after failed attempts?

**Security:**
13. Two-factor authentication needed?
14. OAuth/social login? (Google, GitHub, etc.)
15. Rate limiting on login attempts?

**Edge cases:**
16. What happens to existing data/users (if any)?
17. Account deletion/deactivation?

**Out of scope (confirm):**
18. User profile editing - separate feature?
19. Admin user management - separate feature?
```

---

## Capturing Discovery Output

As you gather requirements, document findings in structured format:

```markdown
## Goals
- [Primary goal]
- [Success metrics]

## Users
- [User type 1]: [needs]
- [User type 2]: [needs]

## Requirements
### Must Have (MVP)
- [Requirement 1]
- [Requirement 2]

### Nice to Have
- [Requirement 3]

## Architecture Considerations
- [Technical approach]
- [Constraints]

## UI/UX Requirements
- [Design notes]

## Out of Scope
- [Explicitly excluded item 1]
- [Explicitly excluded item 2]

## Open Questions
- [Any remaining unknowns]
```

This structured output becomes the `discovery.md` document.
