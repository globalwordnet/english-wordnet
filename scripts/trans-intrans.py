import yaml
from glob import glob
import csv

synsets = set()

for file in glob("src/yaml/entries-*.yaml"):
    data = yaml.safe_load(open(file))
    for lemma, d in data.items():
        if "v" in d:
            for sense in d["v"]["sense"]:
                if "subcat" in sense and any(s.startswith("vt") for s in sense["subcat"]) and any(s.startswith("vi") for s in sense["subcat"]):
                    synsets.add(sense["synset"])

with open("vti-verbs.csv", "w") as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(["synset", "definition", "members", "transitive definition", "intransitive definition", "notes"])
    for file in glob("src/yaml/verb.*.yaml"):
        data = yaml.safe_load(open(file))
        for synset, d in data.items():
            if synset in synsets:
                csvwriter.writerow([synset, d["definition"][0], "; ".join(d["members"]), "", "", ""])
