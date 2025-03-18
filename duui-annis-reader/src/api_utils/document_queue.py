from dataclasses import dataclass
from typing import List, Tuple, Any, Dict, Optional, Union


class AnnisDocument:
    """
    Representation of a annis-document
    """
    def __init__(self,
                 text: str,
                 annotations: List[Tuple[str, str, int, int]],
                 meta_data: Dict[str, Any]
                 ):
        self.text = text
        for i in range(len(annotations)):
            annotations[i] = (annotations[i][0], {"begin": annotations[i][2], "end": annotations[i][3], "value": annotations[i][1]})
        self.annotations: List[Tuple[str, Dict[str, Union[str, int]]]] = annotations
        if meta_data is None:
            self.meta_data = meta_data
        else:
            begin, end = 0, len(self.text)
            md = []
            for key in meta_data:
                md.append(("metadata", {"begin": begin, "end": end, "key": key, "value": meta_data[key]}))
            self.meta_data: List[Tuple[str, Dict[str, Union[str, int]]]] = md

        """for anno in self.annotations + self.meta_data:
            print(anno)"""


class DocumentQueue:
    def __init__(self):
        """
        Queue for annis documents, that are waiting for further processing
        """
        self.docs: List[AnnisDocument] = []

    def has_next(self):
        """
        Queue is not empty
        :return:
        """
        if self.docs:
            return True
        else:
            return False

    def next(self) -> AnnisDocument:
        """
        Return next element in the Queue
        :return:
        """
        return self.docs.pop()

    def get_count(self) -> int:
        """
        Get element count
        :return:
        """
        return len(self.docs)

    def fill(self,
             annotations_per_doc: Dict[int, List[Tuple[str, str, int, int]]],
             text_per_document: Dict[int, str],
             meta_data_per_document: Optional[Dict[int, Dict[str, Any]]]):
        """
        Fill Queue with documents
        :param annotations_per_doc:
        :param text_per_document:
        :param meta_data_per_document:
        :return:
        """
        for key in text_per_document:
            self.docs.append(AnnisDocument(text=text_per_document[key],
                                           annotations=annotations_per_doc[key],
                                           meta_data=meta_data_per_document.get(key) if meta_data_per_document is not None else None))

