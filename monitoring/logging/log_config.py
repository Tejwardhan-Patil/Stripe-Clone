import logging
import logging.config
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
import sys

# Define log directory and ensure it exists
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Basic log format for standard logs
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Error-specific log format for tracking issues
ERROR_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s - Line: %(lineno)d'

# Setting up log file paths
GENERAL_LOG_FILE = os.path.join(LOG_DIR, 'app.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')

# Log level setup
LOG_LEVEL = logging.DEBUG

# Define rotating file handler for general logging
general_file_handler = RotatingFileHandler(
    GENERAL_LOG_FILE, maxBytes=10*1024*1024, backupCount=5  # 10 MB per file, 5 backup files
)
general_file_handler.setLevel(LOG_LEVEL)
general_file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# Define rotating file handler for error logging
error_file_handler = RotatingFileHandler(
    ERROR_LOG_FILE, maxBytes=5*1024*1024, backupCount=3  # 5 MB per file, 3 backup files
)
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(logging.Formatter(ERROR_LOG_FORMAT, datefmt=DATE_FORMAT))

# Console handler for debugging in development
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

# SMTP handler for critical errors (sending emails on errors)
smtp_handler = SMTPHandler(
    mailhost=("smtp.website.com", 587),
    fromaddr="error_logger@website.com",
    toaddrs=["admin@website.com"],
    subject="Critical Error in Application",
    credentials=("user", "password"),
    secure=()
)
smtp_handler.setLevel(logging.CRITICAL)
smtp_handler.setFormatter(logging.Formatter(ERROR_LOG_FORMAT, datefmt=DATE_FORMAT))

# Configure logger
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': LOG_FORMAT,
            'datefmt': DATE_FORMAT,
        },
        'error': {
            'format': ERROR_LOG_FORMAT,
            'datefmt': DATE_FORMAT,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'general_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': GENERAL_LOG_FILE,
            'maxBytes': 10*1024*1024,  # 10 MB
            'backupCount': 5,
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'error',
            'filename': ERROR_LOG_FILE,
            'maxBytes': 5*1024*1024,  # 5 MB
            'backupCount': 3,
        },
        'email': {
            'class': 'logging.handlers.SMTPHandler',
            'level': 'CRITICAL',
            'formatter': 'error',
            'mailhost': ("smtp.website.com", 587),
            'fromaddr': 'error_logger@website.com',
            'toaddrs': ['admin@website.com'],
            'subject': 'Critical Error in Application',
            'credentials': ('user', 'password'),
            'secure': (),
        },
    },
    'loggers': {
        '': {  # root logger
            'level': 'DEBUG',
            'handlers': ['console', 'general_file', 'error_file'],
        },
        'error_logger': {  # logger for critical errors
            'level': 'ERROR',
            'handlers': ['error_file', 'email'],
            'propagate': False,
        },
    }
})

# Test the logger configuration
logger = logging.getLogger(__name__)
error_logger = logging.getLogger('error_logger')

logger.debug("Debug log: Application is running.")
logger.info("Info log: Initialization successful.")
logger.warning("Warning log: Disk space low.")
error_logger.error("Error log: Failed to save user data.")
error_logger.critical("Critical log: System shutdown imminent!")