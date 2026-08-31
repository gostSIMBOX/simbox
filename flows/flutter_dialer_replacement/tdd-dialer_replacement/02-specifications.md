# 02-Specifications

## Test Specifications

This document provides detailed test specifications for each test requirement defined in `01-requirements.md`.

---

## JavaScript Unit Tests

### TEST-JS-001: checkNativeModule - Module Null

**File**: `__tests__/javascript/ReplaceDialer.test.js`

**Test**:
```javascript
describe('ReplaceDialer', () => {
  describe('checkNativeModule', () => {
    it('should throw error when native module is null', () => {
      // Arrange
      NativeModules.ReplaceDialerModule = null;
      const dialer = new ReplaceDialer();
      
      // Act & Assert
      expect(() => dialer.checkNativeModule()).toThrow(
        expect.stringContaining('NativeModule.ReplaceDialerModule is null')
      );
    });

    it('should include troubleshooting steps in error message', () => {
      // Arrange
      NativeModules.ReplaceDialerModule = null;
      const dialer = new ReplaceDialer();
      
      // Act & Assert
      try {
        dialer.checkNativeModule();
        fail('Expected error to be thrown');
      } catch (error) {
        expect(error.message).toContain('Rebuild and re-run the app');
        expect(error.message).toContain('pod install');
        expect(error.message).toContain('manual installation instructions');
        expect(error.message).toContain('mock the native module');
        expect(error.message).toContain('Github repository');
      }
    });

    it('should not throw error when native module is available', () => {
      // Arrange
      NativeModules.ReplaceDialerModule = {
        isDefaultDialer: jest.fn(),
        setDefaultDialer: jest.fn(),
      };
      const dialer = new ReplaceDialer();
      
      // Act & Assert
      expect(() => dialer.checkNativeModule()).not.toThrow();
    });
  });
});
```

**Coverage**: FR-TEST-001

---

### TEST-JS-002: isDefaultDialer - Success Case

**File**: `__tests__/javascript/ReplaceDialer.test.js`

**Test**:
```javascript
describe('isDefaultDialer', () => {
  beforeEach(() => {
    // Mock native module
    NativeModules.ReplaceDialerModule = {
      isDefaultDialer: jest.fn((callback) => callback(true)),
    };
    console.log = jest.fn();
  });

  it('should invoke callback with true when app is default dialer', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.isDefaultDialer(mockCallback);
    
    // Assert
    expect(mockCallback).toHaveBeenCalledTimes(1);
    expect(mockCallback).toHaveBeenCalledWith(true);
  });

  it('should log the result', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.isDefaultDialer(mockCallback);
    
    // Assert
    expect(console.log).toHaveBeenCalledWith('isDefaultDialer()', true);
  });

  it('should call native module method', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.isDefaultDialer(mockCallback);
    
    // Assert
    expect(NativeModules.ReplaceDialerModule.isDefaultDialer)
      .toHaveBeenCalledTimes(1);
  });
});
```

**Coverage**: FR-TEST-002

---

### TEST-JS-003: isDefaultDialer - Failure Case

**File**: `__tests__/javascript/ReplaceDialer.test.js`

**Test**:
```javascript
describe('isDefaultDialer', () => {
  beforeEach(() => {
    NativeModules.ReplaceDialerModule = {
      isDefaultDialer: jest.fn((callback) => callback(false)),
    };
    console.log = jest.fn();
  });

  it('should invoke callback with false when app is not default dialer', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.isDefaultDialer(mockCallback);
    
    // Assert
    expect(mockCallback).toHaveBeenCalledTimes(1);
    expect(mockCallback).toHaveBeenCalledWith(false);
  });

  it('should log false result', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.isDefaultDialer(mockCallback);
    
    // Assert
    expect(console.log).toHaveBeenCalledWith('isDefaultDialer()', false);
  });
});
```

**Coverage**: FR-TEST-003

---

### TEST-JS-004: setDefaultDialer - Callback Invocation

**File**: `__tests__/javascript/ReplaceDialer.test.js`

