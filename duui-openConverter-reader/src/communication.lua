-- Bind static classes from java
StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")

JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
DocumentMetaData = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData")


-- This "serialize" function is called to transform the CAS object into an stream that is sent to the annotator
-- Inputs:
--  - inputCas: The actual CAS object to serialize
--  - outputStream: Stream that is sent to the annotator, can be e.g. a string, JSON payload, ...
function serialize(inputCas, outputStream, params)
    outputStream:write(json.encode({
        msg = "test"
    }))
end

-- This "deserialize" function is called on receiving the results from the annotator that have to be transformed into a CAS object
-- Inputs:
--  - inputCas: The actual CAS object to deserialize into
--  - inputStream: Stream that is received from to the annotator, can be e.g. a string, JSON payload, ...
function deserialize(inputCas, inputStream)
    -- Get string from stream, assume UTF-8 encoding
    local inputString = luajava.newInstance("java.lang.String", inputStream:readAllBytes(), StandardCharsets.UTF_8)

    --
    local results = json.decode(inputString)

    if results["sofa_str"] ~= null then
        content = results["sofa_str"]
    else
        content = "unknown"
    end
    if content == "" then
        content = "unknown"
    end



    inputCas:setDocumentText(content)



    if JCasUtil:select(inputCas, DocumentMetaData):isEmpty() then
        dmd = DocumentMetaData:create(inputCas);
    else
        dmd = JCasUtil:select(inputCas, DocumentMetaData):iterator():next()
    end

    dmd:setDocumentId(results["doc_name"]);
    dmd:setDocumentTitle(results["doc_name"]);
    dmd:addToIndexes();
end