# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Call Management Layer                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Channel Tech   │  Call State     │    Audio Management     │
│  (channel.c)    │  Machine (cpvt) │    (mixbuffer)          │
│                 │                 │                         │
│  - request      │  - 8 states     │  - Mix streams          │
│  - call         │  - 12 flags     │  - Buffer management    │
│  - hangup       │  - Call index   │  - Bridge detection     │
│  - read/write   │  - Direction    │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Data Structures

### Call Private Data (cpvt_t)
```c
typedef struct cpvt {
    AST_LIST_ENTRY(cpvt) entry;
    struct ast_channel* channel;      // Asterisk channel
    struct ast_channel* requestor;    // Requesting channel
    struct pvt* pvt;                  // Device pointer
    short call_idx;                   // 0-31
    call_state_t state;               // Current state
    int flags;                        // Call flags
    unsigned int dir:1;               // 0=outgoing, 1=incoming
    int rd_pipe[2];                   // Split read pipe
    struct mixstream mixstream;       // Audio mixing
    char a_read_buf[FRAME_SIZE + AST_FRIENDLY_OFFSET];
    struct ast_frame a_read_frame;
    long int answered;                // Answer timestamp
} cpvt_t;

#define FRAME_SIZE 320  // 20ms at 8kHz 16-bit
```

### Call States (call_state_t)
```c
typedef enum {
    CALL_STATE_ACTIVE = 0,    // from CLCC
    CALL_STATE_ONHOLD,        // from CLCC
    CALL_STATE_DIALING,       // from CLCC
    CALL_STATE_ALERTING,      // from CLCC
    CALL_STATE_INCOMING,      // from CLCC
    CALL_STATE_WAITING,       // from CLCC
    CALL_STATE_RELEASED,      // call ended
    CALL_STATE_INIT           // being initialized
} call_state_t;
```

### Call Flags (call_flag_t)
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
    CALL_FLAG_BRIDGE_CHECK= 128, // Already checked for bridge
    CALL_FLAG_MULTIPARTY  = 256  // Part of conference
} call_flag_t;
```

## Channel Tech Interface

### Channel Request
```c
static struct ast_channel * channel_request(
    const char * type,
    struct ast_format_cap * cap,
    const struct ast_channel *requestor,
    void * data,
    int * cause
)
{
    // Parse dial string: device/options:number
    parse_dial_string(dest_dev, &dest_num, &opts);
    
    // Find available device
    pvt = find_device_by_resource(dest_dev, opts, requestor, &exists);
    
    // Create channel in INIT state
    channel = new_channel(pvt, AST_STATE_DOWN, NULL, 
                         pvt_get_pseudo_call_idx(pvt),
                         CALL_DIR_OUTGOING, CALL_STATE_INIT, 
                         NULL, requestor);
}
```

### Channel Call
```c
static int channel_call(
    struct ast_channel* channel,
    char* dest,
    int timeout
)
{
    cpvt = ast_channel_tech_pvt(channel);
    pvt = cpvt->pvt;
    
    // Parse dial string
    parse_dial_string(dest_dev, &dest_num, &opts);
    
    // Check device readiness
    if (!ready4voice_call(pvt, cpvt, opts)) {
        return -1;
    }
    
    CPVT_SET_FLAGS(cpvt, opts);
    
    // Queue dial command
    at_enque_dial(cpvt, dest_num, clir);
    
    // Transition to DIALING
    change_channel_state(cpvt, CALL_STATE_DIALING, 0);
}
```

### Dial String Parsing
```c
static int parse_dial_string(
    char * dialstr,
    const char** number,
    int * opts
)
{
    // Format: device[/options]:number
    options = strchr(dialstr, '/');
    if (options) {
        *options++ = '\0';
        dest_num = strchr(options, ':');
        if (!dest_num) {
            dest_num = options;
        } else {
            *dest_num++ = '\0';
            // Parse options
            if (!strcasecmp(options, "holdother"))
                lopts = CALL_FLAG_HOLD_OTHER;
            else if (!strcasecmp(options, "conference"))
                lopts = CALL_FLAG_HOLD_OTHER | CALL_FLAG_CONFERENCE;
        }
    }
    
    // Validate number: 0123456789*#+ABC only
    if (!is_valid_phone_number(dest_num)) {
        return AST_CAUSE_INCOMPATIBLE_DESTINATION;
    }
}
```

## State Transitions

```
                    ┌─────────────┐
                    │    INIT     │
                    └──────┬──────┘
                           │ channel_call()
                           ▼
                    ┌─────────────┐
              ┌─────│   DIALING   │─────┐
              │     └──────┬──────┘     │
    incoming  │            │ alert      │ call answered
    call      │            ▼            │
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

