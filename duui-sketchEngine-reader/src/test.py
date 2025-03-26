import io
import json
import os
import sys
from typing import List
import requests
from tqdm import tqdm



BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))


def test_single_corpus():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/se_example.zip"

    file = {'file': open(test_file, 'rb')}
    response = requests.post(url=init_url, files=file)
    print(response.status_code)  # 201 (Created)
    response = response.json()
    print(response)

    for _ in tqdm(range(response["n_docs"])):
        res_json = {}
        response = requests.post(url=next_url, json={}).json()
        print(response["sofa_str"])
        print(response["token"])
        print(response["doc_name"])


if __name__ == "__main__":
    test_single_corpus()

