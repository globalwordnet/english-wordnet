import sys
import wordnet
import argparse
import re
import change_manager
import csv

def main():
    parser = argparse.ArgumentParser(description="Add or remove a synset")
    parser.add_argument('synset', metavar='SYNSET_ID', type=str, 
            help="The ID of the synset to change")
    parser.add_argument('--add', action='store_true',
            help="Add this relation as a new relation")
    parser.add_argument('--delete', action='store_true',
            help="Remove this relation (do not replace or change)")
    parser.add_argument('--reason', type=str,
            help="The reason for a deletion or merge")

    args = parser.parse_args()

    wn = change_manager.load_wordnet()

    synset = wn.synset_by_id(args.synset)

    if not synset:
        print("Could not find synset")
        sys.exit(-1)

    if args.add:
        change_manager.add_synset(wn, synset, args.defintion)
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
 
