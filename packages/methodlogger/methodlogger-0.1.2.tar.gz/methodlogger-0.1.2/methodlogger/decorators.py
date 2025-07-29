import time
import functools
import logging
import importlib
from methodlogger import log_config

_logger = logging.getLogger(__name__)

_cached_config = None

def _get_config():
    global _cached_config
    if _cached_config is None or log_config.CONFIG.get("force_reload"):
        importlib.reload(log_config)
        _cached_config = log_config.CONFIG.copy()
        _logger.debug("Log config reloaded: %s", _cached_config)
    return _cached_config

def log_method(custom_message=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = _get_config()
            if not config.get("enabled"):
                return func(*args, **kwargs)
            method_name = func.__qualname__
            msg = custom_message or config.get("default_message") or f"→ {method_name}"
            _logger.info(f"→ {msg} ({method_name})")
            start_time = time.time()
            result = func(*args, **kwargs)
            if config.get("log_time"):
                duration = time.time() - start_time
                _logger.info(f"← {msg} ({method_name}) completed in {duration:.3f}s")
            else:
                _logger.info(f"← {msg} ({method_name}) done")
            return result
        return wrapper
    return decorator
