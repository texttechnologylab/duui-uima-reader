import io
import os
import pathlib
import zipfile
from abc import ABC
from http.client import HTTPException
from io import BytesIO
from typing import Union, List, Dict


class FileIOUtils(ABC):
    @staticmethod
    def file_to_bytesio(file) -> BytesIO:
        try:
            # Accumulate the file content in memory
            buffer = BytesIO()
            while True:
                chunk = file.read(1024 * 1024 * 10) # 10 MB chunks
                if chunk:
                    buffer.write(chunk)
                else:
                    break

            # Reset pointer to the beginning before opening with ZipFile
            buffer.seek(0)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

        return buffer

    @staticmethod
    def save_zip_file(zip_bytes: BytesIO, output_path: str, chunk_size: int = 32000):
        zip_bytes.seek(0)
        with open(output_path, "wb") as f:
            while True:
                chunk = zip_bytes.read(chunk_size)
                if not chunk:  # End of BytesIO
                    break
                f.write(chunk)

    @staticmethod
    def save_file_from_zip(zip_ref: zipfile.ZipFile, fileref: str, output_file: str):
        # Extract the specific file to the output_path
        with zip_ref.open(fileref) as source_file:
            with open(output_file, "wb") as target_file:
                target_file.write(source_file.read())

    @staticmethod
    def find_all_files_in_zip(zip_ref_lst: List[str], temp_path: str, zip_ref: zipfile.ZipFile):

        endings = ["txt", "tei", "alto", "doc", "docx", "html"]
        for file in zip_ref_lst:
            ending = file.lower().split(".")[-1]
            if ending in endings:
                pathlib.Path(f"{temp_path}/{ending}/").mkdir(exist_ok=True)
                FileIOUtils.save_file_from_zip(zip_ref, file, f"{temp_path}/{ending}/{file.split('/')[-1]}")
            else:
                pass

    @staticmethod
    def files_from_zip_in_bytes(zip_bytes: Union[bytes, BytesIO], temp_path: str):

        # Use BytesIO to treat the byte data as a file-like object
        # with BytesIO(zip_bytes) as byte_io:
        if isinstance(zip_bytes, bytes):
            byte_io = BytesIO(zip_bytes)
            del zip_bytes
        else:
            byte_io = zip_bytes

        with zipfile.ZipFile(byte_io, 'r') as zip_ref:
            # List all file names in the zip file
            # print("Files in the ZIP archive:", zip_ref.namelist())
            FileIOUtils.find_all_files_in_zip(zip_ref.namelist(), temp_path, zip_ref)
            for file in zip_ref.namelist():
                if ".zip" in file:
                    with zip_ref.open(file) as zf:
                        file_contents = zf.read()
                    FileIOUtils.files_from_zip_in_bytes(file_contents, temp_path)

    @staticmethod
    def change_extensions(directory, new_ext):
        # Ensure new_ext starts with a dot
        if not new_ext.startswith('.'):
            new_ext = '.' + new_ext

        # Iterate through all files in the directory
        for filename in os.listdir(directory):
            # Get full path
            old_path = os.path.join(directory, filename)

            # Skip directories
            if os.path.isdir(old_path):
                continue

            # Split the filename and extension
            base, old_extension = os.path.splitext(filename)
            # Create new filename with new extension
            new_filename = base + "_" + old_extension.strip(".") + new_ext
            new_path = os.path.join(directory, new_filename)

            # Rename the file
            os.rename(old_path, new_path)
            # print(f"Renamed: {filename} -> {new_filename}")

    @staticmethod
    def remove_unknown_line(directory):
        # Loop through all files in the directory
        for filename in os.listdir(directory):
            # Check if file ends with .txt
            if not filename.lower().endswith('.txt'):
                continue

            file_path = os.path.join(directory, filename)

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Check if there's at least one line and it starts with "unknown"
            if lines and lines[0].lower().startswith('unknown'):
                # Remove the first line
                lines = lines[1:]

                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(lines)
            else:
                pass