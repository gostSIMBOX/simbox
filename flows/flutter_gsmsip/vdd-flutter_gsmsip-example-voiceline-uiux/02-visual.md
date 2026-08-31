# Visual Mockups: Voice Line Access

> Version: 1.0
> Status: DRAFT
> Last Updated: 2026-03-11
> Source: sdd-voiceline-* flows

---

## Overview

Экраны выбора и настройки метода работы с голосовой линией (телефонной линией/GSM radio).
Система автоматически определяет доступные методы и предлагает оптимальный.

**Методы доступа к линии:**
1. TTY Port — последовательный порт (модель-специфичный)
2. Telecom API — стандартный Android API
3. Enhanced Mode — системный уровень (Magisk, скрыто из UI)
4. Dongle — внешний адаптер (USB-C / TRRS)

---

## Screen 1: Voice Line Status (Главный экран)

Статус и выбор метода работы с телефонной линией.

```
+----------------------------------------------------------+
|  = VOICE LINE                                      [?]   |
+----------------------------------------------------------+
|                                                          |
|  Current Method (auto-detected)                          |
|  +----------------------------------------------------+  |
|  |  ◉ Dongle: USB-C Audio Accessory                 |  |
|  |     Status: Connected                            |  |
|  |     Quality: ★★★★☆                              |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Available Methods                                       |
|  +----------------------------------------------------+  |
|  |  [✓] Dongle (USB-C/TRRS)         Quality: ★★★★☆   |  |
|  |  [✓] Enhanced Mode               Quality: ★★★★☆   |  |
|  |  [✓] Telecom API                 Quality: ★★★☆☆   |  |
|  |  [ ] TTY Port                    Not available    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Signal Path                                             |
|  +----------------------------------------------------+  |
|  |  SIP ──► [Inversion] ──► Dongle ──► Phone Line   |  |
|  |        [L, -R]        [analog]      [diff]        |  |
|  +----------------------------------------------------+  |
|                                                          |
|                         [Change Method]  [Test]          |
|                                                          |
+----------------------------------------------------------+
```

### States

#### No Method Available (Fallback to Acoustic)

```
+----------------------------------------------------------+
|  = VOICE LINE                                      [?]   |
+----------------------------------------------------------+
|                                                          |
|  ! No hardware or enhanced access detected               |
|                                                          |
|  Current Method                                          |
|  +----------------------------------------------------+  |
|  |  ◉ Acoustic Coupling (Earphone→Mic)              |  |
|  |     Status: Active                               |  |
|  |     Quality: ★★☆☆☆                             |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Recommendations                                         |
|  +----------------------------------------------------+  |
|  |  For better quality:                              |  |
|  |  • Connect USB-C or TRRS adapter                 |  |
|  |  • Enable Enhanced Mode in settings              |  |
|  +----------------------------------------------------+  |
|                                                          |
|                         [Setup Adapter]  [Test]          |
|                                                          |
+----------------------------------------------------------+
```

#### Enhanced Mode Active (Magisk, скрыто)

```
+----------------------------------------------------------+
|  = VOICE LINE                                      [?]   |
+----------------------------------------------------------+
|                                                          |
|  Current Method                                          |
|  +----------------------------------------------------+  |
|  |  ◉ Enhanced Mode                                 |  |
|  |     Status: Active                               |  |
|  |     Quality: ★★★★★                              |  |
|  |     System-level audio access                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Signal Path                                             |
|  +----------------------------------------------------+  |
|  |  SIP ──► [Inversion] ──► Direct Audio ──► GSM    |  |
|  |        [L, -R]        [digital]       [radio]     |  |
|  +----------------------------------------------------+  |
|                                                          |
|                         [Change Method]  [Test]          |
|                                                          |
+----------------------------------------------------------+
```

---

## Screen 2: Select Method (Выбор метода)

Ручной выбор метода работы с линией.

```
+----------------------------------------------------------+
|  [<] SELECT VOICE LINE METHOD                            |
+----------------------------------------------------------+
|                                                          |
|  Recommended (auto-detected)                             |
|  +----------------------------------------------------+  |
|  |  ◉ Dongle: USB-C Audio Accessory                 |  |
|  |     Quality: ★★★★☆  │  Status: Connected        |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Other Available Methods                                 |
|  +----------------------------------------------------+  |
|  |  ( ) Enhanced Mode                               |  |
|  |      Quality: ★★★★★  │  System-level access    |  |
|  |                                                    |  |
|  |  ( ) Telecom API                                 |  |
|  |      Quality: ★★★☆☆  │  Standard Android       |  |
|  |                                                    |  |
|  |  ( ) Acoustic Coupling                           |  |
|  |      Quality: ★★☆☆☆  │  Earphone→Mic           |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Not Available                                           |
|  +----------------------------------------------------+  |
|  |  ( ) TTY Port                  [Why unavailable?] |  |
|  +----------------------------------------------------+  |
|                                                          |
|                                           [Apply]        |
+----------------------------------------------------------+
```

