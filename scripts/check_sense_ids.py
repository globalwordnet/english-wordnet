# This script fixes sense IDs to be strictly increasing
# It won't be needed after 2021 release
from wordnet import *

wn = parse_wordnet("wn.xml")

for synset in wn.synsets:
    members = wn.members_by_id(synset.id)
    senses = [
        [sense for entry in wn.entry_by_lemma(member)
         for sense in wn.entry_by_id(entry).senses
         if sense.synset == synset.id][0]
        for member in members]
    senses = sorted(senses, key=lambda s: s.id[-2:])
    actual = sorted([s.id[-2:] for s in senses])
    if actual[0] == '00':
        goal = ["%02d" % i for i in range(len(senses))]
    else:
        goal = ["%02d" % (i + 1) for i in range(len(senses))]
    if goal != actual:
        for (sense, g) in zip(senses, goal):
            if sense.id[-2:] != g:
                print("sed -i 's/%s/%s/' src/xml/*.xml" %
                      (sense.id, sense.id[:-2] + g))
