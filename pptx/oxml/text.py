# encoding: utf-8

"""
lxml custom element classes for text-related XML elements.
"""

from __future__ import absolute_import

from . import parse_xml
from ..enum.text import (
    MSO_AUTO_SIZE, MSO_VERTICAL_ANCHOR, PP_PARAGRAPH_ALIGNMENT
)
from .ns import nsdecls
from .simpletypes import (
    ST_Coordinate32, ST_TextFontSize, ST_TextIndentLevelType,
    ST_TextTypeface, ST_TextWrappingType, XsdBoolean, XsdString
)
from ..util import Emu
from .xmlchemy import (
    BaseOxmlElement, Choice, OneAndOnlyOne, OneOrMore, OptionalAttribute,
    RequiredAttribute, ZeroOrMore, ZeroOrOne, ZeroOrOneChoice
)


class CT_Hyperlink(BaseOxmlElement):
    """
    Custom element class for <a:hlinkClick> elements.
    """
    rId = OptionalAttribute('r:id', XsdString)


class CT_RegularTextRun(BaseOxmlElement):
    """
    Custom element class for <a:r> elements.
    """
    rPr = ZeroOrOne('a:rPr', successors=('a:t',))
    t = OneAndOnlyOne('a:t')

    @property
    def text(self):
        """
        The text of the ``<a:t>`` child element.
        """
        return self.t.text


class CT_TextBody(BaseOxmlElement):
    """
    ``<p:txBody>`` custom element class, also used for ``<c:txPr>`` in
    charts and perhaps other elements.
    """
    bodyPr = OneAndOnlyOne('a:bodyPr')
    p = OneOrMore('a:p')

    @property
    def defRPr(self):
        """
        ``<a:defRPr>`` element of required first ``p`` child, added with its
        ancestors if not present. Used when element is a ``<c:txPr>`` in
        a chart and the ``p`` element is used only to specify formatting, not
        content.
        """
        p = self.p_lst[0]
        pPr = p.get_or_add_pPr()
        defRPr = pPr.get_or_add_defRPr()
        return defRPr

    @classmethod
    def new(cls):
        """
        Return a new ``<p:txBody>`` element tree
        """
        xml = cls._txBody_tmpl()
        txBody = parse_xml(xml)
        return txBody

    @classmethod
    def new_a_txBody(cls):
        """
        Return a new ``<a:txBody>`` element tree, suitable for use in a table
        cell and possibly other situations.
        """
        xml = cls._a_txBody_tmpl()
        txBody = parse_xml(xml)
        return txBody

    @classmethod
    def new_txPr(cls):
        """
        Return a ``<c:txPr>`` element tree suitable for use in a chart object
        like data labels or tick labels.
        """
        xml = (
            '<c:txPr %s>\n'
            '  <a:bodyPr/>\n'
            '  <a:lstStyle/>\n'
            '  <a:p>\n'
            '    <a:pPr>\n'
            '      <a:defRPr/>\n'
            '    </a:pPr>\n'
            '  </a:p>\n'
            '</c:txPr>\n'
        ) % nsdecls('c', 'a')
        txPr = parse_xml(xml)
        return txPr

    @classmethod
    def _a_txBody_tmpl(cls):
        return (
            '<a:txBody %s>\n'
            '  <a:bodyPr/>\n'
            '  <a:p/>\n'
            '</a:txBody>\n' % (nsdecls('a'))
        )

    @classmethod
    def _txBody_tmpl(cls):
        return (
            '<p:txBody %s>\n'
            '  <a:bodyPr/>\n'
            '  <a:lstStyle/>\n'
            '  <a:p/>\n'
            '</p:txBody>\n' % (nsdecls('a', 'p'))
        )


class CT_TextBodyProperties(BaseOxmlElement):
    """
    <a:bodyPr> custom element class
    """
    eg_textAutoFit = ZeroOrOneChoice((
        Choice('a:noAutofit'), Choice('a:normAutofit'),
        Choice('a:spAutoFit')),
        successors=('a:scene3d', 'a:sp3d', 'a:flatTx', 'a:extLst')
    )
    lIns = OptionalAttribute('lIns', ST_Coordinate32, default=Emu(91440))
    tIns = OptionalAttribute('tIns', ST_Coordinate32, default=Emu(45720))
    rIns = OptionalAttribute('rIns', ST_Coordinate32, default=Emu(91440))
    bIns = OptionalAttribute('bIns', ST_Coordinate32, default=Emu(45720))
    anchor = OptionalAttribute('anchor', MSO_VERTICAL_ANCHOR)
    wrap = OptionalAttribute('wrap', ST_TextWrappingType)

    @property
    def autofit(self):
        """
        The autofit setting for the textframe, a member of the
        ``MSO_AUTO_SIZE`` enumeration.
        """
        if self.noAutofit is not None:
            return MSO_AUTO_SIZE.NONE
        if self.normAutofit is not None:
            return MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
        if self.spAutoFit is not None:
            return MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT
        return None

    @autofit.setter
    def autofit(self, value):
        if value is not None and value not in MSO_AUTO_SIZE._valid_settings:
            raise ValueError(
                'only None or a member of the MSO_AUTO_SIZE enumeration can '
                'be assigned to CT_TextBodyProperties.autofit, got %s'
                % value
            )
        self._remove_eg_textAutoFit()
        if value == MSO_AUTO_SIZE.NONE:
            self._add_noAutofit()
        elif value == MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE:
            self._add_normAutofit()
        elif value == MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT:
            self._add_spAutoFit()