**Test**:
```javascript
describe('setDefaultDialer', () => {
  beforeEach(() => {
    NativeModules.ReplaceDialerModule = {
      setDefaultDialer: jest.fn((callback) => callback(true)),
    };
    console.log = jest.fn();
  });

  it('should invoke callback after native call', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.setDefaultDialer(mockCallback);
    
    // Assert
    expect(mockCallback).toHaveBeenCalledTimes(1);
  });

  it('should invoke callback with result from native module', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.setDefaultDialer(mockCallback);
    
    // Assert
    expect(mockCallback).toHaveBeenCalledWith(true);
  });

  it('should log the result', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.setDefaultDialer(mockCallback);
    
    // Assert
    expect(console.log).toHaveBeenCalledWith('setDefaultDialer', true);
  });

  it('should call native module method', () => {
    // Arrange
    const dialer = new ReplaceDialer();
    const mockCallback = jest.fn();
    
    // Act
    dialer.setDefaultDialer(mockCallback);
    
    // Assert
    expect(NativeModules.ReplaceDialerModule.setDefaultDialer)
      .toHaveBeenCalledTimes(1);
  });
});
```

**Coverage**: FR-TEST-005 (partial - currently documents broken behavior)

---

### TEST-JS-005: Constructor

**File**: `__tests__/javascript/ReplaceDialer.test.js`

**Test**:
```javascript
describe('ReplaceDialer constructor', () => {
  it('should create instance without errors', () => {
    // Arrange & Act
    const dialer = new ReplaceDialer();
    
    // Assert
    expect(dialer).toBeDefined();
    expect(typeof dialer.isDefaultDialer).toBe('function');
    expect(typeof dialer.setDefaultDialer).toBe('function');
    expect(typeof dialer.checkNativeModule).toBe('function');
  });
});
```

**Coverage**: Basic instantiation

---

## Native Android Unit Tests

### TEST-NATIVE-001: getName() Returns Correct Name

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModuleTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;

import static org.junit.Assert.assertEquals;

@RunWith(RobolectricTestRunner.class)
public class ReplaceDialerModuleTest {

    @Mock
    private ReactApplicationContext mockContext;

    private ReplaceDialerModule module;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        module = new ReplaceDialerModule(mockContext);
    }

    @Test
    public void getName_ShouldReturnReplaceDialerModule() {
        // Act
        String name = module.getName();
        
        // Assert
        assertEquals("ReplaceDialerModule", name);
    }
}
```

**Coverage**: FR-TEST-008

---

### TEST-NATIVE-002: isDefaultDialer - Pre-M Android

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModuleTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import android.os.Build;

import com.facebook.react.bridge.Callback;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.never;

@RunWith(RobolectricTestRunner.class)
public class ReplaceDialerModuleTest {

    @Mock
    private ReactApplicationContext mockContext;

    @Mock
    private Callback mockCallback;

    private ReplaceDialerModule module;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        module = new ReplaceDialerModule(mockContext);
    }

    @Test
    @Config(sdk = Build.VERSION_CODES.LOLLIPOP_MR1) // API 22
    public void isDefaultDialer_PreMApiLevel_ShouldInvokeCallbackWithTrue() {
        // Act
        module.isDefaultDialer(mockCallback);
        
        // Assert
        verify(mockCallback).invoke(true);
        // Verify TelecomManager is NOT called
        verify(mockContext, never()).getSystemService(any());
    }

    @Test
    @Config(sdk = Build.VERSION_CODES.M) // API 23
    public void isDefaultDialer_MApiLevel_ShouldCheckTelecomManager() {
        // Arrange
        // (Separate test for M+ behavior)
    }
}
```

**Coverage**: FR-TEST-004

---

### TEST-NATIVE-003: isDefaultDialer - Is Default Dialer

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModuleTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import android.content.Context;
import android.telecom.TelecomManager;

import com.facebook.react.bridge.Callback;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.annotation.Config;

import static org.mockito.Mockito.*;
import static org.junit.Assert.*;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = Build.VERSION_CODES.M)
public class ReplaceDialerModuleTest {

