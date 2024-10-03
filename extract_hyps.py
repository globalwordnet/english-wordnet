import yaml
from glob import glob
for f in glob("src/yaml/verb.*.yaml"):
   d = yaml.load(open(f), Loader=yaml.FullLoader)
   for key, data in d.items():
     for hyp in data.get("hypernym", []):
       print(key,hyp)

