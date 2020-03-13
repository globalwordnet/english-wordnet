"""Utility functions for changing the wordnet"""
from wordnet import *
import pickle
import os
from glob import glob
import fileinput
import hashlib

sense_id_re = re.compile(r"ewn-(.*)-(.)-(\d{8})-\d{2}")

def load_wordnet():
    """Load the wordnet from wn.xml"""
    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))
    return wn

def delete_rel(source, target):
    """Delete all relationships between two synsets"""
    print("Delete %s =*=> %s" % (source.id, target.id))
    wn_source = parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    ss.synset_relations = [r for r in ss.synset_relations if r.target != target.id]
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

def decompose_sense_id(sense_id):
    m = sense_id_re.match(sense_id)
    if m:
        lemma = m.group(1)
        pos = m.group(2)
        ssid = m.group(3)
        return ("ewn-%s-%s" % (ssid, pos), "ewn-%s-%s" % (lemma, pos))
    else:
        raise Exception("Not a sense ID")

def delete_sense_rel(wn, source, target):
    """Delete all relationships between two senses"""
    print("Delete %s =*=> %s" % (source, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = parse_wordnet("src/wn-%s.xml" % lex_name)
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations = [r for r in sense.sense_relations if r.target != target]
    with open("src/wn-%s.xml" % lex_name, "w") as out:
        wn_source.to_xml(out, True)


def insert_rel(source, rel_type, target):
    """Insert a single relation between two synsets"""
    print("Insert %s =%s=> %s" % (source.id, rel_type, target.id))
    wn_source = parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    if [r for r in ss.synset_relations if r.target == target.id and r.rel_type == rel_type]:
        print("Already exists")
        return
    ss.synset_relations.append(SynsetRelation(target.id, rel_type))
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

def empty_if_none(x):
    """Returns an empty list if passed None otherwise the argument"""
    if x:
        return x
    else:
        return []

def escape_lemma(lemma):
    """Format the lemma so it is valid XML id"""
    def elc(c):
        if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z'):
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
        elif c == '-':
            return '-'
        else:
            return '-%04x-' % ord(c)

    return "".join(elc(c) for c in lemma)

def synset_key(synset_id):
    return synset_id[4:-2]

def add_entry(wn, synset, lemma, idx=0, n=-1):
    """Add a new lemma to a synset"""
    print("Adding %s to synset %s" % (lemma, synset.id))
    n_entries = len(empty_if_none(wn.members_by_id(synset.id)))
    entry_global = [entry for entry in empty_if_none(wn.entry_by_lemma(lemma)) 
            if wn.entry_by_id(entry).lemma.part_of_speech == synset.part_of_speech or
               wn.entry_by_id(entry).lemma.part_of_speech == PartOfSpeech.ADJECTIVE and synset.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE or
               wn.entry_by_id(entry).lemma.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE and synset.part_of_speech == PartOfSpeech.ADJECTIVE]
                

    if len(entry_global) == 1:
        entry_global = wn.entry_by_id(entry_global[0])
        n_senses = len(entry_global.senses)
    else:
        entry_global = None
        n_senses = 0

    if idx <= 0:
        idx = n_entries + 1
    elif idx > n_entries + 1:
        raise Exception("IDX value specified is higher than number of entries")
    elif idx == n_entries + 1:
        pass
    else:
        for sense_id in sense_ids_for_synset(wn, synset):
            this_idx = int(sense_id[-2:])
            if this_idx >= idx:
                change_sense_idx(wn, sense_id, this_idx + 1)

    if n < 0:
        n = n_senses
    elif n > n_senses:
        raise Exception("n value exceeds number of senses for lemma")
    elif n == n_senses:
        pass
    else:
        sense_n = 0
        for sense in entry_global.senses:
            if sense_n >= n:
                change_sense_n(wn, entry_global, sense.id, sense_n + 1)
            sense_n += 1

    wn_synset = parse_wordnet("src/wn-%s.xml" % synset.lex_name)
    entries = [entry for entry in empty_if_none(wn_synset.entry_by_lemma(lemma)) if wn.entry_by_id(entry).lemma.part_of_speech == synset.part_of_speech]

    if entries:
        if len(entries) != 1:
            raise Exception("More than one entry for part of speech")
        entry = wn_synset.entry_by_id(entries[0])

        entry.senses.append(Sense(
            id="ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), synset.part_of_speech.value,
                synset_key(synset.id), idx),
            synset=synset.id,
            n=n,
            sense_key=None))
    else:
        n = 0
        wn_synset = parse_wordnet("src/wn-%s.xml" % synset.lex_name)
        entry = LexicalEntry(
            "ewn-%s-%s" % (escape_lemma(lemma), synset.part_of_speech.value))
        entry.set_lemma(Lemma(lemma, synset.part_of_speech))
        entry.add_sense( Sense(
                    id="ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), synset.part_of_speech.value,
                        synset_key(synset.id), idx),
                    synset=synset.id, n=n, sense_key=None))
        wn_synset.add_entry(entry)
    with open("src/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)

def delete_entry(wn, synset, entry_id):
    """Delete a lemma from a synset"""
    print("Deleting %s from synset %s" % (entry_id, synset.id))
    n_entries = len(wn.members_by_id(synset.id))
    entry_global = wn.entry_by_id(entry_id)
    
    if entry_global:
        idx = [int(sense.id[-2:]) for sense in entry_global.senses if sense.synset == synset.id][0]
        n_senses = len(entry_global.senses)
    else:
        print("No entry for this lemma")
        return

    if n_senses != 1:
        n = [ind for ind, sense in enumerate(entry_global.senses) if sense.synset == synset.id][0]
        sense_n = 0
        for sense in entry_global.senses:
            if sense_n >= n:
                change_sense_n(wn, entry_global, sense.id, sense_n - 1)
            sense_n += 1

    for sense_id in sense_ids_for_synset(wn, synset):
        this_idx = int(sense_id[-2:])
        if this_idx >= idx:
            change_sense_idx(wn, sense_id, this_idx - 1)

    for sense in entry_global.senses:
        if sense.synset == synset.id:
            for rel in sense.sense_relations:
                delete_sense_rel(wn, rel.target, sense.id)

    if n_senses == 1: # then delete the whole entry
        wn_synset = parse_wordnet("src/wn-%s.xml" % synset.lex_name)
        wn_synset.entries = [entry for entry in wn_synset.entries if entry.id != entry_global.id]
    else:
        wn_synset = parse_wordnet("src/wn-%s.xml" % synset.lex_name)
        entry = wn_synset.entry_by_id(entry_global.id)
        entry.senses = [sense for sense in entry.senses if sense.synset != synset.id]
    with open("src/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)

def delete_synset(wn, synset, supersede, reason, delent=True):
    """Delete a synset"""
    print("Deleting synset %s" % synset.id)
    
    if delent:
        entries = wn.members_by_id(synset.id)

        for entry in entries:
            delete_entry(wn, synset, 
                    "ewn-%s-%s" % (escape_lemma(entry), synset.part_of_speech.value))

    for rel in synset.synset_relations:
        delete_rel(wn.synset_by_id(rel.target), synset)

    wn_synset = parse_wordnet("src/wn-%s.xml" % synset.lex_name)
    wn_synset.synsets = [ss for ss in wn_synset.synsets
            if synset.id != ss.id]
    with open("src/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)
    if supersede:
        if not isinstance(supersede, list):
            supersede = [supersede]
    else:
        supersede = []
    with open("src/deprecations.csv", "a") as out:
        out.write("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" %
                (synset.id, synset.ili,
                    ",".join(s.id for s in supersede),
                    ",".join(s.ili for s in supersede),
                    reason.replace("\n","").replace("\"","\"\"")))


def change_sense_n(wn, entry, sense_id, new_n):
    """Change the position of a sense within an entry (changes only this sense)"""
    print("Changing n of sense %s of %s to %s" % (sense_id, entry.lemma.written_form, new_n))

    senses = [sense for sense in entry.senses if sense.id == sense_id]
    if len(senses) != 1:
        raise Exception("Could not find sense")
    sense = senses[0]
    synset = wn.synset_by_id(sense.synset)
    lexname = synset.lex_name

    wn_synset = parse_wordnet("src/wn-%s.xml" % lexname)
    entry = wn_synset.entry_by_id(entry.id)
    sense = [sense for sense in entry.senses if sense.id == sense_id][0]
    sense.n = new_n
    with open("src/wn-%s.xml" % lexname, "w") as out:
        wn_synset.to_xml(out, True)

def change_sense_idx(wn, sense_id, new_idx):
    """Change the position of a lemma within a synset"""
    print("Changing idx of sense %s to %s" % (sense_id, new_idx))
    new_sense_id = "%s-%02d" % (sense_id[:-3], new_idx)
    # This is implemented as a find and replace, as this is likely less error-prone
    # than doing it properly
    for f in glob("src/wn-*.xml"):
        with fileinput.FileInput(f, inplace=True) as file:
            for line in file:
                print(line.replace(sense_id, new_sense_id), end='')

def sense_ids_for_synset(wn, synset):
    return [sense.id for lemma in wn.members_by_id(synset.id)
            for entry in wn.entry_by_lemma(lemma)
            for sense in wn.entry_by_id(entry).senses
            if sense.synset == synset.id]

def new_id(wn, pos, definition):
    s = hashlib.sha256()
    s.update(definition.encode())
    nid = "ewn-8%07d-%s" % ((int(s.hexdigest(),16) % 10000000), pos)
    if wn.synset_by_id(nid):
        print("Could not find ID for new synset. Either a duplicate definition or a hash collision for " + nid + ". Note it is possible to force a synset ID by giving it as an argument")
        sys.exit(-1)
    return nid


def add_synset(wn, definition, lexfile, pos, ssid=None):
    if not ssid:
        ssid = new_id(wn, pos, definition)
    ss = Synset(ssid, "in",
            PartOfSpeech(pos), lexfile)
    ss.definitions = [Definition(definition)]
    wn2 = parse_wordnet("src/wn-%s.xml" % lexfile)
    wn2.add_synset(ss)
    wn.add_synset(ss) # So downstream split/merge script work!
    with open("src/wn-%s.xml" % lexfile, "w") as out:
        wn2.to_xml(out, True)
    return ssid

