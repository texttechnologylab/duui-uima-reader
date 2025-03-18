package org.texttechnologylab.SaltyPepper;

import org.corpus_tools.pepper.cli.PepperStarterConfiguration;
import org.corpus_tools.pepper.common.*;
import org.corpus_tools.pepper.connectors.PepperConnector;
import org.corpus_tools.pepper.connectors.impl.PepperOSGiConnector;
import org.eclipse.emf.common.util.URI;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Objects;
import java.util.Properties;
import java.util.Set;

public class Converter {
    private PepperConnector _pepper;

    public Converter() {
        Path relativePluginPath = Paths.get("pepper", "pepper_plugins");
        Path absolutePluginPath = relativePluginPath.toAbsolutePath();
        PepperStarterConfiguration pepperConf = new PepperStarterConfiguration();
        pepperConf.setProperty(PepperStarterConfiguration.PROP_PLUGIN_PATH, absolutePluginPath.toString());
        this._pepper = new PepperOSGiConnector();
        this._pepper.setConfiguration(pepperConf);
        this._pepper.init();
    }

    public static Set<String> findAllSubDirs(Path startDir) {
        Set<String> subDirs = new HashSet<>();
        try {
            Files.walk(startDir)
                    .filter(Files::isDirectory) // Only directories
                    .forEach(path -> {
                        subDirs.add(path.toString());
                    });
        } catch (IOException e) {
            System.err.println("Error walking directory: " + e.getMessage());
        }
        return subDirs;
    }

    public void convertAnyToAny(String inCorpusPath, String outCorpusPath) throws FileNotFoundException {
        convertAnyToAny(inCorpusPath, outCorpusPath, "txt", "1.0");
    }

    public void convertAnyToAny(String inCorpusPath, String outCorpusPath, String out_type, String out_version) throws FileNotFoundException {
        String jobId= this._pepper.createJob();
        PepperJob job= this._pepper.getJob(jobId);
        Set<String> importers = new HashSet<>();

        // Add each importer
        importers.add("RSDImporter");
        importers.add("CoraXMLImporter");
        importers.add("PAULAImporter");
        importers.add("GateImporter");
        importers.add("Tiger2Importer");
        //importers.add("MMAX2Importer");
        importers.add("SpreadsheetImporter");
        //importers.add("AldtImporter");
        importers.add("WebannoTSVImporter");
        //importers.add("UAMImporter");
        importers.add("GeTaImporter");
        importers.add("ToolboxImporter");
        importers.add("CoNLLImporter");
        //importers.add("GraphAnnoImporter");
        importers.add("TEIImporter");
        importers.add("GenericXMLImporter");
        importers.add("TCFImporter");
        importers.add("RSTImporter");
        importers.add("ElanImporter");
        importers.add("PTBImporter");
        importers.add("WolofImporter");
        importers.add("EXMARaLDAImporter");
        //importers.add("GrAFImporter");
        importers.add("CoNLLCorefImporter");
        //importers.add("SaltXMLImporter");
        importers.add("TextImporter");
        importers.add("TreetaggerImporter");


        for (PepperModuleDesc moduleDesc: this._pepper.getRegisteredModules()){

            if (moduleDesc.getModuleType() == MODULE_TYPE.IMPORTER
                    && !Objects.equals(moduleDesc.getName(), "DoNothingImporter")
                    && importers.contains(moduleDesc.getName())
            ) {
                System.out.println(moduleDesc.getName());
                CorpusDesc corpusImport= new CorpusDesc().setCorpusPath(URI.createFileURI(inCorpusPath));
                corpusImport.getFormatDesc().setFormatName(moduleDesc.getSupportedFormats().get(0).getFormatName()); // txt 0.0
                corpusImport.getFormatDesc().setFormatVersion(moduleDesc.getSupportedFormats().get(0).getFormatVersion());
                job.addStepDesc(new StepDesc().setProps(new Properties()).setCorpusDesc(corpusImport).setModuleType(MODULE_TYPE.IMPORTER));


            }
        }
        CorpusDesc corpusExport= new CorpusDesc().setCorpusPath(URI.createFileURI(outCorpusPath));
        corpusExport.getFormatDesc().setFormatName(out_type); // txt 1.0
        corpusExport.getFormatDesc().setFormatVersion(out_version);
        job.addStepDesc(new StepDesc().setProps(new Properties()).setCorpusDesc(corpusExport).setModuleType(MODULE_TYPE.EXPORTER));
        job.convert();
        this._pepper.removeJob(jobId);
    }
}
