import pytest
import logging
import json
import os
from datetime import datetime
from app.core.logging_config import (
    setup_logging,
    get_logger,
    LogContext,
    JSONFormatter
)

@pytest.fixture
def log_file():
    # Buat file log temporary
    log_file = "test.log"
    yield log_file
    # Cleanup setelah test
    if os.path.exists(log_file):
        os.remove(log_file)

def test_setup_logging(log_file):
    """Test setup logging"""
    # Setup logging
    setup_logging(log_file=log_file)
    
    # Cek file log dibuat
    assert os.path.exists(log_file)
    
    # Cek handler terpasang
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) > 0

def test_get_logger():
    """Test mendapatkan logger"""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"

def test_log_context():
    """Test context manager untuk logging"""
    logger = get_logger("test_module")
    
    with LogContext(logger, {"request_id": "123"}):
        logger.info("Test message")
    
    # Cek log message mengandung context
    with open("test.log", "r") as f:
        log_message = json.loads(f.readline())
        assert log_message["request_id"] == "123"

def test_json_formatter():
    """Test JSON formatter"""
    formatter = JSONFormatter()
    
    # Buat log record
    record = logging.LogRecord(
        name="test_module",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Format log record
    formatted = formatter.format(record)
    
    # Cek format JSON
    log_dict = json.loads(formatted)
    assert log_dict["level"] == "INFO"
    assert log_dict["message"] == "Test message"
    assert log_dict["module"] == "test_module"

def test_log_levels(log_file):
    """Test berbagai level logging"""
    logger = get_logger("test_module")
    
    # Log dengan berbagai level
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Cek file log
    with open(log_file, "r") as f:
        log_messages = [json.loads(line) for line in f]
        
        # Cek level logging
        levels = [msg["level"] for msg in log_messages]
        assert "DEBUG" in levels
        assert "INFO" in levels
        assert "WARNING" in levels
        assert "ERROR" in levels

def test_log_with_exception(log_file):
    """Test logging dengan exception"""
    logger = get_logger("test_module")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Error occurred", exc_info=True)
    
    # Cek file log
    with open(log_file, "r") as f:
        log_message = json.loads(f.readline())
        assert "exception" in log_message
        assert "ValueError" in log_message["exception"]

def test_log_with_extra_fields(log_file):
    """Test logging dengan extra fields"""
    logger = get_logger("test_module")
    
    logger.info(
        "Test message",
        extra={
            "user_id": "123",
            "action": "login"
        }
    )
    
    # Cek file log
    with open(log_file, "r") as f:
        log_message = json.loads(f.readline())
        assert log_message["user_id"] == "123"
        assert log_message["action"] == "login"

def test_log_rotation(log_file):
    """Test rotasi file log"""
    # Setup logging dengan maxBytes kecil
    setup_logging(
        log_file=log_file,
        max_bytes=1000,
        backup_count=2
    )
    
    logger = get_logger("test_module")
    
    # Buat log sampai file terisi
    for i in range(100):
        logger.info(f"Test message {i}")
    
    # Cek file backup dibuat
    assert os.path.exists(f"{log_file}.1")
    assert os.path.exists(f"{log_file}.2")

def test_log_timestamp(log_file):
    """Test timestamp dalam log"""
    logger = get_logger("test_module")
    
    logger.info("Test message")
    
    # Cek file log
    with open(log_file, "r") as f:
        log_message = json.loads(f.readline())
        assert "timestamp" in log_message
        
        # Cek format timestamp
        timestamp = datetime.fromisoformat(log_message["timestamp"])
        assert isinstance(timestamp, datetime)

def test_log_with_context_manager(log_file):
    """Test logging dengan context manager"""
    logger = get_logger("test_module")
    
    with LogContext(logger, {"request_id": "123", "user_id": "456"}):
        logger.info("Test message")
        with LogContext(logger, {"action": "process"}):
            logger.info("Nested message")
    
    # Cek file log
    with open(log_file, "r") as f:
        log_messages = [json.loads(line) for line in f]
        
        # Cek context diwarisi
        assert log_messages[0]["request_id"] == "123"
        assert log_messages[0]["user_id"] == "456"
        assert log_messages[1]["request_id"] == "123"
        assert log_messages[1]["user_id"] == "456"
        assert log_messages[1]["action"] == "process" 