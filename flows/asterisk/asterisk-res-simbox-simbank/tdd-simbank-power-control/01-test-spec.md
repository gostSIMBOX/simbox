# SIM-Bank Power Control — Test Specification

> **Tests-Driven Development (TDD)**  
> **Component**: Power Control for SIM Slots  
> **Status**: DRAFT  
> **Generated**: 2026-03-04

---

## Overview

This document specifies the test strategy, test cases, and testing approach for the SIM-bank power control functionality. Power control is a critical operation that manages the electrical power to individual SIM slots.

---

## Test Strategy

### Testing Pyramid

```
                    /\
                   /  \
                  / E2E \       End-to-End Tests (10%)
                 /--------\
                /    \     /    \
               /  Int \   / Int  \   Integration Tests (20%)
              /--------\ /--------\
             /    \     \     /    \
            /  Unit \    \  / Unit  \  Unit Tests (70%)
           /---------\  /  \--------\
```

### Test Distribution

| Test Type | Count | Coverage Goal | Execution Time |
|-----------|-------|---------------|----------------|
| **Unit Tests** | 50+ | 90%+ | < 100ms each |
| **Integration Tests** | 20+ | Critical paths | < 1s each |
| **E2E Tests** | 10+ | Key user journeys | < 5s each |

---

## Unit Tests

### Test File: `internal/simbank/manager_test.go`

#### 1. SetPower Function Tests

**Test Case 1.1**: Successful power on

```go
func TestSetPower_Success(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    slotID := 5
    power := true
    
    // Mock database
    mockDB.On("Model", mock.Anything).Return(&gorm.DB{})
    mockDB.On("Where", "simbank_id = ? AND slot_id = ?", simBankID, slotID).Return(&gorm.DB{})
    mockDB.On("Update", "power", power).Return(&gorm.DB{RowsAffected: 1})
    
    // Mock HTTP client
    mockHTTPClient.On("SetPower", slotID, power).Return(nil)
    
    // Act
    err := manager.SetPower(simBankID, slotID, power)
    
    // Assert
    assert.NoError(t, err)
    mockDB.AssertExpectations(t)
    mockHTTPClient.AssertExpectations(t)
}
```

**Test Case 1.2**: SIM-bank not found

```go
func TestSetPower_SimBankNotFound(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(999)  // Non-existent
    slotID := 5
    power := true
    
    // Act
    err := manager.SetPower(simBankID, slotID, power)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "simbank 999 not found")
}
```

**Test Case 1.3**: HTTP client error

```go
func TestSetPower_HTTPClientError(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    slotID := 5
    power := true
    
    // Mock database
    mockDB.On("Model", mock.Anything).Return(&gorm.DB{})
    mockDB.On("Where", mock.Anything, mock.Anything).Return(&gorm.DB{})
    mockDB.On("Update", mock.Anything, mock.Anything).Return(&gorm.DB{RowsAffected: 1})
    
    // Mock HTTP client with error
    mockHTTPClient.On("SetPower", slotID, power).Return(errors.New("connection timeout"))
    
    // Act
    err := manager.SetPower(simBankID, slotID, power)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "connection timeout")
}
```

**Test Case 1.4**: Database update error

```go
func TestSetPower_DatabaseError(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    slotID := 5
    power := true
    
    // Mock HTTP success
    mockHTTPClient.On("SetPower", slotID, power).Return(nil)
    
    // Mock database error
    mockDB.On("Model", mock.Anything).Return(&gorm.DB{})
    mockDB.On("Where", mock.Anything, mock.Anything).Return(&gorm.DB{})
    mockDB.On("Update", mock.Anything, mock.Anything).Return(&gorm.DB{Error: errors.New("connection lost")})
    
    // Act
    err := manager.SetPower(simBankID, slotID, power)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "connection lost")
}
```

**Test Case 1.5**: Concurrent power control (thread safety)

```go
func TestSetPower_Concurrent(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    slotID := 5
    
    // Act - Run 100 concurrent power operations
    var wg sync.WaitGroup
    errors := make(chan error, 100)
    
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(power bool) {
            defer wg.Done()
            err := manager.SetPower(simBankID, slotID, power)
            if err != nil {
                errors <- err
            }
        }(i%2 == 0)
    }
    
    wg.Wait()
    close(errors)
    
    // Assert - No race conditions or errors
    assert.Empty(t, errors)
}
```

---

#### 2. Power State Validation Tests

**Test Case 2.1**: Validate power state transition (OFF → ON)

