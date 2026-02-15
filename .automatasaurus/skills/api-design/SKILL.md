---
name: api-design
description: REST API design conventions, error handling, and versioning. Use when designing new APIs, reviewing endpoints, or documenting API contracts.
---

# API Design Standards

Guidelines for designing consistent, intuitive, and maintainable APIs.

## REST Principles

### Resource-Oriented URLs

```
# Good: Nouns representing resources
GET    /users
GET    /users/123
POST   /users
PUT    /users/123
DELETE /users/123

# Bad: Verbs/actions in URLs
GET    /getUsers
POST   /createUser
POST   /users/123/delete
```

### Nested Resources

```
# Child resources under parent
GET    /users/123/posts          # Posts by user 123
GET    /users/123/posts/456      # Specific post
POST   /users/123/posts          # Create post for user

# Avoid deep nesting (max 2 levels)
# Bad: /users/123/posts/456/comments/789/likes
# Good: /comments/789/likes
```

## HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource(s) | Yes | Yes |
| POST | Create new resource | No | No |
| PUT | Replace entire resource | Yes | No |
| PATCH | Partial update | Yes | No |
| DELETE | Remove resource | Yes | No |

### Method Semantics

```javascript
// GET - Never modify state
app.get('/users/:id', (req, res) => {
  const user = users.find(req.params.id);
  res.json(user);
});

// POST - Create, return 201 with Location
app.post('/users', (req, res) => {
  const user = users.create(req.body);
  res.status(201)
     .location(`/users/${user.id}`)
     .json(user);
});

// PUT - Full replacement
app.put('/users/:id', (req, res) => {
  const user = users.replace(req.params.id, req.body);
  res.json(user);
});

// PATCH - Partial update
app.patch('/users/:id', (req, res) => {
  const user = users.update(req.params.id, req.body);
  res.json(user);
});

// DELETE - Remove, return 204
app.delete('/users/:id', (req, res) => {
  users.delete(req.params.id);
  res.status(204).send();
});
```

## Status Codes

### Success (2xx)

| Code | When to Use |
|------|-------------|
| 200 OK | Successful GET, PUT, PATCH |
| 201 Created | Successful POST that creates resource |
| 204 No Content | Successful DELETE, or update with no body |

### Client Errors (4xx)

| Code | When to Use |
|------|-------------|
| 400 Bad Request | Malformed request, validation error |
| 401 Unauthorized | Missing or invalid authentication |
| 403 Forbidden | Authenticated but not authorized |
| 404 Not Found | Resource doesn't exist |
| 409 Conflict | State conflict (duplicate, version mismatch) |
| 422 Unprocessable | Valid syntax, but semantic errors |
| 429 Too Many Requests | Rate limited |

### Server Errors (5xx)

| Code | When to Use |
|------|-------------|
| 500 Internal Error | Unexpected server error |
| 502 Bad Gateway | Upstream service error |
| 503 Service Unavailable | Temporarily overloaded |

## Request/Response Format

### Consistent JSON Structure

```javascript
// Single resource
{
  "id": "123",
  "name": "Alice",
  "email": "alice@example.com",
  "createdAt": "2024-01-15T10:30:00Z"
}

// Collection
{
  "data": [
    { "id": "123", "name": "Alice" },
    { "id": "456", "name": "Bob" }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "perPage": 20
  }
}
```

### Naming Conventions

```javascript
// Use camelCase for JSON properties
{
  "userId": 123,
  "firstName": "Alice",
  "createdAt": "2024-01-15T10:30:00Z"
}

// Use ISO 8601 for dates
"2024-01-15T10:30:00Z"

// Use consistent ID format
"id": "550e8400-e29b-41d4-a716-446655440000"  // UUID
"id": 12345                                     // Integer
```

## Error Responses

### Standard Error Format

```javascript
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      },
      {
        "field": "age",
        "message": "Must be at least 18"
      }
    ],
    "requestId": "req-abc123"
  }
}
```

