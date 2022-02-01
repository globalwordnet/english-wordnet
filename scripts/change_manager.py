"""Utility functions for changing the wordnet"""
from wordnet import *
import pickle
import os
from glob import glob
import fileinput
import hashlib
from merge import wn_merge
import wordnet_yaml
from collections import defaultdict
from sense_keys import get_sense_key
from pathlib import Path

sense_id_re = re.compile(r"oewn-(.*)-(.)-(\d{8})-\d{2}")


class ChangeList:
    def __init__(self):
        self.lexfiles = set()
        self.entry_files = set()

    def change_entry(self, wn, entry):
        for sense in entry.senses:
            synset = wn.synset_by_id(sense.synset)
            self.lexfiles.add(synset.lex_name)
        entry_key = entry.lemma.written_form[0].lower()
        if entry_key < 'a' or entry_key > 'z':
            entry_key = '0'
        self.entry_files.add(entry_key)

    def change_synset(self, synset):
        self.lexfiles.add(synset.lex_name)


def load_wordnet():
    """Load the wordnet from disk"""
    mode = None
    # Use whichever version is latest
    mtime_xml = max(os.path.getmtime(f) for f in glob("src/xml/*.xml"))
    mtime_yaml = max(os.path.getmtime(f) for f in glob("src/yaml/*.yaml"))
    if os.path.exists("wn.xml"):
        mtime_wn_xml = os.path.getmtime("wn.xml")
    else:
        mtime_wn_xml = 0
    if os.path.exists("wn.pickle"):
        mtime_pickle = os.path.getmtime("wn.pickle")
    else:
        mtime_pickle = 0
    if mtime_yaml > mtime_xml and mtime_yaml > mtime_wn_xml and mtime_yaml > mtime_pickle:
        print("Reading from YAML")
        wn = wordnet_yaml.load()
        pickle.dump(wn, open("wn.pickle", "wb"))
    elif mtime_xml > mtime_wn_xml and mtime_xml > mtime_pickle:
        print("Merging and reading XML")
        wn_merge()
        wn = parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    elif mtime_wn_xml > mtime_pickle:
        print("Reading XML")
        wn = parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))
    return wn


def save(wn, change_list=None):
    """Save the wordnet to disk (all formats)"""
    wordnet_yaml.save(wn, change_list)
    save_all_xml(wn, change_list)
    with codecs.open("wn.xml", "w", "utf-8") as outp:
        wn.to_xml(outp, True)
    pickle.dump(wn, open("wn.pickle", "wb"))


