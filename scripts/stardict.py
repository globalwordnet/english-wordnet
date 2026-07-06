"""Converts the WN-LMF XML file (`wn.xml`) into a StarDict dictionary.

Requires the `pyglossary` package:

    pip install pyglossary

Usage:

    python scripts/stardict.py
    python scripts/stardict.py --input wn.xml --output english-wordnet-stardict
"""
import argparse
import sys

from wordnet import PartOfSpeech, parse_wordnet

try:
    from pyglossary.glossary_v2 import Glossary
except ImportError:
    sys.exit("This script requires pyglossary. Install it with: pip install pyglossary")

POS_LABELS = {
    PartOfSpeech.NOUN: "n",
    PartOfSpeech.VERB: "v",
    PartOfSpeech.ADJECTIVE: "adj",
    PartOfSpeech.ADJECTIVE_SATELLITE: "adj",
    PartOfSpeech.ADVERB: "adv",
    PartOfSpeech.NAMED_ENTITY: "n",
    PartOfSpeech.CONJUNCTION: "conj",
    PartOfSpeech.ADPOSITION: "prep",
}


def format_definition(lexicon, entry):
    """Build the StarDict definition text for a single LexicalEntry."""
    pos_label = POS_LABELS.get(entry.lemma.part_of_speech, "")
    lines = [f"[{pos_label}]"] if pos_label else []
    n = 0
    for sense in entry.senses:
        synset = lexicon.synset_by_id(sense.synset)
        if synset is None or not synset.definitions:
            continue
        n += 1
        gloss = "; ".join(d.text for d in synset.definitions)
        synonyms = []
        for member_id in synset.members:
            if member_id == entry.id:
                continue
            member = lexicon.entry_by_id(member_id)
            if member is not None and member.lemma.written_form not in synonyms:
                synonyms.append(member.lemma.written_form)
        line = f"{n}. {gloss}"
        if synonyms:
            line += f" (synonyms: {', '.join(synonyms)})"
        lines.append(line)
        for example in synset.examples:
            lines.append(f'   "{example.text}"')
    if n == 0:
        return None
    return "\n".join(lines)


def convert(lexicon, output, bookname, dictzip=False):
    Glossary.init()
    glos = Glossary()
    glos.setInfo("title", bookname)
    glos.setInfo("author", lexicon.label)
    glos.setInfo("publisher", lexicon.label)
    glos.setInfo("description", f"{lexicon.label}, version {lexicon.version} ({lexicon.url})")
    glos.setInfo("website", lexicon.url)

    n_entries = 0
    for entry in lexicon.entries():
        defi = format_definition(lexicon, entry)
        if not defi:
            continue
        words = [entry.lemma.written_form] + [f.written_form for f in entry.forms]
        glos.addEntry(glos.newEntry(words, defi, defiFormat="m"))
        n_entries += 1

    print(f"Writing {n_entries} entries to {output}...", file=sys.stderr)
    glos.write(output, formatName="Stardict", dictzip=dictzip)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="wn.xml",
                         help="Path to the WN-LMF XML file (default: wn.xml)")
    parser.add_argument("--output", default="english-wordnet-stardict",
                         help="Basename of the StarDict files to generate")
    parser.add_argument("--bookname", default=None,
                         help="Name of the dictionary (defaults to the lexicon label and version)")
    parser.add_argument("--dictzip", action="store_true",
                         help="Compress the .dict file with dictzip (requires the dictzip tool)")
    args = parser.parse_args()

    print(f"Loading {args.input}...", file=sys.stderr)
    lexicon = parse_wordnet(args.input)

    bookname = args.bookname or f"{lexicon.label} {lexicon.version}"
    convert(lexicon, args.output, bookname, dictzip=args.dictzip)


if __name__ == "__main__":
    main()
