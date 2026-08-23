# Specifications: Android Telecom Integration

**Status**: DRAFT  
**Type**: SDD (Spec-Driven Development)  
**Module**: android-telecom-integration  
**Generated**: 2026-03-04 by /legacy

---

## Specification Overview

This document specifies the implementation details of the Android telecom integration based on analysis of existing code in `android/src/main/kotlin/org/telon/tele/flutter_tele/TeleService.kt`.

---

## Architecture

### InCallService Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  Android Telecom Framework                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ InCallService                                          │  │
│  │  - onCallAdded(call)                                   │  │
│  │  - onCallRemoved(call)                                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ TeleService : InCallService                            │  │
│  │  - mCalls: List<TeleCall>                              │  │
│  │  - callMapping: Map<Int, Call>                         │  │
│  │  - currentCall: Call?                                  │  │
│  │                                                        │  │
│  │  - onCallAdded():                                      │  │
│  │      • Create TeleCall                                 │  │
│  │      • Register Call.Callback                          │  │
│  │      • Send event to Flutter                           │  │
│  │  - onCallRemoved():                                    │  │
│  │      • Update TeleCall state                           │  │
│  │      • Clean up mapping                                │  │
│  │      • Send event to Flutter                           │  │
│  │  - Call control:                                       │  │
│  │      • answer(), hangup(), hold(), unhold()            │  │
│  │  - Audio control:                                      │  │
│  │      • mute(), speaker(), earpiece()                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                 │
│            EventChannel  │                                   │
│                            ▼                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ FlutterTelePlugin                                      │  │
│  │  - sendEvent(type, data)                               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Callback Chain

```
Android Telecom
     │
     │ onCallAdded(call)
     ▼
TeleService
     │
     ├── Create TeleCall
     ├── callMapping[id] = call
     ├── Register Call.Callback
     │       │
     │       │ onStateChanged(call, state)
     │       ├─────────────────────────────► Send "call_changed" event
     │       │
     │       │ onCallDestroyed(call)
     │       ├─────────────────────────────► Send "call_terminated" event
     │       │
     │       ▼
     │   Clean up mapping
     │
     └── Send "call_received" event
```

---

## TeleService Implementation Specification

### Service Lifecycle

```kotlin
class TeleService : InCallService() {
    companion object {
        private const val TAG = "TeleService"
        private var instance: TeleService? = null
        
        fun getInstance(): TeleService? = instance
    }
    
    // State
    private var mInitialized = false
    private val mCalls = mutableListOf<TeleCall>()
    private var currentCall: Call? = null
    private var teleCallIds = 0
    private val callMapping = mutableMapOf<Int, Call>()
    
    // System services
    private var mHandler: Handler? = null
    private var mAudioManager: AudioManager? = null
    private var mPowerManager: PowerManager? = null
    private var mTelephonyManager: TelephonyManager? = null
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        mHandler = Handler(Looper.getMainLooper())
        mAudioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
        mPowerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        mTelephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        intent?.let { handleIntent(it) }
        return START_STICKY
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
    }
}
```

### Intent Handling

```kotlin
private fun handleIntent(intent: Intent) {
    when (intent.action) {
        "START_TELEPHONY_SERVICE" -> {
            val configuration = intent.getStringExtra("configuration")
            initializeService()
        }
        "MAKE_CALL" -> {
            val sim = intent.getIntExtra("sim", 1)
            val destination = intent.getStringExtra("destination") ?: ""
            val callSettings = intent.getStringExtra("callSettings")
            val msgData = intent.getStringExtra("msgData")
            makeCall(sim, destination, callSettings, msgData)
        }
        "ANSWER_CALL" -> {
            val callId = intent.getIntExtra("callId", -1)
            answerCall(callId)
        }
        "HANGUP_CALL" -> {
            val callId = intent.getIntExtra("callId", -1)
            hangupCall(callId)
        }
        // ... other actions
    }
}
```