def save_all_xml(wn, change_list=None):
    by_lex_name = {}
    for synset in wn.synsets:
        if synset.lex_name not in by_lex_name:
            by_lex_name[synset.lex_name] = Lexicon(
                "oewn", "Open English WordNet", "en",
                "john@mccr.ae", "https://wordnet.princeton.edu/license-and-commercial-use",
                "2019", "https://github.com/globalwordnet/english-wordnet")
            by_lex_name[synset.lex_name].frames = wn.frames
        by_lex_name[synset.lex_name].add_synset(synset)

    for entry in wn.entries:
        sense_no = dict([(e.id, i) for i, e in enumerate(entry.senses)])
        for lex_name in by_lex_name.keys():
            senses = [
                sense for sense in entry.senses if wn.synset_by_id(
                    sense.synset).lex_name == lex_name]
            if senses:
                e = LexicalEntry(entry.id)
                e.set_lemma(entry.lemma)
                for f in entry.forms:
                    e.add_form(f)
                for s in senses:
                    s.n = sense_no[s.id]
                    e.add_sense(s)

                #def find_sense_for_sb(sb_sense):
                #    for sense2 in senses:
                #        if sense2.id == sb_sense:
                #            return sense2.id
                #    return None
                #e.syntactic_behaviours = [SyntacticBehaviour(
                #    sb.subcategorization_frame,
                #    [find_sense_for_sb(sense) for sense in sb.senses])
                #    for sb in entry.syntactic_behaviours]
                #e.syntactic_behaviours = [SyntacticBehaviour(
                #    sb.subcategorization_frame, [s for s in sb.senses if s])
                #    for sb in e.syntactic_behaviours if any(sb.senses)]
                e.pronunciation = entry.pronunciation
                by_lex_name[lex_name].add_entry(e)

    for lex_name, wn in by_lex_name.items():
        if os.path.exists(
                "src/xml/wn-%s.xml" %
                lex_name) and (
                not change_list or lex_name in change_list.lexfiles):
            wn_lex = parse_wordnet("src/xml/wn-%s.xml" % lex_name)
            wn.comments = wn_lex.comments
            entry_order = defaultdict(
                lambda: 10000000, [
                    (e, i) for i, e in enumerate(
                        entry.id for entry in wn_lex.entries)])
            wn.entries = sorted(wn.entries, key=lambda e: entry_order[e.id])
            for entry in wn.entries:
                if wn_lex.entry_by_id(entry.id):
                    sense_order = defaultdict(
                        lambda: 10000, [
                            (e, i) for i, e in enumerate(
                                sense.id for sense in wn_lex.entry_by_id(
                                    entry.id).senses)])
                    entry.senses = sorted(
                        entry.senses, key=lambda s: sense_order[s.id])
                    # This is a bit of a hack as some of the n values are not
                    # continguous
                    for sense in entry.senses:
                        if wn_lex.sense_by_id(sense.id):
                            sense.n = wn_lex.sense_by_id(sense.id).n
                            sense_rel_order = defaultdict(
                                lambda: 10000, [
                                    ((sr.target, sr.rel_type), i) for i, sr in enumerate(
                                        wn_lex.sense_by_id(
                                            sense.id).sense_relations)])
                            sense.sense_relations = sorted(
                                sense.sense_relations, key=lambda sr: sense_rel_order[(sr.target, sr.rel_type)])
                        else:
                            print("sense not found:" + sense.id)
                    #sb_order = defaultdict(
                    #    lambda: 10000, [
                    #        (e, i) for i, e in enumerate(
                    #            sb.subcategorization_frame for sb in wn_lex.entry_by_id(
                    #                entry.id).syntactic_behaviours)])
                    #entry.syntactic_behaviours = sorted(
                    #    entry.syntactic_behaviours, key=lambda sb: sb_order[sb.subcategorization_frame])
                    #for sb in entry.syntactic_behaviours:
                    #    sb2s = [sb2 for sb2 in wn_lex.entry_by_id(entry.id).syntactic_behaviours
                    #            if sb2.subcategorization_frame == sb.subcategorization_frame]
                    #    if sb2s:
                    #        sbe_order = defaultdict(
                    #            lambda: 10000, [
                    #                (e, i) for i, e in enumerate(
                    #                    sb2s[0].senses)])
                    #        sb.senses = sorted(
                    #            sb.senses, key=lambda s: sbe_order[s])
                else:
                    print("not found:" + entry.id)
            synset_order = defaultdict(
                lambda: 1000000, [
                    (e, i) for i, e in enumerate(
                        synset.id for synset in wn_lex.synsets)])
            wn.synsets = sorted(wn.synsets, key=lambda s: synset_order[s.id])
            for synset in wn.synsets:
                if wn_lex.synset_by_id(synset.id):
                    synset_rel_order = defaultdict(
                        lambda: 10000, [
                            ((sr.target, sr.rel_type), i) for i, sr in enumerate(
                                wn_lex.synset_by_id(
                                    synset.id).synset_relations)])
                    synset.synset_relations = sorted(
                        synset.synset_relations, key=lambda sr: synset_rel_order[(sr.target, sr.rel_type)])
        if not change_list or lex_name in change_list.lexfiles:
            Path("src/xml").mkdir(parents=True, exist_ok=True)
            with codecs.open("src/xml/wn-%s.xml" % lex_name, "w", "utf-8") as outp:
                wn.to_xml(outp, True)


def delete_rel(source, target, change_list=None):
    """Delete all relationships between two synsets"""
    print("Delete %s =*=> %s" % (source.id, target.id))
    ss = source
    source.synset_relations = [
        r for r in ss.synset_relations if r.target != target.id]
    if change_list:
        change_list.change_synset(source)


def decompose_sense_id(sense_id):
    m = sense_id_re.match(sense_id)
    if m:
        lemma = m.group(1)
        pos = m.group(2)
        ssid = m.group(3)
        return ("oewn-%s-%s" % (ssid, pos), "oewn-%s-%s" % (lemma, pos))
    else:
        raise Exception("Not a sense ID")


