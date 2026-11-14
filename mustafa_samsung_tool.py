import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess, shutil, re, threading, os, zipfile
from pathlib import Path

APP_TITLE = "MUSTAFA ALJADY | Samsung Auto Root Tool"
ADB_CANDIDATES = ["adb.exe", "platform-tools/adb.exe", "tools/adb.exe"]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("940x680")
        self.minsize(820, 600)
        self.configure(bg="#101827")
        self.adb = self.find_adb()
        self.firmware = tk.StringVar()
        self.status = tk.StringVar(value="Ready — connect a Samsung phone with USB debugging enabled.")
        self._style()
        self._build()

    def _style(self):
        s = ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("TFrame", background="#101827")
        s.configure("TLabel", background="#101827", foreground="#e5eefc", font=("Segoe UI", 10))
        s.configure("Title.TLabel", font=("Segoe UI", 19, "bold"), foreground="#55c7ff")
        s.configure("Sub.TLabel", foreground="#9fb4cc")
        s.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        s.configure("Accent.TButton", background="#087eae", foreground="white")
        s.map("Accent.TButton", background=[("active", "#0b9bd4")])
        s.configure("Treeview", background="#172337", foreground="#e5eefc", fieldbackground="#172337", rowheight=26)
        s.configure("Treeview.Heading", background="#20334d", foreground="white", font=("Segoe UI", 9, "bold"))

    def _build(self):
        root = ttk.Frame(self, padding=18); root.pack(fill="both", expand=True)
        ttk.Label(root, text="MUSTAFA ALJADY", style="Title.TLabel").pack(anchor="w")
        ttk.Label(root, text="SAMSUNG AUTO ROOT TOOL • PROFESSIONAL", style="Sub.TLabel").pack(anchor="w", pady=(0,14))

        bar = ttk.Frame(root); bar.pack(fill="x", pady=5)
        ttk.Button(bar, text="Detect device / فحص الهاتف", style="Accent.TButton", command=self.detect).pack(side="left")
        ttk.Button(bar, text="Choose firmware ZIP / اختيار الفيرموير", command=self.choose_firmware).pack(side="left", padx=8)
        ttk.Button(bar, text="Open output folder", command=self.open_output).pack(side="left")

        self.device_tree = ttk.Treeview(root, columns=("value",), show="tree headings", height=10)
        self.device_tree.heading("#0", text="Device information")
        self.device_tree.heading("value", text="Value")
        self.device_tree.column("#0", width=260); self.device_tree.column("value", width=570)
        self.device_tree.pack(fill="x", pady=12)

        fw = ttk.Frame(root); fw.pack(fill="x", pady=3)
        ttk.Label(fw, text="Firmware:").pack(side="left")
        ttk.Entry(fw, textvariable=self.firmware, state="readonly").pack(side="left", fill="x", expand=True, padx=8)

        actions = ttk.Frame(root); actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Analyze firmware", command=self.analyze_firmware).pack(side="left")
        ttk.Button(actions, text="Magisk root preparation guide", command=self.magisk_guide).pack(side="left", padx=8)
        ttk.Button(actions, text="Bootloader safety checklist", command=self.boot_guide).pack(side="left")

        ttk.Label(root, text="Activity log").pack(anchor="w", pady=(8,3))
        self.logbox = tk.Text(root, height=12, bg="#08111f", fg="#d5e7fa", insertbackground="white",
                              relief="flat", font=("Consolas", 9), wrap="word")
        self.logbox.pack(fill="both", expand=True)
        ttk.Label(root, textvariable=self.status, style="Sub.TLabel").pack(anchor="w", pady=(8,0))
        self.log("Tool started. This build performs device/firmware checks only; it does not bypass locks or flash automatically.")

    def log(self, msg):
        self.logbox.insert("end", msg + "\n"); self.logbox.see("end")

    def find_adb(self):
        for p in ADB_CANDIDATES:
            if Path(p).is_file(): return str(Path(p).resolve())
        return shutil.which("adb")

    def run_adb(self, args, timeout=15):
        if not self.adb:
            raise RuntimeError("ADB not found. Install Android SDK Platform-Tools or place adb.exe beside this app.")
        p = subprocess.run([self.adb] + args, capture_output=True, text=True, timeout=timeout,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if p.returncode != 0 and p.stderr.strip():
            raise RuntimeError(p.stderr.strip())
        return p.stdout.strip()

    def detect(self):
        self.status.set("Checking ADB connection…")
        self.log("Checking ADB connection…")
        threading.Thread(target=self._detect_worker, daemon=True).start()

    def _detect_worker(self):
        try:
            out = self.run_adb(["devices"])
            devices = [x.split()[0] for x in out.splitlines()[1:] if x.strip() and x.split()[-1] == "device"]
            if not devices:
                self.after(0, lambda: self._show_error("No authorized ADB device found. Enable USB debugging and accept the RSA prompt."))
                return
            serial = devices[0]
            props = {}
            keys = {
                "Model": "ro.product.model", "Device": "ro.product.device",
                "Android": "ro.build.version.release", "Build": "ro.build.display.id",
                "AP / build fingerprint": "ro.build.fingerprint",
                "Bootloader locked": "ro.boot.flash.locked",
                "VBMeta device state": "ro.boot.vbmeta.device_state",
                "Verified Boot": "ro.boot.verifiedbootstate",
                "OEM unlock (reported property)": "ro.oem_unlock_supported",
                "Security patch": "ro.build.version.security_patch",
            }
            for label, key in keys.items():
                try: props[label] = self.run_adb(["-s", serial, "shell", "getprop", key])
                except Exception: props[label] = "Unavailable"
            self.after(0, lambda: self._show_device(serial, props))
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))

    def _show_error(self, msg):
        self.status.set("Device check needs attention.")
        self.log("ERROR: " + msg)
        messagebox.showwarning("Device check", msg)

    def _show_device(self, serial, props):
        for item in self.device_tree.get_children(): self.device_tree.delete(item)
        self.device_tree.insert("", "end", text="ADB serial", values=(serial,))
        for k, v in props.items(): self.device_tree.insert("", "end", text=k, values=(v or "(empty)",))
        self.status.set("Device information read successfully.")
        self.log("Device detected: " + serial)
        locked = props.get("Bootloader locked", "")
        state = props.get("VBMeta device state", "")
        if locked == "1" or state.lower() == "locked":
            self.log("NOTICE: Bootloader reports LOCKED. Root flashing is not available until the manufacturer-supported unlock process is completed.")
        else:
            self.log("Bootloader properties do not report a locked state. Confirm on-device Download Mode before any service operation.")

    def choose_firmware(self):
        f = filedialog.askopenfilename(title="Select Samsung firmware archive", filetypes=[("Firmware archives", "*.zip *.7z *.tar *.md5"), ("All files", "*.*")])
        if f:
            self.firmware.set(f); self.log("Selected firmware: " + f)

    def analyze_firmware(self):
        f = self.firmware.get()
        if not f: messagebox.showinfo("Firmware", "Select a firmware archive first."); return
        p = Path(f)
        self.log("Firmware file: " + p.name)
        self.log("Size: %.2f GB" % (p.stat().st_size / (1024**3)))
        if zipfile.is_zipfile(p):
            try:
                with zipfile.ZipFile(p) as z:
                    names = z.namelist()
                candidates = [n for n in names if re.search(r'(^|/)AP_.*\.(tar\.md5|tar)$', n, re.I)]
                self.log("Archive entries: %d" % len(names))
                self.log("AP package: " + (candidates[0] if candidates else "Not detected — verify archive manually"))
                self.log("This tool does not modify firmware or patch images. Use the official Magisk app on the phone to patch the matching AP package.")
            except Exception as e: self.log("Archive analysis error: " + str(e))
        else:
            self.log("Not a ZIP archive readable by the built-in analyzer. No files were changed.")

    def magisk_guide(self):
        messagebox.showinfo("Magisk preparation", 
            "1) Confirm the exact model and complete build number.\n"
            "2) Obtain the exact matching, official firmware for this device/region.\n"
            "3) Extract AP_*.tar.md5 and copy it to the phone.\n"
            "4) In the official Magisk app, choose Install > Select and Patch a File, then select AP.\n"
            "5) Copy the generated magisk_patched*.tar back to the PC.\n"
            "6) Before any Odin operation, verify model/build and understand data-wipe and warranty implications.\n\n"
            "Do not use a patched AP from another model, binary, or firmware build.")

    def boot_guide(self):
        messagebox.showinfo("Bootloader checklist",
            "This tool only reads boot properties. It cannot unlock a bootloader or bypass KG/Knox/carrier restrictions.\n\n"
            "• Check the OEM unlocking option in Developer options.\n"
            "• Confirm the Download Mode screen offers Device unlock mode.\n"
            "• Follow Samsung's supported on-device unlock flow only if available for this exact model/region.\n"
            "• Unlocking commonly wipes user data and may permanently trip Knox Warranty Bit.\n"
            "• If unlock is unavailable, stop; do not attempt exploit or protection-bypass procedures.")

    def open_output(self):
        path = Path.cwd() / "output"
        path.mkdir(exist_ok=True)
        os.startfile(str(path))

if __name__ == "__main__":
    App().mainloop()
