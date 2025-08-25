from enum import Enum
from xml.sax import ContentHandler, parse
import re
import sys
import codecs


class Lexicon:
    """The Lexicon contains all the synsets and entries"""

    def __init__(self, id, label, language, email, license, version, url):
        self.id = id
        self.label = label
        self.language = language
        self.email = email
        self.license = license
        self.version = version
        self.url = url
        self.citation = None
        self.entries = []
        self.synsets = []
        self.frames = []
        self.comments = {}
        self.id2synset = {}
        self.id2entry = {}
        self.id2sense = {}
        self.member2entry = {}
        self.members = {}
        self.sense2synset = {}

    def __str__(self):
        return "Lexicon with ID %s and %d entries and %d synsets" % (
            self.id, len(self.entries), len(self.synsets))

    def add_entry(self, entry):
        if entry.id in self.id2entry:
            sys.stderr.write("Duplicate ID: " + entry.id + "\n")
        self.id2entry[entry.id] = entry
        for sense in entry.senses:
            if sense.synset not in self.members:
                self.members[sense.synset] = []
            self.members[sense.synset].append(entry.lemma.written_form)
            self.sense2synset[sense.id] = sense.synset
            self.id2sense[sense.id] = sense
        if entry.lemma.written_form not in self.member2entry:
            self.member2entry[entry.lemma.written_form] = []
        self.member2entry[entry.lemma.written_form].append(entry.id)
        self.entries.append(entry)

    def del_entry(self, entry):
        """Delete an entry and clear all senses"""
        if entry.id not in self.id2entry:
            return
        del self.id2entry[entry.id]
        for sense in entry.senses:
            self.del_sense(entry, sense)
        self.member2entry[entry.lemma.written_form] = [m for m in 
                self.member2entry[entry.lemma.written_form]
                    if m != entry.id]
        if self.member2entry[entry.lemma.written_form] == []:
            del self.member2entry[entry.lemma.written_form]
        self.entries = [e for e in self.entries if e.id != entry.id]

    def del_sense(self, entry, sense):
        """Remove a single sense from an entry"""
        if sense.id not in self.sense2synset:
            return
        self.members[sense.synset] = [m for m in self.members[sense.synset]
                if m != entry.lemma.written_form]
        if self.members[sense.synset] == []:
            del self.members[sense.synset]
        del self.sense2synset[sense.id]
        del self.id2sense[sense.id]
        entry.senses = [s for s in entry.senses if s.id != sense.id]

    def add_synset(self, synset):
        self.id2synset[synset.id] = synset
        self.synsets.append(synset)

    def entry_by_id(self, id):
        return self.id2entry.get(id)

    def synset_by_id(self, id):
        return self.id2synset.get(id)

    def sense_by_id(self, id):
        return self.id2sense.get(id)

    def entry_by_lemma(self, lemma):
        return self.member2entry.get(lemma, [])

    def members_by_id(self, synset_id):
        return self.members.get(synset_id, [])

    def sense_to_synset(self, sense_id):
        return self.sense2synset[sense_id]

    def change_sense_id(self, sense, new_id):
        del self.sense2synset[sense.id]
        del self.id2sense[sense.id]
        sense.id = new_id
        self.sense2synset[new_id] = sense.synset
        self.id2sense[new_id] = sense

    def to_xml(self, xml_file, part=False):
        xml_file.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
        if part:
            xml_file.write(
                """<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-relaxed-1.3.dtd">\n""")
        else:
            xml_file.write(
                """<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">\n""")
        if self.citation:
            citation_text = f"""
           citation="{self.citation}" """
        else:
            citation_text = ""
        xml_file.write(
            """<LexicalResource xmlns:dc="https://globalwordnet.github.io/schemas/dc/">
  <Lexicon id="%s"
           label="%s"
           language="%s"
           email="%s"
           license="%s"
           version="%s"%s
           url="%s">
""" %
            (self.id,
             self.label,
             self.language,
             self.email,
             self.license,
             self.version,
             citation_text,
             self.url))

        for entry in sorted(self.entries, key=lambda x: x.id):
            entry.to_xml(xml_file, self.comments)
        for synset in sorted(self.synsets, key=lambda x: x.id):
            synset.to_xml(xml_file, self.comments)
        for synbeh in self.frames:
            synbeh.to_xml(xml_file)
        xml_file.write("""  </Lexicon>
</LexicalResource>\n""")


