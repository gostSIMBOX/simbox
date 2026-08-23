# 01-Requirements - eSIM Management

> ГОСТ СИМБОКС - Модуль UniSIM/eSIM

**Status**: DRAFT  
**Date**: 2024-03-04  
**Source**: Legacy Analysis (/legacy)

---

## Business Requirements

### BR-ESIM-001: Управление eSIM профилями

**Описание**: Полнофункциональное управление eSIM профилями UniSIM 1.5.

**Стейкхолдеры**:
- Операторы связи (МТС, Билайн, МегаФон, Теле2)
- Корпоративные клиенты
- Розничные пользователи

**Критерии приемки**:
- [ ] Установка eSIM через QR-код
- [ ] Управление несколькими профилями на устройстве
- [ ] Активация/деактивация профилей
- [ ] Перенос между устройствами
- [ ] Резервное копирование и восстановление

---

### BR-ESIM-002: Поддержка платформ

**Описание**: Кроссплатформенная поддержка eSIM.

**Платформы**:
| Платформа | Версия | Статус |
|-----------|--------|--------|
| Android | 8.0+ (API 26+) | Active |
| iOS | 12.0+ | Active |
| Aurora OS | 4.0+ | Active |
| HarmonyOS | 2.0+ | Planned |

---

### BR-ESIM-003: Интеграция с операторами

**Описание**: API интеграция с российскими операторами.

**Операторы**:
- МТС - eSIM для физ.лиц и бизнеса
- Билайн - eSIM для смартфонов и планшетов
- МегаФон - eSIM для IoT устройств
- Теле2 - eSIM для потребителей

---

## Functional Requirements

### FR-ESIM-001: Сканирование QR-кода

**Приоритет**: High

**Описание**: Установка eSIM профиля через сканирование QR-кода от оператора.

**Use Case**:
```
1. Пользователь нажимает "Добавить eSIM"
2. Открывается камера для сканирования
3. QR-код декодируется
4. Данные профиля извлекаются
5. Профиль устанавливается на устройство
6. Пользователь подтверждает активацию
```

**Валидация QR-кода**:
```
Формат: LPA:1$<SM-DP+ Address>$<Activation Code>
Пример: LPA:1$rsp.mts.ru$MTS-ACTIVATION-CODE-12345
```

---

### FR-ESIM-002: Управление профилями

**Приоритет**: High

**Операции**:
```
LIST    /esim/profiles              # Список профилей
GET     /esim/profiles/{id}         # Детали профиля
POST    /esim/profiles/{id}/activate    # Активация
POST    /esim/profiles/{id}/deactivate  # Деактивация
DELETE  /esim/profiles/{id}         # Удаление
POST    /esim/profiles/{id}/transfer    # Перенос
GET     /esim/profiles/{id}/backup      # Бэкап
POST    /esim/profiles/restore          # Восстановление
```

**Статусы профиля**:
- `downloaded` - Профиль загружен, не активирован
- `active` - Профиль активен и используется
- `inactive` - Профиль деактивирован
- `deleted` - Профиль удален

---

### FR-ESIM-003: Перенос eSIM

**Приоритет**: Medium

**Описание**: Перенос eSIM профиля между устройствами.

**Процесс**:
```
1. Исходное устройство:
   - Создается резервная копия профиля
   - Профиль деактивируется
   - Генерируется токен переноса

2. Пользователь:
   - Сканирует QR-код переноса на новом устройстве
   - Вводит код подтверждения

3. Новое устройство:
   - Загружает профиль по токену
   - Активирует профиль
   - Подтверждает успешный перенос
```

---

### FR-ESIM-004: Безопасность eSIM

**Приоритет**: Critical

**Требования**:
- Шифрование данных профиля (AES-256)
- HMAC-SHA256 для проверки целостности
- Биометрическая аутентификация для операций
- Аудит всех операций с eSIM

---

## Technical Specifications

### UniSIM 1.5 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  UniSIM 1.5                         │
│                                                     │
│  ┌─────────────┐     ┌─────────────┐               │
│  │   LPA       │     │   eUICC     │               │
│  │  (Local     │     │  (Embedded  │               │
│  │  Profile    │     │   UICC)     │               │
│  │  Assistant) │     │             │               │
│  └──────┬──────┘     └──────┬──────┘               │
│         │                   │                       │
│         └─────────┬─────────┘                       │
│                   │                                 │
│         ┌─────────▼─────────┐                       │
│         │   SM-DP+ Server   │                       │
│         │  (Operator)       │                       │
│         └─────────┬─────────┘                       │
│                   │                                 │
│         ┌─────────▼─────────┐                       │
│         │   GSMA SGP.22     │                       │
│         │   Protocol        │                       │
│         └───────────────────┘                       │
└─────────────────────────────────────────────────────┘
```

---

### eSIM Profile Structure

```json
{
  "iccid": "89701000000000000001",
  "eid": "89049032000000000000000000000001",
  "profile_name": "МТС Россия",
  "operator": "MTS",
  "status": "active",
  "activation_code": "LPA:1$rsp.mts.ru$MTS-ACT-CODE",
  "profile_data": {
    "imsi": "250010000000001",
    "ki": "encrypted_key",
    "opc": "encrypted_opc",
    "sm_dp_address": "rsp.mts.ru",
    "matching_id": "MTS-ACT-CODE"
  },
  "device_info": {
    "manufacturer": "Samsung",
    "model": "Galaxy S23",
    "os": "Android 14"
  },
  "created_at": "2024-03-04T10:00:00Z",
  "activated_at": "2024-03-04T10:05:00Z"
}
```

---

### GSMA eSIM Protocols

#### SGP.22 (Consumer eSIM)

```
Процесс установки профиля:

