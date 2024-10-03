from glob import glob
import yaml
import csv

hyps = {}
defs = {}
members = {}

for file in glob("src/yaml/verb.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, d in data.items():
        if "hypernym" in d:
            hyps[ssid] = d["hypernym"]
        if "definition" in d:
            defs[ssid] = d["definition"][0]
        if "members" in d:
            members[ssid] = d["members"]

with open("oewn-verb-copula-hypernyms.csv", "w") as f:
    out = csv.writer(f)
    out.writerow(["Synset ID", "Definition", "Members"])
    for ssid, h in hyps.items():
        if "02610777-v" in h:
            out.writerow([ssid, defs[ssid], ", ".join(members.get(ssid, []))])


