from enum import Enum
from xml.sax import ContentHandler, parse
import re
import sys

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
        self.entries = []
        self.synsets = []
        self.comments = {}
        self.id2synset = {}
        self.id2entry = {}
        self.member2entry = {}
        self.members = {}

    def __str__(self):
        return "Lexicon with ID %s and %d entries and %d synsets" % (self.id, 
                len(self.entries), len(self.synsets))

    def add_entry(self, entry):
        self.id2entry[entry.id] = entry
        for sense in entry.senses:
            if sense.synset not in self.members:
                self.members[sense.synset] = []
            self.members[sense.synset].append(entry.lemma.written_form)
        if entry.lemma.written_form not in self.members:
            self.member2entry[entry.lemma.written_form] = []
        self.member2entry[entry.lemma.written_form].append(entry.id)
        self.entries.append(entry)

    def add_synset(self, synset):
        self.id2synset[synset.id] = synset
        self.synsets.append(synset)

    def entry_by_id(self, id):
        return self.id2entry.get(id)

    def synset_by_id(self, id):
        return self.id2synset.get(id)

    def entry_by_lemma(self, lemma):
        return self.member2entry.get(lemma)

    def members_by_id(self, synset_id):
        return self.members.get(synset_id)

    def to_xml(self, xml_file, part=True):
        xml_file.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
        if part:
            xml_file.write("""<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-relaxed-1.0.dtd">\n""")
        else:
            xml_file.write("""<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.0.dtd">\n""")
        xml_file.write("""<LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">
  <Lexicon id="%s" 
           label="%s" 
           language="%s"
           email="%s"
           license="%s"
           version="%s"
           url="%s">
""" % (self.id, self.label, self.language, self.email,
               self.license, self.version, self.url))

        for entry in self.entries:
            entry.to_xml(xml_file, self.comments)
        for synset in self.synsets:
            synset.to_xml(xml_file, self.comments)
        xml_file.write("""  </Lexicon>
</LexicalResource>\n""")
        
        
class LexicalEntry:
    """The lexical entry consists of a single word"""
    def __init__(self, id):
        self.id = id
        self.lemma = None
        self.forms = []
        self.senses = []
        self.syntactic_behaviours = []

    def set_lemma(self, lemma):
        self.lemma = lemma

    def add_form(self, form):
        self.forms.append(form)

    def add_sense(self, sense):
        self.senses.append(sense)

    def add_syntactic_behaviour(self, synbeh):
        self.syntactic_behaviours.append(synbeh)

    def to_xml(self, xml_file, comments):
        xml_file.write("""    <LexicalEntry id="%s">
      <Lemma writtenForm="%s" partOfSpeech="%s"/>
""" % (self.id, escape_xml_lit(self.lemma.written_form), self.lemma.part_of_speech.value))
        for form in self.forms:
            form.to_xml(xml_file)
        for sense in self.senses:
            sense.to_xml(xml_file, comments)
        for synbeh in self.syntactic_behaviours:
            synbeh.to_xml(xml_file)
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


class Sense:
    """The sense links an entry to a synset"""
    def __init__(self, id, synset, sense_key, n=-1):
        self.id = id
        self.synset = synset
        self.n = n
        self.sense_key = sense_key
        self.sense_relations = []

    def add_sense_relation(self, relation):
        self.sense_relations.append(relation)

    def to_xml(self, xml_file, comments):
        if self.n >= 0:
            n_str = " n=\"%d\"" % self.n
        else:
            n_str = ""
        if self.sense_key:
            sk_str = " dc:identifier=\"%s\"" % escape_xml_lit(self.sense_key)
        else:
            sk_str = ""
        if len(self.sense_relations) > 0:
            xml_file.write("""      <Sense id="%s"%s synset="%s"%s>
""" % (self.id, n_str, self.synset, sk_str))
            for rel in self.sense_relations:
                rel.to_xml(xml_file, comments)
            xml_file.write("""        </Sense>
""")
        else:
            xml_file.write("""      <Sense id="%s"%s synset="%s"%s/>
""" % (self.id, n_str, self.synset, sk_str))


