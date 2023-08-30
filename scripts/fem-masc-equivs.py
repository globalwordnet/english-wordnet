import yaml
import csv
from glob import glob

entry2ssid = {}

ssid2def = {}

hyps = {}

lexfiles = {}

for file in glob("src/yaml/noun.*.yaml"):
    data = yaml.safe_load(open(file))
    lf = file[9:-5]
    for ssid, entry in data.items():
        lexfiles[ssid] = lf
        for member in entry["members"]:
            if member not in entry2ssid:
                entry2ssid[member] = set()
            entry2ssid[member].add(ssid)
        ssid2def[ssid] = entry["definition"][0]
        if "hypernym" in entry:
            hyps[ssid] = entry["hypernym"]

reader = csv.reader(open("fem-masc-equivs.csv"))

next(reader)

new_rows = []
syn_rows = []
hyp_rows = []
other_rows = []

for row in reader:
    if row[3] == "NEW":
        new_rows.append(row)
    elif row[1] == row[3]:
        syn_rows.append(row)
    elif row[1] in hyps and row[3] in hyps[row[1]]:
        hyp_rows.append(row)
    else:
        other_rows.append(row)

not_gender_neutral = set(["cowgirl","policewoman","barmaid","airwoman","horsewoman","newswoman","madwoman","Scotchwoman","Scotswoman","stateswoman","oarswoman","outdoorswoman"])

def masculinize_definition(defn):
    if defn.startswith("a man "):
        return defn
    elif defn.startswith("a "):
        return "a male " + defn[2:]
    elif defn.startswith("an "):
        return "a male " + defn[3:]
    elif defn.startswith("someone "):
        return "a male " + defn[8:]
    elif defn.startswith("the "):
        return "the male " + defn[4:]
    else:
        return "male " + defn

def feminize_definition(defn):
    if defn.startswith("a man "):
        return "a woman" + defn[5:]
    elif defn.startswith("a "):
        return "a female " + defn[2:]
    elif defn.startswith("an "):
        return "a female " + defn[3:]
    elif defn.startswith("someone "):
        return "a female " + defn[8:]
    elif defn.startswith("the "):
        return "the female " + defn[4:]
    else:
        return "female " + defn

masc_done = set()

print("# Feminine to gender-neutral")
for hyp_row in hyp_rows:
    print(f"# {hyp_row[0]} => {hyp_row[2]}")
    print(f"- add_relation:")
    print(f"    source: {hyp_row[3]}")
    print(f"    target: {hyp_row[1]}")
    print(f"    relation: feminine")
    if ssid2def[hyp_row[3]].startswith("a man "):
        print(f"- change_definition:")
        print(f"    synset: {hyp_row[3]}")
        print(f"    definition: \"a person{ssid2def[hyp_row[3]][5:]}\"")
    if hyp_row[0] in not_gender_neutral:
        if hyp_row[3] not in masc_done:
            print(f"- add_synset:")
            print(f"    definition: \"{masculinize_definition(ssid2def[hyp_row[3]])}\"")
            print(f"    lexfile: {lexfiles[hyp_row[3]]}")
            print(f"    pos: n")
            print(f"    lemmas: []")
            print(f"- add_relation:")
            print(f"    source: {hyp_row[3]}")
            print(f"    target: last")
            print(f"    relation: masculine")
            print(f"- add_relation:")
            print(f"    source: last")
            print(f"    target: {hyp_row[3]}")
            print(f"    relation: hypernym")
            masc_done.add(hyp_row[3])
        else:
            print("# ATT: check above entry is the same synset")
        print(f"- move_entry:")
        print(f"    synset: {hyp_row[3]}")
        print(f"    lemma: {hyp_row[2]}")
        print(f"    target_synset: last")

print("# in same synset")
for row in syn_rows:
    print(f"# {row[0]} => {row[2]}")
    print(f"- add_synset:")
    print(f"    definition: \"{feminize_definition(ssid2def[row[1]])}\"")
    print(f"    lexfile: {lexfiles[row[1]]}")
    print(f"    pos: n")
    print(f"    lemmas: []")
    print(f"- move_entry:")
    print(f"    synset: {row[1]}")
    print(f"    lemma: {row[0]}")
    print(f"    target_synset: last")
    print(f"- add_relation:")
    print(f"    source: {row[1]}")
    print(f"    target: last")
    print(f"    relation: feminine")
    print(f"- add_relation:")
    print(f"    target: {row[1]}")
    print(f"    source: last")
    print(f"    relation: hypernym")
    print(f"- add_synset:")
    print(f"    definition: \"{masculinize_definition(ssid2def[row[1]])}\"")
    print(f"    lexfile: {lexfiles[row[1]]}")
    print(f"    pos: n")
    print(f"    lemmas: []")
    print(f"- move_entry:")
    print(f"    synset: {row[1]}")
    print(f"    lemma: {row[2]}")
    print(f"    target_synset: last")
    print(f"- add_relation:")
    print(f"    source: {row[1]}")
    print(f"    target: last")
    print(f"    relation: masculine")
    print(f"- add_relation:")
    print(f"    target: {row[1]}")
    print(f"    source: last")
    print(f"    relation: hypernym")
     