### InCallService Callbacks

#### onCallAdded

```kotlin
override fun onCallAdded(call: Call) {
    super.onCallAdded(call)
    currentCall = call
    
    // Extract call details
    val callDetails = call.details
    val handle = callDetails.handle
    val remoteNumber = handle?.schemeSpecificPart ?: ""
    val remoteName = callDetails.callerDisplayName ?: remoteNumber
    
    // Find existing TeleCall or create new one
    var teleCall = mCalls.find { 
        it.destination == remoteNumber && it.state == "INITIATING" 
    }
    
    if (teleCall == null) {
        // Incoming call: create new TeleCall
        teleCallIds++
        teleCall = TeleCall(
            id = teleCallIds,
            destination = remoteNumber,
            sim = 1,
            state = "INCOMING",
            direction = "DIRECTION_INCOMING",
            remoteNumber = remoteNumber,
            remoteName = remoteName
        )
        mCalls.add(teleCall)
    } else {
        // Outgoing call: update existing TeleCall
        teleCall.state = "CONNECTING"
        teleCall.remoteNumber = remoteNumber
        teleCall.remoteName = remoteName
    }
    
    // Map Android Call to TeleCall
    callMapping[teleCall.id] = call
    
    // Send event to Flutter
    FlutterTelePlugin.getInstance()?.sendEvent(
        "call_received", 
        teleCall.toMap() as Map<String, Any>
    )
    
    // Register Call.Callback for state changes
    call.registerCallback(object : Call.Callback() {
        override fun onStateChanged(call: Call, state: Int) {
            super.onStateChanged(call, state)
            
            teleCall.state = when (state) {
                Call.STATE_RINGING -> "RINGING"
                Call.STATE_DISCONNECTED -> "DISCONNECTED"
                Call.STATE_ACTIVE -> "ACTIVE"
                Call.STATE_HOLDING -> "HOLDING"
                Call.STATE_DIALING -> "DIALING"
                Call.STATE_CONNECTING -> "CONNECTING"
                else -> "UNKNOWN"
            }
            
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
        }
        
        override fun onCallDestroyed(call: Call) {
            super.onCallDestroyed(call)
            
            teleCall.state = "DISCONNECTED"
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_terminated", 
                teleCall.toMap() as Map<String, Any>
            )
            
            mCalls.remove(teleCall)
            callMapping.remove(teleCall.id)
        }
    })
}
```

#### onCallRemoved

```kotlin
override fun onCallRemoved(call: Call) {
    super.onCallRemoved(call)
    
    // Find associated TeleCall
    val teleCallId = callMapping.entries.find { it.value == call }?.key
    val teleCall = if (teleCallId != null) {
        findCall(teleCallId)
    } else {
        findCallByCall(call)
    }
    
    if (teleCall != null) {
        teleCall.state = "DISCONNECTED"
        FlutterTelePlugin.getInstance()?.sendEvent(
            "call_terminated", 
            teleCall.toMap() as Map<String, Any>
        )
        mCalls.remove(teleCall)
        callMapping.remove(teleCall.id)
    }
    
    if (currentCall == call) {
        currentCall = null
    }
}
```

### Call Control Operations

#### makeCall

