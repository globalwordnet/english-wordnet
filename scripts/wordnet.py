from enum import Enum
from xml.sax import ContentHandler, parse

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

    def __str__(self):
        return "Lexicon with ID %s and %d entries and %d synsets" % (self.id, 
                len(self.entries), len(self.synsets))

    def add_entry(self, entry):
        self.entries.append(entry)

    def add_synset(self, synset):
        self.synsets.append(synset)
        
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


class Lemma:
    """The lemma gives the written form and part of speech of an entry"""
    def __init__(self, written_form, part_of_speech):
        self.written_form = written_form
        self.part_of_speech = part_of_speech

class Form:
    """The form gives an inflected form of the entry"""
    def __init__(self, written_form):
        self.written_form = written_form

class Sense:
    """The sense links an entry to a synset"""
    def __init__(self, id, synset, sense_key):
        self.id = id
        self.synset = synset
        self.sense_key = sense_key
        self.sense_relations = []

    def add_sense_relation(self, relation):
        self.sense_relations.append(relation)

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

class Definition:
    def __init__(self, text):
        self.text = text

class Example:
    def __init__(self, text):
        self.text = text

class SynsetRelation:
    def __init__(self, target, rel_type):
        self.target = target
        self.rel_type = rel_type

class SenseRelation:
    def __init__(self, target, rel_type):
        self.target = target
        self.rel_type = rel_type

class SyntacticBehaviour:
    def __init__(self, subcategorization_frame, senses):
        self.subcategorization_frame = subcategorization_frame
        self.senses = senses

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
        self.defn_flag = False
        self.ili_defn_flag = False
        self.example_flag = False
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
            self.sense = Sense(attrs["id"], attrs["synset"], 
                    attrs["dc:identifier"])
        elif name == "Synset":
            self.synset = Synset(attrs["id"], attrs["ili"], 
                PartOfSpeech(attrs["partOfSpeech"]),
                attrs["dc:subject"])
        elif name == "Definition":
            self.defn_flag = True
        elif name == "ILIDefinition":
            self.ili_defn_flag = True
        elif name == "Example":
            self.example_flag = True
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
            self.defn_flag = False
        elif name == "ILIDefinition":
            self.ili_defn_flag = False
        elif name == "Example":
            self.example_flag = False


    def characters(self, content):
        if self.defn_flag:
            self.synset.add_definition(Definition(content))
        elif self.ili_defn_flag:
            self.synset.add_definition(Definition(content), True)
        elif self.example_flag:
            self.synset.add_example(Example(content))
        elif content.strip() == '':
            pass
        else:
            raise ValueError("Text content not expected")


def parse_wordnet(wordnet_file):
    source = open(wordnet_file)
    handler = WordNetContentHandler()
    parse(source, handler)
    print(handler.lexicon)

if __name__ == "__main__":
    parse_wordnet("wn31.xml")
