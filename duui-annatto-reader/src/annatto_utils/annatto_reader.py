import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Union
import os

from conllu import parse_incr

from .file_io import unzip, find_conllu_files, walk_directories
from .annotations import Token
BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


def conllu_to_doc(conllu_path: str):
    data_file = open(conllu_path, "r", encoding="utf-8")
    offset = 0
    sofa = []
    tokens = []
    for tokenlist in parse_incr(data_file):
        for token in tokenlist:
            tokens.append(Token(begin=offset, end=offset+len(token["form"]), value=token["form"]))
            offset += len(token["form"]) + 1
            sofa.append(token["form"])
    return tokens, " ".join(sofa)


def annatto_main(zip_bytes: Union[bytes, BytesIO]):
    temp_dir, toml_sources = unzip(zip_bytes)
    temp_dir_in = temp_dir + "/inp"
    temp_dir_out = temp_dir + "/out"
    os.mkdir(temp_dir_out)

    if len(toml_sources) > 1:
        raise Exception("Multiple toml templates found!!!")
    else:
        with open(toml_sources[0], 'r') as fp:
            toml_template_base = fp.read()


        target_dirs = walk_directories(temp_dir_in)
        for idx, target_dir in enumerate(target_dirs):
            toml_template = toml_template_base.replace("{{IMPORT}}", target_dir)
            toml_template = toml_template.replace("{{EXPORT}}", temp_dir_out + f"/{target_dir.split('/')[-1]}")
            with open(toml_sources[0], 'w') as fp:
                fp.write(toml_template)
            command = [
                f"{BP}/data/annatto-x86_64-unknown-linux-gnu/annatto",
                "run",
                toml_sources[0]
            ]
            # Run the command without shell=True
            result = subprocess.run(command, capture_output=True, text=True)

        conllu_files = find_conllu_files(temp_dir_out)
        # print(*conllu_files, sep="\n")
        docs = []
        for conllu_file in conllu_files:
            tokens, sofa = conllu_to_doc(conllu_file)
            docs.append(("_".join(conllu_file.split("/")[-2:]), tokens, sofa))

    shutil.rmtree(temp_dir)

    return docs