import wordnet
import change_manager

wn30 = wordnet.parse_wordnet("/home/jmccrae/projects/jmccrae/gwn-scala-api/wn30.xml")

lemmas = [
        "Abo",
        "African American",
        "Afro-American",
        "Amerindian race",
        "Black American",
        "blackamoor",
        "Black man",
        "Black person",
        "Black race",
        "Black woman",
        "Caucasian race",
        "Caucasoid race",
        "colored", # noun
        "colored person",
        "darkey",
        "darkie",
        "darky",
        "gay man",
        "jigaboo",
        "Mongolian race",
        "Mongoloid race",
        "Negress",
        "Negroid race",
        "Negro race",
        "nigga",
        "nigger",
        "nigra",
        "oriental",
        "oriental person",
        "paleface",
        "people of color",
        "people of colour",
        "Red Indian",
        "shirtlifter",
        "slant-eye",
        "White people",
        "White race",
        "yellow man",
        "Yellow race",
        "yellow woman",
        "Uncle Tom"]

wn302ili = {
        ("pwn30-" + line.strip().split("\t")[1]): line.split("\t")[0]
        for line in open("../ili/ili-map-pwn30.tab").readlines() }

print(wn302ili["pwn30-09691279-n"])

ili2wn31 = {
        line.split("\t")[0]: "ewn-" + line.strip().split("\t")[1]
        for line in open("../ili/ili-map-pwn31.tab").readlines() }
        
ewn = wordnet.parse_wordnet("wn.xml")

synsets = set()
for lemma in lemmas:
    if lemma == "colored":
        lemma_id = "pwn30-colored-n"
    else:
        lemma_id = wn30.entry_by_lemma(lemma)[0]

    entry = wn30.entry_by_id(lemma_id)

    for sense in entry.senses:
        synsets.add(sense.synset)
        for r in sense.sense_relations:
            print("%s =%s=> %s" % (sense.id, r.rel_type, r.target))

synsets.add("pwn30-09637837-n")

wn302ewn = {}
for synset in synsets:
    ss = wn30.synset_by_id(synset)
    wn302ewn[synset] = change_manager.add_synset(ewn, ss.definitions[0].text, ss.lex_name, ss.part_of_speech.value)

for synset in synsets:
    ss = wn30.synset_by_id(synset)
    for r in ss.synset_relations:
        if wn302ili[r.target] in ili2wn31:
            change_manager.add_relation(ewn,
                    ewn.synset_by_id(wn302ewn[synset]),
                    ewn.synset_by_id(ili2wn31[wn302ili[r.target]]), r.rel_type)
        elif r.target in wn302ewn:
            change_manager.add_relation(ewn,
                    ewn.synset_by_id(wn302ewn[synset]),
                    ewn.synset_by_id(wn302ewn[r.target]), r.rel_type)
        else:
            print("%s => %s" % (r.rel_type, r.target))

for lemma in lemmas:
    if lemma == "colored":
        lemma_id = "pwn30-colored-n"
    else:
        lemma_id = wn30.entry_by_lemma(lemma)[0]

    entry = wn30.entry_by_id(lemma_id)

    for sense in entry.senses:
        change_manager.add_entry(ewn, ewn.synset_by_id(wn302ewn[sense.synset]), entry.lemma.written_form)

change_manager.add_entry(ewn, ewn.synset_by_id(wn302ewn["pwn30-09638245-n"]), "Tom")
change_manager.add_entry(ewn, ewn.synset_by_id(wn302ewn["pwn30-09637837-n"]), "boy")
