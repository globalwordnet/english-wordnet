import wordnet_yaml
import change_manager


def main():
    wn = wordnet_yaml.load()
    change_manager.save_all_xml(wn)


if __name__ == "__main__":
    main()