class LexicalEntry:
    """The lexical entry consists of a single word"""

    def __init__(self, id):
        self.id = id
        self.lemma = None
        self.forms = []
        self.senses = []
        self.pronunciation = []

    def set_lemma(self, lemma):
        self.lemma = lemma

    def add_form(self, form):
        self.forms.append(form)

    def add_sense(self, sense):
        if not any(s.id == sense.id for s in self.senses):
            self.senses.append(sense)

    def to_xml(self, xml_file, comments):
        xml_file.write("""    <LexicalEntry id="%s">""" % self.id)
        if self.pronunciation:
            xml_file.write("""
      <Lemma writtenForm="%s" partOfSpeech="%s">
""" % (escape_xml_lit(self.lemma.written_form), 
        self.lemma.part_of_speech.value if self.lemma.part_of_speech.value != "s" else "a"))
            for pron in self.pronunciation:
                pron.to_xml(xml_file)
            xml_file.write("""      </Lemma>
""")
        else:
            xml_file.write("""
      <Lemma writtenForm="%s" partOfSpeech="%s"/>
""" % (escape_xml_lit(self.lemma.written_form), self.lemma.part_of_speech.value))
        for form in self.forms:
            form.to_xml(xml_file)
        for sense in self.senses:
            sense.to_xml(xml_file, comments)
        xml_file.write("""    </LexicalEntry>
""")


class Lemma:
    """The lemma gives the written form and part of speech of an entry"""

    def __init__(self, written_form, part_of_speech):
        self.written_form = written_form
        self.part_of_speech = part_of_speech


class Form:
    """The form gives an inflected form of the entry"""

    def __init__(self, written_form):
        self.written_form = written_form

    def to_xml(self, xml_file):
        xml_file.write("""      <Form writtenForm="%s"/>
""" % escape_xml_lit(self.written_form))

class Pronunciation:
    """The pronunciation of a lemma"""
    def __init__(self, value, variety):
        self.value = value
        self.variety = variety

    def to_xml(self, xml_file):
        if self.variety:
            xml_file.write("""        <Pronunciation variety="%s">%s</Pronunciation>
""" % (self.variety, escape_xml_lit(self.value)))
        else:
            xml_file.write("""        <Pronunciation>%s</Pronunciation>
""" % (escape_xml_lit(self.value)))


class Sense:
    """The sense links an entry to a synset"""

    def __init__(self, id, synset, sense_key, n=-1, adjposition=None):
        self.id = id
        self.synset = synset
        self.n = n
        self.sense_key = sense_key
        self.sense_relations = []
        self.adjposition = adjposition
        self.sent = []
        self.subcat = []

    def add_sense_relation(self, relation):
        self.sense_relations.append(relation)

    def to_xml(self, xml_file, comments):
        if self.adjposition:
            n_str = " adjposition=\"%s\"" % self.adjposition
        else:
            n_str = ""
        if self.sense_key:
            sk_str = " dc:identifier=\"%s\"" % escape_xml_lit(self.sense_key)
        else:
            sk_str = ""
        if self.subcat:
            subcat_str = " subcat=\"%s\"" % " ".join(self.subcat)
        else:
            subcat_str = ""
        if len(self.sense_relations) > 0:
            xml_file.write("""      <Sense id="%s"%s%s synset="%s"%s>
""" % (self.id, n_str, subcat_str, self.synset, sk_str))
            for rel in self.sense_relations:
                rel.to_xml(xml_file, comments)
            xml_file.write("""        </Sense>
""")
        else:
            xml_file.write("""      <Sense id="%s"%s%s synset="%s"%s/>
""" % (self.id, n_str, subcat_str, self.synset, sk_str))


