# 01-Requirements

## Overview

SMS and USSD handling for Huawei UMTS dongles with PDU mode encoding.

## Functional Requirements

### FR-1: SMS Sending
The system SHALL send SMS messages with:
- PDU mode format (binary encoding)
- UCS-2 character encoding for international characters
- 7-bit GSM default alphabet support
- Message validity period configuration
- Delivery report request support
- Maximum 140 octets per SMS

### FR-2: SMS Receiving
The system SHALL receive SMS messages via:
- `+CMTI` unsolicited notification
- Message retrieval via `AT+CMGR`
- PDU parsing to extract sender and content
- Character decoding (UCS-2/7-bit)
- Optional message deletion after read

### FR-3: USSD Sending
The system SHALL send USSD codes with:
- `AT+CUSD=1,"<code>",15` format
- 7-bit hex or UCS-2 hex encoding
- Raw code support (codes starting with `=`)
- Response capture via `+CUSD`

### FR-4: USSD Receiving
The system SHALL handle USSD responses:
- `+CUSD` unsolicited notification
- Response code parsing (0-3)
- Message decoding (UCS-2/7-bit)
- DCS (Data Coding Scheme) interpretation

### FR-5: Character Encoding
The system SHALL support encodings:
- `STR_ENCODING_7BIT_HEX` - GSM 7-bit (hex encoded)
- `STR_ENCODING_8BIT_HEX` - 8-bit data (hex encoded)
- `STR_ENCODING_UCS2_HEX` - UCS-2 (hex encoded)
- `STR_ENCODING_7BIT` - Plain 7-bit ASCII
- Bidirectional conversion (encode/decode)

### FR-6: PDU Building
The system SHALL build SMS PDU with:
- Service Center Address (SCA)
- Destination address
- Protocol Identifier (PID)
- Data Coding Scheme (DCS)
- Validity Period (VP)
- User Data (UD)

### FR-7: PDU Parsing
The system SHALL parse received PDU:
- Extract SCA length and value
- Extract sender address (OA)
- Extract DCS for encoding detection
- Extract user data length and content
- Handle SMS-DELIVER and SMS-SUBMIT

### FR-8: SMS Storage
The system SHALL manage SMS storage:
- Storage selection via `AT+CPMS`
- Message index tracking
- Delete after read option
- Storage full detection (`+SMSFULL`)

## Non-Functional Requirements

### NFR-1: Performance
- SMS send SHALL complete within 40 seconds
- PDU encoding SHALL handle 160 character messages
- USSD response SHALL be captured within 5 seconds

### NFR-2: Reliability
- Invalid PDU SHALL return error before send
- Encoding errors SHALL be logged
- Delivery reports SHALL be tracked

### NFR-3: Memory
- PDU buffer SHALL be 2048 bytes minimum
- Encoding conversion SHALL handle 4096 byte output
- Temporary allocations SHALL be freed after use

### NFR-4: Compatibility
- PDU mode SHALL work with all Huawei dongles
- UCS-2 SHALL support all Unicode BMP characters
- 7-bit SHALL support GSM default alphabet

## Dependencies

- AT Command Protocol: Command queuing
- Character Conversion: Encoding/decoding
- Device Communication: Data transport

## Constraints

- SMS limited to 140 octets (160 7-bit chars, 70 UCS-2 chars)
- SCA limited to 20 digits
- Destination number limited to 20 digits

## Status

**Status**: DRAFT  
**Created**: 2026-03-02  
**Source**: Legacy analysis of pdu.c/h, char_conv.c/h, at_command.c (SMS functions)
