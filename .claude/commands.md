

<!-- AUTOMATASAURUS:COMMANDS:START -->
<!-- Do not manually edit this section. Run `npx automatasaurus update` to refresh. -->

## Automatasaurus Commands

These are the standard commands used by Automatasaurus agents. Update the commands above to match your project's actual configuration.

### Quick Reference (Update These!)

| Action | Command |
|--------|---------|
| Install dependencies | `npm install` |
| Start development server | `npm run dev` |
| Run all tests | `npm test` |
| Run E2E tests | `npm run test:e2e` |
| Build for production | `npm run build` |
| Lint code | `npm run lint` |

### Browser Testing with Playwright

```bash
# Install Playwright browsers
npx playwright install

# Run Playwright tests
npx playwright test

# Run with UI
npx playwright test --ui

# Record new test
npx playwright codegen [url]
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/issue-[number]-[description]

# Push and create PR
git push -u origin [branch-name]
gh pr create
```

---

**Note**: Update the commands above to match your project. This section is managed by Automatasaurus.

<!-- AUTOMATASAURUS:COMMANDS:END -->
