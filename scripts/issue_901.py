import xml.etree.ElementTree as ET

tree = ET.parse('issue-34.xml')

root = tree.getroot()

definitions = {}

for child in root:
    for defs in child:
        definitions[defs[0].text] = defs[1].text

import yaml
from glob import glob

for file in glob("src/yaml/*.yaml"):
    if not file.startswith("src/yaml/entries") and not file.startswith("src/yaml/frame"):
        print(file)
        data = yaml.safe_load(open(file))
        changes = 0
        for key, entry in data.items():
            if entry["definition"][0] in definitions:
                d2 = definitions[entry["definition"][0]]
                del definitions[entry["definition"][0]]
                entry["definition"][0] = d2
                changes += 1
        if changes > 0:
            with open(file, "w") as outp:
                outp.write(yaml.dump(data, default_flow_style=False,
                    allow_unicode=True))

print("\n".join(definitions.keys()))
