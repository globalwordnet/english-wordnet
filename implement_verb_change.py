from glob import glob
import yaml
import csv

members = {}

for file in glob("src/yaml/verb.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, d in data.items():
        if "members" in d:
            members[ssid] = d["members"]

members["02372362-v"].append("do")

changes = []

with open("oewn-verb-hypernyms - oewn-verb-hypernyms.csv") as f:
    f.readline()
    indata = csv.reader(f)
    for row in indata:
        ssid = row[4].strip()
        if not ssid:
            continue
        hyp_str = row[6].strip()
        if hyp_str:
            for hyp in hyp_str.split(", "):
                if ssid not in members:
                    print(f"Bad key for '{row[4]}'")
                elif hyp not in members[ssid]:
                    print(f"Hypernym '{hyp}' not in members of {row[4]}")
        if row[3].strip() and row[3] != row[4]:
            for t in row[3].split(", "):
                changes.append({"delete_relation": {
                    "source": row[0].strip(),
                    "target": t}})    
        if row[3] != row[4]:
            changes.append({"add_relation": {
                "source": row[0].strip(),
                "target": row[4].strip(),
                "relation": "hypernym"}})

with open("oewn-verb-hypernyms - oewn-verb-copula-hypernyms.csv") as f:
    f.readline()
    indata = csv.reader(f)
    for row in indata:
        ssid = row[3].strip()
        if not ssid:
            continue
        hyp_str = row[4].strip()
        if hyp_str:
            for hyp in hyp_str.split(", "):
                if ssid not in members:
                    print(f"Bad key for '{ssid}'")
                elif hyp not in members[ssid]:
                    print(f"Hypernym '{hyp}' not in members of {ssid}")

        changes.append({"delete_relation": {
            "source": row[0].strip(),
            "target": "02610777-v"}})
        changes.append({"add_relation": {
            "source": row[0].strip(),
            "target": row[3].strip(),
            "relation": "hypernym"}})

with open("changes.yaml", "w") as f:
    yaml.dump(changes, f)




