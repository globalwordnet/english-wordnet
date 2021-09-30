import sys
import wordnet
import argparse
import re
import change_manager


def main():
    parser = argparse.ArgumentParser(
        description="Add or remove an entry from a synset")
    parser.add_argument('synset', metavar='SYNSET_ID', type=str, nargs="?",
                        help="The ID of the synset to change")
    parser.add_argument('lemma', metavar='LEMMA', type=str, nargs="?",
                        help="The lemma to change")
    parser.add_argument('--add', action='store_true',
                        help="Add this entry to a synset")
    parser.add_argument('--delete', action='store_true',
                        help="Remove this entry from a synset")
    parser.add_argument('--move', action='store_true',
                        help="Change this entry to another synset")
    parser.add_argument('--target', type=str,
                        help="The target for a change")
    parser.add_argument(
        '-n',
        metavar='N',
        type=int,
        default=-
        1,
        help="The position of this synset within the list of senses for the entry")
    parser.add_argument('-i', metavar='IDX', type=int, default=-1,
                        help="The position of this lemma in the synset")

    args = parser.parse_args()

    if args.add:
        action = "A"
    elif args.delete:
        action = "D"
    elif args.move:
        action = "M"
    else:
        action = input("[A]dd/[D]elete/[M]ove? ").upper()
        if action != "A" and action != "D" and action != "M":
            print("Bad action")
            sys.exit(-1)

    wn = change_manager.load_wordnet()

    if not args.synset:
        synset_id = "oewn-" + input("Enter synset ID : oewn-")
    else:
        synset_id = args.synset

    synset = wn.synset_by_id(synset_id)

    entries = wn.members_by_id(synset_id)
    if entries:
        print("Entries: " + ", ".join(entries))
    else:
        print("No entries")

    if not args.lemma:
        if action == "A":
            lemma = input("New entry: ")
        elif action == "D":
            lemma = input("Entry to remove: ")
        elif action == "M":
            lemma = input("Entry to move: ")
    else:
        lemma = args.lemma

    if not synset:
        print("Could not find synset")
        sys.exit(-1)

    if action == "M" and not args.target:
        args.target = "oewn-" + input("Target synset: oewn-")

    if action == "A":
        change_manager.add_entry(wn, synset, lemma, args.i, args.n)
    elif action == "D":
        change_manager.delete_entry(
            wn, synset, "oewn-%s-%s" %
            (wordnet.escape_lemma(lemma), synset.part_of_speech.value))
    elif action == "M":
        target_synset = wn.synset_by_id(args.target)

        if not target_synset:
            print("Could not find synset")
            sys.exit(-1)

        if synset.lex_name == target_synset.lex_name:
            change_manager.change_entry(wn, synset, target_synset, lemma)
        else:
            print(
                "Moving across lexicographer files so implementing change as delete then add")
            change_manager.delete_entry(
                wn, synset, "oewn-%s-%s" %
                (wordnet.escape_lemma(lemma), synset.part_of_speech.value))
            change_manager.add_entry(wn, target_synset, lemma, args.i, args.n)
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
