from wordnet import (parse_wordnet, SynsetRelType, PartOfSpeech, SenseRelType,
                     Synset, inverse_synset_rels, inverse_sense_rels, equal_pos)
import re
import sys
import glob
import sense_keys
from sense_keys import unmap_sense_key
from wordnet import xml_id_char
from collections import Counter
from from_yaml import load

def check_symmetry(wn, fix):
    errors = []
    for synset in wn.synsets:
        for rel in synset.synset_relations:
            if rel.rel_type in inverse_synset_rels:
                synset2 = wn.synset_by_id(rel.target)
                if not synset2:
                    # This error only happens if the XML validation is not
                    # being carried out!
                    print(
                        "Referencing bad synset ID %s from %s" %
                        (rel.target, synset.id))
                else:
                    if not any(r for r in synset2.synset_relations if r.target ==
                               synset.id and r.rel_type == inverse_synset_rels[rel.rel_type]):
                        if fix:
                            errors.append("python3 scripts/change-relation.py --add --new-relation %s %s %s" % (
                                inverse_synset_rels[rel.rel_type].value, synset2.id, synset.id))
                        else:
                            errors.append(
                                "No symmetric relation for %s =%s=> %s" %
                                (synset.id, rel.rel_type, synset2.id))
    for entry in wn.entries:
        for sense in entry.senses:
            for rel in sense.sense_relations:
                if rel.rel_type in inverse_sense_rels:
                    sense2 = wn.sense_by_id(rel.target)
                    if not sense2:
                        errors.append(
                                "Reference to no existant sense %s)" % (rel.target))
                        continue
                    if not any(r for r in sense2.sense_relations if r.target ==
                               sense.id and r.rel_type == inverse_sense_rels[rel.rel_type]):
                        if fix:
                            errors.append("python3 scripts/change-relation.py --add --new-relation %s %s %s" % (
                                inverse_sense_rels[rel.rel_type].value, sense2.id, sense.id))
                        else:
                            errors.append(
                                "No symmetric relation for %s =%s=> %s" %
                                (sense.id, rel.rel_type, sense2.id))

    return errors


def check_transitive(wn, fix):
    errors = []
    for synset in wn.synsets:
        for rel in synset.synset_relations:
            if rel.rel_type == SynsetRelType.HYPERNYM:
                synset2 = wn.synset_by_id(rel.target)
                for rel2 in synset2.synset_relations:
                    if (any(r for r in synset.synset_relations if r.target ==
                           rel2.target and r.rel_type == SynsetRelType.HYPERNYM) and
                           rel2.rel_type == SynsetRelType.HYPERNYM):
                        if fix:
                            errors.append(
                                "python scripts/change-relation.py --delete %s %s" %
                                (synset.id, rel2.target))
                        else:
                            errors.append(
                                "Transitive error for %s => %s => %s" %
                                (synset.id, synset2.id, rel2.target))
    return errors

def check_no_loops(wn):
    hypernyms = {}
    for synset in wn.synsets:
        hypernyms[synset.id] = set()
        for rel in synset.synset_relations:
            if rel.rel_type == SynsetRelType.HYPERNYM:
                hypernyms[synset.id].add(rel.target)
    changed = True
    while changed:
        changed = False
        for synset in wn.synsets:
            n_size = len(hypernyms[synset.id])
            for c in hypernyms[synset.id]:
                hypernyms[synset.id] = hypernyms[synset.id].union(
                    hypernyms.get(c, []))
                if synset.id in hypernyms[synset.id]:
                    return ["Loop for %s <-> %s" % (synset.id, c)]
            if len(hypernyms[synset.id]) != n_size:
                changed = True
    return []

