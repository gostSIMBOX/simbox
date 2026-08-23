# 01-Requirements - IMEI Modification

> ГОСТ СИМБОКС - Модуль изменения IMEI

**Status**: DRAFT  
**Date**: 2024-03-04  
**Source**: Legacy Analysis (/legacy)

---

## Business Requirements

### BR-IMEI-001: Изменение IMEI устройств

**Описание**: Безопасное изменение IMEI для устройств Huawei и Qtech.

**Стейкхолдеры**:
- Сервисные центры
- Корпоративные клиенты
- Технические специалисты

**Критерии приемки**:
- [ ] Чтение текущего IMEI
- [ ] Изменение IMEI на пользовательский
- [ ] Восстановление оригинального IMEI
- [ ] Резервное копирование
- [ ] Валидация IMEI (контрольная сумма)

---

### BR-IMEI-002: Поддержка устройств

**Описание**: Поддержка популярных устройств Huawei и Qtech.

**Устройства**:
| Устройство | Статус | Метод |
|------------|--------|-------|
| Huawei E3372 | Supported | AT Commands |
| Huawei E5573 | Supported | AT Commands |
| Huawei B525 | Supported | AT Commands |
| Qtech QMP-M1-N IP68 | Supported | Proprietary |

---

### BR-IMEI-003: Соответствие законодательству

**Описание**: Изменение IMEI только в законных случаях.

**Легальные сценарии**:
- Восстановление после сброса прошивки
- Замена платы устройства
- Тестирование и разработка
- Исследовательские цели

**Предупреждение**: Изменение IMEI в незаконных целях запрещено!

---

## Functional Requirements

### FR-IMEI-001: Обнаружение устройства

**Приоритет**: High

**Описание**: Автоматическое обнаружение подключенного устройства.

**Use Case**:
```
1. Пользователь подключает устройство по USB
2. Система определяет устройство
3. Проверяется совместимость
4. Отображается текущий IMEI
```

**Команда**:
```bash
./scripts/detect_device.sh

# Output:
Device found: Huawei E3372
Serial: C657843210
Current IMEI: 861234567890123
Status: Ready
```

---

### FR-IMEI-002: Чтение IMEI

**Приоритет**: High

**Описание**: Чтение текущего IMEI из устройства.

**AT Команды**:
```
AT+CGSN          # Чтение IMEI (стандарт)
AT+CGSN=1        # Чтение IMEI (альтернативный формат)
AT^ICCID?        # Чтение ICCID
AT+CIMI          # Чтение IMSI
```

**Пример**:
```bash
./scripts/read_imei.sh

# Output:
IMEI: 861234567890123
IMEI SV: 8612345678901234
ICCID: 89701000000000000001
IMSI: 250010000000001
```

---

### FR-IMEI-003: Изменение IMEI

**Приоритет**: High

**Описание**: Изменение IMEI с валидацией.

**Use Case**:
```
1. Пользователь вводит новый IMEI
2. Система проверяет контрольную сумму (Luhn algorithm)
3. Создается резервная копия
4. Отправляется команда изменения
5. Проверяется результат
6. Перезагружается устройство
```

**AT Команды (Huawei)**:
```
AT^CIMEI=<IMEI>    # Изменение IMEI
AT+CFUN=1,1        # Перезагрузка
```

**Пример**:
```bash
./scripts/change_imei.sh 861234567890124

# Output:
Validating IMEI... OK
Creating backup... Saved to backup/imei_20240304_100000.bin
Writing new IMEI... Success
Rebooting device...
Verifying... OK
New IMEI: 861234567890124
```

---

### FR-IMEI-004: Валидация IMEI

**Приоритет**: Critical

**Описание**: Проверка корректности IMEI.

**Алгоритм Luhn**:
```python
def validate_imei(imei: str) -> bool:
    """Проверка IMEI по алгоритму Luhn"""
    if not imei.isdigit() or len(imei) != 15:
        return False
    
    digits = [int(d) for d in imei]
    checksum = 0
    
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    
    return checksum % 10 == 0
```

**Примеры валидации**:
```
861234567890123 → Valid ✓
861234567890124 → Invalid ✗
123456789012345 → Valid ✓
```

---

### FR-IMEI-005: Резервное копирование

**Приоритет**: High

**Описание**: Сохранение оригинального IMEI и конфигурации.

**Формат бэкапа**:
```json
{
  "device_serial": "C657843210",
  "device_model": "Huawei E3372",
  "original_imei": "861234567890123",
  "backup_date": "2024-03-04T10:00:00Z",
  "nv_items": {
    "item_1": "base64_encoded_data",
    "item_2": "base64_encoded_data"
  },
  "checksum": "sha256_hash"
}
```

---

## Technical Specifications

### Architecture

```
gost_simbox_change_imei/
├── src/
│   ├── core/              # Основная логика
│   │   ├── imei_reader.py
│   │   ├── imei_writer.py
│   │   ├── validator.py
│   │   └── backup.py
│   ├── drivers/           # Драйверы
│   │   ├── huawei.py
│   │   ├── qtech.py
│   │   └── usb.py
│   ├── protocols/         # Протоколы
│   │   ├── at_commands.py
│   │   ├── qmi.py
│   │   └── mbim.py
│   └── utils/             # Утилиты
│       ├── logger.py
│       └── config.py
├── scripts/
│   ├── detect_device.sh
│   ├── read_imei.sh
│   ├── change_imei.sh
│   ├── restore_imei.sh
│   └── backup_imei.sh
├── firmware/
│   ├── huawei/
│   └── qtech/
└── tests/
```

