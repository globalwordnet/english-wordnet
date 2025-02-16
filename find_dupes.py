import yaml
from glob import glob
from collections import defaultdict
import csv

defn = defaultdict(list)
members = defaultdict(list)

for file in glob('src/yaml/[nva]*.yaml'):
    with open(file) as f:
        data = yaml.load(f, Loader=yaml.CLoader)
        for id, v in data.items():
            for d in v['definition']:
                defn[d].append(id)
            members[id] = v['members']

with open('dupes.csv', 'w') as f:
    writer = csv.writer(f)
    for k, v in defn.items():
        if len(v) > 1:
            vals = []
            for i in v:
                vals.append(i)
                vals.append(";".join(members[i]))
                vals.append(k)
            writer.writerow(vals)
