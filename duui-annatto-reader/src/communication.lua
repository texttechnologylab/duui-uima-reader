-- Bind static classes from java
StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")

JCasUtil = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")
DocumentMetaData = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData")
Token = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token")
Lemma = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma")
Sentence = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence")
Negation = luajava.bindClass("org.texttechnologylab.annotation.negation.CompleteNegation")
Pos = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS")
FSArray = luajava.bindClass("org.apache.uima.jcas.cas.FSArray")

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

    -- Token
    local token_list = {}
    local token_counter = 1
    if results["token"] ~= null then
        for i, tok in ipairs(results["token"]) do
            local token_obj = luajava.newInstance("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token", inputCas)
            token_obj:setBegin(tok["begin"])
            token_obj:setEnd(tok["end"])
            token_obj:addToIndexes()

            token_list[token_counter] = token_obj
            token_counter = token_counter + 1
        end
    end

    -- POS
    local pos_list = {}
    local pos_counter = 1
    if results["poss"] ~= null then
        for i, pos in ipairs(results["poss"]) do
            local pos_obj = luajava.newInstance("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS", inputCas)
            pos_obj:setBegin(pos["begin"])
            pos_obj:setEnd(pos["end"])
            pos_obj:setPosValue(pos["value"])
            pos_obj:addToIndexes()

            pos_list[pos_counter] = pos_obj
            pos_counter = pos_counter + 1
        end
    end

    -- Lemma
    local lemma_list = {}
    local lemma_counter = 1
    if results["lemmas"] ~= null then
        for i, lemma in ipairs(results["lemmas"]) do
            local lemma_obj = luajava.newInstance("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma", inputCas)
            lemma_obj:setBegin(lemma["begin"])
            lemma_obj:setEnd(lemma["end"])
            lemma_obj:setValue(lemma["value"])
            lemma_obj:addToIndexes()
            lemma_list[lemma_counter] = lemma_obj
            lemma_counter = lemma_counter + 1
        end
    end

end