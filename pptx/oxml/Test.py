from pptx.oxml import parse_from_template, parse_xml
from pptx.oxml.xmlchemy import (
    BaseOxmlElement, Choice, OneAndOnlyOne, OptionalAttribute,
    RequiredAttribute, ZeroOrMore, ZeroOrOne, ZeroOrOneChoice
)

_tag_seq = ('p:cTn', 'p:prevCondLst', 'p:nextCondLst')
cTn = OneAndOnlyOne('p:cTn')
prevCondLst = ZeroOrOne('p:prevCondLst', successors=('p:cTn'))
nextCondLst = ZeroOrOne('p:nextCondLst', successors=('p:cTn', 'p:prevCondLst'))
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
            '</p:video>\n' % (self.next_cTn_id, self._next_cTn_id, shape_id)
        )
        video = parse_xml(video_xml)
        self.append(video)

    def add_autoplay_video(self,shape_id):
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
            '<p:video %d>\n'
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
            '</p:video>\n' % (self.next_cTn_id, self._next_cTn_id, shape_id)
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
shape_id = 4
CT_TimeNodeList.add_autoplay_video(int(shape_id))