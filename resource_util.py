import json
import os
import sys
import logging
from tkinter import filedialog, messagebox
from typing import Optional
from error_reporting import report_error

logger = logging.getLogger(__name__)

CONFIG_FILE = "config_dir.json"

def resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource, works for development and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_base_directory() -> Optional[str]:
    """Get the base directory where SPT_Data is located."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                base_dir = config.get("base_directory")
                if base_dir and os.path.exists(base_dir):
                    return base_dir
        # Show a message box before opening the file dialog
        messagebox.showinfo("Select Base Directory", "Please select the base directory where SPT_Data is located.")
        base_dir = filedialog.askdirectory(title="Select the base directory where SPT_Data is located")
        if base_dir:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"base_directory": base_dir}, f)
            return base_dir
    except (json.JSONDecodeError, IOError) as e:
        report_error(f"Error accessing {CONFIG_FILE}", e)
    return None

def create_lookup_table(metadata: dict) -> dict:
    lookup_table = {}
    for category, files in metadata.items():
        for filename, options in files.items():
            for option_path in options.keys():
                lookup_table[option_path] = filename
    return lookup_table

def load_metadata(file_path: str) -> Optional[dict]:
    """Load metadata from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        report_error(f"Error loading metadata from {file_path}", e)
        return None
