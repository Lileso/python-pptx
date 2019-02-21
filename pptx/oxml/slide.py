# encoding: utf-8

"""Slide-related custom element classes, including those for masters."""

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from pptx.oxml import parse_from_template, parse_xml
from pptx.oxml.dml.fill import CT_GradientFillProperties
from pptx.oxml.ns import nsdecls
from pptx.oxml.simpletypes import XsdString
from pptx.oxml.xmlchemy import (
    BaseOxmlElement, Choice, OneAndOnlyOne, OptionalAttribute,
    RequiredAttribute, ZeroOrMore, ZeroOrOne, ZeroOrOneChoice
)


class _BaseSlideElement(BaseOxmlElement):
    """
    Base class for the six slide types, providing common methods.
    """
    @property
    def spTree(self):
        """
        Return required `p:cSld/p:spTree` grandchild.
        """
        return self.cSld.spTree


class CT_Background(BaseOxmlElement):
    """`p:bg` element."""

    # ---these two are actually a choice, not a sequence, but simpler for
    # ---present purposes this way.
    _tag_seq = (
        'p:bgPr', 'p:bgRef'
    )
    bgPr = ZeroOrOne('p:bgPr', successors=())
    bgRef = ZeroOrOne('p:bgRef', successors=())
    del _tag_seq

    def add_noFill_bgPr(self):
        """Return a new `p:bgPr` element with noFill properties."""
        xml = (
            '<p:bgPr %s>\n'
            '  <a:noFill/>\n'
            '  <a:effectLst/>\n'
            '</p:bgPr>' % nsdecls('a', 'p')
        )
        bgPr = parse_xml(xml)
        self._insert_bgPr(bgPr)
        return bgPr


class CT_BackgroundProperties(BaseOxmlElement):
    """`p:bgPr` element."""

    _tag_seq = (
        'a:noFill', 'a:solidFill', 'a:gradFill', 'a:blipFill', 'a:pattFill',
        'a:grpFill', 'a:effectLst', 'a:effectDag', 'a:extLst',
    )
    eg_fillProperties = ZeroOrOneChoice(
        (
            Choice('a:noFill'), Choice('a:solidFill'), Choice('a:gradFill'),
            Choice('a:blipFill'), Choice('a:pattFill'), Choice('a:grpFill')
        ),
        successors=_tag_seq[6:]
    )
    del _tag_seq

    def _new_gradFill(self):
        """Override default to add default gradient subtree."""
        return CT_GradientFillProperties.new_gradFill()


class CT_CommonSlideData(BaseOxmlElement):
    """`p:cSld` element."""

    _tag_seq = (
        'p:bg', 'p:spTree', 'p:custDataLst', 'p:controls', 'p:extLst'
    )
    bg = ZeroOrOne('p:bg', successors=_tag_seq[1:])
    spTree = OneAndOnlyOne('p:spTree')
    del _tag_seq
    name = OptionalAttribute('name', XsdString, default='')

    def get_or_add_bgPr(self):
        """Return `p:bg/p:bgPr` grandchild.

        If no such grandchild is present, any existing `p:bg` child is first
        removed and a new default `p:bg` with noFill settings is added.
        """
        bg = self.bg
        if bg is None or bg.bgPr is None:
            self._change_to_noFill_bg()
        return self.bg.bgPr

    def _change_to_noFill_bg(self):
        """Establish a `p:bg` child with no-fill settings.

        Any existing `p:bg` child is first removed.
        """
        self._remove_bg()
        bg = self.get_or_add_bg()
        bg.add_noFill_bgPr()
        return bg


class CT_NotesMaster(_BaseSlideElement):
    """
    ``<p:notesMaster>`` element, root of a notes master part
    """
    _tag_seq = ('p:cSld', 'p:clrMap', 'p:hf', 'p:notesStyle', 'p:extLst')
    cSld = OneAndOnlyOne('p:cSld')
    del _tag_seq

    @classmethod
    def new_default(cls):
        """
        Return a new ``<p:notesMaster>`` element based on the built-in
        default template.
        """
        return parse_from_template('notesMaster')


class CT_NotesSlide(_BaseSlideElement):
    """
    ``<p:notes>`` element, root of a notes slide part
    """
    _tag_seq = ('p:cSld', 'p:clrMapOvr', 'p:extLst')
    cSld = OneAndOnlyOne('p:cSld')
    del _tag_seq

    @classmethod
    def new(cls):
        """
        Return a new ``<p:notes>`` element based on the default template.
        Note that the template does not include placeholders, which must be
        subsequently cloned from the notes master.
        """
        return parse_from_template('notes')


