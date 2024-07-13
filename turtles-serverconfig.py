import json
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

# Function to get the resource path
def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Function to get the base directory
def get_base_directory():
    """Get the base directory where SPT_Data is located."""
    config_file = "config_dir.json"
    
    # Check if the configuration file exists
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            base_dir = config.get("base_directory")
            if base_dir and os.path.exists(base_dir):
                return base_dir
    
    # Prompt the user to select the base directory
    base_dir = filedialog.askdirectory(title="Select the base directory where SPT_Data is located")
    if base_dir:
        with open(config_file, 'w') as f:
            json.dump({"base_directory": base_dir}, f)
        return base_dir
    
    return None

# Get the base directory
base_directory = get_base_directory()
if not base_directory:
    messagebox.showerror("Error", "Base directory not set. Exiting.")
    sys.exit()

# Construct paths dynamically
CONFIG_DIR = os.path.join(base_directory, 'SPT_Data', 'Server', 'configs')
METADATA_PATH = resource_path(os.path.join('src', 'metadata.json'))
PRESETS_DIR = os.path.join(base_directory, 'user/mods/turtles-serverconfig/presets')

# Ensure the writable directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(PRESETS_DIR, exist_ok=True)  # Ensure presets directory exists

# List of configuration files
config_files = [
    'core.json', 'match.json', 'playerscav.json', 'pmc.json', 'pmcchatresponse.json', 
    'quest.json', 'ragfair.json', 'repair.json', 'scavcase.json', 'seasonalevents.json', 
    'trader.json', 'weather.json', 'hideout.json', 'http.json', 'inraid.json', 
    'insurance.json', 'inventory.json', 'item.json', 'locale.json', 'location.json', 
    'loot.json', 'lostondeath.json', 'airdrop.json', 'bot.json', 'btr.json', 'health.json'
]

# Load configuration from file
def load_config(filename):
    path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading {filename}: {e}")
        return None

# Save configuration to file
def save_config(filename, config_data):
    path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(path, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving {filename}: {e}")
        return False
    return True

# Save current configuration as a template
def save_template():
    template_filename = filedialog.asksaveasfilename(initialdir=PRESETS_DIR, defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if template_filename:
        template_data = {filename: config_data[filename] for filename in config_files}
        success = save_config_to_path(template_filename, template_data)
        if success:
            messagebox.showinfo("Info", "Template saved successfully!")

# Load configuration from a template
def load_template():
    template_filename = filedialog.askopenfilename(initialdir=PRESETS_DIR, filetypes=[("JSON files", "*.json")])
    if template_filename:
        template_data = load_config_from_path(template_filename)
        if template_data:
            for filename in config_files:
                if filename in template_data:
                    config_data[filename] = template_data[filename]
                    update_ui_from_config(filename)
            messagebox.showinfo("Info", "Template loaded successfully! - Don't Forget to APPLY!")

# Load configuration from a specific path
def load_config_from_path(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Error loading {path}: {e}")
        return None

# Save configuration to a specific path
def save_config_to_path(path, config_data):
    try:
        with open(path, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Error saving {path}: {e}")
        return False
    return True

# Update the UI components from the configuration data
def update_ui_from_config(filename):
    if filename in ui_vars:
        for option_path, var in ui_vars[filename].items():
            keys = option_path.split('.')
            current_value = config_data[filename]
            for key in keys:
                current_value = current_value[key]
            if isinstance(var, tk.BooleanVar):
                var.set(current_value)
            elif isinstance(var, tk.StringVar):
                var.set(str(current_value))

# Toggle the configuration option
def toggle_option(option_path, filename):
    keys = option_path.split('.')
    current_value = config_data[filename]
    for key in keys[:-1]:
        current_value = current_value[key]
    current_value[keys[-1]] = not current_value[keys[-1]]
    ui_vars[filename][option_path].set(current_value[keys[-1]])

# Update the configuration option
def update_option(option_path, filename, value):
    keys = option_path.split('.')
    current_value = config_data[filename]
    for key in keys[:-1]:
        current_value = current_value[key]
    current_value[keys[-1]] = value

# Apply the changes
def apply_changes():
    all_success = True
    for filename, options in ui_vars.items():
        for option_path, var in options.items():
            if isinstance(var, tk.BooleanVar):
                update_option(option_path, filename, var.get())
            elif isinstance(var, tk.StringVar):
                try:
                    if filename in metadata and option_path in metadata[filename]:
                        value_type = metadata[filename][option_path].get("type")
                        if value_type == "float":
                            value = float(var.get())
                        elif value_type == "int":
                            value = int(var.get())
                        else:
                            value = var.get()
                    else:
                        value = var.get()  # Assume string if metadata is missing
                    update_option(option_path, filename, value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for {option_path}: {var.get()}")
                    return
        success = save_config(filename, config_data[filename])
        if not success:
            all_success = False

    if all_success:
        messagebox.showinfo("Info", "All configurations saved successfully!")

# Create UI components dynamically
def create_ui_components(options, parent_frame, filename):
    for key, meta in options.items():
        option_path = key
        keys = option_path.split('.')
        current_value = config_data[filename]
        for k in keys:
            current_value = current_value[k]

        if isinstance(current_value, bool):
            var = tk.BooleanVar(value=current_value)
            checkbutton = tk.Checkbutton(parent_frame, text=meta["displayName"], variable=var, command=lambda op=option_path, fn=filename: toggle_option(op, fn))
            checkbutton.pack(pady=2)
            ui_vars[filename][option_path] = var
        elif isinstance(current_value, (int, float, str)):
            var = tk.StringVar(value=str(current_value))
            label = tk.Label(parent_frame, text=meta["displayName"])
            entry = tk.Entry(parent_frame, textvariable=var)
            label.pack(pady=2)
            entry.pack(pady=2)
            ui_vars[filename][option_path] = var
            if "description" in meta:
                desc_label = tk.Label(parent_frame, text=meta["description"], wraplength=300)
                desc_label.pack(pady=2)

# Load initial configurations
config_data = {filename: load_config(filename) for filename in config_files}
metadata = load_config_from_path(METADATA_PATH)
if None in config_data.values() or metadata is None:
    sys.exit()

# Initialize the main window
root = tk.Tk()
root.title("Turtles Server Config")

# Dictionary to store UI variables
ui_vars = {filename: {} for filename in config_files}

# Create a main frame
main_frame = tk.Frame(root)
main_frame.pack(pady=10, padx=10, fill="both", expand="yes")

# Create a notebook widget for tabs
notebook = ttk.Notebook(main_frame)
notebook.pack(pady=10, padx=10, fill="both", expand="yes")

# Create UI components dynamically for each tab in the metadata
for tab, files in metadata.items():
    tab_frame = ttk.Frame(notebook)
    notebook.add(tab_frame, text=tab)

    paned_window = ttk.PanedWindow(tab_frame, orient=tk.VERTICAL)
    paned_window.pack(pady=10, padx=10, fill="both", expand="yes")

    for filename, options in files.items():
        create_ui_components(options, paned_window, filename)

# Apply button
apply_button = tk.Button(main_frame, text="Apply", command=apply_changes)
apply_button.pack(pady=5)

# Template buttons
template_frame = tk.Frame(main_frame)
template_frame.pack(pady=5)

save_template_button = tk.Button(template_frame, text="Save Template", command=save_template)
save_template_button.pack(side=tk.LEFT, padx=5)

load_template_button = tk.Button(template_frame, text="Load Template", command=load_template)
load_template_button.pack(side=tk.LEFT, padx=5)

# Run the main loop
root.mainloop()