class Synset:
    """The synset is a collection of synonyms"""

    def __init__(self, id, ili, part_of_speech, lex_name, source=None):
        self.id = id
        self.ili = ili
        self.wikidata = None
        self.part_of_speech = part_of_speech
        self.lex_name = lex_name
        self.definitions = []
        self.ili_definition = None
        self.synset_relations = []
        self.examples = []
        self.source = source
        self.members = []

    def add_definition(self, definition, is_ili=False):
        if is_ili:
            if definition not in self.definitions:
                self.definitions.append(definition)
            self.ili_definition = definition
        else:
            self.definitions.append(definition)

    def add_synset_relation(self, relation):
        self.synset_relations.append(relation)

    def add_example(self, example):
        self.examples.append(example)

    def to_xml(self, xml_file, comments):
        if self.id in comments:
            xml_file.write("""    <!-- %s -->
""" % comments[self.id])
        source_tag = ""
        if self.source:
            source_tag = " dc:source=\"%s\"" % (self.source)
        xml_file.write(
            """    <Synset id="%s" ili="%s" members="%s" partOfSpeech="%s" lexfile="%s"%s>
""" %
            (self.id,
             self.ili,
             " ".join(self.members),
             self.part_of_speech.value,
             self.lex_name,
             source_tag))
        for defn in self.definitions:
            defn.to_xml(xml_file)
        if self.ili_definition:
            self.ili_definition.to_xml(xml_file, True)
        for rel in self.synset_relations:
            rel.to_xml(xml_file, comments)
        for ex in self.examples:
            ex.to_xml(xml_file)
        xml_file.write("""    </Synset>
""")


class Definition:
    def __init__(self, text):
        self.text = text

    def to_xml(self, xml_file, is_ili=False):
        if is_ili:
            xml_file.write("""      <ILIDefinition>%s</ILIDefinition>
""" % escape_xml_lit(self.text))
        else:
            xml_file.write("""      <Definition>%s</Definition>
""" % escape_xml_lit(self.text))

    def __eq__(self, other):
        return self.text == other.text


class Example:
    def __init__(self, text, source=None):
        self.text = text
        self.source = source

    def to_xml(self, xml_file):
        if self.source:
            xml_file.write("""      <Example dc:source=\"%s\">%s</Example>
""" % (escape_xml_lit(self.source), escape_xml_lit(self.text)))

        else:
            xml_file.write("""      <Example>%s</Example>
""" % escape_xml_lit(self.text))


class SynsetRelation:
    def __init__(self, target, rel_type):
        self.target = target
        self.rel_type = rel_type

    def to_xml(self, xml_file, comments):
        xml_file.write("""      <SynsetRelation relType="%s" target="%s"/>""" %
                       (self.rel_type.value, self.target))
        if self.target in comments:
            xml_file.write(""" <!-- %s -->
""" % comments[self.target])
        else:
            xml_file.write("\n")


class SenseRelation:
    def __init__(self, target, rel_type, other_type=None):
        self.target = target
        self.rel_type = rel_type
        self.other_type = other_type

    def to_xml(self, xml_file, comments):
        if self.other_type:
            xml_file.write(
                    """        <SenseRelation relType="other" target="%s" dc:type="%s"/>""" %
                (self.target, self.other_type))
        else:
            xml_file.write(
            """        <SenseRelation relType="%s" target="%s"/>""" %
            (self.rel_type.value, self.target))
        if self.target in comments:
            xml_file.write(""" <!-- %s -->
""" % comments[self.target])
        else:
            xml_file.write("\n")


class SyntacticBehaviour:
    def __init__(self, id, subcategorization_frame):
        if not isinstance(subcategorization_frame, str):
            raise "Syntactic Behaviour is not string" + \
                str(subcategorization_frame)
        self.subcategorization_frame = subcategorization_frame
        self.id = id

    def to_xml(self, xml_file):
        xml_file.write(
            """  <SyntacticBehaviour id="%s" subcategorizationFrame="%s"/>
""" %
            (self.id, escape_xml_lit(
                self.subcategorization_frame)))

    def __repr__(self):
        return "SyntacticBehaviour(%s, %s)" % (
            self.id, self.subcategorization_frame)