---

### USB Communication

```python
import serial
import serial.tools.list_ports

class DeviceCommunicator:
    def __init__(self, port: str, baudrate: int = 115200):
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=5
        )
    
    def send_at_command(self, command: str) -> str:
        """Отправка AT команды"""
        self.serial.write(f'{command}\r\n'.encode())
        response = self.serial.read(1024).decode()
        return response
    
    def detect_device(self) -> dict:
        """Обнаружение устройства"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Huawei' in port.description or 'Qtech' in port.description:
                return {
                    'port': port.device,
                    'description': port.description,
                    'serial': port.serial_number
                }
        return None
    
    def read_imei(self) -> str:
        """Чтение IMEI"""
        response = self.send_at_command('AT+CGSN')
        # Парсинг ответа: OK\n861234567890123\n
        lines = response.strip().split('\n')
        for line in lines:
            if line.isdigit() and len(line) == 15:
                return line
        raise Exception('Failed to read IMEI')
    
    def write_imei(self, imei: str) -> bool:
        """Запись IMEI"""
        response = self.send_at_command(f'AT^CIMEI={imei}')
        return 'OK' in response
```

---

### NV Items (Huawei)

```python
class HuaweiNVManager:
    """Управление NV items Huawei"""
    
    # NV item для IMEI
    NV_IMEI_ITEM = 0x0001
    
    def read_nv_item(self, item_id: int) -> bytes:
        """Чтение NV item"""
        command = f'AT^NVREAD={item_id}'
        response = self.comm.send_at_command(command)
        return self._parse_nv_response(response)
    
    def write_nv_item(self, item_id: int, data: bytes) -> bool:
        """Запись NV item"""
        data_hex = data.hex().upper()
        command = f'AT^NVWRITE={item_id},{len(data)},{data_hex}'
        response = self.comm.send_at_command(command)
        return 'OK' in response
    
    def backup_nv_items(self) -> dict:
        """Резервное копирование NV items"""
        backup = {}
        for item_id in [0x0001, 0x0002, 0x0003]:  # IMEI и связанные
            backup[f'item_{item_id}'] = self.read_nv_item(item_id)
        return backup
```

---

### IMEI Structure

```
IMEI: 861234567890123
      │││││││││││││││
      │││││││││││││└─ Check digit (Luhn)
      │││││││││││└─── Software version (optional, IMEISV)
      │││││││└──────── Model identifier
      │││└──────────── Origin code
      └──────────────── Reporting body identifier

Формат: AA-BBBBBB-CCCCCC-D
- AA: Reporting Body Identifier (86 = China)
- BBBBBB: Model identifier
- CCCCCC: Serial number
- D: Check digit
```

---

## Safety & Compliance

### Предупреждения

```
⚠️  ВНИМАНИЕ: Изменение IMEI может быть незаконным в вашей стране!

Используйте этот инструмент только для:
✓ Восстановления после сбоя прошивки
✓ Замены неисправной платы
✓ Тестирования и разработки
✓ Исследовательских целей

Запрещено:
✗ Изменение IMEI для обхода блокировок
✗ Клонирование IMEI других устройств
✗ Сокрытие украденных устройств
```

### Логирование

```python
import logging
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        filename=f'logs/imei_change_{datetime.now():%Y%m%d_%H%M%S}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_operation(operation: str, device: str, old_imei: str, new_imei: str):
    logging.info(f'''
    Operation: {operation}
    Device: {device}
    Serial: {device_serial}
    Old IMEI: {old_imei}
    New IMEI: {new_imei}
    User: {current_user}
    IP: {client_ip}
    ''')
```

---

## Testing

### Unit Tests

```python
def test_imei_validation():
    """Тест валидации IMEI"""
    assert validate_imei('861234567890123') == True
    assert validate_imei('123456789012345') == True
    assert validate_imei('861234567890124') == False
    assert validate_imei('12345') == False
    assert validate_imei('abcdefghijk') == False

def test_imei_checksum():
    """Тест расчета контрольной суммы"""
    assert calculate_luhn_check_digit('86123456789012') == '3'
    assert calculate_luhn_check_digit('12345678901234') == '5'
```

### Integration Tests

```python
def test_full_imei_change():
    """Полный тест изменения IMEI"""
    # 1. Detect device
    device = communicator.detect_device()
    assert device is not None
    
    # 2. Read current IMEI
    old_imei = communicator.read_imei()
    assert validate_imei(old_imei)
    
    # 3. Create backup
    backup_path = backup.create_backup(device, old_imei)
    assert os.path.exists(backup_path)
    
    # 4. Change IMEI
    new_imei = '861234567890124'  # Valid test IMEI
    success = communicator.write_imei(new_imei)
    assert success
    
    # 5. Verify
    current_imei = communicator.read_imei()
    assert current_imei == new_imei
```

---

## Open Questions

1. **Legal**: Какие требования к лицензированию в РФ?
2. **Device Support**: Какие еще устройства поддерживать?
3. **Security**: Как предотвратить незаконное использование?
4. **Backup Storage**: Где хранить резервные копии?

---

*Generated by /legacy from README analysis*
