from io import BytesIO, StringIO
import os
from typing import List, Any, Union
import pandas as pd
import sqlite3
import csv
from abc import ABC


BP = os.path.realpath(os.path.join(os.path.realpath(__file__), "../../.."))


class ANNISImporter(ABC):
    @staticmethod
    def replace_last_whitespace_with_tab(input_string):
        """
        In case annis file is broken (one \t is missing), try to repair it and put it back in (can happen, if
        tab is same size as whitespace?).
        :param input_string:
        :return:
        """
        # Find the index of the last whitespace in the string
        last_whitespace_index = input_string.rfind(' ')
        # If there's a whitespace, replace it with a tab
        if last_whitespace_index != -1:
            return input_string[:last_whitespace_index] + '\t' + input_string[last_whitespace_index + 1:]
        return input_string  # Return the original string if no whitespace is found

    @staticmethod
    def read_csv(file: Union[str, BytesIO, StringIO], seps: int) -> Any:
        """
        Read in annis file which is a tab seperated file.
        :param file:
        :param seps:
        :return:
        """
        if isinstance(file, str):
            # Open and read the TSV file
            with open(file, newline='', encoding='utf-8') as cf:
                lines = cf.readlines()
        elif isinstance(file, BytesIO):
            raw_text = file.read().decode("utf-8")
            lines = raw_text.split("\n")
        elif isinstance(file, StringIO):
            raw_text = file.read()
            lines = raw_text.split("\n")
        else:
            raise Exception("read_csv needs str, BytesIO, or StringIO as Input")
        content = []
        for line in lines:
            if line.count("\t") == seps:
                content.append(line)
            else:
                if line.replace(" ", "") == "":
                    pass
                else:
                    content.append(ANNISImporter.replace_last_whitespace_with_tab(line))
        reader = [line.replace("\n", "").split("\t") for line in content]
        reader = [tuple(row) for row in reader]
        return reader

    @staticmethod
    def import_nodes_annis_file_sql(file: Union[str, BytesIO, StringIO], conn: sqlite3.Connection) -> sqlite3.Connection:
        """
        Import a specific annis file (node.annis)
        :param file:
        :param conn:
        :return:
        """
        # Define database and table
        # Connect to SQLite database
        table_name = "nodes"
        cursor = conn.cursor()

        # Create table (modify columns based on your TSV structure)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
                text_ref INTEGER,
                corpus_ref INTEGER,
                layer TEXT,
                name TEXT,
                left INTEGER,
                right INTEGER,
                token_index INTEGER,
                left_token INTEGER,
                right_token INTEGER,
                seg_index INTEGER,
                seg_name TEXT,
                span TEXT,
                root BOOLEAN
            )
        """)

        reader = ANNISImporter.read_csv(file, 13)
        cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", reader)
        conn.commit()

        return conn

    @staticmethod
    def import_node_annotations_annis_file_sql(file: Union[str, BytesIO, StringIO], conn: sqlite3.Connection) -> sqlite3.Connection:
        """
        Import a specific annis file (node_annotations.annis)
        :param file:
        :param conn:
        :return:
        """
        # Define database and table
        # Connect to SQLite database
        table_name = "annotations"
        cursor = conn.cursor()

        # Create table (modify columns based on your TSV structure)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                node_ref INTEGER,
                namespace TEXT,
                name TEXT,
                value TEXT,
                PRIMARY KEY (node_ref, name)
            )
        """)

        reader = ANNISImporter.read_csv(file, 3)
        cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)", reader)
        conn.commit()

        return conn

    @staticmethod
    def import_corpus_annis_file_sql(file: Union[str, BytesIO, StringIO], conn: sqlite3.Connection) -> sqlite3.Connection:
        """
        Import a specific annis file (corpus.annis)
        :param file:
        :param conn:
        :return:
        """
        # Define database and table
        # Connect to SQLite database
        table_name = "corpus"
        cursor = conn.cursor()

        # Create table (modify columns based on your TSV structure)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER,
                name TEXT,
                type TEXT,
                version TEXT,
                pre INTEGER,
                post INTEGER,
                top_level BOOLEAN
            )
        """)


        reader = ANNISImporter.read_csv(file, 6)
        cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?)", reader)
        conn.commit()

        return conn

    @staticmethod
    def import_corpus_annotation_annis_file_sql(file: Union[str, BytesIO, StringIO], conn: sqlite3.Connection) -> sqlite3.Connection:
        """
        Import a specific annis file (corpus_annotation.annis)
        :param file:
        :param conn:
        :return:
        """
        # Define database and table
        # Connect to SQLite database
        table_name = "corpus_annotations"
        cursor = conn.cursor()

        # Create table (modify columns based on your TSV structure)
        cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        corpus_ref INTEGER,
                        namespace TEXT,
                        name TEXT,
                        value TEXT
                    )
                """
                       )

        reader = ANNISImporter.read_csv(file, 3)
        cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)", reader)
        conn.commit()

        return conn

    @staticmethod
    def import_text_annis_file_sql(file: Union[str, BytesIO, StringIO],
                                   conn: sqlite3.Connection) -> sqlite3.Connection:
        """
        Import a specific annis file (text.annis)
        :param file:
        :param conn:
        :return:
        """
        # Define database and table
        # Connect to SQLite database
        table_name = "text"
        cursor = conn.cursor()

        # Create table (modify columns based on your TSV structure)
        cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            corpus_ref INTEGER,
                            id INTEGER,
                            name TEXT,
                            text TEXT
                        )
                    """
                       )

        reader = ANNISImporter.read_csv(file, 3)
        cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?)", reader)
        conn.commit()

        return conn

    @staticmethod
    def test_db(conn: sqlite3.Connection, table_name: str):
        """
        Testing, if reading works as expected.
        :param conn:
        :param table_name:
        :return:
        """
        cursor = conn.cursor()
        res = cursor.execute("SELECT name FROM sqlite_master")

        print(res.fetchone())
        cursor.execute(f"PRAGMA table_info({table_name})")

        # Fetch all column info (name, type, etc.)
        columns_info = cursor.fetchall()

        # Extract and print column names
        columns = [col[1] for col in columns_info]  # The column name is at index 1
        print(columns)
        # Verify the data was inserted by querying the table and printing the results
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        for row in rows:
            print(row)
            break

    @staticmethod
    def test_node_db(conn: sqlite3.Connection):
        """
        Test node.annis - DB
        :param conn:
        :return:
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * 
            FROM nodes
            WHERE left_token != right_token 
              AND (seg_name = 'text')
        """)
        rows = cursor.fetchall()

        for row in rows:
            print(row)

    @staticmethod
    def get_all_possible_annotations(conn: sqlite3.Connection):
        """
        Find all annotations in a corpus
        :param conn:
        :return:
        """
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT name 
                    FROM annotations
                """)
        rows = cursor.fetchall()

        annos = []
        for row in rows:
            annos.append(row[0])
        return list(set(annos))

    @staticmethod
    def get_all_node_anno_types():
        """
        Find all annotations in multiple corpora
        :return:
        """
        base_dir = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora'
        corpora = os.listdir(base_dir)
        annos = []
        for corpus in corpora:
            fp = f'{base_dir}/{corpus}/node_annotation.annis'
            sq = sqlite3.connect(':memory:')
            sq_conn = ANNISImporter.import_node_annotations_annis_file_sql(fp, conn=sq)
            annos.extend(ANNISImporter.get_all_possible_annotations(sq_conn))
        print(list(set(annos)))

