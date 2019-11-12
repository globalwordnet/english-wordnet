import sys
import wordnet
import argparse
import os
import pickle

def delete_rel(source, target):
    """Delete all relationships between two synsets"""
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    ss.synset_relations = [r for r in ss.synset_relations if r.target != target.id]
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

def insert_rel(source, rel_type, target):
    """Insert a single relation between two synsets"""
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    ss.synset_relations.append(wordnet.SynsetRelation(target.id, rel_type))
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

    
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
    insert_rel(source, rel_type, old_target)
    if rel_type in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[rel_type]
        delete_rel(old_target, source)
        insert_rel(new_target, inv_rel_type, source)

def update_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    delete_rel(source, target)
    insert_rel(soucce, new_rel, target)
    if new_rel in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[new_rel]
        delete_rel(target, source)
        insert_rel(target, inv_rel_type, source)


def main():
    parser = argparse.ArgumentParser(description="Change a relationship within the wordnet")
    parser.add_argument('source_id', metavar='SOURCE_ID', type=str, 
            help="The ID of the source synset (sense) for the relationship")
    parser.add_argument('target_id', metavar='TARGET_ID', type=str,
            help="The ID of the target synset (sense) for the relationship")
    parser.add_argument('--new-source', type=str,
            help="The ID of the new source synset")
    parser.add_argument('--new-target', type=str,
            help="The ID of the new target synset")
    parser.add_argument('--new-relation', type=str,
            help="The type of the new relationship")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))

    source_synset = wn.synset_by_id(args.source_id)

    if not source_synset:
        print("Could not find the source synset %s" % args.source_id)
        sys.exit(-1)

    target_synset = wn.synset_by_id(args.target_id)

    if not target_synset:
        print("Could not find the target synset %s" % args.target_id)
        sys.exit(-1)

    if args.new_source:
        if args.new_target or args.new_relation:
            print("Please perform a single change at a time")
            sys.exit(-1)
        new_source = wn.synset_by_id(args.new_source)

        if not new_source:
            print("Could not find the new source synset %s" % args.new_source)
            sys.exit(-1)

        update_source(wn, source_synset, target_synset, new_source)

    elif args.new_target:
        if args.new_source or args.new_relation:
            print("Please perform a single change at a time")
            sys.exit(-1)
        new_target = wn.synset_by_id(args.new_target)

        if not new_target:
            print("Could not find the new target synset %s" % args.new_target)
            sys.exit(-1)

        update_target(wn, source_synset, target_synset, new_target)

    elif args.new_relation:
        if args.new_source or args.new_target:
            print("Please perform a single change at a time")
            sys.exit(-1)

        if args.new_relation not in wordnet.SynsetRelType:
            print("Not a valid relation type %s" % args.new_relation)

        update_relation(wn, source_synset, target_synset, SynsetRelType(args.new_relation))

    else:
        print("No change specified")

if __name__ == "__main__":
    main()
