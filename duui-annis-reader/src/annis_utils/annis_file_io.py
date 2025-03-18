import io
import zipfile
from io import StringIO, BytesIO
from typing import Any, List, Union


def file_io_from_request(content: Any) -> Union[StringIO, BytesIO]:
    """
    Returns any given content as file like objects.
    :param content:
    :return:
    """
    if isinstance(content, str):
        return io.StringIO(content)
    elif isinstance(content, bytes):
        return io.BytesIO(content)
    else:
        raise Exception("wrong input datatype")


def read_file_as_byte(file_ref: str, zip_ref: zipfile.ZipFile) -> BytesIO:
    """
    read zyp file as bytes and return them in file like byte buffer.
    :param file_ref:
    :param zip_ref:
    :return:
    """
    with zip_ref.open(file_ref) as file:
        file_contents = file.read()  # Read file contents as bytes
        return BytesIO(file_contents)


def find_all_annis_corpora(zip_ref_lst: List[str]):
    """
    Find all relevant annis files in a given .zip file. Can also find multiple annis corpora
    in the gven .zip files.
    :param zip_ref_lst:
    :return:
    """
    annis_files = [ref for ref in zip_ref_lst if ".annis" in ref]
    corpora = dict()
    for file in annis_files:
        if "node.annis" in file or "node_annotation.annis" in file or "corpus.annis" in file or "corpus_annotation.annis" in file or "text.annis" in file:
            if corpora.get("/".join(file.split("/")[:-1])):
                corpora["/".join(file.split("/")[:-1])].append(file)
            else:
                corpora["/".join(file.split("/")[:-1])] = [file]
        else:
            pass
    return corpora


def files_from_zip_in_bytes(zip_bytes: Union[bytes, BytesIO], corpora_dict: dict):
    """
    Find all relevant annis files in a given .zip file. Can also find multiple annis corpora
    in the gven .zip files.
    :param zip_bytes:
    :param corpora_dict:
    :return:
    """
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
        corpora = find_all_annis_corpora(zip_ref.namelist())
        for key in corpora:
            corpora_dict[key] = {file.split("/")[-1]: read_file_as_byte(file, zip_ref) for file in corpora[key]}
        for file in zip_ref.namelist():
            if ".zip" in file:
                with zip_ref.open(file) as zf:
                    file_contents = zf.read()
                files_from_zip_in_bytes(file_contents, corpora_dict)



if __name__ == "__main__":
    test_file = "/home/staff_homes/lehammer/Downloads/DDD-AD-Benediktiner_Regel.zip"
    # test_file = "/home/staff_homes/lehammer/Downloads/relannis-v1.2.zip"

    with open(test_file, 'rb') as f:
        zb = f.read()

    corpora_lst = dict()
    files_from_zip_in_bytes(zb, corpora_lst)
    for key in corpora_lst:
        print(key, corpora_lst[key])

