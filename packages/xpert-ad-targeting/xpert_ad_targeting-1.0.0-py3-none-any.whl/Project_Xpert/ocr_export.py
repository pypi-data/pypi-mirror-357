# import cv2
# import pytesseract
# import os
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from dotenv import load_dotenv

# load_dotenv()

# TESSERACT_PATH = os.path.expanduser(os.getenv("TESSERACT_PATH", "./Tesseract-OCR/tesseract.exe"))
# MONGO_URI = os.getenv("MONGO_URI")

# pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# def ocr_and_export(image_path, timestamp, output_dir=None):
#     if output_dir is None:
#         output_dir = os.path.expanduser(os.getenv("OUTPUT_DIR", "~/Desktop/AllRawTexts"))
#     os.makedirs(output_dir, exist_ok=True)

#     # === ENHANCED IMAGE PREPROCESSING ===
#     img = cv2.imread(image_path)
#     img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray = cv2.GaussianBlur(gray, (5, 5), 0)
#     gray = cv2.adaptiveThreshold(
#         gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
#     )
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
#     gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

#     # === RAW OCR EXTRACTION ===
#     ocr_text = pytesseract.image_to_string(gray, config='--oem 3 --psm 3')

#     # === SAVE RAW TEXT TO FILE ===
#     filename = f"ocr_raw_{timestamp}.txt"
#     output_path = os.path.join(output_dir, filename)
#     try:
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(ocr_text)
#         print(f"✅ Raw OCR text saved to {output_path}")
#     except Exception as e:
#         print(f"❌ Failed to save text file: {e}")
#         return

#     # === UPLOAD RAW TEXT TO MONGODB ===
#     try:
#         client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
#         db = client["XpertDB"]
#         collection = db["raw_ocr_data"]
#         document = {
#             "timestamp": timestamp,
#             "raw_text": ocr_text,
#             "source_image": image_path
#         }
#         insert_result = collection.insert_one(document)
#         print(f"📤 Raw text uploaded successfully with _id: {insert_result.inserted_id}")
#     except Exception as e:
#         print(f"❌ MongoDB upload failed: {e}")

# import cv2
# import pytesseract
# import os
# import numpy as np
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from dotenv import load_dotenv

# load_dotenv()

# TESSERACT_PATH = os.path.expanduser(os.getenv("TESSERACT_PATH", "./Tesseract-OCR/tesseract.exe"))
# MONGO_URI = os.getenv("MONGO_URI")

# pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# def ocr_and_export(image_path, timestamp, output_dir=None):
#     if output_dir is None:
#         output_dir = os.path.expanduser(os.getenv("OUTPUT_DIR", "~/Desktop/AllRawTexts"))
#     os.makedirs(output_dir, exist_ok=True)

#     # ===== ENHANCED PREPROCESSING PIPELINE =====
#     try:
#         # Read image with alpha channel support
#         img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        
#         # Handle alpha channel if present
#         if img.shape[2] == 4:
#             img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
#         # Optimal scaling for document images
#         img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
        
#         # Convert to grayscale using luminance-weighted method
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
#         # Contrast Limited Adaptive Histogram Equalization
#         clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
#         gray = clahe.apply(gray)
        
#         # Noise reduction with bilateral filter
#         gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
#         # Adaptive thresholding with Otsu's method
#         gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                     cv2.THRESH_BINARY, 31, 12)
        
#         # Morphological operations
#         kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
#         gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
#     except Exception as e:
#         print(f"❌ Image processing failed: {e}")
#         return

#     # ===== OPTIMIZED TESSERACT CONFIGURATION =====
#     try:
#         # Multi-config approach for better accuracy
#         custom_config = r'''
#             --oem 3 
#             --psm 6 
#             -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/:,. 
#             -c preserve_interword_spaces=1
#         '''
        
#         ocr_text = pytesseract.image_to_string(gray, config=custom_config)
        
#     except Exception as e:
#         print(f"❌ OCR extraction failed: {e}")
#         return

#     # ===== POST-PROCESSING =====
#     # Remove empty lines and unnecessary whitespace
#     ocr_text = "\n".join([line.strip() for line in ocr_text.splitlines() if line.strip()])