### Why Unavailable? - TTY Port

```
+----------------------------------------------------------+
|  [<] WHY TTY PORT UNAVAILABLE?                           |
+----------------------------------------------------------+
|                                                          |
|  TTY Port requires:                                      |
|                                                          |
|  • Device-specific serial port path                     |
|  • Proper permissions (no root on most devices)         |
|  • Known configuration for your device model            |
|                                                          |
|  Your device: No known TTY port detected                 |
|                                                          |
|  Common TTY paths:                                       |
|  • /dev/ttyUSB*  (USB serial)                           |
|  • /dev/ttyHS*   (Qualcomm high-speed)                  |
|  • /dev/ttyGS*   (GSM serial)                           |
|                                                          |
|  [Report Device Model] - Help add support                |
|                                                          |
|                           [OK]  [Manual Config]          |
+----------------------------------------------------------+
```

---

## Screen 3a: TTY Port Configuration

Ручная настройка TTY порта (для продвинутых пользователей).

```
+----------------------------------------------------------+
|  [<] TTY PORT CONFIGURATION                      [Save]  |
+----------------------------------------------------------+
|                                                          |
|  Port Settings                                           |
|  +----------------------------------------------------+  |
|  |  Port Path: [/dev/ttyUSB0      v]                |  |
|  |                                                    |  |
|  |  Common paths:                                    |  |
|  |  • /dev/ttyUSB0  (most common)                   |  |
|  |  • /dev/ttyHS0   (Qualcomm)                      |  |
|  |  • /dev/ttyGS0   (GSM)                           |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Serial Settings                                         |
|  +----------------------------------------------------+  |
|  |  Baud Rate:   [115200    v]                       |  |
|  |  Data Bits:   [8         v]                       |  |
|  |  Stop Bits:   [1         v]                       |  |
|  |  Parity:      [None      v]                       |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Test Connection                                         |
|  +----------------------------------------------------+  |
|  |  [Test Port]                                      |  |
|  |                                                    |  |
|  |  Last result: Port not tested                     |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Device Model                                            |
|  +----------------------------------------------------+  |
|  |  Model: [____________________]  (for detection)   |  |
|  +----------------------------------------------------+  |
|                                                          |
+----------------------------------------------------------+
```

### TTY Test Result - Success

```
+----------------------------------------------------------+
|  [<] TTY PORT TEST RESULT                                |
+----------------------------------------------------------+
|                                                          |
|  ✓ Port opened successfully                              |
|                                                          |
|  +----------------------------------------------------+  |
|  |  Port:         /dev/ttyUSB0                       |  |
|  |  Baud Rate:    115200                             |  |
|  |  Response:     OK                                 |  |
|  |  Latency:      2ms                                |  |
|  +----------------------------------------------------+  |
|                                                          |
|  AT Command Test                                         |
|  +----------------------------------------------------+  |
|  |  AT          → OK                                 |  |
|  |  AT+CMEE=1   → OK                                 |  |
|  |  ATD12345;   → (test call initiated)              |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Port is ready for voice line access.                    |
|                                                          |
|                           [OK]  [Use This Port]          |
+----------------------------------------------------------+
```

### TTY Test Result - Failure

```
+----------------------------------------------------------+
|  [<] TTY PORT TEST RESULT                                |
+----------------------------------------------------------+
|                                                          |
|  ! Port test failed                                      |
|                                                          |
|  +----------------------------------------------------+  |
|  |  Error: Permission denied                         |  |
|  |  Path:  /dev/ttyUSB0                              |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Possible causes:                                        |
|  • Port path incorrect for your device                  |
|  • Permissions not granted                              |
|  • Port already in use                                  |
|  • Device doesn't support TTY access                    |
|                                                          |
|  Suggestions:                                            |
|  • Try different port path (/dev/ttyHS0, /dev/ttyGS0)   |
|  • Check device compatibility                           |
|  • Use Dongle or other method                           |
|                                                          |
|                           [OK]  [Try Another Port]       |
+----------------------------------------------------------+
```

---

## Screen 3b: Enhanced Mode Setup

Настройка "Enhanced Mode" (Magisk, без явного упоминания).

