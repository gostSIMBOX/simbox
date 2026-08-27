# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AT Command Protocol                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Command Layer │  Response Layer │    Queue Management     │
│  (at_command.c) │ (at_response.c) │    (at_queue.c)         │
│                 │                 │                         │
│  - 60+ commands │  - Response enum│  - Task queue           │
│  - Templates    │  - Parser       │  - Timeout tracking     │
│  - Builders     │  - Matching     │  - Memory management    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Data Structures

### Command Enumeration (at_cmd_t)
```c
typedef enum {
    CMD_USER = 0,
    CMD_AT,           // "AT"
    CMD_AT_A,         // "ATA"
    CMD_AT_CCWA_SET,  // "AT+CCWA="
    CMD_AT_CFUN_V,    // "AT+CFUN?"
    CMD_AT_CFUN,      // "AT+CFUN"
    CMD_AT_CGMI,      // Manufacturer info
    CMD_AT_CGMM,      // Model name
    CMD_AT_CGMR,      // Software version
    CMD_AT_CGSN,      // IMEI
    CMD_AT_CHUP,      // Hangup
    CMD_AT_CIMI,      // IMSI
    CMD_AT_CLIR,      // Caller ID restriction
    CMD_AT_CMGS,      // Send SMS
    CMD_AT_SMSTEXT,   // SMS text (Ctrl-Z terminated)
    CMD_AT_CUSD,      // USSD
    CMD_AT_D,         // Dial
    // ... 60+ total
} at_cmd_t;
```

### Response Enumeration (at_res_t)
```c
typedef enum {
    RES_PARSE_ERROR = -1,
    RES_UNKNOWN = 0,
    RES_BOOT,         // Device boot
    RES_BUSY,         // Busy signal
    RES_CEND,         // Call end
    RES_CMGR,         // SMS read response
    RES_CMTI,         // New SMS notification
    RES_CONF,         // Conference
    RES_CONN,         // Connection
    RES_COPS,         // Operator
    RES_CPIN,         // SIM PIN status
    RES_CREG,         // Registration
    RES_CSQ,          // Signal quality
    RES_CUSD,         // USSD response
    RES_ERROR,        // Error
    RES_OK,           // Success
    RES_ORIG,         // Originating
    RES_RING,         // Ring
    RES_SMS_PROMPT,   // SMS prompt (>)
    // ... 40+ total
} at_res_t;
```

### Queue Command Structure
```c
typedef struct at_queue_cmd {
    at_cmd_t    cmd;       // Command code
    at_res_t    res;       // Expected response
    unsigned    flags;     // STATIC, IGNORE
    struct timeval timeout;// Timeout value
    char*       data;      // Command string
    unsigned    length;    // Data length
} at_queue_cmd_t;

// Flag definitions
#define ATQ_CMD_FLAG_STATIC  0x01  // Don't free data
#define ATQ_CMD_FLAG_IGNORE  0x02  // Ignore response mismatch
```

### Queue Task Structure
```c
typedef struct at_queue_task {
    AST_LIST_ENTRY(at_queue_task) entry;
    unsigned    cmdsno;      // Number of commands
    unsigned    cindex;      // Current command index
    struct cpvt* cpvt;       // Call private data
    at_queue_cmd_t cmds[0];  // Flexible array
} at_queue_task_t;
```

## Command Templates

### Static Command Templates
```c
static const char cmd_at[]      = "AT\r";
static const char cmd_chld1x[]  = "AT+CHLD=1%d\r";
static const char cmd_chld2[]   = "AT+CHLD=2\r";
static const char cmd_clcc[]    = "AT+CLCC\r";
static const char cmd_ddsetex2[]= "AT^DDSETEX=2\r";
```

### Initialization Sequence - Modem
```c
static const at_queue_cmd_t st_cmds1[] = {
    ATQ_CMD_DECLARE_ST(CMD_AT, "AT\r"),           // Ping
    ATQ_CMD_DECLARE_ST(CMD_AT_E, "ATE0\r"),       // Disable echo
    ATQ_CMD_DECLARE_ST(CMD_AT_CGMI, "AT+CGMI\r"), // Manufacturer
    ATQ_CMD_DECLARE_ST(CMD_AT_CGMM, "AT+CGMM\r"), // Model
    ATQ_CMD_DECLARE_ST(CMD_AT_CGMR, "AT+CGMR\r"), // Firmware
    ATQ_CMD_DECLARE_ST(CMD_AT_CMEE, "AT+CMEE=0\r"),// Error reporting
    ATQ_CMD_DECLARE_ST(CMD_AT_CGSN, "AT+CGSN\r"), // IMEI
    ATQ_CMD_DECLARE_ST(CMD_AT_CFUN_V, "AT+CFUN?\r"),// Functionality check
};
```