class Synset:
    """The synset is a collection of synonyms"""
    def __init__(self, id, ili, part_of_speech, lex_name):
        self.id = id
        self.ili = ili
        self.part_of_speech = part_of_speech
        self.lex_name = lex_name
        self.definitions = []
        self.ili_definition = None
        self.synset_relations = []
        self.examples = []

    def add_definition(self, definition, is_ili=False):
        if is_ili:
            if not definition in self.definitions:
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
        xml_file.write("""    <Synset id="%s" ili="%s" partOfSpeech="%s" dc:subject="%s">
""" % (self.id, self.ili, self.part_of_speech.value, self.lex_name))
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
    def __init__(self, text):
        self.text = text

    def to_xml(self, xml_file):
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
    def __init__(self, target, rel_type):
        self.target = target
        self.rel_type = rel_type

    def to_xml(self, xml_file, comments):
        xml_file.write("""        <SenseRelation relType="%s" target="%s"/>""" % 
                (self.rel_type.value, self.target))
        if self.target in comments:
            xml_file.write(""" <!-- %s -->
""" % comments[self.target])
        else:
            xml_file.write("\n")


class SyntacticBehaviour:
    def __init__(self, subcategorization_frame, senses):
        self.subcategorization_frame = subcategorization_frame
        self.senses = senses

    def to_xml(self, xml_file):
        xml_file.write("""      <SyntacticBehaviour subcategorizationFrame="%s" senses="%s"/>
""" % (escape_xml_lit(self.subcategorization_frame), " ".join(self.senses)))


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
    
class WordNetContentHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.lexicon = None
        self.entry = None
        self.sense = None
        self.defn = None
        self.ili_defn = None
        self.example = None
        self.synset = None

    def startElement(self, name, attrs):
        if name == "Lexicon":
            self.lexicon = Lexicon(attrs["id"], attrs["label"], attrs["language"],
                    attrs["email"], attrs["license"], attrs["version"], attrs["url"])
        elif name == "LexicalEntry":
            self.entry = LexicalEntry(attrs["id"])
        elif name == "Lemma":
            self.entry.set_lemma(Lemma(attrs["writtenForm"], PartOfSpeech(attrs["partOfSpeech"])))
        elif name == "Form":
            self.entry.add_form(Form(attrs["writtenForm"]))
        elif name == "Sense":
            if "n" in attrs:
                n = int(attrs["n"])
            else:
                n = -1
            self.sense = Sense(attrs["id"], attrs["synset"], 
                    attrs.get("dc:identifier") or "", n)
        elif name == "Synset":
            self.synset = Synset(attrs["id"], attrs["ili"], 
                PartOfSpeech(attrs["partOfSpeech"]),
                attrs["dc:subject"])
        elif name == "Definition":
            self.defn = ""
        elif name == "ILIDefinition":
            self.ili_defn = ""
        elif name == "Example":
            self.example = ""
        elif name == "SynsetRelation":
            self.synset.add_synset_relation(
                    SynsetRelation(attrs["target"],
                    SynsetRelType(attrs["relType"])))
        elif name == "SenseRelation":
            self.sense.add_sense_relation(
                    SenseRelation(attrs["target"],
                    SenseRelType(attrs["relType"])))
        elif name == "SyntacticBehaviour":
            self.entry.add_syntactic_behaviour(
                    SyntacticBehaviour(
                        attrs["subcategorizationFrame"],
                        attrs["senses"].split(" ")))
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
            self.synset.add_example(Example(self.example))
            self.example = None


    def characters(self, content):
        if self.defn != None:
            self.defn += content
        elif self.ili_defn != None:
            self.ili_defn += content
        elif self.example != None:
            self.example += content
        elif content.strip() == '':
            pass
        else:
            print(content)
            raise ValueError("Text content not expected")

def escape_xml_lit(lit):
    return (lit.replace("&", "&amp;").replace("'", "&apos;").
        replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;"))

def extract_comments(wordnet_file,lexicon):
    with open(wordnet_file) as source:
        sen_rel_comment = re.compile(".*<SenseRelation .* target=\"(.*)\".*/> <!-- (.*) -->")
        syn_rel_comment = re.compile(".*<SynsetRelation .* target=\"(.*)\".*/> <!-- (.*) -->")
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


def parse_wordnet(wordnet_file):
    with open(wordnet_file) as source:
        handler = WordNetContentHandler()
        parse(source, handler)
    extract_comments(wordnet_file, handler.lexicon)
    return handler.lexicon

if __name__ == "__main__":
    wordnet = parse_wordnet(sys.argv[1])
    xml_file = open("wn31-test.xml","w")
    wordnet.to_xml(xml_file, True)