class PartOfSpeech(Enum):
    NOUN = 'n'
    VERB = 'v'
    ADJECTIVE = 'a'
    ADVERB = 'r'
    ADJECTIVE_SATELLITE = 's'
    NAMED_ENTITY = 't'
    CONJUNCTION = 'c'
    ADPOSITION = 'p'
    OTHER = 'x'
    UNKNOWN = 'u'


def equal_pos(pos1, pos2):
    return (pos1 == pos2
            or pos1 == PartOfSpeech.ADJECTIVE and pos2 == PartOfSpeech.ADJECTIVE_SATELLITE
            or pos2 == PartOfSpeech.ADJECTIVE and pos1 == PartOfSpeech.ADJECTIVE_SATELLITE)


class SynsetRelType(Enum):
    AGENT = 'agent'
    ALSO = 'also'
    ATTRIBUTE = 'attribute'
    BE_IN_STATE = 'be_in_state'
    CAUSES = 'causes'
    CLASSIFIED_BY = 'classified_by'
    CLASSIFIES = 'classifies'
    CO_AGENT_INSTRUMENT = 'co_agent_instrument'
    CO_AGENT_PATIENT = 'co_agent_patient'
    CO_AGENT_RESULT = 'co_agent_result'
    CO_INSTRUMENT_AGENT = 'co_instrument_agent'
    CO_INSTRUMENT_PATIENT = 'co_instrument_patient'
    CO_INSTRUMENT_RESULT = 'co_instrument_result'
    CO_PATIENT_AGENT = 'co_patient_agent'
    CO_PATIENT_INSTRUMENT = 'co_patient_instrument'
    CO_RESULT_AGENT = 'co_result_agent'
    CO_RESULT_INSTRUMENT = 'co_result_instrument'
    CO_ROLE = 'co_role'
    DIRECTION = 'direction'
    DOMAIN_REGION = 'domain_region'
    DOMAIN_TOPIC = 'domain_topic'
    EXEMPLIFIES = 'exemplifies'
    ENTAILS = 'entails'
    EQ_SYNONYM = 'eq_synonym'
    HAS_DOMAIN_REGION = 'has_domain_region'
    HAS_DOMAIN_TOPIC = 'has_domain_topic'
    IS_EXEMPLIFIED_BY = 'is_exemplified_by'
    HOLO_LOCATION = 'holo_location'
    HOLO_MEMBER = 'holo_member'
    HOLO_PART = 'holo_part'
    HOLO_PORTION = 'holo_portion'
    HOLO_SUBSTANCE = 'holo_substance'
    HOLONYM = 'holonym'
    HYPERNYM = 'hypernym'
    HYPONYM = 'hyponym'
    IN_MANNER = 'in_manner'
    INSTANCE_HYPERNYM = 'instance_hypernym'
    INSTANCE_HYPONYM = 'instance_hyponym'
    INSTRUMENT = 'instrument'
    INVOLVED = 'involved'
    INVOLVED_AGENT = 'involved_agent'
    INVOLVED_DIRECTION = 'involved_direction'
    INVOLVED_INSTRUMENT = 'involved_instrument'
    INVOLVED_LOCATION = 'involved_location'
    INVOLVED_PATIENT = 'involved_patient'
    INVOLVED_RESULT = 'involved_result'
    INVOLVED_SOURCE_DIRECTION = 'involved_source_direction'
    INVOLVED_TARGET_DIRECTION = 'involved_target_direction'
    IS_CAUSED_BY = 'is_caused_by'
    IS_ENTAILED_BY = 'is_entailed_by'
    LOCATION = 'location'
    MANNER_OF = 'manner_of'
    MERO_LOCATION = 'mero_location'
    MERO_MEMBER = 'mero_member'
    MERO_PART = 'mero_part'
    MERO_PORTION = 'mero_portion'
    MERO_SUBSTANCE = 'mero_substance'
    MERONYM = 'meronym'
    SIMILAR = 'similar'
    OTHER = 'other'
    PATIENT = 'patient'
    RESTRICTED_BY = 'restricted_by'
    RESTRICTS = 'restricts'
    RESULT = 'result'
    ROLE = 'role'
    SOURCE_DIRECTION = 'source_direction'
    STATE_OF = 'state_of'
    TARGET_DIRECTION = 'target_direction'
    SUBEVENT = 'subevent'
    IS_SUBEVENT_OF = 'is_subevent_of'
    ANTONYM = 'antonym'