### Initialization Sequence - SIM
```c
static const at_queue_cmd_t st_cmds2[] = {
    ATQ_CMD_DECLARE_ST(CMD_AT_SN, "AT^SN\r"),      // Serial number
    ATQ_CMD_DECLARE_ST(CMD_AT_ICCID, "AT^ICCID?"), // ICCID
    ATQ_CMD_DECLARE_ST(CMD_AT_SPN, "AT^SPN=0\r"),  // Operator name
    ATQ_CMD_DECLARE_ST(CMD_AT_CIMI, "AT+CIMI\r"),  // IMSI
    ATQ_CMD_DECLARE_STI(CMD_AT_CREG_INIT, "AT+CREG=2\r"),
    ATQ_CMD_DECLARE_ST(CMD_AT_CREG, "AT+CREG?\r"), // Registration
    ATQ_CMD_DECLARE_ST(CMD_AT_CNUM, "AT+CNUM\r"),  // Subscriber number
    ATQ_CMD_DECLARE_ST(CMD_AT_CSSN, "AT+CSSN=1,1\r"),// Supplementary service
    ATQ_CMD_DECLARE_ST(CMD_AT_CMGF, "AT+CMGF=0\r\r"),// PDU mode
    ATQ_CMD_DECLARE_ST(CMD_AT_CSCS, "AT+CSCS=\"UCS2\"\r"),
    ATQ_CMD_DECLARE_ST(CMD_AT_CNMI, "AT+CNMI=1,1,0,1,0\r"),
    ATQ_CMD_DECLARE_ST(CMD_AT_CSQ, "AT+CSQ\r"),    // Signal quality
};
```

## Queue Operations

### Add Task
```c
static at_queue_task_t * at_queue_add(
    struct cpvt * cpvt,
    const at_queue_cmd_t * cmds,
    unsigned cmdsno,
    int prio  // 0=tail, 1=after head
);
```

### Execute Queue
```c
EXPORT_DEF int at_queue_run(struct pvt * pvt)
{
    at_queue_cmd_t * cmd = at_queue_head_cmd_nc(pvt);
    if (cmd && cmd->length > 0) {
        fail = at_write(pvt, cmd->data, cmd->length);
        if (!fail) {
            cmd->timeout = ast_tvadd(ast_tvnow(), cmd->timeout);
            at_queue_free_data(cmd);  // Mark as in-flight
        }
    }
    return fail;
}
```

### Complete Command
```c
EXPORT_DEF void at_queue_remove_cmd(struct pvt* pvt, at_res_t res)
{
    at_queue_task_t * task = AST_LIST_FIRST(&pvt->at_queue);
    if (task) {
        task->cindex++;
        // Remove task if: all done OR response mismatch (unless IGNORE)
        if (task->cindex >= task->cmdsno || 
            (task->cmds[index].res != res && 
             (task->cmds[index].flags & ATQ_CMD_FLAG_IGNORE) == 0)) {
            at_queue_remove(pvt);
        }
    }
}
```

## Timeout Values

| Timeout | Value | Use Case |
|---------|-------|----------|
| 1s | `ATQ_CMD_TIMEOUT_1S` | Quick status checks |
| 2s | `ATQ_CMD_TIMEOUT_2S` | Default (most commands) |
| 5s | `ATQ_CMD_TIMEOUT_5S` | Network queries |
| 10s | `ATQ_CMD_TIMEOUT_10S` | SIM operations |
| 15s | `ATQ_CMD_TIMEOUT_15S` | Complex operations |
| 40s | `ATQ_CMD_TIMEOUT_40S` | SMS send (user input) |

## SMS Sending Flow

```
1. at_enque_sms() called with destination, message
2. Build PDU via pdu_build() (max 2048 bytes)
3. Create two-stage command:
   - CMD_AT_CMGS: "AT+CMGS=<length>\r" (timeout 2s)
   - CMD_AT_SMSTEXT: PDU + Ctrl-Z (0x1A) (timeout 40s)
4. Queue task inserted
5. Execute: Send AT+CMGS, wait for ">" prompt
6. Execute: Send PDU + Ctrl-Z, wait for OK
```

## USSD Sending Flow

```
1. at_enque_ussd() called with USSD code
2. Determine encoding (7-bit hex or UCS-2 hex)
3. Build command: "AT+CUSD=1,\"<encoded_code>\",15\r"
4. Queue as single command (timeout 2s)
5. Execute and wait for +CUSD response
```

## Error Handling

### Write Error
```c
if (fail) {
    ast_log(LOG_ERROR, "[%s] Error write command '%s', cancel\n", 
            PVT_ID(pvt), at_cmd2str(cmd->cmd));
    at_queue_remove_cmd(pvt, cmd->res + 1);  // Force mismatch
}
```

### Response Mismatch
- Command removed from queue
- Error logged with expected vs actual response
- Task continues if IGNORE flag set

### Timeout (commented out in current code)
```c
#if 0
if (ast_tvcmp(ast_tvnow(), cmd->timeout) > 0) {
    ast_log(LOG_ERROR, "[%s] Command '%s' expired, cancel\n", 
            PVT_ID(pvt), at_cmd2str(cmd->cmd));
    at_queue_remove_cmd(pvt, cmd->res + 1);
}
#endif
```

## CLI Interface

```
dongle cmd <device> <at_command>
  - Executes raw AT command
  - Appends \r terminator
  - Returns response to CLI
```

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of at_command.c (1214 lines), at_response.c, at_queue.c (412 lines)