if __name__ == "__main__":
    corpora = "DDD-AD-Benediktiner_Regel"
    # corpora = "DDD-AD-Benediktiner_Regel_Latein"
    fp1 = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/{corpora}/node.annis'
    fp2 = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/{corpora}/node_annotation.annis'
    fp3 = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/{corpora}/corpus.annis'
    fp4 = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/{corpora}/corpus_annotation.annis'
    fp5 = f'{BP}/data/relannis-v1.2/relannis/DDD-AD_1.2-relannis_1-2/corpora/{corpora}/text.annis'

    sqlite_connection = sqlite3.connect(':memory:')
    # sqlite_connection = ANNISImporter.import_nodes_annis_file_sql(fp1, conn=sqlite_connection)
    # sqlite_connection = ANNISImporter.import_node_annotations_annis_file_sql(fp2, conn=sqlite_connection)
    sqlite_connection = ANNISImporter.import_corpus_annis_file_sql(fp3, conn=sqlite_connection)
    sqlite_connection = ANNISImporter.import_corpus_annotation_annis_file_sql(fp4, conn=sqlite_connection)
    sqlite_connection = ANNISImporter.import_text_annis_file_sql(fp5, conn=sqlite_connection)
    # ANNISImporter.test_db(sqlite_connection, "nodes")
    # ANNISImporter.test_db(sqlite_connection, "annotations")
    ANNISImporter.test_db(sqlite_connection, "corpus")
    ANNISImporter.test_db(sqlite_connection, "corpus_annotations")
    ANNISImporter.test_db(sqlite_connection, "text")
    # ANNISImporter.test_node_db(sqlite_connection)
    # ANNISImporter.get_all_possible_annotations(sqlite_connection)
    # ANNISImporter.get_all_node_anno_types()