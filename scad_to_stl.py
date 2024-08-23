import os
import subprocess
import json
import sys
from itertools import product

# Hardcoded path to the OpenSCAD executable
openscad_path = "C:\\Program Files\\OpenSCAD (Nightly)\\openscad.exe"  # Modify this path to your OpenSCAD installation

# Function to load configuration from a JSON file
def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file, object_pairs_hook=dict)  # Preserve order
    return config

# Function to sanitize filenames by removing invalid characters
def sanitize_filename(filename):
    return filename.replace("\"", "").replace(" ", "_")

# Check if a config file is passed as a command-line argument
if len(sys.argv) != 2:
    print("Usage: python generate_stls.py <config_file.json>")
    sys.exit(1)

# Load configuration
config_file = sys.argv[1]
config = load_config(config_file)

# Extract configuration variables
scad_file = config["scad_file"]
variables = config["variables"]
subfolder_format = config["subfolder_format"]
filename_format = config["filename_format"]
base_output_dir = config["base_output_dir"]

# Create the base output directory if it doesn't exist
os.makedirs(base_output_dir, exist_ok=True)

# Get the keys and ranges from the variables
keys = list(variables.keys())
ranges = [variables[key] for key in keys]

# Loop through all possible combinations of the specified variables
for combination in product(*ranges):
    # Create a dictionary of the current variable values
    current_vars = dict(zip(keys, combination))
    
    # Format the subfolder name based on the current variables
    subfolder_name = subfolder_format.format(**current_vars)
    subfolder_path = os.path.join(base_output_dir, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)
    
    # Format the filename based on the current variables, sanitize it for invalid characters
    output_filename = sanitize_filename(filename_format.format(**current_vars))
    output_path = os.path.join(subfolder_path, output_filename)
    
    # Build the OpenSCAD command with the variable definitions
    cmd = [openscad_path, "-o", output_path]
    for key, value in current_vars.items():
        # Add quotes around string values for OpenSCAD
        if isinstance(value, str):
            value = f'"{value}"'
        cmd.extend(["-D", f"{key}={value}"])
    cmd.append(scad_file)

    # Output the current variables and the OpenSCAD command
    print(f"\nGenerating STL with variables: {current_vars}")
    print(f"OpenSCAD Command: {' '.join(cmd)}")
    
    # Run the OpenSCAD command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating {output_filename}: {e}")
        continue

print("STL files generated and stored in respective subfolders successfully.")
