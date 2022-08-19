import sys
import wordnet
import argparse
import os
import pickle
import re
import change_manager


def with_ewn(x):
    if x:
        return "oewn-" + x
    else:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Change a relationship within the wordnet")
    parser.add_argument(
        'source_id',
        metavar='SOURCE_ID',
        type=str,
        nargs="?",
        help="The ID of the source synset (sense) for the relationship")
    parser.add_argument(
        'target_id',
        metavar='TARGET_ID',
        type=str,
        nargs="?",
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
    parser.add_argument('--reverse', action='store_true',
                        help="Reverse this relation (swap source and target)")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    wn = change_manager.load_wordnet()

    if not args.source_id:
        args.source_id = "oewn-" + input("Enter source synset ID: oewn-")

    if change_manager.sense_id_re.match(args.source_id):
        (source_id, source_entry_id) = change_manager.decompose_sense_id(args.source_id)
    else:
        source_id = args.source_id
        source_entry_id = None

    source_synset = wn.synset_by_id(source_id)

    if not source_synset:
        print("Could not find the source synset %s" % source_id)
        sys.exit(-1)

    if not args.target_id:
        args.target_id = "oewn-" + input("Enter target synset ID: oewn-")

    if change_manager.sense_id_re.match(args.target_id):
        (target_id, target_entry_id) = change_manager.decompose_sense_id(args.target_id)
    else:
        target_id = args.target_id
        target_entry_id = None

    target_synset = wn.synset_by_id(target_id)

    if not target_synset:
        print("Could not find the target synset %s" % target_id)
        sys.exit(-1)

    if not args.new_source and not args.new_target and not args.new_relation and not args.delete:
        mode = input(
            "[A]dd new relation/[D]elete existing relation/[R]everse relation/[C]hange relation: ").lower()
        if mode == "a":
            args.add = True
            if not args.new_relation:
                args.new_relation = input("Enter new relation: ")
        elif mode == "c":
            mode = input("Change [S]ubject/[T]arget/[R]elation: ").lower()
            if mode == "s":
                args.new_source = with_ewn(
                    input("Enter new source (or blank for no change): oewn-"))
            elif mode == "t":
                args.new_target = with_ewn(
                    input("Enter new target (or blank for no change): oewn-"))
            elif mode == "r":
                args.new_relation = input(
                    "Enter new relation (or blank for no change): oewn-")
            else:
                print("Bad choice")
                sys.exit(-1)
        elif mode == "d":
            args.delete = True
        elif mode == "r":
            args.reverse = True
        else:
            print("Bad mode")
            sys.exit(-1)
            

    if args.new_source:
        if args.new_target or args.new_relation:
            print("Please perform a single change at a time")
            sys.exit(-1)
        if args.add or args.delete:
            print("Specifying new source when adding or deleting does not make sense")
            sys.exit(-1)

        if source_entry_id or target_entry_id:
            if not change_manager.sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not change_manager.sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            if not change_manager.sense_exists(wn, args.new_source):
                print("New source sense %d does not exist" % args.new_source)
                sys.exit(-1)
            change_manager.update_source_sense(
                wn, args.source_id, args.target_id, args.new_source)
        else:
            new_source = wn.synset_by_id(args.new_source)

            if not new_source:
                print(
                    "Could not find the new source synset %s" %
                    args.new_source)
                sys.exit(-1)

            change_manager.update_source(
                wn, source_synset, target_synset, new_source)

    elif args.new_target:
        if args.new_source or args.new_relation:
            print("Please perform a single change at a time")
            sys.exit(-1)
        if args.add or args.delete:
            print("Specifying new source when adding or deleting does not make sense")
            sys.exit(-1)
        if source_entry_id or target_entry_id:
            if not change_manager.sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not change_manager.sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            if not change_manager.sense_exists(wn, args.new_target):
                print("New target sense %d does not exist" % args.new_target)
                sys.exit(-1)
            change_manager.update_target_sense(
                wn, args.source_id, args.target_id, args.new_target)
        else:
            new_target = wn.synset_by_id(args.new_target)

            if not new_target:
                print(
                    "Could not find the new target synset %s" %
                    args.new_target)
                sys.exit(-1)

            change_manager.update_target(
                wn, source_synset, target_synset, new_target)

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
                if not change_manager.sense_exists(wn, args.source_id):
                    print("Source sense %d does not exist" % args.source_id)
                    sys.exit(-1)
                if not change_manager.sense_exists(wn, args.target_id):
                    print("Target sense %d does not exist" % args.target_id)
                    sys.exit(-1)
                if args.source_id == args.target_id:
                    print("Won't link sense %d to itself" % args.source_id)
                    sys.exit(-1) 
                change_manager.add_sense_relation(
                    wn, args.source_id, args.target_id, wordnet.SenseRelType(
                        args.new_relation))
            else:
                if source_synset == target_synset:
                    print("Won't link synset %s to itself" % source_synset)
                    sys.exit(-1) 
                change_manager.add_relation(
                    wn,
                    source_synset,
                    target_synset,
                    wordnet.SynsetRelType(
                        args.new_relation))
        elif args.delete:
            if source_entry_id or target_entry_id:
                if not change_manager.sense_exists(wn, args.source_id):
                    print("Source sense %d does not exist" % args.source_id)
                    sys.exit(-1)
                if not change_manager.sense_exists(wn, args.target_id):
                    print("Target sense %d does not exist" % args.target_id)
                    sys.exit(-1)
                change_manager.delete_sense_relation(
                    wn, args.source_id, args.target_id)
            else:
                change_manager.delete_relation(
                    wn, source_synset, target_synset)
        else:
            if source_entry_id or target_entry_id:
                if not change_manager.sense_exists(wn, args.source_id):
                    print("Source sense %d does not exist" % args.source_id)
                    sys.exit(-1)
                if not change_manager.sense_exists(wn, args.target_id):
                    print("Target sense %d does not exist" % args.target_id)
                    sys.exit(-1)
                change_manager.update_sense_relation(
                    wn, args.source_id, args.target_id, wordnet.SenseRelType(
                        args.new_relation))
            else:
                change_manager.update_relation(
                    wn, source_synset, target_synset, wordnet.SynsetRelType(
                        args.new_relation))
    elif args.delete:
        if args.add:
            print("Cannot both add and delete a relation")
            sys.exit(-1)
        if source_entry_id or target_entry_id:
            if not change_manager.sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not change_manager.sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            change_manager.delete_sense_relation(
                wn, args.source_id, args.target_id)
        else:
            change_manager.delete_relation(wn, source_synset, target_synset)
    elif args.reverse:
        if source_entry_id or target_entry_id:
            if not change_manager.sense_exists(wn, args.source_id):
                print("Source sense %d does not exist" % args.source_id)
                sys.exit(-1)
            if not change_manager.sense_exists(wn, args.target_id):
                print("Target sense %d does not exist" % args.target_id)
                sys.exit(-1)
            change_manager.reverse_sense_rel(
                wn, args.source_id, args.target_id)
        else:
            change_manager.reverse_rel(wn, source_synset, target_synset)

    else:
        print("No change specified")
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
