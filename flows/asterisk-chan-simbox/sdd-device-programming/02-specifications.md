# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Device Programming Layer                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Core Protocol  │  Programmator   │   Integration           │
│ (ttyprog_core)  │ (ttyprog_prog)  │  (ttyprog_svistok)      │
│                 │                 │                         │
│  - Diag mode    │  - File transfer│  - Asterisk logging     │
│  - HDLC frames  │  - Progress     │  - CLI integration      │
│  - Sequences    │  - State persist│  - Error handling       │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Diagnostic Mode Entry

### Command Sequence
```c
// Command 0: Enter diagnostic mode
unsigned char cmd0[] = {
    0x41, 0x54, 0x24, 0x51, 0x43, 0x44, 0x4D, 0x47, 0x0D, 0x0A
};  // "AT$QCDMG\r\n"

unsigned char res0[] = {
    0x24, 0x51, 0x43, 0x44, 0x4D, 0x47, 0x0D, 0x0D, 0x0A, 
    0x4F, 0x4B, 0x0D, 0x0A
};  // "$QCDMG\r\r\nOK\r\n"

// Command 1: Enable diagnostic logging
unsigned char cmd1[] = {
    0x41, 0x54, 0x5E, 0x44, 0x49, 0x53, 0x4C, 0x4F, 0x47, 
    0x3D, 0x32, 0x35, 0x35, 0x0D, 0x0A, 0x7E, 0x0C, 0x14, 0x3A, 0x7E
};  // "AT^DISLOG=255\r\n" + HDLC probe

unsigned char res1[] = {
    0xD2, 0x7A, 0x7E
};  // Diagnostic mode response
```

### Entry Function
```c
void ttyprog_set_diagmode(int fd)
{
    // Send AT$QCDMG
    writetty_all(fd, cmd0, sizeof(cmd0));
    usleep(100000);
    
    // Send AT^DISLOG=255
    writetty_all(fd, cmd1, sizeof(cmd1));
    usleep(100000);
    
    // Wait for mode switch
    sleep(25);
}
```

## HDLC Frame Structure

### Frame Format
```
+--------+--------+--------+--------+--------+--------+
|  0x7E  |  CMD   |  LEN   | DATA... |  CRC   |  0x7E  |
+--------+--------+--------+--------+--------+--------+
   Start  Command  Length   Payload   Check    End
```

### Known Frames
| Command | Response | Description |
|---------|----------|-------------|
| `cmd0/res0` | Enter diagnostic mode |
| `cmd1/res1` | Enable logging |
| `cmd2/res2` | HDLC probe |
| `cmd4/res4` | Query ESN (CDMA) |
| `cmd5/res5` | Query firmware version |
| `cmd6/res6` | Acknowledge |
| `cmd7/res7` | Prepare for programming |
| `cmd8/res8` | Enter programming mode |

### Firmware Version Query
```c
unsigned char cmd5[] = {
    0x4B, 0xC9, 0x03, 0xFF, 0xE8, 0x99, 0x7E
};

unsigned char res5[] = {
    0x03, 0xFF, 
    0x31, 0x31, 0x2E, 0x36, 0x30, 0x39, 0x2E, 0x31, 0x38, 
    0x2E, 0x30, 0x30, 0x2E, 0x30, 0x30,  // "11.609.18.00.00"
    0x45, 0x31, 0x35, 0x35, 0x30, 0x46, 0x43, 0x44, 
    0x36, 0x41, 0x54, 0x43, 0x50, 0x55, 0x20, 0x56, 
    0x65, 0x72, 0x2E, 0x41,  // "E1550FCD6ATCPU Ver.A"
    0x89, 0x93, 0x7E
};
```

## Programming Sequence

### Main Flow (ttyprog_programmator.c)
```c
void main(int argc, char* argv[])
{
    // Arguments: port device filename
    char* port = argv[1];      // e.g., /dev/ttyUSB5
    char* device = argv[2];    // e.g., 3-1.1.1
    char* filename = argv[3];  // e.g., 123.bin
    
    // Initialize state
    saveparams(device, "state", "init");
    saveparami(device, "progress", 0);
    sleep(5);
    
    // Open port
    int fd = opentty(port);
    
    // Enter diagnostic mode
    saveparams(device, "state", "diag");
    saveparami(device, "progress", 1);
    ttyprog_set_diagmode(fd);
    
    // Wait for mode switch
    saveparams(device, "state", "wait");
    saveparami(device, "progress", 10);
    sleep(25);
    
    // Send firmware
    saveparams(device, "state", "update");
    saveparami(device, "progress", 20);
    ttyprog_sendfile(filename, fd, device);
    
    // Complete
    saveparams(device, "state", "done");
    saveparami(device, "progress", 100);
    
    closetty(port, fd);
}
```