```go
func TestPowerStateTransition_OffToOn(t *testing.T) {
    // Arrange
    slot := &database.SimSlot{
        ID:        1,
        SimBankID: 1,
        SlotID:    5,
        Power:     false,  // Currently OFF
        Status:    "offline",
    }
    
    // Act
    newState := transitionPowerState(slot, true)
    
    // Assert
    assert.True(t, newState.Power)
    assert.Equal(t, "online", newState.Status)
}
```

**Test Case 2.2**: Validate power state transition (ON → OFF)

```go
func TestPowerStateTransition_OnToOff(t *testing.T) {
    // Arrange
    slot := &database.SimSlot{
        ID:        1,
        SimBankID: 1,
        SlotID:    5,
        Power:     true,  // Currently ON
        Status:    "online",
    }
    
    // Act
    newState := transitionPowerState(slot, false)
    
    // Assert
    assert.False(t, newState.Power)
    assert.Equal(t, "offline", newState.Status)
}
```

**Test Case 2.3**: Same state transition (no-op)

```go
func TestPowerStateTransition_SameState(t *testing.T) {
    // Arrange
    slot := &database.SimSlot{
        ID:        1,
        SimBankID: 1,
        SlotID:    5,
        Power:     true,
        Status:    "online",
    }
    
    // Act - Try to power ON when already ON
    newState := transitionPowerState(slot, true)
    
    // Assert
    assert.True(t, newState.Power)
    assert.Equal(t, "online", newState.Status)
    // Should not make unnecessary hardware calls
}
```

---

#### 3. Power Control Debounce Tests

**Test Case 3.1**: Rapid power toggling prevention

```go
func TestPowerControl_Debounce(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    slotID := 5
    
    // Set debounce period to 100ms for testing
    manager.SetDebouncePeriod(100 * time.Millisecond)
    
    // Act - Rapid toggling
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(power bool) {
            defer wg.Done()
            manager.SetPower(simBankID, slotID, power)
        }(i%2 == 0)
    }
    
    wg.Wait()
    
    // Assert - Should only execute 2 operations (last state of each transition)
    assert.LessOrEqual(t, mockHTTPClient.CallCount, 2)
}
```

---

### Test File: `internal/api/handlers/simbank_test.go`

#### 4. HTTP Handler Tests

**Test Case 4.1**: Valid power control request

```go
func TestSetSlotPower_ValidRequest(t *testing.T) {
    // Arrange
    router := setupTestRouter()
    mockManager := new(MockManager)
    
    mockManager.On("SetPower", uint(1), 5, true).Return(nil)
    
    reqBody := `{"power": true}`
    req := httptest.NewRequest("PUT", "/api/v1/simbanks/1/slots/5/power", 
                                strings.NewReader(reqBody))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    
    // Act
    router.ServeHTTP(w, req)
    
    // Assert
    assert.Equal(t, http.StatusOK, w.Code)
    assert.Contains(t, w.Body.String(), "Slot power updated successfully")
    mockManager.AssertExpectations(t)
}
```

**Test Case 4.2**: Invalid simbank ID

```go
func TestSetSlotPower_InvalidSimBankID(t *testing.T) {
    // Arrange
    router := setupTestRouter()
    
    reqBody := `{"power": true}`
    req := httptest.NewRequest("PUT", "/api/v1/simbanks/invalid/slots/5/power", 
                                strings.NewReader(reqBody))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    
    // Act
    router.ServeHTTP(w, req)
    
    // Assert
    assert.Equal(t, http.StatusBadRequest, w.Code)
    assert.Contains(t, w.Body.String(), "Invalid simbank ID")
}
```

**Test Case 4.3**: Invalid slot ID

```go
func TestSetSlotPower_InvalidSlotID(t *testing.T) {
    // Arrange
    router := setupTestRouter()
    
    reqBody := `{"power": true}`
    req := httptest.NewRequest("PUT", "/api/v1/simbanks/1/slots/invalid/power", 
                                strings.NewReader(reqBody))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    
    // Act
    router.ServeHTTP(w, req)
    
    // Assert
    assert.Equal(t, http.StatusBadRequest, w.Code)
    assert.Contains(t, w.Body.String(), "Invalid slot ID")
}
```

**Test Case 4.4**: Missing power field

