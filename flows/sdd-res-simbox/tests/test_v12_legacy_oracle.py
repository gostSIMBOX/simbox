import hashlib
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEGACY = ROOT / "legacy/asterisk-chan-svistok-v2014"

EXPECTED_SHA256 = {
    "reader/adapter.c": "c6a9411c94ef5ed325704324a28198d42bdd269d6812891c233d5655f5b75a4d",
    "reader/emulator.c": "0bfb6ac397e7723fa1c741d9dff291411ac8ff6ddab39f33470beea9ae641ffd",
    "reader/reader_core.c": "30a3bb9c57db6a44df9df8f0d481dc56aa1076693e405d41f8549fc3e70e692c",
    "reader/reader_core.h": "e74530866b7aa39de5800cb4c140f1f359c00f860329165801b6ae5cb6cd0efd",
    "hub-ctrl.c": "92df4eeb30a529d1af9ef1acf90346533f3f22c921566a359e33a0346706a04a",
}


def compile_and_run(source: str, args=(), extra_files=None, use_lock_dir=False):
    extra_files = extra_files or {}
    with tempfile.TemporaryDirectory(prefix="res-simbox-v12-") as directory:
        work = Path(directory)
        (work / "harness.c").write_text(source)
        for name, content in extra_files.items():
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content)
        binary = work / "harness"
        compile_result = subprocess.run(
            ["cc", "-std=gnu99", "-Wno-return-type", "-I", str(work),
             str(work / "harness.c"), "-o", str(binary)],
            text=True, capture_output=True,
        )
        if compile_result.returncode:
            raise AssertionError(compile_result.stderr)
        environment = os.environ.copy()
        if use_lock_dir:
            environment["RES_SIMBOX_LOCK_DIR"] = str(work)
        return subprocess.run(
            [str(binary), *args], text=True, capture_output=True, env=environment
        )


def reader_harness(relative_source: str, fakes: str) -> str:
    source = (LEGACY / relative_source).read_text()
    source = source.replace('#include "reader_core.c"', textwrap.dedent("""
        #include <stdio.h>
        #include <string.h>
        int sim_init(char *dev);
        int emu_init(char *dev);
        void hex2buf(const char *hex, char *buf, int *len);
        void printf_buf(unsigned char *buf, int len);
        size_t writetty_all(int fd, const char *buf, size_t len);
        int readtty_all(int fd, char *buf, int maxsize, int *len);
        void closetty_spec(const char *dev, int fd);
        unsigned int sleep(unsigned int seconds);
    """))
    source = source.replace("void main()", "int legacy_entry(void)")
    return source + "\n" + fakes + "\nint main(void) { legacy_entry(); return 0; }\n"


READER_FAKES = r"""
int sim_init(char *dev) { printf("SIM_INIT:%s\n", dev); return 7; }
int emu_init(char *dev) { printf("EMU_INIT:%s\n", dev); return 8; }
void hex2buf(const char *hex, char *buf, int *len) {
    int i; *len = (int)strlen(hex) / 2;
    for (i = 0; i < *len; ++i) sscanf(hex + i * 2, "%2hhx", &buf[i]);
}
void printf_buf(unsigned char *buf, int len) { (void)buf; (void)len; }
size_t writetty_all(int fd, const char *buf, size_t len) {
    size_t i; printf("WRITE:%d:", fd);
    for (i = 0; i < len; ++i) printf("%02X", (unsigned char)buf[i]);
    printf("\n"); return len;
}
int readtty_all(int fd, char *buf, int maxsize, int *len) {
    (void)fd; (void)maxsize; buf[0] = (char)0x90; buf[1] = 0; *len = 2;
    return 0;
}
void closetty_spec(const char *dev, int fd) { printf("CLOSE:%s:%d\n", dev, fd); }
unsigned int sleep(unsigned int seconds) { (void)seconds; return 0; }
"""


