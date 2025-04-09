import os
import requests

from dtneg_reader_utils import read_dtneg_file, parse_dtneg_file, tokenize_with_offsets_advanced, adjust_offsets

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))

def test_api():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"

    test_file = f"{BP}/data/DT-Neg corpus.zip"

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
    tp = f"{BP}/data/DT-Neg corpus.zip"
    with open(tp, 'rb') as f:
        content = f.read()
    files = read_dtneg_file(content)
    print(files.keys())
    # print(files['bioscope_full'])
    res = parse_dtneg_file(read_dtneg_file(content)['DT-Neg corpus'])
    print(res[3])
    print(10*"-")
    for sent in res[0]:
        print(res[3][sent.begin:sent.end])
    print(10 * "-")
    for tok in res[1]:
        print(res[3][tok.begin:tok.end])
    print(10 * "-")
    for neg in res[2]:
        print(res[3][neg.cue.begin:neg.cue.end])
    print(10 * "-")

    print(len(res[2]))


def test_adjust():
    original = "I built a house, but ca n't wo n't live in it ."
    tokens = tokenize_with_offsets_advanced(original) + [(17, 39)]
    replacements = [(" n't ", " not "), (" ca ", " can "), (" wo ", " will "), (" sha  ", " shall ")]

    print(original)
    print([original[tok[0]:tok[1]] for tok in tokens])
    new, new_tok = adjust_offsets(original, tokens, replacements)
    print(new)
    print([new[tok[0]:tok[1]] for tok in new_tok])


# Example usage
if __name__ == "__main__":
    # test_api()
    test_reading()
