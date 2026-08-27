# SIM-Bank Manager - Test-Driven Development

> Tests-Driven Development: Test specifications and test cases for SIM-bank manager.

## Overview

**Domain**: SIM-Bank Manager  
**Type**: TDD (Tests-Driven Development)  
**Status**: DRAFT  
**Generated**: 2026-03-04  
**Source**: Legacy behavior analysis + Modern requirements

## Test Strategy

### Testing Pyramid

```
                    ┌─────────┐
                   │   E2E   │  10% (Integration tests)
                  ├─────────────┤
                 │  Integration  │ 20% (Component tests)
                ├───────────────────┤
               │      Unit Tests     │ 70% (Function-level)
              └───────────────────────┘
```

### Test Categories

| Category | Coverage | Tools | Purpose |
|----------|----------|-------|---------|
| **Unit Tests** | >90% | `testing`, `testify` | Test individual functions |
| **Integration Tests** | >80% | `testcontainers-go` | Test component interactions |
| **E2E Tests** | Critical paths | `godog` (Cucumber) | Test user scenarios |
| **Performance Tests** | Key operations | `testing`, `vegeta` | Load testing |

## Unit Tests

### Manager Tests

#### Test File: `internal/simbank/manager_test.go`

```go
package simbank

import (
    "context"
    "testing"
    "time"
    
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
)
```

#### Test Cases

##### 1. NewManager Creation

```go
func TestNewManager(t *testing.T) {
    t.Run("creates manager with valid config", func(t *testing.T) {
        // Arrange
        cfg := &config.SimBankConfig{
            PollingInterval: 30 * time.Second,
            Timeout:         10 * time.Second,
        }
        
        // Act
        manager := NewManager(cfg)
        
        // Assert
        assert.NotNil(t, manager)
        assert.NotNil(t, manager.clients)
        assert.Empty(t, manager.clients) // Initially empty
        assert.NotNil(t, manager.ctx)
        assert.NotNil(t, manager.cancel)
    })
    
    t.Run("initializes with empty client map", func(t *testing.T) {
        cfg := &config.SimBankConfig{}
        manager := NewManager(cfg)
        
        assert.Len(t, manager.clients, 0)
    })
}
```

##### 2. Manager Start/Stop Lifecycle

```go
func TestManagerLifecycle(t *testing.T) {
    t.Run("starts and stops gracefully", func(t *testing.T) {
        // Arrange
        cfg := &config.SimBankConfig{
            PollingInterval: 100 * time.Millisecond, // Fast for testing
        }
        manager := NewManager(cfg)
        
        // Mock database
        mockDB := new(MockDatabase)
        mockDB.On("Find", mock.Anything).Return(nil)
        
        // Act - Start
        err := manager.Start()
        assert.NoError(t, err)
        
        // Wait for polling to start
        time.Sleep(150 * time.Millisecond)
        
        // Act - Stop
        manager.Stop()
        
        // Assert
        // Context should be cancelled
        select {
        case <-manager.ctx.Done():
            // Expected
        default:
            t.Error("Context was not cancelled on Stop()")
        }
    })
    
    t.Run("start fails when database load fails", func(t *testing.T) {
        cfg := &config.SimBankConfig{}
        manager := NewManager(cfg)
        
        mockDB := new(MockDatabase)
        mockDB.On("Find", mock.Anything).Return(errors.New("DB error"))
        
        err := manager.Start()
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "failed to load simbanks")
    })
}
```

##### 3. LoadSimBanks

