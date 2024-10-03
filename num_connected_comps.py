from glob import glob
import yaml
import networkx as nx

G = nx.Graph()

rels = [
'agent',
'also',
'attribute',
'be_in_state',
'causes',
'classified_by',
'classifies',
'co_agent_instrument',
'co_agent_patient',
'co_agent_result',
'co_instrument_agent',
'co_instrument_patient',
'co_instrument_result',
'co_patient_agent',
'co_patient_instrument',
'co_result_agent',
'co_result_instrument',
'co_role',
'direction',
'domain_region',
'domain_topic',
'exemplifies',
'entails',
'eq_synonym',
'has_domain_region',
'has_domain_topic',
'is_exemplified_by',
'holo_location',
'holo_member',
'holo_part',
'holo_portion',
'holo_substance',
'holonym',
'hypernym',
'hyponym',
'in_manner',
'instance_hypernym',
'instance_hyponym',
'instrument',
'involved',
'involved_agent',
'involved_direction',
'involved_instrument',
'involved_location',
'involved_patient',
'involved_result',
'involved_source_direction',
'involved_target_direction',
'is_caused_by',
'is_entailed_by',
'location',
'manner_of',
'mero_location',
'mero_member',
'mero_part',
'mero_portion',
'mero_substance',
'meronym',
'similar',
'other',
'patient',
'restricted_by',
'restricts',
'result',
'role',
'source_direction',
'state_of',
'target_direction',
'subevent',
'is_subevent_of',
'antonym'] 


for file in glob("src/yaml/verb.*.yaml"):
    data = yaml.safe_load(open(file))
    for ssid, d in data.items():
        G.add_node(ssid)
        for r in rels:
            for h in d.get(r, []):
                if h.endswith("-v"):
                    G.add_edge(ssid, h)
        #for h in d.get("hypernym", []):
        #    G.add_edge(ssid, h)


#for file in glob("src/yaml/noun.*.yaml"):
#    data = yaml.safe_load(open(file))
#    for ssid, d in data.items():
#        for h in d.get("hypernym", []):
#            G.add_edge(ssid, h)

senseid_to_synset = {}
derivations = {}

for file in glob("src/yaml/entries-*.yaml"):
    data = yaml.safe_load(open(file))
    for lemma, d1 in data.items():
        for pos, d2 in d1.items():
            for sense in d2["sense"]:
                senseid_to_synset[sense["id"]] = sense["synset"]
                derivations[sense["synset"]] = sense.get("derivation", [])

for ssid, derivs in derivations.items():
    for d in derivs:
        if senseid_to_synset[d].endswith("-v"):
            G.add_edge("nouns", senseid_to_synset[d])

print(f"Number of connected components: {nx.number_connected_components(G)}")

i = 0

for c in nx.connected_components(G):
    print(len(c), list(c)[:10])
    i += 1
    if i > 10:
        break
