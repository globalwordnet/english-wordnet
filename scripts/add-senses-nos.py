# This is the script used to add sense numberings to the senses
from glob import glob
import re

indexes = {}


def load_indexes(index):
    for line in open(index).readlines():
        if not line.startswith(" "):
            elems = line.split()
            syn_cnt = int(elems[2])
            if elems[1] == "a":
                indexes["%s-s" % (elems[0])] = elems[-syn_cnt:]
            indexes["%s-%s" % (elems[0], elems[1])] = elems[-syn_cnt:]
    print("Loaded index %s" % index)


# Manual cases
# graeco-roman_wrestling-n
# pasture_land-n
# graeco-roman_architecture-n
# terracotta-n

def main():
    r = re.compile(".*<Sense id=\"oewn-(.*)-([nvars])-(\\d{8})-(\\d{2})\"(.*)>")
    for wn31_part in glob("src/xml/wn31-*.xml"):
        with open("%s.new" % wn31_part, "w") as out:
            for line in open(wn31_part).readlines():
                m = r.match(line)
                if m:
                    lemma = m.group(1).replace(
                        "-ap-", "'").replace("-sl-", "/").replace("-lb-", "(").replace("-rb-", ")")
                    if lemma.endswith("(a)") or lemma.endswith("(p)"):
                        lemma = lemma[:-3]
                    if lemma.endswith("(ip)"):
                        lemma = lemma[:-4]
                    pos = m.group(2)
                    synset = m.group(3)
                    lemma_pos = "%s-%s" % (lemma.lower(), pos)
                    if lemma_pos in indexes:
                        out.write(
                            "      <Sense id=\"oewn-%s-%s-%s-%s\" n=\"%d\"%s>\n" %
                            (m.group(1),
                             m.group(2),
                                m.group(3),
                                m.group(4),
                                indexes[lemma_pos].index(synset),
                                m.group(5)))
                    else:
                        out.write(line)
                else:
                    out.write(line)


if __name__ == "__main__":
    load_indexes("index.noun")
    load_indexes("index.adj")
    load_indexes("index.verb")
    load_indexes("index.adv")
    main()
