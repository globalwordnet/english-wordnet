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
    wn_source = parse_wordnet("src/xml/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    ss.synset_relations = [r for r in ss.synset_relations if r.target != target.id]
    with open("src/xml/wn-%s.xml" % source.lex_name, "w") as out:
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
    wn_source = parse_wordnet("src/xml/wn-%s.xml" % lex_name)
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations = [r for r in sense.sense_relations if r.target != target]
    with open("src/xml/wn-%s.xml" % lex_name, "w") as out:
        wn_source.to_xml(out, True)


def insert_rel(source, rel_type, target):
    """Insert a single relation between two synsets"""
    print("Insert %s =%s=> %s" % (source.id, rel_type, target.id))
    wn_source = parse_wordnet("src/xml/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    if [r for r in ss.synset_relations if r.target == target.id and r.rel_type == rel_type]:
        print("Already exists")
        return
    ss.synset_relations.append(SynsetRelation(target.id, rel_type))
    with open("src/xml/wn-%s.xml" % source.lex_name, "w") as out:
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
        if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') or c == '.':
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
        elif c == ',':
            return '-cm-'
        elif c == '!':
            return '-ex-'
        else:
            return '-%04x-' % ord(c)

    return "".join(elc(c) for c in lemma)

def synset_key(synset_id):
    return synset_id[4:-2]

def change_entry(wn, synset, target_synset, lemma):
    """Change an entry, only works if both synsets are in the same file"""
    print("Adding %s to synset %s" % (lemma, synset.id))
    n_entries = len(empty_if_none(wn.members_by_id(target_synset.id)))
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

    idx = n_entries + 1
    n = n_senses
     
    wn_synset = parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    entries = [entry for entry in empty_if_none(wn_synset.entry_by_lemma(lemma)) if wn.entry_by_id(entry).lemma.part_of_speech == synset.part_of_speech]

    for entry in entries:
        for sense in wn_synset.entry_by_id(entry).senses:
            if sense.synset == synset.id:
                print("Moving %s to %s" % (sense.id, target_synset.id))
                sense.synset = target_synset.id
                sense.id = "ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), 
                        target_synset.part_of_speech.value,
                        synset_key(target_synset.id), idx)

    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)

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

    wn_synset = parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    entries = [entry for entry in empty_if_none(wn_synset.entry_by_lemma(lemma)) if wn.entry_by_id(entry).lemma.part_of_speech == synset.part_of_speech]

    if entries:
        if len(entries) != 1:
            raise Exception("More than one entry for part of speech")
        wn_entry = wn.entry_by_id(entries[0])
        entry = wn_synset.entry_by_id(entries[0])
        sense = Sense(
            id="ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), synset.part_of_speech.value,
                synset_key(synset.id), idx),
            synset=synset.id,
            n=n,
            sense_key=None)

        wn_entry.senses.append(sense)
        entry.senses.append(sense)
    else:
        n = 0
        entry = LexicalEntry(
            "ewn-%s-%s" % (escape_lemma(lemma), synset.part_of_speech.value))
        entry.set_lemma(Lemma(lemma, synset.part_of_speech))
        entry.add_sense( Sense(
                    id="ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), synset.part_of_speech.value,
                        synset_key(synset.id), idx),
                    synset=synset.id, n=n, sense_key=None))
        wn.add_entry(entry)
        wn_synset.add_entry(entry)
    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)
    return entry

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
        wn_synset = parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
        wn_synset.entries = [entry for entry in wn_synset.entries if entry.id != entry_global.id]
        wn.entries = [entry for entry in wn.entries if entry.id != entry_global.id]
    else:
        wn_synset = parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
        entry = wn_synset.entry_by_id(entry_global.id)
        entry.senses = [sense for sense in entry.senses if sense.synset != synset.id]
        entry_global.senses = [sense for sense in entry_global.senses if sense.synset != synset.id]
    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)

