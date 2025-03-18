import copy
import sqlite3
import os
from functools import partial
from io import StringIO, BytesIO
from itertools import groupby
from typing import List, Tuple, Any, Union, Optional, Dict
from concurrent.futures import ThreadPoolExecutor
from deprecated import deprecated

from tqdm import tqdm

from annis_utils import ANNISImporter


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


class ANNISExtractor:
    def __init__(self,
                 node_file: Union[str, StringIO, BytesIO],
                 node_annotation_file: Union[str, StringIO, BytesIO],
                 corpus_file: Optional[Union[str, StringIO, BytesIO]],
                 corpus_annotation_file: Optional[Union[str, StringIO, BytesIO]],
                 text_file: Optional[Union[str, StringIO, BytesIO]]):
        """
        Constructor for the ANNISExtractor Class
        :param node_file:
        :param node_annotation_file:
        :param corpus_file:
        :param corpus_annotation_file:
        :param text_file:
        """
        self.node_file = node_file
        self.node_annotation_file = node_annotation_file
        self.corpus_file = corpus_file
        self.corpus_annotation_file = corpus_annotation_file
        self.text_file = text_file

        self.db = self.init_db(node_file=self.node_file,
                               node_annotation_file=self.node_annotation_file,
                               corpus_file=self.corpus_file,
                               corpus_annotation_file=self.corpus_annotation_file,
                               text_file=self.text_file)

        self.relannis_version, self.text_keyword, self.edition_keyword = self.check_relannis_version(self.db)

    @classmethod
    def from_str_path(cls, corpus_path: str):
        """
        Initiate Class Object from string paths (just for testing)
        :param corpus_path:
        :return:
        """
        return cls(node_file=f"{corpus_path}/node.annis",
                   node_annotation_file=f"{corpus_path}/node_annotation.annis",
                   corpus_file=f"{corpus_path}/corpus.annis",
                   corpus_annotation_file=f"{corpus_path}/corpus_annotation.annis",
                   text_file=f"{corpus_path}/text.annis"
                   )

    @classmethod
    def from_file_like(cls,
                       node_file: Union[StringIO, BytesIO],
                       node_annotation_file: Union[StringIO, BytesIO],
                       corpus_file: Optional[Union[StringIO, BytesIO]],
                       corpus_annotation_file: Optional[Union[StringIO, BytesIO]],
                       text_file: Optional[Union[StringIO, BytesIO]]):
        """
        Initiate class objects from IOByte file like objects (StringIO depricated)
        :param node_file:
        :param node_annotation_file:
        :param corpus_file:
        :param corpus_annotation_file:
        :param text_file:
        :return:
        """
        return cls(node_file=node_file,
                   node_annotation_file=node_annotation_file,
                   corpus_file=corpus_file,
                   corpus_annotation_file=corpus_annotation_file,
                   text_file=text_file
                   )


    @staticmethod
    def init_db(node_file: Union[str, StringIO, BytesIO],
                node_annotation_file: Union[str, StringIO, BytesIO],
                corpus_file: Union[str, StringIO, BytesIO],
                corpus_annotation_file: Union[str, StringIO, BytesIO],
                text_file: Union[str, StringIO, BytesIO],
                debug: bool = False) -> sqlite3.Connection:
        """
        Read .annis files in database. (TODO add metadata...)
        :param node_file:
        :param node_annotation_file:
        :param corpus_file:
        :param corpus_annotation_file:
        :param text_file:
        :param debug:
        :return:
        """
        annis_db = sqlite3.connect(':memory:')
        annis_db = ANNISImporter.import_nodes_annis_file_sql(node_file,
                                                             conn=annis_db)
        annis_db = ANNISImporter.import_node_annotations_annis_file_sql(node_annotation_file,
                                                                        conn=annis_db)
        annis_db = ANNISImporter.import_corpus_annis_file_sql(corpus_file,
                                                              conn=annis_db)
        annis_db = ANNISImporter.import_corpus_annotation_annis_file_sql(corpus_annotation_file,
                                                                         conn=annis_db)
        annis_db = ANNISImporter.import_text_annis_file_sql(text_file,
                                                            conn=annis_db)
        # TODO Add corpus_annotation for meta data
        if debug:
            ANNISImporter.test_db(annis_db, "nodes")
            ANNISImporter.test_db(annis_db, "annotations")
            ANNISImporter.test_db(annis_db, "corpus")
            ANNISImporter.test_db(annis_db, "corpus_annotations")
            ANNISImporter.test_db(annis_db, "text")
        return annis_db

    @staticmethod
    def check_relannis_version(conn: sqlite3.Connection) -> Tuple[str, str, str]:
        """
        Checks the annis-version and return it as well as the different data views,
        where one view is the original dataview and the second one is an edited view
        :param conn:
        :return:
        """
        cursor = conn.cursor()
        cursor.execute(
            """ SELECT seg_name FROM nodes """
            )
        rows = list(set([row[0] for row in cursor.fetchall()]))
        if "edition" in rows and "text" in rows:
            return "v1.2", "text", "edition"
        elif "tok_anno" in rows and "tok_dipl" in rows:
            return "v1.0", "tok_dipl", "tok_anno"
        else:
            raise Exception("Unknown relannis version")

    @staticmethod
    def calc_offsets(tokens: List[str]) -> List[Tuple[int, int]]:
        """
        Calculate offsets of virtual tokens
        :param tokens:
        :return:
        """
        offsets = []
        current_offset = 0
        for tok in tokens:
            offsets.append((current_offset, len(tok) + current_offset))
            if len(tok) > 0:
                current_offset += len(tok) + 1
            else:
                pass
        return offsets

    @staticmethod
    def add_whitespace_split(text: str) -> List[str]:
        splitter = [
            ",", ".", ":", ";", "?", ")", "(", "-", "!",  # Your original list
            "[", "]", "{", "}", "<", ">", "/", "'",  # Brackets, slashes, quotes
            "@", "#", "$", "%", "&", "*", "=", "+", "_",  # Symbols used in various contexts
            "§", "µ", "€", "£", "¥", "°", "±", "©", "®", "™",
            "«", "»", "„", "“", "”", "‚", "‘", "’", "〝", "〞",  # Currency and typographic symbols
        ]

        for char in splitter:
            text = text.replace(char, f" {char} ")

        return [t for t in text.split(" ") if t != ""]

    @staticmethod
    def pad_list_with_empty(existing_list: List[str], target_length: int) -> List[str]:
        if len(existing_list) >= target_length:
            return existing_list[:target_length]  # Truncate if longer
        else:
            return existing_list + [""] * (target_length - len(existing_list))

    @staticmethod
    def find_overlap(s1: str, s2: str) -> str:
        """
        Finds the longest overlapping substring between two strings.
        It first checks if one string is entirely contained within the other.
        If not, it finds the longest substring where s1's suffix matches s2's prefix.
        :param s1:
        :param s2:
        :return:
        """
        # If one string is completely contained in the other, return that string.
        if s2 in s1:
            return s2
        if s1 in s2:
            return s1
        # Otherwise, look for the longest suffix of s1 that is a prefix of s2.
        overlap = ""
        for i in range(1, min(len(s1), len(s2)) + 1):
            if s1[-i:] == s2[:i]:
                overlap = s1[-i:]
        return overlap

    def extract_corpus_doc_mapping(self) -> Dict[str, Dict[int, Tuple[str, int]]]:
        """
        returns dict in form of:
        {
            "corpus": {0: (name, realid) }
            "document": {0: (name, 0) }
        }
        """
        cursor = self.db.cursor()

        cursor.execute(
            """ SELECT * FROM corpus """)
        rows = cursor.fetchall()
        corpus_structure = {"corpus": dict(), "document": dict()}
        cc = 0
        for row in rows:
            if corpus_structure.get(row[2].lower()) is not None:
                if row[2].lower() == "corpus":
                    corpus_structure[row[2].lower()][cc] = (row[1], row[0])
                    cc += 1
                else:
                    corpus_structure[row[2].lower()][row[0]] = (row[1], row[0])

        return corpus_structure


    def extract_corpus_metadata(self) -> Dict[int, Dict[str, str]]:
        """
        Returns a dict in form of:
        {
            realid: {
                        name: value
                    }
        }
        """
        cursor = self.db.cursor()

        cursor.execute(
            """ SELECT * FROM corpus_annotations """)
        rows = cursor.fetchall()
        annos_per_corpus = dict()
        for row in rows:
            if annos_per_corpus.get(row[0]) is None:
                annos_per_corpus[row[0]] = {row[2]: row[3]}
            else:
                annos_per_corpus[row[0]][row[2]] = row[3]

        return annos_per_corpus

    def extract_doc_metadata(self,
                     annos_per_corpus: Dict[int, Dict[str, str]],
                     corpus_structure: Dict[str, Dict[int, Tuple[str, int]]]):
        cursor = self.db.cursor()

        cursor.execute(
            """ SELECT * FROM text """)
        rows = cursor.fetchall()
        meta_data_per_doc = dict()
        for row in rows:
            meta_data = copy.deepcopy(annos_per_corpus[corpus_structure["corpus"][row[1]][1]])
            meta_data["doc-name"] = corpus_structure["document"][row[0]][0]
            meta_data["text"] = row[3] if row[3].replace(" ", "") != "" else ""
            meta_data_per_doc[row[0]] = meta_data

            # print(1, row)
        return meta_data_per_doc

    def extract_text(self):
        """
        Extract tokens (text) and token-offsets.
        :return:
        """
        cursor = self.db.cursor()

        cursor.execute(""" SELECT * FROM nodes WHERE layer = "default_layer" AND seg_name = "NULL" AND root = "FALSE" """)
        rows = cursor.fetchall()
        # Group the rows by age (use groupby after sorting)
        rows.sort(key=lambda row: row[2])  # Sort by docid (index 2)
        grouped = groupby(rows, key=lambda row: row[2])  # Group by docid (index 2)
        tokens_per_doc = dict()
        offsets_per_doc = dict()
        # Print the groups
        pbar = tqdm(desc="Tokenizing Corpus", total=len(rows))
        for doc_id, group in grouped:
            group = list(group)
            group.sort(key=lambda gr: gr[-4])
            tokens = []
            cursor.execute(
                """ SELECT * FROM nodes WHERE corpus_ref = ? AND seg_name = ? """,
                (doc_id, self.text_keyword)
            )
            doc_id_rows_texts = cursor.fetchall()
            cursor.execute(
                """ SELECT * FROM nodes WHERE corpus_ref = ? AND seg_name = ? """,
                (doc_id, self.edition_keyword)
            )
            doc_id_rows_edits = cursor.fetchall()
            for row in group:
                text_row = []
                edit_row = []
                token = ""

                try:
                    for doc_id_row in doc_id_rows_texts:
                        if doc_id_row[-6] <= row[-7] and doc_id_row[-5] >= row[-7]:
                            text_row = doc_id_row
                            break
                except:
                    text_row = []

                try:
                    for doc_id_row in doc_id_rows_edits:
                        if doc_id_row[-6] <= row[-7] and doc_id_row[-5] >= row[-7]:
                            edit_row = doc_id_row
                            break
                except:
                    edit_row = []
                #print(text_row)
                # print(edit_row)

                if text_row == [] and edit_row == []:
                    pass
                elif text_row == [] and edit_row != []:
                    token = edit_row[-2]
                elif text_row != [] and edit_row == []:
                    token = text_row[-2]
                else:
                    if edit_row[-5] == edit_row[-6] and text_row[-5] == text_row[-6]:
                        token = text_row[-2]
                    elif edit_row[-5] == edit_row[-6] and text_row[-5] != text_row[-6]:
                        token = edit_row[-2]
                    elif edit_row[-5] != edit_row[-6] and text_row[-5] == text_row[-6]:
                        token = text_row[-2]
                    else:
                        splitted_text = ANNISExtractor.add_whitespace_split(text_row[-2])
                        splitted_edition = ANNISExtractor.add_whitespace_split(edit_row[-2])

                        if edit_row[-5] == text_row[-5] and edit_row[-6] == text_row[-6]:
                            gap_length = text_row[-5] - text_row[-6] + 1
                            if len(splitted_text) == gap_length:
                                token = splitted_text[row[-7] - text_row[-6]]
                            elif len(splitted_edition) == gap_length:
                                token = splitted_edition[row[-7] - edit_row[-6]]
                            else:
                                if len(splitted_text) < gap_length:
                                    splitted_text = ANNISExtractor.pad_list_with_empty(splitted_text, gap_length)
                                else:
                                    splitted_text = splitted_text[:gap_length]
                                token = splitted_text[row[-7] - edit_row[-6]]
                        else:
                            if len(splitted_text) == text_row[-5] - text_row[-6] + 1:
                                token = splitted_text[row[-7] - text_row[-6]]
                            elif len(splitted_edition) == edit_row[-5] - edit_row[-6] + 1:
                                token = splitted_edition[row[-7] - edit_row[-6]]
                            else:
                                token = ANNISExtractor.find_overlap(text_row[-2], edit_row[-2])

                tokens.append(token)
                pbar.update(1)
            tokens_per_doc[doc_id] = tokens
            offsets_per_doc[doc_id] = ANNISExtractor.calc_offsets(tokens)

        return tokens_per_doc, offsets_per_doc


    @staticmethod
    @deprecated
    def extract_text_multithreaded_task(row, doc_id_rows_texts, doc_id_rows_edits):
        token = " "
        text_row = []
        edit_row = []
        try:
            for doc_id_row in doc_id_rows_texts:
                if doc_id_row[-6] <= row[-7] and doc_id_row[-5] >= row[-7]:
                    text_row = doc_id_row
                    break
        except:
            text_row = []

        try:
            for doc_id_row in doc_id_rows_edits:
                if doc_id_row[-6] <= row[-7] and doc_id_row[-5] >= row[-7]:
                    edit_row = doc_id_row
                    break
        except:
            edit_row = []
        # print(text_row)
        # print(edit_row)

        if text_row == [] and edit_row == []:
            pass
        elif text_row == [] and edit_row != []:
            token = edit_row[-2]
        elif text_row != [] and edit_row == []:
            token = text_row[-2]
        else:
            if edit_row[-5] == edit_row[-6] and text_row[-5] == text_row[-6]:
                token = text_row[-2]
            elif edit_row[-5] == edit_row[-6] and text_row[-5] != text_row[-6]:
                token = edit_row[-2]
            elif edit_row[-5] != edit_row[-6] and text_row[-5] == text_row[-6]:
                token = text_row[-2]
            else:
                token = ANNISExtractor.find_overlap(text_row[-2], edit_row[-2])

        return token, row[-7]

    @deprecated
    def extract_text_multithreaded(self):
        """
        Extract tokens (text) and token-offsets.
        :return:
        """
        cursor = self.db.cursor()

        cursor.execute(""" SELECT * FROM nodes WHERE layer = "default_layer" AND seg_name = "NULL" AND root = "FALSE" """)
        rows = cursor.fetchall()
        # Group the rows by age (use groupby after sorting)
        rows.sort(key=lambda row: row[2])  # Sort by docid (index 2)
        grouped = groupby(rows, key=lambda row: row[2])  # Group by docid (index 2)
        tokens_per_doc = dict()
        offsets_per_doc = dict()
        # Print the groups
        pbar = tqdm(desc="Tokenizing Corpus", total=len(rows))
        for doc_id, group in grouped:
            group = list(group)
            group.sort(key=lambda gr: gr[-4])
            cursor.execute(
                """ SELECT * FROM nodes WHERE corpus_ref = ? AND seg_name = ? """,
                (doc_id, self.text_keyword)
            )
            doc_id_rows_texts = cursor.fetchall()
            cursor.execute(
                """ SELECT * FROM nodes WHERE corpus_ref = ? AND seg_name = ? """,
                (doc_id, self.edition_keyword)
            )
            doc_id_rows_edits = cursor.fetchall()

            with ThreadPoolExecutor(max_workers=20) as executor:
                # Use map to run tasks and collect results
                results = executor.map(
                    partial(ANNISExtractor.extract_text_multithreaded_task, doc_id_rows_texts=doc_id_rows_texts, doc_id_rows_edits=doc_id_rows_edits),
                    group)
            results = [tup[0] for tup in sorted(list(results), key=lambda x: x[1])]
            pbar.update(len(results))
            tokens_per_doc[doc_id] = results
            offsets_per_doc[doc_id] = ANNISExtractor.calc_offsets(results)

        return tokens_per_doc, offsets_per_doc

    def extract_annotations(self, tokens_per_doc, offsets_per_doc):
        """
        Given the tokens and their offsets: Go through all annotations and find their offset.
        :param tokens_per_doc:
        :param offsets_per_doc:
        :return:
        """
        cursor = self.db.cursor()
        cursor.execute(""" SELECT * FROM annotations """)  # exclude text:  WHERE name != "text"
        rows = cursor.fetchall()

        annotations_per_doc = dict()

        for row in rows:
            node_ref, namespace, name, value = row
            cursor.execute("SELECT text_ref, corpus_ref, layer, name, left_token, right_token, seg_name, span FROM nodes WHERE id = ?", (node_ref,))
            res = cursor.fetchall()
            assert len(res) == 1
            corpus_id, document_id, layer, node_name, token_left, token_right, seg_name, span = res[0]
            """
            print(corpus_id, document_id, layer, node_name, token_left, token_right, seg_name, span)
            print(len(offsets_per_doc[document_id]))
            print(len(tokens_per_doc[document_id]))
            print(tokens_per_doc[document_id])
            """

            offset_left = offsets_per_doc[document_id][token_left][0]
            offset_right = offsets_per_doc[document_id][token_right][-1]
            if annotations_per_doc.get(document_id):
                annotations_per_doc[document_id].append((name, value, offset_left, offset_right))
            else:
                annotations_per_doc[document_id] = [(name, value, offset_left, offset_right)]

        text_per_doc = dict()
        for key in tokens_per_doc:
            tokens = []
            text_per_doc[key] = " ".join([ttok for ttok in tokens_per_doc[key] if ttok != ""])
            for idx, token in enumerate(tokens_per_doc[key]):
                tokens.append(("token", token, offsets_per_doc[key][idx][0], offsets_per_doc[key][idx][-1]))
            annotations_per_doc[key].extend(tokens)

        return annotations_per_doc, text_per_doc,

    @deprecated
    def extract_text_old(self) -> Dict[int, List[int]]:
        """
        Extract tokens (text) and token-offsets.
        :return:
        """
        cursor = self.db.cursor()

        cursor.execute(""" SELECT * FROM nodes WHERE layer = "default_layer" AND seg_name = "NULL" AND root = "FALSE" """)
        rows = cursor.fetchall()
        # Group the rows by age (use groupby after sorting)
        rows.sort(key=lambda row: row[2])  # Sort by docid (index 2)
        grouped = groupby(rows, key=lambda row: row[2])  # Group by docid (index 2)
        tokens_per_doc = dict()
        # Print the groups
        pbar = tqdm(desc="Tokenizing Corpus", total=len(rows))
        for doc_id, group in grouped:
            group = list(group)
            group.sort(key=lambda gr: gr[-4])
            tokens = []
            for row in group:
                tokens.append(row[-7])
                pbar.update(1)
            tokens_per_doc[doc_id] = tokens
        return tokens_per_doc

    @deprecated
    def extract_annotations_old(self, tokens_per_doc):
        """
        Given the tokens and their offsets: Go through all annotations and find their offset.
        :param tokens_per_doc:
        :param offsets_per_doc:
        :return:
        """
        cursor = self.db.cursor()
        cursor.execute(""" SELECT * FROM annotations """)  # exclude text:  WHERE name != "text"
        rows = cursor.fetchall()

        annotations_per_doc = dict()

        for row in rows:
            node_ref, namespace, name, value = row
            cursor.execute("SELECT text_ref, corpus_ref, layer, name, left_token, right_token, seg_name, span FROM nodes WHERE id = ?", (node_ref,))
            res = cursor.fetchall()
            assert len(res) == 1
            corpus_id, document_id, layer, node_name, token_left, token_right, seg_name, span = res[0]

            if annotations_per_doc.get(document_id):
                annotations_per_doc[document_id].append((name, value, token_left, token_right))
            else:
                annotations_per_doc[document_id] = [(name, value, token_left, token_right)]

        text_per_doc = dict()
        for key in tokens_per_doc:
            tokens = []
            text_per_doc[key] = "".join(["." for _t in tokens_per_doc[key]])
            for idx, token in enumerate(tokens_per_doc[key]):
                tokens.append(("token", str(token), token, token))
            annotations_per_doc[key].extend(tokens)

        return annotations_per_doc, text_per_doc,


if __name__ == "__main__":
    import time
    fpt1 = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/DDD-AD-Kleinere_Altsächsische_Denkmäler'
    fpt2 = f'{BP}/data/relannis-v1.0_(2)/relannis/rem-relannis-20161223_1-0/rem-relannis-20161223/11-12_1-rhfrhess-PV-X'
    fpt3 = f'{BP}/data/relannis-v1.0/relannis/ReF_v1.0_relannis_1-0/ReF_v1.0_relannis/ref-mlu/14_2-ofr'
    annis_corpus =ANNISExtractor.from_str_path(fpt1)
    annis_corpus.extract_doc_metadata(annis_corpus.extract_corpus_metadata(), annis_corpus.extract_corpus_doc_mapping())
    """s1 = time.time()
    tpd1, opd1 = annis_corpus.extract_text()
    e1 = time.time()

    s2 = time.time()
    tpd2, opd2 = annis_corpus.extract_text_multithreaded()
    e2 = time.time()

    print("Threaded: ", e2-s2, "Single: ", e1-s1)
    for did in tpd1:
        print(tpd1[did])
        print(tpd2[did])
        assert tpd1[did] == tpd2[did]
        assert opd1[did] == opd2[did]"""