def check_no_domain_loops(wn):
    domains = {}
    for synset in wn.synsets:
        domains[synset.id] = set()
        for rel in synset.synset_relations:
            if (rel.rel_type == SynsetRelType.DOMAIN_TOPIC or
                rel.rel_type == SynsetRelType.DOMAIN_REGION or
                rel.rel_type == SynsetRelType.EXEMPLIFIES):
                domains[synset.id].add(rel.target)
    changed = True
    while changed:
        changed = False
        for synset in wn.synsets:
            n_size = len(domains[synset.id])
            for c in domains[synset.id]:
                domains[synset.id] = domains[synset.id].union(
                    domains.get(c, []))
            if len(domains[synset.id]) != n_size:
                changed = True
            if synset.id in domains[synset.id]:
                return ["Domain loop for %s" % (synset.id)]
    return []

def check_not_empty(wn, ss):
    if not wn.members_by_id(ss.id):
        return False
    else:
        return True


def check_ili(ss, fix):
    errors = 0
    if (not ss.ili or ss.ili == "in") and not ss.ili_definition:
        if fix:
            print("python3 scripts/change-definition.py --ili %s" % ss.id)
        else:
            print("%s does not have an ILI definition" % ss.id)
        errors += 1
    return errors


def check_lex_files(wn, fix):
    pos_map = {
        "nou": PartOfSpeech.NOUN,
        "ver": PartOfSpeech.VERB,
        "adj": PartOfSpeech.ADJECTIVE,
        "adv": PartOfSpeech.ADVERB
    }
    errors = 0
    for entry in wn.entries:
        for sense in entry.senses:
            if not sense.id:
                print("%s does not have a sense key" % (sense.id))
                errors += 1
            if not wn.synset_by_id(sense.synset):
                print("%s refers to nonexistent synset %s" %
                      (sense.id, sense.synset))
                errors += 1
                continue
            calc_sense_key = sense_keys.get_sense_key(
                wn, entry, sense)
            sense_key = unmap_sense_key(sense.id)
            if sense_key != calc_sense_key:
                if fix:
                    print(
                        "sed -i 's/%s/%s/' src/xml/*" %
                        (sense_key, calc_sense_key))
                else:
                    print(
                        "%s has declared key %s but should be %s" %
                        (sense.id, sense_key, calc_sense_key))
                errors += 1

    return errors


valid_id = re.compile(fr"^oewn-{xml_id_char}*$")

valid_sense_id = re.compile(
    "^oewn-[A-Za-z0-9_\\-.]+-([nvars])-([0-9]{8})-[0-9]{2}$")

valid_synset_id = re.compile("^oewn-[0-9]{8}-[nvars]$")


def is_valid_id(xml_id):
    return bool(valid_id.match(xml_id))


def is_valid_synset_id(xml_id):
    return bool(valid_synset_id.match(xml_id))


def is_valid_sense_id(xml_id, synset):
    m = valid_sense_id.match(xml_id)
    if not m:
        return False
    else:
        pos = m.group(1)
        key = m.group(2)
        if synset != ("oewn-%s-%s" % (key, pos)):
            print("%s does not match target of %s" % (xml_id, synset))
            return False
        return True