```go
func TestSetSlotPower_MissingPowerField(t *testing.T) {
    // Arrange
    router := setupTestRouter()
    
    reqBody := `{}`  // Missing "power" field
    req := httptest.NewRequest("PUT", "/api/v1/simbanks/1/slots/5/power", 
                                strings.NewReader(reqBody))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    
    // Act
    router.ServeHTTP(w, req)
    
    // Assert
    assert.Equal(t, http.StatusBadRequest, w.Code)
    assert.Contains(t, w.Body.String(), "Invalid request data")
}
```

**Test Case 4.5**: Invalid JSON body

```go
func TestSetSlotPower_InvalidJSON(t *testing.T) {
    // Arrange
    router := setupTestRouter()
    
    reqBody := `{invalid json}`
    req := httptest.NewRequest("PUT", "/api/v1/simbanks/1/slots/5/power", 
                                strings.NewReader(reqBody))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    
    // Act
    router.ServeHTTP(w, req)
    
    // Assert
    assert.Equal(t, http.StatusBadRequest, w.Code)
}
```

---

### Test File: `internal/simbank/client_test.go`

#### 5. HTTP Client Tests

**Test Case 5.1**: Successful power control HTTP request

```go
func TestClient_SetPower_Success(t *testing.T) {
    // Arrange
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        assert.Equal(t, "/slot/power", r.URL.Path)
        assert.Equal(t, "POST", r.Method)
        
        var req PowerRequest
        err := json.NewDecoder(r.Body).Decode(&req)
        assert.NoError(t, err)
        assert.Equal(t, 5, req.SlotID)
        assert.Equal(t, true, req.Power)
        
        w.WriteHeader(http.StatusOK)
    }))
    defer server.Close()
    
    client := NewClient(server.URL, 5*time.Second)
    
    // Act
    err := client.SetPower(5, true)
    
    // Assert
    assert.NoError(t, err)
}
```

**Test Case 5.2**: HTTP timeout

```go
func TestClient_SetPower_Timeout(t *testing.T) {
    // Arrange
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        time.Sleep(2 * time.Second)  // Simulate slow response
        w.WriteHeader(http.StatusOK)
    }))
    defer server.Close()
    
    client := NewClient(server.URL, 100*time.Millisecond)  // 100ms timeout
    
    // Act
    err := client.SetPower(5, true)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "timeout")
}
```

**Test Case 5.3**: HTTP error response

```go
func TestClient_SetPower_ErrorResponse(t *testing.T) {
    // Arrange
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusInternalServerError)
        w.Write([]byte(`{"error": "Internal server error"}`))
    }))
    defer server.Close()
    
    client := NewClient(server.URL, 5*time.Second)
    
    // Act
    err := client.SetPower(5, true)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "500")
}
```

---

## Integration Tests

### Test File: `tests/integration/power_control_test.go`

#### 6. End-to-End Power Control Flow

**Test Case 6.1**: Complete power control flow

```go
func TestIntegration_PowerControlFlow(t *testing.T) {
    // Arrange - Full system setup
    cfg := loadTestConfig()
    db := setupTestDatabase(cfg.Database)
    defer db.Close()
    
    // Create test SIM-bank
    simBank := database.SimBank{
        Name: "Test Bank",
        Type: "smb128",
        URL:  mockHardwareURL,
    }
    db.Create(&simBank)
    
    // Create test slot
    slot := database.SimSlot{
        SimBankID: simBank.ID,
        SlotID:    5,
        Power:     false,
        Status:    "offline",
    }
    db.Create(&slot)
    
    manager := simbank.NewManager(cfg.SimBank)
    defer manager.Stop()
    
    // Act - Power on slot
    err := manager.SetPower(simBank.ID, slot.SlotID, true)
    
    // Assert
    assert.NoError(t, err)
    
    // Verify database state
    var updatedSlot database.SimSlot
    db.First(&updatedSlot, slot.ID)
    assert.True(t, updatedSlot.Power)
    assert.Equal(t, "online", updatedSlot.Status)
    
    // Verify system event logged
    var event database.SystemEvent
    db.Where("type = ? AND source = ?", "info", "simbank").First(&event)
    assert.NotEmpty(t, event.ID)
}
```

#### 7. Concurrent Access Tests

**Test Case 7.1**: Multiple users controlling same slot

