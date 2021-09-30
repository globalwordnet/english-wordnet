import sys
import wordnet
import argparse
import os
import pickle
from autocorrect import Speller


def update_def(wn, synset, defn, add):
    spell = Speller(lang='en')
    if any([spell(w) != w for w in defn.split()]):
        if input(
                "There may be spelling errors in this definition. Proceed [y/N] : ") != "y":
            sys.exit(-1)
    print("Previous definitions:")
    for d in synset.definitions:
        print("> " + d.text)
    wn_synset = wordnet.parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    ss = wn_synset.synset_by_id(synset.id)
    if add:
        ss.definitions = ss.definitions + [wordnet.Definition(defn)]
    else:
        ss.definitions = [wordnet.Definition(defn)]
    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)


def update_ili_def(wn, synset, defn):
    wn_synset = wordnet.parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    ss = wn_synset.synset_by_id(synset.id)
    ss.ili_definition = wordnet.Definition(defn)
    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)


def main():
    parser = argparse.ArgumentParser(
        description="Change a definition within the wordnet")
    parser.add_argument(
        'id',
        metavar='ID',
        type=str,
        nargs="?",
        help="The ID of the synset (sense) for the relationship")
    parser.add_argument(
        '--add',
        action='store_true',
        help="Add the new definition and retain the previous definition (otherwise this definition replaces previous definitions)")
    parser.add_argument('--defn', type=str,
                        help="The new definition")
    parser.add_argument('--ili', action='store_true',
                        help="Set the ILI definition")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime(
            "wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))

    if not args.id:
        id = "oewn-" + input("Enter synset ID : oewn-")
    else:
        id = args.id

    synset = wn.synset_by_id(id)

    if not synset:
        print("Could not find the synset %s" % args.id)
        sys.exit(-1)

    if args.ili:
        if not args.defn:
            args.defn = synset.definitions[0].text

        update_ili_def(wn, synset, args.defn)
    else:
        if not args.defn:
            print("Definition     : " + synset.definitions[0].text)
            defn = input("New Definition : ")
        else:
            defn = args.defn

        update_def(wn, synset, defn, args.add)
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
