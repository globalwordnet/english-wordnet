import re
import csv
import yaml

r = csv.reader(open('verb-trees.csv'))

actions = []

for row in r:
    if re.match("\d{8}-v$", row[5]):
        actions.append({
            "relation": {
                "action": {
                    "add": {
                        "source": row[0],
                        "relation": "hypernym",
                        "target": row[5]
                        }
                    }
                }
            })

print(yaml.dump(actions, default_flow_style=False))
