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
from wordnet_sql import SQLLexicon
from sense_keys import map_sense_key, unmap_sense_key
import argparse
import tempfile
import sqlite3
import gzip

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

def sense_from_yaml(y, lemma, pos, n, prefix):
    """
    Create a Sense object from the YAML data
    """
    s = Sense(map_sense_key(y["id"], prefix),
              f"{prefix}-" + y["synset"], None, n,
              y.get("adjposition"))
    s.sent = y.get("sent")
    for rel, targets in y.items():
        if rel in SenseRelType._value2member_map_:
            for target in targets:
                # Remap senses
                s.add_sense_relation(SenseRelation(
                    map_sense_key(target, prefix), SenseRelType(rel)))
        if rel in OtherSenseRelType._value2member_map_:
            for target in targets:
                s.add_sense_relation(SenseRelation(
                    map_sense_key(target, prefix), SenseRelType.OTHER, rel))
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

def synset_from_yaml(wn, props, id, lex_name, prefix):
    """
    Create a Synset from the YAML data
    """
    if "partOfSpeech" not in props:
        print("No part of speech for %s" % id)
        raise ValueError
    ss = Synset(f"{prefix}-" + id,
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
                    f"{prefix}-" + target, SynsetRelType(rel)))
    ss.members = [wn.entry_id_by_lemma_synset_id(lemma, ss.id) for lemma in props["members"]]
    return ss


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
                continue
            if not [sr for sr in target_synset.synset_relations if sr.target ==
                    synset.id and sr.rel_type == inverse_synset_rels[rel.rel_type]]:
                target_synset.add_synset_relation(
                    SynsetRelation(synset.id,
                                   inverse_synset_rels[rel.rel_type]))


def read_yaml_file(file : str, bufsize: int = 0x100000):
    """
    Read a YAML and return an iterator over its items. This generator handles
    large files by reading them in chunks.
    """
    with open(file, encoding="utf-8") as inp:
        # Read the first line
        line = inp.readline()
        # Initialize buffer
        buf = ""
        # While there are lines to read
        while line:
            # Read until we hit the buffer size
            while line:
                buf += line
                line = inp.readline()
                if len(buf) >= bufsize:
                    break
            # Continue reading lines until we hit a non-indented line
            while line:
                if not line.startswith(" "):
                    # Process the buffer
                    data = yaml.load(buf, Loader=CLoader)
                    if data is not None:
                        for k, v in data.items():
                            yield k, v
                    buf = ""
                    break
                else:
                    # Continue adding to the buffer
                    buf += line
                    line = inp.readline()
        # Process any remaining buffer
        if buf:
            data = yaml.load(buf, Loader=CLoader)
            if data is not None:
                for k, v in data.items():
                    yield k, v


def load(year="2022", plus=False,  db=None, cache_size=1000000, verbose=False, prefix="oewn", path=None):
    """
    Load wordnet from YAML files
    """
    if db:
        wn = SQLLexicon(prefix, "Open English Wordnet", "en",
                    "english-wordnet@googlegroups.com",
                     "https://creativecommons.org/licenses/by/4.0",
                     f"{year}+" if plus else year,
                     "https://github.com/globalwordnet/english-wordnet",
                     db=db, cache_size=cache_size)
    else:
        wn = Lexicon(prefix, "Open English Wordnet", "en",
                 "english-wordnet@googlegroups.com",
                 "https://creativecommons.org/licenses/by/4.0",
                 f"{year}+" if plus else year,
                 "https://github.com/globalwordnet/english-wordnet")
    if path is None:
        path = "src/plus/" if plus else "src/yaml/"
    with open(f"{path}/frames.yaml", encoding="utf-8") as inp:
        frames = yaml.load(inp, Loader=CLoader)
        wn.frames = [SyntacticBehaviour(k,v) for k,v in frames.items()]
    for f in glob(f"{path}/**/entries-*.yaml", recursive=True):
        if verbose:
            print(f"Loading entries from {f}", file=sys.stderr)
        with open(f, encoding="utf-8") as inp:
            y = yaml.load(inp, Loader=CLoader)

            for lemma, pos_map in y.items():
                for pos, props in pos_map.items():
                    entry = LexicalEntry(
                        "%s-%s-%s" % (prefix, escape_lemma(lemma), pos))
                    entry.set_lemma(Lemma(lemma, PartOfSpeech(pos[:1])))
                    if "form" in props:
                        for form in props["form"]:
                            entry.add_form(Form(form))
                    for n, sense in enumerate(props["sense"]):
                        entry.add_sense(sense_from_yaml(sense, lemma, pos, n, prefix))
                    entry.pronunciation = pronunciation_from_yaml(props)
                    wn.add_entry(entry)

    for f in glob(f"{path}/**/*.yaml", recursive=True):
        if verbose:
            print(f"Loading synsets from {f}", file=sys.stderr)
        lex_name = f[9:-5]
        if "entries" not in f and "frames" not in f:
            for id, props in read_yaml_file(f):
                wn.add_synset(synset_from_yaml(wn, props, id, lex_name, prefix))
