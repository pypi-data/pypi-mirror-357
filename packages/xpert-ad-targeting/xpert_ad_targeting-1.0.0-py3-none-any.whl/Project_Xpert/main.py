import os
import sys
import webbrowser
import logging
from pathlib import Path
from dotenv import load_dotenv
from tkinter import messagebox
from PIL import Image
import customtkinter as ctk
import pygetwindow as gw
import pytesseract
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import boto3
import traceback
from datetime import datetime
import threading
import time
import keyboard  # Add this import at the top if not present
import json

# Local module imports
from .capture import monitor_pos
from .ocr_export import ocr_and_export
from .cleanup import cleanup_jsons
from .autorun import add_to_startup

# ===== LOGGING SETUP =====
def setup_logging():
    """Setup comprehensive logging with timestamp"""
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as executable
        app_dir = Path(sys.executable).parent
        log_dir = app_dir / 'logs'
    else:
        # Running as script
        app_dir = Path(__file__).parent
        log_dir = app_dir / 'logs'
    
    # Create logs directory
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = f"xpert_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = log_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 60)
    logger.info(f"XPERT AD-TARGETING APPLICATION STARTED")
    logger.info(f"Log file: {log_filepath}")
    logger.info(f"Application directory: {app_dir}")
    logger.info(f"=" * 60)
    
    return logger

# Initialize logger 
logger = setup_logging()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # Use getattr to safely check for _MEIPASS attribute
        base_path = getattr(sys, '_MEIPASS', None)  # PyInstaller sets this attr
        if base_path is None:
            base_path = os.path.abspath(".")
    except Exception as e:
        logger.warning(f"Error getting _MEIPASS: {e}")
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_paths():
    if getattr(sys, 'frozen', False):
        # Use getattr to safely check for _MEIPASS attribute
        base_path = getattr(sys, '_MEIPASS', None)
        if base_path is None:
            base_path = os.path.dirname(sys.executable)
    else:
        # When running as script, go up one level to the root directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Use the correct Windows path for Tesseract
    tesseract_path = os.path.join(base_path, "Tesseract-OCR", "tesseract.exe")
    dotenv_path = os.path.join(base_path, ".env")
    
    logger.info(f"Base path: {base_path}")
    logger.info(f"Setting Tesseract path to: {tesseract_path}")
    logger.info(f"Tesseract path exists: {os.path.exists(tesseract_path)}")
    
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    return dotenv_path

def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))