```go
func TestLoadSimBanks(t *testing.T) {
    t.Run("loads active SIM-banks from database", func(t *testing.T) {
        // Arrange
        manager := NewManager(&config.SimBankConfig{})
        
        mockSimBanks := []database.SimBank{
            {ID: 1, Name: "Bank-1", URL: "http://192.168.1.1:8080", IsActive: true},
            {ID: 2, Name: "Bank-2", URL: "http://192.168.1.2:8080", IsActive: true},
        }
        
        mockDB := new(MockDatabase)
        mockDB.On("Where", "is_active = ?", true).Return(mockDB)
        mockDB.On("Find", mock.Anything).Run(func(args mock.Arguments) {
            sims := args.Get(0).(*[]database.SimBank)
            *sims = mockSimBanks
        }).Return(nil)
        
        // Act
        err := manager.loadSimBanks()
        
        // Assert
        assert.NoError(t, err)
        assert.Len(t, manager.clients, 2)
        assert.Contains(t, manager.clients, uint(1))
        assert.Contains(t, manager.clients, uint(2))
    })
    
    t.Run("excludes inactive SIM-banks", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        mockSimBanks := []database.SimBank{
            {ID: 1, IsActive: true},
            {ID: 2, IsActive: false}, // Inactive
            {ID: 3, IsActive: true},
        }
        
        mockDB := new(MockDatabase)
        mockDB.On("Where", "is_active = ?", true).Return(mockDB)
        mockDB.On("Find", mock.Anything).Run(func(args mock.Arguments) {
            sims := args.Get(0).(*[]database.SimBank)
            *sims = []database.SimBank{mockSimBanks[0], mockSimBanks[2]} // Only active
        }).Return(nil)
        
        err := manager.loadSimBanks()
        assert.NoError(t, err)
        assert.Len(t, manager.clients, 2) // Only 2 active
    })
}
```

##### 4. UpdateAllSimBanks (Concurrent)

```go
func TestUpdateAllSimBanks(t *testing.T) {
    t.Run("updates all banks concurrently", func(t *testing.T) {
        // Arrange
        manager := NewManager(&config.SimBankConfig{})
        
        // Create mock clients
        client1 := new(MockClient)
        client1.On("GetStatus").Return(&StatusResponse{
            Status: "online",
            Slots: []SlotInfo{{SlotID: 1, Status: "online"}},
        }, nil)
        
        client2 := new(MockClient)
        client2.On("GetStatus").Return(&StatusResponse{
            Status: "online",
            Slots: []SlotInfo{{SlotID: 1, Status: "online"}},
        }, nil)
        
        manager.clients = map[uint]*Client{1: (*Client)(client1), 2: (*Client)(client2)}
        
        // Act
        start := time.Now()
        manager.updateAllSimBanks()
        elapsed := time.Since(start)
        
        // Assert
        // If concurrent, should take ~1x client time, not 2x
        assert.Less(t, elapsed, 150*time.Millisecond) // Less than sequential
        
        client1.AssertExpectations(t)
        client2.AssertExpectations(t)
    })
    
    t.Run("handles individual bank failures gracefully", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        client1 := new(MockClient)
        client1.On("GetStatus").Return(nil, errors.New("timeout"))
        
        client2 := new(MockClient)
        client2.On("GetStatus").Return(&StatusResponse{Status: "online"}, nil)
        
        manager.clients = map[uint]*Client{1: (*Client)(client1), 2: (*Client)(client2)}
        
        // Act
        manager.updateAllSimBanks()
        
        // Assert
        // Both clients should be called despite first failure
        client1.AssertCalled(t, "GetStatus")
        client2.AssertCalled(t, "GetStatus")
    })
}
```

##### 5. SetPower Operation

```go
func TestSetPower(t *testing.T) {
    t.Run("successfully sets power for slot", func(t *testing.T) {
        // Arrange
        manager := NewManager(&config.SimBankConfig{})
        
        mockClient := new(MockClient)
        mockClient.On("SetPower", 5, true).Return(nil)
        
        mockDB := new(MockDatabase)
        mockDB.On("Model", mock.Anything).Return(mockDB)
        mockDB.On("Where", mock.Anything, mock.Anything, mock.Anything).Return(mockDB)
        mockDB.On("Update", "power", true).Return(mockDB)
        
        manager.clients = map[uint]*Client{1: (*Client)(mockClient)}
        
        // Act
        err := manager.SetPower(1, 5, true)
        
        // Assert
        assert.NoError(t, err)
        mockClient.AssertExpectations(t)
        mockDB.AssertExpectations(t)
    })
    
    t.Run("returns error for non-existent SIM-bank", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        manager.clients = map[uint]*Client{} // Empty
        
        err := manager.SetPower(999, 5, true)
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "simbank 999 not found")
    })
    
    t.Run("propagates client error", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        mockClient := new(MockClient)
        mockClient.On("SetPower", 5, true).Return(errors.New("device timeout"))
        
        manager.clients = map[uint]*Client{1: (*Client)(mockClient)}
        
        err := manager.SetPower(1, 5, true)
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "device timeout")
    })
}
```

##### 6. SendUSSD Operation

