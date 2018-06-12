import xml.etree.ElementTree as ET
from glob import glob

def merge_entry(e1, e2):
    i = 0
    for c in e1:
        if c.tag == "Lemma" or c.tag == "Form" or c.tag == "Sense":
            i += 1
    for c in e2:
        if c.tag == "Sense":
            e1.insert(i, c)
            i += 1
    return e1


def main():
    with open("wn31.xml", "w") as out:
        out.write("""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.0.dtd">
    <LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">
      <Lexicon id="ewn" 
               label="English WordNet"
               language="en"
               email="john@mccr.ae"
               license="https://wordnet.princeton.edu/license-and-commercial-use"
               version="3.1" 
               url="https://github.com/globalwordnet/english-wordnet">""")
        lex_entries = {}

        for wn31_part in glob("src/wn31-*.xml"):
            tree = ET.parse(wn31_part).getroot()
            for element in tree[0]:
                if(element.tag == "LexicalEntry"):
                    id = element.attrib["id"]
                    if id in lex_entries:
                        lex_entries[id] = merge_entry(lex_entries[id], element)
                    else:
                        lex_entries[id] = element
        for (k, e) in lex_entries.items():
            out.write(ET.tostring(e).decode()
                    .replace(" xmlns:dc=\"http://purl.org/dc/elements/1.1/\"",""))

        for wn31_part in glob("src/wn31-*.xml"):
            tree = ET.parse(wn31_part).getroot()
            for element in tree[0]:
                if(element.tag == "Synset"):
                    out.write(ET.tostring(element).decode()
                            .replace(" xmlns:dc=\"http://purl.org/dc/elements/1.1/\"",""))
        out.write("""
  </Lexicon>
</LexicalResource>""")


if __name__ == "__main__":
    main()
