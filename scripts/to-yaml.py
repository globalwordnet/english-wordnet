from change_manager import parse_wordnet
from wordnet_yaml import save


def main():
    wn = parse_wordnet("wn.xml")
    save(wn)


if __name__ == "__main__":
    main()
