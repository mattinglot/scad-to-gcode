import os
import json
import subprocess
import sys

def load_settings(settings_file):
    with open(settings_file, 'r') as f:
        return json.load(f)

def process_stls_with_prusaslicer(prusaslicer_path, base_project_file, stl_folder, output_folder):
    # Loop through each STL file in the folder and its subfolders
    for root, _, files in os.walk(stl_folder):
        for stl_file in files:
            if stl_file.endswith('.stl'):
                stl_path = os.path.join(root, stl_file)
                
                # Create the corresponding output subfolder structure
                relative_path = os.path.relpath(root, stl_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)

                output_gcode = os.path.join(output_subfolder, f"{os.path.splitext(stl_file)[0]}.gcode")

                # Command to slice the STL directly with settings from the base project file
                slice_command = [
                    prusaslicer_path,
                    stl_path,
                    '--load', base_project_file,
                    '--export-gcode',
                    '--output', output_gcode
                ]

                print(f"Running: {' '.join(slice_command)}")
                result = subprocess.run(slice_command, check=False)

                # Check if the file was created
                if result.returncode == 0 and os.path.exists(output_gcode):
                    print(f"Successfully processed {stl_file} -> {output_gcode}")
                else:
                    print(f"Failed to process {stl_file}: G-code file not created.")

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

    process_stls_with_prusaslicer(prusaslicer_path, base_project_file, stl_folder, output_folder)
