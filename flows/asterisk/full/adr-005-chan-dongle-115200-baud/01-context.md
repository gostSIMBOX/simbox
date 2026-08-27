# ADR-005: 115200 Baud Serial Communication

## Status
DRAFT

## Type
Constraining

## Context
The chan_dongle driver communicates with Huawei UMTS dongles via USB-to-serial interface. The serial communication parameters must be configured correctly for reliable communication.

### Requirements
- High-speed data transfer for voice audio
- Reliable command/response communication
- Hardware flow control for data integrity
- Compatible with all supported Huawei devices

### Constraints
- Huawei devices use standard USB CDC-ACM interface
- Devices expose serial port at `/dev/ttyUSB*`
- Standard serial parameters apply (baud, data bits, stop bits, parity)
- Linux and FreeBSD support required

## Decision
Use **115200 baud, 8N1, hardware flow control (CRTSCTS)** for all serial communication.

### Configuration
```c
term_attr.c_cflag = B115200 | CS8 | CREAD | CRTSCTS;
term_attr.c_iflag = 0;          // Raw input
term_attr.c_oflag = 0;          // Raw output
term_attr.c_lflag = 0;          // Raw mode
term_attr.c_cc[VMIN] = 1;       // Block until 1 char
term_attr.c_cc[VTIME] = 0;      // No timeout
```

## Consequences

### Positive
- **High throughput**: 115200 baud supports voice audio streaming
- **Standard rate**: 115200 is widely supported
- **Flow control**: Hardware flow control prevents buffer overruns
- **Raw mode**: No character processing, transparent data transfer

### Negative
- **Fixed rate**: Cannot adapt to devices requiring different baud
- **Hardware dependency**: Requires RTS/CTS lines (USB-serial adapters must support)
- **Blocking reads**: VMIN=1 may block indefinitely if device stops responding

### Technical Impact
- All devices configured identically
- No baud rate negotiation
- Flow control required (may need adapter configuration)
- Blocking read behavior

## Alternatives Considered

### Lower Baud Rates (9600, 19200, 57600)
- **Pros**: More compatible with older devices
- **Cons**: Insufficient for voice audio, slower command response

### Software Flow Control (XON/XOFF)
- **Pros**: Works without hardware flow control lines
- **Cons**: In-band control characters interfere with binary data

### Non-blocking I/O
- **Pros**: No indefinite blocking
- **Cons**: More complex, requires polling or select()

## Related Decisions
- AT command queue architecture (ADR-001)
- Qualcomm DIAG protocol (ADR-004)

## References
- `tty_v2.c` - Serial port implementation
- `termios.h` - POSIX terminal interface

## Notes
Some USB-serial adapters may require configuration to enable hardware flow control. The current implementation has device locking commented out, which may cause issues with concurrent access.
