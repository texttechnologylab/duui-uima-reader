/**
 * Copyright (C) 2011-2012 The XDocReport Team <xdocreport@googlegroups.com>
 *
 * All rights reserved.
 *
 * Permission is hereby granted, free  of charge, to any person obtaining
 * a  copy  of this  software  and  associated  documentation files  (the
 * "Software"), to  deal in  the Software without  restriction, including
 * without limitation  the rights to  use, copy, modify,  merge, publish,
 * distribute,  sublicense, and/or sell  copies of  the Software,  and to
 * permit persons to whom the Software  is furnished to do so, subject to
 * the following conditions:
 *
 * The  above  copyright  notice  and  this permission  notice  shall  be
 * included in all copies or substantial portions of the Software.
 *
 * THE  SOFTWARE IS  PROVIDED  "AS  IS", WITHOUT  WARRANTY  OF ANY  KIND,
 * EXPRESS OR  IMPLIED, INCLUDING  BUT NOT LIMITED  TO THE  WARRANTIES OF
 * MERCHANTABILITY,    FITNESS    FOR    A   PARTICULAR    PURPOSE    AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE,  ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
package org.apache.poi.xwpf.converter.core;

import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.poi.openxml4j.opc.PackagePart;
import org.apache.poi.xwpf.converter.core.styles.XWPFStylesDocument;
import org.apache.poi.xwpf.converter.core.utils.DxaUtil;
import org.apache.poi.xwpf.converter.core.utils.StringUtils;
import org.apache.poi.xwpf.converter.core.utils.XWPFRunHelper;
import org.apache.poi.xwpf.converter.core.utils.XWPFTableUtil;
import org.apache.poi.xwpf.usermodel.BodyElementType;
import org.apache.poi.xwpf.usermodel.BodyType;
import org.apache.poi.xwpf.usermodel.IBody;
import org.apache.poi.xwpf.usermodel.IBodyElement;
import org.apache.poi.xwpf.usermodel.XWPFAbstractNum;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFFooter;
import org.apache.poi.xwpf.usermodel.XWPFHeader;
import org.apache.poi.xwpf.usermodel.XWPFHeaderFooter;
import org.apache.poi.xwpf.usermodel.XWPFHyperlink;
import org.apache.poi.xwpf.usermodel.XWPFHyperlinkRun;
import org.apache.poi.xwpf.usermodel.XWPFNum;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.apache.poi.xwpf.usermodel.XWPFPictureData;
import org.apache.poi.xwpf.usermodel.XWPFRun;
import org.apache.poi.xwpf.usermodel.XWPFStyle;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableCell;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.apache.xmlbeans.XmlCursor;
import org.apache.xmlbeans.XmlException;
import org.apache.xmlbeans.XmlObject;
import org.apache.xmlbeans.XmlTokenSource;
import org.openxmlformats.schemas.drawingml.x2006.main.CTGraphicalObject;
import org.openxmlformats.schemas.drawingml.x2006.main.CTGraphicalObjectData;
import org.openxmlformats.schemas.drawingml.x2006.picture.CTPicture;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.CTAnchor;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.CTInline;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.CTPosH;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.CTPosV;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.CTWrapSquare;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.STRelFromH;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.STRelFromV;
import org.openxmlformats.schemas.drawingml.x2006.wordprocessingDrawing.STWrapText;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTBookmark;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTBr;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTDecimalNumber;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTDrawing;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTEmpty;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTHdrFtr;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTHdrFtrRef;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTHyperlink;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTLvl;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTNumPr;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTOnOff;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTP;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTPPr;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTPTab;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTR;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTRow;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTRunTrackChange;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSdtBlock;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSdtCell;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSdtContentBlock;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSdtContentRun;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSdtRun;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSectPr;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSimpleField;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTSmartTagRun;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTString;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTStyle;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTTabs;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTTbl;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTTc;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.CTText;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.FtrDocument;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.HdrDocument;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STBrType;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STFldCharType;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STMerge;
import org.openxmlformats.schemas.wordprocessingml.x2006.main.STOnOff;

/**
 * Visitor to visit elements from entry word/document.xml, word/header*.xml, word/footer*.xml
 * 
 * @param <T>
 * @param <O>
 * @param <E>
 */
