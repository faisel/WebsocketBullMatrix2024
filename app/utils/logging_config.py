import logging
from pytz import timezone
from datetime import datetime
import os
from logging.handlers import TimedRotatingFileHandler

# Custom formatter class to handle Zürich time
class ZurichFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        return dt.astimezone(timezone('Europe/Zurich'))
    
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Set the log file path
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../log/app.log')

    # Ensure the directory exists
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up TimedRotatingFileHandler to rotate logs every night at midnight
    file_handler = TimedRotatingFileHandler(
        log_file_path, when="midnight", interval=1, backupCount=7  # Keep 7 days of logs
    )
    file_handler.setLevel(logging.DEBUG)

    # Set formatter with Zurich time
    formatter = ZurichFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add handler only if not already added
    if not logger.hasHandlers():
        logger.addHandler(file_handler)

    # Test logging
    logger.debug("Logger initialized successfully")
    return logger

def test_logger():
    logger = get_logger('test_logger')
    logger.debug("This is a test log message.")
    logger.handlers[0].flush()  # Flush logs to the file

    # Debugging: Check if logs are being written
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../log/app.log')
    if os.path.exists(log_file_path):
        print(f"Log file exists: {log_file_path}")
    else:
        print(f"Log file not found: {log_file_path}")