class CT_TextCharacterProperties(BaseOxmlElement):
    """
    Custom element class for all of <a:rPr>, <a:defRPr>, and <a:endParaRPr>
    elements. 'rPr' is short for 'run properties', and it corresponds to the
    |Font| proxy class.
    """
    eg_fillProperties = ZeroOrOneChoice((
        Choice('a:noFill'), Choice('a:solidFill'), Choice('a:gradFill'),
        Choice('a:blipFill'), Choice('a:pattFill'), Choice('a:grpFill')),
        successors=(
            'a:effectLst', 'a:effectDag', 'a:highlight', 'a:uLnTx', 'a:uLn',
            'a:uFillTx', 'a:uFill', 'a:latin', 'a:ea', 'a:cs', 'a:sym',
            'a:hlinkClick', 'a:hlinkMouseOver', 'a:rtl', 'a:extLst'
        )
    )
    latin = ZeroOrOne('a:latin', successors=(
        'a:ea', 'a:cs', 'a:sym', 'a:hlinkClick', 'a:hlinkMouseOver', 'a:rtl',
        'a:extLst'
    ))
    hlinkClick = ZeroOrOne('a:hlinkClick', successors=(
        'a:hlinkMouseOver', 'a:rtl', 'a:extLst'
    ))

    sz = OptionalAttribute('sz', ST_TextFontSize)
    b = OptionalAttribute('b', XsdBoolean)
    i = OptionalAttribute('i', XsdBoolean)

    def add_hlinkClick(self, rId):
        """
        Add an <a:hlinkClick> child element with r:id attribute set to *rId*.
        """
        hlinkClick = self.get_or_add_hlinkClick()
        hlinkClick.rId = rId
        return hlinkClick


class CT_TextField(BaseOxmlElement):
    """
    <a:fld> field element, for either a slide number or date field
    """
    t = ZeroOrOne('a:t', successors=())

    @property
    def text(self):
        """
        The text of the ``<a:t>`` child element.
        """
        t = self.t
        return '' if t is None else t.text


class CT_TextFont(BaseOxmlElement):
    """
    Custom element class for <a:latin>, <a:ea>, <a:cs>, and <a:sym> child
    elements of CT_TextCharacterProperties, e.g. <a:rPr>.
    """
    typeface = RequiredAttribute('typeface', ST_TextTypeface)


class CT_TextLineBreak(BaseOxmlElement):
    """
    <a:br> line break element
    """
    @property
    def text(self):
        """
        Unconditionally a single line feed character. A line break element
        can contain no text other than the implicit line feed it represents.
        """
        return '\n'


class CT_TextParagraph(BaseOxmlElement):
    """
    <a:p> custom element class
    """
    pPr = ZeroOrOne('a:pPr', successors=(
        'a:r', 'a:br', 'a:fld', 'a:endParaRPr'
    ))
    r = ZeroOrMore('a:r', successors=('a:endParaRPr',))
    br = ZeroOrMore('a:br', successors=('a:endParaRPr',))
    endParaRPr = ZeroOrOne('a:endParaRPr', successors=())

    def add_br(self):
        """
        Return a newly appended <a:br> element.
        """
        return self._add_br()

    def add_r(self, text=None):
        """
        Return a newly appended <a:r> element.
        """
        r = self._add_r()
        if text:
            r.t.text = text
        return r

    def append_text(self, text):
        """
        Add *text* at the end of this paragraph element, translating line
        feed characters ('\n') into ``<a:br>`` elements.
        """
        _ParagraphTextAppender.append_to_p_from_text(self, text)

    @property
    def content_children(self):
        """
        A sequence containing the text-container child elements of this
        ``<a:p>`` element, i.e. (a:r|a:br|a:fld).
        """
        text_types = (CT_RegularTextRun, CT_TextLineBreak, CT_TextField)
        return tuple(elm for elm in self if isinstance(elm, text_types))

    def remove_child_r_elms(self):
        """
        Return self after removing all <a:r> child elements.
        """
        for r in self.r_lst:
            self.remove(r)
        return self

    def _new_r(self):
        r_xml = '<a:r %s><a:t/></a:r>' % nsdecls('a')
        return parse_xml(r_xml)


class CT_TextParagraphProperties(BaseOxmlElement):
    """
    <a:pPr> custom element class
    """
    defRPr = ZeroOrOne('a:defRPr', successors=('a:extLst',))
    lvl = OptionalAttribute('lvl', ST_TextIndentLevelType, default=0)
    algn = OptionalAttribute('algn', PP_PARAGRAPH_ALIGNMENT)


class _ParagraphTextAppender(object):
    """
    Service object that knows how to translate a Python string into run and
    line break elements appended to a specified ``<a:p>`` element. Contiguous
    sequences of regular characters are appended in a single ``<a:r>``
    element. A newline character ('\n') causes a ``<a:br>`` element to be
    appended.
    """
    def __init__(self, p):
        self._p = p
        self._bfr = []

    @classmethod
    def append_to_p_from_text(cls, p, text):
        """
        Create a "one-shot" ``_ParagraphTextAppender`` instance and use it to
        append ``<a:r>`` and ``<a:br>`` elements to *p* that correspond to
        the contents of *text*.
        """
        appender = cls(p)
        appender._add_text(text)

    def _add_text(self, text):
        """
        Append the paragraph content elements corresponding to *text* to the
        ``<a:p>`` element of this instance.
        """
        for char in text:
            self._add_char(char)
        self._flush()

    def _add_char(self, char):
        """
        Process the next character of input through the translation finite
        state maching (FSM). There are two possible states, buffer pending
        and not pending, but those are hidden behind the ``.flush()`` method
        which must be called at the end of text to ensure any pending
        ``<a:r>`` element is written.
        """
        if char == '\n':
            self._flush()
            self._p.add_br()
        else:
            self._bfr.append(char)

    def _flush(self):
        text = ''.join(self._bfr)
        if text:
            self._p.add_r(text)
        del self._bfr[:]