public abstract class XWPFDocumentVisitor<T, O extends Options, E extends IXWPFMasterPage>
    implements IMasterPageHandler<E>
{

    private static final Logger LOGGER = Logger.getLogger( XWPFDocumentVisitor.class.getName() );

    protected static final String WORD_MEDIA = "word/media/";

    protected final XWPFDocument document;

    private final MasterPageManager masterPageManager;

    private XWPFHeader currentHeader;

    private XWPFFooter currentFooter;

    protected final XWPFStylesDocument stylesDocument;

    protected final O options;

    private boolean pageBreakOnNextParagraph;

    /**
     * Map of w:numId and ListContext
     */
    private Map<Integer, ListContext> listContextMap;

    public XWPFDocumentVisitor( XWPFDocument document, O options )
        throws Exception
    {
        this.document = document;
        this.options = options;
        this.stylesDocument = createStylesDocument( document );
        this.masterPageManager = new MasterPageManager( document.getDocument(), this );
    }

    protected XWPFStylesDocument createStylesDocument( XWPFDocument document )
        throws XmlException, IOException
    {
        return new XWPFStylesDocument( document );
    }

    public XWPFStylesDocument getStylesDocument()
    {
        return stylesDocument;
    }

    public O getOptions()
    {
        return options;
    }

    public MasterPageManager getMasterPageManager()
    {
        return masterPageManager;
    }

    // ------------------------------ Start/End document visitor -----------

    /**
     * Main entry for visit XWPFDocument.
     * 
     * @param out
     * @throws Exception
     */
    public void start()
        throws Exception
    {
        // start document
        T container = startVisitDocument();
        // Create IText, XHTML element for each XWPF elements from the w:body
        List<IBodyElement> bodyElements = document.getBodyElements();
        visitBodyElements( bodyElements, container );
        // end document
        endVisitDocument();
    }

    /**
     * Start of visit document.
     * 
     * @return
     * @throws Exception
     */
    protected abstract T startVisitDocument()
        throws Exception;

    /**
     * End of visit document.
     * 
     * @throws Exception
     */
    protected abstract void endVisitDocument()
        throws Exception;

    // ------------------------------ XWPF Elements visitor -----------

    protected void visitBodyElements( List<IBodyElement> bodyElements, T container )
        throws Exception
    {
        if ( !masterPageManager.isInitialized() )
        {
            // master page manager which hosts each <:w;sectPr declared in the word/document.xml
            // must be initialized. The initialization loop for each
            // <w:p paragraph to compute a list of <w:sectPr which contains information
            // about header/footer declared in the <w:headerReference/<w:footerReference
            masterPageManager.initialize();
        }

        String previousParagraphStyleName = null;
        for ( int i = 0; i < bodyElements.size(); i++ )
        {
            IBodyElement bodyElement = bodyElements.get( i );
            switch ( bodyElement.getElementType() )
            {
                case PARAGRAPH:
                    XWPFParagraph paragraph = (XWPFParagraph) bodyElement;
                    String paragraphStyleName = paragraph.getStyleID();
                    boolean sameStyleBelow =
                        ( paragraphStyleName != null && paragraphStyleName.equals( previousParagraphStyleName ) );

                    visitParagraph( paragraph, i, container );
                    break;
                case TABLE:
                    previousParagraphStyleName = null;
                    visitTable( (XWPFTable) bodyElement, i, container );
                    break;
            }
        }

    }

    /**
     * Visit the given paragraph.
     * 
     * @param paragraph
     * @param index
     * @param container
     * @throws Exception
     */
    protected void visitParagraph( XWPFParagraph paragraph, int index, T container )
        throws Exception
    {
        if ( isWordDocumentPartParsing() )
        {
            // header/footer is not parsing.
            // It's the word/document.xml which is parsing
            // test if the current paragraph define a <w:sectPr
            // to update the header/footer declared in the <w:headerReference/<w:footerReference
            masterPageManager.update( paragraph.getCTP() );
        }
        if ( pageBreakOnNextParagraph )
        {
            pageBreak();
        }
        this.pageBreakOnNextParagraph = false;

        ListItemContext itemContext = null;
        CTNumPr originalNumPr = stylesDocument.getParagraphNumPr( paragraph );
        CTNumPr numPr = getNumPr( originalNumPr );
        if ( numPr != null )
        {
            // paragraph is a numbered/bullet list
            // see http://msdn.microsoft.com/en-us/library/office/ee922775%28v=office.14%29.aspx
            // - <w:p>
            // - <w:pPr>
            // <w:pStyle w:val="style0" />
            // - <w:numPr>
            // <w:ilvl w:val="0" />
            // <w:numId w:val="2" />
            // </w:numPr>

            // get numbering.xml/w:num
            /**
             * <w:num w:numId="2"> <w:abstractNumId w:val="1" /> </w:num>
             */
            XWPFNum num = getXWPFNum( numPr );
            if ( num != null )
            {
                // get the abstractNum by usisng abstractNumId
                /**
                 * <w:abstractNum w:abstractNumId="1"> <w:nsid w:val="3CBA6E67" /> <w:multiLevelType
                 * w:val="hybridMultilevel" /> <w:tmpl w:val="7416D4FA" /> - <w:lvl w:ilvl="0" w:tplc="040C0001">
                 * <w:start w:val="1" /> <w:numFmt w:val="bullet" /> <w:lvlText w:val="o" /> <w:lvlJc w:val="left" /> -
                 * <w:pPr> <w:ind w:left="720" w:hanging="360" /> </w:pPr> - <w:rPr> <w:rFonts w:ascii="Symbol"
                 * w:hAnsi="Symbol" w:hint="default" /> </w:rPr> </w:lvl>
                 */
                XWPFAbstractNum abstractNum = getXWPFAbstractNum( num );

                // get the <w:lvl by using abstractNum and numPr level
                /**
                 * <w:num w:numId="2"> <w:abstractNumId w:val="1" /> </w:num>
                 */
                CTDecimalNumber ilvl = numPr.getIlvl();
                int level = ilvl != null ? ilvl.getVal().intValue() : 0;

                CTLvl lvl = abstractNum.getAbstractNum().getLvlArray( level );
                if ( lvl != null )
                {
                    ListContext listContext = getListContext( originalNumPr.getNumId().getVal().intValue() );
                    itemContext = listContext.addItem( lvl );
                }
            }

        }
        T paragraphContainer = startVisitParagraph( paragraph, itemContext, container );
        visitParagraphBody( paragraph, index, paragraphContainer );
        endVisitParagraph( paragraph, container, paragraphContainer );
    }

    private CTNumPr getNumPr( CTNumPr numPr )
    {
        if ( numPr != null )
        {
            XWPFNum num = getXWPFNum( numPr );
            if ( num != null )
            {
                // get the abstractNum by usisng abstractNumId
                /**
                 * <w:abstractNum w:abstractNumId="1"> <w:nsid w:val="3CBA6E67" /> <w:multiLevelType
                 * w:val="hybridMultilevel" /> <w:tmpl w:val="7416D4FA" /> - <w:lvl w:ilvl="0" w:tplc="040C0001">
                 * <w:start w:val="1" /> <w:numFmt w:val="bullet" /> <w:lvlText w:val="o" /> <w:lvlJc w:val="left" /> -
                 * <w:pPr> <w:ind w:left="720" w:hanging="360" /> </w:pPr> - <w:rPr> <w:rFonts w:ascii="Symbol"
                 * w:hAnsi="Symbol" w:hint="default" /> </w:rPr> </w:lvl>
                 */
                XWPFAbstractNum abstractNum = getXWPFAbstractNum( num );

                CTString numStyleLink = abstractNum.getAbstractNum().getNumStyleLink();
                String styleId = numStyleLink != null ? numStyleLink.getVal() : null;
                if ( styleId != null )
                {

                    // has w:numStyleLink which reference other style
                    /*
                     * <w:abstractNum w:abstractNumId="0"> <w:nsid w:val="03916EF0"/> <w:multiLevelType
                     * w:val="multilevel"/> <w:tmpl w:val="0409001D"/> <w:numStyleLink w:val="EricsListStyle"/>
                     * </w:abstractNum>
                     */
                    CTStyle style = stylesDocument.getStyle( styleId );
                    CTPPr ppr = style.getPPr();
                    if ( ppr == null )
                    {
                        return null;
                    }
                    return getNumPr( ppr.getNumPr() );
                }
            }
        }
        return numPr;
    }

    private ListContext getListContext( int numId )
    {
        if ( listContextMap == null )
        {
            listContextMap = new HashMap<Integer, ListContext>();
        }
        ListContext listContext = listContextMap.get( numId );
        if ( listContext == null )
        {
            listContext = new ListContext();
            listContextMap.put( numId, listContext );
        }
        return listContext;
    }

    protected abstract T startVisitParagraph( XWPFParagraph paragraph, ListItemContext itemContext, T parentContainer )
        throws Exception;

    protected abstract void endVisitParagraph( XWPFParagraph paragraph, T parentContainer, T paragraphContainer )
        throws Exception;

    protected void visitParagraphBody( XWPFParagraph paragraph, int index, T paragraphContainer )
        throws Exception
    {
        List<XWPFRun> runs = paragraph.getRuns();
        if ( runs.isEmpty() )
        {
            // a new line must be generated if :
            // - there is next paragraph/table
            // - if the body is a cell (with none vMerge) and contains just this paragraph
            if ( isAddNewLine( paragraph, index ) )
            {
                visitEmptyRun( paragraphContainer );
            }

            // sometimes, POI tells that run is empty
            // but it can be have w:r in the w:pPr
            // <w:p><w:pPr .. <w:r> => See the header1.xml of DocxBig.docx ,
            // => test if it exist w:r
            // CTP p = paragraph.getCTP();
            // CTPPr pPr = p.getPPr();
            // if (pPr != null) {
            // XmlObject[] wRuns =
            // pPr.selectPath("declare namespace w='http://schemas.openxmlformats.org/wordprocessingml/2006/main' .//w:r");
            // if (wRuns != null) {
            // for ( int i = 0; i < wRuns.length; i++ )
            // {
            // XmlObject o = wRuns[i];
            // o.getDomNode().getParentNode()
            // if (o instanceof CTR) {
            // System.err.println(wRuns[i]);
            // }
            //
            // }
            // }
            // }
            // //XmlObject[] t =
            // o.selectPath("declare namespace w='http://schemas.openxmlformats.org/wordprocessingml/2006/main' .//w:t");
            // //paragraph.getCTP().get
        }
        else
        {
            // Loop for each element of <w:r, w:fldSimple
            // to keep the order of those elements.
            visitRuns( paragraph, paragraphContainer );
        }

        // Page Break
        // Cannot use paragraph.isPageBreak() because it throws NPE because
        // pageBreak.getVal() can be null.
        CTPPr ppr = paragraph.getCTP().getPPr();
        if ( ppr != null )
        {
            if ( ppr.isSetPageBreakBefore() )
            {
                CTOnOff pageBreak = ppr.getPageBreakBefore();
                if ( pageBreak != null
                    && ( pageBreak.getVal() == null || pageBreak.getVal().intValue() == STOnOff.INT_TRUE ) )
                {
                    pageBreak();
                }
            }
        }
    }

    // ------------------------ Numbering --------------

    protected XWPFNum getXWPFNum( CTNumPr numPr )
    {
        CTDecimalNumber numID = numPr.getNumId();
        if ( numID == null )
        {
            // numID can be null, ignore the numbering
            // see https://code.google.com/p/xdocreport/issues/detail?id=239
            return null;
        }
        XWPFNum num = document.getNumbering().getNum( numID.getVal() );
        return num;
    }

    protected XWPFAbstractNum getXWPFAbstractNum( XWPFNum num )
    {
        CTDecimalNumber abstractNumID = num.getCTNum().getAbstractNumId();
        XWPFAbstractNum abstractNum = document.getNumbering().getAbstractNum( abstractNumID.getVal() );
        return abstractNum;
    }

    /**
     * Returns true if the given paragraph which is empty (none <w:r> run) must generate new line and false otherwise.
     * 
     * @param paragraph
     * @param index
     * @return
     */
    private boolean isAddNewLine( XWPFParagraph paragraph, int index )
    {
        // a new line must be generated if :
        // - there is next paragraph/table
        // - if the body is a cell (with none vMerge) and contains just this paragraph
        IBody body = paragraph.getBody();
        List<IBodyElement> bodyElements = body.getBodyElements();
        if ( body.getPartType() == BodyType.TABLECELL && bodyElements.size() == 1 )
        {
            XWPFTableCell cell = (XWPFTableCell) body;
            STMerge.Enum vMerge = stylesDocument.getTableCellVMerge( cell );
            if ( vMerge != null && vMerge.equals( STMerge.CONTINUE ) )
            {
                // here a new line must not be generated because the body is a cell (with none vMerge) and contains just
                // this paragraph
                return false;
            }
            // Loop for each cell of the row : if all cells are empty, new line must be generated otherwise none empty
            // line must be generated.
            XWPFTableRow row = cell.getTableRow();
            List<XWPFTableCell> cells = row.getTableCells();
            for ( XWPFTableCell c : cells )
            {
                if ( c.getBodyElements().size() != 1 )
                {
                    return false;
                }
                IBodyElement element = c.getBodyElements().get( 0 );
                if ( element.getElementType() != BodyElementType.PARAGRAPH )
                {
                    return false;
                }
                return ( (XWPFParagraph) element ).getRuns().size() == 0;
            }
            return true;

        }
        // here a new line must be generated if there is next paragraph/table
        return bodyElements.size() > index + 1;
    }

    private void visitRuns( XWPFParagraph paragraph, T paragraphContainer )
        throws Exception
    {
        boolean fldCharTypeParsing = false;
        boolean pageNumber = false;
        String url = null;
        List<XmlObject> rListAfterSeparate = null;

        CTP ctp = paragraph.getCTP();
        XmlCursor c = ctp.newCursor();
        c.selectPath( "child::*" );
        while ( c.toNextSelection() )
        {
            XmlObject o = c.getObject();
            if ( o instanceof CTR )
            {
                /*
                 * Test if it's : <w:r> <w:rPr /> <w:fldChar w:fldCharType="begin" /> </w:r>
                 */
                CTR r = (CTR) o;
                STFldCharType.Enum fldCharType = XWPFRunHelper.getFldCharType( r );
                if ( fldCharType != null )
                {
                    if ( fldCharType.equals( STFldCharType.BEGIN ) )
                    {
                        process( paragraph, paragraphContainer, pageNumber, url, rListAfterSeparate );
                        fldCharTypeParsing = true;
                        rListAfterSeparate = new ArrayList<XmlObject>();
                        pageNumber = false;
                        url = null;
                    }
                    else if ( fldCharType.equals( STFldCharType.END ) )
                    {

                        process( paragraph, paragraphContainer, pageNumber, url, rListAfterSeparate );
                        fldCharTypeParsing = false;
                        rListAfterSeparate = null;
                        pageNumber = false;
                        url = null;
                    }
                }
                else
                {
                    if ( fldCharTypeParsing )
                    {
                        String instrText = XWPFRunHelper.getInstrText( r );
                        if ( instrText != null )
                        {
                            if ( StringUtils.isNotEmpty( instrText ) )
                            {
                                // test if it's <w:r><w:instrText>PAGE</w:instrText></w:r>
                                boolean instrTextPage = XWPFRunHelper.isInstrTextPage( instrText );
                                if ( !instrTextPage )
                                {
                                    // test if it's <w:instrText>HYPERLINK
                                    // "http://code.google.com/p/xdocrepor"</w:instrText>
                                    String instrTextHyperlink = XWPFRunHelper.getInstrTextHyperlink( instrText );
                                    if ( instrTextHyperlink != null )
                                    {
                                        url = instrTextHyperlink;
                                    }
                                }
                                else
                                {
                                    pageNumber = true;
                                }
                            }
                        }
                        else
                        {
                            rListAfterSeparate.add( r );
                        }
                    }
                    else
                    {
                        XWPFRun run = new XWPFRun( r, paragraph );
                        visitRun( run, false, null, paragraphContainer );
                    }
                }
            }
            else
            {
                if ( fldCharTypeParsing )
                {
                    rListAfterSeparate.add( o );
                }
                else
                {
                    visitRun( paragraph, o, paragraphContainer );
                }
            }
        }
        c.dispose();
        process( paragraph, paragraphContainer, pageNumber, url, rListAfterSeparate );
        fldCharTypeParsing = false;
        rListAfterSeparate = null;
        pageNumber = false;
        url = null;
    }

    private void process( XWPFParagraph paragraph, T paragraphContainer, boolean pageNumber, String url,
                          List<XmlObject> rListAfterSeparate )
        throws Exception
    {
        if ( rListAfterSeparate != null )
        {
            for ( XmlObject oAfterSeparate : rListAfterSeparate )
            {
                if ( oAfterSeparate instanceof CTR )
                {
                    CTR ctr = (CTR) oAfterSeparate;
                    XWPFRun run = new XWPFRun( ctr, paragraph );
                    visitRun( run, pageNumber, url, paragraphContainer );
                }
                else
                {
                    visitRun( paragraph, oAfterSeparate, paragraphContainer );
                }
            }
        }
    }

    private void visitRun( XWPFParagraph paragraph, XmlObject o, T paragraphContainer )
        throws Exception
    {
        if ( o instanceof CTHyperlink )
        {
            CTHyperlink link = (CTHyperlink) o;
            String anchor = link.getAnchor();
            String href = null;
            // Test if the is an id for hyperlink
            String hyperlinkId = link.getId();
            if ( StringUtils.isNotEmpty( hyperlinkId ) )
            {
                XWPFHyperlink hyperlink = document.getHyperlinkByID( hyperlinkId );
                href = hyperlink != null ? hyperlink.getURL() : null;
            }
            for ( CTR r : link.getRList() )
            {
                XWPFRun run = new XWPFHyperlinkRun( link, r, paragraph );
                visitRun( run, false, href != null ? href : "#" + anchor, paragraphContainer );
            }
        }
        else if ( o instanceof CTSdtRun )
        {
            CTSdtContentRun run = ( (CTSdtRun) o ).getSdtContent();
            for ( CTR r : run.getRList() )
            {
                XWPFRun ru = new XWPFRun( r, paragraph );
                visitRun( ru, false, null, paragraphContainer );
            }
        }
        else if ( o instanceof CTRunTrackChange )
        {
            for ( CTR r : ( (CTRunTrackChange) o ).getRList() )
            {
                XWPFRun run = new XWPFRun( r, paragraph );
                visitRun( run, false, null, paragraphContainer );
            }
        }
        else if ( o instanceof CTSimpleField )
        {
            CTSimpleField simpleField = (CTSimpleField) o;
            String instr = simpleField.getInstr();
            // 1) test if it's page number
            // <w:fldSimple w:instr=" PAGE \* MERGEFORMAT "> <w:r> <w:rPr> <w:noProof/>
            // </w:rPr> <w:t>- 1 -</w:t> </w:r> </w:fldSimple>
            boolean fieldPageNumber = XWPFRunHelper.isInstrTextPage( instr );
            String fieldHref = null;
            if ( !fieldPageNumber )
            {
                // not page number, test if it's hyperlink :
                // <w:instrText>HYPERLINK "http://code.google.com/p/xdocrepor"</w:instrText>
                fieldHref = XWPFRunHelper.getInstrTextHyperlink( instr );
            }
            for ( CTR r : simpleField.getRList() )
            {
                XWPFRun run = new XWPFRun( r, paragraph );
                visitRun( run, fieldPageNumber, fieldHref, paragraphContainer );
            }
        }
        else if ( o instanceof CTSmartTagRun )
        {
            // Smart Tags can be nested many times.
            // This implementation does not preserve the tagging information
            // buildRunsInOrderFromXml(o);
        }
        else if ( o instanceof CTBookmark )
        {
            CTBookmark bookmark = (CTBookmark) o;
            visitBookmark( bookmark, paragraph, paragraphContainer );
        }
    }

    protected abstract void visitEmptyRun( T paragraphContainer )
        throws Exception;

    protected void visitRun( XWPFRun run, boolean pageNumber, String url, T paragraphContainer )
        throws Exception

    {
        CTR ctr = run.getCTR();

        // Loop for each element of <w:run text, tab, image etc
        // to keep the order of thoses elements.
        XmlCursor c = ctr.newCursor();
        c.selectPath( "./*" );
        while ( c.toNextSelection() )
        {
            XmlObject o = c.getObject();

            if ( o instanceof CTText )
            {
                CTText ctText = (CTText) o;
                String tagName = o.getDomNode().getNodeName();
                // Field Codes (w:instrText, defined in spec sec. 17.16.23)
                // come up as instances of CTText, but we don't want them
                // in the normal text output
                if ( "w:instrText".equals( tagName ) )
                {

                }
                else
                {
                    visitText( ctText, pageNumber, paragraphContainer );
                }
            }
            else if ( o instanceof CTPTab )
            {
                visitTab( (CTPTab) o, paragraphContainer );
            }
            else if ( o instanceof CTBr )
            {
                visitBR( (CTBr) o, paragraphContainer );
            }
            else if ( o instanceof CTEmpty )
            {
                // Some inline text elements get returned not as
                // themselves, but as CTEmpty, owing to some odd
                // definitions around line 5642 of the XSDs
                // This bit works around it, and replicates the above
                // rules for that case
                String tagName = o.getDomNode().getNodeName();
                if ( "w:tab".equals( tagName ) )
                {
                    CTTabs tabs = stylesDocument.getParagraphTabs( run.getParagraph() );
                    visitTabs( tabs, paragraphContainer );
                }
                if ( "w:br".equals( tagName ) )
                {
                    visitBR( null, paragraphContainer );
                }
                if ( "w:cr".equals( tagName ) )
                {
                    visitBR( null, paragraphContainer );
                }
            }
            else if ( o instanceof CTDrawing )
            {
                visitDrawing( (CTDrawing) o, paragraphContainer );
            }
        }
        c.dispose();
    }

    protected abstract void visitText( CTText ctText, boolean pageNumber, T paragraphContainer )
        throws Exception;

    protected abstract void visitTab( CTPTab o, T paragraphContainer )
        throws Exception;

    protected abstract void visitTabs( CTTabs tabs, T paragraphContainer )
        throws Exception;

    protected void visitBR( CTBr br, T paragraphContainer )
        throws Exception
    {
        STBrType.Enum brType = XWPFRunHelper.getBrType( br );
        if ( brType.equals( STBrType.PAGE ) )
        {
            pageBreakOnNextParagraph = true;
        }
        else
        {
            addNewLine( br, paragraphContainer );
        }
    }

    protected abstract void visitBookmark( CTBookmark bookmark, XWPFParagraph paragraph, T paragraphContainer )
        throws Exception;

    protected abstract void addNewLine( CTBr br, T paragraphContainer )
        throws Exception;

    protected abstract void pageBreak()
        throws Exception;

    protected void visitTable( XWPFTable table, int index, T container )
        throws Exception
    {
        // 1) Compute colWidth
        float[] colWidths = XWPFTableUtil.computeColWidths( table );
        T tableContainer = startVisitTable( table, colWidths, container );
        visitTableBody( table, colWidths, tableContainer );
        endVisitTable( table, container, tableContainer );
    }

    protected void visitTableBody( XWPFTable table, float[] colWidths, T tableContainer )
        throws Exception
    {
        // Proces Row
        boolean firstRow = false;
        boolean lastRow = false;

        List<XWPFTableRow> rows = table.getRows();
        int rowsSize = rows.size();
        for ( int i = 0; i < rowsSize; i++ )
        {
            firstRow = ( i == 0 );
            lastRow = isLastRow( i, rowsSize );
            XWPFTableRow row = rows.get( i );
            visitTableRow( row, colWidths, tableContainer, firstRow, lastRow, i, rowsSize );
        }
    }

    private boolean isLastRow( int rowIndex, int rowsSize )
    {
        return rowIndex == rowsSize - 1;
    }

    protected abstract T startVisitTable( XWPFTable table, float[] colWidths, T tableContainer )
        throws Exception;

    protected abstract void endVisitTable( XWPFTable table, T parentContainer, T tableContainer )
        throws Exception;

    protected void visitTableRow( XWPFTableRow row, float[] colWidths, T tableContainer, boolean firstRow,
                                  boolean lastRowIfNoneVMerge, int rowIndex, int rowsSize )
        throws Exception
    {

        boolean headerRow = stylesDocument.isTableRowHeader( row );
        startVisitTableRow( row, tableContainer, rowIndex, headerRow );

        int nbColumns = colWidths.length;
        // Process cell
        boolean firstCol = true;
        boolean lastCol = false;
        boolean lastRow = false;
        List<XWPFTableCell> vMergedCells = null;
        List<XWPFTableCell> cells = row.getTableCells();
        if ( nbColumns > cells.size() )
        {
            // Columns number is not equal to cells number.
            // POI have a bug with
            // <w:tr w:rsidR="00C55C20">
            // <w:tc>
            // <w:tc>...
            // <w:sdt>
            // <w:sdtContent>
            // <w:tc> <= this tc which is a XWPFTableCell is not included in the row.getTableCells();

            firstCol = true;
            int cellIndex = -1;
            CTRow ctRow = row.getCtRow();
            XmlCursor c = ctRow.newCursor();
            c.selectPath( "./*" );
            while ( c.toNextSelection() )
            {
                XmlObject o = c.getObject();
                if ( o instanceof CTTc )
                {
                    CTTc tc = (CTTc) o;
                    XWPFTableCell cell = row.getTableCell( tc );
                    cellIndex = getCellIndex( cellIndex, cell );
                    lastCol = ( cellIndex == nbColumns );
                    vMergedCells = getVMergedCells( cell, rowIndex, cellIndex );
                    if ( vMergedCells == null || vMergedCells.size() > 0 )
                    {
                        lastRow = isLastRow( lastRowIfNoneVMerge, rowIndex, rowsSize, vMergedCells );
                        visitCell( cell, tableContainer, firstRow, lastRow, firstCol, lastCol, rowIndex, cellIndex,
                                   vMergedCells );
                    }
                    firstCol = false;
                }
                else if ( o instanceof CTSdtCell )
                {
                    // Fix bug of POI
                    CTSdtCell sdtCell = (CTSdtCell) o;
                    List<CTTc> tcList = sdtCell.getSdtContent().getTcList();
                    for ( CTTc ctTc : tcList )
                    {
                        XWPFTableCell cell = new XWPFTableCell( ctTc, row, row.getTable().getBody() );
                        cellIndex = getCellIndex( cellIndex, cell );
                        lastCol = ( cellIndex == nbColumns );
                        vMergedCells = getVMergedCells( cell, rowIndex, cellIndex );
                        if ( vMergedCells == null || vMergedCells.size() > 0 )
                        {
                            lastRow = isLastRow( lastRowIfNoneVMerge, rowIndex, rowsSize, vMergedCells );
                            visitCell( cell, tableContainer, firstRow, lastRow, firstCol, lastCol, rowIndex, cellIndex,
                                       vMergedCells );
                        }
                        firstCol = false;
                    }
                }
            }
            c.dispose();
        }
        else
        {
            // Column number is equal to cells number.
            for ( int i = 0; i < cells.size(); i++ )
            {
                lastCol = ( i == cells.size() - 1 );
                XWPFTableCell cell = cells.get( i );
                vMergedCells = getVMergedCells( cell, rowIndex, i );
                if ( vMergedCells == null || vMergedCells.size() > 0 )
                {
                    lastRow = isLastRow( lastRowIfNoneVMerge, rowIndex, rowsSize, vMergedCells );
                    visitCell( cell, tableContainer, firstRow, lastRow, firstCol, lastCol, rowIndex, i, vMergedCells );
                }
                firstCol = false;
            }
        }

        endVisitTableRow( row, tableContainer, firstRow, lastRow, headerRow );
    }

    private boolean isLastRow( boolean lastRowIfNoneVMerge, int rowIndex, int rowsSize, List<XWPFTableCell> vMergedCells )
    {
        if ( vMergedCells == null )
        {
            return lastRowIfNoneVMerge;
        }
        return isLastRow( rowIndex - 1 + vMergedCells.size(), rowsSize );
    }

    private int getCellIndex( int cellIndex, XWPFTableCell cell )
    {
        BigInteger gridSpan = stylesDocument.getTableCellGridSpan( cell.getCTTc().getTcPr() );
        if ( gridSpan != null )
        {
            cellIndex = cellIndex + gridSpan.intValue();
        }
        else
        {
            cellIndex++;
        }
        return cellIndex;
    }

    protected void startVisitTableRow( XWPFTableRow row, T tableContainer, int rowIndex, boolean headerRow )
        throws Exception
    {

    }

    protected void endVisitTableRow( XWPFTableRow row, T tableContainer, boolean firstRow, boolean lastRow,
                                     boolean headerRow )
        throws Exception
    {

    }

    protected void visitCell( XWPFTableCell cell, T tableContainer, boolean firstRow, boolean lastRow,
                              boolean firstCol, boolean lastCol, int rowIndex, int cellIndex,
                              List<XWPFTableCell> vMergedCells )
        throws Exception
    {
        T tableCellContainer =
            startVisitTableCell( cell, tableContainer, firstRow, lastRow, firstCol, lastCol, vMergedCells );
        visitTableCellBody( cell, vMergedCells, tableCellContainer );
        endVisitTableCell( cell, tableContainer, tableCellContainer );
    }

    private List<XWPFTableCell> getVMergedCells( XWPFTableCell cell, int rowIndex, int cellIndex )
    {
        List<XWPFTableCell> vMergedCells = null;
        STMerge.Enum vMerge = stylesDocument.getTableCellVMerge( cell );
        if ( vMerge != null )
        {
            if ( vMerge.equals( STMerge.RESTART ) )
            {
                // vMerge="restart"
                // Loop for each table cell of each row upon vMerge="restart" was found or cell without vMerge
                // was declared.
                vMergedCells = new ArrayList<XWPFTableCell>();
                vMergedCells.add( cell );

                XWPFTableRow row = null;
                XWPFTableCell c;
                XWPFTable table = cell.getTableRow().getTable();
                for ( int i = rowIndex + 1; i < table.getRows().size(); i++ )
                {
                    row = table.getRow( i );
                    c = row.getCell( cellIndex );
                    if ( c == null )
                    {
                        break;
                    }
                    vMerge = stylesDocument.getTableCellVMerge( c );
                    if ( vMerge != null && vMerge.equals( STMerge.CONTINUE ) )
                    {

                        vMergedCells.add( c );
                    }
                    else
                    {
                        return vMergedCells;
                    }
                }
            }
            else
            {
                // vMerge="continue", ignore the cell because it was already processed
                return Collections.emptyList();
            }
        }
        return vMergedCells;
    }

    protected void visitTableCellBody( XWPFTableCell cell, List<XWPFTableCell> vMergeCells, T tableCellContainer )
        throws Exception
    {
        if ( vMergeCells != null )
        {

            for ( XWPFTableCell mergedCell : vMergeCells )
            {
                List<IBodyElement> bodyElements = mergedCell.getBodyElements();
                visitBodyElements( bodyElements, tableCellContainer );
            }
        }
        else
        {
            List<IBodyElement> bodyElements = cell.getBodyElements();
            visitBodyElements( bodyElements, tableCellContainer );
        }
    }

    protected abstract T startVisitTableCell( XWPFTableCell cell, T tableContainer, boolean firstRow, boolean lastRow,
                                              boolean firstCol, boolean lastCol, List<XWPFTableCell> vMergeCells )
        throws Exception;

    protected abstract void endVisitTableCell( XWPFTableCell cell, T tableContainer, T tableCellContainer )
        throws Exception;

    protected XWPFStyle getXWPFStyle( String styleID )
    {
        if ( styleID == null )
            return null;
        else
            return document.getStyles().getStyle( styleID );
    }

    /**
     * Returns true if word/document.xml is parsing and false otherwise.
     * 
     * @return true if word/document.xml is parsing and false otherwise.
     */
    protected boolean isWordDocumentPartParsing()
    {
        return currentHeader == null && currentFooter == null;
    }

    // ------------------------------ Header/Footer visitor -----------

    public void visitHeaderRef( CTHdrFtrRef headerRef, CTSectPr sectPr, E masterPage )
        throws Exception
    {
        this.currentHeader = getXWPFHeader( headerRef );
        visitHeader( currentHeader, headerRef, sectPr, masterPage );
        this.currentHeader = null;
    }

    protected abstract void visitHeader( XWPFHeader header, CTHdrFtrRef headerRef, CTSectPr sectPr, E masterPage )
        throws Exception;

    public void visitFooterRef( CTHdrFtrRef footerRef, CTSectPr sectPr, E masterPage )
        throws Exception
    {
        this.currentFooter = getXWPFFooter( footerRef );
        visitFooter( currentFooter, footerRef, sectPr, masterPage );
        this.currentFooter = null;
    }

    protected abstract void visitFooter( XWPFFooter footer, CTHdrFtrRef footerRef, CTSectPr sectPr, E masterPage )
        throws Exception;

    /**
     * Returns the list of {@link IBodyElement} of the given header/footer. We do that because
     * {@link XWPFHeaderFooter#getBodyElements()} doesn't contains the // <w:sdt><w:sdtContent>
     * <p
     * (see JUnit Docx4j_GettingStarted, DocXperT_Output_4_3, Issue222 which defines page number in the <w:sdt. ...
     * 
     * @param part
     * @return
     */
    protected List<IBodyElement> getBodyElements( XWPFHeaderFooter part )
    {
        List<IBodyElement> bodyElements = new ArrayList<IBodyElement>();
        XmlTokenSource headerFooter = part._getHdrFtr();
        addBodyElements( headerFooter, part, bodyElements );
        return bodyElements;
    }

    /**
     * Add body elements from the given token source.
     * 
     * @param source
     * @param part
     * @param bodyElements
     */
    private void addBodyElements( XmlTokenSource source, IBody part, List<IBodyElement> bodyElements )
    {
        // parse the document with cursor and add
        // the XmlObject to its lists
        XmlCursor cursor = source.newCursor();
        cursor.selectPath( "./*" );
        while ( cursor.toNextSelection() )
        {
            XmlObject o = cursor.getObject();
            if ( o instanceof CTSdtBlock )
            {
                // <w:sdt><w:sdtContent><p...
                CTSdtBlock block = (CTSdtBlock) o;
                CTSdtContentBlock contentBlock = block.getSdtContent();
                if ( contentBlock != null )
                {
                    addBodyElements( contentBlock, part, bodyElements );
                }
            }
            else if ( o instanceof CTP )
            {
                XWPFParagraph p = new XWPFParagraph( (CTP) o, part );
                bodyElements.add( p );
            }
            else if ( o instanceof CTTbl )
            {
                XWPFTable t = new XWPFTable( (CTTbl) o, part );
                bodyElements.add( t );
            }
        }
        cursor.dispose();
    }

    /**
     * Returns the {@link XWPFHeader} of the given header reference.
     * 
     * @param headerref the header reference.
     * @return
     * @throws XmlException
     * @throws IOException
     */
    protected XWPFHeader getXWPFHeader( CTHdrFtrRef headerRef )
        throws XmlException, IOException
    {
        PackagePart hdrPart = document.getPartById( headerRef.getId() );
        List<XWPFHeader> headers = document.getHeaderList();
        for ( XWPFHeader header : headers )
        {
            if ( header.getPackagePart().equals( hdrPart ) )
            {
                // header is aleady loaded, return it.
                return header;
            }
        }
        // should never come, but load the header if needed.
        HdrDocument hdrDoc = HdrDocument.Factory.parse( hdrPart.getInputStream() );
        CTHdrFtr hdrFtr = hdrDoc.getHdr();
        XWPFHeader hdr = new XWPFHeader( document, hdrFtr );
        return hdr;
    }

    /**
     * Returns the {@link XWPFFooter} of the given footer reference.
     * 
     * @param footerRef the footer reference.
     * @return
     * @throws XmlException
     * @throws IOException
     */
    protected XWPFFooter getXWPFFooter( CTHdrFtrRef footerRef )
        throws XmlException, IOException
    {
        PackagePart hdrPart = document.getPartById( footerRef.getId() );
        List<XWPFFooter> footers = document.getFooterList();
        for ( XWPFFooter footer : footers )
        {
            if ( footer.getPackagePart().equals( hdrPart ) )
            {
                // footer is aleady loaded, return it.
                return footer;
            }
        }
        // should never come, but load the footer if needed.
        FtrDocument hdrDoc = FtrDocument.Factory.parse( hdrPart.getInputStream() );
        CTHdrFtr hdrFtr = hdrDoc.getFtr();
        XWPFFooter ftr = new XWPFFooter( document, hdrFtr );
        return ftr;
    }

    // ------------------------ Image --------------

    protected void visitDrawing( CTDrawing drawing, T parentContainer )
        throws Exception
    {
        List<CTInline> inlines = drawing.getInlineList();
        for ( CTInline inline : inlines )
        {
            visitInline( inline, parentContainer );
        }
        List<CTAnchor> anchors = drawing.getAnchorList();
        for ( CTAnchor anchor : anchors )
        {
            visitAnchor( anchor, parentContainer );
        }
    }

    protected void visitAnchor( CTAnchor anchor, T parentContainer )
        throws Exception
    {
        CTGraphicalObject graphic = anchor.getGraphic();

        /*
         * wp:positionH relativeFrom="column"> <wp:posOffset>-898525</wp:posOffset> </wp:positionH>
         */
        STRelFromH.Enum relativeFromH = null;
        Float offsetX = null;
        CTPosH positionH = anchor.getPositionH();
        if ( positionH != null )
        {
            relativeFromH = positionH.getRelativeFrom();
            offsetX = DxaUtil.emu2points( positionH.getPosOffset() );
        }

        STRelFromV.Enum relativeFromV = null;
        Float offsetY = null;
        CTPosV positionV = anchor.getPositionV();
        if ( positionV != null )
        {
            relativeFromV = positionV.getRelativeFrom();
            offsetY = DxaUtil.emu2points( positionV.getPosOffset() );
        }

        STWrapText.Enum wrapText = null;
        CTWrapSquare wrapSquare = anchor.getWrapSquare();
        if ( wrapSquare != null )
        {
            wrapText = wrapSquare.getWrapText();
        }

        visitGraphicalObject( parentContainer, graphic, offsetX, relativeFromH, offsetY, relativeFromV, wrapText );
    }

    protected void visitInline( CTInline inline, T parentContainer )
        throws Exception
    {
        CTGraphicalObject graphic = inline.getGraphic();
        visitGraphicalObject( parentContainer, graphic, null, null, null, null, null );
    }

    private void visitGraphicalObject( T parentContainer, CTGraphicalObject graphic, Float offsetX,
                                       STRelFromH.Enum relativeFromH, Float offsetY, STRelFromV.Enum relativeFromV,
                                       STWrapText.Enum wrapText )
        throws Exception
    {
        if ( graphic != null )
        {
            CTGraphicalObjectData graphicData = graphic.getGraphicData();
            if ( graphicData != null )
            {
                XmlCursor c = graphicData.newCursor();
                c.selectPath( "./*" );
                while ( c.toNextSelection() )
                {
                    XmlObject o = c.getObject();
                    if ( o instanceof CTPicture )
                    {
                        CTPicture picture = (CTPicture) o;
                        // extract the picture if needed
                        IImageExtractor extractor = getImageExtractor();
                        if ( extractor != null )
                        {
                            XWPFPictureData pictureData = getPictureData( picture );
                            if ( pictureData != null )
                            {
                                try
                                {
                                    extractor.extract( WORD_MEDIA + pictureData.getFileName(), pictureData.getData() );
                                }
                                catch ( Throwable e )
                                {
                                    LOGGER.log( Level.SEVERE,
                                                "Error while extracting the image " + pictureData.getFileName(), e );
                                }
                            }
                        }
                        // visit the picture.
                        visitPicture( picture, offsetX, relativeFromH, offsetY, relativeFromV, wrapText,
                                      parentContainer );
                    }
                }
                c.dispose();
            }
        }
    }

    /**
     * Returns the picture data of the given image id.
     * 
     * @param blipId
     * @return
     */
    protected XWPFPictureData getPictureDataByID( String blipId )
    {
        if ( currentHeader != null )
        {
            return currentHeader.getPictureDataByID( blipId );
        }
        if ( currentFooter != null )
        {
            return currentFooter.getPictureDataByID( blipId );
        }
        return document.getPictureDataByID( blipId );
    }

    /**
     * Returns the image extractor and null otherwise.
     * 
     * @return
     */
    protected IImageExtractor getImageExtractor()
    {
        return options.getExtractor();
    }

    /**
     * Returns the picture data of the given picture.
     * 
     * @param picture
     * @return
     */
    public XWPFPictureData getPictureData( CTPicture picture )
    {
        String blipId = picture.getBlipFill().getBlip().getEmbed();
        return getPictureDataByID( blipId );
    }

    protected abstract void visitPicture( CTPicture picture, Float offsetX, STRelFromH.Enum relativeFromH,
                                          Float offsetY, STRelFromV.Enum relativeFromV, STWrapText.Enum wrapText,
                                          T parentContainer )
        throws Exception;

}
