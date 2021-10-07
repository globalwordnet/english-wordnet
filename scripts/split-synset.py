import sys
import wordnet
import argparse
import re
import change_manager
import csv


def main():
    parser = argparse.ArgumentParser(
        description="Split a synset - delete the synset and add two (or more) new synsets")
    parser.add_argument('synset', metavar='SYNSET_ID', type=str, nargs="?",
                        help="The ID of the synset to change")
    parser.add_argument(
        '--definition',
        type=str,
        action='append',
        help="The definition of the new synsets (repeat for each synset)")
    parser.add_argument(
        '--reason',
        type=str,
        nargs="?",
        help="The reason for this change including issue number")

    args = parser.parse_args()

    wn = change_manager.load_wordnet()

    if not args.synset:
        args.synset = "oewn-" + input("Enter synset ID: oewn-")
    synset = wn.synset_by_id(args.synset)

    if not synset:
        print("Cannot find synset")
        exit(-1)

    if not args.definition:
        args.definition = []
        print("Enter definitions (empty line to finish)")
        while True:
            d1 = input("Definition: ")
            if d1:
                args.definition.append(d1)
            else:
                break

    if not args.definition:
        print("No new definitions")
        exit(-1)

    if not args.reason:
        args.reason = input("Reason for deletion (#IssueNo): ")

    new_ids = []
    for definition in args.definition:
        new_ids.append(
            change_manager.add_synset(
                wn,
                definition,
                synset.lexfile,
                synset.pos))

    change_manager.delete_synset(
        wn, synset, [
            wn.synset_for_id(new_id) for new_id in new_ids], args.reason)
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
