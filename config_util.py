import json
import logging
import os  # Add the missing import
from typing import Any, Dict, Optional
from error_reporting import report_error

logger = logging.getLogger(__name__)

def load_config(path: str) -> Optional[Dict[str, Any]]:
    """Load a JSON configuration file from the given path."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        report_error(f"Error loading {path}", e)
        return None

def save_config(path: str, config_data: Dict[str, Any]) -> bool:
    """Save the given configuration data to a JSON file at the specified path."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
            return True
    except OSError as e:
        report_error(f"Error saving {path}", e)
        return False

def ensure_directory_exists(filepath: str) -> None:
    """Ensure the directory for the given filepath exists."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

def load_file_content(filepath: str) -> Optional[Dict[str, Any]]:
    """Load the content of the specified file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        report_error(f"Error loading {filepath}", e)
        return None
