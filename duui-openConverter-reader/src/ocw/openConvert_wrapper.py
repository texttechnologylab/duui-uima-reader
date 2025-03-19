import os
import pathlib
import shutil
import subprocess
from io import BytesIO
from typing import List

from .file_io_utils import FileIOUtils


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def run_open_convert(zip_bytes: BytesIO) -> List[str]:
    try:
        os.rmdir(f"{BP}/temp")
    except:
        try:
            shutil.rmtree(f"{BP}/temp")
        except:
            pass
    temp_out = f"{BP}/temp/temp_out"
    temp_in = f"{BP}/temp/temp_in"
    pathlib.Path(temp_in).mkdir(exist_ok=False, parents=True)
    pathlib.Path(temp_out).mkdir(exist_ok=True)

    FileIOUtils.files_from_zip_in_bytes(zip_bytes, temp_in)
    # Define the command components
    jar_path = f"{BP}/OpenConvert/dist/OpenConvert.jar"
    output_format = "txt"

    for input_format in os.listdir(temp_in):
        temp_in_dir = f"{temp_in}/{input_format}"
        command = [
            "java", "-jar", jar_path,
            "-from", input_format,
            "-to", output_format,
            temp_in_dir, temp_out
        ]
        # Execute the command
        subprocess.run(command, check=True)

    FileIOUtils.change_extensions(temp_out, output_format)

    if output_format == "txt":
        FileIOUtils.remove_unknown_line(temp_out)

    try:
        os.rmdir(temp_in)
    except:
        try:
            shutil.rmtree(temp_in)
        except:
            pass
    return [os.path.join(temp_out, file_name) for file_name in os.listdir(temp_out)]


if __name__ == "__main__":
    print(BP)