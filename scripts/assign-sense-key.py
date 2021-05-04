from wordnet import *
import change_manager
from glob import glob
import re
from sys import exit
import sense_keys


if __name__ == "__main__":
    wn = change_manager.load_wordnet()
    for e in wn.entries:
        for s in e.senses:
            if not s.sense_key:
                s.sense_key = sense_keys.get_sense_key(wn, e, s, 
                        wn.synset_by_id(s.synset).lex_name)
    change_manager.save(wn)