```kotlin
private fun makeCall(sim: Int, destination: String, 
                     callSettings: String?, msgData: String?) {
    try {
        // Create TeleCall for tracking
        teleCallIds++
        val teleCall = TeleCall(
            id = teleCallIds,
            destination = destination,
            sim = sim,
            state = "INITIATING"
        )
        mCalls.add(teleCall)
        
        // Send call_received event
        FlutterTelePlugin.getInstance()?.sendEvent(
            "call_received", 
            teleCall.toMap()
        )
        
        // Make actual phone call using Intent.ACTION_CALL
        val url = "tel:$destination"
        val callIntent = Intent(Intent.ACTION_CALL, Uri.parse(url)).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            // Set SIM slot information (try multiple keys for compatibility)
            val simSlotNames = arrayOf(
                "android.intent.extra.SLOT_ID",
                "android.intent.extra.SIM_SLOT_INDEX",
                "android.intent.extra.SUB_ID"
            )
            for (slotName in simSlotNames) {
                putExtra(slotName, sim - 1)  // Convert to 0-based
            }
            
            // Try to set PhoneAccountHandle for specific SIM
            try {
                val subscriptionManager = getSystemService(
                    Context.TELEPHONY_SUBSCRIPTION_SERVICE
                ) as SubscriptionManager
                val telecomManager = getSystemService(
                    Context.TELECOM_SERVICE
                ) as TelecomManager
                
                val phoneAccounts = telecomManager.callCapablePhoneAccounts
                if (phoneAccounts.isNotEmpty()) {
                    val phoneAccount = phoneAccounts.getOrNull(sim - 1) 
                        ?: phoneAccounts.first()
                    putExtra(
                        "android.telecom.extra.PHONE_ACCOUNT_HANDLE", 
                        phoneAccount
                    )
                }
            } catch (e: Exception) {
                Log.w(TAG, "Could not set phone account handle: ${e.message}")
            }
        }
        
        // Start call activity
        startActivity(callIntent)
        
        // Simulate state change after delay (1 second)
        mHandler?.postDelayed({
            teleCall.state = "CONNECTING"
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
        }, 1000)
        
    } catch (e: Exception) {
        Log.e(TAG, "Error making call", e)
        FlutterTelePlugin.getInstance()?.sendEvent(
            "call_error", 
            mapOf(
                "error" to e.message,
                "destination" to destination,
                "sim" to sim
            )
        )
    }
}
```

#### answerCall

```kotlin
private fun answerCall(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            val androidCall = callMapping[callId] ?: currentCall
            
            if (androidCall != null) {
                androidCall.answer(0)
                Log.d(TAG, "Answered Android call for TeleCall ID: $callId")
            } else {
                Log.w(TAG, "No Android Call object found for TeleCall ID: $callId")
            }
            
            teleCall.state = "CONNECTED"
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error answering call", e)
    }
}
```

#### hangupCall

```kotlin
private fun hangupCall(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            val androidCall = callMapping[callId] ?: currentCall
            
            if (androidCall != null) {
                androidCall.disconnect()
                Log.d(TAG, "Disconnected Android call for TeleCall ID: $callId")
            } else {
                Log.w(TAG, "No Android Call object found for TeleCall ID: $callId")
            }
            
            teleCall.state = "DISCONNECTED"
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_terminated", 
                teleCall.toMap() as Map<String, Any>
            )
            mCalls.remove(teleCall)
            callMapping.remove(callId)
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error hanging up call", e)
    }
}
```

#### holdCall / unholdCall

```kotlin
private fun holdCall(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            val androidCall = callMapping[callId] ?: currentCall
            
            if (androidCall != null) {
                androidCall.hold()
                Log.d(TAG, "Held Android call for TeleCall ID: $callId")
            }
            
            teleCall.held = true
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error holding call", e)
    }
}

private fun unholdCall(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            val androidCall = callMapping[callId] ?: currentCall
            
            if (androidCall != null) {
                androidCall.unhold()
                Log.d(TAG, "Unheld Android call for TeleCall ID: $callId")
            }
            
            teleCall.held = false
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error unholding call", e)
    }
}
```

### Audio Control Operations

#### muteCall / unMuteCall

```kotlin
private fun muteCall(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            mAudioManager?.isMicrophoneMute = true
            teleCall.muted = true
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
            Log.d(TAG, "Call muted: $callId")
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error muting call", e)
    }
}

private fun unMuteCall(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            mAudioManager?.isMicrophoneMute = false
            teleCall.muted = false
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
            Log.d(TAG, "Call unmuted: $callId")
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error unmuting call", e)
    }
}
```