USB_H = r"""
#ifndef FAKE_USB_H
#define FAKE_USB_H
#define USB_TYPE_CLASS 0x20
#define USB_RECIP_DEVICE 0x00
#define USB_RECIP_OTHER 0x03
#define USB_ENDPOINT_IN 0x80
#define USB_REQ_GET_STATUS 0
#define USB_REQ_CLEAR_FEATURE 1
#define USB_REQ_SET_FEATURE 3
#define USB_REQ_GET_DESCRIPTOR 6
#define USB_DT_HUB 0x29
#define USB_CLASS_HUB 9
struct usb_device_descriptor { int bDeviceClass; };
struct usb_bus;
struct usb_device {
    struct usb_device *next;
    struct usb_bus *bus;
    int devnum;
    struct usb_device_descriptor descriptor;
};
struct usb_bus { struct usb_bus *next; struct usb_device *devices; char dirname[8]; };
typedef struct usb_dev_handle { int marker; } usb_dev_handle;
void usb_init(void);
int usb_find_busses(void);
int usb_find_devices(void);
struct usb_bus *usb_get_busses(void);
usb_dev_handle *usb_open(struct usb_device *dev);
int usb_close(usb_dev_handle *handle);
int usb_control_msg(usb_dev_handle *, int, int, int, int, char *, int, int);
#endif
"""

USB_FAKE = r"""
static struct usb_dev_handle fake_handle;
static struct usb_device fake_device;
static struct usb_bus fake_bus;
void usb_init(void) {
    memset(&fake_device, 0, sizeof(fake_device));
    memset(&fake_bus, 0, sizeof(fake_bus));
    strcpy(fake_bus.dirname, "001");
    fake_bus.devices = &fake_device;
    fake_device.bus = &fake_bus;
    fake_device.devnum = 2;
    fake_device.descriptor.bDeviceClass = USB_CLASS_HUB;
}
int usb_find_busses(void) { return 1; }
int usb_find_devices(void) { return 1; }
struct usb_bus *usb_get_busses(void) { return &fake_bus; }
usb_dev_handle *usb_open(struct usb_device *dev) { (void)dev; return &fake_handle; }
int usb_close(usb_dev_handle *handle) { (void)handle; return 0; }
int usb_control_msg(usb_dev_handle *handle, int rt, int request, int feature,
                    int index, char *buf, int size, int timeout) {
    (void)handle; (void)rt; (void)timeout;
    if (request == USB_REQ_GET_DESCRIPTOR) {
        memset(buf, 0, (size_t)size);
        buf[0] = 9; buf[2] = 4; buf[3] = (char)0x80;
        return 9;
    }
    if (request == USB_REQ_GET_STATUS) {
        memset(buf, 0, (size_t)size); return size;
    }
    printf("CONTROL:%d:%d:%d\n", request, feature, index);
    return 0;
}
"""

ASTERISK_STUBS = {
    "asterisk.h": r"""
        #ifndef ASTERISK_H
        #define ASTERISK_H
        #include <stddef.h>
        #define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))
        #define ASTERISK_GPL_KEY "GPL"
        #endif
    """,
    "asterisk/lock.h": r"""
        #ifndef ASTERISK_LOCK_H
        #define ASTERISK_LOCK_H
        #include <pthread.h>
        typedef pthread_mutex_t ast_mutex_t;
        #define AST_MUTEX_DEFINE_STATIC(name) static ast_mutex_t name = PTHREAD_MUTEX_INITIALIZER
        #define ast_mutex_lock pthread_mutex_lock
        #define ast_mutex_unlock pthread_mutex_unlock
        #endif
    """,
    "asterisk/logger.h": "#ifndef ASTERISK_LOGGER_H\n#define ASTERISK_LOGGER_H\n#endif\n",
    "asterisk/module.h": r"""
        #ifndef ASTERISK_MODULE_H
        #define ASTERISK_MODULE_H
        struct ast_module { int refs; };
        struct ast_module_info { struct ast_module *self; };
        static struct ast_module stub_module;
        static struct ast_module_info stub_module_info = { &stub_module };
        static struct ast_module_info *ast_module_info = &stub_module_info;
        static inline struct ast_module *ast_module_ref(struct ast_module *m) { ++m->refs; return m; }
        static inline void ast_module_unref(struct ast_module *m) { --m->refs; }
        #define AST_MODULE_LOAD_SUCCESS 0
        #define AST_MODULE_LOAD_DECLINE -1
        #define AST_MODFLAG_GLOBAL_SYMBOLS 1
        #define AST_MODULE_INFO(...) /* registration is runtime-tested on Linux */
        #endif
    """,
    "asterisk/cli.h": r"""
        #ifndef ASTERISK_CLI_H
        #define ASTERISK_CLI_H
        struct ast_cli_entry { const char *command; const char *usage; };
        struct ast_cli_args { int fd; int argc; char **argv; };
        #define CLI_INIT 1
        #define CLI_GENERATE 2
        #define CLI_SUCCESS ((char *)0)
        #define CLI_FAILURE ((char *)1)
        #define CLI_SHOWUSAGE ((char *)2)
        #define AST_CLI_DEFINE(function, description) { 0, 0 }
        static inline int ast_cli_register_multiple(struct ast_cli_entry *e, int n) { (void)e; (void)n; return 0; }
        static inline void ast_cli_unregister_multiple(struct ast_cli_entry *e, int n) { (void)e; (void)n; }
        #endif
    """,
    "asterisk/optional_api.h": r"""
        #ifndef ASTERISK_OPTIONAL_API_H
        #define ASTERISK_OPTIONAL_API_H
        #define AST_OPTIONAL_API_UNAVAILABLE (-2147483647 - 1)
        #ifdef AST_API_MODULE
        #define AST_OPTIONAL_API(result, name, proto, stub) result name proto;
        #else
        #define AST_OPTIONAL_API(result, name, proto, stub) static result name proto stub
        #endif
        #define AST_OPTIONAL_API_NAME(name) name
        #endif
    """,
}


