# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Management Layer                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Show Commands  │ Control Commands│  Config Commands        │
│  (read-only)    │  (state-change) │  (persistence)          │
│                 │                 │                         │
│  - devices      │  - start        │  - setgroup             │
│  - device state │  - reset        │  - setgroupimsi         │
│  - statistics   │  - reload       │  - callwaiting          │
│  - version      │  - discovery    │  - changeimei           │
│                 │  - update       │  - diagmode             │
└─────────────────┴─────────────────┴─────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Communication Commands                          │
│  - sms, ussd, pdu, cmd                                      │
└─────────────────────────────────────────────────────────────┘
```

## Command Registration Pattern

```c
static char* cli_<name>(struct ast_cli_entry* e, int cmd, struct ast_cli_args* a)
{
    switch (cmd) {
        case CLI_INIT:
            e->command = "dongle <command>";
            e->usage = "Usage: dongle <command>\n"
                       "       Description\n";
            return NULL;
        case CLI_GENERATE:
            return NULL;
    }
    
    // Validate arguments
    if (a->argc != <expected>) {
        return CLI_SHOWUSAGE;
    }
    
    // Command implementation
    // ...
    
    return CLI_SUCCESS;
}
```

## Show Commands

### dongle show devices
```c
static char* cli_show_devices(...)
{
    // Format: ID Group State RSSI Mode Submode Provider Model Firmware IMEI IMSI Balance
    #define FORMAT1 "%-12.12s %-5.5s %-10.10s %-4.4s %-4.4s %-7.7s %-14.14s %-10.10s %-17.17s %-16.16s %-16.16s %-6.6s\n"
    #define FORMAT2 "%-12.12s %-5d %-10.10s %-4d %-4d %-7d %-14.14s %-10.10s %-17.17s %-16.16s %-16.16s %-6.6s\n"
    
    ast_cli(a->fd, FORMAT1, "ID", "Group", "State", "RSSI", "Mode", 
            "Submode", "Provider Name", "Model", "Firmware", "IMEI", "IMSI", "Balance");
    
    AST_RWLIST_TRAVERSE(&gpublic->devices, pvt, entry) {
        readpvtinfo(pvt);
        ast_cli(a->fd, FORMAT2,
            PVT_ID(pvt),
            CONF_SHARED(pvt, group),
            pvt_str_state(pvt),
            pvt->rssi,
            pvt->linkmode,
            pvt->linksubmode,
            pvt->provider_name,
            pvt->model,
            pvt->firmware,
            pvt->imei,
            pvt->imsi,
            PVT_STAT(pvt, balance));
    }
}
```

### dongle show device state
```c
static char* cli_show_device_state(...)
{
    // Validate device exists
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    // Show call states
    ast_cli(a->fd, "Device: %s\n", PVT_ID(pvt));
    ast_cli(a->fd, "State: %s\n", pvt_str_state(pvt));
    ast_cli(a->fd, "RSSI: %d\n", pvt->rssi);
    
    // Show active calls
    AST_LIST_TRAVERSE(&pvt->calls, cpvt, entry) {
        ast_cli(a->fd, "  Call %d: %s %s\n", 
                cpvt->call_idx,
                call_state2str(cpvt->state),
                cpvt->dir ? "IN" : "OUT");
    }
}
```

### dongle show device statistics
```c
static char* cli_show_device_statistics(...)
{
    // Show counters
    ast_cli(a->fd, "Device: %s\n", PVT_ID(pvt));
    ast_cli(a->fd, "Calls: %d\n", PVT_STAT(pvt, calls));
    ast_cli(a->fd, "Duration: %d seconds\n", PVT_STAT(pvt, duration));
    ast_cli(a->fd, "SMS sent: %d\n", PVT_STAT(pvt, sms_sent));
    ast_cli(a->fd, "SMS received: %d\n", PVT_STAT(pvt, sms_received));
    ast_cli(a->fd, "USSD sent: %d\n", PVT_STAT(pvt, ussd_sent));
    
    // Calculate ACD (Average Call Duration)
    acd = getACD(PVT_STAT(pvt, calls), PVT_STAT(pvt, duration));
    ast_cli(a->fd, "ACD: %d seconds\n", acd);
}
```

## Control Commands

### dongle cmd (Raw AT Command)
```c
static char* cli_dongle_cmd(...)
{
    // Usage: dongle cmd <device> <command>
    if (a->argc != 4) return CLI_SHOWUSAGE;
    
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    const char* at_cmd = a->argv[4];
    
    // Execute via AT queue
    at_enque_cmd_proc(cpvt, at_cmd);
    
    ast_cli(a->fd, "Command queued: %s\n", at_cmd);
    return CLI_SUCCESS;
}
```

### dongle sms
```c
static char* cli_dongle_sms(...)
{
    // Usage: dongle sms <device> <number> <message>
    if (a->argc != 5) return CLI_SHOWUSAGE;
    
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    const char* number = a->argv[4];
    const char* message = a->argv[5];
    
    // Send via helpers.c
    send_sms(pvt->id, number, message, 0, 0, 0, NULL);
    
    ast_cli(a->fd, "SMS queued for send to %s\n", number);
    return CLI_SUCCESS;
}
```

### dongle ussd
```c
static char* cli_dongle_ussd(...)
{
    // Usage: dongle ussd <device> <code>
    if (a->argc != 4) return CLI_SHOWUSAGE;
    
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    const char* code = a->argv[4];
    
    // Send via helpers.c
    send_ussd(pvt->id, code, 0, 0, 0, NULL);
    
    ast_cli(a->fd, "USSD queued for send: %s\n", code);
    return CLI_SUCCESS;
}
```

### dongle reset
```c
static char* cli_dongle_reset(...)
{
    // Usage: dongle reset <device>
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    // Send reset command
    send_reset(pvt);
    
    ast_cli(a->fd, "Device %s reset initiated\n", PVT_ID(pvt));
    return CLI_SUCCESS;
}
```

### dongle update (Firmware)
```c
static char* cli_dongle_update(...)
{
    // Usage: dongle update <device>
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    // Enter diagnostic mode and flash
    ttyprog_sendfile(filename, fd, device);
    
    ast_cli(a->fd, "Firmware update started for %s\n", PVT_ID(pvt));
    return CLI_SUCCESS;
}
```

## Configuration Commands

### dongle setgroup
```c
static char* cli_dongle_setgroup(...)
{
    // Usage: dongle setgroup <device> <group>
    if (a->argc != 5) return CLI_SHOWUSAGE;
    
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    const char* group = a->argv[4];
    
    // Update configuration
    CONF_SHARED(pvt, group) = ast_strdup(group);
    
    // Persist to storage
    writepvtlimits(pvt);
    
    ast_cli(a->fd, "Device %s group set to %s\n", PVT_ID(pvt), group);
    return CLI_SUCCESS;
}
```

### dongle setgroupimsi
```c
static char* cli_dongle_setgroupimsi(...)
{
    // Usage: dongle setgroupimsi <imsi> <group>
    if (a->argc != 4) return CLI_SHOWUSAGE;
    
    const char* imsi = a->argv[3];
    const char* group = a->argv[4];
    
    // Find device by IMSI
    pvt = find_device_by_imsi(imsi);
    if (!pvt) {
        ast_cli(a->fd, "Device with IMSI %s not found\n", imsi);
        return CLI_SUCCESS;
    }
    
    CONF_SHARED(pvt, group) = ast_strdup(group);
    writepvtlimits(pvt);
    
    ast_cli(a->fd, "Device %s group set to %s\n", PVT_ID(pvt), group);
    return CLI_SUCCESS;
}
```

## Tab Completion

```c
static char* complete_device(const char* word, int state)
{
    struct pvt* pvt;
    char* res = NULL;
    int which = 0;
    int wordlen = strlen(word);
    
    AST_RWLIST_RDLOCK(&gpublic->devices);
    AST_RWLIST_TRAVERSE(&gpublic->devices, pvt, entry) {
        if (!strncasecmp(PVT_ID(pvt), word, wordlen) && ++which > state) {
            res = ast_strdup(PVT_ID(pvt));
            break;
        }
    }
    AST_RWLIST_UNLOCK(&gpublic->devices);
    
    return res;
}
```

## Command Table

| Command | Args | Description |
|---------|------|-------------|
| `dongle show devices` | 0 | List all devices |
| `dongle show devicesl` | 0 | List with limits |
| `dongle show devicesd` | 0 | Detailed list |
| `dongle show devicesi` | 0 | Info list |
| `dongle show device settings` | 1 | Show settings |
| `dongle show device state` | 1 | Show state |
| `dongle show device statistics` | 1 | Show statistics |
| `dongle show version` | 0 | Show version |
| `dongle cmd` | 2 | Execute AT command |
| `dongle sms` | 3 | Send SMS |
| `dongle ussd` | 2 | Send USSD |
| `dongle pdu` | 2 | Send PDU |
| `dongle start` | 1 | Start device |
| `dongle reset` | 1 | Reset device |
| `dongle reload` | 0 | Reload config |
| `dongle discovery` | 0 | Discover devices |
| `dongle setgroup` | 2 | Set group |
| `dongle setgroupimsi` | 2 | Set group by IMSI |
| `dongle callwaiting` | 1 | Toggle call waiting |
| `dongle diagmode` | 1 | Enter diagnostic mode |
| `dongle changeimei` | 2 | Change IMEI |
| `dongle update` | 1 | Firmware update |

## Output Formats

### Device State Strings
```c
const char* pvt_str_state(struct pvt* pvt)
{
    switch (pvt->state) {
        case DEV_STATE_NEW: return "new";
        case DEV_STATE_WAIT: return "wait";
        case DEV_STATE_OPEN: return "open";
        case DEV_STATE_INIT: return "init";
        case DEV_STATE_WAIT_SMS: return "wait_sms";
        case DEV_STATE_READY: return "ready";
        case DEV_STATE_HANGUP: return "hangup";
        case DEV_STATE_RESTART: return "restart";
        default: return "unknown";
    }
}
```

### Call State Strings
```c
const char* call_state2str(call_state_t state)
{
    static const char* states[] = {
        "active", "held", "dialing", "alerting",
        "incoming", "waiting", "released", "initialize"
    };
    return enum2str(state, states, ITEMS_OF(states));
}
```

## Error Handling

### Device Not Found
```c
pvt = find_device(device_name);
if (!pvt) {
    ast_cli(a->fd, "Device %s not found\n", device_name);
    return CLI_SUCCESS;  // Don't fail, just inform
}
```

### Invalid Arguments
```c
if (a->argc != expected) {
    return CLI_SHOWUSAGE;  // Shows usage help
}
```

### Command Queued
```c
// For async operations (SMS, USSD, AT commands)
ast_cli(a->fd, "Command queued for execution\n");
return CLI_SUCCESS;
```

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of cli.c (1643 lines), cli.h
