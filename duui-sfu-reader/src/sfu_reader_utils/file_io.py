import os
from pathlib import Path
import zipfile
import tempfile
import shutil
from io import BytesIO
from typing import Dict, Optional

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def replace_illegal_xml_chars(text: str) -> str:
    """
    Replace or remove illegal XML 1.0 characters from a string.

    Args:
        text (str): The input string to process.
        replacement (str): The string to replace illegal characters with (default: empty string).
                          Use None to replace with specific safe alternatives where applicable.

    Returns:
        str: The cleaned string with illegal characters replaced or removed.
    """
    # Define illegal ranges for XML 1.0
    illegal_ranges = [
        (0x00, 0x08),  # C0 control chars (excluding TAB, LF, CR)
        (0x0B, 0x0C),  # VT, FF
        (0x0E, 0x1F),  # SO to US
        (0x80, 0x9F),  # C1 control chars (e.g., 0x92, 0x93)
        (0xD800, 0xDFFF),  # Surrogate pairs
        (0xFFFE, 0xFFFF)  # Non-characters
    ]

    # Mapping for common C1 misencodings (e.g., Windows-1252 smart quotes)
    smart_quote_replacements = {
        '\x91': "'",  # Left single quote
        '\x92': "'",  # Right single quote
        '\x93': '"',  # Left double quote
        '\x94': '"',  # Right double quote
        '\x85': '...',  # Ellipsis
        '\x96': '-',  # En dash
        '\x97': '--'  # Em dash
    }

    result = []
    for char in text:
        code_point = ord(char)
        is_illegal = False

        # Check if the character falls in an illegal range
        for start, end in illegal_ranges:
            if start <= code_point <= end:
                is_illegal = True
                break

        if is_illegal:
            # If replacement is None, use smart quote mapping where applicable
            if char in smart_quote_replacements:
                result.append(smart_quote_replacements[char])
            else:
                result.append(" ")
        else:
            result.append(char)

    return ''.join(result)


def find_xml_files(start_path, xml_files_dict: Dict[str, str], dir_dict: Dict[str, int], temp_dir_base: Optional[Path] = None):
    """
    Find all .xml files in a directory and its subdirectories, including nested zips,
    storing their contents in a dictionary by their containing folder.

    Args:
        start_path (str or Path): The starting directory path to begin the search
        temp_dir_base (str, optional): Base temporary directory for nested zip extraction

    Returns:
        dict: Dictionary with folder paths as keys and dicts of filename:contents as values
        :param xml_files_dict:
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
            # Process .xml files
            xml_files = [f for f in files if f.lower().endswith('.xml')]
            if xml_files:
                # Store contents instead of just paths
                for file in xml_files:
                    file_path = folder_path / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            dir_name = str(file_path).split("/")[-2].split(".")[0]
                            if dir_dict.get(dir_name) is None:
                                dir_dict[dir_name] = 0
                            else:
                                dir_dict[dir_name] += 1

                            xml_files_dict[dir_name + "_" + str(dir_dict[dir_name])] = f.read()
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
                    find_xml_files(nested_temp_dir, xml_files_dict, dir_dict, temp_dir_base)
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