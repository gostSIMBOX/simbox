# 02-Specifications

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SMS/USSD Handling Layer                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│   PDU Layer     │ Character Conv  │   AT Integration        │
│   (pdu.c/h)     │ (char_conv.c/h) │  (at_command.c)         │
│                 │                 │                         │
│  - pdu_build    │  - str_recode   │  - at_enque_sms         │
│  - pdu_parse    │  - get_encoding │  - at_enque_pdu         │
│  - pdu_parse_sca│  - parse_hex    │  - at_enque_ussd        │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Character Encoding

### Encoding Types
```c
typedef enum {
    STR_ENCODING_7BIT_HEX   = 0,  // GSM 7-bit (hex encoded)
    STR_ENCODING_8BIT_HEX   = 1,  // 8-bit data (hex encoded)
    STR_ENCODING_UCS2_HEX   = 2,  // UCS-2 (hex encoded)
    STR_ENCODING_7BIT       = 3,  // Plain 7-bit ASCII
    STR_ENCODING_UNKNOWN    = 4
} str_encoding_t;
```

### Encoding/Decoding
```c
ssize_t str_recode(
    recode_direction_t dir,  // RECODE_ENCODE or RECODE_DECODE
    str_encoding_t encoding,
    const char* in,
    size_t in_length,
    char* out,
    size_t out_size
);
```

### Examples
| Input | Encoding | Output |
|-------|----------|--------|
| "Hello" | 7BIT_HEX | "48656C6C6F" |
| "Привет" | UCS2_HEX | "041F04400438043204350442" |
| "48656C6C6F" | 7BIT_HEX (decode) | "Hello" |

## PDU Structure

### SMS-SUBMIT PDU Format
```
+------------------+------------------+------------------+
|    SCA Length    |    SCA Type      |    SCA Digits    |
|    (1 byte)      |    (1 byte)      |    (var)         |
+------------------+------------------+------------------+
|   PDU Type (1)   |    MR (1)        |   DA Length      |
+------------------+------------------+------------------+
|   DA Type        |   DA Digits      |   PID (1)        |
+------------------+------------------+------------------+
|   DCS (1)        |   VP (1)         |   UDL (1)        |
+------------------+------------------+------------------+
|                    User Data (UD)                     |
|                    (hex encoded)                       |
+-------------------------------------------------------+
```

### Field Definitions
| Field | Size | Description |
|-------|------|-------------|
| SCA Length | 1 byte | Service Center Address length |
| SCA Type | 1 byte | Address type (91=intl) |
| SCA Digits | var | Service center number |
| PDU Type | 1 byte | 11=SMS-SUBMIT |
| MR | 1 byte | Message Reference |
| DA Length | 1 byte | Destination Address length |
| DA Type | 1 byte | Address type |
| DA Digits | var | Destination number |
| PID | 1 byte | Protocol Identifier |
| DCS | 1 byte | Data Coding Scheme |
| VP | 1 byte | Validity Period |
| UDL | 1 byte | User Data Length |
| UD | var | User Data (encoded) |

## PDU Building

### Function Signature
```c
int pdu_build(
    char * buffer,
    size_t length,
    const char * csca,        // Service center (empty for default)
    const char * dst,         // Destination number
    const char * msg,         // Message (UTF-8)
    unsigned valid_minutes,   // Validity period
    int srr                   // Status report request
);
```

### DCS Values
| DCS | Encoding |
|-----|----------|
| 00  | 7-bit default |
| 04  | 8-bit data |
| 08  | UCS-2 (16-bit) |

### Validity Period Encoding
```c
// VP encoding (relative format)
if (vp <= 5)          vp_encoded = vp * 5 - 1;       // 5 min to 25 min
else if (vp <= 120)   vp_encoded = vp + 24;          // 30 min to 144 min
else if (vp <= 1440)  vp_encoded = (vp / 60) + 143;  // 2h to 24h
else                  vp_encoded = (vp / 1440) + 166;// 2d to 30d
```

### Example PDU Build
```
Destination: +1234567890
Message: "Hello"
SCA: (default)
Validity: 4320 minutes (3 days)

PDU: 0011000B912143658709F00008AA0A8656C6C6F
     ^^ SCA length (0 = use default)
       ^^ PDU type (11 = SMS-SUBMIT)
         ^^ Message reference (00)
           ^^ DA length (0B = 11 digits)
             ^^ DA type (91 = international)
               ^^ DA digits (2143658709F0 = +1234567890)
                             ^^ PID (00)
                               ^^ DCS (08 = UCS-2)
                                 ^^ VP (AA = 3 days)
                                   ^^ UDL (0A = 10 hex chars = 5 chars)
                                     ^^ UD (hex encoded "Hello")
```

## PDU Parsing

### Parse SCA
```c
int pdu_parse_sca(char ** pdu, size_t * length)
{
    int scalen = parse_hexdigit((*pdu)[0]) * 2;
    *pdu += 2;
    *length -= scalen + 2;
    return scalen + 2;  // Total SCA bytes including length field
}
```

