import yaml
from glob import glob

mem2ssid = {}
definitions = {}

for file in glob("src/yaml/verb.*"):
    data = yaml.safe_load(open(file))
    for ssid, entry in data.items():
        for member in entry["members"]:
            if member not in mem2ssid:
                mem2ssid[member] = []
            mem2ssid[member].append(ssid)
        definitions[ssid] = entry["definition"][0]

print(mem2ssid.keys())

import csv
import re

reader = csv.reader(open("verb-trees.csv"))

next(reader)

with open("verb-trees2.csv", "w") as f:
    writer = csv.writer(f)
    for row in reader:
        if row[4] != "TOP" and not re.match("[0-9]{8}-v", row[5]):
            if row[4] in mem2ssid:
                for ssid in mem2ssid[row[4]]:
                    writer.writerow([row[0], row[2], row[3], row[4], ssid, definitions[ssid]])
                writer.writerow([])
            else:
                writer.writerow([row[0], row[2], row[3], row[4], "NO IDS", ""])
                writer.writerow([])