class CT_Slide(_BaseSlideElement):
    """`p:sld` element, root element of a slide part (XML document)."""

    _tag_seq = (
        'p:cSld', 'p:clrMapOvr', 'p:transition', 'p:timing', 'p:extLst'
    )
    cSld = OneAndOnlyOne('p:cSld')
    clrMapOvr = ZeroOrOne('p:clrMapOvr', successors=_tag_seq[2:])
    timing = ZeroOrOne('p:timing', successors=_tag_seq[4:])
    del _tag_seq

    @classmethod
    def new(cls):
        """Return new `p:sld` element configured as base slide shape."""
        return parse_xml(cls._sld_xml())

    @property
    def bg(self):
        """Return `p:bg` grandchild or None if not present."""
        return self.cSld.bg

    def get_or_add_childTnLst(self):
        """Return parent element for a new `p:video` child element.

        The `p:video` element causes play controls to appear under a video
        shape (pic shape containing video). There can be more than one video
        shape on a slide, which causes the precondition to vary. It needs to
        handle the case when there is no `p:sld/p:timing` element and when
        that element already exists. If the case isn't simple, it just nukes
        what's there and adds a fresh one. This could theoretically remove
        desired existing timing information, but there isn't any evidence
        available to me one way or the other, so I've taken the simple
        approach.
        """
        childTnLst = self._childTnLst
        if childTnLst is None:
            childTnLst = self._add_childTnLst()
        return childTnLst

    def _add_childTnLst(self):
        """Add `./p:timing/p:tnLst/p:par/p:cTn/p:childTnLst` descendant.

        Any existing `p:timing` child element is ruthlessly removed and
        replaced.
        """
        self.remove(self.get_or_add_timing())
        timing = parse_xml(self._childTnLst_timing_xml())
        self._insert_timing(timing)
        return timing.xpath('./p:tnLst/p:par/p:cTn/p:childTnLst')[0]

    @property
    def _childTnLst(self):
        """Return `./p:timing/p:tnLst/p:par/p:cTn/p:childTnLst` descendant.

        Return None if that element is not present.
        """
        childTnLsts = self.xpath(
            './p:timing/p:tnLst/p:par/p:cTn/p:childTnLst'
        )
        if not childTnLsts:
            return None
        return childTnLsts[0]

    @staticmethod
    def _childTnLst_timing_xml():
        return (
            '<p:timing %s>\n'
            '  <p:tnLst>\n'
            '    <p:par>\n'
            '      <p:cTn id="1" dur="indefinite" restart="never" nodeType="'
            'tmRoot">\n'
            '        <p:childTnLst/>\n'
            '      </p:cTn>\n'
            '    </p:par>\n'
            '  </p:tnLst>\n'
            '</p:timing>' % nsdecls('p')
        )

    @staticmethod
    def _sld_xml():
        return (
            '<p:sld %s>\n'
            '  <p:cSld>\n'
            '    <p:spTree>\n'
            '      <p:nvGrpSpPr>\n'
            '        <p:cNvPr id="1" name=""/>\n'
            '        <p:cNvGrpSpPr/>\n'
            '        <p:nvPr/>\n'
            '      </p:nvGrpSpPr>\n'
            '      <p:grpSpPr/>\n'
            '    </p:spTree>\n'
            '  </p:cSld>\n'
            '  <p:clrMapOvr>\n'
            '    <a:masterClrMapping/>\n'
            '  </p:clrMapOvr>\n'
            '</p:sld>' % nsdecls('a', 'p', 'r')
        )


class CT_SlideLayout(_BaseSlideElement):
    """
    ``<p:sldLayout>`` element, root of a slide layout part
    """
    _tag_seq = (
        'p:cSld', 'p:clrMapOvr', 'p:transition', 'p:timing', 'p:hf',
        'p:extLst'
    )
    cSld = OneAndOnlyOne('p:cSld')
    del _tag_seq


class CT_SlideLayoutIdList(BaseOxmlElement):
    """
    ``<p:sldLayoutIdLst>`` element, child of ``<p:sldMaster>`` containing
    references to the slide layouts that inherit from the slide master.
    """
    sldLayoutId = ZeroOrMore('p:sldLayoutId')


class CT_SlideLayoutIdListEntry(BaseOxmlElement):
    """
    ``<p:sldLayoutId>`` element, child of ``<p:sldLayoutIdLst>`` containing
    a reference to a slide layout.
    """
    rId = RequiredAttribute('r:id', XsdString)


