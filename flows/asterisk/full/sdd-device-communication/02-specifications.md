# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               Device Communication Layer                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│    TTY Layer    │  Ring Buffer    │   I/O Multiplexing      │
│   (tty_v2.c)    │ (ringbuffer.h)  │      (select.h)         │
│                 │                 │                         │
│  - opentty      │  - rb_read_iov  │  - pvt_select           │
│  - closetty     │  - rb_write_iov │  - call_request         │
│  - lock_try     │  - read_until   │  - pvt_select_stat      │
│  - write_all    │  - rb_used/free │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Serial Port Configuration

### Termios Settings
```c
struct termios term_attr;

// Get current attributes
tcgetattr(fd, &term_attr);

// Configure for 115200 8N1 with hardware flow control
term_attr.c_cflag = B115200 | CS8 | CREAD | CRTSCTS;
term_attr.c_iflag = 0;          // No input processing
term_attr.c_oflag = 0;          // No output processing
term_attr.c_lflag = 0;          // No local processing (raw mode)
term_attr.c_cc[VMIN] = 1;       // Block until 1 char available
term_attr.c_cc[VTIME] = 0;      // No timeout

// Apply settings, drain output queue
tcsetattr(fd, TCSAFLUSH, &term_attr);
```

### Baud Rate Constants
| Baud | Constant |
|------|----------|
| 115200 | B115200 |
| 57600 | B57600 |
| 38400 | B38400 |
| 19200 | B19200 |
| 9600 | B9600 |

## Device Locking

### Lock File Path
```c
// Format: /var/lock/LOCK..{basename}
// Example: /var/lock/LOCK..ttyUSB0
lock_build(devname, buf, length) {
    basename = strrchr(devname, '/');
    if (basename) basename++;
    else basename = devname;
    snprintf(buf, length, "/var/lock/LOCK..%s", basename);
}
```

### Lock Check and Create
```c
static int lock_try(const char* devname)
{
    char name[256];
    char pidb[21];
    
    lock_build(devname, name, sizeof(name));
    
    fd = open(name, O_RDONLY);
    if (fd >= 0) {
        // Read PID from lock file
        len = read(fd, pidb, sizeof(pidb) - 1);
        pidb[len] = 0;
        pid = strtol(pidb, NULL, 10);
        
        // Check if process still exists
        if (kill(pid, 0) == 0) {
            close(fd);
            return pid;  // Locked by another process
        }
        // Stale lock - process dead
        close(fd);
        unlink(name);  // Remove stale lock
    }
    
    // Create new lock
    lock_create(name);
    return 0;  // Lock acquired
}
```

### Lock File Content
```
{PID}
```
Example: `12345` (ASCII)

## Device Open

```c
int opentty(const char* dev)
{
    int fd;
    struct termios term_attr;
    
    // Open device
    fd = open(dev, O_RDWR | O_NOCTTY);
    if (fd < 0) return -1;
    
    // Get and configure attributes
    if (tcgetattr(fd, &term_attr) != 0) {
        close(fd);
        return -1;
    }
    
    term_attr.c_cflag = B115200 | CS8 | CREAD | CRTSCTS;
    term_attr.c_iflag = 0;
    term_attr.c_oflag = 0;
    term_attr.c_lflag = 0;
    term_attr.c_cc[VMIN] = 1;
    term_attr.c_cc[VTIME] = 0;
    
    tcsetattr(fd, TCSAFLUSH, &term_attr);
    
    // Note: Locking currently disabled in code
    // pid = lock_try(dev);
    // if (pid != 0) { close(fd); return -1; }
    
    return fd;
}
```

## Device Close

```c
void closetty(const char* dev, int fd)
{
    close(fd);
    
    // Note: Lock removal currently disabled in code
    // lock_build(dev, name, sizeof(name));
    // unlink(name);
}
```

## Write Operations

### Write All (Guaranteed Full Write)
```c
size_t write_all(int fd, const char* buf, size_t count)
{
    ssize_t out_count;
    size_t total = 0;
    unsigned errs = 10;
    
    while (count > 0) {
        out_count = write(fd, buf, count);
        if (out_count <= 0) {
            if (errno == EINTR || errno == EAGAIN) {
                errs--;
                if (errs != 0) continue;  // Retry
            }
            break;  // Error
        }
        errs = 10;  // Reset error count
        count -= out_count;
        buf += out_count;
        total += out_count;
    }
    return total;
}
```

