import yaml
from glob import glob

female_words = set(line.strip() for line in open("fem-words").readlines())

synsets = set()

print("Lemma,Synset,Masculine")

for file in glob("src/yaml/entries-*.yaml"):
    data = yaml.safe_load(open(file))
    for lemma, d in data.items():
        if lemma in female_words and "n" in d:
            for sense in d["n"]["sense"]:
                print("%s,%s," % (lemma, sense["synset"]))