class CT_SlideMaster(_BaseSlideElement):
    """
    ``<p:sldMaster>`` element, root of a slide master part
    """
    _tag_seq = (
        'p:cSld', 'p:clrMap', 'p:sldLayoutIdLst', 'p:transition', 'p:timing',
        'p:hf', 'p:txStyles', 'p:extLst'
    )
    cSld = OneAndOnlyOne('p:cSld')
    sldLayoutIdLst = ZeroOrOne('p:sldLayoutIdLst', successors=_tag_seq[3:])
    del _tag_seq


class CT_SlideTiming(BaseOxmlElement):
    """`p:timing` element, specifying animations and timed behaviors."""

    _tag_seq = ('p:tnLst', 'p:bldLst', 'p:extLst')
    tnLst = ZeroOrOne('p:tnLst', successors=_tag_seq[1:])
    del _tag_seq


class CT_TimeNodeList(BaseOxmlElement):
    """`p:tnLst` or `p:childTnList` element."""

    def add_video(self, shape_id):
        """Add a new `p:video` child element for movie having *shape_id*."""
        video_xml = (
            '<p:video %s>\n'
            '  <p:cMediaNode vol="80000">\n'
            '    <p:cTn id="%d" fill="hold" display="0">\n'
            '      <p:stCondLst>\n'
            '        <p:cond delay="indefinite"/>\n'
            '      </p:stCondLst>\n'
            '    </p:cTn>\n'
            '    <p:tgtEl>\n'
            '      <p:spTgt spid="%d"/>\n'
            '    </p:tgtEl>\n'
            '  </p:cMediaNode>\n'
            '</p:video>\n' % (nsdecls('p'), self._next_cTn_id, shape_id)
        )
        video = parse_xml(video_xml)
        self.append(video)

    def add_autoplay_video(self, shape_id):
        """Add a new `p:video` child element for movie having *shape_id*."""
        animation1_xml = (
            '<p:seq concurrent="1" nextAc="seek">\n'
            '    <p:cTn id="%d" dur="indefinite" nodeType="mainSeq">\n'
            '        <p:childTnLst>\n'
            '            <p:par>\n'
            '                <p:cTn id="%d" fill="hold">\n'
            '                    <p:stCondLst>\n'
            '                        <p:cond delay="indefinite"/>\n'
            '                        <p:cond evt="onBegin" delay="0">\n'
            '                            <p:tn val="2"/>\n'
            '                        </p:cond>\n'
            '                    </p:stCondLst>\n'
            '                    <p:childTnLst>\n'
            '                        <p:par>\n'
            '                            <p:cTn id="%d" fill="hold">\n'
            '                                <p:stCondLst>\n'
            '                                    <p:cond delay="0"/>\n'
            '                                </p:stCondLst>\n'
            '                                <p:childTnLst>\n'
            '                                    <p:par>\n'
            '                                        <p:cTn id="%d" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect">\n'
            '                                            <p:stCondLst>\n'
            '                                                <p:cond delay="0"/>\n'
            '                                            </p:stCondLst>\n'
            '                                            <p:childTnLst>\n'
            '                                                <p:cmd type="call" cmd="playFrom(0.0)">\n'
            '                                                    <p:cBhvr>\n'
            '                                                        <p:cTn id="%d" dur="24705" fill="hold"/>\n'
            '                                                        <p:tgtEl>\n'
            '                                                            <p:spTgt spid="4"/>\n'
            '                                                        </p:tgtEl>\n'
            '                                                    </p:cBhvr>\n'
            '                                                </p:cmd>\n'
            '                                            </p:childTnLst>\n'
            '                                        </p:cTn>\n'
            '                                    </p:par>\n'
            '                                </p:childTnLst>\n'
            '                            </p:cTn>\n'
            '                        </p:par>\n'
            '                    </p:childTnLst>\n'
            '                </p:cTn>\n'
            '            </p:par>\n'
            '        </p:childTnLst>\n'
            '    </p:cTn>\n'
            '    <p:prevCondLst>\n'
            '        <p:cond evt="onPrev" delay="0">\n'
            '            <p:tgtEl>\n'
            '                <p:sldTgt/>\n'
            '            </p:tgtEl>\n'
            '        </p:cond>\n'
            '    </p:prevCondLst>\n'
            '    <p:nextCondLst>\n'
            '        <p:cond evt="onNext" delay="0">\n'
            '            <p:tgtEl>\n'
            '                <p:sldTgt/>\n'
            '            </p:tgtEl>\n'
            '        </p:cond>\n'
            '    </p:nextCondLst>\n'
            '</p:seq>\n' % (self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, self._next_cTn_id)
        )
        video_xml = (
            '<p:video %s>\n'
            '  <p:cMediaNode vol="80000">\n'
            '    <p:cTn id="%d" fill="hold" display="0">\n'
            '      <p:stCondLst>\n'
            '        <p:cond delay="indefinite"/>\n'
            '      </p:stCondLst>\n'
            '    </p:cTn>\n'
            '    <p:tgtEl>\n'
            '      <p:spTgt spid="%d"/>\n'
            '    </p:tgtEl>\n'
            '  </p:cMediaNode>\n'
            '</p:video>\n' % (nsdecls('p'), self._next_cTn_id, shape_id)
        )
        animation2_xml = (
            '<p:seq concurrent="1" nextAc="seek">\n'
            '    <p:cTn id="%d" restart="whenNotActive" fill="hold" evtFilter="cancelBubble" nodeType="interactiveSeq">\n'
            '        <p:stCondLst>\n'
            '            <p:cond evt="onClick" delay="0">\n'
            '                <p:tgtEl>\n'
            '                    <p:spTgt spid="4"/>\n'
            '                </p:tgtEl>\n'
            '            </p:cond>\n'
            '        </p:stCondLst>\n'
            '        <p:endSync evt="end" delay="0">\n'
            '            <p:rtn val="all"/>\n'
            '        </p:endSync>\n'
            '        <p:childTnLst>\n'
            '            <p:par>\n'
            '                <p:cTn id="%d" fill="hold">\n'
            '                    <p:stCondLst>\n'
            '                        <p:cond delay="0"/>\n'
            '                    </p:stCondLst>\n'
            '                    <p:childTnLst>\n'
            '                        <p:par>\n'
            '                            <p:cTn id="%d" fill="hold">\n'
            '                                <p:stCondLst>\n'
            '                                    <p:cond delay="0"/>\n'
            '                                </p:stCondLst>\n'
            '                                <p:childTnLst>\n'
            '                                    <p:par>\n'
            '                                        <p:cTn id="%d" presetID="2" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="clickEffect">\n'
            '                                            <p:stCondLst>\n'
            '                                                <p:cond delay="0"/>\n'
            '                                            </p:stCondLst>\n'
            '                                            <p:childTnLst>\n'
            '                                                <p:cmd type="call" cmd="togglePause">\n'
            '                                                    <p:cBhvr>\n'
            '                                                        <p:cTn id="%d" dur="1" fill="hold"/>\n'
            '                                                        <p:tgtEl>\n'
            '                                                            <p:spTgt spid="4"/>\n'
            '                                                        </p:tgtEl>\n'
            '                                                    </p:cBhvr>\n'
            '                                                </p:cmd>\n'
            '                                            </p:childTnLst>\n'
            '                                        </p:cTn>\n'
            '                                    </p:par>\n'
            '                                </p:childTnLst>\n'
            '                            </p:cTn>\n'
            '                        </p:par>\n'
            '                    </p:childTnLst>\n'
            '                </p:cTn>\n'
            '            </p:par>\n'
            '        </p:childTnLst>\n'
            '    </p:cTn>\n'
            '    <p:nextCondLst>\n'
            '        <p:cond evt="onClick" delay="0">\n'
            '            <p:tgtEl>\n'
            '                <p:spTgt spid="4"/>\n'
            '            </p:tgtEl>\n'
            '        </p:cond>\n'
            '    </p:nextCondLst>\n'
            '</p:seq>\n' % (self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, self._next_cTn_id, self._next_cTn_id)
        )
        animation1 = parse_xml(animation1_xml)
        print(animation1)
        self.append(animation1)
        video = parse_xml(video_xml)
        self.append(video)
        animation2 = parse_xml(animation2_xml)
        self.append(animation2)
        print(animation2)
    @property
    def _next_cTn_id(self):
        """Return the next available unique ID (int) for p:cTn element."""
        cTn_id_strs = self.xpath('/p:sld/p:timing//p:cTn/@id')
        ids = [int(id_str) for id_str in cTn_id_strs]
        return max(ids) + 1


class CT_TLMediaNodeVideo(BaseOxmlElement):
    """`p:video` element, specifying video media details."""

    _tag_seq = ('p:cMediaNode',)
    cMediaNode = OneAndOnlyOne('p:cMediaNode')
    del _tag_seq


class CT_TLTimeNodeSequence(BaseOxmlElement):
    """`p:seq` element, animations."""

    _tag_seq = ('p:cTn', 'p:prevCondLst', 'p:nextCondLst')
    cTn = OneAndOnlyOne('p:cTn')
    prevCondLst = ZeroOrOne('p:prevCondLst',)
    nextCondLst = ZeroOrOne('p:nextCondLst',)
    del _tag_seq