# 02-Specifications - eSIM Management

> ГОСТ СИМБОКС - Модуль UniSIM/eSIM

**Status**: DRAFT
**Date**: 2026-03-04
**Source**: Requirements 01-requirements.md
**Type**: SDD (Spec-Driven Development)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  EsimManager (Dart/JS)                                 │  │
│  │  - Profile management                                  │  │
│  │  - QR code scanning                                    │  │
│  │  - Operator API client                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            │ Platform Channel                │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Native eSIM Manager (Android/iOS/Aurora)             │  │
│  │  - EuiccManager (Android)                              │  │
│  │  - CTCellularPlan (iOS)                                │  │
│  │  - Platform-specific APIs                              │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            │ GSMA SGP.22/SGP.32              │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  eUICC Hardware                                        │  │
│  │  - Profile storage                                     │  │
│  │  - Secure element                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Model Specification

### EsProfile Class

```dart
class EsProfile {
  /// Unique profile identifier (ICCID)
  final String iccid;
  
  /// eUICC identifier (device-specific)
  final String eid;
  
  /// Human-readable profile name
  final String profileName;
  
  /// Operator name (МТС, Билайн, МегаФон, Теле2)
  final String operator;
  
  /// Profile status
  final EsProfileStatus status;
  
  /// Activation code from QR
  final String? activationCode;
  
  /// Encrypted profile data
  final String? profileData;
  
  /// SM-DP+ server address
  final String? smDpAddress;
  
  /// Confirmation code (if required)
  final String? confirmationCode;
  
  /// Profile nickname (user-defined)
  final String? nickname;
  
  /// Installation timestamp
  final DateTime? installedAt;
  
  /// Activation timestamp
  final DateTime? activatedAt;
  
  /// Expiration timestamp (if applicable)
  final DateTime? expiresAt;
  
  /// Data plan details
  final DataPlan? dataPlan;
  
  EsProfile({
    required this.iccid,
    required this.eid,
    required this.profileName,
    required this.operator,
    required this.status,
    this.activationCode,
    this.profileData,
    this.smDpAddress,
    this.confirmationCode,
    this.nickname,
    this.installedAt,
    this.activatedAt,
    this.expiresAt,
    this.dataPlan,
  });
  
  factory EsProfile.fromMap(Map<String, dynamic> map) {
    return EsProfile(
      iccid: map['iccid'] as String,
      eid: map['eid'] as String,
      profileName: map['profile_name'] as String,
      operator: map['operator'] as String,
      status: EsProfileStatus.fromString(map['status'] as String),
      activationCode: map['activation_code'] as String?,
      profileData: map['profile_data'] as String?,
      smDpAddress: map['sm_dp_address'] as String?,
      confirmationCode: map['confirmation_code'] as String?,
      nickname: map['nickname'] as String?,
      installedAt: map['installed_at'] != null 
          ? DateTime.parse(map['installed_at'] as String) 
          : null,
      activatedAt: map['activated_at'] != null 
          ? DateTime.parse(map['activated_at'] as String) 
          : null,
      expiresAt: map['expires_at'] != null 
          ? DateTime.parse(map['expires_at'] as String) 
          : null,
      dataPlan: map['data_plan'] != null 
          ? DataPlan.fromMap(map['data_plan']) 
          : null,
    );
  }
  
  Map<String, dynamic> toMap() {
    return {
      'iccid': iccid,
      'eid': eid,
      'profile_name': profileName,
      'operator': operator,
      'status': status.toString(),
      'activation_code': activationCode,
      'profile_data': profileData,
      'sm_dp_address': smDpAddress,
      'confirmation_code': confirmationCode,
      'nickname': nickname,
      'installed_at': installedAt?.toIso8601String(),
      'activated_at': activatedAt?.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'data_plan': dataPlan?.toMap(),
    };
  }
}
```

### EsProfileStatus Enum

```dart
enum EsProfileStatus {
  /// Profile downloaded, not activated
  downloaded,
  
  /// Profile active and in use
  active,
  
  /// Profile installed but disabled
  inactive,
  
  /// Profile deleted from eUICC
  deleted,
  
  /// Profile transfer in progress
  transferring,
  
  /// Profile installation failed
  failed,
}
```

### DataPlan Class

