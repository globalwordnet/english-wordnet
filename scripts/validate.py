import wordnet
import re
import sys

valid_id = re.compile("^ewn-[A-Za-z0-9_\\-.]*$")

def is_valid_id(xml_id):
    return bool(valid_id.match(xml_id))

def main():
    wn = wordnet.parse_wordnet("wn.xml")

    errors = 0

    for entry in wn.entries:
        if not is_valid_id(entry.id):
            print("ERROR: Invalid ID " + entry.id)
            errors += 1
        for sense in entry.senses:
            if not is_valid_id(sense.id):
                print("ERROR: Invalid ID " + sense.id)
                errors += 1
    for synset in wn.synsets:
        if not is_valid_id(synset.id):
            print("ERROR: Invalid ID " + synset.id)
            errors += 1

    if errors > 0:
        print("Validation failed. %d errors" % errors)
        sys.exit(-1)
    else:
        print("No validity issues")

if __name__ == "__main__":
    main()
