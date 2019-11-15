import sys
import wordnet
import argparse
import re
import change_manager

def main():
    parser = argparse.ArgumentParser(description="Add or remove a synset")
    parser.add_argument('synset', metavar='SYNSET_ID', type=str, 
            help="The ID of the synset to change")
    parser.add_argument('--add', action='store_true',
            help="Add this relation as a new relation")
    parser.add_argument('--delete', action='store_true',
            help="Remove this relation (do not replace or change)")

    args = parser.parse_args()

    wn = change_manager.load_wordnet()

    synset = wn.synset_by_id(args.synset)

    if not synset:
        print("Could not find synset")
        sys.exit(-1)

    if args.add:
        change_manager.add_synset(wn, synset, args.defintion)
    elif args.delete:
        change_manager.delete_synset(wn, synset)
    else:
        print("No action chosen")
        sys.exit(-1)

if __name__ == "__main__":
    main()
 
