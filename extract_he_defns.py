from glob import glob
import yaml
import re
import csv

with open("he_words.csv", "w") as f:
    out = csv.writer(f)
    for file in glob('src/yaml/*.yaml'):
        if (file.startswith("src/yaml/noun") or
            file.startswith("src/yaml/verb") or
            file.startswith("src/yaml/adj") or
            file.startswith("src/yaml/adv")):
            data = yaml.load(open(file), Loader=yaml.CLoader)
            for ssid, entry in data.items():
                for definition in entry['definition']:
                    for word in re.split(r"\b", definition.lower().strip()):
                        if word == "he" or word == "him" or word == "himself" or word == "his":
                            out.writerow([ssid, ", ".join(entry['members']), definition])
                            break
