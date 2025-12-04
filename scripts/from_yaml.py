"""Converts the internal YAML data into a GWA standard XML file and
  writes it to `wn.xml`"""
import sys
import yaml
from glob import glob
from yaml import CLoader
import codecs
from wordnet import (Lexicon, Lemma, PartOfSpeech, LexicalEntry, Sense, 
                     SenseRelation, Definition, Example, Pronunciation, 
                     Synset, SynsetRelation, SynsetRelType, Form,
                     SenseRelType, OtherSenseRelType, SyntacticBehaviour,
                     escape_lemma, inverse_sense_rels,
                     inverse_synset_rels)

entry_orders = {}

KEY_PREFIX_LEN = 5 # = len("oewn-")

def escape_sense_key(s : str) -> str:
    """
    Escape a sense key for OEWN
    """
    return (s.replace("-", "--")
            .replace("'", "-ap-").replace(" ", "_")
            .replace("!", "-excl-").replace("#", "-num-")
            .replace("$", "-dollar-").replace("%", "-percnt-")
            .replace("&", "-amp-").replace("(", "-lpar-")
            .replace(")", "-rpar-").replace("*", "-ast-")
            .replace("+", "-plus-").replace(",", "-comma-")
            .replace("/", "-sol-").replace("{", "-lbrace-")
            .replace("|", "-vert-").replace("}", "-rbrace-")
            .replace("~", "-tilde-").replace("¢", "-cent-")
            .replace("£", "-pound-").replace("§", "-sect-")
            .replace("©", "-copy-").replace("®", "-reg-")
            .replace("°", "-deg-").replace("´", "-acute-")
            .replace("¶", "-para-").replace("º", "-ordm-"))

def unescape_sense_key(s : str) -> str:
    """
    Unescape a sense key from OEWN
    """
    return (s.replace("-ap-", "'").replace("_", " ")
            .replace("-excl-", "!").replace("-num-", "#")
            .replace("-dollar-", "$").replace("-percnt-", "%")
            .replace("-amp-", "&").replace("-lpar-", "(")
            .replace("-rpar-", ")").replace("-ast-", "*")
            .replace("-plus-", "+").replace("-comma-", ",")
            .replace("-sol-", "/").replace("-lbrace-", "{")
            .replace("-vert-", "|").replace("-rbrace-", "}")
            .replace("-tilde-", "~").replace("-cent-", "¢")
            .replace("-pound-", "£").replace("-sect-", "§")
            .replace("-copy-", "©").replace("-reg-", "®")
            .replace("-deg-", "°").replace("-acute-", "´")
            .replace("-para-", "¶").replace("-ordm-", "º")
            .replace("--", "-"))

def map_sense_key(sk):
    """
    Maps a sense key into an OEWN from
    """
    if "%" in sk:
        e = sk.split("%")
        if len(e) > 2:
            lemma = "%".join(e[:-1])
            info = e[-1]
        else:
            lemma = e[0]
            info = e[1]
        lemma = escape_sense_key(lemma)
        return ("oewn-" + lemma +
            "__" + info.replace("_","-sp-").replace(":","."))
    else:
        sk = escape_sense_key(sk)
        return "oewn-" + sk

def unmap_sense_key(sk):
    """
    Maps an OEWN sense key to a WN sense key
    """
    if "__" in sk:
        e = sk.split("__")
        oewn_key = e[0][KEY_PREFIX_LEN:]
        r = "__".join(e[1:])
        return (unescape_sense_key(oewn_key) + "%" +
                r.replace("-sp-", "_").replace(".", ":"))
    else: 
        return unescape_sense_key(sk[KEY_PREFIX_LEN:])


def make_pos(y, pos):
    """
    Convert a part of speech value to a single character
    """
    if "adjposition" in y:
        return y["adjposition"] + "-" + pos
    elif len(pos) > 1:
        return pos[:1]
    else:
        return pos

def sense_from_yaml(y, lemma, pos, n):
    """
    Create a Sense object from the YAML data
    """
    s = Sense(map_sense_key(y["id"]),
              "oewn-" + y["synset"], None, n,
              y.get("adjposition"))
    s.sent = y.get("sent")
    for rel, targets in y.items():
        if rel in SenseRelType._value2member_map_:
            for target in targets:
                # Remap senses
                s.add_sense_relation(SenseRelation(
                    map_sense_key(target), SenseRelType(rel)))
        if rel in OtherSenseRelType._value2member_map_:
            for target in targets:
                s.add_sense_relation(SenseRelation(
                    map_sense_key(target), SenseRelType.OTHER, rel))
    if "sent" in y:
        s.sent = y["sent"]
    if "subcat" in y:
        s.subcat = y["subcat"]
    return s