inverse_synset_rels = {
    SynsetRelType.HYPERNYM: SynsetRelType.HYPONYM,
    SynsetRelType.HYPONYM: SynsetRelType.HYPERNYM,
    SynsetRelType.INSTANCE_HYPERNYM: SynsetRelType.INSTANCE_HYPONYM,
    SynsetRelType.INSTANCE_HYPONYM: SynsetRelType.INSTANCE_HYPERNYM,
    SynsetRelType.MERONYM: SynsetRelType.HOLONYM,
    SynsetRelType.HOLONYM: SynsetRelType.MERONYM,
    SynsetRelType.MERO_LOCATION: SynsetRelType.HOLO_LOCATION,
    SynsetRelType.HOLO_LOCATION: SynsetRelType.MERO_LOCATION,
    SynsetRelType.MERO_MEMBER: SynsetRelType.HOLO_MEMBER,
    SynsetRelType.HOLO_MEMBER: SynsetRelType.MERO_MEMBER,
    SynsetRelType.MERO_PART: SynsetRelType.HOLO_PART,
    SynsetRelType.HOLO_PART: SynsetRelType.MERO_PART,
    SynsetRelType.MERO_PORTION: SynsetRelType.HOLO_PORTION,
    SynsetRelType.HOLO_PORTION: SynsetRelType.MERO_PORTION,
    SynsetRelType.MERO_SUBSTANCE: SynsetRelType.HOLO_SUBSTANCE,
    SynsetRelType.HOLO_SUBSTANCE: SynsetRelType.MERO_SUBSTANCE,
    SynsetRelType.BE_IN_STATE: SynsetRelType.STATE_OF,
    SynsetRelType.STATE_OF: SynsetRelType.BE_IN_STATE,
    SynsetRelType.CAUSES: SynsetRelType.IS_CAUSED_BY,
    SynsetRelType.IS_CAUSED_BY: SynsetRelType.CAUSES,
    SynsetRelType.SUBEVENT: SynsetRelType.IS_SUBEVENT_OF,
    SynsetRelType.IS_SUBEVENT_OF: SynsetRelType.SUBEVENT,
    SynsetRelType.MANNER_OF: SynsetRelType.IN_MANNER,
    SynsetRelType.IN_MANNER: SynsetRelType.MANNER_OF,
    SynsetRelType.RESTRICTS: SynsetRelType.RESTRICTED_BY,
    SynsetRelType.RESTRICTED_BY: SynsetRelType.RESTRICTS,
    SynsetRelType.CLASSIFIES: SynsetRelType.CLASSIFIED_BY,
    SynsetRelType.CLASSIFIED_BY: SynsetRelType.CLASSIFIES,
    SynsetRelType.ENTAILS: SynsetRelType.IS_ENTAILED_BY,
    SynsetRelType.IS_ENTAILED_BY: SynsetRelType.ENTAILS,
    SynsetRelType.DOMAIN_REGION: SynsetRelType.HAS_DOMAIN_REGION,
    SynsetRelType.HAS_DOMAIN_REGION: SynsetRelType.DOMAIN_REGION,
    SynsetRelType.DOMAIN_TOPIC: SynsetRelType.HAS_DOMAIN_TOPIC,
    SynsetRelType.HAS_DOMAIN_TOPIC: SynsetRelType.DOMAIN_TOPIC,
    SynsetRelType.EXEMPLIFIES: SynsetRelType.IS_EXEMPLIFIED_BY,
    SynsetRelType.IS_EXEMPLIFIED_BY: SynsetRelType.EXEMPLIFIES,
    SynsetRelType.ROLE: SynsetRelType.INVOLVED,
    SynsetRelType.INVOLVED: SynsetRelType.ROLE,
    SynsetRelType.AGENT: SynsetRelType.INVOLVED_AGENT,
    SynsetRelType.INVOLVED_AGENT: SynsetRelType.AGENT,
    SynsetRelType.PATIENT: SynsetRelType.INVOLVED_PATIENT,
    SynsetRelType.INVOLVED_PATIENT: SynsetRelType.PATIENT,
    SynsetRelType.RESULT: SynsetRelType.INVOLVED_RESULT,
    SynsetRelType.INVOLVED_RESULT: SynsetRelType.RESULT,
    SynsetRelType.INSTRUMENT: SynsetRelType.INVOLVED_INSTRUMENT,
    SynsetRelType.INVOLVED_INSTRUMENT: SynsetRelType.INSTRUMENT,
    SynsetRelType.LOCATION: SynsetRelType.INVOLVED_LOCATION,
    SynsetRelType.INVOLVED_LOCATION: SynsetRelType.LOCATION,
    SynsetRelType.DIRECTION: SynsetRelType.INVOLVED_DIRECTION,
    SynsetRelType.INVOLVED_DIRECTION: SynsetRelType.DIRECTION,
    SynsetRelType.TARGET_DIRECTION: SynsetRelType.INVOLVED_TARGET_DIRECTION,
    SynsetRelType.INVOLVED_TARGET_DIRECTION: SynsetRelType.TARGET_DIRECTION,
    SynsetRelType.SOURCE_DIRECTION: SynsetRelType.INVOLVED_SOURCE_DIRECTION,
    SynsetRelType.INVOLVED_SOURCE_DIRECTION: SynsetRelType.SOURCE_DIRECTION,
    SynsetRelType.CO_AGENT_PATIENT: SynsetRelType.CO_PATIENT_AGENT,
    SynsetRelType.CO_PATIENT_AGENT: SynsetRelType.CO_AGENT_PATIENT,
    SynsetRelType.CO_AGENT_INSTRUMENT: SynsetRelType.CO_INSTRUMENT_AGENT,
    SynsetRelType.CO_INSTRUMENT_AGENT: SynsetRelType.CO_AGENT_INSTRUMENT,
    SynsetRelType.CO_AGENT_RESULT: SynsetRelType.CO_RESULT_AGENT,
    SynsetRelType.CO_RESULT_AGENT: SynsetRelType.CO_AGENT_RESULT,
    SynsetRelType.CO_PATIENT_INSTRUMENT: SynsetRelType.CO_INSTRUMENT_PATIENT,
    SynsetRelType.CO_INSTRUMENT_PATIENT: SynsetRelType.CO_PATIENT_INSTRUMENT,
    SynsetRelType.CO_RESULT_INSTRUMENT: SynsetRelType.CO_INSTRUMENT_RESULT,
    SynsetRelType.CO_INSTRUMENT_RESULT: SynsetRelType.CO_RESULT_INSTRUMENT,
    SynsetRelType.ANTONYM: SynsetRelType.ANTONYM,
    SynsetRelType.EQ_SYNONYM: SynsetRelType.EQ_SYNONYM,
    SynsetRelType.SIMILAR: SynsetRelType.SIMILAR,
    #        SynsetRelType.ALSO: SynsetRelType.ALSO,
    SynsetRelType.ATTRIBUTE: SynsetRelType.ATTRIBUTE,
    SynsetRelType.CO_ROLE: SynsetRelType.CO_ROLE
}


