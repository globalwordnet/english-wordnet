import sys
import wordnet
import argparse
import os
import pickle
import re

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
    if new_rel in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[new_rel]
        delete_rel(target, source)
        insert_rel(target, inv_rel_type, source)

def add_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    insert_rel(source, new_rel, target)
    if new_rel in wordnet.inverse_synset_rels:
        inv_rel_type = wordnet.inverse_synset_rels[new_rel]
        insert_rel(target, inv_rel_type, source)

def delete_relation(wn, source, target):
    """Change the type of a link"""
    delete_rel(source, target)
    delete_rel(target, source)


def delete_sense_rel(wn, source, target):
    """Delete all relationships between two senses"""
    print("Delete %s =*=> %s" % (source, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % lex_name)
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations = [r for r in sense.sense_relations if r.target != target]
    with open("src/wn-%s.xml" % lex_name, "w") as out:
        wn_source.to_xml(out, True)

def insert_sense_rel(wn, source, rel_type, target):
    """Insert a single relation between two senses"""
    print("Insert %s =%s=> %s" % (source, rel_type, target))
    (source_synset, source_entry) = decompose_sense_id(source)
    lex_name = wn.synset_by_id(source_synset).lex_name
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % lex_name)
    entry = wn_source.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    sense.sense_relations.append(wordnet.SenseRelation(target, rel_type))
    with open("src/wn-%s.xml" % lex_name, "w") as out:
        wn_source.to_xml(out, True)

    
def find_sense_type(wn, source, target):
    """Get the first relation type between the senses"""
    (source_synset, source_entry) = decompose_sense_id(source)
    entry = wn.entry_by_id(source_entry)
    sense = [sense for sense in entry.senses if sense.id == source][0]
    x = [r for r in source.sense_relations if r.target == target.id]
    if len(x) != 1:
        raise Exception("Synsets not linked or linked by more than one property")
    return x[0].rel_type
    

def update_source_sense(wn, old_source, target, new_source):
    """Change the source of a link"""
    rel_type = find_sense_type(old_source, target)
    delete_sense_rel(wn, old_source, target)
    insert_sense_rel(wn, new_source, rel_type, target)
    if rel_type in wordnet.inverse_sense_rels:
        inv_rel_type = wordnet.inverse_sense_rels[rel_type]
        delete_sense_rel(wn, target, old_source)
        insert_sense_rel(wn, target, inv_rel_type, new_source)

def update_target_sense(wn, source, old_target, new_target):
    """Change the target of a link"""
    rel_type = find_sense_type(source, old_target)
    delete_sense_rel(wn, source, old_target)
    insert_sense_rel(wn, source, rel_type, new_target)
    if rel_type in wordnet.inverse_sense_rels:
        inv_rel_type = wordnet.inverse_sense_rels[rel_type]
        delete_sense_rel(wn, old_target, source)
        insert_sense_rel(wn, new_target, inv_rel_type, source)

def update_sense_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    delete_sense_rel(wn, source, target)
    insert_sense_rel(wn, source, new_rel, target)
    if new_rel in wordnet.inverse_sense_rels:
        inv_rel_type = wordnet.inverse_sense_rels[new_rel]
        delete_sense_rel(wn, target, source)
        insert_sense_rel(wn, target, inv_rel_type, source)

def add_sense_relation(wn, source, target, new_rel):
    """Change the type of a link"""
    insert_sense_rel(wn, source, new_rel, target)
    if new_rel in wordnet.inverse_sense_rels:
        inv_rel_type = wordnet.inverse_sense_rels[new_rel]
        insert_sense_rel(wn, target, inv_rel_type, source)

def delete_sense_relation(wn, source, target):
    """Change the type of a link"""
    delete_sense_rel(wn, source, target)
    delete_sense_rel(wn, target, source)


sense_id_re = re.compile(r"ewn-(.*)-(.)-(\d{8})-\d{2}")

def decompose_sense_id(sense_id):
    m = sense_id_re.match(sense_id)
    if m:
        lemma = m.group(1)
        pos = m.group(2)
        ssid = m.group(3)
        return ("ewn-%s-%s" % (ssid, pos), "ewn-%s-%s" % (lemma, pos))
    else:
        raise Exception("Not a sense ID")


