import yaml
import os
from typing import Optional, Any, Dict
from dotenv import load_dotenv
import logging

_logger = logging.getLogger(__name__)

def _substitute_env_vars(obj: Any) -> Any:
    """Recursively substitute environment variables in configuration values."""
    if isinstance(obj, dict):
        return {key: _substitute_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        return os.path.expandvars(obj)
    else:
        return obj

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    if config_path is None:
        # Resolve path relative to this loader.py file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'settings.yaml')
    
    # Try to find .env in current directory or project root
    env_path = os.path.join(os.getcwd(), '.env')
    if not os.path.exists(env_path):
        # Fallback to project root if called from elsewhere
        project_root = os.path.dirname(os.path.dirname(base_dir))
        env_path = os.path.join(project_root, '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        _logger.warning(f".env file not found at {env_path}. Ensure environment variables are set.")

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
    substituted_config = _substitute_env_vars(config)
    
    # Type assertion for mypy
    assert isinstance(substituted_config, dict)
    return substituted_config
