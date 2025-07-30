"""
Entry point for running the XPERT AD-TARGETING package directly.
This allows the package to be run with: python -m Project_Xpert
"""

from .main import XpertPOSApp

def main():
    """Main entry point for the application"""
    print("[DEBUG] Starting XpertPOSApp...")
    app = XpertPOSApp()
    print("[DEBUG] App initialized, entering mainloop()...")
    app.window.mainloop()

if __name__ == "__main__":
    main() 