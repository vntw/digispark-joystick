Import("env")

from pathlib import Path
import re

# -----------------------
# CONFIG
# -----------------------
USB_CONFIG_PATH = "lib/DigisparkJoystick/usbconfig.h"

VENDOR_STR  = env.GetProjectOption("custom_usb_vendor_str")
PRODUCT_STR  = env.GetProjectOption("custom_usb_product_str")
SERIAL_STR  = env.GetProjectOption("custom_usb_serial_str")

# Optional, set to None to leave unchanged
USB_VENDOR_ID_RHS = "0xc0, 0x16"  # e.g. "0xc0, 0x16"  (VID = 0x16C0)
USB_DEVICE_ID_RHS = "0xdc, 0x27"  # e.g. "0xdc, 0x27"  (PID = 0x27DC)
USB_DEVICE_VERSION_RHS = None     # e.g. "0x02, 0x01"  (bcdDevice = 0x0102)

# -----------------------
# Implementation
# -----------------------
def to_usb_charlist(s: str) -> str:
    # ASCII recommended (avoid umlauts/emoji)
    s = s.replace("\n", " ").replace("\r", " ")
    parts = []
    for ch in s:
        if ch == "'":
            parts.append("'\\''")   # single quote character
        else:
            parts.append("'" + ch + "'")
    return ",".join(parts)

def replace_define_line(text: str, name: str, rhs: str) -> tuple[str, int]:
    pat = re.compile(rf"^(?P<prefix>\s*#define\s+{re.escape(name)}\s+).*$", re.MULTILINE)
    return pat.subn(rf"\g<prefix>{rhs}", text)

def replace_define_len(text: str, name: str, length: int) -> tuple[str, int]:
    pat = re.compile(rf"^(?P<prefix>\s*#define\s+{re.escape(name)}\s+)\d+(\s*)$", re.MULTILINE)
    return pat.subn(rf"\g<prefix>{length}", text)

def must_patch_once(name: str, count: int) -> None:
    if count != 1:
        raise RuntimeError(f"Expected to patch exactly 1 line for {name}, but patched {count}")

project_dir = Path(env.subst("$PROJECT_DIR"))
usbconfig = project_dir / USB_CONFIG_PATH

if not usbconfig.exists():
    raise FileNotFoundError(f"usbconfig.h not found: {usbconfig}")

original = usbconfig.read_text(encoding="utf-8", errors="ignore")
text = original

if (VENDOR_STR is None or not isinstance(VENDOR_STR, str) or not VENDOR_STR.strip() or
    PRODUCT_STR is None or not isinstance(PRODUCT_STR, str) or not PRODUCT_STR.strip() or
    SERIAL_STR is None or not isinstance(SERIAL_STR, str) or not SERIAL_STR.strip()):
    raise RuntimeError("Invalid config values")

print(f"[pre] Setting custom config values: VENDOR_STR: {VENDOR_STR} PRODUCT_STR: {PRODUCT_STR} SERIAL_STR: {SERIAL_STR}")

VENDOR_STR  = VENDOR_STR.strip()
PRODUCT_STR = PRODUCT_STR.strip()
SERIAL_STR  = SERIAL_STR.strip()

text, n = replace_define_line(text, "USB_CFG_VENDOR_NAME", to_usb_charlist(VENDOR_STR))
must_patch_once("USB_CFG_VENDOR_NAME", n)
text, n = replace_define_len(text, "USB_CFG_VENDOR_NAME_LEN", len(VENDOR_STR))
must_patch_once("USB_CFG_VENDOR_NAME_LEN", n)

text, n = replace_define_line(text, "USB_CFG_DEVICE_NAME", to_usb_charlist(PRODUCT_STR))
must_patch_once("USB_CFG_DEVICE_NAME", n)
text, n = replace_define_len(text, "USB_CFG_DEVICE_NAME_LEN", len(PRODUCT_STR))
must_patch_once("USB_CFG_DEVICE_NAME_LEN", n)

text, n = replace_define_line(text, "USB_CFG_SERIAL_NUMBER", to_usb_charlist(SERIAL_STR))
must_patch_once("USB_CFG_SERIAL_NUMBER", n)
text, n = replace_define_len(text, "USB_CFG_SERIAL_NUMBER_LEN", len(SERIAL_STR))
must_patch_once("USB_CFG_SERIAL_NUMBER_LEN", n)

if USB_VENDOR_ID_RHS is not None:
    text, n = replace_define_line(text, "USB_CFG_VENDOR_ID", USB_VENDOR_ID_RHS)
    must_patch_once("USB_CFG_VENDOR_ID", n)

if USB_DEVICE_ID_RHS is not None:
    text, n = replace_define_line(text, "USB_CFG_DEVICE_ID", USB_DEVICE_ID_RHS)
    must_patch_once("USB_CFG_DEVICE_ID", n)

if USB_DEVICE_VERSION_RHS is not None:
    text, n = replace_define_line(text, "USB_CFG_DEVICE_VERSION", USB_DEVICE_VERSION_RHS)
    must_patch_once("USB_CFG_DEVICE_VERSION", n)

if text != original:
    usbconfig.write_text(text, encoding="utf-8")
    print(f"[pre] Patched USB config: {usbconfig}")
else:
    print(f"[pre] No changes needed: {usbconfig}")
