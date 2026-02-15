---
name: security-standards
description: Security best practices for application development. Use when handling user input, authentication, secrets, or reviewing code for vulnerabilities.
---

# Security Standards

Guidelines for writing secure code and avoiding common vulnerabilities.

## Core Principles

1. **Never trust user input** - Validate and sanitize everything
2. **Least privilege** - Grant minimum necessary permissions
3. **Defense in depth** - Multiple layers of protection
4. **Fail securely** - Errors should not expose sensitive data
5. **Keep secrets secret** - Never commit credentials

## Input Validation

### Validate All Input

```javascript
// Bad: Trust user input
const userId = req.params.id;
const user = await db.query(`SELECT * FROM users WHERE id = ${userId}`);

// Good: Validate and parameterize
const userId = parseInt(req.params.id, 10);
if (isNaN(userId) || userId < 0) {
  throw new ValidationError('Invalid user ID');
}
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

### Allowlist Over Denylist

```javascript
// Bad: Trying to block bad input
const sanitized = input.replace(/<script>/gi, '');

// Good: Only allow expected patterns
const ALLOWED_PATTERN = /^[a-zA-Z0-9_-]+$/;
if (!ALLOWED_PATTERN.test(input)) {
  throw new ValidationError('Invalid characters');
}
```

### Type Coercion

```javascript
// Bad: Loose comparison allows bypass
if (req.body.admin == true) { ... }

// Good: Strict type checking
if (req.body.admin === true && typeof req.body.admin === 'boolean') { ... }
```

## SQL Injection Prevention

### Always Use Parameterized Queries

```javascript
// Bad: String concatenation
db.query(`SELECT * FROM users WHERE email = '${email}'`);

// Good: Parameterized query
db.query('SELECT * FROM users WHERE email = $1', [email]);

// Good: ORM with proper escaping
User.findOne({ where: { email } });
```

## XSS Prevention

### Escape Output

```javascript
// Bad: Direct HTML insertion
element.innerHTML = userComment;

// Good: Text content (auto-escapes)
element.textContent = userComment;

// Good: Sanitize if HTML needed
element.innerHTML = DOMPurify.sanitize(userComment);
```

### React/JSX

```jsx
// Safe: React escapes by default
<div>{userInput}</div>

// Dangerous: Avoid unless absolutely necessary
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

### Content Security Policy

```javascript
// Set CSP headers
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],  // No inline scripts
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
  },
}));
```

## Authentication

### Password Handling

```javascript
// Never store plain text passwords
// Bad
user.password = req.body.password;

// Good: Hash with bcrypt (cost factor 12+)
const bcrypt = require('bcrypt');
user.passwordHash = await bcrypt.hash(req.body.password, 12);

// Verify
const valid = await bcrypt.compare(inputPassword, user.passwordHash);
```

### Session Management

```javascript
// Secure session configuration
app.use(session({
  secret: process.env.SESSION_SECRET,
  name: 'sessionId',  // Don't use default name
  cookie: {
    httpOnly: true,   // No JavaScript access
    secure: true,     // HTTPS only
    sameSite: 'strict',
    maxAge: 3600000,  // 1 hour
  },
  resave: false,
  saveUninitialized: false,
}));
```

### JWT Best Practices

```javascript
// Sign with strong secret, short expiration
const token = jwt.sign(
  { userId: user.id, role: user.role },
  process.env.JWT_SECRET,
  { expiresIn: '15m', algorithm: 'HS256' }
);

// Always verify algorithm
jwt.verify(token, secret, { algorithms: ['HS256'] });
```

## Authorization

### Check Permissions Server-Side

```javascript
// Bad: Client-side only check
if (user.role === 'admin') {
  showAdminPanel();
}

// Good: Server enforces authorization
app.delete('/users/:id', requireAuth, async (req, res) => {
  if (req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  await deleteUser(req.params.id);
});
```

### Avoid IDOR (Insecure Direct Object Reference)

```javascript
// Bad: User can access any record by changing ID
app.get('/documents/:id', async (req, res) => {
  const doc = await Document.findById(req.params.id);
  res.json(doc);
});

// Good: Verify ownership
app.get('/documents/:id', requireAuth, async (req, res) => {
  const doc = await Document.findOne({
    _id: req.params.id,
    ownerId: req.user.id,  // Must belong to user
  });
  if (!doc) return res.status(404).json({ error: 'Not found' });
  res.json(doc);
});
```

## Secrets Management

### Never Commit Secrets

```gitignore
# .gitignore
.env
.env.local
*.pem
*.key
credentials.json
secrets/
```

### Environment Variables

```javascript
// Load from environment
const apiKey = process.env.API_KEY;
if (!apiKey) {
  throw new Error('API_KEY environment variable required');
}

// Never log secrets
console.log('Connecting with key:', apiKey);  // Bad!
console.log('Connecting to API...');           // Good
```

### Rotate Compromised Secrets Immediately

If a secret is ever committed:
1. Revoke/rotate the secret immediately
2. Remove from git history (if possible)
3. Audit for unauthorized access

## CSRF Protection

```javascript
// Use CSRF tokens for state-changing requests
const csrf = require('csurf');
app.use(csrf({ cookie: true }));

// Include token in forms
<input type="hidden" name="_csrf" value="<%= csrfToken %>" />

// Or in headers for AJAX
headers: { 'X-CSRF-Token': csrfToken }
```

## Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

// General rate limiting
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // 100 requests per window
}));

// Stricter for auth endpoints
app.use('/auth', rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 5,               // 5 attempts
}));
```

## Error Handling

### Don't Leak Information

```javascript
// Bad: Exposes internals
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,
    query: err.sql,
  });
});

// Good: Generic message, log details
app.use((err, req, res, next) => {
  console.error('Error:', err);  // Log full error
  res.status(500).json({
    error: 'An unexpected error occurred',
    requestId: req.id,  // For support reference
  });
});
```

## Dependency Security

```bash
# Check for vulnerabilities
npm audit
pip install safety && safety check

# Keep dependencies updated
npm update
npm outdated

# Use lockfiles
npm ci  # Install from lock file
```

## Security Headers

```javascript
const helmet = require('helmet');
app.use(helmet());

// Sets:
// - X-Content-Type-Options: nosniff
// - X-Frame-Options: DENY
// - X-XSS-Protection: 1; mode=block
// - Strict-Transport-Security (HSTS)
// - And more...
```

## Logging for Security

### Log Security Events

```javascript
// Log authentication attempts
logger.info('Login attempt', { email, success: true, ip: req.ip });
logger.warn('Failed login', { email, attempts: failedCount, ip: req.ip });

// Log authorization failures
logger.warn('Unauthorized access attempt', {
  userId: req.user.id,
  resource: req.path,
  ip: req.ip,
});
```

### Never Log Sensitive Data

```javascript
// Bad
logger.info('User created', { user });  // May include password

// Good
logger.info('User created', { userId: user.id, email: user.email });
```