def sense_exists(wn, sense_id):
    if sense_id_re.match(sense_id):
        (_, entry_id) = decompose_sense_id(sense_id)
        entry = wn.entry_by_id(entry_id)
        if entry:
            senses = [sense for sense in entry.senses if sense.id == sense_id]
            return len(senses) == 1
    return False


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
    parser.add_argument('--add', action='store_true',
            help="Add this relation as a new relation")
    parser.add_argument('--delete', action='store_true',
            help="Remove this relation (do not replace or change)")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))
    
    if sense_id_re.match(args.source_id):
        (source_id, source_entry_id) = decompose_sense_id(args.source_id)
    else:
        source_id = args.source_id
        source_entry_id = None

    source_synset = wn.synset_by_id(source_id)

    if not source_synset:
        print("Could not find the source synset %s" % source_id)
        sys.exit(-1)

    if sense_id_re.match(args.target_id):
        (target_id, target_entry_id) = decompose_sense_id(args.target_id)
    else:
        target_id = args.target_id
        target_entry_id = None

    target_synset = wn.synset_by_id(target_id)

    if not target_synset:
        print("Could not find the target synset %s" % target_id)
        sys.exit(-1)

    if args.new_source:
        if args.new_target or args.new_relation:
            print("Please perform a single change at a time")
            sys.exit(-1)
        if args.add or args.delete:
            print("Specifying new source when adding or deleting does not make sense")
            sys.exit(-1)

        if source_entry_id or target_entry_id:
            if not sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            if not sense_exists(wn, args.new_source):
                print("New source sense %d does not exist" % args.new_source)
                sys.exit(-1)
            update_source_sense(wn, args.source_id, args.target_id, args.new_source)
        else:
            new_source = wn.synset_by_id(args.new_source)

            if not new_source:
                print("Could not find the new source synset %s" % args.new_source)
                sys.exit(-1)


            update_source(wn, source_synset, target_synset, new_source)

    elif args.new_target:
        if args.new_source or args.new_relation:
            print("Please perform a single change at a time")
            sys.exit(-1)
        if args.add or args.delete:
            print("Specifying new source when adding or deleting does not make sense")
            sys.exit(-1)
        if source_entry_id or target_entry_id:
            if not sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            if not sense_exists(wn, args.new_target):
                print("New target sense %d does not exist" % args.new_target)
                sys.exit(-1)
            update_target_sense(wn, args.source_id, args.target_id, args.new_target)
        else:
            new_target = wn.synset_by_id(args.new_target)

            if not new_target:
                print("Could not find the new target synset %s" % args.new_target)
                sys.exit(-1)

            update_target(wn, source_synset, target_synset, new_target)

    elif args.new_relation:
        if args.new_source or args.new_target:
            print("Please perform a single change at a time")
            sys.exit(-1)

        if source_entry_id:
            if args.new_relation not in wordnet.SenseRelType._value2member_map_:
                print("Not a valid relation type %s" % args.new_relation)
                sys.exit(-1)
        else:
            if args.new_relation not in wordnet.SynsetRelType._value2member_map_:
                print("Not a valid relation type %s" % args.new_relation)
                sys.exit(-1)

        if args.add:
            if args.delete:
                print("Cannot both add and delete a relation")
                sys.exit(-1)
            if source_entry_id or target_entry_id:
                if not sense_exists(wn, args.source_id):
                    print("Source sense %d does not exist" % args.source_id)
                    sys.exit(-1)
                if not sense_exists(wn, args.target_id):
                    print("Target sense %d does not exist" % args.target_id)
                    sys.exit(-1)
                add_sense_relation(wn, args.source_id, args.target_id, wordnet.SenseRelType(args.new_relation))
            else:
                add_relation(wn, source_synset, target_synset, wordnet.SynsetRelType(args.new_relation))
        elif args.delete:
            if source_entry_id or target_entry_id:
                if not sense_exists(wn, args.source_id):
                    print("Source sense %d does not exist" % args.source_id)
                    sys.exit(-1)
                if not sense_exists(wn, args.target_id):
                    print("Target sense %d does not exist" % args.target_id)
                    sys.exit(-1)
                delete_sense_relation(wn, args.source_id, args.target_id)
            else:
                delete_relation(wn, source_synset, target_synset)
        else:
            if source_entry_id or target_entry_id:
                if not sense_exists(wn, args.source_id):
                    print("Source sense %d does not exist" % args.source_id)
                    sys.exit(-1)
                if not sense_exists(wn, args.target_id):
                    print("Target sense %d does not exist" % args.target_id)
                    sys.exit(-1)
                update_sense_relation(wn, args.source_id, args.target_id, wordnet.SenseRelType(args.new_relation))
            else:
                update_relation(wn, source_synset, target_synset, wordnet.SynsetRelType(args.new_relation))
    elif args.delete:
        if args.add:
            print("Cannot both add and delete a relation")
            sys.exit(-1)
        if source_entry_id or target_entry_id:
            if not sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            delete_sense_relation(wn, args.source_id, args.target_id)
        else:
            delete_relation(wn, source_synset, target_synset)
    else:
        print("No change specified")

if __name__ == "__main__":
    main()