```
+----------------------------------------------------------+
|  [<] ENHANCED MODE SETUP                                 |
+----------------------------------------------------------+
|                                                          |
|  Enhanced Audio Access                                   |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  |  Enables system-level audio access for            |  |
|  |  optimal voice quality.                           |  |
|  |                                                    |  |
|  |  Benefits:                                         |  |
|  |  • Direct digital audio path                      |  |
|  |  • No acoustic coupling loss                      |  |
|  |  • Best audio quality                             |  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Requirements                                            |
|  +----------------------------------------------------+  |
|  |  [✓] System modifications enabled                 |  |
|  |  [✓] Privileged access available                  |  |
|  |  [✓] Gateway app installed as system app          |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Status: Ready                                           |
|                                                          |
|  +----------------------------------------------------+  |
|  |  [Enable Enhanced Mode]                           |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Note: Requires device restart after enabling.           |
|                                                          |
+----------------------------------------------------------+
```

### Enhanced Mode - Not Available

```
+----------------------------------------------------------+
|  [<] ENHANCED MODE SETUP                                 |
+----------------------------------------------------------+
|                                                          |
|  ! Enhanced Mode not available                           |
|                                                          |
|  This feature requires:                                  |
|  • System-level access                                  |
|  • Special installation procedure                       |
|  • Device modifications                                 |
|                                                          |
|  Alternative options:                                    |
|  • Use Dongle (USB-C or TRRS adapter)                  |
|  • Use Acoustic Coupling (earphone→mic)                |
|                                                          |
|  [Contact Support] for installation assistance.          |
|                                                          |
|                           [OK]  [Alternative Methods]    |
+----------------------------------------------------------+
```

---

## Screen 4: Test Voice Line

Тестирование выбранного метода работы с линией.

```
+----------------------------------------------------------+
|  [<] TEST VOICE LINE                           [Stop]    |
+----------------------------------------------------------+
|                                                          |
|  Method: Dongle (USB-C Audio Accessory)                  |
|  Test: Signal Path Verification                          |
|                                                          |
|  ---------------------------------------------------------
|  Signal Path Test                                        |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  |  TX Path (SIP → Line)                             |  |
|  |  [SIP] ──► [Inversion] ──► [Dongle] ──► [Line]   |  |
|  |   ✓         ✓              ✓           ✓         |  |
|  |                                                    |  |
|  |  RX Path (Line → SIP)                             |  |
|  |  [Line] ──► [Dongle] ──► [ADC] ──► [SIP]        |  |
|  |    ✓          ✓           ✓          ✓          |  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Audio Quality Test                                      |
|  +----------------------------------------------------+  |
|  |  Test Tone: 1kHz                                   |  |
|  |                                                    |  |
|  |  TX Level:  [============>     ] -6 dB   OK       |  |
|  |  RX Level:  [===========>      ] -8 dB    OK       |  |
|  |  Latency:   5ms                            OK       |  |
|  |  THD+N:     0.02%                           OK      |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Result: [====== EXCELLENT ======]                       |
|                                                          |
+----------------------------------------------------------+
```

### Test States

#### Testing in Progress

```
+----------------------------------------------------------+
|  [<] TESTING...                                [Cancel]  |
+----------------------------------------------------------+
|                                                          |
|  Running voice line tests...                             |
|                                                          |
|  [=====>          ] 45%                                  |
|                                                          |
|  Current: Testing TX path...                             |
|                                                          |
|  Completed:                                              |
|  ✓ Method detection                                      |
|  ✓ Hardware check                                        |
|  ✓ Signal path verification                              |
|                                                          |
|  In progress:                                            |
|  → Audio quality test                                    |
|                                                          |
|  Pending:                                                |
|  • Echo test                                             |
|  • Full call test                                        |
|                                                          |
+----------------------------------------------------------+
```

#### Test Failed

```
+----------------------------------------------------------+
|  [<] TEST RESULT                                         |
+----------------------------------------------------------+
|                                                          |
|  ! Test failed                                           |
|                                                          |
|  +----------------------------------------------------+  |
|  |  TX Path:     ✓ Passed                           |  |
|  |  RX Path:     ✗ Failed                           |  |
|  |  Audio Level: ✗ Failed                           |  |
|  +----------------------------------------------------+  |
|                                                          |
|  Error: No signal detected on RX path                    |
|                                                          |
|  Possible causes:                                        |
|  • Dongle not properly connected                        |
|  • Wrong dongle type selected                           |
|  • Hardware fault                                       |
|                                                          |
|  Suggestions:                                            |
|  • Reconnect dongle                                     |
|  • Check dongle type configuration                      |
|  • Try different USB port                               |
|                                                          |
|                           [OK]  [Retry]  [Help]          |
+----------------------------------------------------------+
```

