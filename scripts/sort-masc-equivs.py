import yaml
import csv
from glob import glob

entry2ssid = {}

ssid2def = {}

hyps = {}

for file in glob("src/yaml/noun.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, entry in data.items():
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

print("Link to gender-neutral entries")
print("==============================")
print()

for hyp_row in hyp_rows:
    print(f"* {hyp_row[0]} (`{hyp_row[1]}` {ssid2def[hyp_row[1]]}) to {hyp_row[2]} (`{hyp_row[3]}` {ssid2def[hyp_row[3]]})")
 
print()
print("Link to form in same synset")
print("===========================")
print()

for row in syn_rows:
    print(f"* {row[0]} (`{row[1]}` {ssid2def[row[1]]}) to {row[2]}")

print()
print("Other link (including to masculine entry)")
print("==========================================")
print()

for row in other_rows:
    if row[1] in ssid2def:
        print(f"* {row[0]} (`{row[1]}` {ssid2def[row[1]]}) to {row[2]} (`{row[3]}` {ssid2def[row[3]]})")
    else:
        print(f"* {row[0]} (`{row[1]}`) to {row[2]} (`{row[3]}` {ssid2def[row[3]]})")

print()
print("Novel masculine terms to be introduced")
print("======================================")

for row in new_rows:
    print(f"* {row[2]} - {row[4]} (from {row[0]})")
