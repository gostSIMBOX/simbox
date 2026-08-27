# ADR-006: RESTful Design for HTTP API

**Status**: Accepted  
**Date**: 2026-03-04  
**Type**: Architectural Decision  
**Source**: `/legacy` reverse engineering

## Context

The application exposes HTTP API for:
- SIM-Bank CRUD operations
- Slot status queries
- Remote control (power, USSD)
- System monitoring

We need to decide on API design approach to balance:
- Ease of use (intuitive endpoints)
- Standardization (industry conventions)
- Flexibility (future extensibility)
- Client compatibility (various consumers)

### Requirements

- Support CRUD operations for SIM-banks
- Provide real-time status queries
- Enable remote control operations
- Return consistent response format
- Support filtering and pagination

### Constraints

- Go application with Gin framework
- JSON request/response
- RESTful conventions available
- Multiple endpoint types (CRUD, actions, queries)

## Decision

**Use RESTful design with standard HTTP methods, resource-based URLs, and consistent response format.**

### Implementation

**Framework**: Gin  
**Response Format**: `{success: bool, data/message: ...}`  
**Error Format**: `{error: string}`

### API Endpoints

#### SIM-Bank CRUD (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/simbanks` | List all SIM-banks |
| GET | `/simbanks/:id` | Get SIM-bank details |
| POST | `/simbanks` | Create SIM-bank |
| PUT | `/simbanks/:id` | Update SIM-bank |
| DELETE | `/simbanks/:id` | Delete SIM-bank |

#### Operations (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/simbanks/:id/status` | Get real-time device status |
| POST | `/simbanks/:id/slots/:slot_id/power` | Control slot power |
| POST | `/simbanks/:id/slots/:slot_id/ussd` | Send USSD command |
| GET | `/simbanks/:id/slots` | Get slots with filtering |

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     HTTP API Layer                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Gin Router                                      │   │
│  │  - Middleware (logging, recovery)                │   │
│  │  - Route matching                                │   │
│  └──────────────────────────────────────────────────┘   │
│                       │                                  │
│                       ▼                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Handlers (SimBankHandler)                       │   │
│  │  - Request validation (Gin binding)              │   │
│  │  - Delegate to Manager                           │   │
│  │  - Format response                               │   │
│  └──────────────────────────────────────────────────┘   │
│                       │                                  │
│                       ▼                                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Business Logic (simbank.Manager)                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Response Format

**Success with data**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Bank-1",
    "type": "SMB128",
    "url": "http://192.168.1.100:8080"
  }
}
```

**Success with message**:
```json
{
  "success": true,
  "message": "Slot power updated successfully"
}
```

**Error**:
```json
{
  "error": "SimBank not found"
}
```

### HTTP Status Codes

| Code | Use Case |
|------|----------|
| 200 | Success |
| 201 | Created (POST success) |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rationale

**RESTful design was chosen because:**

1. **Industry standard**: Widely understood pattern
2. **Tooling support**: Swagger/OpenAPI, client generators
3. **HTTP semantics**: Leverage standard methods (GET/POST/PUT/DELETE)
4. **Resource-oriented**: Intuitive URL structure
5. **Gin support**: Framework designed for REST APIs

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **RPC-style** | Explicit actions, versioning | Less discoverable, custom conventions | REST is more standard |
| **GraphQL** | Flexible queries, single endpoint | Complexity, overkill for CRUD | REST sufficient for current needs |
| **gRPC-Web** | Type-safe, streaming | Browser support, complexity | REST has broader client support |
| **Custom API** | Full control | Reinventing, learning curve | REST has ecosystem benefits |

## Consequences

### Positive

- **Intuitive**: Standard patterns developers understand
- **Discoverable**: Resource URLs are self-documenting
- **Cacheable**: GET requests can be cached
- **Stateless**: Each request is independent
- **Consistent**: Uniform response format

### Negative

- **Verbosity**: Multiple endpoints for operations
- **Over-fetching**: GET returns full resource
- **Action semantics**: POST for actions less explicit than RPC
- **Versioning**: Need strategy for API evolution

### Mitigation Strategies

1. **Filtering**: Query params reduce over-fetching (`?is_active=true`)
2. **Versioning**: Add `/api/v1/` prefix when needed
3. **Documentation**: OpenAPI/Swagger for API docs
4. **Consistent errors**: Standard error response format

## Endpoint Specifications

### List SIM-Banks

```http
GET /simbanks?is_active=true HTTP/1.1
```

**Query Parameters**:
- `is_active` (optional): Filter by active status

**Response (200)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Bank-1",
      "type": "SMB128",
      "url": "http://192.168.1.100:8080",
      "is_active": true,
      "slots": [...]
    }
  ]
}
```

### Create SIM-Bank

```http
POST /simbanks HTTP/1.1
Content-Type: application/json

{
  "name": "Bank-1",
  "type": "SMB128",
  "url": "http://192.168.1.100:8080"
}
```

**Response (201)**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Bank-1",
    "type": "SMB128",
    "url": "http://192.168.1.100:8080"
  }
}
```

### Control Slot Power

```http
POST /simbanks/1/slots/5/power HTTP/1.1
Content-Type: application/json

{
  "power": true
}
```

**Response (200)**:
```json
{
  "success": true,
  "message": "Slot power updated successfully"
}
```

### Send USSD Command

```http
POST /simbanks/1/slots/3/ussd HTTP/1.1
Content-Type: application/json

{
  "command": "*100#"
}
```

**Response (200)**:
```json
{
  "success": true,
  "response": "Balance: $10.50"
}
```

## Error Handling

### Validation Errors (400)

```json
{
  "error": "Invalid request data"
}
```

### Not Found (404)

```json
{
  "error": "SimBank not found"
}
```

### Internal Error (500)

```json
{
  "error": "Failed to get simbanks"
}
```

## Compliance

**Compliant Flows**:
- `flows/sdd-api-handlers/01-requirements.md` - API endpoint specifications

**Handler Pattern**:
```go
func (h *SimBankHandler) GetSimBanks(c *gin.Context) {
    // Query with filtering
    query := database.DB.Preload("Slots")
    if isActive := c.Query("is_active"); isActive != "" {
        query = query.Where("is_active = ?", isActive == "true")
    }
    
    // Execute query
    var simBanks []database.SimBank
    query.Find(&simBanks)
    
    // Consistent response
    c.JSON(http.StatusOK, gin.H{
        "success": true,
        "data": simBanks,
    })
}
```

## Notes

**Future considerations**:
- API versioning (`/api/v1/`, `/api/v2/`)
- Pagination for list endpoints
- HATEOAS for discoverability
- OpenAPI/Swagger documentation

**Security considerations** (not yet implemented):
- Authentication (JWT/OAuth2)
- Rate limiting
- Input sanitization
- CORS configuration

---

*Generated by /legacy reverse engineering - DRAFT for review*
