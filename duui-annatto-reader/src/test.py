import os
import requests

from annatto_utils import annatto_main
from annatto_utils.annatto_reader import conllu_to_doc

from annatto_utils.file_io import unzip

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))

def test_api():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/test_data/reader_test/reader_test_in/inp.zip"

    file = {'file': open(test_file, 'rb')}
    response = requests.post(url=init_url, files=file)
    print(response.status_code)  # 201 (Created)
    response = response.json()
    print(response)

    for _ in range(response["n_docs"]):
        res_json = {}
        response = requests.post(url=next_url, json={}).json()
        print(response["sofa_str"])
        # print(response["token"])



def test_reading():
    with open(f"{BP}/data/test_data/reader_test/reader_test_in/inp.zip", 'rb') as fp:
        content = fp.read()
    res = annatto_main(content)
    print(len(res))


# Example usage
if __name__ == "__main__":
    test_api()
