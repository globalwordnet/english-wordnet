import yaml
from glob import glob
from collections import defaultdict
import csv
import re

uk_spelling = "86712636-n"
uk_spelling_sense = "british_spelling%1:10:01::"
us_spelling = "87027384-n"
us_spelling_sense = "american_spelling%1:10:01::"
ca_spelling = "80475027-n"
ca_spelling_sense = "canadian_spelling%1:10:01::"
au_spelling = "84746436-n"
au_spelling_sense = "australian_spelling%1:10:01::"
uk_english = "82423757-n"
uk_english_sense = "british_english%1:10:01::"
us_english = "06960241-n"
us_english_sense = "american_english%1:10:01::"

members2ssid = defaultdict(list)
ssid2members = {}
ssid2definition = {}

for file in glob("src/yaml/[nva]*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, entry in data.items():
        ssid2members[ssid] = entry["members"]
        for m in entry["members"]:
           members2ssid[m].append(ssid)
        ssid2definition[ssid] = entry["definition"][0]

ssid_lemma2sense = {}

for file in glob("src/yaml/entries*.yaml"):
    data = yaml.safe_load(open(file))
    for lemma, pos_entry in data.items():
        for pos, entry in pos_entry.items():
            for sense in entry["sense"]:
                ssid_lemma2sense[(sense["synset"], lemma)] = sense["id"]


ubuntu_data = csv.reader(open("us_uk_categorized.csv"))
next(ubuntu_data)
ubuntu_data = list(ubuntu_data)

def print_spelling_change(ssid : str, us_word : str, uk_word : str, ca=False, au=True):
    print(f"add_relation:")
    print(f"  - source: {ssid}")
    print(f"  - source_sense: '{ssid_lemma2sense[(ssid, us_word)]}'")
    print(f"  - relation: exemplifies")
    print(f"  - target: {us_spelling}")
    print(f"  - target_sense: {us_spelling_sense}")
    print(f"add_relation:")
    print(f"  - source: {ssid}")
    print(f"  - source_sense: '{ssid_lemma2sense[(ssid, uk_word)]}'")
    print(f"  - relation: exemplifies")
    print(f"  - target: {uk_spelling}")
    print(f"  - target_sense: {uk_spelling_sense}")
    if ca:
        print(f"add_relation:")
        print(f"  - source: {ssid}")
        print(f"  - source_sense: '{ssid_lemma2sense[(ssid, uk_word)]}'")
        print(f"  - relation: exemplifies")
        print(f"  - target: {ca_spelling}")
        print(f"  - target_sense: {ca_spelling_sense}")
    if au:
        print(f"add_relation:")
        print(f"  - source: {ssid}")
        print(f"  - source_sense: '{ssid_lemma2sense[(ssid, uk_word)]}'")
        print(f"  - relation: exemplifies")
        print(f"  - target: {au_spelling}")
        print(f"  - target_sense: {au_spelling_sense}")
    print("")

# ou/o
print("## ou/o changes")
def apply_changes(key, us_ending, uk_ending, final=True, ca=False, au=True):
    handled = set()
    for row in ubuntu_data:
        if row[2] == key:
            for ssid in members2ssid[row[0]]:
                if row[1] in ssid2members[ssid]:
                    print(f"# {row[0]} => {row[1]} (from Ubuntu)")
                    print_spelling_change(ssid, row[0], row[1],ca=ca,au=au)
                else:
                    print(f"# Not found {row[0]} => {row[1]} (from Ubuntu)")
                    print("# add_entry:")
                    print(f"#  synset: {ssid}")
                    print(f"#  lemma: {row[1]}")
                    print(f"#  pos : n")
                handled.add(ssid)

    if final:
        for ssid, members in ssid2members.items():
            if ssid not in handled:
                for uk_word in members:
                    if uk_word.endswith(uk_ending):
                        us_word = re.sub(f"{uk_ending}$", "us_ending", uk_word)
                        if us_word in members:
                            print(f"# {us_word} => {uk_word} (from search)")
                            print_spelling_change(ssid, us_word, uk_word,ca=ca,au=au)

apply_changes("ou/o", "or", "our",ca=True)

# re/er
print("## re/er changes")
apply_changes("re/or", "er", "re",ca=True)

print("## ce/se changes")
apply_changes("ce/se", "se", "ce",ca=True)

print("## ae/e changes")
apply_changes("ae/e", "e", "ae", final=False)

print("## oe/e changes")
apply_changes("oe/e", "e", "oe", final=False)

print("## ise/ize changes")
apply_changes("ise/ize", "ize", "ise")
apply_changes("", "ization", "isation")
apply_changes("", "izing", "ising")

print("## yse/yze changes")
apply_changes("yse/yze", "yze", "yse")
apply_changes("", "yzation", "ysation")
apply_changes("", "yzing", "ysing")

print("## ogue/og changes")
apply_changes("ogue/og", "og", "ogue",ca=True)

print("## ally/ly changes")
apply_changes("ally/ly", "ly", "ally")

print("## eable/able changes")
apply_changes("eable/able", "able", "eable",au=False)

def apply_other_changes(key):
    for row in ubuntu_data:
        if row[2].startswith(key):
            for ssid in members2ssid[row[0]]:
                if row[1] in ssid2members[ssid]:
                    print(f"# {row[0]} => {row[1]} (from Ubuntu; {row[2]})")
                    print_spelling_change(ssid, row[0], row[1])
                else:
                    print(f"# Not found {row[0]} => {row[1]} (from Ubuntu; {row[2]})")
                    print("# add_entry:")
                    print(f"#  synset: {ssid}")
                    print(f"#  lemma: {row[1]}")
                    print(f"#  pos : n")
                    print("")



print("## hyphen changes")
apply_other_changes("hyphen")

print("## double changes")
apply_other_changes("double")

print("## Other changes")
apply_other_changes("other")

def print_semantic_change(ssid : str, us_word : str, uk_word : str, ca=False, au=True):
    print(f"# Definition: {ssid2definition[ssid]}")
    print(f"add_relation:")
    print(f"  - source: {ssid}")
    print(f"  - source_sense: '{ssid_lemma2sense[(ssid, us_word)]}'")
    print(f"  - relation: exemplifies")
    print(f"  - target: {us_english}")
    print(f"  - target_sense: {us_english_sense}")
    print(f"add_relation:")
    print(f"  - source: {ssid}")
    print(f"  - source_sense: '{ssid_lemma2sense[(ssid, uk_word)]}'")
    print(f"  - relation: exemplifies")
    print(f"  - target: {uk_english}")
    print(f"  - target_sense: {uk_english_sense}")
    print("")


def apply_semantic_changes(key):
    for row in ubuntu_data:
        if row[2].startswith(key):
            for ssid in members2ssid[row[0]]:
                if row[1] in ssid2members[ssid]:
                    print(f"# {row[0]} => {row[1]} (from Ubuntu; {row[2]})")
                    print_semantic_change(ssid, row[0], row[1])
                else:
                    print(f"# Not found {row[0]} => {row[1]} (from Ubuntu; {row[2]})")
                    print("# add_entry:")
                    print(f"#  synset: {ssid}")
                    print(f"#  lemma: {row[1]}")
                    print(f"#  pos : n")
                    print("")



print("## Semantic changes")
apply_semantic_changes("semantic")