def main():
    #wn = parse_wordnet("wn.xml")
    wn = load()

    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fix = True
    else:
        fix = False

    errors = 0

    errors += check_lex_files(wn, fix)

    sense_keys = {}

    for entry in wn.entries:
        if (entry.id[-1:] != entry.lemma.part_of_speech.value and not entry.id[-1].isnumeric()
            or entry.id[-1].isnumeric() and entry.id[-3:-2] != entry.lemma.part_of_speech.value):
            print("ERROR: Entry ID not same as part of speech %s as %s" %
                  (entry.id, entry.lemma.part_of_speech.value))
            errors += 1
        if not is_valid_id(entry.id):
            if fix:
                sys.stderr.write("Cannot be fixed")
                sys.exit(-1)
            print("ERROR: Invalid ID " + entry.id)
            errors += 1
        for sense in entry.senses:
            synset = wn.synset_by_id(sense.synset)
            if not synset:
                print(
                    "ERROR: Entry %s refers to nonexistent synset %s" %
                    (entry.id, sense.synset))
                errors += 1
            if (synset and entry.lemma.part_of_speech != synset.part_of_speech
                    and not (entry.lemma.part_of_speech == PartOfSpeech.ADJECTIVE and
                        synset.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE)):
                print(
                    "ERROR: Part of speech of entry not the same as synset %s in %s" %
                    (entry.id, synset.id))
                errors += 1
            for sr in sense.sense_relations:
                if sr.rel_type == SenseRelType.PERTAINYM:
                    ss_source = wn.synset_by_id(sense.synset)
                    if ((not equal_pos(ss_source.part_of_speech, PartOfSpeech.ADJECTIVE)
                         and not equal_pos(ss_source.part_of_speech, PartOfSpeech.ADVERB))):
                        print(
                            "ERROR: Pertainyms should be between adjectives %s => %s" %
                            (sense.id, sr.target))
                        errors += 1
            sr_counter = Counter((sr.target, sr.other_type if sr.other_type else sr.rel_type)
                                 for sr in sense.sense_relations)
            for item, count in sr_counter.items():
                if count > 1:
                    print(
                        "ERROR: Duplicate relation %s =%s=> %s" %
                        (sense.id, item[1], item[0]))
                    errors += 1
                # if sr.target == sense.id:
                #    print("ERROR: Reflexive sense relation %s" % (sense.id))
                #    errors += 1
            if unmap_sense_key(sense.id) in sense_keys:
                print("ERROR: Duplicate sense key %s" % sense.id)
                errors += 1
            else:
                sense_keys[sense.id] = sense.synset
            sb_counter = Counter(sense.subcat)
            for item, count in sb_counter.items():
                if count > 1:
                    print(
                        "ERROR: Duplicate syntactic behaviour in entry %s" %
                        (entry.id))
                    errors += 1
            for sense2 in entry.senses:
                if sense2.id != sense.id and sense2.synset == sense.synset:
                    print("ERROR: Duplicate senses %s/%s referring to %s" % (
                        sense.id, sense2.id, sense.synset))
                    errors += 1

    instances = set()
    ilis = set()
    wikidatas = set()
    definitions = set()

    for synset in wn.synsets:
        if synset.id[-1:] != synset.part_of_speech.value:
            print(
                "ERROR: Synset ID not same as part of speech %s as %s" %
                (synset.id, synset.part_of_speech.value))
            errors += 1
        if not is_valid_synset_id(synset.id):
            if fix:
                sys.stderr.write("Cannot be fixed")
                sys.exit(-1)
            print("ERROR: Invalid ID " + synset.id)
            errors += 1
        if not check_not_empty(wn, synset):
            print("ERROR: Empty synset " + synset.id)
            errors += 1

        errors += check_ili(synset, fix)

        similars = 0
        for sr in synset.synset_relations:
            if (sr.rel_type == SynsetRelType.HYPERNYM and not equal_pos(
                    synset.part_of_speech, wn.synset_by_id(sr.target).part_of_speech)):
                print(
                    "ERROR: Cross-part-of-speech hypernym %s => %s" %
                    (synset.id, sr.target))
                errors += 1
            if sr.rel_type == SynsetRelType.SIMILAR:
                if (not equal_pos(synset.part_of_speech, PartOfSpeech.VERB) and
                        not equal_pos(synset.part_of_speech, PartOfSpeech.ADJECTIVE)):
                    print(
                        "ERROR: similar not between verb/adjective %s => %s" %
                        (synset.id, sr.target))
                    errors += 1
                similars += 1
                if similars > 1 and synset.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE:
                    print(
                        "ERROR: satellite of more than one synset %s" %
                        (synset.id))
                    errors += 1
            if sr.rel_type == SynsetRelType.ANTONYM:
                print(
                    "ERROR: antonymy should be at the sense level %s => %s" %
                    (synset.id, sr.target))
                errors += 1
            # if sense.id == sr.target:
            #    print("ERROR: reflexive synset relation for %s" % (synset.id))
            #    errors += 1

        # Duplicate relation check
        sr2 = sorted(synset.synset_relations, key=lambda sr: (sr.target, sr.rel_type.value))
        for i in range(len(sr2)-1):
            if sr2[i].target == sr2[i+1].target and sr2[i].rel_type == sr2[i+1].rel_type:
                print("ERROR: Duplicate synset relation %s =%s=> %s" %
                        (synset.id, sr2[i].rel_type.value, sr2[i].target))
                errors += 1

        if synset.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE and similars == 0:
            print(
                "ERROR: satellite must have at least one similar link %s" %
                (synset.id))
            errors += 1

        if (synset.part_of_speech == PartOfSpeech.NOUN and not
            [sr for sr in synset.synset_relations 
                if sr.rel_type == SynsetRelType.HYPERNYM or
                   sr.rel_type == SynsetRelType.INSTANCE_HYPERNYM] and
            synset.id != "oewn-00001740-n"):
            print("ERROR: noun synset %s has no hypernym" % synset.id)
            errors += 1

        if any(sr.rel_type == SynsetRelType.INSTANCE_HYPERNYM 
               for sr in synset.synset_relations):
            if any(sr.rel_type == SynsetRelType.HYPERNYM
                   for sr in synset.synset_relations):
                print("Error: synset %s has both hypernym and instance hypernym"
                      % synset.id)
                errors += 1
            instances.add(synset.id)

        if len(synset.definitions) == 0:
            print("ERROR: synset without definition %s" % (synset.id))
            errors += 1
        for defn in synset.definitions:
            if len(defn.text) == 0:
                print("ERROR: empty definition for %s" % (synset.id))
                errors += 1
            if defn.text in definitions:
                print("ERROR: duplicate definition for %s (%s)" % (synset.id, defn.text))
                errors += 1
            else:
                definitions.add(defn.text)

        sr_counter = Counter((sr.target, sr.rel_type)
                             for sr in synset.synset_relations)
        for item, count in sr_counter.items():
            if count > 1:
                print(
                    "ERROR: Duplicate relation %s =%s=> %s" %
                    (synset.id, item[1], item[0]))
                errors += 1

        if synset.ili != "in" and synset.ili in ilis:
            print(f"ERROR: ILI {synset.ili} is duplicated")
            errors += 1
        else:
            ilis.add(synset.ili)

        if synset.wikidata and synset.wikidata in wikidatas:
            print(f"ERROR: QID {synset.wikidata} is duplicated")
            errors += 1
        else:
            wikidatas.add(synset.wikidata)

    for synset in wn.synsets:
        for sr in synset.synset_relations:
            if sr.rel_type == SynsetRelType.HYPERNYM:
                if sr.target in instances:
                    print(
                        "ERROR: Hypernym targets instance %s => %s" %
                        (synset.id, sr.target))
                    errors += 1

    for error in check_symmetry(wn, fix):
        if fix:
            print(error)
        else:
            print("ERROR: " + error)
            errors += 1

    for error in check_transitive(wn, fix):
        if fix:
            print(error)
        else:
            print("ERROR: " + error)
            errors += 1

    for error in check_no_loops(wn):
        if fix:
            sys.stderr.write("Cannot be fixed")
            sys.exit(-1)
        else:
            print("ERROR: " + error)
            errors += 1

    for error in check_no_domain_loops(wn):
        if fix:
            sys.stderr.write("Cannot be fixed")
            sys.exit(-1)
        else:
            print("ERROR: " + error)
            errors += 1

 
    if fix:
        pass
    elif errors > 0:
        print("Validation failed. %d errors" % errors)
        sys.exit(-1)
    else:
        print("No validity issues")


if __name__ == "__main__":
    main()
