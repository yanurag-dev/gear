import pytest
from config.loader import load_config
import os

def test_load_config_basic():
    # Create a dummy settings.yaml for this basic test
    # In a real scenario, you'd mock the file system or use tmp_path
    # For this basic test, we'll assume settings.yaml exists and is valid
    # or that load_config handles its absence gracefully (which it does now)

    # Temporarily create a dummy settings.yaml if it doesn't exist
    # This is just for the basic test to pass without needing a real file
    # in the test environment.
    dummy_config_path = 'config/settings.yaml'
    if not os.path.exists(dummy_config_path):
        os.makedirs(os.path.dirname(dummy_config_path), exist_ok=True)
        with open(dummy_config_path, 'w') as f:
            f.write("llm:\n  provider: test_provider")

    config = load_config()
    assert isinstance(config, dict)
    assert 'llm' in config
    assert 'provider' in config['llm']

    # Clean up the dummy file if created
    if os.path.exists(dummy_config_path) and os.path.getsize(dummy_config_path) == len("llm:\n  provider: test_provider"):
        os.remove(dummy_config_path)