```dart
class DataPlan {
  /// Total data allowance in bytes
  final int totalBytes;
  
  /// Used data in bytes
  final int usedBytes;
  
  /// Plan renewal date
  final DateTime? renewalDate;
  
  /// Plan type (prepaid/postpaid)
  final DataPlanType type;
  
  const DataPlan({
    required this.totalBytes,
    required this.usedBytes,
    this.renewalDate,
    required this.type,
  });
  
  double get usagePercent {
    if (totalBytes == 0) return 0.0;
    return (usedBytes / totalBytes) * 100;
  }
  
  int get remainingBytes => totalBytes - usedBytes;
  
  factory DataPlan.fromMap(Map<String, dynamic> map) {
    return DataPlan(
      totalBytes: map['total_bytes'] as int,
      usedBytes: map['used_bytes'] as int,
      renewalDate: map['renewal_date'] != null 
          ? DateTime.parse(map['renewal_date'] as String) 
          : null,
      type: DataPlanType.fromString(map['type'] as String),
    );
  }
  
  Map<String, dynamic> toMap() {
    return {
      'total_bytes': totalBytes,
      'used_bytes': usedBytes,
      'renewal_date': renewalDate?.toIso8601String(),
      'type': type.toString(),
    };
  }
}

enum DataPlanType { prepaid, postpaid, unlimited }
```

---

## Security Specification

### EsimSecurity Class

```dart
class EsimSecurity {
  /// AES-256 encryption key
  final Uint8List _encryptionKey;
  
  /// HMAC-SHA256 key for integrity
  final Uint8List _integrityKey;
  
  EsimSecurity({
    required Uint8List encryptionKey,
    required Uint8List integrityKey,
  })  : _encryptionKey = encryptionKey,
        _integrityKey = integrityKey;
  
  /// Encrypt profile data before storage
  Uint8List encrypt(Uint88 plainData) {
    final aes = AES(_encryptionKey);
    final iv = generateSecureIV();
    final encrypted = aes.encrypt(plainData, iv: iv);
    return Uint8List.fromList(iv + encrypted);
  }
  
  /// Decrypt profile data for use
  Uint8List decrypt(Uint8List encryptedData) {
    final iv = encryptedData.sublist(0, 16);
    final data = encryptedData.sublist(16);
    final aes = AES(_encryptionKey);
    return aes.decrypt(data, iv: iv);
  }
  
  /// Generate HMAC for integrity verification
  String generateHMAC(Uint8List data) {
    final hmac = Hmac(sha256, _integrityKey);
    final digest = hmac.convert(data);
    return digest.toString();
  }
  
  /// Verify data integrity
  bool verifyHMAC(Uint8List data, String expectedHmac) {
    final actualHmac = generateHMAC(data);
    return actualHmac == expectedHmac;
  }
}
```

### Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| Encryption | AES-256-GCM for profile data |
| Integrity | HMAC-SHA256 for tamper detection |
| Key Storage | Android Keystore / iOS Keychain |
| QR Data | Encrypted in transit only |
| Backup | Encrypted with user passphrase |

---

## QR Code Specification

### Format

```
LPA:1$<SM-DP+ Address>$<Activation Code>
```

### Example

```
LPA:1$rsp.mts.ru$MTS-ACTIVATION-CODE-12345-67890
```

### Parsing

```dart
class QrCodeParser {
  static QrCodeData parse(String qrContent) {
    // Validate format
    if (!qrContent.startsWith('LPA:1$')) {
      throw FormatException('Invalid LPA format');
    }
    
    final parts = qrContent.substring(6).split('\$');
    if (parts.length != 2) {
      throw FormatException('Invalid QR code structure');
    }
    
    return QrCodeData(
      smDpAddress: parts[0],
      activationCode: parts[1],
    );
  }
}

class QrCodeData {
  final String smDpAddress;
  final String activationCode;
  
  QrCodeData({
    required this.smDpAddress,
    required this.activationCode,
  });
}
```

### Generation (for operator portals)

```dart
class QrCodeGenerator {
  static String generate({
    required String smDpAddress,
    required String activationCode,
  }) {
    return 'LPA:1\$$smDpAddress\$$activationCode';
  }
  
  /// Generate QR code image for display
  static Future<Uint8List> generateImage({
    required String smDpAddress,
    required String activationCode,
    int size = 256,
  }) async {
    final qrData = generate(
      smDpAddress: smDpAddress,
      activationCode: activationCode,
    );
    
    final qr = QrCode(2, QrErrorCorrectLevel.M);
    qr.addData(qrData);
    qr.make();
    
    final image = QrImage(qr);
    return image.toImageData(size, size);
  }
}
```

---

## API Client Specification

### OperatorApiClient

