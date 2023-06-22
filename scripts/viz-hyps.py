import yaml
from yaml import CLoader as Loader
from glob import glob
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

defs = {}

members = {}

labels = {}

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
            labels[ssid] = data["members"][0]

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


sinks = {n for n in G.nodes() if G.out_degree(n) == 0}

def write_tree(node, depth):
    if size[node] >= 35:
        print("%s- [%s](https://en-word.net/id/oewn-%s) (%d)" % ("  " * (depth-1), ", ".join(members[node]), node, size[node]))
        for p in sorted(G.predecessors(node), key=lambda n: -size[n]):
            write_tree(p, depth + 1)

for s in sorted(sinks, key=lambda n: -size[n]):
    write_tree(s, 1)

#G2 = nx.subgraph_view(G, filter_node=filter_by_size)
#
#labels = {k: v for k, v in labels.items() if k in G2.nodes()}
#
#
#pos = nx.spring_layout(G2, k = 1/10)
#
#nx.draw_networkx_nodes(G2, pos = pos)
#nx.draw_networkx_edges(G2, pos = pos, arrows=True)
#nx.draw_networkx_labels(G2, pos = pos, labels = labels, font_size=8)
#plt.show()