def delete_synset(wn, synset, supersede, reason, delent=True):
    """Delete a synset"""
    print("Deleting synset %s" % synset.id)
    
    if delent:
        entries = empty_if_none(wn.members_by_id(synset.id))

        for entry in entries:
            delete_entry(wn, synset, 
                    "ewn-%s-%s" % (escape_lemma(entry), synset.part_of_speech.value))

    for rel in synset.synset_relations:
        delete_rel(wn.synset_by_id(rel.target), synset)

    wn_synset = parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    wn_synset.synsets = [ss for ss in wn_synset.synsets
            if synset.id != ss.id]
    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
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
    if new_n <= 0:
        return

    senses = [sense for sense in entry.senses if sense.id == sense_id]
    if len(senses) != 1:
        raise Exception("Could not find sense")
    sense = senses[0]
    synset = wn.synset_by_id(sense.synset)
    lexname = synset.lex_name

    wn_synset = parse_wordnet("src/xml/wn-%s.xml" % lexname)
    entry = wn_synset.entry_by_id(entry.id)
    sense = [sense for sense in entry.senses if sense.id == sense_id][0]
    sense.n = new_n
    with open("src/xml/wn-%s.xml" % lexname, "w") as out:
        wn_synset.to_xml(out, True)

def change_sense_idx(wn, sense_id, new_idx):
    """Change the position of a lemma within a synset"""
    print("Changing idx of sense %s to %s" % (sense_id, new_idx))
    new_sense_id = "%s-%02d" % (sense_id[:-3], new_idx)
    # This is implemented as a find and replace, as this is likely less error-prone
    # than doing it properly
    for f in glob("src/xml/wn-*.xml"):
        with fileinput.FileInput(f, inplace=True) as file:
            for line in file:
                print(line.replace(sense_id, new_sense_id).rstrip())

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
    wn2 = parse_wordnet("src/xml/wn-%s.xml" % lexfile)
    wn2.add_synset(ss)
    wn.add_synset(ss) # So downstream split/merge script work!
    with open("src/xml/wn-%s.xml" % lexfile, "w") as out:
        wn2.to_xml(out, True)
    return ssid

def merge_synset(wn, synsets, reason, lexfile, ssid=None):
    """Create a new synset merging all the facts from other synsets"""
    pos = synsets[0].part_of_speech.value
    if not ssid:
        ssid = new_id(wn, pos, synsets[0].definitions[0].text)
    ss = Synset(ssid, "in",
            PartOfSpeech(pos), lexfile)
    ss.definitions = [d for s in synsets for d in s.definitions]
    ss.examples = [x for s in synsets for x in s.examples]
    members = {}
    wn_ss = parse_wordnet("src/xml/wn-%s.xml" % lexfile)
    wn_ss.add_synset(ss)
    wn.add_synset(ss)
    with open("src/xml/wn-%s.xml" % lexfile, "w") as outp:
        wn_ss.to_xml(outp, True)

    for s in synsets:
        # Add all relations
        for r in s.synset_relations:
            if not any(r == r2 for r2 in ss.synset_relations):
                add_relation(wn_ss, ss, wn.synset_by_id(r.target), r.rel_type)
        # Add members
        for m in wn.members_by_id(s.id):
            if m not in members:
                members[m] = add_entry(wn_ss, ss, m)
                add_entry(wn, ss, m)
            e = [e for e in [wn.entry_by_id(e2) for e2 in wn.entry_by_lemma(m)]
                    if e.lemma.part_of_speech.value == pos][0]
            for f in e.forms:
                if not any(f2 == f for f in members[m].forms):
                    members[m].add_form(f)
            # syn behaviours - probably fix manually for the moment
    with open("src/xml/wn-%s.xml" % lexfile, "w") as outp:
        wn_ss.to_xml(outp, True)
    return ss


def find_type(source, target):
    """Get the first relation type between the synsets"""
    x = [r for r in source.synset_relations if r.target == target.id]
    if len(x) != 1:
        raise Exception("Synsets not linked or linked by more than one property")
    return x[0].rel_type

def update_source(wn, old_source, target, new_source):
    """Change the source of a link"""
    rel_type = find_type(old_source, target)
    delete_rel(old_source, target)
    insert_rel(new_source, rel_type, target)
    if rel_type in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[rel_type]
        delete_rel(target, old_source)
        insert_rel(target, inv_rel_type, new_source)

def update_target(wn, source, old_target, new_target):
    """Change the target of a link"""
    rel_type = find_type(source, old_target)
    delete_rel(source, old_target)
    insert_rel(source, rel_type, new_target)
    if rel_type in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[rel_type]
        delete_rel(old_target, source)
        insert_rel(new_target, inv_rel_type, source)

