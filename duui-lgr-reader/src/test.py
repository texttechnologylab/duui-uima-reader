import os
import requests

from ar_reader_utils import read_ar_file, parse_ar_file, parse_ar_file_for_UCE

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))

def test_api():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/african_tex.zip"

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

        print(response["dalinks"])




def test_reading():
    tp = f"{BP}/data/african_tex.zip"
    with open(tp, 'rb') as f:
        content = f.read()
    files = read_ar_file(content)
    print(files.keys())
    # res = parse_ar_file(read_ar_file(content)['Akan'])
    res = parse_ar_file_for_UCE(read_ar_file(content)['Akan'])
    print(len(res), 174*4)

    print(res[4])
    print(res[5])
    print(res[6])
    print(res[7])




# Example usage
if __name__ == "__main__":
    test_api()
    # test_reading()
