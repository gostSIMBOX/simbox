# ADR-001: AT Command Queue Architecture

## Status
DRAFT

## Type
Enabling

## Context
The chan_dongle driver needs to communicate with Huawei UMTS dongles using AT commands over a serial connection. The communication has several challenges:

1. **Asynchronous responses**: Commands are sent, but responses arrive asynchronously
2. **Command sequencing**: Some operations require multiple commands in sequence (e.g., SMS send)
3. **Timeout handling**: Commands may not receive responses due to device issues
4. **Response matching**: Responses must be matched to the originating command
5. **Priority handling**: Some commands need to be executed before others

## Decision
Use a **task-based command queue with timeout tracking and response matching**.

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    AT Command Queue                          │
├─────────────────────────────────────────────────────────────┤
│  Task Queue (linked list)                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │ Task 1   │───▶│ Task 2   │───▶│ Task 3   │               │
│  │ 3 cmds   │    │ 1 cmd    │    │ 2 cmds   │               │
│  └──────────┘    └──────────┘    └──────────┘               │
├─────────────────────────────────────────────────────────────┤
│  Per-Command:                                                │
│  - Command code (at_cmd_t)                                   │
│  - Expected response (at_res_t)                              │
│  - Timeout value (1s-40s)                                    │
│  - Flags (STATIC, IGNORE)                                    │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Choices

1. **Task-based grouping**: Multiple related commands grouped into single task
   - SMS send: `AT+CMGS=<len>` + PDU data
   - Initialization: 10+ commands in sequence

2. **Expected response per command**: Each command specifies expected response type
   - Enables automatic response matching
   - Mismatch triggers error handling

3. **Configurable timeouts**: Different timeout values for different operations
   - 1s: Quick status checks
   - 2s: Standard commands (default)
   - 5s-40s: Long operations (SMS send)

4. **Flags for memory management**:
   - STATIC: Don't free command data (static strings)
   - IGNORE: Don't fail on response mismatch

## Consequences

### Positive
- **Reliable command execution**: Queue ensures sequential execution
- **Automatic response matching**: No manual correlation needed
- **Timeout protection**: Hung commands don't block indefinitely
- **Memory efficient**: STATIC flag avoids unnecessary allocations
- **Flexible**: Task grouping supports complex operations

### Negative
- **Complexity**: Queue management adds code complexity
- **Memory overhead**: Task structures require allocation
- **Timeout handling**: Current implementation has timeout check commented out

### Risks
- Queue overflow if commands accumulate faster than execution
- Timeout handling not fully implemented (commented out in code)
- Response mismatch handling may be too aggressive (removes entire task)

## Related Decisions
- PDU mode for SMS (ADR-002)
- 115200 baud serial communication (ADR-005)

## References
- `at_queue.c` - Queue implementation (412 lines)
- `at_command.h` - Command enumeration
- `at_response.h` - Response enumeration

## Notes
The timeout expiration check is currently disabled in the code (`#if 0` block in `at_queue_run()`). This should be revisited for production use.