class SenseRelType(Enum):
    ANTONYM = 'antonym'
    ALSO = 'also'
    PARTICIPLE = 'participle'
    PERTAINYM = 'pertainym'
    DERIVATION = 'derivation'
    DOMAIN_TOPIC = 'domain_topic'
    HAS_DOMAIN_TOPIC = 'has_domain_topic'
    DOMAIN_REGION = 'domain_region'
    HAS_DOMAIN_REGION = 'has_domain_region'
    EXEMPLIFIES = 'exemplifies'
    IS_EXEMPLIFIED_BY = 'is_exemplified_by'
    SIMILAR = 'similar'
    OTHER = 'other'

class OtherSenseRelType(Enum):
    AGENT = 'agent'
    MATERIAL = 'material'
    EVENT = 'event'
    INSTRUMENT = 'instrument'
    LOCATION = 'location'
    BY_MEANS_OF = 'by_means_of'
    UNDERGOER = 'undergoer'
    PROPERTY = 'property'
    RESULT = 'result'
    STATE = 'state'
    USES = 'uses'
    DESTINATION = 'destination'
    BODY_PART = 'body_part'
    VEHICLE = 'vehicle'

inverse_sense_rels = {
    SenseRelType.DOMAIN_REGION: SenseRelType.HAS_DOMAIN_REGION,
    SenseRelType.HAS_DOMAIN_REGION: SenseRelType.DOMAIN_REGION,
    SenseRelType.DOMAIN_TOPIC: SenseRelType.HAS_DOMAIN_TOPIC,
    SenseRelType.HAS_DOMAIN_TOPIC: SenseRelType.DOMAIN_TOPIC,
    SenseRelType.EXEMPLIFIES: SenseRelType.IS_EXEMPLIFIED_BY,
    SenseRelType.IS_EXEMPLIFIED_BY: SenseRelType.EXEMPLIFIES,
    SenseRelType.ANTONYM: SenseRelType.ANTONYM,
    SenseRelType.SIMILAR: SenseRelType.SIMILAR,
    SenseRelType.ALSO: SenseRelType.ALSO,
    SenseRelType.DERIVATION: SenseRelType.DERIVATION,
}


class WordNetContentHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.lexicon = None
        self.entry = None
        self.sense = None
        self.defn = None
        self.ili_defn = None
        self.example = None
        self.example_source = None
        self.synset = None
        self.pron = None
        self.pron_var = None

    def startElement(self, name, attrs):
        if name == "Lexicon":
            self.lexicon = Lexicon(
                attrs["id"],
                attrs["label"],
                attrs["language"],
                attrs["email"],
                attrs["license"],
                attrs["version"],
                attrs["url"])
        elif name == "LexicalEntry":
            self.entry = LexicalEntry(attrs["id"])
        elif name == "Lemma":
            self.entry.set_lemma(
                Lemma(
                    attrs["writtenForm"],
                    PartOfSpeech(
                        attrs["partOfSpeech"])))
        elif name == "Form":
            self.entry.add_form(Form(attrs["writtenForm"]))
        elif name == "Sense":
            if "n" in attrs:
                n = int(attrs["n"])
            else:
                n = -1
            self.sense = Sense(attrs["id"], attrs["synset"], attrs.get(
                "dc:identifier") or "", n, attrs.get("adjposition"))
        elif name == "Synset":
            self.synset = Synset(attrs["id"], attrs["ili"],
                                 PartOfSpeech(attrs["partOfSpeech"]),
                                 attrs.get("lexfile", attrs.get("dc:subject", "")),
                                 attrs.get("dc:source", ""))
            self.synset.members = attrs.get("members", "").split(" ")
        elif name == "Definition":
            self.defn = ""
        elif name == "ILIDefinition":
            self.ili_defn = ""
        elif name == "Example":
            self.example = ""
            self.example_source = attrs.get("dc:source")
        elif name == "SynsetRelation":
            self.synset.add_synset_relation(
                SynsetRelation(attrs["target"],
                               SynsetRelType(attrs["relType"])))
        elif name == "SenseRelation":
            self.sense.add_sense_relation(
                SenseRelation(attrs["target"],
                              SenseRelType(attrs["relType"]),
                              attrs.get("dc:type")))
        elif name == "SyntacticBehaviour":
            pass
            #self.entry.add_syntactic_behaviour(
            #    SyntacticBehaviour(
            #        attrs["subcategorizationFrame"],
            #        attrs["senses"].split(" ")))
        elif name == "Pronunciation":
            self.pron = ""
            self.pron_var = attrs.get("variety")
        elif name == "LexicalResource":
            pass
        else:
            raise ValueError("Unexpected Tag: " + name)

    def endElement(self, name):
        if name == "LexicalEntry":
            self.lexicon.add_entry(self.entry)
            self.entry = None
        elif name == "Sense":
            self.entry.add_sense(self.sense)
            self.sense = None
        elif name == "Synset":
            self.lexicon.add_synset(self.synset)
            self.synset = None
        elif name == "Definition":
            self.synset.add_definition(Definition(self.defn))
            self.defn = None
        elif name == "ILIDefinition":
            self.synset.add_definition(Definition(self.ili_defn), True)
            self.ili_defn = None
        elif name == "Example":
            self.synset.add_example(Example(self.example, self.example_source))
            self.example = None
        elif name == "Pronunciation":
            self.entry.pronunciation.append(Pronunciation(self.pron, self.pron_var))
            self.pron = None

    def characters(self, content):
        if self.defn is not None:
            self.defn += content
        elif self.ili_defn is not None:
            self.ili_defn += content
        elif self.example is not None:
            self.example += content
        elif self.pron is not None:
            self.pron += content
        elif content.strip() == '':
            pass
        else:
            print(content)
            raise ValueError("Text content not expected")