def update_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    delete_rel(source, target)
    insert_rel(source, new_rel, target)
    if new_rel in inverse_synset_rels:
        inv_rel_type = inverse_synset_rels[new_rel]
        delete_rel(target, source)
        insert_rel(target, inv_rel_type, source)

def add_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    insert_rel(source, new_rel, target)
    if new_rel in inverse_synset_rels:
        inv_rel_type = inverse_synset_rels[new_rel]
        insert_rel(target, inv_rel_type, source)

def delete_relation(wn, source, target):
    """Change the type of a link"""
    delete_rel(source, target)
    delete_rel(target, source)

def reverse_rel(wn, source, target):
    """Reverse the direction of relations"""
    rel_type = find_type(source, target)
    delete_rel(source, target)
    if rel_type in inverse_synset_rels:
        delete_rel(target, source)
    insert_rel(target, rel_type, source)
    if rel_type in inverse_synset_rels:
        inv_rel_type = inverse_synset_rels[rel_type]
        insert_rel(source, inv_rel_type, target)

def delete_sense_rel(wn, source, target):
    """Delete all relationships between two senses"""
    print("Delete %s =*=> %s" % (source, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = parse_wordnet("src/xml/wn-%s.xml" % lex_name)
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations = [r for r in sense.sense_relations if r.target != target]
    with open("src/xml/wn-%s.xml" % lex_name, "w") as out:
        wn_source.to_xml(out, True)

def insert_sense_rel(wn, source, rel_type, target):
    """Insert a single relation between two senses"""
    print("Insert %s =%s=> %s" % (source, rel_type, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = parse_wordnet("src/xml/wn-%s.xml" % lex_name)
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations.append(SenseRelation(target, rel_type))
    with open("src/xml/wn-%s.xml" % lex_name, "w") as out:
        wn_source.to_xml(out, True)

    
def find_sense_type(wn, source, target):
    """Get the first relation type between the senses"""
    (source_synset, source_entry) = decompose_sense_id(source)
    entry = wn.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    x = set([r for r in sense.sense_relations if r.target == target])
    if len(x) == 0:
        raise Exception("Synsets not linked or linked by more than one property")
    return next(iter(x)).rel_type
    

def update_source_sense(wn, old_source, target, new_source):
    """Change the source of a link"""
    rel_type = find_sense_type(wn, old_source, target)
    delete_sense_rel(wn, old_source, target)
    insert_sense_rel(wn, new_source, rel_type, target)
    if rel_type in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[rel_type]
        delete_sense_rel(wn, target, old_source)
        insert_sense_rel(wn, target, inv_rel_type, new_source)

def update_target_sense(wn, source, old_target, new_target):
    """Change the target of a link"""
    rel_type = find_sense_type(wn, source, old_target)
    delete_sense_rel(wn, source, old_target)
    insert_sense_rel(wn, source, rel_type, new_target)
    if rel_type in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[rel_type]
        delete_sense_rel(wn, old_target, source)
        insert_sense_rel(wn, new_target, inv_rel_type, source)

def update_sense_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    delete_sense_rel(wn, source, target)
    insert_sense_rel(wn, source, new_rel, target)
    if new_rel in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[new_rel]
        delete_sense_rel(wn, target, source)
        insert_sense_rel(wn, target, inv_rel_type, source)

def add_sense_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    insert_sense_rel(wn, source, new_rel, target)
    if new_rel in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[new_rel]
        insert_sense_rel(wn, target, inv_rel_type, source)

def delete_sense_relation(wn, source, target):
    """Change the type of a link"""
    delete_sense_rel(wn, source, target)
    delete_sense_rel(wn, target, source)

def reverse_sense_rel(wn, source, target):
    """Reverse the direction of a sense relation"""
    rel_type = find_sense_type(wn, source, target)
    delete_sense_rel(wn, source, target)
    if rel_type in inverse_sense_rels:
        delete_sense_rel(wn, target, source)
    insert_sense_rel(wn, target, rel_type, source)
    if rel_type in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[rel_type]
        insert_sense_rel(wn, source, inv_rel_type, target)

def sense_exists(wn, sense_id):
    if sense_id_re.match(sense_id):
        (_, entry_id) = decompose_sense_id(sense_id)
        entry = wn.entry_by_id(entry_id)
        if entry:
            senses = [sense for sense in entry.senses if sense.id == sense_id]
            return len(senses) == 1
    return False