class LegacyOracleTests(unittest.TestCase):
    def test_legacy_hashes_are_immutable(self):
        for relative, expected in EXPECTED_SHA256.items():
            digest = hashlib.sha256((LEGACY / relative).read_bytes()).hexdigest()
            self.assertEqual(expected, digest, relative)

    def test_reader_adapter_apdu_sequence(self):
        result = compile_and_run(reader_harness("reader/adapter.c", READER_FAKES))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("SIM_INIT:/dev/ttyUSB24", result.stdout)
        writes = [line for line in result.stdout.splitlines() if line.startswith("WRITE:")]
        self.assertEqual([
            "WRITE:7:A0A4000002", "WRITE:7:7F4D", "WRITE:7:A0A4000002",
            "WRITE:7:8F0D", "WRITE:7:A0B20104B001",
        ], writes)
        self.assertIn("CLOSE:/dev/ttyUSB24:7", result.stdout)

    def test_reader_emulator_preserves_immediate_return(self):
        result = compile_and_run(reader_harness("reader/emulator.c", READER_FAKES))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("EMU_INIT:/dev/ttyUSB25", result.stdout)
        self.assertNotIn("CLOSE:", result.stdout)

    def test_hub_power_and_led_translation(self):
        source = "#include <stdlib.h>\n" + (LEGACY / "hub-ctrl.c").read_text() + "\n" + USB_FAKE
        power = compile_and_run(source, ("-h", "0", "-P", "3", "-p", "1"), {"usb.h": USB_H})
        self.assertEqual(0, power.returncode, power.stderr)
        self.assertIn("CONTROL:3:8:3", power.stdout)
        led = compile_and_run(source, ("-h", "0", "-P", "2", "-l", "2"), {"usb.h": USB_H})
        self.assertEqual(0, led.returncode, led.stderr)
        self.assertIn("CONTROL:3:22:514", led.stdout)

    def test_hub_listing_and_invalid_arguments(self):
        source = "#include <stdlib.h>\n" + (LEGACY / "hub-ctrl.c").read_text() + "\n" + USB_FAKE
        listing = compile_and_run(source, (), {"usb.h": USB_H})
        self.assertEqual(0, listing.returncode, listing.stderr)
        self.assertIn("Hub #0 at 001:002", listing.stdout)
        invalid = compile_and_run(source, ("-b", "1"), {"usb.h": USB_H})
        self.assertEqual(1, invalid.returncode)
        self.assertIn("Usage:", invalid.stderr)