def escape_xml_lit(lit):
    return (lit.replace("&", "&amp;").replace("'", "&apos;").
            replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;"))


def extract_comments(wordnet_file, lexicon):
    with codecs.open(wordnet_file, "r", encoding="utf-8") as source:
        sen_rel_comment = re.compile(
            ".*<SenseRelation .* target=\"(.*)\".*/> <!-- (.*) -->")
        syn_rel_comment = re.compile(
            ".*<SynsetRelation .* target=\"(.*)\".*/> <!-- (.*) -->")
        comment = re.compile(".*<!-- (.*) -->.*")
        synset = re.compile(".*<Synset id=\"(\\S*)\".*")
        c = None
        for line in source.readlines():
            m = sen_rel_comment.match(line)
            if m:
                lexicon.comments[m.group(1)] = m.group(2)
            else:
                m = syn_rel_comment.match(line)
                if m:
                    lexicon.comments[m.group(1)] = m.group(2)
                else:
                    m = comment.match(line)
                    if m:
                        c = m.group(1)
                    else:
                        m = synset.match(line)
                        if m and c:
                            lexicon.comments[m.group(1)] = c
                            c = None


# Regular expressions for valid NameChar
# based on the XML 1.0 specification.
# We don't check for 1st character extra restrictions
# because it's always prefixed with 'oewn-'
xml_id_az = r'A-Za-z'
xml_id_num = r'0-9'
xml_id_extend = (
    r'\xC0-\xD6' # ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ
    r'\xD8-\xF6' # ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö
    r'\xF8-\u02FF'
    r'\u0370-\u037D'
    r'\u037F-\u1FFF'
    r'\u200C-\u200D'
    r'\u2070-\u218F'
    r'\u2C00-\u2FEF'
    r'\u3001-\uD7FF'
    r'\uF900-\uFDCF'
    r'\uFDF0-\uFFFD'
)
xml_id_not_first = (
    r'\u0300-\u036F'
    r'\u203F-\u2040'
)
# name_start_char = fr'[_{xml_id_az}{xml_id_extend}]' # not used if oewn- prefix
xml_id_char = fr'[_\-\.·{xml_id_az}{xml_id_num}{xml_id_extend}{xml_id_not_first}]'
xml_id_char_re = re.compile(xml_id_char)

def escape_lemma(lemma):
    """Format the lemma so it is valid XML id"""
    def elc(c):
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9') or c == '.':
            return c
        elif c == ' ':
            return '_'
        elif c == '(':
            return '-lb-'
        elif c == ')':
            return '-rb-'
        elif c == '\'':
            return '-ap-'
        elif c == '/':
            return '-sl-'
        elif c == ':':
            return '-cn-'
        elif c == ',':
            return '-cm-'
        elif c == '!':
            return '-ex-'
        elif c == '+':
            return '-pl-'
        elif c == '%':
            return '-pc-'
        elif xml_id_char_re.match(c):
            return c
        raise ValueError(f'Illegal character {c}')

    return "".join(elc(c) for c in lemma)


def parse_wordnet(wordnet_file):
    with codecs.open(wordnet_file, "r", encoding="utf-8") as source:
        handler = WordNetContentHandler()
        parse(source, handler)
    extract_comments(wordnet_file, handler.lexicon)
    return handler.lexicon
