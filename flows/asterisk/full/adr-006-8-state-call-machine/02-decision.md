# Solution

## State Enumeration

```c
typedef enum {
    // Real device states (from CLCC)
    CALL_STATE_ACTIVE = 0,    // Active conversation
    CALL_STATE_ONHOLD,        // Call on hold
    CALL_STATE_DIALING,       // Dialing outbound
    CALL_STATE_ALERTING,      // Remote ringing
    CALL_STATE_INCOMING,      // Incoming call
    CALL_STATE_WAITING,       // Call waiting
    
    // Pseudo states (internal)
    CALL_STATE_RELEASED,      // Call terminated
    CALL_STATE_INIT,          // Being initialized
    
    CALL_STATE_MAX = CALL_STATE_INIT
} call_state_t;
```

## State Transition Diagram

```
                         ┌─────────────┐
                         │    INIT     │
                         └──────┬──────┘
                                │ channel_call()
                                ▼
                         ┌─────────────┐
                   ┌─────│   DIALING   │─────┐
                   │     └──────┬──────┘     │
     incoming      │            │ alert      │ call answered
     call          │            ▼            │
                   │     ┌─────────────┐     │
                   │     │  ALERTING   │     │
                   │     └──────┬──────┘     │
                   │            │            │
                   │            ▼            │
                   │     ┌─────────────┐     │
                   │     │   ACTIVE    │◄────┘
                   │     └──────┬──────┘
                   │            │
         ┌─────────┴────────────┼────────────┐
         │                      │            │
         ▼                      ▼            ▼
   ┌─────────┐          ┌──────────┐  ┌──────────┐
   │ INCOMING│          │  ONHOLD  │  │ WAITING  │
   └────┬────┘          └────┬─────┘  └────┬─────┘
        │                    │             │
        │ answer             │ retrieve    │ accept
        ▼                    ▼             ▼
   ┌─────────────────────────────────────────┐
   │              ACTIVE                     │
   └─────────────────┬───────────────────────┘
                     │
                     │ hangup / CEND
                     ▼
   ┌─────────────────────────────────────────┐
   │             RELEASED                    │
   └─────────────────────────────────────────┘
```

## CLCC Mapping

AT+CLCC response format:
```
+CLCC: <id>,<dir>,<stat>,<mode>,<mpty>,<number>,<type>

stat values:
0 = ACTIVE
1 = HOLD
2 = DIALING
3 = ALERTING
4 = INCOMING
5 = WAITING
```

```c
// CLCC state to internal state mapping
call_state_t clcc_to_state(int stat) {
    switch (stat) {
        case 0: return CALL_STATE_ACTIVE;
        case 1: return CALL_STATE_ONHOLD;
        case 2: return CALL_STATE_DIALING;
        case 3: return CALL_STATE_ALERTING;
        case 4: return CALL_STATE_INCOMING;
        case 5: return CALL_STATE_WAITING;
        default: return CALL_STATE_RELEASED;
    }
}
```

## State Transition Functions

```c
void change_channel_state(struct cpvt * cpvt, unsigned newstate, int cause)
{
    call_state_t oldstate = cpvt->state;
    cpvt->state = newstate;
    
    // Notify Asterisk
    queue_control_channel(cpvt, get_control_frame(newstate));
    
    // Update channel state
    if (newstate == CALL_STATE_RELEASED) {
        queue_hangup(cpvt->channel, cause);
    }
}
```

## Call Flags

```c
typedef enum {
    CALL_FLAG_NONE        = 0,
    CALL_FLAG_HOLD_OTHER  = 1,   // Hold other calls when dialing
    CALL_FLAG_NEED_HANGUP = 2,   // Must issue hangup
    CALL_FLAG_ACTIVATED   = 4,   // FD attached to channel
    CALL_FLAG_ALIVE       = 8,   // Still in CLCC list
    CALL_FLAG_CONFERENCE  = 16,  // Begin conference after activate
    CALL_FLAG_MASTER      = 32,  // Owns audio FD
    CALL_FLAG_BRIDGE_LOOP = 64,  // Detected bridge loop
    CALL_FLAG_MULTIPARTY  = 256  // Part of conference
} call_flag_t;
```

## State-Dependent Operations

| Current State | Valid Operations |
|---------------|------------------|
| INIT | channel_call() |
| DIALING | hangup, wait for alerting |
| ALERTING | hangup, answer |
| ACTIVE | hold, hangup, dtmf |
| ONHOLD | retrieve, hangup |
| INCOMING | answer, hangup |
| WAITING | accept, reject |
| RELEASED | (none - cleanup) |

## Asterisk State Mapping

```c
int call_state_to_asterisk(call_state_t state) {
    switch (state) {
        case CALL_STATE_INIT:     return AST_STATE_DOWN;
        case CALL_STATE_DIALING:  return AST_STATE_DIALING;
        case CALL_STATE_ALERTING: return AST_STATE_RINGING;
        case CALL_STATE_INCOMING: return AST_STATE_RING;
        case CALL_STATE_ACTIVE:   return AST_STATE_UP;
        case CALL_STATE_ONHOLD:   return AST_STATE_HOLD;
        default:                  return AST_STATE_DOWN;
    }
}
```
