import xml.etree.ElementTree as ET
from glob import glob


def merge_entry(e1, e2):
    i = 0
    for c in e1:
        if c.tag == "Lemma" or c.tag == "Form" or c.tag == "Sense" or c.tag == "Pronunciation":
            i += 1
    for c in e2:
        if c.tag == "Sense":
            e1.insert(i, c)
            i += 1
        if c.tag == "SyntacticBehaviour":
            src = [c2 for c2 in e1 if c2.tag == "SyntacticBehaviour" and c2.attrib["subcategorizationFrame"]
                   == c.attrib["subcategorizationFrame"]]
            if not src:
                e1.insert(i, c)
                i += 1
            else:
                for s in src:
                    s.attrib["senses"] += " " + c.attrib["senses"]
    return e1


def order_entry(e):
    f = ET.Element('LexicalEntry')
    f.attrib = e.attrib
    senses = []
    for c in e:
        if c.tag == "Lemma" or c.tag == "Form" or c.tag == "Pronunciation":
            f.append(c)
        elif c.tag == "Sense":
            senses.append(c)
    senses.sort(key=lambda x: int(x.attrib["n"]))
    for c in senses:
        del c.attrib["n"]
        f.append(c)
    for c in e:
        if c.tag == "SyntacticBehaviour":
            f.append(c)
    return f


def indent(elem, level=0):
    i = "\n" + level * "  "
    j = "\n" + (level + 1) * "  "
    if len(elem):
        elem.text = j
        n = 1
        for subelem in elem:
            if n != len(elem):
                indent(subelem, level + 1)
                subelem.tail = j
            else:
                subelem.tail = i
            n += 1
    else:
        elem.tail = i
    return elem


def wn_merge():
    with open("wn.xml", "w", encoding="utf-8") as out:
        out.write("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.1.dtd">
<LexicalResource xmlns:dc="https://globalwordnet.github.io/schemas/dc/">
  <Lexicon id="oewn"
           label="Open English WordNet"
           language="en"
           email="english-wordnet@googlegroups.com"
           license="https://creativecommons.org/licenses/by/4.0/"
           version="2021"
           citation = "John P. McCrae, Alexandre Rademaker, Francis Bond, Ewa Rudnicka and Christiane Fellbaum (2019) English WordNet 2019 – An Open-Source WordNet for English, *Proceedings of the 10th Global WordNet Conference* – GWC 2019"
           url="https://github.com/globalwordnet/english-wordnet">""")
        lex_entries = {}
    
        ET.register_namespace("dc", "https://globalwordnet.github.io/schemas/dc/")

        for wn_part in glob("src/xml/wn-*.xml"):
            tree = ET.parse(wn_part).getroot()
            for element in tree[0]:
                if(element.tag == "LexicalEntry"):
                    id = element.attrib["id"]
                    if id in lex_entries:
                        lex_entries[id] = merge_entry(lex_entries[id], element)
                    else:
                        lex_entries[id] = element
        for (k, e) in lex_entries.items():
            out.write("\n    ")
            out.write(
                ET.tostring(
                    indent(
                        order_entry(e),
                        level=2)).decode() .replace(
                    " xmlns:dc=\"https://globalwordnet.github.io/schemas/dc/\"",
                    ""))
        out.write("\n    ")

        for wn_part in glob("src/xml/wn-*.xml"):
            tree = ET.parse(wn_part).getroot()
            for element in tree[0]:
                if(element.tag == "Synset"):
                    out.write(ET.tostring(element).decode() .replace(
                        " xmlns:dc=\"https://globalwordnet.github.io/schemas/dc/\"", ""))
        tree = ET.parse("src/xml/wn-verb.body.xml").getroot()
        for element in tree[0]:
            if element.tag == "SyntacticBehaviour":
                out.write(ET.tostring(element).decode() .replace(
                    " xmlns:dc=\"https://globalwordnet.github.io/schemas/dc/\"", ""))
        out.write("""
  </Lexicon>
</LexicalResource>""")


def main():
    wn_merge()


if __name__ == "__main__":
    main()
