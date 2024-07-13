import os
import json
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict
from config_util import ensure_directory_exists, save_config, load_file_content
from error_reporting import report_error

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_files, config_data, metadata, base_directory, config_dir, database_dir, lookup_table):
        self.config_files = config_files
        self.config_data = config_data
        self.metadata = metadata
        self.base_directory = base_directory
        self.config_dir = config_dir
        self.database_dir = database_dir
        self.lookup_table = lookup_table

    def apply_changes(self, ui_vars):
        all_success = True
        for relative_path, options in ui_vars.items():
            success = self.process_file(relative_path, options)
            if not success:
                all_success = False
        self.show_result_message(all_success)

    def process_file(self, relative_path, options):
        try:
            for option_path, var in options.items():
                self.update_config_data(option_path, var, relative_path)

            full_path = self.determine_full_path(relative_path)

            existing_content = load_file_content(full_path)
            if existing_content == self.config_data[relative_path]:
                return True

            return self.save_file(full_path, self.config_data[relative_path])
        except Exception as e:
            report_error(f"Error processing file {relative_path}", e)
            return False

    def update_config_data(self, option_path, var, relative_path):
        keys = option_path.split('.')
        current_value = self.config_data[relative_path]
        for key in keys[:-1]:
            current_value = current_value[key]

        self.set_config_value(current_value, keys[-1], var, relative_path, option_path)

    def set_config_value(self, current_value, last_key, var, relative_path, option_path):
        try:
            if isinstance(var, tk.BooleanVar):
                current_value[last_key] = var.get()
            elif isinstance(var, tk.StringVar):
                value_type = self.get_value_type(relative_path, option_path)
                current_value[last_key] = self.convert_value(var.get(), value_type)
        except ValueError as e:
            report_error(f"Invalid value for {option_path}", e)

    def get_value_type(self, relative_path, option_path):
        filename = self.lookup_table.get(option_path)
        if filename and filename in self.metadata and option_path in self.metadata[filename]:
            return self.metadata[filename][option_path].get("type")
        return None

    @staticmethod
    def convert_value(value, value_type):
        if value_type == "float":
            return float(value)
        elif value_type == "int":
            return int(value)
        return value

    def determine_full_path(self, relative_path):
        return os.path.join(self.base_directory, 'SPT_Data', 'Server', relative_path)

    def save_file(self, full_path, config_data):
        try:
            ensure_directory_exists(full_path)
            return save_config(full_path, config_data)
        except OSError as e:
            report_error(f"Failed to save configuration file: {full_path}", e)
            return False

    @staticmethod
    def show_result_message(all_success):
        if all_success:
            messagebox.showinfo("Info", "All configurations saved successfully!")
        else:
            messagebox.showerror("Error", "Some configurations failed to save. Please check the logs for details.")
