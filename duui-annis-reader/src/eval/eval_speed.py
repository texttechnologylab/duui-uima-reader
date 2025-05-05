import time
import os
import subprocess

from annis_utils import files_from_zip_in_bytes, ANNISExtractor

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))

import zipfile


def zip_directories_in_directory(source_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all entries in the source directory
    for entry in os.listdir(source_dir):
        entry_path = os.path.join(source_dir, entry)

        # Check if the entry is a directory
        if os.path.isdir(entry_path):
            # Define the output zip file name (e.g., "mydir" -> "mydir.zip")
            zip_filename = f"{entry}.zip"
            zip_path = os.path.join(output_dir, zip_filename)

            # Create a zip file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through the directory and add all files/subdirs
                for root, _, files in os.walk(entry_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Calculate the arcname to preserve directory structure
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)

            print(f"Created {zip_path}")


def meassure_speed_annis_og(fp: str):
    s = time.time()
    #command = f"/home/staff_homes/lehammer/Downloads/graphannis-cli-x86_64-unknown-linux-gnu/annis ./data -c 'import {fp}'"
    #result = subprocess.run(command, shell=True, capture_output=True, text=True)
    command = [
        "/home/staff_homes/lehammer/Downloads/graphannis-cli-x86_64-unknown-linux-gnu/annis",
        "/home/staff_homes/lehammer/Downloads/graphannis-cli-x86_64-unknown-linux-gnu/data",
        "-c",
        f"import {fp}"
    ]

    # Run the command without shell=True
    result = subprocess.run(command, capture_output=True, text=True)
    e = time.time()
    return e - s

def meassure_speed_annis_annatto(fp: str):
    s = time.time()
    #command = f"/home/staff_homes/lehammer/Downloads/graphannis-cli-x86_64-unknown-linux-gnu/annis ./data -c 'import {fp}'"
    #result = subprocess.run(command, shell=True, capture_output=True, text=True)
    with open("/home/staff_homes/lehammer/Documents/work/AnnisReader/data/annatto-x86_64-unknown-linux-gnu/temp.toml", "w") as f:
        f.write("[[import]]\n")
        f.write('format = "relannis"\n')
        f.write(f'path = "{fp}"\n')
        f.write("\n")
        f.write('[import.config]')

    command = [
        "/home/staff_homes/lehammer/Documents/work/AnnisReader/data/annatto-x86_64-unknown-linux-gnu/annatto",
        "run",
        "/home/staff_homes/lehammer/Documents/work/AnnisReader/data/annatto-x86_64-unknown-linux-gnu/temp.toml"
    ]

    # Run the command without shell=True
    result = subprocess.run(command, capture_output=True, text=True)
    e = time.time()
    return e - s

def meassure_speed_annis_new(fp: str):
    s = time.time()
    annis_corpus = ANNISExtractor.from_str_path(fp)
    apd, tpd = annis_corpus.extract_annotations(*annis_corpus.extract_text())
    e = time.time()
    return e - s


def get_file_size(file_path):
    # Get size in bytes
    size_bytes = os.path.getsize(file_path)

    # Convert to human-readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


def get_file_sizeMB(file_path):
    # Get size in bytes
    size_bytes = os.path.getsize(file_path)

    # Convert directly to MB (1 MB = 1024 * 1024 bytes)
    size_mb = size_bytes / (1024.0 * 1024.0)

    # Return formatted as MB with 2 decimal places
    return f"{size_mb:.2f} MB"


if __name__ == '__main__':
    """zfp1 = f"{BP}/data/test_data/DDD-AD-Genesis.zip"
    zfp2 = "/home/staff_homes/lehammer/Documents/work/AnnisReader/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/DDD-AD-Genesis"
    meassure_speed_annis_og(zfp1)
    meassure_speed_annis_new(zfp2)"""
    base_dir_uz = f"{BP}/data/test_data/speed/speed_data_unzip"
    base_dir_z = f"{BP}/data/test_data/speed/speed_data_zip"

    with open(f"{BP}/data/test_data/speed/test_results01.txt", "w") as f:
        for dr in os.listdir(base_dir_uz):
            try:
                dru = os.path.join(base_dir_uz, dr)
                drz = os.path.join(base_dir_z, f"{dr}.zip")
                uzr = meassure_speed_annis_new(dru)
                zr = meassure_speed_annis_og(drz)
                azr = meassure_speed_annis_annatto(dru)
                result = f"NAME: {dr} :: ANNIS: {zr} :: ANNATTO :: {azr} OWN: {uzr} :: FILE-SIZE: {get_file_sizeMB(drz)}"
                print(result)
                f.write(result + "\n")
            except Exception as e:
                print(e)
                pass

