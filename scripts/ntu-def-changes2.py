from wordnet import *
import csv
import re

wn = parse_wordnet("wn.xml")

with open("ntu-changes2.csv") as inp:
    inp.readline()
    r = csv.reader(inp)
    for row in r:
        key, def_ntu, def_ewn, def_new, ntu, ewn, new, other = row

        if new == "TRUE":
            ss = wn.synset_by_id(key)
            if not ss:
                print("bad ss: " + key)
                continue

            wn_ss = parse_wordnet("src/wn-%s.xml" % (ss.lex_name))
            with open("src/wn-%s.xml" % (ss.lex_name), "w") as xml:
                wn_ss.synset_by_id(key).definitions[0] = Definition(def_new)
                wn_ss.to_xml(xml, True)
        elif other:
            ss = wn.synset_by_id(key)
            if not ss:
                print("bad ss: " + key)
                continue

            wn_ss = parse_wordnet("src/wn-%s.xml" % (ss.lex_name))
            with open("src/wn-%s.xml" % (ss.lex_name), "w") as xml:
                wn_ss.synset_by_id(key).definitions[0] = Definition(other)
                wn_ss.to_xml(xml, True)





