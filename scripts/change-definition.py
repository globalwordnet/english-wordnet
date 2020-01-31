import sys
import wordnet
import argparse
import os
import pickle

def update_def(wn, synset, defn, add):
    print("Previous definitions:")
    for d in synset.definitions:
        print("> " + d.text)
    wn_synset = wordnet.parse_wordnet("src/wn-%s.xml" % synset.lex_name)
    ss = wn_synset.synset_by_id(synset.id)
    if add:
        ss.definitions = ss.definitions + [wordnet.Definition(defn)]
    else:
        ss.definitions = [wordnet.Definition(defn)]
    with open("src/wn-%s.xml" % synset.lex_name, "w") as out:
        wn_synset.to_xml(out, True)

def main():
    parser = argparse.ArgumentParser(description="Change a definition within the wordnet")
    parser.add_argument('id', metavar='ID', type=str, nargs="?",
            help="The ID of the synset (sense) for the relationship")
    parser.add_argument('--add', action='store_true',
            help="Add the new definition and retain the previous definition (otherwise this definition replaces previous definitions)")
    parser.add_argument('--defn', type=str,
            help="The new definition")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))
    
    if not args.id:
        id = "ewn-" + input("Enter synset ID : ewn-")
    else:
        id = args.id

    synset = wn.synset_by_id(id)

    if not synset:
        print("Could not find the synset %s" % args.id)
        sys.exit(-1)

    if not args.defn:
        print("Definition     : " + synset.definitions[0].text)
        defn = input("New Definition : ")
    else:
        defn = args.defn

    update_def(wn, synset, defn, args.add)

if __name__ == "__main__":
    main()
