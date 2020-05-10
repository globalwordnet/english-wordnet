import yaml
from change_manager import load_wordnet
from wordnet import SynsetRelType, SenseRelType

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

def map_sense_key(sk):
    """Convert sense keys to a YAML friendly form"""
    sk = sk.replace(':', '_')
    if sk.endswith("__"):
        return sk[:-2]
    else:
        return sk

ignored_symmetric_sense_rels = set([
    SenseRelType.HAS_DOMAIN_REGION, SenseRelType.HAS_DOMAIN_TOPIC,
    SenseRelType.IS_EXEMPLIFIED_BY])

def sense_to_yaml(wn, s):
    """Converts a single sense to the YAML form"""
    y = {}
    y["synset"] = s.synset[4:]
    y["key"] = map_sense_key(s.sense_key)
    if s.adjposition:
        y["adjposition"] = s.adjposition
    for sr in s.sense_relations:
        if sr.rel_type not in ignored_symmetric_sense_rels:
            if sr.rel_type.value not in y:
                y[sr.rel_type.value] = [map_sense_key(wn.sense_by_id(sr.target).sense_key)]
            else:
                y[sr.rel_type.value].append(map_sense_key(wn.sense_by_id(sr.target).sense_key))
    return y

def definition_to_yaml(wn, d):
    """Convert a definition to YAML"""
    return d.text

def example_to_yaml(wn, x):
    """Convert an example to YAML"""
    if x.source:
        return {"text": x.text, "source": x.source}
    else:
        return x.text

ignored_symmetric_synset_rels = set([
    SynsetRelType.HYPONYM, SynsetRelType.INSTANCE_HYPONYM, 
    SynsetRelType.HOLONYM, SynsetRelType.HOLO_LOCATION,
    SynsetRelType.HOLO_MEMBER, SynsetRelType.HOLO_PART,
    SynsetRelType.HOLO_PORTION, SynsetRelType.HOLO_SUBSTANCE,
    SynsetRelType.STATE_OF,
    SynsetRelType.IS_CAUSED_BY, SynsetRelType.IS_SUBEVENT_OF,
    SynsetRelType.IN_MANNER, SynsetRelType.RESTRICTED_BY,
    SynsetRelType.CLASSIFIED_BY, SynsetRelType.IS_ENTAILED_BY,
    SynsetRelType.HAS_DOMAIN_REGION, SynsetRelType.HAS_DOMAIN_TOPIC,
    SynsetRelType.IS_EXEMPLIFIED_BY, SynsetRelType.INVOLVED,
    SynsetRelType.INVOLVED_AGENT, SynsetRelType.INVOLVED_PATIENT,
    SynsetRelType.INVOLVED_RESULT, SynsetRelType.INVOLVED_INSTRUMENT,
    SynsetRelType.INVOLVED_LOCATION, SynsetRelType.INVOLVED_DIRECTION,
    SynsetRelType.INVOLVED_TARGET_DIRECTION, SynsetRelType.INVOLVED_SOURCE_DIRECTION,
    SynsetRelType.CO_PATIENT_AGENT, SynsetRelType.CO_INSTRUMENT_AGENT,
    SynsetRelType.CO_RESULT_AGENT, SynsetRelType.CO_INSTRUMENT_PATIENT,
    SynsetRelType.CO_INSTRUMENT_RESULT])


def lemma2senseorder(wn, l, synset_id):
    for e2 in wn.entry_by_lemma(l):
        for sense in wn.entry_by_id(e2).senses:
            if sense.synset == synset_id:
                return sense.id[-2:]
    return "99"


def entries_ordered(wn, synset_id):
    """Get the lemmas for entries ordered correctly"""
    e = wn.members_by_id(synset_id)
    e.sort(key=lambda l: lemma2senseorder(wn, l, synset_id))
    return e


if __name__ == "__main__":
    wn = load_wordnet()

    entry_yaml = {c: {} for c in char_range('a','z')}
    entry_yaml['0'] = {}
    for entry in wn.entries:
        e = {}
        if entry.forms:
            e['form'] = [f.written_form for f in entry.forms]
        e['senses'] = [sense_to_yaml(wn, s) for s in entry.senses]
        # TODO: Syntactic behaviour
        first = entry.lemma.written_form[0].lower()
        if first not in char_range('a', 'z'):
            first = '0'
        if entry.lemma.written_form not in entry_yaml[first]:
            entry_yaml[first][entry.lemma.written_form] = {}
        if entry.lemma.part_of_speech.value in entry_yaml[first][entry.lemma.written_form]:
            print("Duplicate: %s - %s" % (entry.lemma.written_form, entry.lemma.part_of_speech.value))
        entry_yaml[first][entry.lemma.written_form][entry.lemma.part_of_speech.value] = e

    for c in char_range('a', 'z'):
        with open("src/yaml/entries-%s.yaml" % c, "w") as outp:
            outp.write(yaml.dump(entry_yaml[c]))
    with open("src/yaml/entries-0.yaml", "w") as outp:
        outp.write(yaml.dump(entry_yaml['0']))

    synset_yaml = {}
    for synset in wn.synsets:
        s = {}
        if synset.ili and synset.ili != "in":
            s["ili"] = synset.ili
        s["pos"] = synset.part_of_speech.value
        s["definitions"] = [definition_to_yaml(wn, d) for d in synset.definitions]
        if synset.examples:
            s["examples"] = [example_to_yaml(wn, x) for x in synset.examples]
        if synset.source:
            s["source"] = synset.source
        for r in synset.synset_relations:
            if r.rel_type not in ignored_symmetric_synset_rels:
                if r.rel_type.value not in s:
                    s[r.rel_type.value] = [r.target[4:]]
                else:
                    s[r.rel_type.value].append(r.target[4:])
        if synset.lex_name not in synset_yaml:
            synset_yaml[synset.lex_name] = {}
        synset_yaml[synset.lex_name][synset.id[4:]] = s
        s["entries"] = entries_ordered(wn, synset.id)

    for key, synsets in synset_yaml.items():
        with open("src/yaml/%s.yaml" % key, "w") as outp:
            outp.write(yaml.dump(synsets))

