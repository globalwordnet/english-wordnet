import sys
import wordnet
import argparse
import re
import change_manager

def main():
    parser = argparse.ArgumentParser(description="Add or remove an entry from a synset")
    parser.add_argument('synset', metavar='SYNSET_ID', type=str, nargs="?",
            help="The ID of the synset to change")
    parser.add_argument('lemma', metavar='LEMMA', type=str, nargs="?",
            help="The lemma to change")
    parser.add_argument('--add', action='store_true',
            help="Add this relation as a new relation")
    parser.add_argument('--delete', action='store_true',
            help="Remove this relation (do not replace or change)")
    parser.add_argument('-n', metavar='N', type=int, default=-1,
            help="The position of this synset within the list of senses for the entry")
    parser.add_argument('-i', metavar='IDX', type=int, default=-1,
            help="The position of this lemma in the synset")

    args = parser.parse_args()

    if not args.add and not args.delete:
        print("No action chosen")
        sys.exit(-1)

    wn = change_manager.load_wordnet()

    if not args.synset:
        synset_id = "ewn-" + input("Enter synset ID : ewn-")
    else:
        synset_id = args.synset

    synset = wn.synset_by_id(synset_id)

    print("Entries: " + ", ".join(wn.members_by_id(synset_id)))

    if not args.lemma:
        if args.add:
            lemma = input("New entry: ")
        elif args.delete:
            lemma = input("Entry to remove: ")
    else:
        lemma = args.lemma

    if not synset:
        print("Could not find synset")
        sys.exit(-1)

    if args.add:
        change_manager.add_entry(wn, synset, lemma, args.i, args.n)
    elif args.delete:
        change_manager.delete_entry(wn, synset, 
                "ewn-%s-%s" % (change_manager.escape_lemma(lemma), synset.part_of_speech.value))

if __name__ == "__main__":
    main()
 
