# Solution

## Queue Structure

### Task Structure
```c
typedef struct at_queue_task {
    AST_LIST_ENTRY(at_queue_task) entry;  // Linked list
    unsigned cmdsno;                       // Number of commands
    unsigned cindex;                       // Current command index
    struct cpvt* cpvt;                     // Call private data
    at_queue_cmd_t cmds[0];                // Flexible array
} at_queue_task_t;
```

### Command Structure
```c
typedef struct at_queue_cmd {
    at_cmd_t cmd;           // Command code
    at_res_t res;           // Expected response
    unsigned flags;         // STATIC, IGNORE
    struct timeval timeout; // Timeout value
    char* data;             // Command string
    unsigned length;        // Data length
} at_queue_cmd_t;
```

## Operations

### Add Task to Queue
```c
static at_queue_task_t * at_queue_add(
    struct cpvt * cpvt,
    const at_queue_cmd_t * cmds,
    unsigned cmdsno,
    int prio  // 0=tail, 1=after head
)
```

### Execute Queue
```c
EXPORT_DEF int at_queue_run(struct pvt * pvt)
{
    at_queue_cmd_t * cmd = at_queue_head_cmd_nc(pvt);
    if (cmd && cmd->length > 0) {
        // Write command to device
        fail = at_write(pvt, cmd->data, cmd->length);
        if (!fail) {
            // Set timeout
            cmd->timeout = ast_tvadd(ast_tvnow(), cmd->timeout);
            // Free data (mark as in-flight)
            at_queue_free_data(cmd);
        }
    }
    return fail;
}
```

### Handle Response
```c
EXPORT_DEF void at_queue_remove_cmd(struct pvt* pvt, at_res_t res)
{
    at_queue_task_t * task = AST_LIST_FIRST(&pvt->at_queue);
    if (task) {
        task->cindex++;  // Advance to next command
        
        // Remove task if: all commands done OR response mismatch
        if (task->cindex >= task->cmdsno || 
            (task->cmds[index].res != res && 
             (task->cmds[index].flags & ATQ_CMD_FLAG_IGNORE) == 0)) {
            at_queue_remove(pvt);
        }
    }
}
```

## Timeout Values

| Constant | Value | Use Case |
|----------|-------|----------|
| `ATQ_CMD_TIMEOUT_1S` | 1 | Quick status |
| `ATQ_CMD_TIMEOUT_2S` | 2 | Default |
| `ATQ_CMD_TIMEOUT_5S` | 5 | Network queries |
| `ATQ_CMD_TIMEOUT_10S` | 10 | SIM operations |
| `ATQ_CMD_TIMEOUT_15S` | 15 | Complex ops |
| `ATQ_CMD_TIMEOUT_40S` | 40 | SMS send |

## Example: SMS Send

```c
// Two-stage SMS send
at_queue_cmd_t at_cmd[] = {
    { CMD_AT_CMGS,    RES_SMS_PROMPT, 
      ATQ_CMD_FLAG_DEFAULT, { ATQ_CMD_TIMEOUT_2S, 0 }, NULL, 0 },
    { CMD_AT_SMSTEXT, RES_OK, 
      ATQ_CMD_FLAG_DEFAULT, { ATQ_CMD_TIMEOUT_40S, 0 }, NULL, 0 }
};

// Stage 1: AT+CMGS=<length>
at_cmd[0].data = ast_strdup("AT+CMGS=23\r");
at_cmd[0].length = 11;

// Stage 2: PDU + Ctrl-Z
at_cmd[1].data = ast_malloc(pdu_len + 1);
memcpy(at_cmd[1].data, pdu, pdu_len);
at_cmd[1].data[pdu_len] = 0x1A;  // Ctrl-Z

at_queue_insert_task(cpvt, at_cmd, 2, 0, &task);
at_queue_run(pvt);
```

## State Machine

```
┌─────────────┐
│   IDLE      │◀──────────────────────┐
└──────┬──────┘                       │
       │ queue_run()                  │
       ▼                              │
┌─────────────┐    response          │
│  COMMAND    │─────────────────────▶│ handle_response()
│  SENT       │                      │
└──────┬──────┘                      │
       │                             │
       │ timeout (not implemented)   │
       ▼                             │
┌─────────────┐                      │
│  EXPIRED    │──────────────────────┘
│  (blocked)  │
└─────────────┘
```