#            with open(f, encoding="utf-8") as inp:
#                y = yaml.load(inp, Loader=CLoader)
#
#                if y is None:
#                    continue
#                for id, props in y.items():
#                    wn.add_synset(synset_from_yaml(wn, props, id, lex_name, prefix))

    for entry in wn.entries():
        for sense in entry.senses:
            fix_sense_rels(wn, sense)

    for synset in wn.synsets():
        fix_synset_rels(wn, synset)

    by_lex_name = {}
    for synset in wn.synsets():
        if synset.lex_name not in by_lex_name:
            by_lex_name[synset.lex_name] = Lexicon(
                prefix, "Open English Wordnet", "en",
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


#def sense_to_yaml(wn, s, sb_map, prefix):
#    """Converts a single sense to the YAML form"""
#    y = {}
#    y["synset"] = s.synset[len(prefix)+1:]
#    y["id"] = unmap_sense_key(s.sense_key)
#    if s.adjposition:
#        y["adjposition"] = s.adjposition
#    for sr in s.sense_relations:
#        if sr.rel_type not in ignored_symmetric_sense_rels:
#            if sr.rel_type.value not in y:
#                if not wn.sense_by_id(sr.target):
#                    print(sr.target)
#                if wn.sense_by_id(sr.target):
#                    y[sr.rel_type.value] = [map_sense_key(
#                        wn.sense_by_id(sr.target).sense_key)]
#                else:
#                    print(f"Dead link from {s.sense_key} to {sr.target}")
#            else:
#                if wn.sense_by_id(sr.target):
#                    y[sr.rel_type.value].append(map_sense_key(
#                        wn.sense_by_id(sr.target).sense_key))
#                else:
#                    print(f"Dead link from {s.sense_key} to {sr.target}")
#    if sb_map[s.id]:
#        y["subcat"] = sorted(sb_map[s.id])
#    if s.sent:
#        y["sent"] = s.sent
#    return y


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
    parse = argparse.ArgumentParser(
        description="Convert Open English Wordnet YAML data to GWA standard XML"
    )
    parse.add_argument(
        "--year",
        type=str,
        help="Year of the Wordnet version (default 2024)",
        default="2024"
    )
    parse.add_argument(
        "--plus",
        action="store_true",
        help="Use the Wordnet+ source files",
        default=False
    )
    parse.add_argument(
        "--output",
        type=str,
        help="Output XML file (default wn.xml)",
        default="wn.xml"
        )
    parse.add_argument(
        "--sql",
        action="store_true",
        help="Use MySQL for storage (for large Wordnets)",
        default=False
        )
    parse.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
        default=False
        )
    parse.add_argument(
        "--cache-size",
        type=int,
        help="Cache size for MySQL (default 1000000)",
        default=1000000
        )
    parse.add_argument(
        "--folder",
        type=str,
        help="Folder containing YAML files (default src/yaml or src/plus)",
        default=None
        )
    parse.add_argument(
        "--prefix",
        type=str,
        help="Resource name for XML metadata (default oewn)",
        default="oewn"
        )
    parse.add_argument(
        "--gzip",
        action="store_true",
        help="Compress output XML with gzip",
        default=False
        )
    args = parse.parse_args()
    
    if args.sql:
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            with sqlite3.connect(tmp.name) as db:
                wn = load(year=args.year, plus=args.plus, db=db, verbose=args.verbose,
                          cache_size=args.cache_size, prefix=args.prefix,
                          path=args.folder)
    else:
        wn = load(year=args.year, plus=args.plus, verbose=args.verbose, 
                  prefix=args.prefix, path=args.folder)
    if args.gzip:
        with gzip.open(args.output, "wt", encoding="utf-8") as outp:
            wn.to_xml(outp)
    else:
        with codecs.open(args.output, "w", "utf-8") as outp:
            wn.to_xml(outp)


if __name__ == "__main__":
    main()

