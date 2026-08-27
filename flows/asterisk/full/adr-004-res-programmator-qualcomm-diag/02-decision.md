# Solution

## DIAG Mode Entry Sequence

```c
// Command 0: Enter diagnostic mode
unsigned char cmd0[] = "AT$QCDMG\r\n";

// Command 1: Enable diagnostic logging
unsigned char cmd1[] = "AT^DISLOG=255\r\n" + HDLC_probe;

// Response indicates DIAG mode active
unsigned char res1[] = {0xD2, 0x7A, 0x7E};
```

## HDLC Frame Format

```
+--------+--------+--------+--------+--------+--------+
|  0x7E  |  CMD   |  LEN   | DATA... |  CRC   |  0x7E  |
+--------+--------+--------+--------+--------+--------+
```

## Known DIAG Commands

| Command | Response | Description |
|---------|----------|-------------|
| `cmd0/res0` | Enter diagnostic mode |
| `cmd1/res1` | Enable logging |
| `cmd5/res5` | Query firmware version |
| `cmd8/res8` | Enter programming mode |

### Firmware Version Query
```c
unsigned char cmd5[] = {0x4B, 0xC9, 0x03, 0xFF, 0xE8, 0x99, 0x7E};

// Response includes:
// - Firmware version: "11.609.18.00.00"
// - Device model: "E1550FCD6ATCPU Ver.A"
```

## Programming Sequence

```c
void main(int argc, char* argv[])
{
    // 1. Initialize
    saveparams(device, "state", "init");
    saveparami(device, "progress", 0);
    
    // 2. Open port
    int fd = opentty(port);
    
    // 3. Enter DIAG mode
    saveparams(device, "state", "diag");
    saveparami(device, "progress", 1);
    ttyprog_set_diagmode(fd);
    
    // 4. Wait for mode switch
    saveparams(device, "state", "wait");
    saveparami(device, "progress", 10);
    sleep(25);
    
    // 5. Transfer firmware
    saveparams(device, "state", "update");
    saveparami(device, "progress", 20);
    ttyprog_sendfile(filename, fd, device);
    
    // 6. Complete
    saveparams(device, "state", "done");
    saveparami(device, "progress", 100);
    
    closetty(port, fd);
}
```

## State Persistence

```
/var/simnode/
├── {device}.state    # init/diag/wait/update/done
└── {device}.progress # 0-100 percentage
```

## Progress Tracking

| State | Progress | Description |
|-------|----------|-------------|
| init | 0% | Starting |
| diag | 1% | Entering DIAG mode |
| wait | 10% | Waiting for mode switch |
| update | 20-99% | Transferring firmware |
| done | 100% | Complete |

## Error Handling

```c
// File open error
FILE* f = fopen(filename, "rb");
if (!f) {
    saveparams(device, "state", "error");
    saveparams(device, "error", "File not found");
    return;
}

// Transfer error
if (write_error) {
    saveparams(device, "state", "error");
    return;
}
```

## CLI Integration

```
dongle update <device>
  - Start firmware update
  - Shows progress via state files
```
