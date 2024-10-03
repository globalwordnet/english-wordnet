from glob import glob
import yaml
import csv

hyps = {}
defs = {}
members = {}
lexfiles = {}

for file in glob("src/yaml/verb.*.yaml"):
    lexfile = file[14:-5]
    data = yaml.safe_load(open(file))
    for ssid, d in data.items():
        lexfiles[ssid] = lexfile
        if "hypernym" in d:
            hyps[ssid] = d["hypernym"]
        if "definition" in d:
            defs[ssid] = d["definition"][0]
        if "members" in d:
            members[ssid] = d["members"]

not_cross = 0
cross = 0

for ssid, hs in hyps.items():
    for h in hs:
        if lexfiles[ssid] != lexfiles[h]:
            cross += 1
        else:
            not_cross += 1

print(f"Cross-lex hypernyms: {cross}")
print(f"Non-cross-lex hypernyms: {not_cross}")