    @Mock
    private ReactApplicationContext mockContext;

    @Mock
    private TelecomManager mockTelecomManager;

    @Mock
    private Callback mockCallback;

    private ReplaceDialerModule module;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        
        when(mockContext.getSystemService(Context.TELECOM_SERVICE))
            .thenReturn(mockTelecomManager);
        when(mockContext.getPackageName())
            .thenReturn("com.example.dialer");
        
        module = new ReplaceDialerModule(mockContext);
    }

    @Test
    public void isDefaultDialer_AppIsDefault_ShouldInvokeCallbackWithTrue() {
        // Arrange
        when(mockTelecomManager.getDefaultDialerPackage())
            .thenReturn("com.example.dialer");
        
        // Act
        module.isDefaultDialer(mockCallback);
        
        // Assert
        verify(mockCallback).invoke(true);
    }

    @Test
    public void isDefaultDialer_AppIsNotDefault_ShouldInvokeCallbackWithFalse() {
        // Arrange
        when(mockTelecomManager.getDefaultDialerPackage())
            .thenReturn("com.other.dialer");
        
        // Act
        module.isDefaultDialer(mockCallback);
        
        // Assert
        verify(mockCallback).invoke(false);
    }
}
```

**Coverage**: FR-TEST-002, FR-TEST-003

---

### TEST-NATIVE-004: setDefaultDialer - Intent Creation

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModuleTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import android.content.Intent;
import android.telecom.TelecomManager;

import com.facebook.react.bridge.Callback;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.shadows.ShadowActivity;
import org.robolectric.shadows.ShadowIntent;

import static org.mockito.Mockito.*;
import static org.junit.Assert.*;
import static org.robolectric.Shadows.shadowOf;

@RunWith(RobolectricTestRunner.class)
public class ReplaceDialerModuleTest {

    @Mock
    private ReactApplicationContext mockContext;

    @Mock
    private ShadowActivity mockShadowActivity;

    @Mock
    private Callback mockCallback;

    private ReplaceDialerModule module;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        module = new ReplaceDialerModule(mockContext);
    }

    @Test
    public void setDefaultDialer_ShouldCreateCorrectIntent() {
        // Arrange
        ArgumentCaptor<Intent> intentCaptor = ArgumentCaptor.forClass(Intent.class);
        when(mockContext.getPackageName()).thenReturn("com.example.dialer");
        
        // Act
        module.setDefaultDialer(mockCallback);
        
        // Assert
        verify(mockContext).startActivityForResult(
            intentCaptor.capture(),
            eq(ReplaceDialerModule.RC_DEFAULT_PHONE),
            any()
        );
        
        Intent capturedIntent = intentCaptor.getValue();
        assertEquals(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER, 
                     capturedIntent.getAction());
        assertEquals("com.example.dialer", 
                     capturedIntent.getStringExtra(
                         TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME));
    }
}
```

**Coverage**: FR-TEST-007

---

### TEST-NATIVE-005: setDefaultDialer - Callback Invoked Immediately (BUG DOCUMENTATION)

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModuleTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import com.facebook.react.bridge.Callback;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;

import static org.mockito.Mockito.*;

/**
 * This test documents the current (buggy) behavior.
 * After fixing BUG-001, this test should be updated to expect
 * callback NOT to be invoked immediately.
 */
@RunWith(RobolectricTestRunner.class)
public class ReplaceDialerModuleTest {

    @Mock
    private ReactApplicationContext mockContext;

    @Mock
    private Callback mockCallback;