### State Transitions
```
init (0%) 
  │
  ▼
diag (1%) ──→ Enter AT$QCDMG
  │
  ▼
wait (10%) ──→ Wait 25 seconds
  │
  ▼
update (20%) ──→ Transfer firmware
  │
  ▼
done (100%)
```

## State Persistence

### Save String Parameter
```c
void saveparams(const char* device, char* name, char* value)
{
    char filename[256] = "/var/simnode/";
    strcat(filename, device);
    strcat(filename, ".");
    strcat(filename, name);
    
    FILE* fd = fopen(filename, "w");
    if (fd) {
        fprintf(fd, "%s", value);
        fclose(fd);
    }
    printf("%s %s=%s\n", device, name, value);
}
```

### Save Integer Parameter
```c
void saveparami(const char* device, char* name, int value)
{
    char filename[256] = "/var/simnode/";
    strcat(filename, device);
    strcat(filename, ".");
    strcat(filename, name);
    
    FILE* fd = fopen(filename, "w");
    if (fd) {
        fprintf(fd, "%d", value);
        fclose(fd);
    }
    printf("%s %s=%d\n", device, name, value);
}
```

### State Files
| File | Content |
|------|---------|
| `{device}.state` | Current state string |
| `{device}.progress` | Progress percentage (0-100) |

## Firmware Transfer

### Send File
```c
void ttyprog_sendfile(const char* filename, int fd, const char* device)
{
    FILE* f = fopen(filename, "rb");
    if (!f) {
        tty_log(NULL, "Cannot open firmware file: %s\n", filename);
        saveparams(device, "state", "error");
        return;
    }
    
    // Get file size
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    // Transfer in chunks
    int sent = 0;
    char buffer[1024];
    while ((read = fread(buffer, 1, sizeof(buffer), f)) > 0) {
        // HDLC frame and send
        send_hdlc_frame(fd, buffer, read);
        sent += read;
        
        // Update progress
        int progress = 20 + (sent * 80 / size);
        saveparami(device, "progress", progress);
    }
    
    fclose(f);
}
```

### HDLC Frame Send
```c
void send_hdlc_frame(int fd, const char* data, int length)
{
    // Build HDLC frame
    unsigned char frame[2048];
    int pos = 0;
    
    frame[pos++] = 0x7E;  // Start delimiter
    // ... add command, length, data, CRC
    frame[pos++] = 0x7E;  // End delimiter
    
    writetty_all(fd, frame, pos);
}
```

## Logging

### Log Function
```c
void tty_log(FILE* fd, char* fmt, ...)
{
    char buf[512];
    va_list ap;
    va_start(ap, fmt);
    vsprintf(buf, fmt, ap);
    va_end(ap);
    
    if (fd == NULL) {
        // Asterisk logging
        ast_verb(3, "%s", buf);
    } else {
        // File logging
        fprintf(fd, "%s", buf);
    }
}
```

### Log Format
```
[TIMESTAMP] [STATE] Message
```

## Error Handling

### File Open Error
```c
FILE* f = fopen(filename, "rb");
if (!f) {
    tty_log(NULL, "Cannot open firmware file: %s\n", filename);
    saveparams(device, "state", "error");
    saveparams(device, "error", "File not found");
    return;
}
```

### Transfer Error
```c
if (writetty_all(fd, buffer, read) != read) {
    tty_log(NULL, "Write error during transfer\n");
    saveparams(device, "state", "error");
    return;
}
```

### Timeout
```c
// After sending command, wait for response
int timeout = 5;  // seconds
while (timeout > 0) {
    if (readtty_all(fd, buf, sizeof(buf), &received) == 0) {
        if (received > 0) break;  // Got response
    }
    sleep(1);
    timeout--;
}
if (timeout == 0) {
    tty_log(NULL, "Timeout waiting for response\n");
    return -1;
}
```

## CLI Integration

### dongle update Command
```c
static char* cli_dongle_update(struct ast_cli_entry* e, 
                                int cmd, 
                                struct ast_cli_args* a)
{
    switch (cmd) {
        case CLI_INIT:
            e->command = "dongle update";
            e->usage = "Usage: dongle update <device>\n"
                       "       Update device firmware\n";
            return NULL;
        case CLI_GENERATE:
            return NULL;
    }
    
    if (a->argc != 4) return CLI_SHOWUSAGE;
    
    pvt = find_device(a->argv[3]);
    if (!pvt) return CLI_SHOWUSAGE;
    
    // Start firmware update in background
    ttyprog_start_update(pvt);
    
    ast_cli(a->fd, "Firmware update started for %s\n", PVT_ID(pvt));
    return CLI_SUCCESS;
}
```

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of ttyprog_core.c (305 lines), ttyprog_programmator.c, ttyprog_svistok.c