#### useSpeaker / useEarpiece

```kotlin
private fun useSpeaker(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            mAudioManager?.mode = AudioManager.MODE_NORMAL
            mAudioManager?.isSpeakerphoneOn = true
            teleCall.speaker = true
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
            Log.d(TAG, "Speaker enabled: $callId")
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error using speaker", e)
    }
}

private fun useEarpiece(callId: Int) {
    try {
        val teleCall = findCall(callId)
        if (teleCall != null) {
            mAudioManager?.mode = AudioManager.MODE_IN_COMMUNICATION
            mAudioManager?.isSpeakerphoneOn = false
            teleCall.speaker = false
            FlutterTelePlugin.getInstance()?.sendEvent(
                "call_changed", 
                teleCall.toMap() as Map<String, Any>
            )
            Log.d(TAG, "Earpiece enabled: $callId")
        }
    } catch (e: Exception) {
        Log.e(TAG, "Error using earpiece", e)
    }
}
```

### Helper Methods

#### findCall

```kotlin
private fun findCall(callId: Int): TeleCall? {
    return mCalls.find { it.id == callId }
}
```

#### findCallByCall (fallback)

```kotlin
private fun findCallByCall(call: Call): TeleCall? {
    // Simplified implementation - may return wrong call in multi-call scenarios
    return mCalls.lastOrNull()
}
```

---

## TeleCall Data Class Specification

```kotlin
data class TeleCall(
    val id: Int,
    val destination: String? = null,
    val sim: Int? = null,
    var state: String? = null,
    var held: Boolean? = null,
    var muted: Boolean? = null,
    var speaker: Boolean? = null,
    val direction: String? = null,
    var remoteNumber: String? = null,
    var remoteName: String? = null
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "id" to id,
            "destination" to (destination ?: ""),
            "sim" to (sim ?: 1),
            "state" to (state ?: "UNKNOWN"),
            "held" to (held ?: false),
            "muted" to (muted ?: false),
            "speaker" to (speaker ?: false),
            "direction" to (direction ?: "UNKNOWN"),
            "remoteNumber" to (remoteNumber ?: ""),
            "remoteName" to (remoteName ?: "")
        )
    }
}
```

**Note**: This is a minimal model (10 fields) compared to Dart's TeleCall (40+ fields). See sdd-call-model for full specification.

---

## Intent Action Specification

| Action | Parameters | Handler | Description |
|--------|------------|---------|-------------|
| START_TELEPHONY_SERVICE | configuration: String | initializeService() | Start service with config |
| MAKE_CALL | sim: Int, destination: String, callSettings: String, msgData: String | makeCall() | Initiate outgoing call |
| ANSWER_CALL | callId: Int | answerCall() | Answer incoming call |
| HANGUP_CALL | callId: Int | hangupCall() | End call |
| DECLINE_CALL | callId: Int | declineCall() | Reject incoming call |
| HOLD_CALL | callId: Int | holdCall() | Hold call |
| UNHOLD_CALL | callId: Int | unholdCall() | Resume held call |
| MUTE_CALL | callId: Int | muteCall() | Mute microphone |
| UNMUTE_CALL | callId: Int | unMuteCall() | Unmute microphone |
| USE_SPEAKER | callId: Int | useSpeaker() | Enable speakerphone |
| USE_EARPIECE | callId: Int | useEarpiece() | Enable earpiece |

---

## SIM Slot Selection Specification

### Strategy

1. **Convert to 0-based**: `simSlot = sim - 1`
2. **Try Intent extras** (multiple keys for compatibility):
   - `android.intent.extra.SLOT_ID`
   - `android.intent.extra.SIM_SLOT_INDEX`
   - `android.intent.extra.SUB_ID`