#     # ===== SAVE AND UPLOAD =====
#     try:
#         filename = f"ocr_raw_{timestamp}.txt"
#         output_path = os.path.join(output_dir, filename)
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(ocr_text)
#         print(f"✅ Raw OCR text saved to {output_path}")
        
#         # MongoDB upload
#         client = MongoClient(MONGO_URI)
#         db = client["XpertDB"]
#         collection = db["raw_ocr_data"]
        
#         document = {
#             "timestamp": timestamp,
#             "raw_text": ocr_text,
#             "source_image": image_path,
#             "processing_steps": {
#                 "scaling": 2.0,
#                 "clahe": True,
#                 "bilateral_filter": True,
#                 "adaptive_threshold": True
#             }
#         }
        
#         insert_result = collection.insert_one(document)
#         print(f"📤 Raw text uploaded successfully with _id: {insert_result.inserted_id}")
        
#     except Exception as e:
#         print(f"❌ Save/upload failed: {e}")
import cv2
import pytesseract
import os
import numpy as np
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging
from datetime import datetime
import sys
from pathlib import Path
import traceback
#09876543210
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
    log_filename = f"ocr_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_filepath = log_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_filepath, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # This will work even if console is hidden
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"=" * 60)
    logger.info(f"OCR APPLICATION STARTED")
    logger.info(f"Log file: {log_filepath}")
    logger.info(f"Application directory: {app_dir}")
    logger.info(f"Running as executable: {getattr(sys, 'frozen', False)}")
    logger.info(f"=" * 60)
    
    return logger

# Initialize logger
logger = setup_logging()

