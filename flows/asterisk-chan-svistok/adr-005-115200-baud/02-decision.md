# Solution

## Serial Configuration

```c
int opentty(const char* dev)
{
    int fd = open(dev, O_RDWR | O_NOCTTY);
    if (fd < 0) return -1;
    
    struct termios term_attr;
    tcgetattr(fd, &term_attr);
    
    // Configure: 115200 8N1 HW flow control
    term_attr.c_cflag = B115200 | CS8 | CREAD | CRTSCTS;
    term_attr.c_iflag = 0;
    term_attr.c_oflag = 0;
    term_attr.c_lflag = 0;
    term_attr.c_cc[VMIN] = 1;
    term_attr.c_cc[VTIME] = 0;
    
    tcsetattr(fd, TCSAFLUSH, &term_attr);
    return fd;
}
```

## Parameter Breakdown

| Parameter | Value | Description |
|-----------|-------|-------------|
| Baud rate | 115200 | Bits per second |
| Data bits | 8 (CS8) | 8 bits per character |
| Stop bits | 1 (implicit) | 1 stop bit |
| Parity | None (implicit) | No parity |
| Flow control | CRTSCTS | Hardware (RTS/CTS) |
| Input mode | 0 | Raw, no processing |
| Output mode | 0 | Raw, no processing |
| Local mode | 0 | Raw mode |
| VMIN | 1 | Block until 1 char available |
| VTIME | 0 | No timeout |

## Throughput Calculation

```
115200 baud / 10 bits per character = 11520 bytes/second
  - 8 data bits
  - 1 start bit
  - 1 stop bit
  - No parity

Effective throughput: ~11.25 KB/s
```

## Voice Audio Requirements

```
G.711 codec: 8000 samples/s × 8 bits = 64000 bits/s = 8 KB/s
115200 baud provides sufficient bandwidth for voice + overhead
```

## Write Operation

```c
size_t write_all(int fd, const char* buf, size_t count)
{
    size_t total = 0;
    unsigned errs = 10;
    
    while (count > 0) {
        ssize_t out_count = write(fd, buf, count);
        if (out_count <= 0) {
            if (errno == EINTR || errno == EAGAIN) {
                if (--errs == 0) break;
                continue;  // Retry
            }
            break;
        }
        errs = 10;
        count -= out_count;
        buf += out_count;
        total += out_count;
    }
    return total;
}
```

## Read Operation

```c
int readtty_all(int fd, char* buf, int maxsize, int *readed)
{
    int bytes;
    int r = ioctl(fd, FIONREAD, &bytes);  // Check available
    
    if (r == 0 && bytes > 0) {
        *readed = read(fd, buf, maxsize);
    }
    return r;
}
```

## Device Locking (Commented Out)

```c
// Current implementation has locking disabled:
// pid = lock_try(dev);
// if (pid != 0) { close(fd); return -1; }

// Lock file: /var/lock/LOCK..ttyUSB0
// Contains: PID of owning process
```

## Hardware Requirements

- USB-serial adapter must support RTS/CTS
- Cable must have RTS/CTS wires connected
- Some adapters require `setserial` configuration
