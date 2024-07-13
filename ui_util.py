import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
import logging
from error_reporting import report_error

logger = logging.getLogger(__name__)

def update_ui_from_config(filename: str, ui_vars: Dict[str, Any], config_data: Dict[str, Any]) -> None:
    if filename in ui_vars:
        for option_path, var in ui_vars[filename].items():
            value = get_nested_value(config_data[filename], option_path.split('.'))
            set_variable_value(var, value)

def get_nested_value(data: Dict[str, Any], keys: [str]) -> Any:
    try:
        for key in keys:
            data = data[key]
        return data
    except KeyError as e:
        logger.error(f"KeyError accessing {'.'.join(keys)} in {data}: {e}")
        logger.error(f"Available keys in data: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        raise
    except TypeError as e:
        logger.error(f"TypeError accessing {'.'.join(keys)} in {data}: {e}")
        raise

def set_variable_value(var: tk.Variable, value: Any) -> None:
    var.set(value if isinstance(var, tk.BooleanVar) else str(value))

def toggle_option(option_path: str, filename: str, config_data: Dict[str, Any], ui_vars: Dict[str, Any]) -> None:
    keys = option_path.split('.')
    data = config_data[filename]
    for key in keys[:-1]:
        data = data[key]
    data[keys[-1]] = not data[keys[-1]]
    ui_vars[filename][option_path].set(data[keys[-1]])

def create_ui_components(options: Dict[str, Any], parent_frame: tk.Frame, config_data: Dict[str, Any], ui_vars: Dict[str, Any], toggle_option, lookup_table: Dict[str, str]) -> None:
    errors = []
    for option_path, meta in options.items():
        filename = lookup_table.get(option_path)
        if not filename:
            error_msg = f"No filename found for option path {option_path}. It may be missing or misspelled."
            logger.error(error_msg)
            errors.append(error_msg)
            continue
        try:
            if filename not in config_data or config_data[filename] is None:
                raise FileNotFoundError(f"Configuration file not loaded: {filename}")
            value = get_nested_value(config_data[filename], option_path.split('.'))
        except (KeyError, FileNotFoundError, TypeError) as e:
            error_msg = f"Failed to get value for {option_path} in {filename}. It may be missing or misspelled."
            logger.error(error_msg)
            errors.append(error_msg)
            continue
        var = create_variable(value)
        ui_vars[filename][option_path] = var
        create_component(parent_frame, meta, var, option_path, filename, toggle_option, config_data, ui_vars)
    if errors:
        messagebox.showwarning("Warning", "\n".join(errors))

def create_variable(value: Any) -> tk.Variable:
    return tk.BooleanVar(value=value) if isinstance(value, bool) else tk.StringVar(value=str(value))

def create_component(parent_frame: tk.Frame, meta: Dict[str, Any], var: tk.Variable, option_path: str, filename: str, toggle_option, config_data: Dict[str, Any], ui_vars: Dict[str, Any]) -> None:
    frame = ttk.Frame(parent_frame)
    frame.pack(fill="x", pady=2)
    if isinstance(var, tk.BooleanVar):
        comp = tk.Checkbutton(frame, text=meta["displayName"], variable=var, command=lambda: toggle_option(option_path, filename, config_data, ui_vars))
    else:
        ttk.Label(frame, text=meta["displayName"], anchor="w").pack(side="left", padx=5)
        comp = tk.Entry(frame, textvariable=var, width=30)
    comp.pack(side="left")
    if "description" in meta:
        create_tooltip(comp, meta["description"])

def create_grouped_ui(tab_name: str, group_options: Dict[str, Any], notebook: ttk.Notebook, filename: str, config_data: Dict[str, Any], ui_vars: Dict[str, Any], toggle_option, lookup_table: Dict[str, str]) -> None:
    tab_frame = ttk.Frame(notebook)
    notebook.add(tab_frame, text=tab_name)

    for group_name, options in group_options.items():
        group_frame = ttk.Frame(tab_frame)
        group_frame.pack(fill="x", padx=10, pady=5)

        group_title_frame = ttk.Frame(group_frame)
        group_title_frame.pack(fill="x")

        content_frame = ttk.Frame(group_frame)
        content_frame.pack(fill="x", padx=5, pady=5)

        toggle_button = ttk.Button(group_title_frame, text="Hide")
        toggle_button.pack(side="right", padx=5, pady=5)

        def create_toggle_command(cf=content_frame, tb=toggle_button):
            return lambda: toggle_group(cf, tb)

        toggle_button.config(command=create_toggle_command(content_frame, toggle_button))

        group_title = ttk.Label(group_title_frame, text=group_name, font=("Arial", 12, "bold"))
        group_title.pack(side="left", padx=5, pady=5)
        group_title.bind("<Button-1>", lambda e, cf=content_frame, tb=toggle_button: toggle_group(cf, tb))

        create_ui_components(options, content_frame, config_data, ui_vars, toggle_option, lookup_table)

def toggle_group(content_frame: ttk.Frame, toggle_button: ttk.Button) -> None:
    if content_frame.winfo_ismapped():
        content_frame.pack_forget()
        toggle_button.config(text="Show")
    else:
        content_frame.pack(fill="x", padx=5, pady=5)
        toggle_button.config(text="Hide")

def create_tooltip(widget: tk.Widget, text: str) -> None:
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.withdraw()

    label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
    label.pack()

    def show_tooltip(event):
        x = event.x_root + 10
        y = event.y_root + 10
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

# Assuming lookup_table is populated elsewhere in the code and is available globally
lookup_table = {}
