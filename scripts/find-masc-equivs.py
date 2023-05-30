import yaml
import csv
from glob import glob

entry2ssid = {}

ssid2def = {}

for file in glob("src/yaml/noun.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, entry in data.items():
        for member in entry["members"]:
            if member not in entry2ssid:
                entry2ssid[member] = set()
            entry2ssid[member].add(ssid)
        ssid2def[ssid] = entry["definition"][0]

reader = csv.reader(open("female-words.csv"))

next(reader)

with open("fem-masc-equivs.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Fem", "SSID", "Masc", "SSID", "Definition"])
    for row in reader:
        print(row)
        if row[2] == "NONE":
            pass
        elif row[2] not in entry2ssid:
            writer.writerow([row[0], row[1], row[2], "NEW", ssid2def[row[1]]])
        else:
            for ssid in entry2ssid[row[2]]:
                writer.writerow([row[0], row[1], row[2], ssid, ssid2def[ssid]])





