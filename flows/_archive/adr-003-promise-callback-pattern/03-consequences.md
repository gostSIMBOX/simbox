# ADR 003: Promise Callback Pattern - Consequences

## Technical Consequences

### Architecture Impact

- **Constraint**: All native calls must be wrapped in Promises
- **Enabling**: Applications can use async/await
- **Pattern**: Consistent error handling across all methods

### Code Impact

Files affected:
- `src/Endpoint.js` - All 10+ call control methods
- `src/tele_endpoint.js` - Call control methods
- Any future native module wrappers

### Testing Impact

- Mock native callbacks in unit tests
- Test both success and failure paths
- Verify Promise resolution/rejection
- Test edge cases (null data, boolean returns)

## Operational Consequences

### Runtime Behavior

- All async operations return Promises
- Errors propagate through Promise chain
- Unhandled rejections possible if not caught
- Async/await syntax encouraged

### Performance

- Minimal overhead from Promise wrapping (microseconds)
- No blocking operations
- All operations already async (native calls)

## Error Handling Consequences

### Error Format

Current implementation:
```javascript
// Error may be string or object
reject(data);  // data could be "Native error" or { code: 500, message: "Error" }
```

**Issue**: Inconsistent error format from native module.

**Recommendation**: Standardize error format:
```javascript
if (!successful) {
    const error = typeof data === 'string' 
        ? new Error(data)
        : new Error(JSON.stringify(data));
    error.nativeData = data;
    reject(error);
}
```

### Error Messages

Applications may receive:
- Raw strings from native module
- Error objects
- Custom error data structures

**Impact**: Applications must handle multiple error formats.

## Developer Experience

### Positive

1. **Familiar Pattern**: Promises are standard JavaScript
2. **Clean Syntax**: Async/await is readable
3. **Error Propagation**: Try/catch blocks work naturally
4. **Tooling**: IDE autocomplete for Promise methods

### Negative

1. **Error Format Uncertainty**: Don't know what type error will be
2. **Stack Traces**: May lose native stack information
3. **Debugging**: Hard to trace errors through Promise chain

### Learning Curve

- Junior developers: Must understand Promises and async/await
- Experienced developers: Familiar pattern, minimal learning

## Maintenance Consequences

### Adding New Methods

Template for all new native module methods:
```javascript
newMethod(param1, param2) {
    return new Promise((resolve, reject) => {
        NativeModules.TeleModule.newMethod(param1, param2, (successful, data) => {
            if (successful) {
                resolve(data);
            } else {
                reject(data);
            }
        });
    });
}
```

### Refactoring Risk

Changing callback pattern would require:
- Updating all method implementations
- Testing all error paths
- Potential breaking change for applications

## Documentation Impact

Must document:
1. **Return types**: All methods return Promises
2. **Error types**: What errors may be thrown
3. **Examples**: Show async/await and .then()/.catch() usage
4. **Edge cases**: Document special handling (like `data === true`)

### Example Documentation

```javascript
/**
 * Answer an incoming call.
 *
 * @param {Call} call - Call instance to answer
 * @returns {Promise<any>} Resolves on success
 * @throws {any} Error data from native module
 *
 * @example
 * try {
 *     await endpoint.answerCall(call);
 *     console.log('Call answered');
 * } catch (error) {
 *     console.error('Failed to answer:', error);
 * }
 */
```

## Migration Considerations

### If Changing Pattern

If we ever change to a different error handling pattern:
- Major version bump required
- Deprecation warnings for old pattern
- Migration guide for applications
- Backward compatibility layer (temporary)

### Version History

- Current: Promise-based with (successful, data) tuple
- Previous: Unknown (no version history in analyzed code)

## Security Considerations

- Error messages may expose internal implementation details
- Consider sanitizing error messages before passing to application
- Don't leak sensitive data in error objects

## Future Considerations

### Potential Improvements

1. **Custom Error Classes**: Create TelephonyError with standardized format
2. **Error Codes**: Add numeric error codes for programmatic handling
3. **Error Recovery**: Provide suggestions in error messages
4. **Logging**: Log errors before rejecting for debugging

### Example: Custom Error Class

```javascript
class TelephonyError extends Error {
    constructor(message, code, nativeData) {
        super(message);
        this.name = 'TelephonyError';
        this.code = code;
        this.nativeData = nativeData;
    }
}

// Usage
if (!successful) {
    reject(new TelephonyError('Failed to answer call', 'ANSWER_FAILED', data));
}
```

## Stakeholder Impact

### Application Developers

- **Benefit**: Clean async/await API
- **Requirement**: Must handle Promises properly
- **Risk**: Unhandled promise rejections if not careful

### Library Maintainers

- **Benefit**: Consistent pattern across all methods
- **Requirement**: Must maintain Promise wrappers
- **Risk**: Breaking change if pattern changes

### End Users

- **No direct impact**: Implementation detail
- **Benefit**: More reliable error handling in apps
- **Risk**: App crashes if errors not handled

---

*Generated by /legacy - Legacy Analysis Flow*  
*Status: DRAFT - Requires human review*