```go
func TestSendUSSD(t *testing.T) {
    t.Run("successfully sends USSD command", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        mockClient := new(MockClient)
        mockClient.On("SendUSSD", 3, "*100#").Return(&USSDResponse{
            Response: "Balance: $10.50",
        }, nil)
        
        manager.clients = map[uint]*Client{1: (*Client)(mockClient)}
        
        response, err := manager.SendUSSD(1, 3, "*100#")
        
        assert.NoError(t, err)
        assert.Equal(t, "Balance: $10.50", response)
        mockClient.AssertExpectations(t)
    })
    
    t.Run("handles USSD error response", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        mockClient := new(MockClient)
        mockClient.On("SendUSSD", 3, "*100#").Return(nil, errors.New("network timeout"))
        
        manager.clients = map[uint]*Client{1: (*Client)(mockClient)}
        
        response, err := manager.SendUSSD(1, 3, "*100#")
        
        assert.Error(t, err)
        assert.Empty(t, response)
    })
}
```

##### 7. GetSimBankStatus

```go
func TestGetSimBankStatus(t *testing.T) {
    t.Run("returns status for existing SIM-bank", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        mockClient := new(MockClient)
        mockClient.On("GetStatus").Return(&StatusResponse{
            Status: "online",
            Slots: []SlotInfo{
                {SlotID: 1, Status: "online", Signal: 85},
                {SlotID: 2, Status: "online", Signal: 72},
            },
        }, nil)
        
        manager.clients = map[uint]*Client{1: (*Client)(mockClient)}
        
        status, err := manager.GetSimBankStatus(1)
        
        assert.NoError(t, err)
        assert.NotNil(t, status)
        assert.Equal(t, "online", status.Status)
        assert.Len(t, status.Slots, 2)
    })
    
    t.Run("returns error for non-existent bank", func(t *testing.T) {
        manager := NewManager(&config.SimBankConfig{})
        
        _, err := manager.GetSimBankStatus(999)
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "simbank 999 not found")
    })
}
```

### Client Tests

#### Test File: `internal/simbank/client_test.go`

```go
func TestClientGetStatus(t *testing.T) {
    t.Run("successfully retrieves status", func(t *testing.T) {
        // Arrange - Mock HTTP server
        server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            assert.Equal(t, "/status", r.URL.Path)
            assert.Equal(t, http.MethodGet, r.Method)
            
            w.Header().Set("Content-Type", "application/json")
            json.NewEncoder(w).Encode(StatusResponse{
                Status: "online",
                Slots: []SlotInfo{
                    {SlotID: 1, IMSI: "123456789012345", Status: "online", Signal: 85},
                },
            })
        }))
        defer server.Close()
        
        client := NewClient(server.URL, 5*time.Second)
        
        // Act
        status, err := client.GetStatus()
        
        // Assert
        assert.NoError(t, err)
        assert.NotNil(t, status)
        assert.Equal(t, "online", status.Status)
        assert.Len(t, status.Slots, 1)
        assert.Equal(t, "123456789012345", status.Slots[0].IMSI)
    })
    
    t.Run("handles HTTP error", func(t *testing.T) {
        server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            w.WriteHeader(http.StatusInternalServerError)
            w.Write([]byte("Internal Server Error"))
        }))
        defer server.Close()
        
        client := NewClient(server.URL, 5*time.Second)
        
        _, err := client.GetStatus()
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "status request failed: 500")
    })
    
    t.Run("handles timeout", func(t *testing.T) {
        server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            time.Sleep(100 * time.Millisecond) // Longer than timeout
        }))
        defer server.Close()
        
        client := NewClient(server.URL, 10*time.Millisecond)
        
        _, err := client.GetStatus()
        
        assert.Error(t, err)
        assert.Contains(t, err.Error(), "timeout")
    })
}

func TestClientSetPower(t *testing.T) {
    t.Run("successfully sets power", func(t *testing.T) {
        server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            assert.Equal(t, "/slot/power", r.URL.Path)
            assert.Equal(t, http.MethodPost, r.Method)
            
            var req PowerRequest
            json.NewDecoder(r.Body).Decode(&req)
            assert.Equal(t, 5, req.SlotID)
            assert.Equal(t, true, req.Power)
            
            w.WriteHeader(http.StatusOK)
        }))
        defer server.Close()
        
        client := NewClient(server.URL, 5*time.Second)
        err := client.SetPower(5, true)
        
        assert.NoError(t, err)
    })
}

func TestClientSendUSSD(t *testing.T) {
    t.Run("successfully sends USSD", func(t *testing.T) {
        server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            assert.Equal(t, "/ussd", r.URL.Path)
            
            var req USSDRequest
            json.NewDecoder(r.Body).Decode(&req)
            assert.Equal(t, 3, req.SlotID)
            assert.Equal(t, "*100#", req.Command)
            
            w.Header().Set("Content-Type", "application/json")
            json.NewEncoder(w).Encode(USSDResponse{
                Response: "Balance: $10.50",
            })
        }))
        defer server.Close()
        
        client := NewClient(server.URL, 5*time.Second)
        response, err := client.SendUSSD(3, "*100#")
        
        assert.NoError(t, err)
        assert.Equal(t, "Balance: $10.50", response)
    })
}
```

