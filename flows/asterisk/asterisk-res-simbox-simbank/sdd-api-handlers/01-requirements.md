# API Handlers - Requirements & Specifications

> Spec-Driven Development: API handlers domain.

## Overview

**Domain**: API Handlers  
**Type**: SDD (Spec-Driven Development)  
**Status**: DRAFT (Legacy Analysis Generated)  
**Generated**: 2026-03-04  
**Source**: `/legacy` reverse engineering

## Requirements

### Business Requirements

**BR-1: SIM-Bank CRUD**

The system SHALL provide CRUD operations for SIM-bank devices.

**Rationale**: Operators need to register, configure, and manage devices.

**BR-2: Slot Status Queries**

The system SHALL provide queries for slot status.

**Rationale**: Operators need visibility into individual SIM slots.

**BR-3: Remote Control**

The system SHALL provide remote control of slot power.

**Rationale**: Remote reset of SIM cards without physical access.

**BR-4: USSD Commands**

The system SHALL support USSD command execution.

**Rationale**: Balance checks, tariff changes, network operations.

### Technical Requirements

**TR-1: RESTful Design**

API SHALL follow RESTful conventions.

**TR-2: Consistent Response Format**

All responses SHALL use consistent format.

**Format**: `{success: bool, data/message: ...}`

**TR-3: Query Filtering**

List endpoints SHALL support query parameter filtering.

**TR-4: Error Handling**

API SHALL return appropriate HTTP status codes.

### Non-Functional Requirements

**NFR-1: Response Format**

All responses SHALL be JSON.

**NFR-2: Validation**

Request data SHALL be validated.

**NFR-3: Logging**

Write operations SHALL be logged.

## Specifications

### Handler Structure

**Package**: `internal/api/handlers`

**SimBankHandler**:
```go
type SimBankHandler struct {
    manager *simbank.Manager
}

func NewSimBankHandler(manager *simbank.Manager) *SimBankHandler
```

### Endpoints (9 Total)

#### SIM-Bank CRUD (5 endpoints)

**1. GET /simbanks** - List all SIM-banks

Query Parameters:
- `is_active` (optional): Filter by active status

Response (200):
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Bank-1", "type": "SMB128", ...}
  ]
}
```

**2. GET /simbanks/:id** - Get SIM-bank details

Path Parameters:
- `id`: SIM-bank ID

Response (200):
```json
{
  "success": true,
  "data": {"id": 1, "name": "Bank-1", ...}
}
```

Errors:
- 404: SimBank not found

**3. POST /simbanks** - Create SIM-bank

Body:
```json
{
  "name": "Bank-1",
  "type": "SMB128",
  "url": "http://192.168.1.100:8080"
}
```

Response (201):
```json
{
  "success": true,
  "data": {"id": 1, "name": "Bank-1", ...}
}
```

**4. PUT /simbanks/:id** - Update SIM-bank

Path Parameters:
- `id`: SIM-bank ID

Body (partial update):
```json
{
  "name": "Updated Name",
  "is_active": true
}
```

Response (200):
```json
{
  "success": true,
  "data": {"id": 1, "name": "Updated Name", ...}
}
```

**5. DELETE /simbanks/:id** - Delete SIM-bank

Path Parameters:
- `id`: SIM-bank ID

Response (200):
```json
{
  "success": true,
  "message": "SimBank deleted successfully"
}
```

#### Operations (4 endpoints)

**6. GET /simbanks/:id/status** - Get real-time device status

Path Parameters:
- `id`: SIM-bank ID

Response (200):
```json
{
  "success": true,
  "data": {
    "status": "online",
    "slots": [...]
  }
}
```

**7. POST /simbanks/:id/slots/:slot_id/power** - Control slot power

Path Parameters:
- `id`: SIM-bank ID
- `slot_id`: Slot number

Body:
```json
{
  "power": true
}
```

Response (200):
```json
{
  "success": true,
  "message": "Slot power updated successfully"
}
```

**8. POST /simbanks/:id/slots/:slot_id/ussd** - Send USSD command

Path Parameters:
- `id`: SIM-bank ID
- `slot_id`: Slot number

Body:
```json
{
  "command": "*100#"
}
```

Response (200):
```json
{
  "success": true,
  "response": "Balance: $10.50"
}
```

**9. GET /simbanks/:id/slots** - Get slots

Path Parameters:
- `id`: SIM-bank ID

Query Parameters:
- `status` (optional): Filter by status
- `is_active` (optional): Filter by active status

Response (200):
```json
{
  "success": true,
  "data": [
    {"id": 1, "slot_id": 1, "imsi": "...", "status": "online", ...}
  ]
}
```

### Response Format

**Success Responses**:
```json
{
  "success": true,
  "data": { ... }
}
```

or

```json
{
  "success": true,
  "message": "Operation completed"
}
```

**Error Responses**:
```json
{
  "error": "Error description"
}
```

### HTTP Status Codes

| Code | Use Case |
|------|----------|
| 200 | Success |
| 201 | Created |
| 400 | Invalid request / Bad input |
| 404 | Resource not found |
| 500 | Internal server error |

### Validation

**Gin Binding**:
```go
var request struct {
    Command string `json:"command" binding:"required"`
}

if err := c.ShouldBindJSON(&request); err != nil {
    c.JSON(http.StatusBadRequest, gin.H{
        "error": "Invalid request data",
    })
    return
}
```

### Error Handling Pattern

```go
// Invalid input
c.JSON(http.StatusBadRequest, gin.H{
    "error": "Invalid simbank ID",
})

// Not found
c.JSON(http.StatusNotFound, gin.H{
    "error": "SimBank not found",
})

// Internal error
logger.Logger.Errorf("Failed to get simbanks: %v", err)
c.JSON(http.StatusInternalServerError, gin.H{
    "error": "Failed to get simbanks",
})
```

### Logging

**Write Operations**:
```go
logger.Logger.Infof("Created SimBank: %s (ID: %d)", simBank.Name, simBank.ID)
logger.Logger.Infof("Updated SimBank: %s (ID: %d)", simBank.Name, simBank.ID)
logger.Logger.Infof("Deleted SimBank: %s (ID: %d)", simBank.Name, simBank.ID)
```

**Error Logging**:
```go
logger.Logger.Errorf("Failed to get simbanks: %v", err)
logger.Logger.Errorf("Failed to set slot power: %v", err)
```

### Dependencies

**Uses**:
- `database.DB` - Data access
- `simbank.Manager` - Business logic
- `logger.Logger` - Logging

**Used By**:
- External API consumers (frontend, mobile, integrations)

---

*Generated by /legacy reverse engineering - DRAFT for review*
