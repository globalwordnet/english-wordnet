import sys
import wordnet
import argparse
import os
import pickle


def add_ex(wn, synset, example):
    wn_synset = wordnet.parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    ss = wn_synset.synset_by_id(synset.id)
    ss.examples = ss.examples + [wordnet.Example(example)]
    with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)


def delete_ex(wn, synset, example):
    wn_synset = wordnet.parse_wordnet("src/xml/wn-%s.xml" % synset.lex_name)
    ss = wn_synset.synset_by_id(synset.id)
    n_exs = len(ss.examples)
    ss.examples = [ex for ex in ss.examples if ex.text != example]
    if len(ss.examples) == n_exs:
        print("No change")
    else:
        with open("src/xml/wn-%s.xml" % synset.lex_name, "w") as out:
            wn_synset.to_xml(out, True)


def main():
    parser = argparse.ArgumentParser(
        description="Add (or delete) an example of a synset")
    parser.add_argument(
        'id',
        metavar='ID',
        type=str,
        help="The ID of the synset (sense) for the relationship")
    parser.add_argument('--delete', action='store_true',
                        help="Delete this definition instead of adding it")
    parser.add_argument('--example', type=str,
                        help="The new example")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime(
            "wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))

    synset = wn.synset_by_id(args.id)

    if not synset:
        print("Could not find the synset %s" % args.id)
        sys.exit(-1)

    if not args.example:
        print("Please specify an example")
        sys.exit(-1)

    if not args.example.startswith("\""):
        print("Examples must start and end with a quotation")
        sys.exit(-1)

    if args.delete:
        delete_ex(wn, synset, args.example)
    else:
        add_ex(wn, synset, args.example)
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
