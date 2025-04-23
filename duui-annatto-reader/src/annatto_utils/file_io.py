import os
from pathlib import Path
import zipfile
import tempfile
import shutil
from io import BytesIO
from typing import Dict, Optional, Union, List, Any
import zipfile
import io
import os
import tempfile


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def unzip(zip_content: Union[BytesIO, bytes]) -> tuple[str, list[str]]:
    """
    -
    :param zip_content:
    :return:
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(dir=f"{BP}/temp")
    toml_sources = []

    def extract_zip(content: Union[BytesIO, bytes], extract_to: str, toml: List[str]):
        """
        -
        :param content:
        :param extract_to:
        :param toml:
        :return:
        """
        # Create a BytesIO object to read the zip content
        if isinstance(content, BytesIO):
            pass
        else:
            content = BytesIO(content)
        try:
            with zipfile.ZipFile(content, 'r') as zf:
                # Extract all files to the specified directory
                zf.extractall(extract_to)

                # Check each extracted file for nested zips
                for file_name in zf.namelist():
                    file_path = os.path.join(extract_to, file_name)
                    # If the file is a zip, recursively extract it
                    if os.path.isfile(file_path) and file_name.lower().endswith('.zip'):
                        with open(file_path, 'rb') as f:
                            nested_content = f.read()
                        # Recursively extract the nested zip
                        os.mkdir(file_path.rstrip(".zip"))
                        extract_zip(nested_content, file_path.rstrip(".zip"), toml)
                        # Optionally, remove the nested zip file after extraction
                        os.remove(file_path)
                    elif os.path.isfile(file_path) and file_name.lower().endswith('.toml'):
                        # print(file_path)
                        toml.append(file_path)

        except zipfile.BadZipFile:
            # Skip files that are not valid zip files
            pass

    # Start the extraction process with the initial zip content
    extract_zip(zip_content, temp_dir + "/inp", toml_sources)

    return temp_dir, toml_sources


def find_conllu_files(directory: str) -> list[str]:
    """
    Recursively find all .conllu files in the given directory and its subdirectories,
    regardless of depth, and return their absolute paths.

    Args:
        directory (str): Path to the directory to search.

    Returns:
        list[str]: List of absolute paths to .conllu files.
    """
    conllu_files = []

    # Recursively walk through the directory and all subdirectories
    for root, _, files in os.walk(directory):
        # Check each file in the current directory
        for file in files:
            # Check if the file ends with .conllu (case-insensitive)
            if file.lower().endswith('.conllu'):
                # Construct the full absolute path
                file_path = os.path.join(root, file)
                conllu_files.append(os.path.abspath(file_path))

    return conllu_files


def walk_directories(directory: str) -> list[str]:
    """
    Recursively walk through all directories in the given directory and return their paths.

    Args:
        directory (str): Path to the starting directory.

    Returns:
        list[str]: List of absolute paths to all directories (including the root and subdirectories).
    """
    directories = []

    # Ensure the directory exists
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")

    # Walk through the directory tree
    for root, dirs, _ in os.walk(directory):
        # Add the current root directory
        directories.append(os.path.abspath(root))
        # Note: dirs contains subdirectories in the current root, but we don't need to process them
        # separately since os.walk() will visit them automatically

    return directories


if __name__ == "__main__":
    """with open(f"{BP}/data/test_data/reader_test/reader_test_in/inp.zip", 'rb') as fp:
        content = fp.read()
    temp_dir, toml_sources = unzip(content)
    print(toml_sources)
    print(temp_dir)"""

    print(*find_conllu_files(f"{BP}/data/test_data/output"), sep="\n")