# turtles-serverconfig
Edit SPT Server Values


---

## Installation and Customization

### Installation

1. **Download and Extract**:
   - Download the latest release of the project from the GitHub releases page.
   - Extract the downloaded files.

2. **Install to Mod Folder**:
   - Copy the extracted files to your game's mod folder (typically located within your game's directory).

3. **Launch the Application**:
   - Run the executable (`main.py`).
   - When prompted, select the parent folder of `SPT_Data`.

### Usage

1. **Launch the GUI**:
   - Upon launching, the GUI will display.
   - The tabs and data displayed are dynamically created by parsing the `metadata.json` file.

2. **Changing Settings**:
   - Navigate through the tabs to find different settings.
   - You can change settings on any tab.
   - After making changes, click the "Apply" button to save all changes across all tabs.
   - **Note**: You do not need to apply each tab individually.

3. **Saving Presets**:
   - You can save the current configuration as a preset.
   - Only the options defined in the `metadata.json` file will be saved.
   - Be sure to apply after loading any presets to ensure changes take effect.

### Customization

1. **Modifying Metadata**:
   - You can customize the GUI by modifying the `metadata.json` file.
   - This file allows you to add more tabs, groups, and options dynamically.

2. **Adding New Config Files**:
   - To add a new config file:
     - Add the file to `required_files.json` with the appropriate format.
     - Update `metadata.json` to include the new options, following the existing format.

---

You can use the application with just the pythin files, or you comile your own exe with the program and command below.

cd "YOUR_FULL_PATH\user\mods\turtles-serverconfig"
pyinstaller --onefile --windowed --add-data "src;src" --add-data "YOUR_FULL_PATH/SPT_Data;SPT_Data" main.py
