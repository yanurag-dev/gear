import yaml
import os
from dotenv import load_dotenv
import logging

_logger = logging.getLogger(__name__)

def _substitute_env_vars(obj):
    """Recursively substitute environment variables in configuration values."""
    if isinstance(obj, dict):
        return {key: _substitute_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        return os.path.expandvars(obj)
    else:
        return obj

def load_config(config_path: str = 'config/settings.yaml'):
    load_dotenv() # Load environment variables from .env file

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError as e:
        _logger.error(f"Config file not found at {config_path}: {e}")
        raise ValueError(f"Config file not found at {config_path}") from e
    except PermissionError as e:
        _logger.error(f"Permission denied to read config file at {config_path}: {e}")
        raise ValueError(f"Permission denied to read config file at {config_path}") from e
    except yaml.YAMLError as e:
        _logger.error(f"Error parsing YAML config file at {config_path}: {e}")
        raise ValueError(f"Error parsing YAML config file at {config_path}") from e
    
    # Substitute environment variables in the config
    config = _substitute_env_vars(config)
    
    return config
