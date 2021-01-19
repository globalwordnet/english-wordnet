from wordnet import *
import change_manager
from glob import glob
import re
from sys import exit
import sense_keys

def assign_keys(wn, wn_file):
    swn = parse_wordnet(wn_file)
    for e in swn.entries:
        for s in e.senses:
            if not s.sense_key:
                s.sense_key = sense_keys.get_sense_key(wn, swn, e, s, wn_file)
    with open(wn_file, "w") as outp:
        swn.to_xml(outp, True)


if __name__ == "__main__":
    wn = change_manager.load_wordnet()
    for f in glob ("src/xml/wn-*.xml"):
        assign_keys(wn, f)
