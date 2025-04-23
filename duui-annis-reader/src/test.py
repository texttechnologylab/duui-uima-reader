import io
import json
import os
import sys
from typing import List
import requests
import pandas as pd
from tqdm import tqdm

from duui_annis_reader import DUUIRequest

BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../.."))


def test_single_corpus():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"
    # test_file = f"{BP}/data/test_data/DDD-AD-Benediktiner_Regel.zip"
    # test_file = f"{BP}/data/test_data/DDD-AD-Benediktiner_Regel_Latein.zip"
    test_file = f"{BP}/data/test_data/DDD-AD-Genesis.zip"
    # test_file = f"{BP}/data/test_data/DDD-AD-Z-Notker-Psalmen.zip"

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
        print(response["lemma"])
        # print(response["meta_data"])
        """for key in response:
            if key in ["sofa_str", "accepted"]:
                pass
            else:
                res_json[key] = [anno["value"] for anno in response[key]]

        with open(f"{BP}/data/dump/example_annotation_values.json", "w", encoding="utf-8") as jf:
            json.dump(response, jf, ensure_ascii=False, indent=4)"""


def test_multiple_corpora():
    init_url = "http://0.0.0.0:9714/v1/init"
    next_url = "http://0.0.0.0:9714/v1/process"
    # test_file = f"{BP}/data/test_data/relannis-v1.2.zip"
    # test_file = f"{BP}/data/test_data/notker.zip"
    test_file = f"{BP}/data/test_data/ref-mlu.zip"

    file = {'file': open(test_file, 'rb')}
    response = requests.post(url=init_url, files=file)
    print(response.status_code)  # 201 (Created)
    response = response.json()
    print(response)

    for _ in tqdm(range(response["n_docs"])):
        response = requests.post(url=next_url, json={}).json()
        print(response["sofa_str"])
        print(response["token"])


def test_upload():
    up_url = "http://0.0.0.0:9714/v1/upload"
    file = {'file': open(f"{BP}/data/test_data/DDD-AD-Benediktiner_Regel.zip", 'rb')}
    resp = requests.post(url=up_url, files=file)
    print(resp.json())

def max_worker_recommendation():
    def get_available_memory():
        """Estimate available memory in bytes."""
        if sys.platform.startswith("linux"):
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) * 1024  # KB to bytes
        elif sys.platform.startswith("win"):
            try:
                import psutil  # Requires 'pip install psutil'
                return psutil.virtual_memory().available
            except ImportError:
                print("Install 'psutil' for accurate memory info on Windows")
        # Fallback: Assume 1 GB
        return 1 * 1024 * 1024 * 1024

    def estimate_max_workers(io_bound_factor=5, stack_size=None):
        """Estimate max_workers for ThreadPoolExecutor."""
        # CPU count (logical CPUs)
        cpu_count = os.cpu_count() or 1  # Fallback to 1 if None

        # Default stack size per thread (in bytes)
        default_stack_size = 8 * 1024 * 1024 if sys.platform.startswith("linux") else 1 * 1024 * 1024
        stack_size = stack_size or default_stack_size

        # Available memory
        available_memory = get_available_memory()

        # Memory-based max threads
        memory_based_max = available_memory // stack_size

        # I/O-bound heuristic (e.g., cpu_count * 5)
        io_bound_max = cpu_count * io_bound_factor

        # Practical maximum: balance memory and I/O needs, cap for sanity
        practical_max = min(memory_based_max, io_bound_max, 1000)

        print({
            "cpu_count": cpu_count,
            "available_memory_mb": available_memory / (1024 * 1024),
            "stack_size_mb": stack_size / (1024 * 1024),
            "memory_based_max": memory_based_max,
            "io_bound_max": io_bound_max,
            "recommended_max_workers": practical_max
        })

    estimate_max_workers()

if __name__ == "__main__":
    test_single_corpus()