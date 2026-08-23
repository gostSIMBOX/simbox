# ADR-005: Immutable Dart Data Models

> Enabling architectural decision: Value objects for state consistency and predictability

## Status

DRAFT

## Type

Enabling - This decision enables predictable state management and simplifies reasoning about code.

## Context

The Flutter plugin needs to represent SIP entities in Dart:

- Endpoint (SIP initialization state)
- Account (SIP account configuration and status)
- AccountRegistration (registration status)
- Call (active call state and metadata)

**Requirements:**
1. State must be consistent across operations
2. Changes must be explicit and trackable
3. Equality comparisons needed for UI updates
4. Serialization for platform channel communication
5. Thread-safe (Dart isolates may copy data)

**Constraints:**
- Data crosses platform boundary (Kotlin → Dart)
- Maps received from MethodChannel are mutable
- UI needs to compare objects for changes
- State changes come from events, not mutation

## Decision

We will use **immutable data classes** with value semantics for all Dart models:

### Architecture Pattern

```
┌─────────────────┐
│  Platform Data  │
│  (Map<String,   │
│   dynamic>)     │
└────────┬────────┘
         │ fromMap()
         ▼
┌─────────────────┐
│  Immutable      │
│  Data Class     │  ← final fields
│  (Dart)         │  ← No setters
└────────┬────────┘
         │ toMap()
         ▼
┌─────────────────┐
│  Serialized     │
│  for Platform   │
└─────────────────┘
```

### Implementation Details

1. **All fields are final** (immutable after construction)
2. **Factory constructors** for deserialization (fromMap)
3. **toMap() methods** for serialization
4. **Value-based equality** (== and hashCode)
5. **toString()** for debugging

### Code Pattern

```dart
// account.dart
class Account {
  final int id;
  final String uri;
  final String name;
  final String username;
  final String domain;
  final String password;
  final String? proxy;
  final String? transport;
  final String? contactParams;
  final String? contactUriParams;
  final String? regServer;
  final int? regTimeout;
  final String? regContactParams;
  final Map<String, dynamic>? regHeaders;
  final AccountRegistration registration;

  Account({
    required this.id,
    required this.uri,
    required this.name,
    required this.username,
    required this.domain,
    required this.password,
    this.proxy,
    this.transport,
    this.contactParams,
    this.contactUriParams,
    this.regServer,
    this.regTimeout,
    this.regContactParams,
    this.regHeaders,
    required this.registration,
  });

  // Factory constructor for deserialization
  factory Account.fromMap(Map<String, dynamic> map) {
    return Account(
      id: map['id'] as int,
      uri: map['uri'] as String,
      name: map['name'] as String,
      username: map['username'] as String,
      domain: map['domain'] as String,
      password: map['password'] as String,
      proxy: map['proxy'] as String?,
      transport: map['transport'] as String?,
      contactParams: map['contactParams'] as String?,
      contactUriParams: map['contactUriParams'] as String?,
      regServer: map['regServer'] as String?,
      regTimeout: map['regTimeout'] as int?,
      regContactParams: map['regContactParams'] as String?,
      regHeaders: map['regHeaders'] as Map<String, dynamic>?,
      registration: AccountRegistration.fromMap(map['registration'] as Map<String, dynamic>),
    );
  }

  // Serialization
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'uri': uri,
      'name': name,
      'username': username,
      'domain': domain,
      'password': password,
      'proxy': proxy,
      'transport': transport,
      'contactParams': contactParams,
      'contactUriParams': contactUriParams,
      'regServer': regServer,
      'regTimeout': regTimeout,
      'regContactParams': regContactParams,
      'regHeaders': regHeaders,
      'registration': registration.toMap(),
    };
  }

  // Value-based equality
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Account && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() {
    return 'Account(id: $id, name: $name, username: $username, domain: $domain)';
  }
}
```

```dart
// account_registration.dart
class AccountRegistration {
  final bool status;
  final int? code;
  final String? reason;
  final int? expiration;
  final int? retryAfter;

  AccountRegistration({
    required this.status,
    this.code,
    this.reason,
    this.expiration,
    this.retryAfter,
  });

  factory AccountRegistration.fromMap(Map<String, dynamic> map) {
    return AccountRegistration(
      status: map['status'] as bool? ?? false,
      code: map['code'] as int?,
      reason: map['reason'] as String?,
      expiration: map['expiration'] as int?,
      retryAfter: map['retryAfter'] as int?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'status': status,
      'code': code,
      'reason': reason,
      'expiration': expiration,
      'retryAfter': retryAfter,
    };
  }

  @override
  String toString() {
    return 'AccountRegistration(status: $status, code: $code, reason: $reason)';
  }
}
```

