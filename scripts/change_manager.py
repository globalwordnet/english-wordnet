"""Utility functions for changing the wordnet"""
from wordnet import *
import pickle
import os

def load_wordnet():
    """Load the wordnet from wn.xml"""
    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))
    return wn

def delete_rel(source, target):
    """Delete all relationships between two synsets"""
    print("Delete %s =*=> %s" % (source.id, target.id))
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    ss.synset_relations = [r for r in ss.synset_relations if r.target != target.id]
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

def insert_rel(source, rel_type, target):
    """Insert a single relation between two synsets"""
    print("Insert %s =%s=> %s" % (source.id, rel_type, target.id))
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    if [r for r in ss.synset_relations if r.target == target.id and r.rel_type == rel_type]:
        print("Already exists")
        return
    ss.synset_relations.append(wordnet.SynsetRelation(target.id, rel_type))
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

 

def add_entry(wn, synset, lemma, idx=0, n=-1):
    """Add a new lemma to a synset"""
    print("Adding %s to synset %s" % (lemma, synset))
    wn_synset = wordnet.parse_wordnet("src/wn-%s.xml" % synset.lex_name)
    entries = [entry for entry in wn_synset.entry_by_lemma(lemma) if entry.lemma.part_of_speech == synset.part_of_speech]
    n_entries = len(wn.members_by_id(synset.id))
    if idx <= 0:
        idx = n_entries + 1
    elif idx > n_entries + 1:
        raise Exception("IDX value specified is higher than number of entries")
    elif idx == n_entries + 1:
        pass
    else:
        raise Exception("TODO: Bump entries")
    if entries:
        if len(entries) != 1:
            raise Exception("More than one entry for part of speech")
        entry = entries[0]
        n_senses = [entry for entry in wn.entry_by_lemma(lemma) if entry.lemma.part_of_speech == synset.part_of_speech]
        if n < 0:
            n = n_senses
        elif n > n_senses:
            raise Exception("n value exceeds number of senses for lemma")
        elif n == n_senses:
            pass
        else:
            raise Exception("TODO: Bump entries")

        entry.senses.append(Sense(
            id="ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), synset.part_of_speech,
                synset_key(synset.id), idx),
            synset.id,
            n,
            None))
    else:
        n = 0
        wn_source.add_entry(LexicalEntry(
            "ewn-%s-%s" % (escape_lemma(lemma), synset.part_of_speech),
            Lemma(lemma, synset.part_of_speech),
            senses=[
                Sense(
                    id="ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), synset.part_of_speech,
                        synset_key(synset.id), idx),
                    synset.id, n, None)]))
    with open("src/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)



            


