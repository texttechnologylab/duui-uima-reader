import os
import requests

from src.socc_utils import read_socc_negation, convert_tsv

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))


def test_method():
    # Example: Search for a folder named "target" starting from "C:/Users"
    zd = f"{BP}/data/sfu-opinion-and-comments-corpus-socc.zip"  # Replace with your starting path
    folder_to_find = "Negation_annotation"  # Replace with your target folder name

    # Example: Reading a zip file as bytes (replace with your actual bytes source)
    with open(zd, "rb") as f:  # Simulating bytes input
        zp = f.read()

    res = read_socc_negation(zp, folder_to_find)
    # print(len(res))
    # print(res.keys())
    for key in res:
        print(*convert_tsv(key, res[key]), sep="\n")
        break

def test_api():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/sfu-opinion-and-comments-corpus-socc.zip"

    file = {'file': open(test_file, 'rb')}
    response = requests.post(url=init_url, files=file)
    print(response.status_code)  # 201 (Created)
    response = response.json()
    print(response)

    for _ in range(response["n_docs"]):
        res_json = {}
        response = requests.post(url=next_url, json={}).json()
        # print(response["sofa_str"])
        # print(response["token"])
        print(response["doc_name"])

# Example usage
if __name__ == "__main__":
    test_api()