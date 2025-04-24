import logging
from logging.handlers import RotatingFileHandler
import time
import threading
from datetime import datetime
import inspect

class Logger:
    _instance = None
    
    def __new__(cls, name, log_path, enabled=True):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, name, log_path, enabled=True):
        if self._initialized:
            return
            
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._initialized = True
        
        if not enabled:
            self.logger.addHandler(logging.NullHandler())
            return
            
        class TimingFilter(logging.Filter):
            def __init__(self):
                super().__init__()
                self.last_time = time.time() * 1000  
                
            def filter(self, record):
                current_time = time.time() * 1000
                record.ms_since_last = int(current_time - self.last_time)
                self.last_time = current_time
                return True

        class DetailedFormatter(logging.Formatter):
            def format(self, record):
                # Get caller information
                frame = inspect.currentframe()
                while frame:
                    if frame.f_code.co_name == '_log':
                        caller_frame = frame.f_back
                        break
                    frame = frame.f_back
                
                if caller_frame:
                    record.src_info = (f"{caller_frame.f_code.co_filename}:"
                                     f"{caller_frame.f_lineno}:"
                                     f"{caller_frame.f_code.co_name}")
                else:
                    record.src_info = "unknown:0:unknown"
                
                record.dt = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                record.thread_id = threading.get_ident()
                
                return super().format(record)
        
        # Used for creating handlers
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        console_handler = logging.StreamHandler()
        
        # used for applying formatters
        formatter = DetailedFormatter(
            "[%(dt)s %(ms_since_last)d msSinceLastMsg] [thread %(thread_id)d] "
            "[%(levelname)s] [srcInfo: %(src_info)s] %(message)s"
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        timing_filter = TimingFilter()
        file_handler.addFilter(timing_filter)
        console_handler.addFilter(timing_filter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.propagate = False