### Error Codes

Use consistent, machine-readable error codes:

```javascript
const ErrorCodes = {
  VALIDATION_ERROR: 'Validation failed',
  NOT_FOUND: 'Resource not found',
  UNAUTHORIZED: 'Authentication required',
  FORBIDDEN: 'Permission denied',
  CONFLICT: 'Resource conflict',
  RATE_LIMITED: 'Too many requests',
  INTERNAL_ERROR: 'Internal server error',
};
```

## Pagination

### Cursor-Based (Preferred)

```javascript
// Request
GET /posts?limit=20&cursor=abc123

// Response
{
  "data": [...],
  "meta": {
    "hasMore": true,
    "nextCursor": "def456"
  }
}
```

### Offset-Based (Simpler)

```javascript
// Request
GET /posts?page=2&perPage=20

// Response
{
  "data": [...],
  "meta": {
    "total": 150,
    "page": 2,
    "perPage": 20,
    "totalPages": 8
  }
}
```

## Filtering & Sorting

### Query Parameters

```bash
# Filtering
GET /users?status=active
GET /users?role=admin&status=active
GET /posts?createdAfter=2024-01-01

# Sorting
GET /users?sort=name           # Ascending
GET /users?sort=-createdAt     # Descending (prefix with -)
GET /users?sort=lastName,firstName  # Multiple fields

# Field selection
GET /users?fields=id,name,email
```

### Search

```bash
# Simple search
GET /users?q=alice

# Field-specific search
GET /users?email=*@example.com
```

## Versioning

### URL Path Versioning (Recommended)

```
GET /v1/users
GET /v2/users
```

### Header Versioning (Alternative)

```
GET /users
Accept: application/vnd.api+json; version=2
```

### Version Lifecycle

1. **Active**: Current recommended version
2. **Deprecated**: Still works, migration encouraged
3. **Sunset**: End-of-life announced, will be removed

```http
# Deprecation headers
Deprecation: true
Sunset: Sat, 01 Jun 2025 00:00:00 GMT
Link: </v2/users>; rel="successor-version"
```

## Authentication

### Bearer Token

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### API Key

```http
# Header (preferred)
X-API-Key: sk_live_abc123

# Query param (less secure, use for read-only)
GET /data?api_key=sk_live_abc123
```

## Rate Limiting

### Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
Retry-After: 60
```

### Response When Limited

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "retryAfter": 60
  }
}
```

## HATEOAS (Optional)

Include links for discoverability:

```json
{
  "id": "123",
  "name": "Alice",
  "_links": {
    "self": { "href": "/users/123" },
    "posts": { "href": "/users/123/posts" },
    "avatar": { "href": "/users/123/avatar" }
  }
}
```

## Documentation

### OpenAPI/Swagger

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List all users
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive]
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### Include Examples

```yaml
examples:
  userExample:
    value:
      id: "123"
      name: "Alice"
      email: "alice@example.com"
```

## Common Patterns

### Bulk Operations

```javascript
// Bulk create
POST /users/bulk
{
  "users": [
    { "name": "Alice" },
    { "name": "Bob" }
  ]
}

// Bulk update
PATCH /users/bulk
{
  "updates": [
    { "id": "123", "status": "active" },
    { "id": "456", "status": "inactive" }
  ]
}
```

### Long-Running Operations

```javascript
// Start operation, return 202 Accepted
POST /reports/generate
{
  "type": "annual"
}

// Response
{
  "operationId": "op-123",
  "status": "pending",
  "_links": {
    "status": { "href": "/operations/op-123" }
  }
}

// Poll for status
GET /operations/op-123
{
  "status": "complete",
  "result": { "href": "/reports/2024-annual.pdf" }
}
```

### Webhooks

```javascript
// Register webhook
POST /webhooks
{
  "url": "https://example.com/hooks",
  "events": ["user.created", "user.deleted"]
}

// Webhook payload
{
  "event": "user.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": "123",
    "name": "Alice"
  }
}
```
