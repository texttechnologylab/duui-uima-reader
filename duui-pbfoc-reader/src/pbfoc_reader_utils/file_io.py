import os
from pathlib import Path
import zipfile
import tempfile
import shutil
from io import BytesIO
from typing import Dict, Optional

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def find_pbfoc_files(start_path, pbfoc_files_dict: Dict[str, str], dir_dict: Dict[str, int], temp_dir_base: Optional[Path] = None):
    """
    Find all pbfoc files in a directory and its subdirectories, including nested zips,
    storing their contents in a dictionary by their containing folder.

    Args:
        start_path (str or Path): The starting directory path to begin the search
        temp_dir_base (str, optional): Base temporary directory for nested zip extraction

    Returns:
        dict: Dictionary with folder paths as keys and dicts of filename:contents as values
        :param temp_dir_base:
        :param dir_dict:
        :param start_path:
        :param pbfoc_files_dict:
    """
    start_path = Path(start_path)

    # Use provided temp_dir_base or create a new one

    if not start_path.exists() or not start_path.is_dir():
        return

    if temp_dir_base is None:
        temp_dir_base = Path(tempfile.mkdtemp())

    try:
        for root, _, files in os.walk(start_path):
            folder_path = Path(root)
            # Process .pbfoc files
            pbfoc_files = [f for f in files if f.lower().endswith('.merged')]
            if pbfoc_files:
                # Store contents instead of just paths
                for file in pbfoc_files:
                    file_path = folder_path / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            pbfoc_files_dict[str(file_path).split("/")[-1].replace(".merged", "")] = f.read()
                    except Exception as e:
                        print(e)

            # Process nested .zip files
            zip_files = [f for f in files if f.lower().endswith('.zip')]
            for zip_file in zip_files:
                zip_path = folder_path / zip_file
                nested_temp_dir = tempfile.mkdtemp(dir=temp_dir_base)
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(nested_temp_dir)
                    # Recursively process the extracted contents
                    find_pbfoc_files(nested_temp_dir, pbfoc_files_dict, dir_dict, temp_dir_base)
                except zipfile.BadZipFile:
                    print(f"Skipping invalid nested zip: {zip_path}")
                finally:
                    shutil.rmtree(nested_temp_dir, ignore_errors=True)

        return

    except PermissionError:
        print(f"Permission denied accessing some directories in {start_path}")
        return
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return
    finally:
        if temp_dir_base == Path(temp_dir_base):  # Only clean up if we created it
            shutil.rmtree(temp_dir_base, ignore_errors=True)