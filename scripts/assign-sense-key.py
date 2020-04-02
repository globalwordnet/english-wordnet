from wordnet import *
import change_manager
from glob import glob
import re
from sys import exit

lex_filenums = {
        "src/wn-adj.all.xml": 0,
        "src/wn-adj.pert.xml": 1,
        "src/wn-adv.all.xml": 2,
        "src/wn-noun.Tops.xml": 3,
        "src/wn-noun.act.xml": 4,
        "src/wn-noun.animal.xml": 5,
        "src/wn-noun.artifact.xml": 6,
        "src/wn-noun.attribute.xml": 7,
        "src/wn-noun.body.xml": 8,
        "src/wn-noun.cognition.xml": 9,
        "src/wn-noun.communication.xml": 10,
        "src/wn-noun.event.xml": 11,
        "src/wn-noun.feeling.xml": 12,
        "src/wn-noun.food.xml": 13,
        "src/wn-noun.group.xml": 14,
        "src/wn-noun.location.xml": 15,
        "src/wn-noun.motive.xml": 16,
        "src/wn-noun.object.xml": 17,
        "src/wn-noun.person.xml": 18,
        "src/wn-noun.phenomenon.xml": 19,
        "src/wn-noun.plant.xml": 20,
        "src/wn-noun.possession.xml": 21,
        "src/wn-noun.process.xml": 22,
        "src/wn-noun.quantity.xml": 23,
        "src/wn-noun.relation.xml": 24,
        "src/wn-noun.shape.xml": 25,
        "src/wn-noun.state.xml": 26,
        "src/wn-noun.substance.xml": 27,
        "src/wn-noun.time.xml": 28,
        "src/wn-verb.body.xml": 29,
        "src/wn-verb.change.xml": 30,
        "src/wn-verb.cognition.xml": 31,
        "src/wn-verb.communication.xml": 32,
        "src/wn-verb.competition.xml": 33,
        "src/wn-verb.consumption.xml": 34,
        "src/wn-verb.contact.xml": 35,
        "src/wn-verb.creation.xml": 36,
        "src/wn-verb.emotion.xml": 37,
        "src/wn-verb.motion.xml": 38,
        "src/wn-verb.perception.xml": 39,
        "src/wn-verb.possession.xml": 40,
        "src/wn-verb.social.xml": 41,
        "src/wn-verb.stative.xml": 42,
        "src/wn-verb.weather.xml": 43,
        "src/wn-adj.ppl.xml": 44,
        "src/wn-contrib.colloq.xml": 50,
        "src/wn-contrib.plwn.xml": 51 }

ss_types = {
        PartOfSpeech.NOUN: 1,
        PartOfSpeech.VERB: 2,
        PartOfSpeech.ADJECTIVE: 3,
        PartOfSpeech.ADVERB: 4,
        PartOfSpeech.ADJECTIVE_SATELLITE: 5
        }

sense_id_lex_id = re.compile(".*%\d:\d\d:(\d\d):.*")
id_lemma = re.compile("ewn-(.*)-[as]-\d{8}-\d{2}")

def gen_lex_id(swn, e, s):
    max_id = 0
    unseen = 1
    seen = False
    for s2 in e.senses:
        if s2.sense_key:
            m = re.match(sense_id_lex_id, s2.sense_key)
            max_id = max(max_id, int(m.group(1)))
        else:
            if not seen:
                if s2.id == s.id:
                    seen = True
                else:
                    unseen += 1
    return max_id + unseen


def sense_for_entry_synset_id(wn, ss_id, lemma):
    return [
            s for e in wn.entry_by_lemma(lemma)
                for s in wn.entry_by_id(e).senses
                if s.synset == ss_id][0]

def get_head_word(wn, s):
    ss = wn.synset_by_id(s.synset)
    srs = [r for r in ss.synset_relations if r.rel_type == SynsetRelType.SIMILAR]
    if len(srs) != 1:
        print(srs)
        print(s.id)
        print("Could not deduce target of satellite")
    else:
        s2s = [sense_for_entry_synset_id(wn, srs[0].target, m) for m in wn.members_by_id(srs[0].target)]
        s2s = sorted(s2s, key = lambda s2: s2.id[-2:])
        s2 = s2s[0]

        if not re.match(id_lemma, s2.id):
            print(s2.id)
        entry_id = re.match(id_lemma, s2.id).group(1)
        if s2.sense_key:
            return entry_id, re.match(sense_id_lex_id, s2.sense_key).group(1)
        else:
            print("No sense key for target of satellite! Marking as 99... please fix for " + s.id)
            return entry_id, "99"
    print("Failed to find target for satellite synset")
    exit(-1)
        
            


def assign_keys(wn, wn_file):
    swn = parse_wordnet(wn_file)
    for e in swn.entries:
        for s in e.senses:
            if not s.sense_key:
                lemma = e.lemma.written_form.replace(" ", "_").replace("&apos","'").lower()
                ss_type = ss_types[e.lemma.part_of_speech]
                lex_filenum = lex_filenums[wn_file]
                lex_id = gen_lex_id(swn, e, s)
                if e.lemma.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE:
                    head_word, head_id = get_head_word(wn, s)
                else:
                    head_word = ""
                    head_id = ""
                s.sense_key = "%s%%%d:%02d:%02d:%s:%s" % (lemma, ss_type, lex_filenum,
                        lex_id, head_word, head_id)
    with open(wn_file, "w") as outp:
        swn.to_xml(outp, True)

if __name__ == "__main__":
    wn = change_manager.load_wordnet()
    for f in glob ("src/wn-*.xml"):
        assign_keys(wn, f)
