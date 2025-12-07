import os
import json
import subprocess
import sys

def load_settings(settings_file):
    with open(settings_file, 'r') as f:
        settings = json.load(f)
        # If supported_extensions isn't specified, use defaults
        if 'supported_extensions' not in settings:
            settings['supported_extensions'] = ['.stl', '.step']
        # If specified, ensure all extensions start with a dot
        else:
            settings['supported_extensions'] = [
                f".{ext.lower().lstrip('.')}" for ext in settings['supported_extensions']
            ]
        # Set default for ignore_if_gcode_exists if not specified
        if 'ignore_if_gcode_exists' not in settings:
            settings['ignore_if_gcode_exists'] = False
            
        return settings

def process_stls_with_prusaslicer(prusaslicer_path, base_project_file, stl_folder, output_folder, 
                                supported_extensions, ignore_if_gcode_exists):
    # Loop through each file in the folder and its subfolders
    for root, _, files in os.walk(stl_folder):
        for input_file in files:
            file_ext = os.path.splitext(input_file)[1].lower()
            if file_ext in supported_extensions:
                file_path = os.path.join(root, input_file)
               
                # Create the corresponding output subfolder structure
                relative_path = os.path.relpath(root, stl_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)
                output_gcode = os.path.join(output_subfolder, f"{os.path.splitext(input_file)[0]}.gcode")

                # Check if gcode exists and should be skipped
                if ignore_if_gcode_exists and os.path.exists(output_gcode):
                    print(f"Skipping {input_file} - G-code already exists at {output_gcode}")
                    continue

                # Command to slice the file directly with settings from the base project file
                slice_command = [
                    prusaslicer_path,
                    file_path,
                    '--load', base_project_file,
                    '--export-gcode',
                    '--output', output_gcode
                ]
                print(f"Running: {' '.join(slice_command)}")
                result = subprocess.run(slice_command, check=False)

                # Check if the file was created
                if result.returncode == 0 and os.path.exists(output_gcode):
                    print(f"Successfully processed {input_file} -> {output_gcode}")
                else:
                    print(f"Failed to process {input_file}: G-code file not created.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python stl_to_gcode.py <settings.json>")
        sys.exit(1)

    settings_file = sys.argv[1]
    # Load settings from the JSON file
    settings = load_settings(settings_file)
    prusaslicer_path = settings["prusaslicer_path"]
    base_project_file = settings["base_project_file"]
    stl_folder = settings["stl_folder"]
    output_folder = settings["output_folder"]
    supported_extensions = settings["supported_extensions"]
    ignore_if_gcode_exists = settings["ignore_if_gcode_exists"]

    print(f"Processing files with extensions: {', '.join(supported_extensions)}")
    print(f"Ignore existing G-code files: {ignore_if_gcode_exists}")
    
    process_stls_with_prusaslicer(
        prusaslicer_path,
        base_project_file,
        stl_folder,
        output_folder,
        supported_extensions,
        ignore_if_gcode_exists
    )