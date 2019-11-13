import sys
import wordnet
import argparse
import os
import pickle

def update_def(wn, synset, defn):
    print("Previous definitions:")
    for d in synset.definitions:
        print("> " + d)
    wn_synset = wordnet.parse_wordnet("src/wn-%s.xml" % synset.lex_name)
    ss = wn_synset.synset_by_id(synset.id)
    ss.definitions = [defn]
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

def main():
    parser = argparse.ArgumentParser(description="Change a relationship within the wordnet")
    parser.add_argument('id', metavar='ID', type=str, 
            help="The ID of the synset (sense) for the relationship")
    parser.add_argument('--defn', type=str,
            help="The new definition")
    parser.add_argumnet('--add',
            help="Add the new definition and retain the previous definition (otherwise this definition replaces previous definitions)")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))

    synset = wn.synset_by_id(args.source_id)

    if not synset:
        print("Could not find the synset %s" % args.source_id)
        sys.exit(-1)

    if not args.defn:
        print("Please specify a definition")
        sys.exit(-1)

    update_def(wn, synset, args.defn)

if __name__ == "__main__":
    main()