def delete_sense_rel(wn, source, target, change_list=None):
    """Delete all relationships between two senses"""
    print("Delete %s =*=> %s" % (source, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    entry = wn.entry_by_id(source_entry)
    if change_list:
        change_list.change_entry(wn, entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations = [
        r for r in sense.sense_relations if r.target != target]


def insert_rel(source, rel_type, target, change_list=None):
    """Insert a single relation between two synsets"""
    print("Insert %s =%s=> %s" % (source.id, rel_type, target.id))
    ss = source
    if [r for r in ss.synset_relations if r.target ==
            target.id and r.rel_type == rel_type]:
        print("Already exists")
        return
    ss.synset_relations.append(SynsetRelation(target.id, rel_type))
    if change_list:
        change_list.change_synset(target)


def empty_if_none(x):
    """Returns an empty list if passed None otherwise the argument"""
    if x:
        return x
    else:
        return []

KEY_PREFIX_LEN = 5

def synset_key(synset_id):
    return synset_id[KEY_PREFIX_LEN:-2]


def change_entry(wn, synset, target_synset, lemma, change_list=None):
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

    wn_synset = wn
    entries = [entry for entry in empty_if_none(wn_synset.entry_by_lemma(
        lemma)) if wn.entry_by_id(entry).lemma.part_of_speech == synset.part_of_speech]

    for entry in entries:
        for sense in wn_synset.entry_by_id(entry).senses:
            if sense.synset == synset.id:
                print("Moving %s to %s" % (sense.id, target_synset.id))
                sense.synset = target_synset.id
                wn.change_sense_id(
                    sense,
                    "oewn-%s-%s-%s-%02d" %
                    (escape_lemma(lemma),
                     target_synset.part_of_speech.value,
                     synset_key(
                        target_synset.id),
                        idx),
                    change_list)
    if change_list:
        change_list.change_entry(wn, entry)


def add_entry(wn, synset, lemma, idx=0, n=-1, change_list=None):
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

    wn_synset = wn
    entries = [entry for entry in empty_if_none(wn_synset.entry_by_lemma(
        lemma)) if wn.entry_by_id(entry).lemma.part_of_speech == synset.part_of_speech]

    if entries:
        if len(entries) != 1:
            raise Exception("More than one entry for part of speech")
        print("Found an entry!")
        wn_entry = wn.entry_by_id(entries[0])
        entry = wn_synset.entry_by_id(entries[0])
        sense = Sense(
            id="oewn-%s-%s-%s-%02d" %
            (escape_lemma(lemma),
             synset.part_of_speech.value,
             synset_key(
                synset.id),
                idx),
            synset=synset.id,
            n=n,
            sense_key=None)

        wn_entry.senses.append(sense)
        entry.senses.append(sense)
        sense.sense_key = get_sense_key(wn, entry, sense, synset.lex_name)
        if sense.synset not in wn.members:
            wn.members[sense.synset] = []
        wn.members[sense.synset].append(wn_entry.lemma.written_form)
    else:
        n = 0
        print("Creating new entry")
        entry = LexicalEntry(
            "oewn-%s-%s" % (escape_lemma(lemma), synset.part_of_speech.value))
        entry.set_lemma(Lemma(lemma, synset.part_of_speech))
        sense = Sense(
                id="oewn-%s-%s-%s-%02d" %
                (escape_lemma(lemma),
                 synset.part_of_speech.value,
                 synset_key(
                    synset.id),
                    idx),
                synset=synset.id,
                n=n,
                sense_key=None)
        entry.add_sense(sense)
        sense.sense_key = get_sense_key(wn, entry, sense, synset.lex_name)
        wn.add_entry(entry)
    if change_list:
        change_list.change_entry(wn, entry)
    return entry


def delete_entry(wn, synset, entry_id, change_list=None):
    """Delete a lemma from a synset"""
    print("Deleting %s from synset %s" % (entry_id, synset.id))
    n_entries = len(wn.members_by_id(synset.id))
    entry_global = wn.entry_by_id(entry_id)

    if entry_global:
        idxs = [int(sense.id[-2:])
                for sense in entry_global.senses if sense.synset == synset.id]
        if not idxs:
            print("Entry not in synset")
            return
        idx = idxs[0]
        n_senses = len(entry_global.senses)
    else:
        print("No entry for this lemma")
        return
    
    if n_senses == 0:
        entry = wn_synset.entry_by_id(entry_global.id)
        if entry:
            wn.del_entry(entry)
        return

    if n_senses != 1:
        n = [ind for ind, sense in enumerate(
            entry_global.senses) if sense.synset == synset.id][0]
        sense_n = 0
        for sense in entry_global.senses:
            if sense_n >= n:
                change_sense_n(wn, entry_global, sense.id, sense_n - 1)
            sense_n += 1

    for sense_id in sense_ids_for_synset(wn, synset):
        this_idx = int(sense_id[-2:])
        if this_idx > idx:
            change_sense_idx(wn, sense_id, this_idx - 1)

    for sense in entry_global.senses:
        if sense.synset == synset.id:
            for rel in sense.sense_relations:
                delete_sense_rel(wn, rel.target, sense.id, change_list)
                delete_sense_rel(wn, sense.id, rel.target, change_list)

    if n_senses == 1:  # then delete the whole entry
        wn_synset = wn
        entry = wn_synset.entry_by_id(entry_global.id)
        if change_list:
            change_list.change_entry(wn, entry)
        wn_synset.del_entry(entry)
        wn.del_entry(entry)
    else:
        wn_synset = wn
        entry = wn_synset.entry_by_id(entry_global.id)
        if change_list:
            change_list.change_entry(wn, entry)
        sense = [s for s in entry.senses if s.synset == synset.id]
        if sense:
            sense = sense[0]
            wn_synset.del_sense(entry, sense)
            wn.del_sense(entry, sense)
        else:
            print("this may be a bug")


def delete_synset(
        wn,
        synset,
        supersede,
        reason,
        delent=True,
        change_list=None):
    """Delete a synset"""
    print("Deleting synset %s" % synset.id)

    if delent:
        entries = empty_if_none(wn.members_by_id(synset.id))

        for entry in entries:
            delete_entry(
                wn, synset, "oewn-%s-%s" %
                (escape_lemma(entry), synset.part_of_speech.value), change_list)

    for rel in synset.synset_relations:
        delete_rel(wn.synset_by_id(rel.target), synset, change_list)

    wn_synset = wn
    wn_synset.synsets = [ss for ss in wn_synset.synsets
                         if synset.id != ss.id]
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
                   reason.replace("\n", "").replace("\"", "\"\"")))
    if change_list:
        change_list.change_synset(synset)


def change_sense_n(wn, entry, sense_id, new_n, change_list=None):
    """Change the position of a sense within an entry (changes only this sense)"""
    print("Changing n of sense %s of %s to %s" %
          (sense_id, entry.lemma.written_form, new_n))
    if new_n <= 0:
        return

    senses = [sense for sense in entry.senses if sense.id == sense_id]
    if len(senses) != 1:
        raise Exception("Could not find sense")
    sense = senses[0]
    synset = wn.synset_by_id(sense.synset)
    lexname = synset.lex_name

    wn_synset = wn
    entry = wn_synset.entry_by_id(entry.id)
    sense = [sense for sense in entry.senses if sense.id == sense_id][0]
    sense.n = new_n
    if change_list:
        change_list.change_entry(wn, entry)


def change_sense_idx(wn, sense_id, new_idx, change_list=None):
    """Change the position of a lemma within a synset"""
    print("Changing idx of sense %s to %s" % (sense_id, new_idx))
    new_sense_id = "%s-%02d" % (sense_id[:-3], new_idx)
    for entry in wn.entries:
        for sense in entry.senses:
            if sense.id == sense_id:
                wn.change_sense_id(sense, new_sense_id)
            for sr in sense.sense_relations:
                if sr.target == sense_id:
                    sr.target = new_sense_id
        for sb in entry.syntactic_behaviours:
            sb.senses = [
                new_sense_id if s == sense_id else s
                for s in sb.senses]
        if change_list:
            change_list.change_entry(wn, entry)


def sense_ids_for_synset(wn, synset):
    return [sense.id for lemma in wn.members_by_id(synset.id)
            for entry in wn.entry_by_lemma(lemma)
            for sense in wn.entry_by_id(entry).senses
            if sense.synset == synset.id]


def new_id(wn, pos, definition):
    s = hashlib.sha256()
    s.update(definition.encode())
    nid = "oewn-8%07d-%s" % ((int(s.hexdigest(), 16) % 10000000), pos)
    if wn.synset_by_id(nid):
        print(
            "Could not find ID for new synset. Either a duplicate definition or a hash collision for " +
            nid +
            ". Note it is possible to force a synset ID by giving it as an argument")
        sys.exit(-1)
    return nid


def add_synset(wn, definition, lexfile, pos, ssid=None, change_list=None):
    if not ssid:
        ssid = new_id(wn, pos, definition)
    ss = Synset(ssid, "in",
                PartOfSpeech(pos), lexfile)
    ss.definitions = [Definition(definition)] 
    ss.ili_definition = Definition(definition)
    wn.add_synset(ss)
    if change_list:
        change_list.change_synset(ss)
    return ssid


def merge_synset(wn, synsets, reason, lexfile, ssid=None, change_list=None):
    """Create a new synset merging all the facts from other synsets"""
    pos = synsets[0].part_of_speech.value
    if not ssid:
        ssid = new_id(wn, pos, synsets[0].definitions[0].text)
    ss = Synset(ssid, "in",
                PartOfSpeech(pos), lexfile)
    ss.definitions = [d for s in synsets for d in s.definitions]
    ss.examples = [x for s in synsets for x in s.examples]
    members = {}
    wn.add_synset(ss)

    for s in synsets:
        # Add all relations
        for r in s.synset_relations:
            if not any(r == r2 for r2 in ss.synset_relations):
                add_relation(
                    wn, ss, wn.synset_by_id(
                        r.target), r.rel_type, change_list)
        # Add members
        for m in wn.members_by_id(s.id):
            if m not in members:
                members[m] = add_entry(wn, ss, m, change_list)
                add_entry(wn, ss, m, change_list)
            e = [e for e in [wn.entry_by_id(e2) for e2 in wn.entry_by_lemma(m)]
                 if e.lemma.part_of_speech.value == pos][0]
            for f in e.forms:
                if not any(f2 == f for f in members[m].forms):
                    members[m].add_form(f)
            # syn behaviours - probably fix manually for the moment
    if change_list:
        change_list.change_synset(ss)
    return ss


def find_type(source, target):
    """Get the first relation type between the synsets"""
    x = [r for r in source.synset_relations if r.target == target.id]
    if len(x) != 1:
        raise Exception(
            "Synsets not linked or linked by more than one property")
    return x[0].rel_type


def update_source(wn, old_source, target, new_source, change_list=None):
    """Change the source of a link"""
    rel_type = find_type(old_source, target)
    delete_rel(old_source, target, change_list)
    insert_rel(new_source, rel_type, target, change_list)
    if rel_type in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[rel_type]
        delete_rel(target, old_source, change_list)
        insert_rel(target, inv_rel_type, new_source, change_list)


def update_target(wn, source, old_target, new_target, change_list=None):
    """Change the target of a link"""
    rel_type = find_type(source, old_target)
    delete_rel(source, old_target, change_list)
    insert_rel(source, rel_type, new_target, change_list)
    if rel_type in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[rel_type]
        delete_rel(old_target, source, change_list)
        insert_rel(new_target, inv_rel_type, source, change_list)


def update_relation(wn, source, target, new_rel, change_list=None):
    """Change the type of a link"""
    delete_rel(source, target, change_list)
    insert_rel(source, new_rel, target, change_list)
    if new_rel in inverse_synset_rels:
        inv_rel_type = inverse_synset_rels[new_rel]
        delete_rel(target, source, change_list)
        insert_rel(target, inv_rel_type, source, change_list)


def add_relation(wn, source, target, new_rel, change_list=None):
    """Change the type of a link"""
    insert_rel(source, new_rel, target, change_list)
    if new_rel in inverse_synset_rels:
        inv_rel_type = inverse_synset_rels[new_rel]
        insert_rel(target, inv_rel_type, source, change_list)


def delete_relation(wn, source, target, change_list=None):
    """Change the type of a link"""
    delete_rel(source, target, change_list)
    delete_rel(target, source, change_list)


def reverse_rel(wn, source, target, change_list=None):
    """Reverse the direction of relations"""
    rel_type = find_type(source, target)
    delete_rel(source, target, change_list)
    if rel_type in inverse_synset_rels:
        delete_rel(target, source, change_list)
    insert_rel(target, rel_type, source, change_list)
    if rel_type in inverse_synset_rels:
        inv_rel_type = inverse_synset_rels[rel_type]
        insert_rel(source, inv_rel_type, target, change_list)


def delete_sense_rel(wn, source, target, change_list=None):
    """Delete all relationships between two senses"""
    print("Delete %s =*=> %s" % (source, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = wn
    entry = wn_source.entry_by_id(source_entry)
    if entry:
        sense = [sense for sense in entry.senses if sense.id == source][0]
        if not any(r for r in sense.sense_relations if r.target == target):
            print("No sense relations deleted")
        else:
            sense.sense_relations = [
                r for r in sense.sense_relations if r.target != target]
            if change_list:
                change_list.change_entry(wn, entry)
    else:
        print("No entry for " + source_entry)


def insert_sense_rel(wn, source, rel_type, target, change_list=None):
    """Insert a single relation between two senses"""
    print("Insert %s =%s=> %s" % (source, rel_type, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = wn
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations.append(SenseRelation(target, rel_type))
    if change_list:
        change_list.change_entry(wn, entry)


def find_sense_type(wn, source, target):
    """Get the first relation type between the senses"""
    (source_synset, source_entry) = decompose_sense_id(source)
    entry = wn.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    x = set([r for r in sense.sense_relations if r.target == target])
    if len(x) == 0:
        raise Exception(
            "Synsets not linked or linked by more than one property")
    return next(iter(x)).rel_type


def update_source_sense(wn, old_source, target, new_source, change_list=None):
    """Change the source of a link"""
    rel_type = find_sense_type(wn, old_source, target)
    delete_sense_rel(wn, old_source, target, change_list)
    insert_sense_rel(wn, new_source, rel_type, target, change_list)
    if rel_type in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[rel_type]
        delete_sense_rel(wn, target, old_source, change_list)
        insert_sense_rel(wn, target, inv_rel_type, new_source, change_list)


def update_target_sense(wn, source, old_target, new_target, change_list=None):
    """Change the target of a link"""
    rel_type = find_sense_type(wn, source, old_target)
    delete_sense_rel(wn, source, old_target, change_list)
    insert_sense_rel(wn, source, rel_type, new_target, change_list)
    if rel_type in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[rel_type]
        delete_sense_rel(wn, old_target, source, change_list)
        insert_sense_rel(wn, new_target, inv_rel_type, source, change_list)


def update_sense_relation(wn, source, target, new_rel, change_list=None):
    """Change the type of a link"""
    delete_sense_rel(wn, source, target, change_list)
    insert_sense_rel(wn, source, new_rel, target, change_list)
    if new_rel in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[new_rel]
        delete_sense_rel(wn, target, source, change_list)
        insert_sense_rel(wn, target, inv_rel_type, source, change_list)


def add_sense_relation(wn, source, target, new_rel, change_list=None):
    """Change the type of a link"""
    insert_sense_rel(wn, source, new_rel, target, change_list)
    if new_rel in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[new_rel]
        insert_sense_rel(wn, target, inv_rel_type, source, change_list)


def delete_sense_relation(wn, source, target, change_list=None):
    """Change the type of a link"""
    delete_sense_rel(wn, source, target, change_list)
    delete_sense_rel(wn, target, source, change_list)


def reverse_sense_rel(wn, source, target, change_list=None):
    """Reverse the direction of a sense relation"""
    rel_type = find_sense_type(wn, source, target)
    delete_sense_rel(wn, source, target, change_list)
    if rel_type in inverse_sense_rels:
        delete_sense_rel(wn, target, source, change_list)
    insert_sense_rel(wn, target, rel_type, source, change_list)
    if rel_type in inverse_sense_rels:
        inv_rel_type = inverse_sense_rels[rel_type]
        insert_sense_rel(wn, source, inv_rel_type, target, change_list)


def sense_exists(wn, sense_id):
    if sense_id_re.match(sense_id):
        (_, entry_id) = decompose_sense_id(sense_id)
        entry = wn.entry_by_id(entry_id)
        if entry:
            senses = [sense for sense in entry.senses if sense.id == sense_id]
            return len(senses) == 1
    return False


def update_def(wn, synset, defn, add, change_list=None):
    wn_synset = wn
    ss = wn_synset.synset_by_id(synset.id)
    if add:
        ss.definitions = ss.definitions + [Definition(defn)]
    else:
        ss.definitions = [Definition(defn)]
    if change_list:
        change_list.change_synset(synset)


def update_ili_def(wn, synset, defn, change_list=None):
    wn_synset = wn
    ss = wn_synset.synset_by_id(synset.id)
    ss.ili_definition = Definition(defn)
    if change_list:
        change_list.change_synset(synset)


def add_ex(wn, synset, example, change_list=None):
    wn_synset = wn
    ss = wn_synset.synset_by_id(synset.id)
    ss.examples = ss.examples + [Example(example)]
    if change_list:
        change_list.change_synset(synset)


def delete_ex(wn, synset, example, change_list=None):
    wn_synset = wn
    ss = wn_synset.synset_by_id(synset.id)
    n_exs = len(ss.examples)
    ss.examples = [ex for ex in ss.examples if ex.text != example]
    if len(ss.examples) == n_exs:
        print("No change")
    if change_list:
        change_list.change_synset(synset)