def pronunciation_from_yaml(props):
    """
    Create a Pronunciation object from the YAML data
    """
    return [Pronunciation(p["value"], p.get("variety")) 
            for p in props.get("pronunciation",[])]

def synset_from_yaml(wn, props, id, lex_name):
    """
    Create a Synset from the YAML data
    """
    if "partOfSpeech" not in props:
        print("No part of speech for %s" % id)
        raise ValueError
    ss = Synset("oewn-" + id,
                props.get("ili", "in"),
                PartOfSpeech(props["partOfSpeech"]),
                lex_name,
                props.get("source"))
    ss.wikidata = props.get("wikidata")
    for defn in props["definition"]:
        ss.add_definition(Definition(defn))
    if "ili" not in props:
        ss.add_definition(Definition(props["definition"][0]), True)
    for example in props.get("example", []):
        if isinstance(example, str):
            ss.add_example(Example(example))
        else:
            ss.add_example(Example(example["text"], example["source"]))
    for rel, targets in props.items():
        if rel in SynsetRelType._value2member_map_:
            for target in targets:
                ss.add_synset_relation(SynsetRelation(
                    "oewn-" + target, SynsetRelType(rel)))
    ss.members = [entry_for_synset(wn, ss, lemma) for lemma in props["members"]]
    return ss

def entry_for_synset(wn, ss, lemma):
    """
    Find the entry for a synset member
    """
    for e in wn.entry_by_lemma(lemma):
        for s in wn.entry_by_id(e).senses:
            if s.synset == ss.id:
                return e
    print("Could not find %s referring to %s" % (lemma, ss.id))
    return ""


def fix_sense_rels(wn, sense):
    """
    Add inverse sense relations as needed
    """
    for rel in sense.sense_relations:
        target_id = rel.target
        if (rel.rel_type in inverse_sense_rels
                and inverse_sense_rels[rel.rel_type] != rel.rel_type):
            sense2 = wn.sense_by_id(target_id)
            if not any(sr for sr in sense2.sense_relations
                    if sr.rel_type == inverse_sense_rels[rel.rel_type] and
                        sr.target == sense.id):
                sense2.add_sense_relation(
                        SenseRelation(sense.id,
                            inverse_sense_rels[rel.rel_type]))


def fix_synset_rels(wn, synset):
    """
    Add inverse synset relations as needed
    """
    for rel in synset.synset_relations:
        if (rel.rel_type in inverse_synset_rels
                and inverse_synset_rels[rel.rel_type] != rel.rel_type):
            target_synset = wn.synset_by_id(rel.target)
            if not target_synset:
                print(synset.id)
                print(rel.target)
            if not [sr for sr in target_synset.synset_relations if sr.target ==
                    synset.id and sr.rel_type == inverse_synset_rels[rel.rel_type]]:
                target_synset.add_synset_relation(
                    SynsetRelation(synset.id,
                                   inverse_synset_rels[rel.rel_type]))


def load(year="2022"):
    """
    Load wordnet from YAML files
    """
    wn = Lexicon("oewn", "Open Engish Wordnet", "en",
                 "english-wordnet@googlegroups.com",
                 "https://creativecommons.org/licenses/by/4.0",
                 year,
                 "https://github.com/globalwordnet/english-wordnet")
    with open("src/yaml/frames.yaml", encoding="utf-8") as inp:
        frames = yaml.load(inp, Loader=CLoader)
        wn.frames = [SyntacticBehaviour(k,v) for k,v in frames.items()]
    for f in glob("src/yaml/entries-*.yaml"):
        with open(f, encoding="utf-8") as inp:
            y = yaml.load(inp, Loader=CLoader)

            for lemma, pos_map in y.items():
                for pos, props in pos_map.items():
                    entry = LexicalEntry(
                        "oewn-%s-%s" % (escape_lemma(lemma), pos))
                    entry.set_lemma(Lemma(lemma, PartOfSpeech(pos[:1])))
                    if "form" in props:
                        for form in props["form"]:
                            entry.add_form(Form(form))
                    for n, sense in enumerate(props["sense"]):
                        entry.add_sense(sense_from_yaml(sense, lemma, pos, n))
                    entry.pronunciation = pronunciation_from_yaml(props)
                    wn.add_entry(entry)

    for f in glob("src/yaml/*.yaml"):
        lex_name = f[9:-5]
        if "entries" not in f and "frames" not in f:
            with open(f, encoding="utf-8") as inp:
                y = yaml.load(inp, Loader=CLoader)

                for id, props in y.items():
                    wn.add_synset(synset_from_yaml(wn, props, id, lex_name))
                    entry_orders[id] = props["members"]

    for entry in wn.entries:
        for sense in entry.senses:
            fix_sense_rels(wn, sense)

    for synset in wn.synsets:
        fix_synset_rels(wn, synset)

    by_lex_name = {}
    for synset in wn.synsets:
        if synset.lex_name not in by_lex_name:
            by_lex_name[synset.lex_name] = Lexicon(
                "oewn", "Open English Wordnet", "en",
                "john@mccr.ae", "https://wordnet.princeton.edu/license-and-commercial-use",
                year, "https://github.com/globalwordnet/english-wordnet")
        by_lex_name[synset.lex_name].add_synset(synset)

    return wn


