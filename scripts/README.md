## PlatformIO

```ini
[env]
build_flags =
  -Ilib/DigisparkJoystick

custom_usb_vendor_str = example.com
custom_usb_product_str = Example Product
custom_usb_serial_str  = example.com:example_product

extra_scripts = pre:scripts/pre_patch_usbconfig.py
```
