import yaml
from glob import glob
from wordnet import *
from change_manager import escape_lemma, synset_key
from yaml import CLoader

entry_orders = {}

def map_sense_key(sk):
    e = sk.split("%")
    e[1] = e[1].replace("_", ":")
    if len(e[1].split(":")) == 3:
        return "%s%%%s::" % (e[0], e[1])
    else:
        return "%s%%%s" % (e[0], e[1])

def sense_from_yaml(y, lemma, pos, n):
    s = Sense("ewn-%s-%s-%s" % (
        escape_lemma(lemma), pos, y["synset"][:-2]),
        "ewn-" + y["synset"], map_sense_key(y["key"]), n,
        y.get("adjposition"))
    for rel, targets in y.items():
        if rel in SenseRelType._value2member_map_:
            for target in targets:
                # Remap senses
                s.add_sense_relation(SenseRelation(
                    map_sense_key(target), SenseRelType(rel)))
    return s

def synset_from_yaml(props, id, lex_name):
    if "pos" not in props:
        print(props)
    ss = Synset("ewn-" + id,
            props.get("ili", "in"),
            PartOfSpeech(props["pos"]),
            lex_name,
            props.get("source"))
    for defn in props["definitions"]:
        ss.add_definition(Definition(defn))
    if "ili" not in props:
        ss.add_definition(Definition(props["definitions"][0]), True)
    for example in props.get("examples", []):
        if isinstance(example, str):
            ss.add_example(Example(example))
        else:
            ss.add_example(Example(example["text"], example["source"]))
    for rel, targets in props.items():
        if rel in SynsetRelType._value2member_map_:
            for target in targets:
                ss.add_synset_relation(SynsetRelation(
                    "ewn-" + target, SynsetRelType(rel)))
    return ss

def fix_sense_id(sense, lemma, key2id):
    idx = entry_orders[sense.synset[4:]].index(lemma)
    sense.id = "%s-%02d" % (sense.id, idx)
    key2id[sense.sense_key] = sense.id

def fix_sense_rels(wn, sense, key2id):
    for rel in sense.sense_relations:
        if rel.target.startswith("ewn-"):
           rel.target = key2id[rel.target[:-3]]
           if (rel.rel_type in inverse_sense_rels 
               and inverse_sense_rels[rel.rel_type] != rel.rel_type):
               wn.sense_by_id(rel.target[:-3]).add_sense_relation(
                       SenseRelation(sense.id,
                           inverse_sense_rels[rel.rel_type]))

def fix_synset_rels(wn, synset):
    for rel in synset.synset_relations:
        if (rel.rel_type in inverse_synset_rels
                and inverse_synset_rels[rel.rel_type] != rel.rel_type):
            wn.synset_by_id(rel.target).add_synset_relation(
                    SenseRelation(synset.id,
                        inverse_synset_rels[rel.rel_type]))

def main():
    wn = Lexicon("ewn", "Engish WordNet", "en", 
            "english-wordnet@googlegroups.com",
            "https://creativecommons.org/licenses/by/4.0",
            "2020",
            "https://github.com/globalwordnet/english-wordnet")
    for f in glob("src/yaml/entries-*.yaml"):
        with open(f) as inp:
            y = yaml.load(inp, Loader=CLoader)

            for lemma, pos_map in y.items():
                for pos, props in pos_map.items():
                    entry = LexicalEntry(
                            "ewn-%s-%s" % (escape_lemma(lemma), pos))
                    entry.set_lemma(Lemma(lemma, PartOfSpeech(pos)))
                    if "form" in props:
                        for form in props["form"]:
                            entry.add_form(form)
                    for n, sense in enumerate(props["senses"]):
                        entry.add_sense(sense_from_yaml(sense, lemma, pos, n))
                    wn.add_entry(entry)

    for f in glob("src/yaml/*.yaml"): 
        lex_name = f[9:-4]
        if "entries" not in f:
            with open(f) as inp:
                y = yaml.load(inp, Loader=CLoader)

                for id, props in y.items():
                    wn.add_synset(synset_from_yaml(props, id, lex_name))
                    entry_orders[id] = props["entries"]

    key2id = {}
    for entry in wn.entries:
        for sense in entry.senses:
            fix_sense_id(sense, entry.lemma.written_form, key2id)

    for entry in wn.entries:
        for sense in entry.senses:
            fix_sense_rels(wn, sense, key2id)

    for synset in wn.synsets:
        fix_synset_rels(wn, synset)

    with open("wn-from-yaml.xml","w") as outp:
        wn.to_xml(outp, True)

if __name__ == "__main__":
    main()

