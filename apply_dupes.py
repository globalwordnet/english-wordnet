import csv
import yaml

changes = []

with open("/home/jmccrae/Downloads/OEWN dupes - dupes.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        for i in range(0, int(len(row)/3)):
            if row[i*3+1]:
                changes.append({
                    "change_definition": {
                        "synset": row[i*3],
                        "definition": row[i*3+2]
                        }
                    })

with open("changes.yaml", "w") as f:
    yaml.dump(changes, f)
