#####################################
## English WordNet Editor (EWE)

def enter_synset(wordnet):
    synset = None
    while not synset:
        synset_id = "ewn-" + input("Enter synset ID : ewn-")
        synset = wn.synset_by_id(synset_id)
        if not synset:
            print("Synset not found")
    return synset


def change_entry():
    action = input("[A]dd/[D]elete/[M]ove? ").upper()
    while action != "A" and action != "D" and action != "M":
        print("Bad action")
        action = input("[A]dd/[D]elete/[M]ove? ").upper()

    wn = change_manager.load_wordnet()

    synset = enter_synset(wn)

    entries = wn.members_by_id(synset_id)
    if entries:
        print("Entries: " + ", ".join(entries))
    else:
        print("No entries")

    if action == "A":
        lemma = input("New entry: ")
    elif action == "D":
        lemma = input("Entry to remove: ")
    elif action == "M":
        lemma = input("Entry to move: ")

    if action == "A":
        change_manager.add_entry(wn, synset, lemma)
    elif action == "D":
        change_manager.delete_entry(wn, synset, 
                "ewn-%s-%s" % (change_manager.escape_lemma(lemma), synset.part_of_speech.value))
    elif action == "M":
        target_synset = enter_synset(wn)

        if synset.lex_name == target_synset.lex_name:
            change_manager.change_entry(wn, synset, target_synset, lemma)
        else:
            print("Moving across lexicographer files so implementing change as delete then add")
            change_manager.delete_entry(wn, synset, 
                    "ewn-%s-%s" % (change_manager.escape_lemma(lemma), synset.part_of_speech.value))
            change_manager.add_entry(wn, target_synset, lemma)


def main_menu():
    print("Please choose an option:")
    print("1. Add/delete/move entry")
    print("2. Add/delete a synset")
    print("3. Change a definition")
    print("4. Change an example")
    print("5. Change a relation")
    print("6. Exit EWE")
    
    mode = input("Option> ")
    if mode == "1":
        print("change-entry")
    elif mode == "2":
        print("change-synset")
    elif mode == "3":
        print("change-definition")
    elif mode == "4":
        print("change-example")
    elif mode == "5":
        print("change-relation")
    elif mode == "6":
        return False
    else:
        print("Please enter a number between 1 and 6")
    return True

def main():
    print("")
    print("         ,ww                             ")
    print("   wWWWWWWW_)  Welcome to EWE            ") 
    print("   `WWWWWW'    - English WordNet Editor  ")
    print("    II  II                               ")
    print("")

    while main_menu():
        pass


if __name__ == "__main__":
    main()
