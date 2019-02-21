from pptx.oxml.xmlchemy import (
    BaseOxmlElement, Choice, OneAndOnlyOne, OptionalAttribute,
    RequiredAttribute, ZeroOrMore, ZeroOrOne, ZeroOrOneChoice
)

_tag_seq = ('p:cTn', 'p:prevCondLst', 'p:nextCondLst')
cTn = OneAndOnlyOne('p:cTn')
prevCondLst = ZeroOrOne('p:prevCondLst', successors=('p:cTn'))
nextCondLst = ZeroOrOne('p:nextCondLst', successors=('p:cTn', 'p:prevCondLst'))
del _tag_seq