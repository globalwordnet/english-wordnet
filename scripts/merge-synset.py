import sys
import wordnet
import argparse
import re
import change_manager
import csv
from merge import wn_merge


def main():
    parser = argparse.ArgumentParser(
        description="Merge a synset - delete one or more synset and merge all properties. This may create weird or contradictory results so should be used with care")
    parser.add_argument('synsets', metavar='SYNSET_ID', type=str, nargs="*",
                        help="The ID of the synset to change")
    parser.add_argument(
        '--reason',
        type=str,
        nargs="?",
        help="The reason for this change including issue number")
    parser.add_argument('--lex_file', type=str,
                        help="The lex file to write the new synset to")

    args = parser.parse_args()

    wn = change_manager.load_wordnet()

    if not args.synsets:
        args.synsets = []
        print("Enter synsets (empty line to finish)")
        while True:
            id1 = input("Enter synset ID: oewn-")
            if id1:
                args.synsets.append("oewn-" + id1)
            else:
                break

    if not args.synsets:
        print("Need at least one synset to merge")
        exit(-1)

    synsets = [wn.synset_by_id(ss) for ss in args.synsets]

    if any(s is None for s in synsets):
        print("Cannot find synset")
        exit(-1)

    if any(s.part_of_speech != synsets[0].part_of_speech for s in synsets):
        print("Merging across parts of speech is not correct!")
        exit(-1)

    if not args.lex_file and any(
            s.lex_name != synsets[0].lex_name for s in synsets):
        print("Merging across lex files: " +
              ", ".join(s.lex_name for s in synsets))
        args.lex_file = input("Lex file : ")
    elif not args.lex_file:
        args.lex_file = synsets[0].lex_name

    if not args.reason:
        args.reason = input("Reason for deletion (#IssueNo): ")

    new_id = change_manager.merge_synset(
        wn, synsets, args.reason, args.lex_file)

    wn_merge()
    wn = change_manager.load_wordnet()

    for synset in synsets:
        change_manager.delete_synset(wn, synset,
                                     [new_id],
                                     args.reason)


if __name__ == "__main__":
    main()
