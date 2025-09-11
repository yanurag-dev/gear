import yaml
import os
from dotenv import load_dotenv

def load_config(config_path: str = 'config/settings.yaml'):
    load_dotenv() # Load environment variables from .env file

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override API key from environment variable if available
    if 'GEMINI_API_KEY' in os.environ:
        if 'llm' not in config:
            config['llm'] = {}
        config['llm']['api_key'] = os.environ['GEMINI_API_KEY']

    return config