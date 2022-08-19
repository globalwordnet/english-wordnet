from wordnet import *
from glob import glob
import re
from sys import exit
from wordnet_yaml import unmap_sense_key

lex_filenums = {
    "src/xml/wn-adj.all.xml": 0,
    "src/xml/wn-adj.pert.xml": 1,
    "src/xml/wn-adv.all.xml": 2,
    "src/xml/wn-noun.Tops.xml": 3,
    "src/xml/wn-noun.act.xml": 4,
    "src/xml/wn-noun.animal.xml": 5,
    "src/xml/wn-noun.artifact.xml": 6,
    "src/xml/wn-noun.attribute.xml": 7,
    "src/xml/wn-noun.body.xml": 8,
    "src/xml/wn-noun.cognition.xml": 9,
    "src/xml/wn-noun.communication.xml": 10,
    "src/xml/wn-noun.event.xml": 11,
    "src/xml/wn-noun.feeling.xml": 12,
    "src/xml/wn-noun.food.xml": 13,
    "src/xml/wn-noun.group.xml": 14,
    "src/xml/wn-noun.location.xml": 15,
    "src/xml/wn-noun.motive.xml": 16,
    "src/xml/wn-noun.object.xml": 17,
    "src/xml/wn-noun.person.xml": 18,
    "src/xml/wn-noun.phenomenon.xml": 19,
    "src/xml/wn-noun.plant.xml": 20,
    "src/xml/wn-noun.possession.xml": 21,
    "src/xml/wn-noun.process.xml": 22,
    "src/xml/wn-noun.quantity.xml": 23,
    "src/xml/wn-noun.relation.xml": 24,
    "src/xml/wn-noun.shape.xml": 25,
    "src/xml/wn-noun.state.xml": 26,
    "src/xml/wn-noun.substance.xml": 27,
    "src/xml/wn-noun.time.xml": 28,
    "src/xml/wn-verb.body.xml": 29,
    "src/xml/wn-verb.change.xml": 30,
    "src/xml/wn-verb.cognition.xml": 31,
    "src/xml/wn-verb.communication.xml": 32,
    "src/xml/wn-verb.competition.xml": 33,
    "src/xml/wn-verb.consumption.xml": 34,
    "src/xml/wn-verb.contact.xml": 35,
    "src/xml/wn-verb.creation.xml": 36,
    "src/xml/wn-verb.emotion.xml": 37,
    "src/xml/wn-verb.motion.xml": 38,
    "src/xml/wn-verb.perception.xml": 39,
    "src/xml/wn-verb.possession.xml": 40,
    "src/xml/wn-verb.social.xml": 41,
    "src/xml/wn-verb.stative.xml": 42,
    "src/xml/wn-verb.weather.xml": 43,
    "src/xml/wn-adj.ppl.xml": 44,
    "src/xml/wn-contrib.colloq.xml": 50,
    "src/xml/wn-contrib.plwn.xml": 51}

ss_types = {
    PartOfSpeech.NOUN: 1,
    PartOfSpeech.VERB: 2,
    PartOfSpeech.ADJECTIVE: 3,
    PartOfSpeech.ADVERB: 4,
    PartOfSpeech.ADJECTIVE_SATELLITE: 5
}

sense_id_lex_id = re.compile(".*%\\d:\\d\\d:(\\d\\d):.*")

def gen_lex_id(e, s):
    max_id = 0
    unseen = 1
    seen = False
    for s2 in e.senses:
        if s2.id:
            m = re.match(sense_id_lex_id, unmap_sense_key(s2.id))
            max_id = max(max_id, int(m.group(1)))
        else:
            if not seen:
                if s2.id == s.id:
                    seen = True
                else:
                    unseen += 1
    return max_id + unseen


def extract_lex_id(sense_key):
    return int(re.match(sense_id_lex_id, sense_key).group(1))


def sense_for_entry_synset_id(wn, ss_id, lemma):
    return [
        s for e in wn.entry_by_lemma(lemma)
        for s in wn.entry_by_id(e).senses
        if s.synset == ss_id][0]


def get_head_word(wn, s):
    ss = wn.synset_by_id(s.synset)
    # The hack here is we don't care about satellites in non-Princeton sets
    srs = [r for r in ss.synset_relations if r.rel_type ==
           SynsetRelType.SIMILAR and not r.target.startswith("oewn-9") and not r.target.startswith("oewn-8")]
    if len(srs) != 1:
        print([r.target for r in srs])
        print(s.id)
        print("Could not deduce target of satellite")
    else:
        tss = wn.synset_by_id(srs[0].target)
        entry = wn.entry_by_id(tss.members[0])
        s2 = [sense for sense in entry.senses
                if sense.synset == srs[0].target][0]

        entry_id = unmap_sense_key(s2.id)
        entry_id = entry_id[:entry_id.index("%")]
        if s2.id:
            return entry_id, re.match(sense_id_lex_id, unmap_sense_key(s2.id)).group(1)
        else:
            print(
                "No sense key for target of satellite! Marking as 99... please fix for " +
                s.id)
            return entry_id, "99"
    print("Failed to find target for satellite synset")
    exit(-1)


def get_sense_key(wn, e, s, wn_file):
    """Calculate the sense key for a sense of an entry"""
    ss = wn.synset_by_id(s.synset)
    lemma = e.lemma.written_form.replace(
        " ", "_").replace(
        "&apos", "'").replace("+", "-pl-").lower()
    ss_type = ss_types[ss.part_of_speech]
    if not wn_file.startswith("src/xml/wn-"):
        wn_file = f"src/xml/wn-{wn_file}.xml"
    lex_filenum = lex_filenums[wn_file]
    if s.id:
        lex_id = extract_lex_id(unmap_sense_key(s.id))
    else:
        lex_id = gen_lex_id(e, s)
    if ss.part_of_speech == PartOfSpeech.ADJECTIVE_SATELLITE:
        head_word, head_id = get_head_word(wn, s)
    else:
        head_word = ""
        head_id = ""
    return "%s%%%d:%02d:%02d:%s:%s" % (lemma, ss_type, lex_filenum,
                                       lex_id, head_word, head_id)
