import os
from pathlib import Path
import zipfile
import tempfile
import shutil
from io import BytesIO
from typing import Dict, Optional

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def find_folder_pathlib(zip_data, target_folder, temp_dir: Path):
    """
    Extract a zip file from bytes or BytesIO and recursively search for a folder within its contents.

    Args:
        zip_data (bytes or BytesIO): Zip file contents as bytes or BytesIO object
        target_folder (str): The name of the folder to find

    Returns:
        Path: Path object to the target folder if found, None if not found
        :param temp_dir:
    """

    try:
        if isinstance(zip_data, bytes):
            zip_data = BytesIO(zip_data)

        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        start_path = Path(temp_dir)
        if not start_path.exists() or not start_path.is_dir():
            return None

        for item in start_path.iterdir():
            if item.is_dir() and item.name == target_folder:
                return item
            elif item.is_dir():
                result = find_folder_pathlib_recursive(item, target_folder)
                if result:
                    return result
        return None

    except zipfile.BadZipFile:
        print("Error: Invalid zip data provided")
        return None
    except PermissionError:
        print("Permission denied during extraction or search")
        return None


def find_folder_pathlib_recursive(start_path, target_folder):
    """Helper function for recursive search"""
    try:
        for item in start_path.iterdir():
            if item.is_dir() and item.name == target_folder:
                return item
            elif item.is_dir():
                result = find_folder_pathlib_recursive(item, target_folder)
                if result:
                    return result
        return None
    except PermissionError:
        return None


def find_tsv_files(start_path, tsv_files_dict: Dict[str, str], temp_dir_base: Optional[Path] = None):
    """
    Find all .tsv files in a directory and its subdirectories, including nested zips,
    storing their contents in a dictionary by their containing folder.

    Args:
        start_path (str or Path): The starting directory path to begin the search
        temp_dir_base (str, optional): Base temporary directory for nested zip extraction

    Returns:
        dict: Dictionary with folder paths as keys and dicts of filename:contents as values
        :param tsv_files_dict:
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
            # Process .tsv files
            tsv_files = [f for f in files if f.lower().endswith('.tsv')]
            if tsv_files:
                # Store contents instead of just paths
                for file in tsv_files:
                    file_path = folder_path / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tsv_files_dict[str(file_path).split("/")[-2].split(".")[0]] = f.read()
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
                    find_tsv_files(nested_temp_dir, tsv_files_dict, temp_dir_base)
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