```dart
class OperatorApiClient {
  final String baseUrl;
  final String operatorId;
  final http.Client _client;
  
  OperatorApiClient({
    required this.baseUrl,
    required this.operatorId,
    http.Client? client,
  }) : _client = client ?? http.Client();
  
  /// Request eSIM profile from operator
  Future<EsProfile> requestProfile({
    required String userId,
    required String deviceId,
    String? planId,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/api/v1/esim/request'),
      headers: {
        'Content-Type': 'application/json',
        'X-Operator-ID': operatorId,
      },
      body: jsonEncode({
        'user_id': userId,
        'device_id': deviceId,
        'plan_id': planId,
      }),
    );
    
    if (response.statusCode != 200) {
      throw ApiException('Failed to request profile: ${response.body}');
    }
    
    final data = jsonDecode(response.body);
    return EsProfile.fromMap(data);
  }
  
  /// Get profile status from operator
  Future<EsProfileStatus> getProfileStatus(String iccid) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/v1/esim/profiles/$iccid/status'),
      headers: {'X-Operator-ID': operatorId},
    );
    
    if (response.statusCode != 200) {
      throw ApiException('Failed to get status');
    }
    
    final data = jsonDecode(response.body);
    return EsProfileStatus.fromString(data['status']);
  }
  
  /// Activate profile with operator
  Future<void> activateProfile(String iccid) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/api/v1/esim/profiles/$iccid/activate'),
      headers: {'X-Operator-ID': operatorId},
    );
    
    if (response.statusCode != 200) {
      throw ApiException('Failed to activate');
    }
  }
  
  /// Deactivate profile with operator
  Future<void> deactivateProfile(String iccid) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/api/v1/esim/profiles/$iccid/deactivate'),
      headers: {'X-Operator-ID': operatorId},
    );
    
    if (response.statusCode != 200) {
      throw ApiException('Failed to deactivate');
    }
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);
  @override
  String toString() => 'ApiException: $message';
}
```

### Operator Configurations

```dart
class OperatorConfig {
  static final Map<String, OperatorConfig> _configs = {
    'mts': OperatorConfig(
      id: 'mts',
      name: 'МТС',
      baseUrl: 'https://api.mts.ru/esim',
      supportsQR: true,
      supportsTransfer: true,
    ),
    'beeline': OperatorConfig(
      id: 'beeline',
      name: 'Билайн',
      baseUrl: 'https://api.beeline.ru/esim',
      supportsQR: true,
      supportsTransfer: false,
    ),
    'megafon': OperatorConfig(
      id: 'megafon',
      name: 'МегаФон',
      baseUrl: 'https://api.megafon.ru/esim',
      supportsQR: true,
      supportsTransfer: true,
    ),
    'tele2': OperatorConfig(
      id: 'tele2',
      name: 'Теле2',
      baseUrl: 'https://api.tele2.ru/esim',
      supportsQR: true,
      supportsTransfer: true,
    ),
  };
  
  final String id;
  final String name;
  final String baseUrl;
  final bool supportsQR;
  final bool supportsTransfer;
  
  OperatorConfig({
    required this.id,
    required this.name,
    required this.baseUrl,
    required this.supportsQR,
    required this.supportsTransfer,
  });
  
  static OperatorConfig? getById(String id) => _configs[id];
  static Iterable<OperatorConfig> get supported => _configs.values;
}
```

---

## Platform Implementation

### Android (API 26+)

```kotlin
class AndroidEsimManager {
  private val euiccManager: EuiccManager
  
  fun getProfiles(): List<EsProfile> {
    val infoList = euiccManager.allProfiles
    return infoList.map { info ->
      EsProfile(
        iccid = info.iccid,
        eid = euiccManager.euiccId ?: "",
        profileName = info.profileName ?: "Unknown",
        operator = info.carrierName ?: "Unknown",
        status = when (info.state) {
          EuiccProfileInfo.PROFILE_STATE_ENABLED -> EsProfileStatus.ACTIVE
          else -> EsProfileStatus.INACTIVE
        },
      )
    }
  }
  
  fun downloadProfile(smDpAddress: String, activationCode: String) {
    val intent = Intent(activity, DownloadProfileActivity::class.java).apply {
      putExtra(EuiccManager.EXTRA_SM_DP_ADDRESS, smDpAddress)
      putExtra(EuiccManager.EXTRA_ACTIVATION_CODE, activationCode)
    }
    activity.startActivity(intent)
  }
  
  fun activateProfile(iccid: String): Boolean {
    return euiccManager.switchToProfile(iccid).also { success ->
      if (success) {
        notifyProfileChanged(iccid, EsProfileStatus.ACTIVE)
      }
    }
  }
  
  fun deactivateProfile(iccid: String): Boolean {
    return euiccManager.disableProfile(iccid).also { success ->
      if (success) {
        notifyProfileChanged(iccid, EsProfileStatus.INACTIVE)
      }
    }
  }
  
  fun deleteProfile(iccid: String): Boolean {
    return euiccManager.eraseProfile(iccid).also { success ->
      if (success) {
        notifyProfileChanged(iccid, EsProfileStatus.DELETED)
      }
    }
  }
}
```

### iOS (12.0+)