    private ReplaceDialerModule module;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        module = new ReplaceDialerModule(mockContext);
    }

    @Test
    public void setDefaultDialer_CurrentBehavior_CallbackInvokedImmediately() {
        // Arrange
        when(mockContext.getPackageName()).thenReturn("com.example.dialer");
        
        // Act
        module.setDefaultDialer(mockCallback);
        
        // Assert - THIS DOCUMENTS THE BUG
        // Callback is invoked immediately with true, before activity result
        verify(mockCallback).invoke(true);
        
        // NOTE: After fixing BUG-001, this should be:
        // verify(mockCallback, never()).invoke(any());
        // And callback should be invoked in onActivityResult() instead
    }
}
```

**Coverage**: BUG-001-TEST-001 (documents existing bug)

---

### TEST-NATIVE-006: onActivityResult - Success Case (AFTER FIX)

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModuleTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import android.app.Activity;
import android.content.Intent;

import com.facebook.react.bridge.Callback;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;

import static org.mockito.Mockito.*;

/**
 * This test should pass AFTER fixing BUG-001.
 * Currently will fail because onActivityResult is not implemented.
 */
@RunWith(RobolectricTestRunner.class)
public class ReplaceDialerModuleTest {

    @Mock
    private ReactApplicationContext mockContext;

    @Mock
    private Callback mockCallback;

    private ReplaceDialerModule module;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        module = new ReplaceDialerModule(mockContext);
    }

    @Test
    public void onActivityResult_ResultOk_ShouldInvokeCallbackWithTrue() {
        // Arrange - this should be set by setDefaultDialer()
        // After fix: setDefaultDialer stores callback but doesn't invoke it
        module.setDefaultDialer(mockCallback);
        reset(mockCallback); // Reset to verify onActivityResult invocation
        
        // Act
        module.onActivityResult(
            ReplaceDialerModule.RC_DEFAULT_PHONE,
            Activity.RESULT_OK,
            null
        );
        
        // Assert
        verify(mockCallback).invoke(true);
        verify(mockCallback, never()).invoke(false);
    }

    @Test
    public void onActivityResult_ResultCanceled_ShouldInvokeCallbackWithFalse() {
        // Arrange
        module.setDefaultDialer(mockCallback);
        reset(mockCallback);
        
        // Act
        module.onActivityResult(
            ReplaceDialerModule.RC_DEFAULT_PHONE,
            Activity.RESULT_CANCELED,
            null
        );
        
        // Assert
        verify(mockCallback).invoke(false);
        verify(mockCallback, never()).invoke(true);
    }

    @Test
    public void onActivityResult_CallbackClearedAfterInvocation() {
        // Arrange
        module.setDefaultDialer(mockCallback);
        
        // Act
        module.onActivityResult(
            ReplaceDialerModule.RC_DEFAULT_PHONE,
            Activity.RESULT_OK,
            null
        );
        
        // Assert - after fix, callback should be cleared
        // This prevents memory leaks and duplicate invocations
        // Implementation depends on how static field is managed
    }
}
```

**Coverage**: BUG-001-TEST-001, BUG-001-TEST-002, BUG-001-TEST-003

---

### TEST-NATIVE-007: Package Registration

**File**: `android/app/src/test/java/one/telefon/replacedialer/ReplaceDialerModulePackageTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.robolectric.RobolectricTestRunner;

import java.util.List;

import static org.junit.Assert.*;

@RunWith(RobolectricTestRunner.class)
public class ReplaceDialerModulePackageTest {

    @Mock
    private ReactApplicationContext mockContext;

    private ReplaceDialerModulePackage pkg;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        pkg = new ReplaceDialerModulePackage();
    }

    @Test
    public void createNativeModules_ShouldReturnListWithOneModule() {
        // Act
        List<NativeModule> modules = pkg.createNativeModules(mockContext);
        
        // Assert
        assertNotNull(modules);
        assertEquals(1, modules.size());
        assertTrue(modules.get(0) instanceof ReplaceDialerModule);
    }

    @Test
    public void createViewManagers_ShouldReturnEmptyList() {
        // Act
        List viewManagers = pkg.createViewManagers(mockContext);
        
        // Assert
        assertNotNull(viewManagers);
        assertTrue(viewManagers.isEmpty());
    }
}
```

**Coverage**: FR-TEST-009

---

## Integration Tests

### TEST-INT-001: JavaScript-to-Native Bridge