```go
func TestIntegration_ConcurrentPowerControl(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    slotID := 5
    
    // Act - 10 concurrent users trying to control same slot
    var wg sync.WaitGroup
    results := make(chan error, 10)
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(power bool) {
            defer wg.Done()
            err := manager.SetPower(simBankID, slotID, power)
            results <- err
        }(i%2 == 0)
    }
    
    wg.Wait()
    close(results)
    
    // Assert - All operations complete without data corruption
    errorCount := 0
    for err := range results {
        if err != nil {
            errorCount++
        }
    }
    assert.Equal(t, 0, errorCount)
}
```

---

## Edge Case Tests

### Test File: `internal/simbank/edge_cases_test.go`

#### 8. Boundary Conditions

**Test Case 8.1**: Slot ID boundary (0)

```go
func TestEdgeCase_SlotIDZero(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    
    // Act
    err := manager.SetPower(1, 0, true)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "invalid slot ID")
}
```

**Test Case 8.2**: Slot ID boundary (max)

```go
func TestEdgeCase_SlotIDMax(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    
    // Act - SMB128 has 128 slots (1-128)
    err := manager.SetPower(1, 129, true)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "slot ID out of range")
}
```

**Test Case 8.3**: Negative slot ID

```go
func TestEdgeCase_NegativeSlotID(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    
    // Act
    err := manager.SetPower(1, -1, true)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "invalid slot ID")
}
```

---

#### 9. Hardware Failure Scenarios

**Test Case 9.1**: SIM-bank unreachable

```go
func TestEdgeCase_SimBankUnreachable(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    simBankID := uint(1)
    
    // Mock unreachable hardware
    mockHTTPClient.On("SetPower", mock.Anything, mock.Anything).
        Return(errors.New("connection refused"))
    
    // Act
    err := manager.SetPower(simBankID, 5, true)
    
    // Assert
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "connection refused")
    
    // Verify event logged
    assertSystemEventLogged(t, "error", "simbank", "Failed to set power")
}
```

**Test Case 9.2**: Partial failure (some slots fail)

```go
func TestEdgeCase_PartialFailure(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    
    // Mock: slots 1-5 succeed, slot 6 fails
    mockHTTPClient.On("SetPower", mock.MatchedBy(func(id int) bool { return id <= 5 }), true).Return(nil)
    mockHTTPClient.On("SetPower", 6, true).Return(errors.New("slot malfunction"))
    
    // Act
    var wg sync.WaitGroup
    for i := 1; i <= 6; i++ {
        wg.Add(1)
        go func(slotID int) {
            defer wg.Done()
            manager.SetPower(1, slotID, true)
        }(i)
    }
    wg.Wait()
    
    // Assert - 5 success, 1 failure
    assert.Equal(t, 5, mockHTTPClient.SuccessCount)
    assert.Equal(t, 1, mockHTTPClient.FailureCount)
}
```

---

#### 10. State Consistency Tests

**Test Case 10.1**: Database and hardware state mismatch

```go
func TestEdgeCase_StateMismatch(t *testing.T) {
    // Arrange
    // Database says ON, hardware says OFF
    
    // Act - Try to power ON (should detect no change needed)
    err := manager.SetPower(1, 5, true)
    
    // Assert
    // Should skip hardware call since DB state matches requested state
    assert.NoError(t, err)
    mockHTTPClient.AssertNotCalled(t, "SetPower")
}
```

---

## Performance Tests

### Test File: `tests/performance/power_control_test.go`

#### 11. Load Tests

**Test Case 11.1**: High concurrent load

```go
func TestPerformance_HighConcurrentLoad(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    concurrency := 1000
    operations := 10000
    
    // Act
    start := time.Now()
    var wg sync.WaitGroup
    errors := make(chan error, operations)
    
    for i := 0; i < operations; i++ {
        wg.Add(1)
        go func(simBankID uint, slotID int) {
            defer wg.Done()
            err := manager.SetPower(simBankID, slotID, true)
            if err != nil {
                errors <- err
            }
        }(uint(i%10+1), i%128+1)
    }
    
    wg.Wait()
    close(errors)
    duration := time.Since(start)
    
    // Assert
    assert.Empty(t, errors)
    assert.Less(t, duration, 30*time.Second)  // Target: < 30s for 10k operations
    t.Logf("Throughput: %.2f ops/sec", float64(operations)/duration.Seconds())
}
```

---

#### 12. Stress Tests

**Test Case 12.1**: Memory leak detection

