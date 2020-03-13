from wordnet import *
import csv
import re

defn_re = re.compile("^(\(.*\) )?(.*)$")

wn = parse_wordnet("wn.xml")

with open("ntu-changes2.csv", "w") as outp:
    with open("ntu-def-changes.csv") as inp:
        inp.readline()
        r = csv.reader(inp)
        w = csv.writer(outp)
        for row in r:
            key = row[1]
            old_defn = row[4].strip()
            new_defn = row[5].strip()
            accept = row[7]

            if accept != "TRUE":
                continue

            ss = wn.synset_by_id(key)
            if not ss:
                print("bad ss: " + key)
                continue
            act_def = ss.definitions[0].text.strip()
            m = re.match(defn_re, act_def)
            if m and old_defn == m.group(2) and m.group(1):
                old_defn = m.group(1) + old_defn
                new_defn = m.group(1) + new_defn
             
            if act_def != old_defn:
                w.writerow([row[1], row[4], act_def, row[5]])
                continue

            wn_ss = parse_wordnet("src/wn-%s.xml" % (ss.lex_name))
            with open("src/wn-%s.xml" % (ss.lex_name), "w") as xml:
                wn_ss.synset_by_id(key).definitions[0] = Definition(new_defn)
                wn_ss.to_xml(xml, True)




