import wordnet_yaml
import change_manager


def main():
    wn = wordnet_yaml.load()
    print(wn.entry_by_id("ewn-a-n").pronunciation)
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