## Hold and Conference Operations

### Hold Other Calls
```c
// AT+CHLD=2 - Hold all active calls
at_enque_generic(cpvt, CMD_AT_CHLD_2, 0, "AT+CHLD=2\r");
```

### Release Specific Call
```c
// AT+CHLD=1x - Release call x
at_enque_generic(cpvt, CMD_AT_CHLD_1x, 0, "AT+CHLD=1%d\r", call_idx);
```

### Conference (Merge Calls)
```c
// AT+CHLD=3 - Conference all held and active calls
at_enque_generic(cpvt, CMD_AT_CHLD_3, 0, "AT+CHLD=3\r");
CPVT_SET_FLAGS(cpvt, CALL_FLAG_MULTIPARTY);
```

### List Current Calls
```c
// AT+CLCC - List current calls
at_enque_generic(cpvt, CMD_AT_CLCC, 0, "AT+CLCC\r");
// Response: +CLCC: <id>,<dir>,<stat>,<mode>,<mpty>,<number>,<type>
```

## Bridge Loop Detection

```c
static int check_bridge_loop(struct cpvt * cpvt)
{
    // Check if channel is bridged to another channel on same device
    struct ast_channel * bridged = ast_bridged_channel(cpvt->channel);
    if (bridged) {
        struct cpvt * other = ast_channel_tech_pvt(bridged);
        if (other && other->pvt == cpvt->pvt) {
            // Bridge loop detected!
            CPVT_SET_FLAGS(cpvt, CALL_FLAG_BRIDGE_LOOP);
            return 1;
        }
    }
    return 0;
}
```

## Audio Management

### Frame Size
```c
#define FRAME_SIZE 320  // 20ms at 8kHz, 16-bit mono
```

### Read Frame
```c
static struct ast_frame * channel_read(struct ast_channel * channel)
{
    cpvt = ast_channel_tech_pvt(channel);
    
    // Read from device via ring buffer
    rb_read_until_char_iov(&pvt->read_rb, iov, '\n');
    
    // Build Asterisk frame
    cpvt->a_read_frame.frametype = AST_FRAME_VOICE;
    cpvt->a_read_frame.data.ptr = cpvt->a_read_buf;
    cpvt->a_read_frame.datalen = FRAME_SIZE;
    cpvt->a_read_frame.samples = FRAME_SIZE / 2;  // 16-bit
    
    return &cpvt->a_read_frame;
}
```

### Write Frame
```c
static int channel_write(struct ast_channel * channel, struct ast_frame * frame)
{
    cpvt = ast_channel_tech_pvt(channel);
    pvt = cpvt->pvt;
    
    // Write to device via ring buffer
    rb_write(&pvt->write_rb, frame->data.ptr, frame->datalen);
    
    return 0;
}
```

## CLI Commands

```
dongle show device state <device>
  - Shows all calls on device
  - Call index, state, direction, flags
  - Channel association

dongle show devices
  - Lists all devices with call counts
  - Active calls, held calls
```

## Manager Events

```
DongleCallStart
  - CallID: <call_idx>
  - Direction: outgoing/incoming
  - Number: <dialed number>
  - State: dialing/alerting/active

DongleCallEnd
  - CallID: <call_idx>
  - Duration: <seconds>
  - Cause: <hangup cause>
```

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of channel.c (1571 lines), cpvt.h, channel.h
