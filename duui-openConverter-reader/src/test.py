import os
from io import BytesIO
from tqdm import tqdm
import requests

from ocw import run_open_convert, FileIOUtils


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))


def test_single_corpus():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/test.zip"

    file = {'file': open(test_file, 'rb')}
    response = requests.post(url=init_url, files=file)
    print(response.status_code)  # 201 (Created)
    response = response.json()
    print(response)

    for _ in tqdm(range(response["n_docs"])):
        response = requests.post(url=next_url, json={}).json()
        print(response["sofa_str"])



if __name__ == "__main__":
    """test_file = f"{BP}/data/test.zip"
    # test_file = f"{BP}/data/file-sample_100kB.zip"
    file = open(test_file, 'rb')
    file = FileIOUtils.file_to_bytesio(file)

    run_open_convert(file)"""
    test_single_corpus()

