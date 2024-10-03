from glob import glob
import yaml
import csv

new_hyps = {}
defs = {}
members = {}

for file in glob("src/yaml/verb.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, d in data.items():
        if "hypernym" in d:
            new_hyps[ssid] = d["hypernym"]
        if "definition" in d:
            defs[ssid] = d["definition"][0]
        if "members" in d:
            members[ssid] = d["members"]

old_hyps = {}

for file in glob("/home/jmccrae/scratch/english-wordnet/src/yaml/verb.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, d in data.items():
        if "hypernym" in d:
            old_hyps[ssid] = d["hypernym"]

with open("oewn-verb-hypernyms.csv", "w") as f:
    out = csv.writer(f)
    out.writerow(["Synset ID", "Definition", "Members", "Previous Hypernyms", "New Hypernym ID", "New Hypernym Definition", "New Hypernym Members"])
    for ssid in new_hyps:
        if old_hyps.get(ssid, []) != new_hyps[ssid]:
            for hyp in new_hyps[ssid]:
                out.writerow([ssid, defs[ssid], 
                              ", ".join(members.get(ssid, [])), 
                              ", ".join(old_hyps.get(ssid, [])), hyp, defs.get(hyp, ""), 
                              ", ".join(members.get(hyp, []))])


