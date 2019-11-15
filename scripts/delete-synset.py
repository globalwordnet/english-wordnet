import sys
import wordnet
import argparse
import os
import pickle

def delete_rel(source, target):
    """Delete all relationships between two synsets"""
    print("Delete %s =*=> %s" % (source.id, target.id))
    wn_source = wordnet.parse_wordnet("src/wn-%s.xml" % source.lex_name)
    ss = wn_source.synset_by_id(source.id)
    ss.synset_relations = [r for r in ss.synset_relations if r.target != target.id]
    with open("src/wn-%s.xml" % source.lex_name, "w") as out:
        wn_source.to_xml(out, True)

def referring_synsets(wn, synset):
    """Get all other synsets that refer to this synset"""
    return [ss for ss in wn.synsets if [r for r in ss.synset_relations if r.target == synset.id]]

def delete_synset(wn, synset):
    for r in referring_synsets(wn, synset):
        delete_rel(synset, r)
        delete_rel(r, synset)


def main():
    parser = argparse.ArgumentParser(description="Delete a synset")
    parser.add_argument('id', metavar='ID', type=str,
            help="The identifier of the synset to delete")
    parser.add_argument('--reason', type=str,
            help="A justification for deleting this synset")

    args = parser.parse_args()

    # Slightly speeds up the loading of WordNet
    if not os.path.exists("wn.pickle") or os.path.getmtime("wn.pickle") < os.path.getmtime("wn.xml"):
        print("Loading wordnet")
        wn = wordnet.parse_wordnet("wn.xml")
        pickle.dump(wn, open("wn.pickle", "wb"))
    else:
        wn = pickle.load(open("wn.pickle", "rb"))

    synset = wn.synset_by_id(args.id)

    if not synset:
        print("Could not find the synset %s" % args.id)
        sys.exit(-1)

    input("This will permanently delete a synset. Are you sure this wouldn't be better handled with a merge? Press any key to continue...")

    delete_synset(wn, synset)

if __name__ == "__main__":
    main()


