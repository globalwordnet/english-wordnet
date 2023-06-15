import yaml
from yaml import CLoader as Loader
from glob import glob
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

defs = {}

members = {}

for f in glob("src/yaml/verb.*.yaml"):
    for ssid, data in yaml.load(open(f),Loader=Loader).items():
        if "hypernym" in data:
            for h in data["hypernym"]:
                G.add_edge(ssid, h)
        else:
            G.add_node(ssid)
        if "definition" in data:
            defs[ssid] = data["definition"][0]
        if "members" in data:
            members[ssid] = data["members"]

size = {n: -1 for n in G.nodes()}

def calc_size(n):
    if size[n] >= 0:
        return size[n]
    else:
        z = sum(calc_size(p) for p in G.predecessors(n)) + 1
        size[n] = z
        return z

for n in G.nodes():
    calc_size(n)

def filter_by_size(n):
    return size[n] >= 35

nx.draw(nx.subgraph_view(G, filter_node=filter_by_size))
plt.show()
