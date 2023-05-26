import yaml
from yaml import CLoader as Loader
from glob import glob
import networkx as nx

G = nx.DiGraph()

defs = {}

members = {}

for f in glob("src/yaml/verb.*.yaml"):
    for ssid, data in yaml.load(open(f),Loader=Loader).items():
        if "hypernym" in data:
            for h in data["hypernym"]:
                G.add_edge(ssid, h)
        if "definition" in data:
            defs[ssid] = data["definition"][0]
        if "members" in data:
            members[ssid] = data["members"]

sinks = [node for node in G.nodes() if G.out_degree(node) == 0]

sup_size = {s: 0 for s in sinks}

for n in G.nodes():
    if n not in sinks:
        for s in sinks:
            if nx.has_path(G, n, s):
                sup_size[s] += 1

sup_size = sorted(sup_size.items(), key=lambda x: -x[1])

for sup, size in sup_size:
    print("%s,%d,\"%s\",\"%s\"" % (sup, size, ", ".join(members[sup]), defs[sup].replace("\"", "\"\"")))
