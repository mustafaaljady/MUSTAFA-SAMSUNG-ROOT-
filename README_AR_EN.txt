MUSTAFA ALJADY — Samsung Auto Root Tool (Windows build kit)

IMPORTANT
This is a Windows-buildable starter application, not a compiled EXE. The current app:
- Detects an authorized ADB device and reads public getprop values.
- Displays bootloader-related status properties.
- Selects and inspects a local ZIP firmware archive for an AP package name.
- Provides safe Magisk preparation and bootloader checklists.

It DOES NOT unlock a bootloaders, bypass KG/Knox/carrier locks, patch firmware itself, or flash automatically.
A Samsung AP file must match the exact model and firmware build. A matching security binary alone is not sufficient.

BUILD ON WINDOWS 10/11 (64-bit)
1. Install Python 3.11+ from python.org and enable "Add Python to PATH".
2. Extract this folder.
3. Double-click build_windows.bat.
4. The EXE will be created at dist\MUSTAFA_ALJADY_Samsung_Tool.exe.

ADB
Install Android SDK Platform-Tools and either add adb.exe to PATH or copy adb.exe beside the Python script.
On the phone, enable USB debugging and authorize the PC.

NOTES
- Rooting/unlocking may erase data and permanently affect Knox warranty status.
- Availability of bootloader unlocking depends on exact Samsung model, carrier and region.
- Always back up data and use exact official firmware.
