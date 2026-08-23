# 01-Stakeholder Requirements: VoIP Calling Feature

## Overview

This document describes the VoIP (Voice over IP) calling feature from a stakeholder perspective. It explains what business value the feature provides and what capabilities end-users expect.

## Business Value

### Problem Statement

Organizations need mobile communication solutions that:
- Work over internet (WiFi/cellular data)
- Integrate with existing SIP/PBX infrastructure
- Provide enterprise-grade call quality
- Support remote and mobile workers
- Reduce communication costs (especially for international calls)

### Solution Value

**react-native-sip2** enables businesses to:
- Build custom mobile SIP clients for iOS and Android
- Leverage existing PBX phone systems
- Provide employees with business phone numbers on personal devices
- Enable video calling capabilities
- Support remote work scenarios
- Reduce mobile communication costs

### Target Users

1. **Enterprise Employees**: Business calling on mobile devices
2. **Remote Workers**: Home office SIP phone capability
3. **Customer Support**: Mobile softphone for support agents
4. **Healthcare**: Secure HIPAA-compliant communication
5. **Field Services**: Dispatch communication via mobile

## Stakeholder Requirements

### SR-1: Make Outgoing Calls

**As a** mobile worker  
**I want to** dial phone numbers and make calls over internet  
**So that** I can communicate with clients and colleagues without using cellular minutes

**Acceptance Criteria**:
- Can dial phone numbers or SIP addresses
- Call connects within 3 seconds on good network
- Audio quality is clear and natural
- Works on WiFi and cellular data (3G/4G/5G)
- Shows call duration and status

**Business Value**:
- Eliminates need for separate business phone
- Reduces mobile phone bills
- Enables international calls at low cost

### SR-2: Receive Incoming Calls

**As a** remote employee  
**I want to** receive calls to my business number on my mobile device  
**So that** clients can reach me wherever I am

**Acceptance Criteria**:
- Incoming calls ring within 2 seconds
- Works when app is in background (push notifications)
- Shows caller ID (name/number)
- Can answer with single tap
- Automatic audio routing (speaker/earpiece)

**Business Value**:
- Improves responsiveness to clients
- Enables true mobile office capability
- Maintains professional presence

### SR-3: Video Calling

**As a** healthcare provider  
**I want to** have face-to-face video calls with patients  
**So that** I can provide remote consultations effectively

**Acceptance Criteria**:
- Can enable video during audio call
- Shows self-preview and remote video
- Video is smooth (minimum 15 FPS)
- Automatically adjusts quality based on network
- Can switch between front/back camera
- Can turn video on/off during call

**Business Value**:
- Enables telemedicine consultations
- Improves patient engagement
- Reduces need for in-person visits

### SR-4: Call Management

**As a** customer support agent  
**I want to** manage multiple calls (hold, transfer, conference)  
**So that** I can handle customer inquiries professionally

**Acceptance Criteria**:
- Can put calls on hold
- Can transfer calls to other extensions
- Can merge calls for conference
- Can mute/unmute microphone
- Can switch between speaker and earpiece
- Can send DTMF tones (for phone menus)

**Business Value**:
- Professional call handling
- Efficient customer service
- Reduced call drops and transfers

### SR-5: Account Configuration

**As an** IT administrator  
**I want to** configure SIP accounts on employee devices  
**So that** they can connect to our PBX system

**Acceptance Criteria**:
- Can add SIP account with username/password
- Supports common SIP providers (Asterisk, FreePBX, 3CX)
- Configures server, port, transport automatically
- Shows registration status (connected/disconnected)
- Auto-reconnects if connection lost
- Supports multiple accounts (personal + business)

**Business Value**:
- Easy deployment to employee devices
- Supports existing PBX infrastructure
- Minimal IT support required

### SR-6: Network Resilience

**As a** field service technician  
**I want** calls to work reliably on various networks  
**So that** I can communicate from any location

**Acceptance Criteria**:
- Works on WiFi, 4G, 5G networks
- Handles network switching (WiFi → cellular)
- Reconnects automatically after signal loss
- Shows network status indicator
- Works in areas with weak signal

**Business Value**:
- Reliable communication from anywhere
- Reduced missed calls
- Improved service quality

### SR-7: Battery Efficiency

**As a** mobile worker  
**I want** the app to be battery-efficient  
**So that** my phone lasts through the workday

**Acceptance Criteria**:
- Background registration uses minimal battery
- Idle drain is less than 5% per hour
- Calls don't cause excessive battery drain
- App doesn't overheat device

**Business Value**:
- All-day battery life
- Employee satisfaction
- No need for constant charging

### SR-8: Security & Privacy

**As a** healthcare provider  
**I want** calls to be secure and private  
**So that** patient information remains confidential

**Acceptance Criteria**:
- Supports encrypted connections (TLS)
- Supports secure media (SRTP)
- No call logs stored on device (optional)
- Complies with HIPAA requirements
- Password-protected account configuration

**Business Value**:
- Regulatory compliance (HIPAA, GDPR)
- Patient trust
- Legal protection

## Non-Stakeholder Requirements (Technical)

These are important but not visible to stakeholders:

- **NSR-1**: Native PjSIP integration (performance)
- **NSR-2**: EventEmitter architecture (maintainability)
- **NSR-3**: Promise-based API (developer experience)
- **NSR-4**: Immutable data models (reliiability)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Call Setup Time | < 3 seconds | Time from dial to ringing |
| Call Success Rate | > 95% | Successful connects / attempts |
| Audio Quality (MOS) | > 4.0 | Mean Opinion Score |
| Video Frame Rate | > 15 FPS | Frames per second |
| Battery Drain (idle) | < 5%/hour | Background consumption |
| Registration Success | > 99% | Successful registrations |
| Crash Rate | < 0.1% | Crashes per session |

## Stakeholder Glossary

| Term | Definition |
|------|------------|
| **SIP** | Session Initiation Protocol - standard for VoIP calls |
| **PBX** | Private Branch Exchange - business phone system |
| **Extension** | Internal phone number within PBX |
| **VoIP** | Voice over IP - phone calls over internet |
| **Softphone** | Software-based phone (app vs hardware) |
| **Registration** | Process of connecting SIP account to server |
| **DTMF** | Dual-Tone Multi-Frequency - phone keypad tones |
| **MOS** | Mean Opinion Score - audio quality rating (1-5) |

## Related Documents

- **SDD**: flows/sdd-endpoint/ - Technical API specification
- **ADR**: flows/adr-*/* - Architectural decisions
- **Installation**: docs/installation_ios.md, docs/installation_android.md

---

*Status: DRAFT | Type: DDD | Generated by /legacy*