```swift
import CoreTelephony

class IosEsimManager {
    private let cellularPlanManager = CTCellularPlanManager()
    
    func getProfiles() -> [EsProfile] {
        guard let plans = cellularPlanManager.allPlans else { return [] }
        return plans.map { plan in
            EsProfile(
                iccid: plan.iccid,
                eid: plan.eid ?? "",
                profileName: plan.label ?? "Unknown",
                operator: plan.carrierName ?? "Unknown",
                status: plan.status == .active ? .active : .inactive
            )
        }
    }
    
    func addPlan(addPlanActivation: CTCellularPlanActivation) {
        cellularPlanManager.addPlan(
            with: addPlanActivation,
            completionHandler: { result in
                switch result {
                case .success:
                    self.notifyProfileAdded(addPlanActivation.iccid)
                case .failure(let error):
                    self.notifyError(error)
                @unknown default:
                    break
                }
            }
        )
    }
    
    func activatePlan(_ iccid: String) {
        cellularPlanManager.activatePlan(
            with: iccid,
            completionHandler: { result in
                // Handle result
            }
        )
    }
    
    func deletePlan(_ iccid: String) {
        cellularPlanManager.deletePlan(
            with: iccid,
            completionHandler: { result in
                // Handle result
            }
        )
    }
}
```

---

## Error Handling

### Error Types

```dart
enum EsimErrorType {
  /// eUICC not available on device
  hardwareNotAvailable,
  
  /// QR code invalid format
  invalidQRCode,
  
  /// Profile download failed
  downloadFailed,
  
  /// Profile activation failed
  activationFailed,
  
  /// Profile not found
  profileNotFound,
  
  /// Operator API error
  apiError,
  
  /// Security/encryption error
  securityError,
  
  /// Permission denied
  permissionDenied,
}

class EsimException implements Exception {
  final EsimErrorType type;
  final String message;
  final Exception? cause;
  
  EsimException({
    required this.type,
    required this.message,
    this.cause,
  });
  
  @override
  String toString() => 'EsimException(${type.name}): $message';
}
```

### Error Recovery

| Error | Recovery Action |
|-------|----------------|
| hardwareNotAvailable | Show user message, disable eSIM features |
| invalidQRCode | Prompt to rescan, show format example |
| downloadFailed | Retry with exponential backoff (3 attempts) |
| activationFailed | Verify network, retry activation |
| profileNotFound | Refresh profile list from eUICC |
| apiError | Show operator-specific error message |
| securityError | Clear cached data, prompt for re-authentication |
| permissionDenied | Request permission with explanation |

---

## Testing Strategy

### Unit Tests

```dart
void main() {
  group('QrCodeParser', () {
    test('parses valid QR code', () {
      final qr = 'LPA:1\$rsp.mts.ru\$MTS-ACTIVATION-CODE';
      final result = QrCodeParser.parse(qr);
      
      expect(result.smDpAddress, 'rsp.mts.ru');
      expect(result.activationCode, 'MTS-ACTIVATION-CODE');
    });
    
    test('throws on invalid format', () {
      expect(
        () => QrCodeParser.parse('INVALID'),
        throwsA(isA<FormatException>()),
      );
    });
  });
  
  group('EsProfile', () {
    test('serializes to map', () {
      final profile = EsProfile(
        iccid: '89701234567890123456',
        eid: '89049120000000000000000000000123',
        profileName: 'МТС eSIM',
        operator: 'МТС',
        status: EsProfileStatus.active,
      );
      
      final map = profile.toMap();
      expect(map['iccid'], '89701234567890123456');
      expect(map['status'], 'active');
    });
  });
}
```

### Integration Tests

```dart
void main() {
  testWidgets('eSIM flow: scan → download → activate', (tester) async {
    // Mock native eUICC
    final mockEsimManager = MockEsimManager();
    
    // Setup test profile
    final testProfile = EsProfile(
      iccid: '89701234567890123456',
      eid: '89049120000000000000000000000123',
      profileName: 'Test Profile',
      operator: 'МТС',
      status: EsProfileStatus.downloaded,
    );
    
    when(mockEsimManager.downloadProfile(any, any))
        .thenAnswer((_) async => testProfile);
    
    // Run UI flow
    await tester.pumpWidget(EsimSetupScreen(manager: mockEsimManager));
    
    // Tap scan button
    await tester.tap(find.byIcon(Icons.qr_code_scanner));
    await tester.pumpAndSettle();
    
    // Verify profile list updated
    expect(find.text('Test Profile'), findsOneWidget);
  });
}
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| qr_flutter | ^4.1.0 | QR code generation |
| qr_code_scanner | ^1.0.0 | QR code scanning |
| encrypt | ^5.0.1 | AES encryption |
| crypto | ^3.0.3 | HMAC-SHA256 |
| http | ^1.2.1 | Operator API calls |

---

*Status: DRAFT | Type: SDD | Created: 2026-03-04*
