import csv
from wordnet import *

def escape_lemma(l):
    return l.replace(" ", "_").replace("'","-ap-").replace("/","-sl-").replace("(","-lp-").replace(")","-rp-").replace(",","-cm-")

def map_target(tid):
    if tid.startswith("wn31-"):
        return "ewn-" + tid[5:]
    elif tid.startswith("pl-"):
        return  "ewn-92%06d-n" % (int(tid[3:]))
    else:
        print("Unrecognized target: " + tid)
        sys.exit(-1)

def map_rel(r):
    if r == "fuzzynym":
        return SynsetRelType.ALSO
    if r == "has_domain_usage":
        return SynsetRelType.IS_EXEMPLIFIED_BY
    return SynsetRelType(r)

def map_defn(d):
    example = []
    wiki_defn = []
    d = d.replace("\n", " ").replace("[##P ]", "")
    d = re.sub("{##L:.*?}", "", d)
    d = d.replace("{##:L}", "")
    while "##P" in d:
        m = re.match("^(.*) \[##PP?: ?(.*)\]", d)
        if not m:
            print("x" + d)
        example.append(m.group(2))
        d = m.group(1)
    while "##W" in d:
        m = re.match("^(.*) \[##W: ?(.*)\]", d)
        if not m:
            print("w" + d)
        wiki_defn.append(m.group(2))
        d = m.group(1)


    if d.startswith("##D: "):
        d = d[5:]
    return d, example, wiki_defn


all_targets = set()
with open("enwordnet-validate.csv") as csvfile:
    csvfile.readline() # discard header
    reader = csv.reader(csvfile)
    
    for row in reader:
        plwn_id = row[0]
        all_targets.add(map_target(plwn_id))

with open("enwordnet-validate.csv") as csvfile:
    new_wn = Lexicon("ewn", "English WordNet", "en", "john@mccr.ae",
            "https://wordnet.princeton.edu/license-and-commercial-use", "2019",
            "https://github.com/globalwordnet/english-wordnet")
    all_wn = parse_wordnet("wn.xml")
    csvfile.readline() # discard header
    reader = csv.reader(csvfile)

    sense_no = {}

    for row in reader:
        if row[5] == "TRUE":
            plwn_id = row[0]
            defn = row[1]
            lemmas = row[2].split(";")
            pos = row[3]
            relations = row[4].split(";")
            new_defn = row[7]

            ssno = "92%06d" % (int(plwn_id[3:]))

            for n, lemma in enumerate(lemmas):
                if re.match("^[A-Za-z0-9 \-'.\(\)/,]+$", lemma):
                    entry_id = "ewn-%s-%s" % (escape_lemma(lemma), pos) 
                    if not new_wn.entry_by_id(entry_id):
                        e = LexicalEntry(entry_id)
                        e.set_lemma(Lemma(lemma, PartOfSpeech(pos)))
                        new_wn.add_entry(e)
                        all_e = all_wn.entry_by_id(entry_id)
                        if all_e:
                            sense_no[entry_id] = len(all_e.senses) + 1
                        else:
                            sense_no[entry_id] = 1 
                    else:
                        e = new_wn.entry_by_id(entry_id)
                        sense_no[entry_id] += 1
                    e.add_sense(Sense(
                        id = "ewn-%s-%s-%s-%02d" % (escape_lemma(lemma), pos,
                            ssno, n),
                        synset = "ewn-%s-%s" % (ssno, pos),
                        n = sense_no[entry_id],
                        sense_key = None))
                else:
                    sys.stderr.write("Non-ASCII lemma: " + lemma + "\n")
            ss = Synset(
               id = "ewn-%s-%s" % (ssno, pos),
               ili = "in",
               part_of_speech = PartOfSpeech(pos),
               lex_name = None)
            new_wn.add_synset(ss)
            if new_defn:
                ss.add_definition(Definition(new_defn))
            else:
                defn, examples, wiki_defns = map_defn(defn)
                ss.add_definition(Definition(defn))
                for example in examples:
                    ss.add_example(Example(example))
                for wiki_defn in wiki_defns:
                    d = Example(wiki_defn)
                    d.source = "https://en.wikipedia.org"
                    ss.add_example(d)

            for rel in relations:
                if rel:
                    target = map_target(rel.split("=")[1])
                    if target in all_targets or all_wn.synset_by_id(target):
                        ss.add_synset_relation(SynsetRelation(
                            target,
                            map_rel(rel.split("=")[0])))
                    else:
                        print(rel.split("=")[0] + " => " + target)

    with open("src/wn-contrib.wroclaw.xml", "w") as outp:
        new_wn.to_xml(outp, True)
