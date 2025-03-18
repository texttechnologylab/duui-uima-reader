-- Bind static classes from java
StandardCharsets = luajava.bindClass("java.nio.charset.StandardCharsets")

Lemma = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma")
POS = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS")
Token = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token")
MetaDataStringField = luajava.bindClass("de.tudarmstadt.ukp.dkpro.core.api.metadata.type.MetaDataStringField")

Lang = luajava.bindClass("org.texttechnologylab.annotation.annis.Language")
Verse = luajava.bindClass("org.texttechnologylab.annotation.annis.Verse")
PosLemma = luajava.bindClass("org.texttechnologylab.annotation.annis.PosLemma")
Rhyme = luajava.bindClass("org.texttechnologylab.annotation.annis.Rhyme")
Translation = luajava.bindClass("org.texttechnologylab.annotation.annis.Translation")
Inflection = luajava.bindClass("org.texttechnologylab.annotation.annis.Inflection")
InflectionClass = luajava.bindClass("org.texttechnologylab.annotation.annis.InflectionClass")
InflectionClassLemma = luajava.bindClass("org.texttechnologylab.annotation.annis.InflectionClassLemma")
Clause = luajava.bindClass("org.texttechnologylab.annotation.annis.Clause")
Variation = luajava.bindClass("org.texttechnologylab.annotation.annis.Variation")
Writer = luajava.bindClass("org.texttechnologylab.annotation.annis.Writer")
Chapter = luajava.bindClass("org.texttechnologylab.annotation.annis.Chapter")
Subchapter = luajava.bindClass("org.texttechnologylab.annotation.annis.SubChapter")
Page = luajava.bindClass("org.texttechnologylab.annotation.annis.Page")
Line = luajava.bindClass("org.texttechnologylab.annotation.annis.Line")