print("# masculine to feminine")
for row in other_rows:
    print(f"# {row[0]} => {row[2]}")
    print(f"- add_relation:")
    print(f"    source: {row[1]}")
    print(f"    target: {row[3]}")
    print(f"    relation: masculine")
    print(f"- add_relation:")
    print(f"    target: {row[1]}")
    print(f"    source: {row[3]}")
    print(f"    relation: feminine")

print("# new masculine terms to be introduced")
new_masc = [
    ("agony uncle","a male newspaper columnist who answers questions and offers advice on personal problems to people who write in","agony aunt"),
    ("air host","a male steward on an airplane","air hostess"),
    ("baby papa","the father of at least one of your children","baby mama"),
    ("charman","a human male employed to do housework","charwoman"),
    ("coquet","a seductive man who uses his sex appeal to exploit women","coquette"),
    ("cover boy","a very pretty boy who works as a photographer's model","cover girl"),
    ("fanboy","A male fan who is obsessive about a particular subject (especially, someone or something in popular entertainment media","fangirl"),
    ("first gentleman","the husband of a chief executive","first lady"),
    ("flower boy","a young boy who carries flowers in a (wedding) procession","flower girl"),
    ("boy Friday","a male assistant who has a range of duties","girl Friday"),
    ("golf widower","a husband who is left alone much of the time because his wife is playing golf","golf widow"),
    ("kept man","an adulterous man; a man who has an ongoing extramarital sexual relationship with a woman","kept woman"),
    ("needleman","a man who makes or mends dresses","needlewoman"),
    ("king","the husband or widower of a queen","queen"),
    ("seductor","a man who seduces","seductress"),
    #("sempster","a man who makes or mends dresses","sempstress"),
    ("showboy","a man who dances in a chorus line","showgirl"),
    ("superdad","an informal term for a father who can combine childcare and full-time employment","supermom"),
    ("trophy husband","a husband who is an attractive young man; seldom the first husband of an affluent older woman","trophy wife"),
    ("lollipop man","a man hired to help children cross a road safely near a school","lollipop lady"),
#    ("lollipop man","a man hired to help children cross a road safely near a school","lollipop woman"),
    ("loose man","a male adulterer","loose woman"),
    ("cleaning man","a human female employed to do housework","cleaning lady"),
#    ("cleaning man","a human female employed to do housework","cleaning woman"),
    ("washman","a working woman who takes in washing","washwoman"),
    ("wonder man","a man who can be a succesful husband and care for his children","wonder woman") ]



for row in new_rows:
    for new_masc_term, new_masc_def, _ in [nm for nm in new_masc if nm[2] == row[0]]:
        print(f"- add_synset:")
        print(f"    definition: \"{new_masc_def}\"")
        print(f"    lexfile: {lexfiles[row[1]]}")
        print(f"    pos: n")
        print(f"    lemmas:")
        print(f"      - {new_masc_term}")
        print(f"- add_relation:")
        print(f"    source: last")
        print(f"    target: {row[1]}")
        print(f"    relation: feminine")
        print(f"- add_relation:")
        print(f"    source: {row[1]}")
        print(f"    target: last")
        print(f"    relation: masculine")
        print(f"- add_relation:")
        print(f"     source: last")
        print(f"     target: {hyps[row[1]][0]}")
        print(f"     relation: hypernym")
        if new_masc_term == "needleman":
            print(f"- add_entry:")
            print(f"    synset: last")
            print(f"    lemma: sempster")
            print(f"    pos: n")

gender_neutral_terms = {
        "09879912-n": "blond person",
        "09884685-n": "bondsperson",
        "10129754-n": "freedperson",
        "10130792-n": "freeperson",
        "10406317-n": "outdoorsperson",
        "10821647-n": "yachtsperson"
        }

for ssid, gnt in gender_neutral_terms.items():
    print(f"- add_entry:")
    print(f"    synset: {ssid}")
    print(f"    lemma: {gnt}")
    print(f"    pos: n")