class ExtractedImplementationTests(unittest.TestCase):
    def test_reader_shared_adapter_matches_legacy_sequence(self):
        reader = ROOT / "libsCpp/asterisk-res-simbox-reader/src"
        source = "#include <stdio.h>\n#include <string.h>\n" + READER_FAKES + textwrap.dedent(f"""
            #include "{reader / 'reader_lock.c'}"
            #include "{reader / 'reader_adapter.c'}"
            int main(void) {{ return res_simbox_reader_run_adapter(NULL); }}
        """)
        result = compile_and_run(source, use_lock_dir=True)
        self.assertEqual(0, result.returncode, result.stderr)
        writes = [line for line in result.stdout.splitlines() if line.startswith("WRITE:")]
        self.assertEqual([
            "WRITE:7:A0A4000002", "WRITE:7:7F4D", "WRITE:7:A0A4000002",
            "WRITE:7:8F0D", "WRITE:7:A0B20104B001",
        ], writes)
        self.assertIn("CLOSE:/dev/ttyUSB24:7", result.stdout)

    def test_reader_shared_emulator_matches_legacy_return(self):
        reader = ROOT / "libsCpp/asterisk-res-simbox-reader/src"
        source = "#include <stdio.h>\n#include <string.h>\n" + READER_FAKES + textwrap.dedent(f"""
            #include "{reader / 'reader_lock.c'}"
            #include "{reader / 'reader_emulator.c'}"
            int main(void) {{ return res_simbox_reader_run_emulator(NULL); }}
        """)
        result = compile_and_run(source, use_lock_dir=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("EMU_INIT:/dev/ttyUSB25", result.stdout)
        self.assertNotIn("CLOSE:", result.stdout)

    def test_hub_shared_implementation_matches_legacy_translation(self):
        hub = ROOT / "libsCpp/asterisk-res-simbox-hub/src"
        source = "#include <stdlib.h>\n" + textwrap.dedent(f"""
            #include "{hub / 'hub_lock.c'}"
            #include "{hub / 'hub-ctrl.c'}"
            #include "{hub / 'hub_service.c'}"
            #include "{hub / 'hub_main.c'}"
        """) + USB_FAKE
        power = compile_and_run(
            source, ("-h", "0", "-P", "3", "-p", "1"),
            {"usb.h": USB_H}, use_lock_dir=True,
        )
        self.assertEqual(0, power.returncode, power.stderr)
        self.assertIn("CONTROL:3:8:3", power.stdout)
        led = compile_and_run(
            source, ("-h", "0", "-P", "2", "-l", "2"),
            {"usb.h": USB_H}, use_lock_dir=True,
        )
        self.assertEqual(0, led.returncode, led.stderr)
        self.assertIn("CONTROL:3:22:514", led.stdout)

    def test_operational_sources_have_no_process_exit(self):
        hub = (ROOT / "libsCpp/asterisk-res-simbox-hub/src/hub-ctrl.c").read_text()
        self.assertNotIn("exit (", hub)
        reader_cli = (ROOT / "libsCpp/asterisk-res-simbox-reader/src/reader_module.c").read_text()
        self.assertNotIn('char* apdu', reader_cli)
        self.assertNotIn('char *apdu', reader_cli)

    def test_core_registry_lifecycle_and_dispatch(self):
        core = ROOT / "libsCpp/asterisk-res-simbox-core"
        source = textwrap.dedent(f"""
            #include <assert.h>
            #include <errno.h>
            #include "{core / 'src/component_registry.c'}"

            static int detached_count;
            static int status(void *context) {{ return *(int *)context; }}
            static int execute(void *context,
                const struct res_simbox_component_request *request) {{
                return *(int *)context + request->value;
            }}
            static void detached(void *context) {{
                (void)context; ++detached_count;
            }}

            int main(void) {{
                int base = 7;
                struct ast_module owner = {{ 0 }};
                struct ast_module other_owner = {{ 0 }};
                struct res_simbox_component component = {{
                    RES_SIMBOX_COMPONENT_ABI, RES_SIMBOX_COMPONENT_READER,
                    "reader", &owner, &base, status, execute, detached
                }};
                struct res_simbox_component duplicate = component;
                struct res_simbox_component_request request = {{
                    RES_SIMBOX_READER_ADAPTER, 0, 0, 0, 5
                }};
                duplicate.owner = &other_owner;
                assert(res_simbox_component_registry_init() == 0);
                assert(res_simbox_component_registry_register(&component) == 0);
                assert(res_simbox_component_registry_register(&component) == 0);
                assert(res_simbox_component_registry_register(&duplicate) == -EEXIST);
                assert(res_simbox_component_registry_status(RES_SIMBOX_COMPONENT_READER) == 7);
                assert(res_simbox_component_registry_execute(RES_SIMBOX_COMPONENT_READER, &request) == 12);
                assert(owner.refs == 0);
                res_simbox_component_registry_fini();
                assert(detached_count == 1);
                assert(res_simbox_component_registry_status(RES_SIMBOX_COMPONENT_READER) == -ENODEV);
                return 0;
            }}
        """)
        files = dict(ASTERISK_STUBS)
        for name in ("res_simbox_component.h", "res_simbox_reader_api.h", "res_simbox_hub_api.h"):
            files[name] = (core / "include" / name).read_text()
        result = compile_and_run(source, extra_files=files)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_asterisk_adapters_compile_against_contract_stubs(self):
        core = ROOT / "libsCpp/asterisk-res-simbox-core"
        reader = ROOT / "libsCpp/asterisk-res-simbox-reader/src"
        hub = ROOT / "libsCpp/asterisk-res-simbox-hub/src"
        with tempfile.TemporaryDirectory(prefix="res-simbox-modules-") as directory:
            work = Path(directory)
            for name, content in ASTERISK_STUBS.items():
                destination = work / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content)
            includes = [
                "-I", str(work), "-I", str(core / "include"),
                "-I", str(reader), "-I", str(hub), "-I", str(core / "src"),
            ]
            sources = [
                reader / "reader_module.c", reader / "reader_provider.c",
                hub / "hub_module.c", hub / "hub_provider.c",
                core / "src/component_registry_api.c",
            ]
            for index, source in enumerate(sources):
                result = subprocess.run(
                    ["cc", "-std=gnu99", "-Werror", *includes, "-c", str(source),
                     "-o", str(work / f"module-{index}.o")],
                    text=True, capture_output=True,
                )
                self.assertEqual(0, result.returncode, f"{source}:\n{result.stderr}")

    def test_modules_never_load_children_or_spawn_binaries(self):
        roots = [
            ROOT / "libsCpp/asterisk-res-simbox-core/src/component_registry.c",
            ROOT / "libsCpp/asterisk-res-simbox-reader/src/reader_module.c",
            ROOT / "libsCpp/asterisk-res-simbox-hub/src/hub_module.c",
        ]
        forbidden = ("ast_load_resource", "ast_unload_resource", "fork(", "exec(", "system(")
        for path in roots:
            source = path.read_text()
            for token in forbidden:
                self.assertNotIn(token, source, f"{token} in {path}")

    def test_reader_device_lock_rejects_second_process(self):
        reader = ROOT / "libsCpp/asterisk-res-simbox-reader/src"
        source = textwrap.dedent(f"""
            #include <stdio.h>
            #include <string.h>
            #include <unistd.h>
            #include "{reader / 'reader_lock.c'}"
            int main(int argc, char **argv) {{
                struct res_simbox_reader_lock lock;
                if (argc != 3) return 9;
                if (res_simbox_reader_lock_acquire(&lock, argv[2]) != 0)
                    return 3;
                puts("LOCKED"); fflush(stdout);
                if (strcmp(argv[1], "hold") == 0) sleep(2);
                res_simbox_reader_lock_release(&lock);
                return 0;
            }}
        """)
        with tempfile.TemporaryDirectory(prefix="res-simbox-lock-") as directory:
            work = Path(directory)
            source_path = work / "lock.c"
            binary = work / "lock"
            source_path.write_text(source)
            compiled = subprocess.run(
                ["cc", "-std=gnu99", str(source_path), "-o", str(binary)],
                text=True, capture_output=True,
            )
            self.assertEqual(0, compiled.returncode, compiled.stderr)
            environment = os.environ.copy()
            environment["RES_SIMBOX_LOCK_DIR"] = str(work)
            holder = subprocess.Popen(
                [str(binary), "hold", "/dev/ttyUSB24"], text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
            )
            self.assertEqual("LOCKED", holder.stdout.readline().strip())
            collision = subprocess.run(
                [str(binary), "try", "/dev/ttyUSB24"], text=True,
                capture_output=True, env=environment,
            )
            independent = subprocess.run(
                [str(binary), "try", "/dev/ttyUSB25"], text=True,
                capture_output=True, env=environment,
            )
            self.assertEqual(3, collision.returncode)
            self.assertEqual(0, independent.returncode, independent.stderr)
            remaining_stdout, holder_stderr = holder.communicate(timeout=5)
            self.assertEqual(0, holder.returncode, holder_stderr + remaining_stdout)

    def test_dual_artifact_build_graphs_share_common_objects(self):
        reader_make = (ROOT / "libsCpp/asterisk-res-simbox-reader/Makefile").read_text()
        hub_make = (ROOT / "libsCpp/asterisk-res-simbox-hub/Makefile").read_text()
        self.assertIn("BIN = res-simbox-reader", reader_make)
        self.assertIn("MODULE = res_simbox_reader.so", reader_make)
        self.assertIn("BIN_OBJS = $(COMMON_OBJS)", reader_make)
        self.assertIn("MODULE_OBJS = $(COMMON_OBJS)", reader_make)
        self.assertIn("BIN = res-simbox-hub", hub_make)
        self.assertIn("MODULE = res_simbox_hub.so", hub_make)
        self.assertIn("COMPAT_BIN = hub-ctrl", hub_make)
        self.assertIn("BIN_OBJS = $(COMMON_OBJS)", hub_make)
        self.assertIn("MODULE_OBJS = $(COMMON_OBJS)", hub_make)

        for path in (
            ROOT / "libsCpp/asterisk-res-simbox-reader/src/reader_main.c",
            ROOT / "libsCpp/asterisk-res-simbox-hub/src/hub_main.c",
        ):
            self.assertNotIn("<asterisk", path.read_text())

    def test_core_lifecycle_owns_registry_not_child_lifecycle(self):
        source = (ROOT / "libsCpp/asterisk-res-simbox-core/src/chan_dongle.c").read_text()
        self.assertIn("res_simbox_component_registry_init();", source)
        self.assertIn("res_simbox_component_registry_fini()", source)
        self.assertIn("AST_MODFLAG_GLOBAL_SYMBOLS", source)
        self.assertNotIn('ast_load_resource("res_simbox_reader', source)
        self.assertNotIn('ast_load_resource("res_simbox_hub', source)

    def test_reader_child_works_independently_then_attaches(self):
        core = ROOT / "libsCpp/asterisk-res-simbox-core/include"
        reader = ROOT / "libsCpp/asterisk-res-simbox-reader/src"
        source = textwrap.dedent(f"""
            #include <assert.h>
            #include "{reader / 'reader_module.c'}"
            static const struct res_simbox_component *captured;
            static int unregistered;
            static int register_component(const struct res_simbox_component *c) {{ captured = c; return 0; }}
            static int unregister_component(const struct res_simbox_component *c) {{
                assert(c == captured); ++unregistered; return 0;
            }}
            int res_simbox_reader_run_adapter(const char *device) {{ (void)device; return 11; }}
            int res_simbox_reader_run_emulator(const char *device) {{ (void)device; return 12; }}
            int main(void) {{
                struct res_simbox_component_request request = {{ RES_SIMBOX_READER_ADAPTER, 0, 0, 0, 0 }};
                assert(load_module() == AST_MODULE_LOAD_SUCCESS);
                assert(res_simbox_reader_attach_core(register_component, unregister_component) == 0);
                assert(captured && captured->execute(0, &request) == 11);
                captured->detached(0);
                assert(res_simbox_reader_attach_core(register_component, unregister_component) == 0);
                assert(unload_module() == 0);
                assert(unregistered == 1);
                return 0;
            }}
        """)
        files = dict(ASTERISK_STUBS)
        for name in ("res_simbox_component.h", "res_simbox_core_api.h"):
            files[name] = (core / name).read_text()
        result = compile_and_run(source, extra_files=files)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_hub_child_works_independently_then_attaches(self):
        core = ROOT / "libsCpp/asterisk-res-simbox-core/include"
        hub = ROOT / "libsCpp/asterisk-res-simbox-hub/src"
        source = textwrap.dedent(f"""
            #include <assert.h>
            #include "{hub / 'hub_module.c'}"
            static const struct res_simbox_component *captured;
            static int register_component(const struct res_simbox_component *c) {{ captured = c; return 0; }}
            static int unregister_component(const struct res_simbox_component *c) {{ return c == captured ? 0 : -1; }}
            int res_simbox_hub_list(void) {{ return 21; }}
            int res_simbox_hub_set_power(int h, int p, int v) {{ return h + p + v; }}
            int res_simbox_hub_set_led(int h, int p, int v) {{ return h + p + v + 1; }}
            int main(void) {{
                struct res_simbox_component_request request = {{ RES_SIMBOX_HUB_POWER, 0, 1, 2, 3 }};
                assert(load_module() == AST_MODULE_LOAD_SUCCESS);
                assert(res_simbox_hub_attach_core(register_component, unregister_component) == 0);
                assert(captured && captured->execute(0, &request) == 6);
                assert(unload_module() == 0);
                return 0;
            }}
        """)
        files = dict(ASTERISK_STUBS)
        for name in ("res_simbox_component.h", "res_simbox_core_api.h"):
            files[name] = (core / name).read_text()
        result = compile_and_run(source, extra_files=files)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