util = luajava.bindClass("org.apache.uima.fit.util.JCasUtil")


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

    -- Parse JSON data from string into object
    local results = json.decode(inputString)

    inputCas:setDocumentText(results["sofa_str"])

    if JCasUtil:select(inputCas, DocumentMetaData.class):isEmpty() then
        dmd = DocumentMetaData.create(jc);
    else
        dmd = JCasUtil:select(inputCas, DocumentMetaData.class):stream():findFirst()
    end

    -- Meta Data
    local meta_data_list = {}
    local meta_data_counter = 1
    if results["meta_data"] ~= null then
        for i, meta_data in ipairs(results["meta_data"]) do
            if meta_data["key"] == "doc-id" then
                dmd:setDocumentId(meta_data["value"]);
                dmd:setDocumentTitle(meta_data["value"]);
            end
            -- Meta Data
            local meta_obj = luajava.newInstance(MetaDataStringField, inputCas)
            meta_obj:setBegin(meta_obj["begin"])
            meta_obj:setEnd(meta_obj["end"])
            meta_obj:addToIndexes()

            meta_data_list[meta_data_counter] = meta_obj
            meta_data_counter = meta_data_counter + 1
        end
    end

    -- Token
    local token_list = {}
    local token_counter = 1
    if results["token"] ~= null then
        for i, tok in ipairs(results["token"]) do
            local token_obj = luajava.newInstance(Token, inputCas)
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
    if results["pos"] ~= null then
        for i, pos in ipairs(results["pos"]) do
            local pos_obj = luajava.newInstance(POS, inputCas)
            pos_obj:setBegin(pos["begin"])
            pos_obj:setEnd(pos["end"])
            pos_obj:setPosValue(pos["value"])
            pos_obj:addToIndexes()

            pos_list[pos_counter] = pos_obj
            pos_counter = pos_counter + 1
        end
    end

    -- Lang
    local lang_list = {}
    local lang_counter = 1
    if results["lang"] ~= null then
        for i, lang in ipairs(results["lang"]) do
            local lang_obj = luajava.newInstance(Lang, inputCas)
            lang_obj:setBegin(lang["begin"])
            lang_obj:setEnd(lang["end"])
            lang_obj:setValue(lang["value"])
            lang_obj:addToIndexes()
            lang_list[lang_counter] = lang_obj
            lang_counter = lang_counter + 1
        end
    end

    -- Lemma
    local lemma_list = {}
    local lemma_counter = 1
    if results["lemma"] ~= null then
        for i, lemma in ipairs(results["lemma"]) do
            local lemma_obj = luajava.newInstance(Lemma, inputCas)
            lemma_obj:setBegin(lemma["begin"])
            lemma_obj:setEnd(lemma["end"])
            lemma_obj:setValue(lemma["value"])
            lemma_obj:addToIndexes()
            lemma_list[lemma_counter] = lemma_obj
            lemma_counter = lemma_counter + 1
        end
    end

    --[[Document
    local document_list = {}
    local document_counter = 1
    if results["document"] ~= null then
        for i, document in ipairs(results["document"]) do
            local document_obj = luajava.newInstance(Document, inputCas)
            document_obj:setBegin(document["begin"])
            document_obj:setEnd(document["end"])
            document_obj:setValue(document["value"])
            document_obj:addToIndexes()
            document_list[document_counter] = document_obj
            document_counter = document_counter + 1
        end
    end
    -- ]]

    -- Verse
    local verse_list = {}
    local verse_counter = 1
    if results["verse"] ~= null then
        for i, verse in ipairs(results["verse"]) do
            local verse_obj = luajava.newInstance(Verse, inputCas)
            verse_obj:setBegin(verse["begin"])
            verse_obj:setEnd(verse["end"])
            verse_obj:setValue(verse["value"])
            verse_obj:addToIndexes()
            verse_list[verse_counter] = verse_obj
            verse_counter = verse_counter + 1
        end
    end

    -- Line
    local line_list = {}
    local line_counter = 1
    if results["line"] ~= null then
        for i, line in ipairs(results["line"]) do
            local line_obj = luajava.newInstance(Line, inputCas)
            line_obj:setBegin(line["begin"])
            line_obj:setEnd(line["end"])
            line_obj:setValue(line["value"])
            line_obj:addToIndexes()
            line_list[line_counter] = line_obj
            line_counter = line_counter + 1
        end
    end

    -- Writer
    local writer_list = {}
    local writer_counter = 1
    if results["writer"] ~= null then
        for i, writer in ipairs(results["writer"]) do
            local writer_obj = luajava.newInstance(Writer, inputCas)
            writer_obj:setBegin(writer["begin"])
            writer_obj:setEnd(writer["end"])
            writer_obj:setValue(writer["value"])
            writer_obj:addToIndexes()
            writer_list[writer_counter] = writer_obj
            writer_counter = writer_counter + 1
        end
    end

    -- Clause
    local clause_list = {}
    local clause_counter = 1
    if results["clause"] ~= null then
        for i, clause in ipairs(results["clause"]) do
            local clause_obj = luajava.newInstance(Clause, inputCas)
            clause_obj:setBegin(clause["begin"])
            clause_obj:setEnd(clause["end"])
            clause_obj:setValue(clause["value"])
            clause_obj:addToIndexes()
            clause_list[clause_counter] = clause_obj
            clause_counter = clause_counter + 1
        end
    end

    -- InflectionClassLemma
    local inflectionClassLemma_list = {}
    local inflectionClassLemma_counter = 1
    if results["inflectionClassLemma"] ~= null then
        for i, icl in ipairs(results["inflectionClassLemma"]) do
            local icl_obj = luajava.newInstance(InflectionClassLemma, inputCas)
            icl_obj:setBegin(icl["begin"])
            icl_obj:setEnd(icl["end"])
            icl_obj:setValue(icl["value"])
            icl_obj:addToIndexes()
            inflectionClassLemma_list[inflectionClassLemma_counter] = icl_obj
            inflectionClassLemma_counter = inflectionClassLemma_counter + 1
        end
    end

    -- Subchapter
    local subchapter_list = {}
    local subchapter_counter = 1
    if results["subchapter"] ~= null then
        for i, subchapter in ipairs(results["subchapter"]) do
            local subchapter_obj = luajava.newInstance(Subchapter, inputCas)
            subchapter_obj:setBegin(subchapter["begin"])
            subchapter_obj:setEnd(subchapter["end"])
            subchapter_obj:setValue(subchapter["value"])
            subchapter_obj:addToIndexes()
            subchapter_list[subchapter_counter] = subchapter_obj
            subchapter_counter = subchapter_counter + 1
        end
    end

    -- PosLemma
    local posLemma_list = {}
    local posLemma_counter = 1
    if results["posLemma"] ~= null then
        for i, posLemma in ipairs(results["posLemma"]) do
            local posLemma_obj = luajava.newInstance(PosLemma, inputCas)
            posLemma_obj:setBegin(posLemma["begin"])
            posLemma_obj:setEnd(posLemma["end"])
            posLemma_obj:setValue(posLemma["value"])
            posLemma_obj:addToIndexes()
            posLemma_list[posLemma_counter] = posLemma_obj
            posLemma_counter = posLemma_counter + 1
        end
    end

    -- Inflection
    local inflection_list = {}
    local inflection_counter = 1
    if results["inflection"] ~= null then
        for i, inflection in ipairs(results["inflection"]) do
            local inflection_obj = luajava.newInstance(Inflection, inputCas)
            inflection_obj:setBegin(inflection["begin"])
            inflection_obj:setEnd(inflection["end"])
            inflection_obj:setValue(inflection["value"])
            inflection_obj:addToIndexes()
            inflection_list[inflection_counter] = inflection_obj
            inflection_counter = inflection_counter + 1
        end
    end

    --[[Line_m
    local line_m_list = {}
    local line_m_counter = 1
    if results["line_m"] ~= null then
        for i, line_m in ipairs(results["line_m"]) do
            local line_m_obj = luajava.newInstance(Line_m, inputCas)
            line_m_obj:setBegin(line_m["begin"])
            line_m_obj:setEnd(line_m["end"])
            line_m_obj:setValue(line_m["value"])
            line_m_obj:addToIndexes()
            line_m_list[line_m_counter] = line_m_obj
            line_m_counter = line_m_counter + 1
        end
    end
    ]]

    -- Page
    local page_list = {}
    local page_counter = 1
    if results["page"] ~= null then
        for i, page in ipairs(results["page"]) do
            local page_obj = luajava.newInstance(Page, inputCas)
            page_obj:setBegin(page["begin"])
            page_obj:setEnd(page["end"])
            page_obj:setValue(page["value"])
            page_obj:addToIndexes()
            page_list[page_counter] = page_obj
            page_counter = page_counter + 1
        end
    end

    -- Rhyme
    local rhyme_list = {}
    local rhyme_counter = 1
    if results["rhyme"] ~= null then
        for i, rhyme in ipairs(results["rhyme"]) do
            local rhyme_obj = luajava.newInstance(Rhyme, inputCas)
            rhyme_obj:setBegin(rhyme["begin"])
            rhyme_obj:setEnd(rhyme["end"])
            rhyme_obj:setValue(rhyme["value"])
            rhyme_obj:addToIndexes()
            rhyme_list[rhyme_counter] = rhyme_obj
            rhyme_counter = rhyme_counter + 1
        end
    end

    -- Translation
    local translation_list = {}
    local translation_counter = 1
    if results["translation"] ~= null then
        for i, translation in ipairs(results["translation"]) do
            local translation_obj = luajava.newInstance(Translation, inputCas)
            translation_obj:setBegin(translation["begin"])
            translation_obj:setEnd(translation["end"])
            translation_obj:setValue(translation["value"])
            translation_obj:addToIndexes()
            translation_list[translation_counter] = translation_obj
            translation_counter = translation_counter + 1
        end
    end

    -- Chapter
    local chapter_list = {}
    local chapter_counter = 1
    if results["chapter"] ~= null then
        for i, chapter in ipairs(results["chapter"]) do
            local chapter_obj = luajava.newInstance(Chapter, inputCas)
            chapter_obj:setBegin(chapter["begin"])
            chapter_obj:setEnd(chapter["end"])
            chapter_obj:setValue(chapter["value"])
            chapter_obj:addToIndexes()
            chapter_list[chapter_counter] = chapter_obj
            chapter_counter = chapter_counter + 1
        end
    end

    -- InflectionClass
    local inflectionClass_list = {}
    local inflectionClass_counter = 1
    if results["inflectionClass"] ~= null then
        for i, ic in ipairs(results["inflectionClass"]) do
            local ic_obj = luajava.newInstance(InflectionClass, inputCas)
            ic_obj:setBegin(ic["begin"])
            ic_obj:setEnd(ic["end"])
            ic_obj:setValue(ic["value"])
            ic_obj:addToIndexes()
            inflectionClass_list[inflectionClass_counter] = ic_obj
            inflectionClass_counter = inflectionClass_counter + 1
        end
    end

    -- Edition
    local edition_list = {}
    local edition_counter = 1
    if results["edition"] ~= null then
        for i, edition in ipairs(results["edition"]) do
            local edition_obj = luajava.newInstance(Variation, inputCas)
            edition_obj:setBegin(edition["begin"])
            edition_obj:setEnd(edition["end"])
            edition_obj:setValue(edition["value"])
            edition_obj:setLayer("edition")
            edition_obj:addToIndexes()
            edition_list[edition_counter] = edition_obj
            edition_counter = edition_counter + 1
        end
    end

    -- PlainText
    local text_list = {}
    local text_counter = 1
    if results["text"] ~= null then
        for i, text in ipairs(results["text"]) do
            local text_obj = luajava.newInstance(Variation, inputCas)
            text_obj:setBegin(text["begin"])
            text_obj:setEnd(text["end"])
            text_obj:setValue(text["value"])
            text_obj:setLayer("plain_text")
            text_obj:addToIndexes()
            text_list[text_counter] = text_obj
            text_counter = text_counter + 1
        end
    end

end