**File**: `android/app/src/androidTest/java/one/telefon/replacedialer/BridgeIntegrationTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import android.content.Context;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.rule.ActivityTestRule;

import com.facebook.react.ReactInstanceManager;
import com.facebook.react.bridge.ReactContext;
import com.facebook.react.bridge.NativeModule;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class BridgeIntegrationTest {

    @Rule
    public ActivityTestRule<TestActivity> activityRule =
        new ActivityTestRule<>(TestActivity.class);

    private ReactContext reactContext;

    @Before
    public void setUp() {
        // Get React context from test activity
        reactContext = activityRule.getActivity().getReactContext();
    }

    @Test
    public void bridge_ModuleRegistered_ShouldBeAccessible() {
        // Act
        NativeModule module = reactContext.getNativeModule("ReplaceDialerModule");
        
        // Assert
        assertNotNull(module);
        assertTrue(module instanceof ReplaceDialerModule);
    }
}
```

**Coverage**: Bridge integration

---

### TEST-INT-002: End-to-End Dialer Status Check

**File**: `android/app/src/androidTest/java/one/telefon/replacedialer/DialerFlowIntegrationTest.java`

**Test**:
```java
package one.telefon.replacedialer;

import android.telecom.TelecomManager;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import com.facebook.react.bridge.Callback;
import com.facebook.react.bridge.ReactApplicationContext;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;

import static org.mockito.Mockito.*;

@RunWith(AndroidJUnit4.class)
public class DialerFlowIntegrationTest {

    private ReactApplicationContext context;

    @Before
    public void setUp() {
        context = new ReactApplicationContext(
            ApplicationProvider.getApplicationContext()
        );
    }

    @Test
    public void fullFlow_IsDefaultDialer_ShouldReturnCorrectStatus() {
        // Arrange
        ReplaceDialerModule module = new ReplaceDialerModule(context);
        MockCallback callback = new MockCallback();
        
        // Act
        module.isDefaultDialer(callback);
        
        // Assert
        assertTrue(callback.wasCalled);
        // Note: Actual result depends on system state
        assertNotNull(callback.result);
    }

    // Helper class for testing
    private static class MockCallback implements Callback {
        boolean wasCalled = false;
        Object result = null;

        @Override
        public void invoke(Object... args) {
            wasCalled = true;
            if (args.length > 0) {
                result = args[0];
            }
        }
    }
}
```

**Coverage**: End-to-end flow

---

## Mock Implementations

### JavaScript Mock

**File**: `__tests__/javascript/__mocks__/NativeModules.js`

```javascript
// Mock for NativeModules.ReplaceDialerModule
export const ReplaceDialerModuleMock = {
  isDefaultDialer: jest.fn((callback) => callback(true)),
  setDefaultDialer: jest.fn((callback) => callback(true)),
};

export default {
  ReplaceDialerModule: ReplaceDialerModuleMock,
};
```

### Native Android Mock

**File**: `android/app/src/test/java/one/telefon/replacedialer/MockCallback.java`

```java
package one.telefon.replacedialer;

import com.facebook.react.bridge.Callback;

public class MockCallback implements Callback {
    private boolean wasCalled = false;
    private Object[] args = null;

    @Override
    public void invoke(Object... args) {
        this.wasCalled = true;
        this.args = args;
    }

    public boolean wasCalled() {
        return wasCalled;
    }

    public Object getResult() {
        return args != null && args.length > 0 ? args[0] : null;
    }

    public void reset() {
        wasCalled = false;
        args = null;
    }
}
```

---

## Test Execution

### JavaScript Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Coverage report location: coverage/
```

### Native Android Tests

```bash
# Run unit tests
./gradlew test

# Run with coverage
./gradlew jacocoTestReport

# Coverage report location:
# android/app/build/reports/jacoco/jacocoTestReport/html/
```

### Integration Tests

```bash
# Run on emulator
./gradlew connectedAndroidTest

# Coverage report location:
# android/app/build/outputs/code_coverage/
```

---

*Generated by /legacy analysis on 2026-03-04*
*Status: DRAFT*
