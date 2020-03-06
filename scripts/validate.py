from wordnet import *
import re
import sys

def check_symmetry(wn, fix):
    errors = []
    for synset in wn.synsets:
        for rel in synset.synset_relations:
            if rel.rel_type in inverse_synset_rels:
                synset2 = wn.synset_by_id(rel.target)
                if not any(r for r in synset2.synset_relations if r.target == synset.id and r.rel_type == inverse_synset_rels[rel.rel_type]):
                    if fix:
                        errors.append("python scripts/change-relations.py --add --new-relation %s %s %s" % (inverse_synset_rels[rel.rel_type].value, synset2.id, synset.id))
                    else:
                        errors.append("No symmetric relation for %s =%s=> %s" % (synset.id, rel.rel_type, synset2.id))
    return errors

def check_transitive(wn, fix):
    errors = []
    for synset in wn.synsets:
        for rel in synset.synset_relations:
            if rel.rel_type == SynsetRelType.HYPERNYM:
                synset2 = wn.synset_by_id(rel.target)
                for rel2 in synset2.synset_relations:
                    if any(r for r in synset.synset_relations if r.target == rel2.target and r.rel_type == SynsetRelType.HYPERNYM):
                        if fix:
                            errors.append("python scripts/change-relation.py --delete %s %s" % (synset.id, rel2.target))
                        else:
                            errors.append("Transitive error for %s => %s => %s" %(synset.id, synset2.id, rel2.target))
    return errors

def check_no_loops(wn):
    errors = []
    chains = []
    for synset in wn.synsets:
        c2 = []
        i = 0
        while i < len(chains):
            if chains[i][-1] == synset.id:
                c2.append(chains.pop(i))
            else:
                i += 1
        for rel in synset.synset_relations:
            if rel.rel_type == SynsetRelType.HYPERNYM:
                for c in c2:
                    c3 = c.copy()
                    if any(y for y in c3 if y == rel.target):
                        errors.append("Loop in chain %s => %s " % (c3, rel.target))
                    c3.append(rel.target)
                    chains.append(c3)

    return errors

valid_id = re.compile("^ewn-[A-Za-z0-9_\\-.]*$")

def is_valid_id(xml_id):
    return bool(valid_id.match(xml_id))

def main():
    wn = parse_wordnet("wn.xml")

    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fix = True
    else:
        fix = False

    errors = 0

    for entry in wn.entries:
        if not is_valid_id(entry.id):
            if fix:
                sys.stderr.write("Cannot be fixed")
                sys.exit(-1)
            print("ERROR: Invalid ID " + entry.id)
            errors += 1
        for sense in entry.senses:
            if not is_valid_id(sense.id):
                if fix:
                    sys.stderr.write("Cannot be fixed")
                    sys.exit(-1)
                print("ERROR: Invalid ID " + sense.id)
                errors += 1
    for synset in wn.synsets:
        if not is_valid_id(synset.id):
            if fix:
                sys.stderr.write("Cannot be fixed")
                sys.exit(-1)
            print("ERROR: Invalid ID " + synset.id)
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

    if fix:
        pass
    elif errors > 0:
        print("Validation failed. %d errors" % errors)
        sys.exit(-1)
    else:
        print("No validity issues")

if __name__ == "__main__":
    main()
