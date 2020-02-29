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
    parser.add_argument('--reason', type=str,
            help="The reason for a deletion or merge")
    parser.add_argument('--definition', type=str,
            help="The definition of the new synset")
    parser.add_argument('--lexfile', type=str,
            help="The lexicographer file to write the synset to")
    parser.add_argument('--pos', type=str,
            help="The part of speech (n|v|a|r|s)")


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
            args.synset = "ewn-" + input("Enter synset ID: ewn-")
        synset = wn.synset_by_id(args.synset)

        if not synset:
            print("Could not find synset")
            sys.exit(-1)

    if args.add:
        if not args.definition:
            args.definition = input("Definition: ")
        if not args.lexfile:
            args.lexfile = input("Lexicographer file: ")
        if not args.pos:
            args.pos = input("Part of speech (n)oun/(v)erb/(a)djective/adve(r)b/(s)atellite: ").lower()

    if args.add:
        new_id = change_manager.add_synset(wn, args.definition, args.lexfile, args.pos)
        print("New synset created with ID %s. Please use change-entry and change-relation scripts to add entries and relations" % new_id) 
    elif args.delete:
        if not args.reason:
            print("Please give a reason for deletion")
            sys.exit(-1)
        change_manager.delete_synset(wn, synset)

        with open("src/deprecations.csv",'a') as f:
            writer = csv.writer(f)
            writer.writerow([synset.id, synset.ili, '', '', args.reason])
    else:
        print("No action chosen")
        sys.exit(-1)

if __name__ == "__main__":
    main()
 