### Parse Full PDU
```c
const char * pdu_parse(
    char ** pdu,           // Input/output PDU pointer
    size_t tpdu_length,    // TPDU length
    char * oa,             // Output sender address
    size_t oa_len,         // Sender buffer size
    str_encoding_t * oa_enc,// Sender encoding
    char ** msg,           // Output message
    str_encoding_t * msg_enc // Message encoding
);
```

## SMS Sending Flow

### Two-Stage Send
```c
EXPORT_DEF int at_enque_sms(
    struct cpvt* cpvt,
    const char* destination,
    const char* msg,
    unsigned validity_minutes,
    int report_req,
    void ** id
)
{
    // Build PDU
    res = pdu_build(pdu_buf, sizeof(pdu_buf), "", 
                    destination, msg, validity_minutes, report_req);
    
    // Two-stage command
    at_queue_cmd_t at_cmd[] = {
        { CMD_AT_CMGS,    RES_SMS_PROMPT, 
          ATQ_CMD_FLAG_DEFAULT, { ATQ_CMD_TIMEOUT_2S, 0 }, NULL, 0 },
        { CMD_AT_SMSTEXT, RES_OK, 
          ATQ_CMD_FLAG_DEFAULT, { ATQ_CMD_TIMEOUT_40S, 0 }, NULL, 0 }
    };
    
    // Stage 1: AT+CMGS=<length>
    at_cmd[0].length = snprintf(buf, sizeof(buf), "AT+CMGS=%d\r", pdulen/2);
    at_cmd[0].data = ast_strdup(buf);
    
    // Stage 2: PDU + Ctrl-Z
    at_cmd[1].data = ast_malloc(length + 2);
    memcpy(at_cmd[1].data, pdu, length);
    at_cmd[1].data[length] = 0x1A;  // Ctrl-Z
    at_cmd[1].data[length+1] = 0x0;
    
    return at_queue_insert_task(cpvt, at_cmd, 2, 0, id);
}
```

### Response Sequence
```
>> AT+CMGS=23
<< >                 (RES_SMS_PROMPT)
>> 001100...1A       (PDU + Ctrl-Z)
<< OK                (RES_OK)
```

## USSD Handling

### Send USSD
```c
EXPORT_DEF int at_enque_ussd(
    struct cpvt * cpvt,
    const char * code,
    void ** id
)
{
    static const char cmd[] = "AT+CUSD=1,\"";
    static const char cmd_end[] = "\",15\r";
    
    // Determine encoding
    if (pvt->cusd_use_7bit_encoding)
        cusd_encoding = STR_ENCODING_7BIT_HEX;
    else if (pvt->use_ucs2_encoding)
        cusd_encoding = STR_ENCODING_UCS2_HEX;
    else
        cusd_encoding = STR_ENCODING_7BIT;
    
    // Build command
    memcpy(buf, cmd, STRLEN(cmd));
    length = STRLEN(cmd);
    
    if (*code != '=') {
        // Encode the code
        res = str_recode(RECODE_ENCODE, cusd_encoding, code, 
                        strlen(code), buf + length, 
                        sizeof(buf) - length - STRLEN(cmd_end) - 1);
        length += res;
    } else {
        // Raw code (skip leading =)
        strcpy(buf + length, code + 1);
        length += strlen(code) - 1;
    }
    
    memcpy(buf + length, cmd_end, STRLEN(cmd_end) + 1);
    length += STRLEN(cmd_end);
    
    at_cmd.data = ast_strdup(buf);
    at_cmd.length = length;
    
    return at_queue_insert_task(cpvt, &at_cmd, 1, 0, id);
}
```

### USSD Response Codes
| Code | Meaning |
|------|---------|
| 0 | No further action required |
| 1 | Further action required |
| 2 | Session terminated by network |
| 3 | Other local client has responded |

## SMS Storage Commands

### Storage Selection
```
AT+CPMS="ME","ME","ME"  // Use ME storage for read/write/delete
```

### Read SMS
```
AT+CMGR=<index>
+CMGR: <stat>,<oa>,<alpha>,<scts>[,<tooa>,<fo>,<pid>,<dcs>,<sca>,<tosca>,<length>
<PDU data>
OK
```

### Delete SMS
```
AT+CMGD=<index>[,<delflag>]
```

### New SMS Notification
```
+CNMI=1,1,0,1,0  // Mode settings

+CMTI: "ME",<index>  // New SMS notification
```

## Error Handling

### PDU Build Errors
| Error | Code | Description |
|-------|------|-------------|
| Message too long | -E2BIG | Exceeds 140 octets |
| Invalid number | -EINVAL | Invalid phone number format |
| Memory error | -ENOMEM | Allocation failed |

### Send Errors
| Error | Handling |
|-------|----------|
| No SMS prompt | Timeout after 2s, retry |
| No OK response | Timeout after 40s, log error |
| Invalid PDU | Return error before queue |

## CLI Commands

```
dongle sms <device> <number> <message>
  - Send SMS from CLI
  - UTF-8 message converted to PDU

dongle pdu <device> <pdu>
  - Send raw PDU
  - For testing/debugging

dongle ussd <device> <code>
  - Send USSD code
  - Display response
```

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of pdu.h, char_conv.h, at_command.c (SMS/USSD functions)
