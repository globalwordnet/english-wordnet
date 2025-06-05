## Create QuickStatements to push changes to wikidata
##
## These changes can be enacted at https://quickstatements.toolforge.org/
import argparse
import yaml
import requests
from glob import glob
from collections import defaultdict

def get_current_wikidata_data():
    url = "https://query.wikidata.org/sparql?query=select%20%2a%20%7B%0A%20%20%3Fwikidata%20wdt%3AP5063%20%3Fwordnet%0A%7D"
    header = {
        "Accept": "text/csv"
    }
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from Wikidata: {response.status_code}")
    wd2wn = defaultdict(set)
    for line in response.text.splitlines():
        if line.startswith("http://www.wikidata.org/entity/"):
            elems = line.split(",")
            wd2wn[elems[0].split("/")[-1]].add(elems[1])
    
    return wd2wn

def get_wordnet_data():
    wd2wn = defaultdict(set)
    ili2id = {}
    for file in glob("src/yaml/[nva]*.yaml"):
        with open(file, "r") as f:
            yaml_data = yaml.safe_load(f)
            for wordnet_key, item in yaml_data.items():
                if "wikidata" in item and "ili" in item:
                    
                    if isinstance(item["wikidata"], list):
                        wikidata = item["wikidata"]
                    elif isinstance(item["wikidata"], str):
                        wikidata = [item["wikidata"]]
                    for wd in wikidata:
                        wd2wn[wd].add(item["ili"])
                if "ili" in item:
                    ili2id[item["ili"]] = wordnet_key
    return wd2wn, ili2id
 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create QuickStatements for Wikidata synchronization.")
    parser.add_argument("quickstatements_file", type=str, help="Path to the QuickStatements file to write output.")
    parser.add_argument("ewe_file", type=str, help="Path to the EWE file to write output.")
    args = parser.parse_args()

    wikidata = get_current_wikidata_data()
    wordnetdata, ili2id = get_wordnet_data()

    ili2wd = {v: k for k, vs in wordnetdata.items() for v in vs}

    joint_keys = set(wikidata.keys()).union(set(wordnetdata.keys()))

    with open(args.quickstatements_file, "w") as qs_file:
        with open(args.ewe_file, "w") as ewe_file:
            for key in joint_keys:
                if len(wikidata[key]) > 0 and all(wd not in ili2wd for wd in wikidata[key]):
                    wd = next(iter(wikidata[key]))
                    if wd not in ili2id:
                        print(f"Warning: Wikidata ID {wd} not found in ILI mapping.")
                        continue
                    ewe_file.write(f"- change_wikidata:\n")
                    ewe_file.write(f"    synset: {ili2id[wd]}\n")
                    ewe_file.write(f"    wikidata: {key}\n")
                else:
                    for to_remove in wikidata[key] - wordnetdata[key]:
                        qs_file.write(f"-{key}\tP5063\t\"{to_remove}\"\n")
                    for to_add in wordnetdata[key] - wikidata[key]:
                        qs_file.write(f"{key}\tP5063\t\"{to_add}\"\n")


