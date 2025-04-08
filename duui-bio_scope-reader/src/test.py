import os
import requests

from bs_reader_utils import read_bs_file, parse_bs_file

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))

def test_api():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/bioscope-corpus-negation-annotated.zip"

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
        for neg in response["negations"]:
            print(response["sofa_str"][neg["cue"]["begin"]:neg["cue"]["end"]])


def test_reading():
    tp = f"{BP}/data/bioscope-corpus-negation-annotated.zip"
    with open(tp, 'rb') as f:
        content = f.read()
    files = read_bs_file(content)
    print(files.keys())
    # print(files['bioscope_full'])
    res = parse_bs_file(read_bs_file(content)['bioscope_full'])
    for neg in res[2]:
        print(neg)


# Example usage
if __name__ == "__main__":
    test_api()