3. **Try PhoneAccountHandle** (more reliable):
   - Get `callCapablePhoneAccounts` from TelecomManager
   - Select account by index: `phoneAccounts.getOrNull(simSlot)`
   - Fallback to first account if index out of bounds
   - Set `PHONE_ACCOUNT_HANDLE` extra
4. **Handle exceptions**: Log warning, continue without SIM selection

### Code

```kotlin
// Step 1: Convert to 0-based
val simSlot = sim - 1

// Step 2: Try Intent extras
val simSlotNames = arrayOf(
    "android.intent.extra.SLOT_ID",
    "android.intent.extra.SIM_SLOT_INDEX",
    "android.intent.extra.SUB_ID"
)
for (slotName in simSlotNames) {
    callIntent.putExtra(slotName, simSlot)
}

// Step 3: Try PhoneAccountHandle
try {
    val subscriptionManager = getSystemService(
        Context.TELEPHONY_SUBSCRIPTION_SERVICE
    ) as SubscriptionManager
    val telecomManager = getSystemService(
        Context.TELECOM_SERVICE
    ) as TelecomManager
    
    val phoneAccounts = telecomManager.callCapablePhoneAccounts
    if (phoneAccounts.isNotEmpty()) {
        val phoneAccount = phoneAccounts.getOrNull(simSlot) 
            ?: phoneAccounts.first()
        callIntent.putExtra(
            "android.telecom.extra.PHONE_ACCOUNT_HANDLE", 
            phoneAccount
        )
    }
} catch (e: Exception) {
    Log.w(TAG, "Could not set phone account handle: ${e.message}")
}
```

---

## Known Issues and Limitations

### Issue 1: State Change Simulation

**Problem**: `makeCall()` posts delayed state change instead of waiting for real callback.

```kotlin
// Simulate state change after delay
mHandler?.postDelayed({
    teleCall.state = "CONNECTING"
    FlutterTelePlugin.getInstance()?.sendEvent("call_changed", teleCall.toMap())
}, 1000)  // 1 second delay
```

**Impact**: State may not match actual call state if call fails quickly.

**Recommended Fix**: Remove simulation, rely on `Call.Callback.onStateChanged()`.

### Issue 2: findCallByCall() Fallback

**Problem**: Uses `lastOrNull()` which may return wrong call.

```kotlin
private fun findCallByCall(call: Call): TeleCall? {
    return mCalls.lastOrNull()  // May return wrong call!
}
```

**Impact**: Operations may affect wrong call in multi-call scenarios.

**Recommended Fix**: Always use `callMapping`, remove `findCallByCall()`.

### Issue 3: Audio Mode Management

**Problem**: Changes audio mode without saving/restoring previous mode.

```kotlin
mAudioManager?.mode = AudioManager.MODE_NORMAL  // Overwrites previous mode
mAudioManager?.isSpeakerphoneOn = true
```

**Impact**: May conflict with other audio-using apps.

**Recommended Fix**: Save mode before change, restore after call ends.

### Issue 4: Service Restart State Loss

**Problem**: `START_STICKY` restarts service but state is lost.

```kotlin
return START_STICKY  // Service restarted, but mCalls and callMapping are empty
```

**Impact**: Call tracking lost on service restart.

**Recommended Fix**: Persist state or re-sync with `TelecomManager` on restart.

---

## Testing Recommendations

### Unit Tests

1. **State Mapping Tests**
   - Test all Android Call.State → TeleCall state mappings
   - Test unknown state handling

2. **Call Mapping Tests**
   - Test add/remove from callMapping
   - Test lookup by ID

3. **Audio Control Tests**
   - Test mute/unmute
   - Test speaker/earpiece switching

### Integration Tests

1. **InCallService Tests**
   - Test onCallAdded callback handling
   - Test onCallRemoved callback handling
   - Test Call.Callback registration

2. **Multi-Call Tests**
   - Test handling multiple simultaneous calls
   - Test call mapping correctness

---

*Generated by /legacy reverse engineering*
