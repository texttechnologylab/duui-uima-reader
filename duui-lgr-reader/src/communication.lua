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

    -- Sentences
    local sent_list = {}
    local sent_counter = 1
    if results["sentences"] ~= null then
        for i, sent in ipairs(results["sentences"]) do
            local sent_obj = luajava.newInstance("de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence", inputCas)
            sent_obj:setBegin(sent["begin"])
            sent_obj:setEnd(sent["end"])
            sent_obj:addToIndexes()
            sent_list[sent_counter] = sent_obj
            sent_counter = sent_counter + 1
        end
    end

    -- meta data (uce)
    local uce_list = {}
    local uce_counter = 1
    if results["uce_metadata"] ~= null then
        for i, uce in ipairs(results["uce_metadata"]) do
            local uce_obj = luajava.newInstance("org.texttechnologylab.annotation.uce.Metadata", inputCas)
            uce_obj:setValue(uce["value"])
            uce_obj:setKey(uce["key"])
            uce_obj:setValueType(uce["value_type"])
            uce_obj:addToIndexes()
            uce_list[uce_counter] = uce_obj
            uce_counter = uce_counter + 1
        end
    end

    -- dd document links
    local dlink_list = {}
    local dlink_counter = 1
    if results["dlinks"] ~= null then
        for i, dlink in ipairs(results["dlinks"]) do
            local dlink_obj = luajava.newInstance("org.texttechnologylab.annotation.link.DLink", inputCas)
            dlink_obj:setFrom(dlink["fromX"])
            dlink_obj:setTo(dlink["toY"])
            dlink_obj:setLinkType(dlink["link_type"])
            dlink_obj:setLinkId(dlink["id"])
            dlink_obj:addToIndexes()
            dlink_list[dlink_counter] = dlink_obj
            dlink_counter = dlink_counter + 1
        end
    end

    -- ad document links
    local adlink_list = {}
    local adlink_counter = 1
    if results["adlinks"] ~= null then
        for i, adlink in ipairs(results["adlinks"]) do
            local adlink_obj = luajava.newInstance("org.texttechnologylab.annotation.link.ADLink", inputCas)
            local begin_idx = adlink["fromX"]["begin"]
            local end_idx = adlink["fromX"]["end"]
            for s, real_sent in ipairs(sent_list) do
                if real_sent:getBegin() == begin_idx and real_sent:getEnd() == end_idx then
                    adlink_obj:setFrom(real_sent)
                    break
                end
            end
            adlink_obj:setTo(adlink["toY"])
            adlink_obj:setLinkType(adlink["link_type"])
            adlink_obj:setLinkId(adlink["id"])
            adlink_obj:addToIndexes()
            adlink_list[adlink_counter] = adlink_obj
            adlink_counter = adlink_counter + 1
        end
    end

    -- da document links
    local dalink_list = {}
    local dalink_counter = 1
    if results["dalinks"] ~= null then
        for i, dalink in ipairs(results["dalinks"]) do
            local dalink_obj = luajava.newInstance("org.texttechnologylab.annotation.link.DALink", inputCas)
            dalink_obj:setFrom(dalink["fromX"])
            local begin_idx = dalink["toY"]["begin"]
            local end_idx = dalink["toY"]["end"]
            for s, real_sent in ipairs(sent_list) do
                if real_sent:getBegin() == begin_idx and real_sent:getEnd() == end_idx then
                    dalink_obj:setTo(real_sent)
                    break
                end
            end
            dalink_obj:setLinkType(dalink["link_type"])
            dalink_obj:setLinkId(dalink["id"])
            dalink_obj:addToIndexes()
            dalink_list[dalink_counter] = dalink_obj
            dalink_counter = dalink_counter + 1
        end
    end

    -- Negations
    local neg_list = {}
    local neg_counter = 1
    if results["negations"] ~= null then
        for i, neg in ipairs(results["negations"]) do
            local neg_obj = luajava.newInstance("org.texttechnologylab.annotation.negation.CompleteNegation", inputCas)
            local event_lst = {}
            local scope_lst = {}
            local xscope_lst = {}
            local focus_lst = {}
            local cue = null
            local negType = null

            if neg["event"] ~= null then
                local tok_idx = 1
                for j, tok in ipairs(neg["event"]) do
                    local begin_idx = tok["begin"]
                    local end_idx = tok["end"]
                    for k, real_tok in ipairs(token_list) do
                        if real_tok:getBegin() == begin_idx and real_tok:getEnd() == end_idx then
                            event_lst[tok_idx] = real_tok
                            tok_idx = tok_idx + 1
                            break
                        end
                    end
                end
            end

            if neg["xscope"] ~= null then
                local tok_idx = 1
                for j, tok in ipairs(neg["xscope"]) do
                    local begin_idx = tok["begin"]
                    local end_idx = tok["end"]
                    for k, real_tok in ipairs(token_list) do
                        if real_tok:getBegin() == begin_idx and real_tok:getEnd() == end_idx then
                            xscope_lst[tok_idx] = real_tok
                            tok_idx = tok_idx + 1
                            break
                        end
                    end

                end
            end

            if neg["scope"] ~= null then
                local tok_idx = 1
                for j, tok in ipairs(neg["scope"]) do
                    local begin_idx = tok["begin"]
                    local end_idx = tok["end"]
                    for k, real_tok in ipairs(token_list) do
                        if real_tok:getBegin() == begin_idx and real_tok:getEnd() == end_idx then
                            scope_lst[tok_idx] = real_tok
                            tok_idx = tok_idx + 1
                            break
                        end
                    end

                end
            end

            if neg["focus"] ~= null then
                local tok_idx = 1
                for j, tok in ipairs(neg["focus"]) do
                    local begin_idx = tok["begin"]
                    local end_idx = tok["end"]
                    for k, real_tok in ipairs(token_list) do
                        if real_tok:getBegin() == begin_idx and real_tok:getEnd() == end_idx then
                            focus_lst[tok_idx] = real_tok
                            tok_idx = tok_idx + 1
                            break
                        end
                    end

                end
            end

            if neg["cue"] ~= null then
                local begin_idx = neg["cue"]["begin"]
                local end_idx = neg["cue"]["end"]
                for k, real_tok in ipairs(token_list) do
                    if real_tok:getBegin() == begin_idx and real_tok:getEnd() == end_idx then
                        cue = real_tok
                        break
                    end
                end
            end

            if cue ~= null then
                neg_obj:setCue(cue)
            end

            if negType ~= null then
                neg_obj:setNegType(negType)
            end

            if #focus_lst ~= 0 then
                local arr = luajava.newInstance("org.apache.uima.jcas.cas.FSArray", inputCas, #focus_lst)
                for j, tok in ipairs(focus_lst) do
                    arr:set(j-1, tok)
                end
                neg_obj:setFocus(arr)
            end

            if #xscope_lst ~= 0 then
                local arr = luajava.newInstance("org.apache.uima.jcas.cas.FSArray", inputCas, #xscope_lst)
                for j, tok in ipairs(xscope_lst) do
                    arr:set(j-1, tok)
                end
                neg_obj:setXscope(arr)
            end

            if #scope_lst ~= 0 then
                local arr = luajava.newInstance("org.apache.uima.jcas.cas.FSArray", inputCas, #scope_lst)
                for j, tok in ipairs(scope_lst) do
                    arr:set(j-1, tok)
                end
                neg_obj:setScope(arr)
            end

            if #event_lst ~= 0 then
                local arr = luajava.newInstance("org.apache.uima.jcas.cas.FSArray", inputCas, #event_lst)
                for j, tok in ipairs(event_lst) do
                    arr:set(j-1, tok)
                end
                neg_obj:setEvent(arr)
            end

            neg_obj:addToIndexes()
            neg_list[neg_counter] = neg_obj
            neg_counter = neg_counter + 1
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