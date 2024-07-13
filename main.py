import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import logging
import json

from resource_util import resource_path, get_base_directory, load_metadata, create_lookup_table
from config_manager import ConfigManager
from config_util import load_file_content, save_config
from ui_util import update_ui_from_config, toggle_option, create_ui_components, create_grouped_ui, create_tooltip
from logging_config import setup_logging
from error_reporting import report_error

setup_logging()

logger = logging.getLogger(__name__)

def scan_directory(directory, extension=".json"):
    """Scan the directory for files with a given extension."""
    try:
        return {
            os.path.relpath(os.path.join(root, file), directory): os.path.join(root, file)
            for root, _, files in os.walk(directory)
            for file in files if file.endswith(extension)
        }
    except Exception as e:
        report_error(f"Error scanning directory {directory}", e)
        return {}

def save_template(config_files, config_data, presets_dir):
    """Save a template of the current configuration data to a JSON file."""
    try:
        template_filename = filedialog.asksaveasfilename(
            initialdir=presets_dir, defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if template_filename:
            template_data = {filename: config_data[filename] for filename in config_files}
            if save_config(template_filename, template_data):
                messagebox.showinfo("Info", "Template saved successfully!")
    except Exception as e:
        report_error("Error saving template", e)

def load_template(config_files, config_data, ui_vars, presets_dir):
    """Load a template from a JSON file."""
    try:
        template_filename = filedialog.askopenfilename(
            initialdir=presets_dir, filetypes=[("JSON files", "*.json")]
        )
        if template_filename:
            template_data = load_file_content(template_filename)
            if template_data:
                for filename in config_files:
                    if filename in template_data:
                        config_data[filename] = template_data[filename]
                        update_ui_from_config(filename, ui_vars, config_data)
                messagebox.showinfo("Info", "Template loaded successfully! - Don't Forget to APPLY!")
    except Exception as e:
        report_error("Error loading template", e)

def initialize_directories(base_directory):
    """Initialize the required directories."""
    try:
        CONFIG_DIR = os.path.join(base_directory, 'SPT_Data', 'Server', 'configs')
        DATABASE_DIR = os.path.join(base_directory, 'SPT_Data', 'Server', 'database')
        PRESETS_DIR = os.path.join(base_directory, 'user/mods/turtles-serverconfig/presets')
        return CONFIG_DIR, DATABASE_DIR, PRESETS_DIR
    except Exception as e:
        report_error("Error initializing directories", e)
        return None, None, None

def load_all_config_files(required_files, base_directory):
    """Load only the required configuration files."""
    try:
        config_data = {}
        for relative_path in required_files:
            full_path = os.path.join(base_directory, 'SPT_Data', 'Server', relative_path)
            try:
                config_data[relative_path] = load_file_content(full_path)
                if config_data[relative_path] is None:
                    raise FileNotFoundError(f"File not found or failed to load: {relative_path}")
            except FileNotFoundError as e:
                logger.error(f"Failed to load configuration file: {relative_path}. It may be missing or misspelled.")
                messagebox.showwarning("Warning", f"Failed to load configuration file: {relative_path}. It may be missing or misspelled.")
        return config_data
    except Exception as e:
        report_error("Error loading all config files", e)
        return {}

def create_main_ui(metadata, all_config_files, config_data, ui_vars, base_directory, CONFIG_DIR, DATABASE_DIR, PRESETS_DIR, lookup_table):
    """Create the main user interface."""
    try:
        root = tk.Tk()
        root.title("Turtles Server Config")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        notebook_frame = tk.Frame(scrollable_frame)
        notebook_frame.pack(expand=True)

        notebook = ttk.Notebook(notebook_frame)
        notebook.pack(pady=10, padx=10)

        for tab, files in metadata.items():
            group_options = {}
            for filename, options in files.items():
                for option, meta in options.items():
                    group_name = meta.get("group", "General")
                    group_options.setdefault(group_name, {})[option] = meta

            create_grouped_ui(tab, group_options, notebook, filename, config_data, ui_vars, toggle_option, lookup_table)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        create_controls(root, all_config_files, ui_vars, config_data, metadata, base_directory, CONFIG_DIR, DATABASE_DIR, PRESETS_DIR, lookup_table)

        root.update_idletasks()
        tabs_width = sum(notebook.nametowidget(tab).winfo_width() for tab in notebook.tabs()) + 20
        window_width, window_height = tabs_width, 600
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        position_top, position_right = int(screen_height / 2 - window_height / 2), int(screen_width / 2 - window_width / 2)

        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        notebook_frame.pack(anchor="center")

        # Bind the window close event to the custom handler
        root.protocol("WM_DELETE_WINDOW", lambda: on_exit(root, ui_vars, config_data, CONFIG_DIR, DATABASE_DIR, lookup_table))

        root.mainloop()
    except Exception as e:
        report_error("Error creating main UI", e)

def create_controls(root, all_config_files, ui_vars, config_data, metadata, base_directory, CONFIG_DIR, DATABASE_DIR, PRESETS_DIR, lookup_table):
    """Create the control buttons for applying changes and saving/loading templates."""
    try:
        control_frame = tk.Frame(root)
        control_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        buttons_frame = tk.Frame(control_frame)
        buttons_frame.pack(anchor="center")

        def create_button(text, command, tooltip):
            button = tk.Button(buttons_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=5)
            create_tooltip(button, tooltip)
            return button

        # Create an instance of ConfigManager
        config_manager = ConfigManager(all_config_files, config_data, metadata, base_directory, CONFIG_DIR, DATABASE_DIR, lookup_table)
        root.config_manager = config_manager  # Attach config_manager to root for access in on_exit

        create_button("Apply Changes", lambda: config_manager.apply_changes(ui_vars), "Apply the changes to the configuration files.")
        create_button("Save Preset", lambda: save_template(all_config_files, config_data, PRESETS_DIR), "Save the current configuration as a preset.")
        create_button("Load Preset", lambda: load_template(all_config_files, config_data, ui_vars, PRESETS_DIR), "Load a configuration preset.")
    except Exception as e:
        report_error("Error creating controls", e)

def on_exit(root, ui_vars, config_data, CONFIG_DIR, DATABASE_DIR, lookup_table):
    """Handle the window close event."""
    result = messagebox.askyesnocancel("Exit", "Do you want to apply current settings before exiting?")
    if result is None:
        return  # Cancel, do nothing
    elif result:
        config_manager = root.config_manager  # Use the same instance of ConfigManager
        config_manager.apply_changes(ui_vars)
    root.destroy()

if __name__ == "__main__":
    try:
        base_directory = get_base_directory()
        if not base_directory:
            logger.error("Base directory not set. Exiting.")
            messagebox.showerror("Error", "Base directory not set. Exiting.")
            sys.exit()

        CONFIG_DIR, DATABASE_DIR, PRESETS_DIR = initialize_directories(base_directory)

        required_files = load_file_content(resource_path(os.path.join('src', 'required_files.json')))
        if required_files is None:
            logger.error("Failed to load required files list.")
            messagebox.showerror("Error", "Failed to load required files list.")
            sys.exit()

        config_data = load_all_config_files(required_files, base_directory)

        metadata = load_file_content(resource_path(os.path.join('src', 'metadata.json')))
        if metadata is None:
            logger.error("Failed to load metadata file.")
            messagebox.showerror("Error", "Failed to load metadata file.")
            sys.exit()

        ui_vars = {relative_path: {} for relative_path in required_files if relative_path in config_data}

        lookup_table = create_lookup_table(metadata)

        create_main_ui(metadata, required_files, config_data, ui_vars, base_directory, CONFIG_DIR, DATABASE_DIR, PRESETS_DIR, lookup_table)
    except Exception as e:
        report_error("Error during main execution", e)
