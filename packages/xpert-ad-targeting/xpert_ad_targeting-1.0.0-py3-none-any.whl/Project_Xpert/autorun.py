import os
import sys
import win32com.client  # pip install pywin32

def add_to_startup():
    if getattr(sys, 'frozen', False):  # Only do this when running as a .exe
        exe_path = sys.executable
    else:
        return  # Not in .exe form, skip

    startup_dir = os.path.join(
        os.environ['APPDATA'],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut_path = os.path.join(startup_dir, "XPERT_POS.lnk")

    if not os.path.exists(shortcut_path):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.IconLocation = exe_path
            shortcut.save()
            print("✅ Shortcut added to Startup.")
        except Exception as e:
            print(f"❌ Could not create Startup shortcut: {e}")
    else:
        print("ℹ️ Shortcut already exists in Startup.")
