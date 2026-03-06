# Generate Open English Wordnet+ the version of Open English Wordnet extended
# with additional words and synsets from Open English Namenet.
from glob import glob
import argparse
import os
import yaml

def compare_pronunciations(pron1, pron2):
    """Compare two pronunciation entries for equality."""
    if pron1.keys() != pron2.keys():
        return False
    for key in pron1:
        if pron1[key] != pron2[key]:
            return False
    return True

def merge_addendum(data, add, sense_orders):
    """Merge the addendum data together. Recursively merge the dictionaries,
        together, raising an exception if there are any key conflicts.
        A special case is `sense` where we must match the `id` field when
        merging"""
    for key, value in add.items():
        if key not in data:
            data[key] = value
        else:
            if isinstance(value, dict):
                merge_addendum(data[key], value, sense_orders.get(key, {}))
            elif isinstance(value, list):
                if key == "sense":
                    id2sense = {sense["id"]: sense for sense in data[key]}
                    for sense in value:
                        if sense["id"] in id2sense:
                            merge_addendum(id2sense[sense["id"]], sense, {})
                        else:
                            data[key].append(sense)

                    # If sense_orders is a list, then sort the senses by this list
                    if isinstance(sense_orders, list):
                        id_order = {sid: i for i, sid in enumerate(sense_orders)}
                        data[key].sort(key=lambda s: id_order.get(s["id"], len(id_order)))
                elif key == "pronunciation":
                    for pron in value:
                        if not any(compare_pronunciations(pron, existing) for existing in data[key]):
                            data[key].append(pron)
                else:
                    data[key].extend(value)
            elif isinstance(value, str) and isinstance(data[key], str) and data[key] == value:
                pass
            else:
                print(type(value))
                raise ValueError(f"Conflict at key {key}: {data[key]} vs {value}")

def merge_curated(data, curated, is_entry):
    """Merge the curated data together. For entries, we match the first two keys
    (lemma and pos) when merging. For other files, we merge by key."""
    if is_entry:
        for lemma, by_pos in curated.items():
            if lemma not in data:
                data[lemma] = by_pos
            else:
                for pos, entry in by_pos.items():
                    if pos not in data[lemma]:
                        data[lemma][pos] = entry
                    else:
                        merge_addendum(data[lemma][pos], entry, {})
    else:
        # Check the keys are disjoint
        for key in curated:
            if key in data:
                raise ValueError(f"Conflict at key {key} during curated merge")
        data.update(curated)

def recursively_sort(data):
    """Recursively sort the dictionary by keys."""
    if isinstance(data, dict):
        sorted_data = dict()
        for key in sorted(data.keys()):
            sorted_data[key] = recursively_sort(data[key])
        return sorted_data
    elif isinstance(data, list):
        return [recursively_sort(item) for item in data]
    else:
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Open English Wordnet+ from Open English Wordnet and Open English Namenet"
    )
    parser.add_argument(
        "oenn",
        type=str,
        help="Directory containing Open English Wordnet files",
    )
    args = parser.parse_args()

    oenn_path = args.oenn
    if not oenn_path.endswith("/"):
        oenn_path += "/"

    if not os.path.exists(f"{oenn_path}data/addendum/sense_orders.yaml"):
        raise ValueError(f"Addendum file not found: {oenn_path}data/addendum/sense_orders.yaml")

    with open(oenn_path + "data/addendum/sense_orders.yaml", "r") as so_file:
        sense_orders = yaml.safe_load(so_file)

    for f in glob("src/yaml/*.yaml"):
        filename = f.split("/")[-1]
        print(f"Processing {filename}...")
        with open(f, "r") as file:
            data = yaml.safe_load(file)
        if os.path.exists(oenn_path + "data/addendum/" + filename):
            print(f"  Merging addendum for {filename}...")
            with open(oenn_path + "data/addendum/" + filename, "r") as add_file:
                add_data = yaml.safe_load(add_file)
                merge_addendum(data, add_data, sense_orders)
        if os.path.exists(oenn_path + "data/curated/" + filename):
            print(f"  Merging curated for {filename}...")
            with open(oenn_path + "data/curated/" + filename, "r") as curated_file:
                curated_data = yaml.safe_load(curated_file)
                merge_curated(data, curated_data, filename.startswith("entries"))
        data = recursively_sort(data)
        with open("src/plus/" + filename, "w") as out_file:
            yaml.dump(data, out_file, sort_keys=False, allow_unicode=True)




