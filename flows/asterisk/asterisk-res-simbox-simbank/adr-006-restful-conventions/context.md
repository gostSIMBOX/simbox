# ADR-006: RESTful API Conventions

**Date**: 2026-03-04  
**Status**: Accepted  
**Type**: Constraining  
**Source**: Legacy analysis via `/legacy` command

---

## Context

The application exposes a REST API for managing SIM-banks, monitoring slot status, and controlling hardware operations. The API must be consistent, predictable, and follow industry standards to enable easy integration with frontend applications, third-party systems, and automation tools.

Key requirements:
- Standard HTTP methods and status codes
- Consistent response format across all endpoints
- Resource-oriented URL structure
- Support for filtering, pagination, and sorting
- Clear error messages and error response format
- Versioning support for API evolution

---

## Decision

**Follow RESTful conventions with consistent response format and standard HTTP semantics.**

The API uses standard HTTP methods (GET, POST, PUT, DELETE), standard status codes (200, 201, 400, 404, 500), and a consistent JSON response format with `success` and `data` fields.

Implementation details:
```go
// From api/handlers/simbank.go

// Consistent response format
type Response struct {
    Success bool        `json:"success"`
    Data    interface{} `json:"data,omitempty"`
    Message string      `json:"message,omitempty"`
}

// Success response example
c.JSON(http.StatusOK, gin.H{
    "success": true,
    "data":    simBanks,
})

// Error response example
c.JSON(http.StatusBadRequest, gin.H{
    "error": "Invalid request data",
})

// Created response
c.JSON(http.StatusCreated, gin.H{
    "success": true,
    "data":    simBank,
})

// Not found response
c.JSON(http.StatusNotFound, gin.H{
    "error": "SimBank not found",
})
```

API Structure:
```
GET    /api/v1/simbanks              - List all SIM-banks
POST   /api/v1/simbanks              - Create SIM-bank
GET    /api/v1/simbanks/:id          - Get SIM-bank details
PUT    /api/v1/simbanks/:id          - Update SIM-bank
DELETE /api/v1/simbanks/:id          - Delete SIM-bank
GET    /api/v1/simbanks/:id/status   - Get SIM-bank status (real-time)
GET    /api/v1/simbanks/:id/slots    - List slots for SIM-bank
PUT    /api/v1/simbanks/:id/slots/:slot_id/power - Control slot power
POST   /api/v1/simbanks/:id/slots/:slot_id/ussd  - Send USSD command
```

HTTP Method Semantics:
- **GET**: Retrieve resources (idempotent, no side effects)
- **POST**: Create new resources or perform actions
- **PUT**: Update existing resources (idempotent)
- **DELETE**: Remove resources (idempotent)

Status Code Usage:
- **200 OK**: Successful GET, PUT requests
- **201 Created**: Successful POST (resource creation)
- **204 No Content**: Successful DELETE (optional)
- **400 Bad Request**: Invalid input, validation errors
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server-side errors

---

## Consequences

### Positive

1. **Predictability**: Developers familiar with REST can understand the API quickly
2. **Tooling support**: Standard HTTP methods work with all HTTP clients and testing tools
3. **Cacheability**: GET requests can be cached by intermediaries
4. **Idempotency**: PUT and DELETE operations are idempotent (safe to retry)
5. **Consistent errors**: Uniform error format simplifies client error handling
6. **Versioning**: `/api/v1/` prefix allows future API versions
7. **Gin integration**: Leverages Gin's routing and middleware capabilities

### Negative

1. **Verbosity**: Consistent response format adds extra JSON wrapping
2. **REST constraints**: May not fit all operations naturally (e.g., complex actions)
3. **Over-fetching**: GET /simbanks/:id always returns full resource (no field selection)
4. **Under-fetching**: May need multiple requests to get related data (solved with Preload)

### Trade-offs

| Alternative | Pros | Cons | Why Not Chosen |
|-------------|------|------|----------------|
| **RPC-style API** | Clear action semantics, flexible | Not cacheable, harder to integrate with web tools | REST better for CRUD operations |
| **GraphQL** | Flexible queries, no over/under-fetching | More complex, requires GraphQL client | Overkill for current requirements |
| **Custom format** | Full control over API design | Reinventing the wheel, learning curve | REST has industry-standard conventions |
| **No versioning** | Simpler URLs | Breaking changes require migration | `/api/v1/` allows smooth evolution |

---

## Compliance

### Requirements Met
- API consistency: All handlers use consistent response format
- Standard HTTP methods: GET/POST/PUT/DELETE semantics
- Proper status codes: 200, 201, 400, 404, 500 used appropriately
- Resource-oriented URLs: `/simbanks/:id/slots/:slot_id`

### Related SDDs
- `flows/sdd-api-handlers/01-requirements.md` - Section 2.5 API Endpoints
- `flows/sdd-api-handlers/01-requirements.md` - Section 4.1 Response Format

---

## Notes

**Legacy Analysis Addition (2026-03-04)**:  
This ADR was reverse-engineered from existing code during `/legacy` BFS analysis. All 9 API endpoints follow consistent RESTful conventions.

**Endpoints Implemented**:
1. ✅ `GET /api/v1/simbanks` - List SIM-banks (with filtering)
2. ✅ `POST /api/v1/simbanks` - Create SIM-bank
3. ✅ `GET /api/v1/simbanks/:id` - Get SIM-bank details
4. ✅ `PUT /api/v1/simbanks/:id` - Update SIM-bank
5. ✅ `DELETE /api/v1/simbanks/:id` - Delete SIM-bank
6. ✅ `GET /api/v1/simbanks/:id/status` - Get real-time status
7. ✅ `GET /api/v1/simbanks/:id/slots` - List slots (with filtering)
8. ✅ `PUT /api/v1/simbanks/:id/slots/:slot_id/power` - Control power
9. ✅ `POST /api/v1/simbanks/:id/slots/:slot_id/ussd` - Send USSD

**Response Format Examples**:

Success (List):
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "SMB-001", "type": "smb128", ...}
  ]
}
```

Success (Single):
```json
{
  "success": true,
  "data": {"id": 1, "name": "SMB-001", ...}
}
```

Error:
```json
{
  "error": "Invalid request data"
}
```

---

*Generated via /legacy analysis on 2026-03-04*
