# Solution

## PDU Mode Configuration

During SIM initialization:
```c
AT+CMGF=0    // Set PDU mode
AT+CSCS="UCS2"  // Set UCS-2 character encoding
```

## PDU Structure (SMS-SUBMIT)

```
+--------+--------+--------+--------+--------+--------+
| SCA    | PDU    | MR     | DA     | PID    | DCS    |
| Length | Type   |        | Length |        |        |
+--------+--------+--------+--------+--------+--------+
| VP     | UDL    | User Data (UD)                     |
|        |        | (hex encoded)                       |
+--------+--------+------------------------------------+
```

### Field Definitions

| Field | Size | Description |
|-------|------|-------------|
| SCA Length | 1 byte | Service Center Address length |
| PDU Type | 1 byte | 11=SMS-SUBMIT |
| MR | 1 byte | Message Reference (0 for auto) |
| DA Length | 1 byte | Destination Address length |
| DA Type | 1 byte | 91=international, 81=national |
| PID | 1 byte | Protocol Identifier (00) |
| DCS | 1 byte | Data Coding Scheme (08=UCS-2) |
| VP | 1 byte | Validity Period |
| UDL | 1 byte | User Data Length |
| UD | var | User Data (hex encoded) |

## Implementation

### PDU Build Function
```c
int pdu_build(
    char * buffer,
    size_t length,
    const char * csca,        // Service center (empty=default)
    const char * dst,         // Destination number
    const char * msg,         // Message (UTF-8)
    unsigned valid_minutes,   // Validity period
    int srr                   // Status report request
);
```

### Two-Stage Send
```c
// Stage 1: AT+CMGS=<length>
>> AT+CMGS=23
<< >

// Stage 2: PDU + Ctrl-Z
>> 0011000B912143658709F00008AA0A8656C6C6F1A
<< OK
```

### Character Encoding
```c
// UTF-8 to UCS-2 conversion
"Hello" → "00480065006C006C006F"
"Привет" → "041F04400438043204350442"
```

## Validity Period Encoding

```c
if (vp <= 5)          vp_encoded = vp * 5 - 1;       // 5-25 min
else if (vp <= 120)   vp_encoded = vp + 24;          // 30min-2h
else if (vp <= 1440)  vp_encoded = (vp / 60) + 143;  // 2h-24h
else                  vp_encoded = (vp / 1440) + 166;// 2d-30d
```

Default: 4320 minutes (3 days) → `0xAA`

## Example PDU

```
Destination: +1234567890
Message: "Hello" (UCS-2)
Validity: 3 days

PDU: 00 11 00 0B 91 21 43 65 87 09 F0 00 08 AA 0A 
     86 56 C6 C6 F0

Breakdown:
00          - SCA length (use default)
11          - PDU type (SMS-SUBMIT)
00          - Message reference
0B          - DA length (11 digits)
91          - DA type (international)
21 43 65 87 09 F0 - Destination (+1234567890)
00          - PID
08          - DCS (UCS-2)
AA          - VP (3 days)
0A          - UDL (10 hex chars = 5 characters)
86 56 C6 C6 F0 - "Hello" in UCS-2
```
