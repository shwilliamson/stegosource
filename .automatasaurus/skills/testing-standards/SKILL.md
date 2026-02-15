---
name: testing-standards
description: Testing strategies, patterns, and best practices. Use when writing tests, reviewing test coverage, or setting up testing infrastructure.
---

# Testing Standards

Guidelines for writing effective tests that catch bugs, enable refactoring, and document behavior.

## Testing Pyramid

Prefer more tests at the bottom, fewer at the top:

```
        /  E2E  \        Few, slow, high confidence
       /----------\
      / Integration \    Some, medium speed
     /----------------\
    /    Unit Tests    \  Many, fast, focused
```

## What to Test

### Always Test
- Business logic and calculations
- Edge cases and boundary conditions
- Error handling paths
- Public API contracts
- Security-sensitive code
- Complex conditionals

### Usually Skip
- Simple getters/setters
- Framework code (React renders, Express routing)
- Third-party library internals
- Private implementation details
- Logging statements

## Unit Tests

### Structure: Arrange-Act-Assert

```javascript
test('calculates total with discount', () => {
  // Arrange
  const cart = new Cart([{ price: 100 }, { price: 50 }]);
  const discount = 0.1;

  // Act
  const total = cart.calculateTotal(discount);

  // Assert
  expect(total).toBe(135);
});
```

### Naming Convention

```
test('[unit] [action] [expected result] [condition]')
```

Examples:
- `test('User.validate rejects empty email')`
- `test('calculateTax returns 0 for tax-exempt items')`
- `test('login redirects to dashboard on success')`

### Keep Tests Focused

```javascript
// Bad: Testing multiple behaviors
test('user registration', () => {
  expect(validate(user)).toBe(true);
  expect(hash(password)).toMatch(/^\$2b\$/);
  expect(sendEmail).toHaveBeenCalled();
  expect(db.save).toHaveBeenCalled();
});

// Good: One behavior per test
test('validates user email format', () => { ... });
test('hashes password with bcrypt', () => { ... });
test('sends welcome email after registration', () => { ... });
test('persists user to database', () => { ... });
```

## Integration Tests

Test how components work together:

```javascript
describe('User Registration Flow', () => {
  test('creates user and sends welcome email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', password: 'secure123' });

    expect(response.status).toBe(201);
    expect(await User.findByEmail('test@example.com')).toBeTruthy();
    expect(emailService.sent).toContainEqual(
      expect.objectContaining({ to: 'test@example.com' })
    );
  });
});
```

## End-to-End Tests

Reserve for critical user journeys:

```javascript
// Critical paths worth E2E testing
test('user can complete checkout flow', async () => { ... });
test('user can reset password via email', async () => { ... });

// Too granular for E2E
test('button changes color on hover', async () => { ... }); // Use unit test
```

## Mocking Strategy

### Mock External Dependencies
- API calls to third-party services
- Database in unit tests
- File system operations
- Time/dates for deterministic tests

### Don't Over-Mock
```javascript
// Bad: Mocking everything, testing nothing
jest.mock('./userService');
jest.mock('./emailService');
jest.mock('./database');
test('registers user', () => {
  // This only tests that mocks were called, not real behavior
});

// Good: Mock boundaries, test real logic
jest.mock('./emailService'); // External service
test('registers user', async () => {
  const user = await registerUser(validData);
  expect(user.email).toBe(validData.email);
  expect(emailService.send).toHaveBeenCalled();
});
```

## Test Data

### Use Factories/Builders

```javascript
// Factory for consistent test data
const createUser = (overrides = {}) => ({
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  role: 'member',
  ...overrides,
});

test('admin can delete users', () => {
  const admin = createUser({ role: 'admin' });
  const target = createUser({ id: 'user-456' });
  // ...
});
```

### Avoid Magic Values

```javascript
// Bad
expect(result).toBe(42);

// Good
const EXPECTED_TAX = 42;
expect(result).toBe(EXPECTED_TAX);
```

## Coverage Guidelines

### Targets
- **Unit tests**: 80%+ line coverage for business logic
- **Integration**: Cover all API endpoints
- **E2E**: Cover critical user journeys (login, checkout, etc.)

### Coverage is a Metric, Not a Goal

High coverage with bad tests is worse than moderate coverage with good tests.

```javascript
// 100% coverage, 0% value
test('covers the function', () => {
  doThing();
  // No assertions!
});
```

## Testing Async Code

```javascript
// Always await or return promises
test('fetches user data', async () => {
  const user = await fetchUser(123);
  expect(user.name).toBe('Alice');
});

// Test error cases
test('throws on invalid user ID', async () => {
  await expect(fetchUser(-1)).rejects.toThrow('Invalid user ID');
});
```

## Flaky Test Prevention

- Don't depend on test execution order
- Use fixed dates/times, not `Date.now()`
- Wait for conditions, not arbitrary timeouts
- Isolate test data (unique IDs per test)
- Clean up after tests

```javascript
// Bad: Arbitrary timeout
await sleep(1000);
expect(element).toBeVisible();

// Good: Wait for condition
await waitFor(() => expect(element).toBeVisible());
```

## Test File Organization

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx      # Co-located unit tests
├── services/
│   ├── userService.ts
│   └── userService.test.ts
tests/
├── integration/              # Integration tests
│   └── api/
│       └── users.test.ts
└── e2e/                      # E2E tests
    └── checkout.spec.ts
```