## Integration Tests

### Test File: `internal/simbank/manager_integration_test.go`

```go
//go:build integration

package simbank

import (
    "context"
    "testing"
    "time"
    
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestManagerWithRealDatabase(t *testing.T) {
    // Setup test container
    ctx := context.Background()
    
    dbContainer, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "postgres:14",
            ExposedPorts: []string{"5432/tcp"},
            Env: map[string]string{
                "POSTGRES_USER":     "test",
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB":       "simhub_test",
            },
            WaitingFor: wait.ForLog("database system is ready to accept connections"),
        },
        Started: true,
    })
    defer dbContainer.Terminate(ctx)
    
    // Get connection string
    host, _ := dbContainer.Host(ctx)
    port, _ := dbContainer.MappedPort(ctx, "5432")
    
    // Initialize database
    cfg := &config.DatabaseConfig{
        Host:     host,
        Port:     port.Int(),
        User:     "test",
        Password: "test",
        DBName:   "simhub_test",
    }
    database.Connect(cfg)
    database.AutoMigrate()
    
    // Seed test data
    database.DB.Create(&database.SimBank{
        ID:       1,
        Name:     "Test-Bank",
        Type:     "SMB128",
        URL:      "http://localhost:8080",
        IsActive: true,
    })
    
    // Test manager
    manager := NewManager(&config.SimBankConfig{
        PollingInterval: 1 * time.Second,
        Timeout:         500 * time.Millisecond,
    })
    
    err = manager.Start()
    assert.NoError(t, err)
    
    time.Sleep(2 * time.Second) // Let it poll
    
    manager.Stop()
}
```

## Test Coverage Requirements

| Component | Minimum Coverage | Critical Paths |
|-----------|-----------------|----------------|
| Manager | >90% | Start/Stop, SetPower, SendUSSD |
| Client | >85% | GetStatus, SetPower, SendUSSD |
| updateSlots | >95% | Upsert logic, error handling |
| monitorLoop | >80% | Context cancellation, ticker |

## Mock Implementations

```go
// MockDatabase for testing
type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) Where(query interface{}, args ...interface{}) *gorm.DB {
    args := m.Called(query, args)
    return args.Get(0).(*gorm.DB)
}

func (m *MockDatabase) Find(out interface{}) *gorm.DB {
    args := m.Called(out)
    return args.Get(0).(*gorm.DB)
}

// MockClient for testing
type MockClient struct {
    mock.Mock
}

func (m *MockClient) GetStatus() (*StatusResponse, error) {
    args := m.Called()
    return args.Get(0).(*StatusResponse), args.Error(1)
}

func (m *MockClient) SetPower(slotID int, power bool) error {
    args := m.Called(slotID, power)
    return args.Error(0)
}

func (m *MockClient) SendUSSD(slotID int, command string) (*USSDResponse, error) {
    args := m.Called(slotID, command)
    return args.Get(0).(*USSDResponse), args.Error(1)
}
```

## Running Tests

```bash
# Unit tests
go test ./internal/simbank/... -v -race -cover

# Integration tests (requires Docker)
go test ./internal/simbank/... -v -tags=integration

# Specific test
go test ./internal/simbank -run TestManagerLifecycle -v

# Coverage report
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Legacy Test Gaps

| Legacy Behavior | Modern Test Coverage |
|----------------|---------------------|
| No tests in PHP code | >90% unit test coverage |
| Manual testing only | Automated CI/CD tests |
| No mock infrastructure | Comprehensive mocks |
| No concurrency tests | Race detector enabled |

---

*Generated by /legacy reverse engineering - TDD specification for implementation*