def load_logo_image():
    try:
        logger.info(f"Loading logo from path: {LOGO_PATH}")
        if not os.path.exists(LOGO_PATH):
            logger.warning(f"Logo file not found at: {LOGO_PATH}")
            return None
            
        logo_img = Image.open(LOGO_PATH)
        logo_img = logo_img.resize((200, 120), Image.Resampling.LANCZOS)
        ctk_image = ctk.CTkImage(light_image=logo_img, size=(200, 120))
        logger.info("Logo loaded successfully")
        return ctk_image
    except Exception as e:
        logger.error(f"Error loading logo: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

def check_tesseract_exists():
    try:
        logger.info(f"Checking Tesseract at path: {pytesseract.pytesseract.tesseract_cmd}")
        if not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
            error_msg = f"Tesseract not found at:\n{pytesseract.pytesseract.tesseract_cmd}"
            logger.error(error_msg)
            show_error_dialog("Tesseract Not Found", error_msg)
            sys.exit(1)
        logger.info("Tesseract found successfully")
    except Exception as e:
        logger.error(f"Error checking Tesseract: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        show_error_dialog("Tesseract Error", f"Error checking Tesseract: {e}")
        sys.exit(1)

def show_error_dialog(title, message):
    dialog = ctk.CTkToplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.grid_rowconfigure(0, weight=1)
    dialog.grid_columnconfigure(0, weight=1)

    label = ctk.CTkLabel(dialog, text=message, font=("Segoe UI", 14), wraplength=350)
    label.grid(row=0, column=0, padx=20, pady=20)

    button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, font=("Segoe UI", 14), fg_color="#FF6C00", hover_color="#E55B00")
    button.grid(row=1, column=0, pady=10)

# ===== S3 UPLOAD FUNCTIONALITY =====
class S3Uploader:
    def __init__(self, screenshot_dir, output_dir):
        self.screenshot_dir = screenshot_dir
        self.output_dir = output_dir
        self.s3_client = None
        self.upload_enabled = True
        self.initialize_s3_client()
        
    def initialize_s3_client(self):
        """Initialize and test S3 client connection"""
        logger.info("🔍 Initializing S3 client...")
        
        try:
            # Get AWS credentials from environment or use fallback
            access_key = os.getenv('AWS_ACCESS_KEY')
            secret_key = os.getenv('AWS_SECRET_KEY')
            AWS_REGION = os.getenv('AWS_REGION')
            S3_BUCKET = os.getenv('S3_BUCKET')
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=AWS_REGION
            )
            
            # Test connection by listing buckets
            logger.info("Testing S3 connection...")
            response = self.s3_client.list_buckets()
            logger.info(f"✅ S3 connection successful. Available buckets: {len(response['Buckets'])}")
            
            # Check if target bucket exists
            bucket_exists = any(bucket['Name'] == S3_BUCKET for bucket in response['Buckets'])
            if bucket_exists:
                logger.info(f"✅ Target bucket '{S3_BUCKET}' found")
            else:
                logger.warning(f"⚠️ Target bucket '{S3_BUCKET}' not found in available buckets")
            
        except Exception as e:
            logger.error(f"❌ S3 client initialization failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.s3_client = None
            self.upload_enabled = False

    def upload_file_to_s3(self, local_file_path, s3_folder='uploads/'):
        """Upload a single file to S3"""
        if not self.upload_enabled or not self.s3_client:
            logger.warning("S3 upload disabled or client not available")
            return False
            
        try:
            filename = os.path.basename(local_file_path)
            s3_key = os.path.join(s3_folder, filename).replace('\\', '/')
            
            logger.info(f"📤 Uploading: {filename}")
            
            # Upload file
            self.s3_client.upload_file(local_file_path, S3_BUCKET, s3_key)
            
            logger.info(f"✅ Successfully uploaded: {filename} → s3://{S3_BUCKET}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to upload {filename}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def upload_files_from_directory(self, source_directory, s3_folder='uploads/', file_extensions=None):
        """Upload files from source directory to S3"""
        if not self.upload_enabled or not self.s3_client:
            logger.warning("S3 upload disabled or client not available")
            return False
            
        if file_extensions is None:
            file_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.txt', '.json'}
        
        logger.info(f"🚀 Starting S3 upload from {source_directory}")
        
        # Check if source directory exists
        if not os.path.exists(source_directory):
            logger.error(f"❌ Source directory does not exist: {source_directory}")
            return False
        
        # Get list of files to upload
        files_to_upload = []
        try:
            for filename in os.listdir(source_directory):
                file_extension = os.path.splitext(filename)[1].lower()
                if file_extension in file_extensions:
                    files_to_upload.append(filename)
            
            logger.info(f"📊 Found {len(files_to_upload)} files to upload")
            
            if not files_to_upload:
                logger.info("ℹ️ No files found matching the specified extensions")
                return True
            
        except Exception as e:
            logger.error(f"❌ Failed to list files in directory: {e}")
            return False
        
        # Upload files
        successful_uploads = 0
        failed_uploads = 0
        
        for filename in files_to_upload:
            try:
                local_file_path = os.path.join(source_directory, filename)
                s3_key = os.path.join(s3_folder, filename).replace('\\', '/')
                
                # Upload file
                self.s3_client.upload_file(local_file_path, S3_BUCKET, s3_key)
                
                logger.info(f"✅ Successfully uploaded: {filename} → s3://{S3_BUCKET}/{s3_key}")
                successful_uploads += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to upload {filename}: {e}")
                failed_uploads += 1
        
        # Summary
        logger.info(f"📊 Upload Summary - Success: {successful_uploads}, Failed: {failed_uploads}")
        
        return failed_uploads == 0

    def periodic_upload(self, interval_minutes=5):
        """Periodically upload files from both directories"""
        while self.upload_enabled:
            try:
                logger.info("🔄 Starting periodic upload...")
                
                # Upload screenshots
                image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
                self.upload_files_from_directory(self.screenshot_dir, 'screenshots/', image_extensions)
                
                # Upload output files
                output_extensions = {'.txt', '.json', '.csv', '.xlsx'}
                self.upload_files_from_directory(self.output_dir, 'outputs/', output_extensions)
                
                logger.info(f"💤 Waiting {interval_minutes} minutes before next upload...")
                time.sleep(interval_minutes * 60)  # Convert minutes to seconds
                
            except Exception as e:
                logger.error(f"❌ Periodic upload error: {e}")
                time.sleep(60)  # Wait 1 minute before retry

class XpertPOSApp:
    def __init__(self):
        try:
            logger.info("Initializing XpertPOSApp...")
            
            logger.info("Setting up paths...")
            setup_paths()  # Set up Tesseract path first
            logger.info("Paths setup completed")
            
            logger.info("Checking Tesseract...")
            check_tesseract_exists()
            logger.info("Tesseract check passed")
            
            logger.info("Setting up appearance mode...")
            ctk.set_appearance_mode("system")
            ctk.set_default_color_theme("dark-blue")
            logger.info("Appearance mode set")

            logger.info("Creating main window...")
            self.window = ctk.CTk()
            self.window.title("XPERT AD-TARGETING")
            self.window.resizable(True, True)
            self.center_window(750, 420)
            self.window.grid_rowconfigure(0, weight=1)
            self.window.grid_columnconfigure(0, weight=1)
            logger.info("Main window created")

            logger.info("Loading logo...")
            self.logo = load_logo_image()
            logger.info("Logo loaded")

            logger.info("Initializing variables...")
            self.screenshot_dir = None
            self.output_dir = None
            self.s3_uploader = None
            self.upload_thread = None

            # Persistence files
            self.selected_pos_file = "selected_pos.txt"
            self.user_info_file = "user_info.txt"
            self.pos_window_title = None
            self.login_key = None
            self.shop_name = None

            # Initialize threading variables
            self.stop_monitoring_event = threading.Event()
            self._monitoring_thread = None
            logger.info("Variables initialized")

            logger.info("Loading user info...")
            # Load persisted user info
            self.load_user_info()
            logger.info("User info loaded")

            logger.info("Checking for existing POS selection...")
            if self.login_key and os.path.exists(self.selected_pos_file):
                logger.info("Found existing POS selection")
                with open(self.selected_pos_file, encoding='utf-8') as f:
                    saved_title = f.read().strip()
                if saved_title:
                    logger.info(f"Using saved POS title: {saved_title}")
                    self.pos_window_title = saved_title
                    self.create_desktop_folders()
                    # Fetch shop name from MongoDB if not already loaded
                    if not self.shop_name:
                        logger.info("Fetching shop name from MongoDB...")
                        self.shop_name = self.fetch_shop_name(self.login_key)
                    self.show_active_status_ui(self.shop_name)
                    # Start monitoring in background instead of calling run_pipeline directly
                    self.start_monitoring_in_background()
                else:
                    logger.info("Saved POS title is empty, showing POS selection UI")
                    self.select_pos_window_ui()
            elif self.login_key:
                logger.info("Login key exists but no POS selection, showing POS selection UI")
                self.select_pos_window_ui()
            else:
                logger.info("No login key found, showing login UI")
                self.create_login_ui()
                
            logger.info("XpertPOSApp initialization completed successfully")
            
        except Exception as e:
            logger.error(f"ERROR in XpertPOSApp.__init__: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def load_user_info(self):
        if os.path.exists(self.user_info_file):
            try:
                with open(self.user_info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.login_key = data.get('login_key')
                self.shop_name = data.get('shop_name')
            except Exception as e:
                logger.error(f"Failed to load user info: {e}")
                self.login_key = None
                self.shop_name = None

    def save_user_info(self, login_key, shop_name):
        try:
            with open(self.user_info_file, 'w', encoding='utf-8') as f:
                json.dump({'login_key': login_key, 'shop_name': shop_name}, f)
        except Exception as e:
            logger.error(f"Failed to save user info: {e}")

    def clear_user_info(self):
        if os.path.exists(self.user_info_file):
            os.remove(self.user_info_file)
        self.login_key = None
        self.shop_name = None

    def fetch_shop_name(self, login_key):
        try:
            client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
            
            # Test basic connectivity first
            try:
                client.admin.command('ping')
            except Exception as ping_error:
                logger.error(f"❌ MongoDB ping failed in fetch_shop_name: {ping_error}")
                return None
            
            # Try to access the database
            try:
                db = client["XpertDB"]
                collection = db["billing_data"]
                result = collection.find_one({"login_key": login_key})
                if result and "shop_name" in result:
                    logger.info(f"✅ Shop name fetched successfully: {result['shop_name']}")
                    return result["shop_name"]
                else:
                    logger.warning(f"❌ Shop name not found for key: {login_key}")
                    return None
            except Exception as db_error:
                logger.error(f"❌ Database access error in fetch_shop_name: {db_error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ General error in fetch_shop_name: {e}")
            return None
        finally:
            try:
                client.close()
            except:
                pass

    def show_active_status_ui(self, shop_name):
        self.clear_window()
        self.window.configure(bg="#181A20")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(
            self.window,
            fg_color="#181A20",
            corner_radius=0,
            border_width=0
        )
        container.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            container,
            text=f"Shop Name: {shop_name if shop_name else 'N/A'}",
            font=("Inter", 22, "bold"),
            text_color="#fff",
            bg_color="#181A20"
        ).pack(pady=(48, 12))

        # Status label (store as self.status_label for updates)
        self.status_label = ctk.CTkLabel(
            container,
            text="Status: Active",
            font=("Inter", 18),
            text_color="#00FF00",
            bg_color="#181A20"
        )
        self.status_label.pack(pady=(0, 24))

        ctk.CTkButton(
            container,
            text="Logout",
            command=self.logout,
            font=("Inter", 15, "bold"),
            fg_color="#FF6C00",
            hover_color="#E55B00",
            text_color="#fff",
            width=200,
            height=44,
            corner_radius=10
        ).pack(pady=(0, 32))

        ctk.CTkButton(
            container,
            text="Start Monitoring",
            command=self.start_monitoring_in_background,
            font=("Inter", 15, "bold"),
            fg_color="#00AAFF",
            hover_color="#0088CC",
            text_color="#fff",
            width=200,
            height=44,
            corner_radius=10
        ).pack(pady=(0, 16))

        ctk.CTkButton(
            container,
            text="Change POS",
            command=self.change_pos,
            font=("Inter", 15, "bold"),
            fg_color="#0077FF",
            hover_color="#0055AA",
            text_color="#fff",
            width=200,
            height=44,
            corner_radius=10
        ).pack(pady=(0, 16))

        # Start monitoring in the background
        self.start_monitoring_in_background()

    def logout(self):
        # Stop background threads if needed (set a flag for your monitoring loop to exit)
        # Optionally update status to Inactive before closing
        if hasattr(self, 'status_label'):
            self.status_label.configure(text="Status: Inactive", text_color="#FF0000")
        
        # Stop monitoring thread
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.info("Stopping monitoring thread for logout...")
            self.stop_monitoring_event.set()
            self._monitoring_thread.join(timeout=2)  # Wait up to 2 seconds for thread to stop
        
        self.clear_user_info()
        if os.path.exists(self.selected_pos_file):
            os.remove(self.selected_pos_file)
        self.window.after(500, self.window.destroy)  # Give time for UI update

    def verify_key(self):
        entered_key = self.key_entry.get().strip()
        if not entered_key:
            show_error_dialog("Error", "Please enter a valid license key.")
            return
        try:
            # First, test the connection without specifying a database
            client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
            
            # Test basic connectivity
            try:
                client.admin.command('ping')
                logger.info("✅ MongoDB connection successful")
            except Exception as ping_error:
                logger.error(f"❌ MongoDB ping failed: {ping_error}")
                show_error_dialog("Connection Error", f"Could not connect to database server: {ping_error}")
                return
            
            # Try to access the XpertDB database
            try:
                db = client["XpertDB"]
                collection = db["billing_data"]
                
                # Test if we can access the collection
                result = collection.find_one({"login_key": entered_key})
                if result:
                    shop_name = result.get("shop_name", "N/A")
                    self.save_user_info(entered_key, shop_name)
                    self.login_key = entered_key
                    self.shop_name = shop_name
                    self.show_welcome_ui()
                    logger.info(f"✅ Key verification successful for shop: {shop_name}")
                else:
                    show_error_dialog("Invalid Key", "The license key entered is invalid or not found in the database.")
                    logger.warning(f"❌ Invalid key attempted: {entered_key}")
                    
            except Exception as db_error:
                logger.error(f"❌ Database access error: {db_error}")
                if "authentication failed" in str(db_error).lower():
                    show_error_dialog("Authentication Error", 
                                    "Database authentication failed. Please check your connection credentials.")
                elif "not authorized" in str(db_error).lower():
                    show_error_dialog("Authorization Error", 
                                    "You don't have permission to access the XpertDB database.")
                else:
                    show_error_dialog("Database Error", 
                                    f"Could not access the database: {db_error}")
                    
        except Exception as e:
            logger.error(f"❌ General connection error: {e}")
            if "authentication failed" in str(e).lower():
                show_error_dialog("Authentication Error", 
                                "Could not authenticate with the database. Please check your connection string.")
            elif "bad auth" in str(e).lower():
                show_error_dialog("Authentication Error", 
                                "Bad authentication. Please verify your database credentials.")
            else:
                show_error_dialog("Connection Error", f"Could not verify key: {e}")
        finally:
            try:
                client.close()
            except:
                pass

    def show_welcome_ui(self):
        self.clear_window()
        self.window.configure(bg="#181A20")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(
            self.window,
            fg_color="#181A20",
            corner_radius=0,
            border_width=0
        )
        container.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        ctk.CTkLabel(
            container,
            text="XPERT AD-TARGETING",
            font=("Inter", 28, "bold"),
            text_color="#fff",
            bg_color="#181A20"
        ).pack(pady=(80, 8))

        ctk.CTkLabel(
            container,
            text="Select your POS window to start ad targeting.",
            font=("Inter", 15),
            text_color="#B0B3B8",
            wraplength=400,
            bg_color="#181A20"
        ).pack(pady=(0, 48))

        proceed_btn = ctk.CTkButton(
            container,
            text="Proceed",
            command=self.select_pos_window_ui,
            font=("Inter", 16, "bold"),
            fg_color="#FF6C00",
            hover_color="#E55B00",
            text_color="#fff",
            width=220,
            height=48,
            corner_radius=12
        )
        proceed_btn.pack()
        
        self.window.bind('<Return>', lambda event: self.select_pos_window_ui())

    def create_desktop_folders(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.screenshot_dir = os.path.join(desktop, "screenshots")
        self.output_dir = os.path.join(desktop, "AllJsons")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize S3 uploader
        self.s3_uploader = S3Uploader(self.screenshot_dir, self.output_dir)

    def select_pos_window_ui(self):
        self.clear_window()
        self.window.geometry("700x400")
        self.window.configure(bg="#181A20")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.create_desktop_folders()

        container = ctk.CTkFrame(
            self.window,
            fg_color="#181A20",
            corner_radius=0,
            border_width=0
        )
        container.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            container,
            text="Select POS Window",
            font=("Inter", 22, "bold"),
            text_color="#fff",
            bg_color="#181A20"
        ).pack(pady=(64, 12))

        ctk.CTkLabel(
            container,
            text="Choose the POS window to monitor.",
            font=("Inter", 14),
            text_color="#B0B3B8",
            wraplength=500,
            bg_color="#181A20"
        ).pack(pady=(0, 32))

        window_titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
        if not window_titles:
            self.show_error_dialog("Error", "No windows found.")
            return

        self.selected_window = ctk.StringVar(value=window_titles[0])
        ctk.CTkOptionMenu(
            container,
            variable=self.selected_window,
            values=window_titles,
            font=("Inter", 14),
            width=350,
            height=38,
            fg_color="#23272F",
            button_color="#FF6C00",
            button_hover_color="#E55B00",
            dropdown_fg_color="#23272F",
            dropdown_hover_color="#34394A",
            dropdown_text_color="#fff"
        ).pack(pady=(0, 32))

        ctk.CTkButton(
            container,
            text="Confirm",
            command=self.save_and_start_monitoring,
            font=("Inter", 16, "bold"),
            fg_color="#FF6C00",
            hover_color="#E55B00",
            width=160,
            height=44,
            corner_radius=10
        ).pack()

        self.window.bind('<Return>', self._on_confirm_enter)

    def show_error_dialog(self, title, message):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(dialog, text=message, font=("Segoe UI", 14), wraplength=350)
        label.grid(row=0, column=0, padx=20, pady=20)

        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, font=("Segoe UI", 14), fg_color="#FF6C00", hover_color="#E55B00")
        button.grid(row=1, column=0, pady=10)

    def _on_confirm_enter(self, event):
        self.save_and_start_monitoring()
        self.window.unbind('<Return>')

    def save_and_start_monitoring(self):
        self.pos_window_title = self.selected_window.get()
        with open(self.selected_pos_file, "w", encoding='utf-8') as f:
            f.write(self.pos_window_title)
        add_to_startup()
        self.show_active_status_ui(self.shop_name)
        self.start_monitoring_in_background()  # Restart monitoring with new POS

    def start_monitoring(self, from_persistence=False):
        add_to_startup()
        self.window.withdraw()
        self.show_active_status_ui(self.shop_name)

    def start_s3_upload_thread(self):
        """Start the S3 upload thread for periodic uploads"""
        if self.s3_uploader and self.s3_uploader.upload_enabled:
            self.upload_thread = threading.Thread(
                target=self.s3_uploader.periodic_upload,
                args=(UPLOAD_INTERVAL_MINUTES,),
                daemon=True
            )
            self.upload_thread.start()
            logger.info("🚀 S3 upload thread started")

    def run_pipeline(self, stop_event):
        def on_phone_captured(phone_number):
            output_dir = self.output_dir or os.path.join(os.path.expanduser("~"), "Desktop", "AllJsons")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            phone_file = os.path.join(output_dir, f'phone_number_{phone_number}_{timestamp}.txt')
            with open(phone_file, 'w') as f:
                f.write(phone_number)
            if self.s3_uploader:
                self.s3_uploader.upload_file_to_s3(phone_file, 'phone_numbers/')
            logger.info(f"Captured and uploaded phone number: {phone_number}")

        def pipeline_callback(before_path, timestamp):
            before_path_expanded = expand_path(before_path)
            if not os.path.exists(before_path_expanded):
                import cv2
                import numpy as np
                dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
                os.makedirs(os.path.dirname(before_path_expanded), exist_ok=True)
                cv2.imwrite(before_path_expanded, dummy_img)

            # Run OCR and export
            ocr_and_export(before_path_expanded, timestamp, self.output_dir)
            
            # Fix the cleanup_jsons call to handle None case
            if self.output_dir:
                cleanup_jsons(folder_path=Path(self.output_dir))
            else:
                logger.warning("output_dir is None, skipping cleanup_jsons")

            # INSTANT UPLOAD: Upload the screenshot and output files immediately
            if self.s3_uploader:
                # Upload the screenshot
                self.s3_uploader.upload_file_to_s3(before_path_expanded, 'screenshots/')
                # Upload all new .json and .txt files in the output directory for this timestamp
                output_dir = self.output_dir or os.path.join(os.path.expanduser("~"), "Desktop", "AllJsons")
                for ext in ('.json', '.txt'):
                    output_file = os.path.join(output_dir, f"ocr_raw_{timestamp}{ext}")
                    if os.path.exists(output_file):
                        self.s3_uploader.upload_file_to_s3(output_file, 'outputs/')

        # No keyboard.hook here; phone number capture is handled in capture.py
        monitor_pos(self.pos_window_title, pipeline_callback, self.screenshot_dir, on_phone_captured=on_phone_captured, stop_event=stop_event)

    def center_window(self, width, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def create_login_ui(self):
        self.clear_window()
        self.window.configure(bg="#181A20")
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(
            self.window,
            fg_color="#181A20",
            corner_radius=0,
            border_width=0
        )
        container.grid(row=0, column=0, sticky="nsew")

        if self.logo:
            ctk.CTkLabel(container, image=self.logo, text="", bg_color="#181A20").pack(pady=(48, 12))

        ctk.CTkLabel(
            container,
            text="Sign in to XPERT",
            font=("Inter", 22, "bold"),
            text_color="#fff",
            bg_color="#181A20"
        ).pack(pady=(0, 24))

        self.key_entry = ctk.CTkEntry(
            container,
            width=260,
            height=44,
            show="*",
            placeholder_text="API Key",
            font=("Inter", 15),
            corner_radius=10,
            fg_color="#23272F",
            border_color="#333",
            text_color="#fff"
        )
        self.key_entry.pack(pady=(0, 24))
        self.key_entry.bind("<Return>", lambda event: self.verify_key())
        ctk.CTkButton(
            container,
            text="Log In",
            command=self.verify_key,
            font=("Inter", 15, "bold"),
            fg_color="#FF6C00",
            hover_color="#E55B00",
            text_color="#fff",
            width=200,
            height=44,
            corner_radius=10
        ).pack(pady=(0, 32))

        support_label = ctk.CTkLabel(
            container,
            text="Need help? support@xpert.chat",
            font=("Inter", 10),
            text_color="#888",
            cursor="hand2",
            bg_color="#181A20"
        )
        support_label.pack(pady=(0, 10))
        support_label.bind("<Button-1>", lambda e: webbrowser.open("mailto:support@xpert.chat"))

    def start_monitoring_in_background(self):
        # Stop any existing monitoring thread
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self.stop_monitoring_event.set()
            self._monitoring_thread.join()
        self.stop_monitoring_event.clear()
        self._monitoring_thread = threading.Thread(
            target=self.run_pipeline,
            args=(self.stop_monitoring_event,),
            daemon=True
        )
        self._monitoring_thread.start()

    def update_status(self, status_text, color):
        def do_update():
            self.status_label.configure(text=status_text, text_color=color)
        self.window.after(0, do_update)

    def change_pos(self):
        # Stop current monitoring thread before changing POS
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.info("Stopping current monitoring thread for POS change...")
            self.stop_monitoring_event.set()
            self._monitoring_thread.join(timeout=2)  # Wait up to 2 seconds for thread to stop
            if self._monitoring_thread.is_alive():
                logger.warning("Monitoring thread did not stop gracefully")
            self.stop_monitoring_event.clear()
        
        # Show the POS selection UI
        self.select_pos_window_ui()

# Load environment variables
dotenv_path = resource_path('.env')
load_dotenv(dotenv_path)

# Environment variables
LOGO_PATH = os.path.expanduser(os.path.expandvars(os.getenv("LOGO_PATH", "./xpert_ad_targeting_logo.jpeg")))
MONGO_URI = os.getenv("MONGO_URI")

# AWS S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
UPLOAD_INTERVAL_MINUTES = int(os.path.expandvars(os.getenv("UPLOAD_INTERVAL_MINUTES", "5")))

if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("STARTING MAIN EXECUTION")
        logger.info("=" * 60)
        
        print("[DEBUG] Starting XpertPOSApp...")
        logger.info("Creating XpertPOSApp instance...")
        
        app = XpertPOSApp()
        logger.info("XpertPOSApp instance created successfully")
        
        print("[DEBUG] App initialized, entering mainloop()...")
        logger.info("Starting mainloop...")
        
        app.window.mainloop()
        logger.info("Mainloop completed")
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR in main execution: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"[ERROR] Application crashed: {e}")
        print(f"[ERROR] Check logs for details")
        
        # Show error dialog to user
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Application Error", f"Application crashed:\n{str(e)}\n\nCheck logs for details.")
        except:
            pass  # If even the error dialog fails, just exit
    