1. Device → LPA: Scan QR Code
2. LPA → SM-DP+: Initiate Authentication
3. SM-DP+ → LPA: Challenge + Certificate
4. LPA → eUICC: Download Profile
5. eUICC → LPA: Profile Installed
6. LPA → SM-DP+: Confirmation
7. SM-DP+ → Operator: Profile Active
```

#### SGP.32 (IoT eSIM)

```
Для IoT устройств:
- Упрощенный процесс активации
- Поддержка M2M коммуникации
- Удаленное управление профилями
- Массовая активация
```

---

### Security Implementation

#### Шифрование данных профиля

```dart
import 'package:encrypt/encrypt.dart';

class EsimSecurity {
  final Key _key;
  final IV _iv;
  
  EsimSecurity(String masterKey) 
    : _key = Key.fromUtf8(masterKey.padRight(32)),
      _iv = IV.fromLength(16);
  
  // Шифрование данных профиля
  String encryptProfile(Map<String, dynamic> profileData) {
    final encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
    final json = jsonEncode(profileData);
    final encrypted = encrypter.encrypt(json, iv: _iv);
    return encrypted.base64;
  }
  
  // Расшифровка данных профиля
  Map<String, dynamic> decryptProfile(String encryptedData) {
    final encrypter = Encrypter(AES(_key, mode: AESMode.cbc));
    final decrypted = encrypter.decrypt64(encryptedData, iv: _iv);
    return jsonDecode(decrypted);
  }
  
  // HMAC для проверки целостности
  String generateHMAC(String data, String secret) {
    final hmac = Hmac(sha256, utf8.encode(secret));
    final digest = hmac.convert(utf8.encode(data).codeUnits);
    return digest.toString();
  }
  
  // Проверка целостности
  bool verifyHMAC(String data, String signature, String secret) {
    final expectedSignature = generateHMAC(data, secret);
    return signature == expectedSignature;
  }
}
```

---

### QR Code Generation

```dart
import 'package:qr_flutter/qr_flutter.dart';

class QRCodeGenerator {
  // Генерация QR-кода для установки eSIM
  String generateActivationQR({
    required String smdpAddress,
    required String activationCode,
  }) {
    // Формат: LPA:1$<SM-DP+ Address>$<Activation Code>
    final lpaUrl = 'LPA:1\$$smdpAddress\$$activationCode';
    return lpaUrl;
  }
  
  // Генерация QR-кода для переноса
  String generateTransferQR({
    required String tokenId,
    required String expiryDate,
  }) {
    // Формат: ESIM-TRANSFER:1$<Token>$<Expiry>
    return 'ESIM-TRANSFER:1\$$tokenId\$$expiryDate';
  }
  
  // Виджет QR-кода
  Widget buildQRCode(String data, {double size = 200}) {
    return QrImageView(
      data: data,
      version: QrVersions.auto,
      size: size,
      backgroundColor: Colors.white,
      foregroundColor: Colors.black,
    );
  }
}
```

---

## Integration with Operators

### API Integration Example

```dart
class OperatorApiClient {
  final Dio _dio;
  
  OperatorApiClient(String baseUrl, String apiKey)
    : _dio = Dio(BaseOptions(
        baseUrl: baseUrl,
        headers: {'Authorization': 'Bearer $apiKey'},
      ));
  
  // Получение профиля eSIM от оператора
  Future<EsProfile> requestProfile({
    required String iccid,
    required String deviceId,
  }) async {
    final response = await _dio.post('/esim/profile', data: {
      'iccid': iccid,
      'eid': deviceId,
      'profile_type': 'consumer',
    });
    
    return EsProfile.fromJson(response.data);
  }
  
  // Активация профиля
  Future<void> activateProfile(String profileId) async {
    await _dio.put('/esim/activate', data: {
      'profile_id': profileId,
    });
  }
  
  // Проверка статуса
  Future<ProfileStatus> checkStatus(String profileId) async {
    final response = await _dio.get('/esim/status/$profileId');
    return ProfileStatus.fromJson(response.data);
  }
}
```

---

## Testing Requirements

### Unit Tests

```dart
void main() {
  group('eSIM Security Tests', () {
    test('should encrypt and decrypt profile data', () {
      final security = EsimSecurity('test-master-key-32-chars');
      final profile = {'iccid': '89701000000000000001'};
      
      final encrypted = security.encryptProfile(profile);
      final decrypted = security.decryptProfile(encrypted);
      
      expect(decrypted['iccid'], equals(profile['iccid']));
    });
    
    test('should verify HMAC signature', () {
      final security = EsimSecurity('test-key');
      final data = 'test-data';
      final signature = security.generateHMAC(data, 'secret');
      
      expect(
        security.verifyHMAC(data, signature, 'secret'),
        isTrue,
      );
    });
  });
}
```

---

## Open Questions

1. **UniSIM Licensing**: Какие требования к лицензированию UniSIM 1.5?
2. **Operator Integration**: Какие API предоставляют операторы?
3. **eUICC Compatibility**: Какие устройства поддерживают eSIM?
4. **Backup Strategy**: Где хранить резервные копии eSIM профилей?

---

*Generated by /legacy from README analysis*
