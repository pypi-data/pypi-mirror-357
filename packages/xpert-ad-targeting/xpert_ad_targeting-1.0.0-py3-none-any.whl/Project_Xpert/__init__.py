"""
XPERT AD-TARGETING PACKAGE

A Python package for automated POS monitoring and OCR processing.
"""

__version__ = "1.0.0"
__author__ = "XPERT Team"
__description__ = "Automated POS monitoring and OCR processing application"

# Import the main application class for easy access
from .main import XpertPOSApp

# Make the main function available at package level
def run():
    """Run the XPERT AD-TARGETING application"""
    from .main import XpertPOSApp
    app = XpertPOSApp()
    app.window.mainloop()

# When the package is run directly, execute the main function
if __name__ == "__main__":
    run() 