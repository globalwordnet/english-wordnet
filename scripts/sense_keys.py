from wordnet import *
from glob import glob
import re
from sys import exit

lex_filenums = {
    "adj.all": 0,
    "adj.pert": 1,
    "adv.all": 2,
    "noun.Tops": 3,
    "noun.act": 4,
    "noun.animal": 5,
    "noun.artifact": 6,
    "noun.attribute": 7,
    "noun.body": 8,
    "noun.cognition": 9,
    "noun.communication": 10,
    "noun.event": 11,
    "noun.feeling": 12,
    "noun.food": 13,
    "noun.group": 14,
    "noun.location": 15,
    "noun.motive": 16,
    "noun.object": 17,
    "noun.person": 18,
    "noun.phenomenon": 19,
    "noun.plant": 20,
    "noun.possession": 21,
    "noun.process": 22,
    "noun.quantity": 23,
    "noun.relation": 24,
    "noun.shape": 25,
    "noun.state": 26,
    "noun.substance": 27,
    "noun.time": 28,
    "verb.body": 29,
    "verb.change": 30,
    "verb.cognition": 31,
    "verb.communication": 32,
    "verb.competition": 33,
    "verb.consumption": 34,
    "verb.contact": 35,
    "verb.creation": 36,
    "verb.emotion": 37,
    "verb.motion": 38,
    "verb.perception": 39,
    "verb.possession": 40,
    "verb.social": 41,
    "verb.stative": 42,
    "verb.weather": 43,
    "adj.ppl": 44,
    "contrib.colloq": 50,
    "contrib.plwn": 51}

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


def get_sense_key(wn, e, s):
    """Calculate the sense key for a sense of an entry"""
    ss = wn.synset_by_id(s.synset)
    lemma = (e.lemma.written_form
        .replace(" ", "_")
        .replace("&apos", "'")
        .lower())
    ss_type = ss_types[ss.part_of_speech]
    lex_filenum = lex_filenums[ss.lex_name]
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

KEY_PREFIX_LEN = 5 # = len("oewn-")

def escape_sense_key(s : str) -> str:
    """
    Escape a sense key for OEWN
    """
    return (s.replace("-", "--")
            .replace("'", "-apos-")
            .replace("!", "-excl-").replace("#", "-num-")
            .replace("$", "-dollar-").replace("%", "-percnt-")
            .replace("&", "-amp-").replace("(", "-lpar-")
            .replace(")", "-rpar-").replace("*", "-ast-")
            .replace("+", "-plus-").replace(",", "-comma-")
            .replace("/", "-sol-").replace("{", "-lbrace-")
            .replace("|", "-vert-").replace("}", "-rbrace-")
            .replace("~", "-tilde-").replace("¢", "-cent-")
            .replace("£", "-pound-").replace("§", "-sect-")
            .replace("©", "-copy-").replace("®", "-reg-")
            .replace("°", "-deg-").replace("´", "-acute-")
            .replace("¶", "-para-").replace("º", "-ordm-")
            .replace(":", "-colon-"))


def unescape_sense_key(s : str) -> str:
    """
    Unescape a sense key from OEWN
    """
    return (s.replace("-apos-", "'")
            .replace("-colon-", ":")
            .replace("-excl-", "!").replace("-num-", "#")
            .replace("-dollar-", "$").replace("-percnt-", "%")
            .replace("-amp-", "&").replace("-lpar-", "(")
            .replace("-rpar-", ")").replace("-ast-", "*")
            .replace("-plus-", "+").replace("-comma-", ",")
            .replace("-sol-", "/").replace("-lbrace-", "{")
            .replace("-vert-", "|").replace("-rbrace-", "}")
            .replace("-tilde-", "~").replace("-cent-", "¢")
            .replace("-pound-", "£").replace("-sect-", "§")
            .replace("-copy-", "©").replace("-reg-", "®")
            .replace("-deg-", "°").replace("-acute-", "´")
            .replace("-para-", "¶").replace("-ordm-", "º")
            .replace("--", "-"))

def map_sense_key(sk):
    """
    Maps a sense key into an XML-compatible sense key
    """
    if "%" in sk:
        e = sk.split("%")
        if len(e) > 2:
            lemma = "%".join(e[:-1])
            info = e[-1]
        else:
            lemma = e[0]
            info = e[1]
        lemma = escape_sense_key(lemma)
        return ("oewn-" + lemma +
            "__" + info.replace("_","-sp-").replace(":","."))
    else:
        sk = escape_sense_key(sk)
        return "oewn-" + sk

def unmap_sense_key(sk):
    """
    Maps an XML-compatible sense key back to a normal sense key
    """
    if "__" in sk:
        e = sk.split("__")
        oewn_key = e[0][KEY_PREFIX_LEN:]
        r = "__".join(e[1:])
        return (unescape_sense_key(oewn_key) + "%" +
                r.replace("-sp-", "_").replace(".", ":"))
    else: 
        return unescape_sense_key(sk[KEY_PREFIX_LEN:])