```go
func TestPerformance_MemoryLeak(t *testing.T) {
    // Arrange
    manager := setupTestManager()
    var m1, m2 runtime.MemStats
    
    // Act - 100,000 operations
    for i := 0; i < 100000; i++ {
        manager.SetPower(1, i%128+1, i%2 == 0)
        
        if i%10000 == 0 {
            runtime.GC()
            runtime.ReadMemStats(&m1)
            t.Logf("Iteration %d: Alloc=%d KB", i, m1.Alloc/1024)
        }
    }
    
    runtime.GC()
    runtime.ReadMemStats(&m2)
    
    // Assert - Memory should not grow significantly
    growth := float64(m2.Alloc-m1.Alloc) / float64(m1.Alloc) * 100
    assert.Less(t, growth, 10.0)  // Less than 10% growth
}
```

---

## Test Data

### Fixtures

```go
// fixtures/simbank.go

// TestSimBank creates a test SIM-bank
func TestSimBank() database.SimBank {
    return database.SimBank{
        Name:     "Test Bank",
        Type:     "smb128",
        URL:      "http://localhost:8080",
        IsActive: true,
    }
}

// TestSimSlot creates a test SIM slot
func TestSimSlot(simBankID uint, slotID int) database.SimSlot {
    return database.SimSlot{
        SimBankID: simBankID,
        SlotID:    slotID,
        IMSI:      fmt.Sprintf("460001234567%03d", slotID),
        ICCID:     fmt.Sprintf("8986001234567890%03d", slotID),
        Operator:  "MTS",
        Status:    "offline",
        Power:     false,
        Signal:    0,
    }
}

// TestConfig creates test configuration
func TestConfig() *config.Config {
    return &config.Config{
        SimBank: config.SimBankConfig{
            PollingInterval: 30 * time.Second,
            Timeout:         5 * time.Second,
            RetryAttempts:   3,
            RetryDelay:      1 * time.Second,
        },
    }
}
```

---

## Mock Implementations

### Mock HTTP Client

```go
// mocks/http_client.go

type MockHTTPClient struct {
    mock.Mock
    CallCount     int
    SuccessCount  int
    FailureCount  int
}

func (m *MockHTTPClient) SetPower(slotID int, power bool) error {
    m.CallCount++
    
    args := m.Called(slotID, power)
    err := args.Error(0)
    
    if err == nil {
        m.SuccessCount++
    } else {
        m.FailureCount++
    }
    
    return err
}

func (m *MockHTTPClient) GetStatus() (*StatusResponse, error) {
    args := m.Called()
    return args.Get(0).(*StatusResponse), args.Error(1)
}
```

### Mock Database

```go
// mocks/database.go

type MockDB struct {
    mock.Mock
}

func (m *MockDB) Model(value interface{}) *gorm.DB {
    args := m.Called(value)
    return args.Get(0).(*gorm.DB)
}

func (m *MockDB) Where(query interface{}, args ...interface{}) *gorm.DB {
    args := m.Called(query, args)
    return args.Get(0).(*gorm.DB)
}

func (m *MockDB) Update(column string, value interface{}) *gorm.DB {
    args := m.Called(column, value)
    return args.Get(0).(*gorm.DB)
}
```

---

## Test Execution

### Running Tests

```bash
# Run all tests
go test ./...

# Run power control tests only
go test ./internal/simbank -run TestSetPower

# Run with coverage
go test ./... -coverprofile=coverage.out

# Run integration tests
go test ./tests/integration -tags=integration

# Run performance tests
go test ./tests/performance -tags=performance -timeout=5m

# Run with race detector
go test ./... -race
```

### Coverage Requirements

| Package | Target Coverage |
|---------|-----------------|
| `internal/simbank` | 90%+ |
| `internal/api/handlers` | 85%+ |
| `internal/database` | 80%+ |

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Go
        uses: actions/setup-go@v3
        with:
          go-version: 1.21
      
      - name: Run unit tests
        run: go test ./... -race -coverprofile=coverage.out
      
      - name: Run integration tests
        run: go test ./tests/integration -tags=integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.out
```

---

## Test Reports

### Coverage Report Example

```
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out

# Output:
internal/simbank/manager.go:     92.5%
internal/simbank/client.go:      88.3%
internal/api/handlers/simbank.go: 85.7%
internal/database/database.go:   80.2%
total:                           87.4%
```

---

## Acceptance Criteria

### Definition of Done

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Code coverage ≥ 90%
- [ ] No race conditions detected
- [ ] Performance tests within acceptable limits
- [ ] Edge cases covered
- [ ] Error scenarios tested

---

*Document Version: 1.0*  
*Last Updated: 2026-03-04*  
*Status: DRAFT - Pending Review*