# ===== ENVIRONMENT LOADING WITH LOGGING =====
def load_environment():
    """Load environment variables with comprehensive logging"""
    try:
        # Get the directory where the executable is located
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).parent
        else:
            app_dir = Path(__file__).parent
        
        env_path = app_dir / '.env'
        logger.info(f"Looking for .env file at: {env_path}")
        logger.info(f".env file exists: {env_path.exists()}")
        
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("✅ .env file loaded successfully")
        else:
            logger.warning("⚠️ .env file not found, using system environment variables")
            load_dotenv()  # Load from system environment
        
        # Get environment variables
        # Use Windows path as default, not Linux path
        default_tesseract_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Tesseract-OCR", "tesseract.exe")
        tesseract_path = os.path.expanduser(os.getenv("TESSERACT_PATH", default_tesseract_path))
        mongo_uri = os.getenv("MONGO_URI")
        output_dir = os.path.expanduser(os.getenv("OUTPUT_DIR", "~/Desktop/AllRawTexts"))
        
        logger.info(f"TESSERACT_PATH: {tesseract_path}")
        logger.info(f"TESSERACT_PATH exists: {os.path.exists(tesseract_path)}")
        logger.info(f"MONGO_URI loaded: {mongo_uri is not None}")
        logger.info(f"MONGO_URI length: {len(mongo_uri) if mongo_uri else 0}")
        logger.info(f"OUTPUT_DIR: {output_dir}")
        
        return tesseract_path, mongo_uri, output_dir
        
    except Exception as e:
        logger.error(f"❌ Environment loading failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Load environment
TESSERACT_PATH, MONGO_URI, DEFAULT_OUTPUT_DIR = load_environment()
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def test_mongodb_connection(mongo_uri):
    """Test MongoDB connection with detailed logging"""
    logger.info("🔍 Testing MongoDB connection...")
    
    if not mongo_uri:
        logger.error("❌ MONGO_URI is None or empty")
        return False
    
    try:
        client = MongoClient(
            mongo_uri,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test connection
        result = client.admin.command('ping')
        logger.info(f"✅ MongoDB ping successful: {result}")
        
        # Test database access
        db = client["XpertDB"]
        collections = db.list_collection_names()
        logger.info(f"✅ Database 'XpertDB' accessible, collections: {collections}")
        
        client.close()
        logger.info("✅ MongoDB connection test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def ocr_and_export(image_path, timestamp, output_dir=None):
    """Enhanced OCR function with comprehensive logging"""
    logger.info(f"🚀 Starting OCR processing for: {image_path}")
    logger.info(f"📅 Timestamp: {timestamp}")
    
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    logger.info(f"📁 Output directory: {output_dir}")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"✅ Output directory created/verified")
    except Exception as e:
        logger.error(f"❌ Failed to create output directory: {e}")
        return False

    # ===== IMAGE VALIDATION =====
    logger.info("🔍 Validating image...")
    if not os.path.exists(image_path):
        logger.error(f"❌ Image file does not exist: {image_path}")
        return False
    
    file_size = os.path.getsize(image_path)
    logger.info(f"📊 Image file size: {file_size} bytes")

    # ===== ENHANCED PREPROCESSING PIPELINE =====
    logger.info("🖼️ Starting image preprocessing...")
    try:
        # Read image with alpha channel support
        logger.debug("Reading image with cv2.imdecode...")
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        
        if img is None:
            logger.error("❌ Failed to load image - image is None")
            return False
        
        logger.info(f"✅ Image loaded successfully, shape: {img.shape}")
        
        # Handle alpha channel if present
        if len(img.shape) == 3 and img.shape[2] == 4:
            logger.debug("Converting BGRA to BGR...")
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # Optimal scaling for document images
        logger.debug("Scaling image...")
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
        logger.info(f"✅ Image scaled, new shape: {img.shape}")
        
        # Convert to grayscale using luminance-weighted method
        logger.debug("Converting to grayscale...")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Contrast Limited Adaptive Histogram Equalization
        logger.debug("Applying CLAHE...")
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Noise reduction with bilateral filter
        logger.debug("Applying bilateral filter...")
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Adaptive thresholding with Otsu's method
        logger.debug("Applying adaptive thresholding...")
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 12)
        
        # Morphological operations
        logger.debug("Applying morphological operations...")
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        logger.info("✅ Image preprocessing completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Image processing failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

    # ===== OPTIMIZED TESSERACT CONFIGURATION =====
    logger.info("🔤 Starting OCR extraction...")
    try:
        # Multi-config approach for better accuracy
        custom_config = r'''
            --oem 3 
            --psm 6 
            -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/:,. 
            -c preserve_interword_spaces=1
        '''
        
        logger.debug(f"Tesseract config: {custom_config.strip()}")
        ocr_text = pytesseract.image_to_string(gray, config=custom_config)
        
        logger.info(f"✅ OCR extraction completed, text length: {len(ocr_text)} characters")
        logger.debug(f"OCR text preview (first 100 chars): {ocr_text[:100]}")
        
    except Exception as e:
        logger.error(f"❌ OCR extraction failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

    # ===== POST-PROCESSING =====
    logger.info("🧹 Post-processing OCR text...")
    original_length = len(ocr_text)
    ocr_text = "\n".join([line.strip() for line in ocr_text.splitlines() if line.strip()])
    logger.info(f"✅ Post-processing completed, length: {original_length} -> {len(ocr_text)}")

    # ===== SAVE TO FILE =====
    logger.info("💾 Saving text to file...")
    try:
        filename = f"ocr_raw_{timestamp}.txt"
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ocr_text)
        logger.info(f"✅ Raw OCR text saved to {output_path}")
    except Exception as e:
        logger.error(f"❌ File save failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

    # ===== MONGODB UPLOAD =====
    logger.info("📤 Starting MongoDB upload...")
    
    # Test connection first
    if not test_mongodb_connection(MONGO_URI):
        logger.error("❌ MongoDB connection test failed, skipping upload")
        return False
    
    client = None
    try:
        logger.debug("Creating MongoDB client...")
        client = MongoClient(
            MONGO_URI,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        logger.debug("Accessing database and collection...")
        db = client["XpertDB"]
        collection = db["raw_ocr_data"]
        
        document = {
            "timestamp": timestamp,
            "raw_text": ocr_text,
            "source_image": image_path,
            "processing_steps": {
                "scaling": 2.0,
                "clahe": True,
                "bilateral_filter": True,
                "adaptive_threshold": True
            },
            "metadata": {
                "text_length": len(ocr_text),
                "file_size": file_size,
                "processed_at": datetime.now().isoformat()
            }
        }
        
        logger.debug(f"Document prepared, size: {len(str(document))} characters")
        
        insert_result = collection.insert_one(document)
        logger.info(f"✅ Raw text uploaded successfully with _id: {insert_result.inserted_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB upload failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
        
    finally:
        if client:
            logger.debug("Closing MongoDB connection...")
            client.close()

