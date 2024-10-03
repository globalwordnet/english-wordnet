from glob import glob
import yaml

ssid2synset = {}

for f in glob('src/yaml/entries*.yaml'):
    entries = yaml.load(open(f), Loader=yaml.CLoader)
    for lemma, by_pos in entries.items():
        for pos, entry in by_pos.items():
            for sense in entry['sense']:
                ssid2synset[sense['id']] = sense['synset']

with open("core-wordnet.txt") as f:
    for line in f.readlines():
        sense_id = line.split()[1][1:-1]
        if sense_id not in ssid2synset:
            print(f"Missing synset for {sense_id}")
            continue
