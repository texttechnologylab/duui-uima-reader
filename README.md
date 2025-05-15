# duui-uima-reader
This repository contains components for the {unk} framework, a corpus conversion framework integrated into [DUUI](https://github.com/texttechnologylab/DockerUnifiedUIMAInterface). It enables the transformation of a wide range of corpus formats into the UIMA format. The resulting UIMA-formatted data can then be further processed and utilized by tools such as [DUUI](https://github.com/texttechnologylab/DockerUnifiedUIMAInterface) and [UCE](https://github.com/texttechnologylab/UCE).

## Supported Formats:

- List of integrated third-party conversion tools. Each component supports multiple corpus formats, with some tools offering overlapping functionality:

  -   | **Component**    | **Module**               | **File Format**            |
      |------------------|--------------------------|----------------------------|
      | **Pepper**       |                          |                            |
      |                  | RSD                      | .rsd                       |
      |                  | CoraXML                  | .xml                       |
      |                  | PAULA                    | .xml                       |
      |                  | Gate                     | .xml                       |
      |                  | TigerXML                 | .xml                       |
      |                  | Treetagger               | .txt                       |
      |                  | Spreadsheet†             | .xls \| .xlsx              |
      |                  | WebannoTSV               | .tsv                       |
      |                  | GeTa                     | .json                      |
      |                  | Toolbox                  | .txt                       |
      |                  | CoNLL†                   | .conll \| .txt            |
      |                  | TEI†                     | .tei \| .xml              |
      |                  | GenericXML               | .xml                       |
      |                  | TCF                      | .xml                       |
      |                  | RST                      | .rst                       |
      |                  | Elan                     | .eaf                       |
      |                  | PTB                      | .mrg                       |
      |                  | EXMARaLDA†               | .exb \| .exs \| .exf      |
      |                  | CoNLLCoref               | .conll                     |
      |                  | SaltXML                  | .xml                       |
      |                  | Text                     | .txt                       |
      |                  | MMAX2†                   | .mmax \| .xml             |
      |                  | GrAF†                    | .xml \| .graf             |
      |                  | GraphAnno                | .json                      |
      |                  | UAM†                     | .txt \| .xml \| .uam      |
      | **Annatto**      |                          |                            |
      |                  | CoNLL-U                  | .conllu                    |
      |                  | EXMARaLDA                | .exb                       |
      |                  | GraphML                  | .xml                       |
      |                  | meta                     | .csv                       |
      |                  | opus                     | .xml                       |
      |                  | PTB                      | .mrg                       |
      |                  | relANNIS-3.3†            | .annis \| .version ...    |
      |                  | SaltXML                  | .xml                       |
      |                  | table                    | .csv                       |
      |                  | textgrid                 | .txt                       |
      |                  | toolbox                  | .txt                       |
      |                  | treetagger               | .txt                       |
      |                  | whisper                  | .json                      |
      |                  | Spreadsheet              | .xlsx                      |
      |                  | GenericXml               | .xml                       |
      | **openConv**     |                          |                            |
      |                  | text                     | .txt                       |
      |                  | TEI†                     | .tei \| .xml              |
      |                  | alto                     | .alto                      |
      |                  | doc                      | .doc                       |
      |                  | docx                     | .docx                      |
      |                  | HTML                     | .html                      |

- List of dedicated reader components and the specific file formats they support. Some components may share the same file format extension, but often require distinct internal structures. For instance, the CSV format used by Sketch Engine differs significantly from that of the Bioscope corpus:
  - | **Component**         | **Module**         | **File Format**           |
    |-----------------------|--------------------|---------------------------|
    | **ANNIS**             |                    |                           |
    |                       | relANNIS-3.3†      | .annis \| .version ...   |
    | **Sketch Engine**     |                    |                           |
    |                       | SE                 | .csv                      |
    | **SOCC**              |                    |                           |
    |                       | SOCC               | .tsv                      |
    | **SFU**               |                    |                           |
    |                       | SFU                | .xml                      |
    | **Conan Doyle**       |                    |                           |
    |                       | CD-SCO             | .txt*                     |
    | **PB-FOC**            |                    |                           |
    |                       | PB-FOC             | .txt*                     |
    | **Bioscope**          |                    |                           |
    |                       | BS                 | .csv                      |
    | **Deeptutor Neg**     |                    |                           |
    |                       | DT-Neg             | .txt                      |
    | **Leipzig Glossing**  |                    |                           |
    |                       | LGR                | .tex                      |
