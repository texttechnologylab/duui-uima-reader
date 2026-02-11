# DUUR (duui-uima-reader)
[![Discord-Server](http://img.shields.io/badge/Join-Discord_Server-fc0098.svg)](https://discord.gg/DxsgfbK7Jh)


### About
This repository contains components for the DUUR framework, a corpus conversion framework integrated into [DUUI](https://github.com/texttechnologylab/DockerUnifiedUIMAInterface). It enables the transformation of a wide range of corpus formats into the UIMA format. The resulting UIMA-formatted data can then be further processed and utilized by tools such as [DUUI](https://github.com/texttechnologylab/DockerUnifiedUIMAInterface) and [UCE](https://github.com/texttechnologylab/UCE).

**DUUI** as well as **DUUR** are developed and maintained at the **Texttechnologylab** ([TTLab](https://www.texttechnologylab.org/)) at the Goethe University Frankfurt.


### Introduction

Despite their success, LLMs are too computationally expensive to replace task- or domain-specific NLP systems. Yet, the diversity of corpus formats across domains makes it difficult to reuse or adapt these specialized systems. As a result, the NLP field faces a trade-off between the efficiency of domain-specific systems and the generality of large language models, underscoring the need for an interoperable NLP landscape. DUUR addresses this challenge by pursuing two objectives: standardizing corpus formats and enabling massively parallel corpus processing. DUUR represents a unified conversion framework embedded in a massively parallel, microservice-based, programming language-independent NLP architecture designed for modularity and extensibility. It allows for the integration of external NLP conversion tools and supports the addition of new components that meet basic compatibility requirements.

```java

public class ReaderTestExample {
    int iWorker = 1;

    public ReaderTestExample() throws URISyntaxException, IOException {
    }

    @Test
    public void DynamicDTNegReaderTestFull() throws Exception {
        // Without Docker: DUUIPipelineComponent readerComp = new DUUIRemoteDriver.Component("http://0.0.0.0:9714").build();
        DUUIPipelineComponent readerComp = new DUUIDockerDriver.Component("duui-biofid_reader:1.0")
                .withScale(iWorker).withImageFetching()
                .build().withTimeout(30);

        List<DUUIPipelineComponent> compList = List.of(readerComp);
        Path filePath = Path.of("/path/to/your/corpus/data/biofid_test.zip");
        DUUIDynamicReaderLazy dynamicReader = new DUUIDynamicReaderLazy(filePath, compList);

        String sOutputPath = "/path/to/your/output/corpus/data/biofid_test.zip";
        DUUIAsynchronousProcessor pProcessor = new DUUIAsynchronousProcessor(dynamicReader);
        new File(sOutputPath).mkdir();
        DUUILuaContext ctx = new DUUILuaContext().withJsonLibrary();
        DUUIComposer composer = new DUUIComposer()
                .withSkipVerification(true)   
                .withLuaContext(ctx)         
                .withWorkers(iWorker);     

        DUUIDockerDriver docker_driver = new DUUIDockerDriver();
        DUUISwarmDriver swarm_driver = new DUUISwarmDriver();
        DUUIRemoteDriver remote_driver = new DUUIRemoteDriver();
        DUUIUIMADriver uima_driver = new DUUIUIMADriver()
                .withDebug(true);
        composer.addDriver(docker_driver, uima_driver
                ,swarm_driver, remote_driver
        );

        composer.add(new DUUIUIMADriver.Component(createEngineDescription(XmiWriter.class,
                XmiWriter.PARAM_TARGET_LOCATION, sOutputPath,
                XmiWriter.PARAM_PRETTY_PRINT, true,
                XmiWriter.PARAM_OVERWRITE, true,
                XmiWriter.PARAM_VERSION, "1.1",
                XmiWriter.PARAM_COMPRESSION, CompressionMethod.BZIP2
        )).withScale(iWorker).build());

        composer.run(pProcessor, "DynamicReaderBiofidTest");

    }

}



```


### Usage & Support

To use DUUR, you only need Docker or podman and DUUI to run a Compose setup.


### Cite
If you want to use the project please quote this as follows:

Hammerla, L., Mehler, A., & Abrami, G. (2025, December). Standardizing Heterogeneous Corpora with DUUR: A Dual Data- and Process-Oriented Approach to Enhancing NLP Pipeline Integration. In K. Inui, S. Sakti, H. Wang, D. F. Wong, P. Bhattacharyya, B. Banerjee, … D. P. Singh (Eds), Proceedings of the 14th International Joint Conference on Natural Language Processing and the 4th Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics (pp. 1410–1425). Retrieved from https://aclanthology.org/2025.findings-ijcnlp.87/

### BibTeX
```

@inproceedings{Hammerla:et:al:2025a,
  author    = {Hammerla, Leon and Mehler, Alexander and Abrami, Giuseppe},
  title     = {Standardizing Heterogeneous Corpora with {DUUR}: A Dual Data-
               and Process-Oriented Approach to Enhancing NLP Pipeline Integration},
  editor    = {Inui, Kentaro and Sakti, Sakriani and Wang, Haofen and Wong, Derek F.
               and Bhattacharyya, Pushpak and Banerjee, Biplab and Ekbal, Asif and Chakraborty, Tanmoy
               and Singh, Dhirendra Pratap},
  booktitle = {Proceedings of the 14th International Joint Conference on Natural
               Language Processing and the 4th Conference of the Asia-Pacific
               Chapter of the Association for Computational Linguistics},
  month     = {dec},
  year      = {2025},
  address   = {Mumbai, India},
  publisher = {The Asian Federation of Natural Language Processing and The Association for Computational Linguistics},
  url       = {https://aclanthology.org/2025.findings-ijcnlp.87/},
  pages     = {1410--1425},
  isbn      = {979-8-89176-303-6},
  abstract  = {Despite their success, LLMs are too computationally expensive
               to replace task- or domain-specific NLP systems. However, the
               variety of corpus formats makes reusing these systems difficult.
               This underscores the importance of maintaining an interoperable
               NLP landscape. We address this challenge by pursuing two objectives:
               standardizing corpus formats and enabling massively parallel corpus
               processing. We present a unified conversion framework embedded
               in a massively parallel, microservice-based, programming language-independent
               NLP architecture designed for modularity and extensibility. It
               allows for the integration of external NLP conversion tools and
               supports the addition of new components that meet basic compatibility
               requirements. To evaluate our dual data- and process-oriented
               approach to standardization, we (1) benchmark its efficiency in
               terms of processing speed and memory usage, (2) demonstrate the
               benefits of standardized corpus formats for NLP downstream tasks,
               and (3) illustrate the advantages of incorporating custom formats
               into a corpus format ecosystem.}
}



```

### Supported Formats:

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