---

## Screen 5: Voice Line Settings

Расширенные настройки голосовой линии.

```
+----------------------------------------------------------+
|  [<] VOICE LINE SETTINGS                         [Save]  |
+----------------------------------------------------------+
|                                                          |
|  Audio Settings                                          |
|  +----------------------------------------------------+  |
|  |  Sample Rate:   [48000 Hz   v]                    |  |
|  |  Bit Depth:     [16-bit      v]                  |  |
|  |  Channels:      [Stereo      v]                  |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Signal Processing                                       |
|  +----------------------------------------------------+  |
|  |  [✓] Right Channel Inversion                      |  |
|  |      (for differential signaling)                 |  |
|  |                                                    |  |
|  |  [✓] Echo Cancellation                            |  |
|  |  [ ] Noise Reduction                              |  |
|  |  [ ] Automatic Gain Control                       |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Call Settings                                           |
|  +----------------------------------------------------+  |
|  |  Default Method: [Auto-detect   v]               |  |
|  |                                                    |  |
|  |  [ ] Enable call recording                        |  |
|  |  * May require additional setup                   |  |
|  +----------------------------------------------------+  |
|                                                          |
|  ---------------------------------------------------------
|  Advanced                                                |
|  +----------------------------------------------------+  |
|  |  [Diagnostics]  [Reset to Defaults]               |  |
|  +----------------------------------------------------+  |
|                                                          |
+----------------------------------------------------------+
```

---

## Flow: Voice Line Method Selection

```
                        ┌─────────────────┐
                        │   App Start     │
                        └────────┬────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Detect Available      │
                    │  Methods               │
                    └────────┬───────────────┘
                             │
                             ▼
                    ┌────────────────────────┐
                    │  Best Method Found?    │
                    └────────┬───────────────┘
                             │
              ┌──────────────┼──────────────┐
              │ Yes          │ No           │
              ▼              ▼              ▼
     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
     │ Use Best    │ │ Fallback to │ │ Fallback to │
     │ Method      │ │ Next Best   │ │ Acoustic    │
     └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
            │               │                │
            └───────────────┼────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  Show Status    │
                   │  on Main Screen │
                   └─────────────────┘
```

### Flow: Manual Override

```
[Main Screen] ──(Change Method)──> [Select Method]
                                          │
                                          │ User selects
                                          ▼
                                   ┌──────────────┐
                                   │  Method      │
                                   │  Available?  │
                                   └──────┬───────┘
                                          │
                          ┌───────────────┼───────────────┐
                          │ Yes           │ No            │
                          ▼               ▼               ▼
                   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
                   │  Apply &    │ │  Show Why   │ │  Suggest    │
                   │  Return     │ │  Unavailable│ │  Alternative│
                   └─────────────┘ └─────────────┘ └─────────────┘
```

### Flow: Test Sequence

```
[Test Menu]
     │
     ├─(Signal Path)──> [Path Test] ──> [Result]
     │
     ├─(Audio Quality)──> [Tone Test] ──> [Levels/THD]
     │
     ├─(Echo Test)──────> [Line Echo] ──> [Echo Detection]
     │
     └─(Call Test)──────> [Test Call] ──> [Full Path Verify]
```

---

## Component: Method Quality Indicator

Визуальное отображение качества метода.

```
Quality Levels:

★★★★★  Excellent  (Enhanced Mode)
         Direct digital path, no loss

★★★★☆  Great      (Dongle with DAC, TTY Port)
         High quality, minimal loss

★★★☆☆  Good       (Dongle analog, Telecom API)
         Acceptable for most calls

★★☆☆☆  Fair       (Acoustic Coupling)
         Noticeable quality loss

★☆☆☆☆  Poor       (Fallback, misconfigured)
         Usable but degraded
```

---

## Component: Method Status Icon

```
Connected:    [✓] or ● (green)
Disconnected: [ ] or ○ (gray)
Error:        [!] or ● (red)
Testing:      [⟳] or ● (blinking yellow)
```

---

## Notes

- **Magisk не упоминается** в UI — используется "Enhanced Mode" или "System-level Access"
- **Авто-детекция** — система сама определяет доступные методы
- **Fallback цепочка** — от лучшего к худшему качеству
- **TTY paths** — модель-специфичны, требуется база данных устройств

---

## Approval

- [ ] Reviewed by: [name]
- [ ] Approved on: [date]
- [ ] Notes: [any conditions or clarifications]

---

*Created by /vdd based on sdd-voiceline-* flows*