```dart
// call.dart - Immutable with computed properties
class Call {
  final int id;
  final int callId;
  final int accountId;
  final String state;
  final String stateText;
  final bool held;
  final bool muted;
  final bool speaker;
  final int connectDuration;
  final int totalDuration;
  // ... more fields

  // Internal tracking (final, set at construction)
  final int _constructionTime;

  Call({
    required this.id,
    required this.callId,
    required this.accountId,
    required this.state,
    required this.stateText,
    required this.held,
    required this.muted,
    required this.speaker,
    required this.connectDuration,
    required this.totalDuration,
    // ...
  }) : _constructionTime = DateTime.now().millisecondsSinceEpoch ~/ 1000;

  // Computed property (not stored)
  int getConnectDuration() {
    final time = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final offset = time - _constructionTime;
    return connectDuration + offset;
  }

  // Value-based equality
  @override
  bool operator ==(Object other) => other is Call && other.id == id;

  @override
  int get hashCode => id.hashCode;
}
```

## Consequences

### Positive

1. **State Consistency**: Immutability guarantees state doesn't change unexpectedly:
   - No accidental mutations
   - Safe to share across isolates
   - Predictable behavior

2. **Value Semantics**: Equality by ID makes comparisons intuitive:
   - `account1 == account2` compares IDs
   - Works correctly in Sets and as Map keys
   - UI can detect changes via equality

3. **Thread Safety**: Immutable objects are inherently thread-safe:
   - No synchronization needed
   - Safe to pass between isolates
   - No race conditions on reads

4. **Explicit State Changes**: State changes require new object creation:
   - Changes are visible and trackable
   - Easy to implement undo/redo
   - Supports time-travel debugging

5. **Simplified Reasoning**: Easier to understand code:
   - No hidden mutations
   - Data flow is explicit
   - Fewer side effects

6. **Platform Channel Safe**: fromMap/toMap pattern handles serialization:
   - Clear conversion logic
   - Type casting explicit
   - Easy to test

### Negative

1. **Object Creation Overhead**: New object for each state change:
   - More GC pressure
   - Memory allocation for updates
   - Potential performance impact

2. **Verbose Updates**: Updating nested state requires copying:
   ```dart
   // Verbose: Must rebuild entire object tree
   final updatedAccount = Account(
     ...account,  // Copy existing fields
     registration: AccountRegistration(
       ...account.registration,  // Copy nested
       status: true,  // Update one field
     ),
   );
   ```

3. **No Built-in Copy Method**: Dart doesn't have copyWith:
   - Must manually copy all fields
   - Easy to forget fields
   - More boilerplate

4. **Identity vs Equality**: Equality by ID may hide differences:
   - Two Account objects with same ID but different data are "equal"
   - May miss state changes if ID is same
   - hashCode only considers ID

### Trade-offs

**Rejected Alternative: Mutable Data Classes**

We considered mutable models with setters:

```dart
// Rejected: Mutable model
class Account {
  int id;
  String name;  // Not final
  
  set name(String value) {
    _name = value;
    notifyListeners();  // For reactivity
  }
}
```

**Why Rejected:**
- Harder to reason about state changes
- Requires change notification mechanism
- Race conditions possible
- Not safe across isolates

**Rejected Alternative: Freezed Code Generation**

We considered using freezed package for immutability:

```dart
// Rejected: Freezed
@freezed
class Account with _$Account {
  factory Account({
    required int id,
    required String name,
  }) = _Account;
}
```

**Why Rejected:**
- Adds build_runner dependency
- Increases build time
- Generated code complexity
- Overkill for simple data models

**Rejected Alternative: Record Class Pattern**

We considered Record-style classes:

```dart
// Rejected: Record pattern
typedef Account = ({
  int id,
  String name,
  // ...
});
```

**Why Rejected:**
- No methods on records
- Harder to add behavior
- Less IDE support
- New language feature (compatibility)

**Accepted Trade-off:** Verbose updates for safety - Manual object copying is verbose but makes state changes explicit and safe.

## Related Decisions

- **ADR-006**: Real-time duration calculation (uses immutable _constructionTime)

## References

- [Dart Immutability Guide](https://dart.dev/guides/language/effective-dart/design#prefer-declaring-fields-as-final-whenever-possible)
- [Account.dart](../lib/src/account.dart)
- [Call.dart](../lib/src/call.dart)
- [AccountRegistration.dart](../lib/src/account_registration.dart)

---

*Generated by /legacy analysis | 2026-03-04*