def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


ignored_symmetric_sense_rels = set([
    SenseRelType.HAS_DOMAIN_REGION, SenseRelType.HAS_DOMAIN_TOPIC,
    SenseRelType.IS_EXEMPLIFIED_BY])


def sense_to_yaml(wn, s, sb_map):
    """Converts a single sense to the YAML form"""
    y = {}
    y["synset"] = s.synset[KEY_PREFIX_LEN:]
    y["id"] = unmap_sense_key(s.sense_key)
    if s.adjposition:
        y["adjposition"] = s.adjposition
    for sr in s.sense_relations:
        if sr.rel_type not in ignored_symmetric_sense_rels:
            if sr.rel_type.value not in y:
                if not wn.sense_by_id(sr.target):
                    print(sr.target)
                if wn.sense_by_id(sr.target):
                    y[sr.rel_type.value] = [map_sense_key(
                        wn.sense_by_id(sr.target).sense_key)]
                else:
                    print(f"Dead link from {s.sense_key} to {sr.target}")
            else:
                if wn.sense_by_id(sr.target):
                    y[sr.rel_type.value].append(map_sense_key(
                        wn.sense_by_id(sr.target).sense_key))
                else:
                    print(f"Dead link from {s.sense_key} to {sr.target}")
    if sb_map[s.id]:
        y["subcat"] = sorted(sb_map[s.id])
    if s.sent:
        y["sent"] = s.sent
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


frames = {
    "nonreferential": "It is ----ing",
    "nonreferential-sent": "It ----s that CLAUSE",
    "ditransitive": "Somebody ----s somebody something",
    "via": "Somebody ----s",
    "via-adj": "Somebody ----s Adjective",
    "via-at": "Somebody ----s at something",
    "via-for": "Somebody ----s for something",
    "via-ger": "Somebody ----s VERB-ing",
    "via-inf": "Somebody ----s INFINITIVE",
    "via-on-anim": "Somebody ----s on somebody",
    "via-on-inanim": "Somebody ----s on something",
    "via-out-of": "Somebody ----s out of somebody",
    "via-pp": "Somebody ----s PP",
    "via-that": "Somebody ----s that CLAUSE",
    "via-to": "Somebody ----s to somebody",
    "via-to-inf": "Somebody ----s to INFINITIVE",
    "via-whether-inf": "Somebody ----s whether INFINITIVE",
    "vibody": "Somebody's (body part) ----s",
    "vii": "Something ----s",
    "vii-adj": "Something ----s Adjective/Noun",
    "vii-inf": "Something ----s INFINITIVE",
    "vii-pp": "Something is ----ing PP",
    "vii-to": "Something ----s to somebody",
    "vtaa": "Somebody ----s somebody",
    "vtaa-inf": "Somebody ----s somebody INFINITIVE",
    "vtaa-into-ger": "Somebody ----s somebody into V-ing something",
    "vtaa-of": "Somebody ----s somebody of something",
    "vtaa-pp": "Somebody ----s somebody PP",
    "vtaa-to-inf": "Somebody ----s somebody to INFINITIVE",
    "vtaa-with": "Somebody ----s somebody with something",
    "vtai": "Somebody ----s something",
    "vtai-from": "Somebody ----s something from somebody",
    "vtai-on": "Somebody ----s something on somebody",
    "vtai-pp": "Somebody ----s something PP",
    "vtai-to": "Somebody ----s something to somebody",
    "vtai-with": "Somebody ----s something with something",
    "vtia": "Something ----s somebody",
    "vtii": "Something ----s something",
    "vtii-adj": "Something ----s something Adjective/Noun",
}

frames_inv = {v: k for k, v in frames.items()}

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


def lemma2senseorder(wn, lemma, synset_id):
    """Find sense order of lemmas"""
    for e2 in wn.entry_by_lemma(lemma):
        for sense in wn.entry_by_id(e2).senses:
            if sense.synset == synset_id:
                return sense.id[-2:]
    return "99"


def entries_ordered(wn, synset_id):
    """Get the lemmas for entries ordered correctly"""
    e = wn.members_by_id(synset_id)
    e.sort(key=lambda lemma: lemma2senseorder(wn, lemma, synset_id))
    return e


def main():
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = "2024"
    wn = load(year)
    with codecs.open("wn.xml", "w", "utf-8") as outp:
        wn.to_xml(outp)


if __name__ == "__main__":
    main()