### AT Command Write with Logging
```c
int at_write(struct pvt* pvt, const char* buf, size_t count)
{
    // Log to file
    at_log(pvt, dn, strlen(dn));  // Timestamp
    at_log(pvt, " >> ", 4);
    at_log(pvt, buf, count);
    
    // Debug log
    ast_debug(5, "[%s] [%.*s]\n", PVT_ID(pvt), (int)count, buf);
    
    // Write to device
    wrote = write_all(pvt->data_fd, buf, count);
    PVT_STAT(pvt, d_write_bytes) += wrote;
    
    if (wrote != count) {
        ast_debug(1, "[%s] write() error: %d\n", PVT_ID(pvt), errno);
    }
    
    return wrote != count;  // 0 = success
}
```

## Read Operations

### Read Available Bytes
```c
int readtty_all(int fd, char* buf, int maxsize, int *readed)
{
    *readed = 0;
    int bytes;
    int r = ioctl(fd, FIONREAD, &bytes);
    
    if (r == -1) return r;
    
    if (bytes > 0) {
        *readed = read(fd, buf, maxsize);
    }
    
    return r;
}
```

## Ring Buffer

### Structure
```c
struct ringbuffer {
    void* buffer;    // Data buffer pointer
    size_t size;     // Total buffer size
    size_t used;     // Bytes currently used
    size_t read;     // Read position
    size_t write;    // Write position
};
```

### Initialization
```c
void rb_init(struct ringbuffer* rb, void* buf, size_t size)
{
    rb->buffer = buf;
    rb->size   = size;
    rb->used   = 0;
    rb->read   = 0;
    rb->write  = 0;
}
```

### Status
```c
size_t rb_used(const struct ringbuffer* rb) { return rb->used; }
size_t rb_free(const struct ringbuffer* rb) { return rb->size - rb->used; }
```

### Vector Read (for writev)
```c
int rb_read_all_iov(const struct ringbuffer* rb, struct iovec iov[2])
{
    // Returns 1 or 2 iovec entries depending on wrap
}

int rb_read_until_char_iov(const struct ringbuffer* rb, 
                           struct iovec iov[2], char delim)
{
    // Find delimiter and return iovec up to and including it
}
```

### Vector Write (for readv)
```c
int rb_write_iov(const struct ringbuffer* rb, struct iovec iov[2])
{
    // Returns 1 or 2 iovec entries for free space
}
```

### Update Positions
```c
size_t rb_read_upd(struct ringbuffer* rb, size_t len)
{
    rb->read = (rb->read + len) % rb->size;
    rb->used -= len;
    return len;
}

size_t rb_write_upd(struct ringbuffer* rb, size_t len)
{
    rb->write = (rb->write + len) % rb->size;
    rb->used += len;
    return len;
}
```

## I/O Multiplexing

### Call Request Structure
```c
typedef struct call_request {
    const char * resource;           // For CMD parameters
    const struct ast_channel * requestor;
    const struct public_state * state;
    int opts;
    
    int dial_type;  // 1 = group type L0<=HZ
    int group;
    int limitnum;
    char limittype;
    
    char numberdial[32];
    char numberb[32];
    char numbera[32];
    
    // ... routing parameters
} call_request_t;
```

### Device Selection
```c
typedef struct pvt_select {
    struct pvt * pvt;
    int IMB_pos;
    char IMB_type;
    int diff;
    long sou_diff_start;
} pvt_select_t;

void pvt_select_stat(struct call_request *cr, struct pvt_select * pvt_select);
```

## Error Handling

### Open Errors
| Error | Return |
|-------|--------|
| Device not found | -1 |
| Permission denied | -1 |
| tcgetattr fails | -1 |

### Write Errors
| Error | Handling |
|-------|----------|
| EINTR | Retry (max 10) |
| EAGAIN | Retry (max 10) |
| Other | Log and return error |

### Read Errors
| Error | Handling |
|-------|----------|
| ioctl fails | Return -1 |
| read fails | Return bytes read (may be 0) |

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of tty_v2.c (221 lines), ringbuffer.h, select.h
