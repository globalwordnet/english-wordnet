import sys
import wordnet
import argparse
import re
import change_manager
import csv


def main():
    parser = argparse.ArgumentParser(description="Add or remove a synset")
    parser.add_argument('synset', metavar='SYNSET_ID', type=str, nargs="?",
                        help="The ID of the synset to change")
    parser.add_argument('--add', action='store_true',
                        help="Add this synset")
    parser.add_argument('--delete', action='store_true',
                        help="Remove this synset")
    parser.add_argument(
        '--reason',
        type=str,
        help="The reason for a deletion or merge (required for deletion)")
    parser.add_argument('--definition', type=str,
                        help="The definition of the new synset")
    parser.add_argument('--lexfile', type=str,
                        help="The lexicographer file to write the synset to")
    parser.add_argument('--pos', type=str,
                        help="The part of speech (n|v|a|r|s)")
    parser.add_argument(
        '--supersededby',
        type=str,
        help="The ID of the superseding synset (required for deletion)")

    args = parser.parse_args()

    wn = change_manager.load_wordnet()

    if not args.delete and not args.add:
        mode = input("(A)dd synset/(d)elete synset: ").lower()
        if mode == "a":
            args.add = True
        elif mode == "d":
            args.delete = True
        else:
            print("Bad mode: " + mode)
            sys.exit(-1)

    if args.delete:
        if not args.synset:
            args.synset = "oewn-" + input("Enter synset ID: oewn-")
        synset = wn.synset_by_id(args.synset)

        if not synset:
            print("Could not find synset")
            sys.exit(-1)

        if not args.reason:
            args.reason = input("Reason for deletion with (#IssueNo): ")

        if not args.supersededby:
            args.supersededby = "oewn-" + \
                input("Enter superseding synset ID: oewn-")

        supersede_synset = wn.synset_by_id(args.supersededby)

        if not supersede_synset:
            print("Could not find synset")
            sys.exit(-1)

    if args.add:
        if not args.definition:
            args.definition = input("Definition: ")
        if not args.lexfile:
            args.lexfile = input("Lexicographer file: ")
        if not args.pos:
            args.pos = input(
                "Part of speech (n)oun/(v)erb/(a)djective/adve(r)b/(s)atellite: ").lower()

    if args.add:
        new_id = change_manager.add_synset(
            wn, args.definition, args.lexfile, args.pos)
        print(
            "New synset created with ID %s. Please use change-entry and change-relation scripts to add entries and relations" %
            new_id)
    elif args.delete:
        if not args.reason:
            print("Please give a reason for deletion")
            sys.exit(-1)
        change_manager.delete_synset(wn, synset, supersede_synset, args.reason)
    else:
        print("No action chosen")
        sys.exit(-1)
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
