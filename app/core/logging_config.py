import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatter untuk menghasilkan log dalam format JSON
    """
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Mengatur konfigurasi logging
    """
    # Buat direktori log jika belum ada
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Set level logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Buat logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Hapus handler yang sudah ada
    root_logger.handlers = []
    
    # Formatter
    json_formatter = JSONFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler jika log_file disediakan
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)
    
    # Logging untuk library pihak ketiga
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

class LogContext:
    """
    Context manager untuk menambahkan konteks ke log
    """
    def __init__(self, logger: logging.Logger, **kwargs):
        self.logger = logger
        self.old_extra = getattr(logger, 'extra', {})
        self.extra = kwargs
    
    def __enter__(self):
        self.logger.extra = {**self.old_extra, **self.extra}
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.extra = self.old_extra

def get_logger(name: str) -> logging.Logger:
    """
    Mendapatkan logger dengan nama tertentu
    """
    return logging.getLogger(name)

# Contoh penggunaan:
"""
from app.core.logging_config import get_logger, LogContext

logger = get_logger(__name__)

# Logging biasa
logger.info("Pesan log biasa")

# Logging dengan konteks
with LogContext(logger, user_id=123, request_id="abc"):
    logger.info("Pesan log dengan konteks")
    logger.error("Error dengan konteks", exc_info=True)
""" 