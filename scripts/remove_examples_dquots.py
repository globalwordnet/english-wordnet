import wordnet
import change_manager
from merge import wn_merge

#wn_merge()
wn = change_manager.parse_wordnet("wn.xml")

for synset in wn.synsets:
    synset.examples = [
            wordnet.Example(ex.text[1:-1], ex.source) 
            if ex.text.startswith("\"") and ex.text.endswith("\"")
            else ex
            for ex in synset.examples]


change_manager.save(wn)
