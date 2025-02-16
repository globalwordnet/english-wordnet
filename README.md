# Open English Wordnet

Open English Wordnet is a lexical network of the English language grouping words into synsets and linking them according
to relationships such as hypernymy, antonymy and meronymy. It is intended to be used in natural language processing 
applications and provides deep lexical information about the English language as a graph.

Open English Wordnet is a fork of the [Princeton WordNet](https://wordnet.princeton.edu/) developed under
an open source methodology. The quality and veracity of the resource may differ from the Princeton 
Wordnet and we welcome contributions. Contributions to this wordnet may eventually be incorporated into
future releases of Princeton WordNet. Correspondance to previous versions and wordnets in other language is provided
through the [Collaborative Interlingual Index (CILI)](https://github.com/globalwordnet/cili). The Open English Wordnet is available as individual files in [GWN-LMF](http://globalwordnet.github.io/schemas/) format.

## Releases

Open English Wordnet is released through the [Open English Wordnet website](https://en-word.net/). The versions released are

* **2024 Edition** (Released 1st November 2024). [(LMF)](https://en-word.net/static/english-wordnet-2024.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2024.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2024.zip)
* **2023 Edition** (Released 31st October 2023). [(LMF)](https://en-word.net/static/english-wordnet-2023.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2023.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2023.zip)
* **2022 Edition** (Released 31st December 2022). [(LMF)](https://en-word.net/static/english-wordnet-2022.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2022.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2022.zip)
* **2021 Edition** (Released 9th November 2021). [(LMF)](https://en-word.net/static/english-wordnet-2021.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2021.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2021.zip)
* **2020 Edition** (Released 17th April 2020). [(LMF)](https://en-word.net/static/english-wordnet-2020.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2020.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2020.zip)
* **2019 Edition** (Released 17th April 2019). [(LMF)](https://en-word.net/static/english-wordnet-2019.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2019.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2019.zip)

The size of each resource is as follows

| Edition | Words   | Synsets | Relations |
|---------|---------|---------|-----------|
| 2024    | 161,705 | 120,630 | 419,168   |
| 2023    | 161,338 | 120,135 | 415,905   |
| 2022    | 161,221 | 120,068 | 386,437   |
| 2021    | 163,161 | 120,039 | 384,505   |
| 2020    | 163,079 | 120,052 | 385,211   |
| 2019    | 160,051 | 117,791 | 378,201   |
| Princeton 3.1 | 159,015 | 117,791 | 378,203 | 

## Usage

To compile these into a single file please use the following script(s)

    python scripts/from_yaml.py

This will create a file at `wn.xml` that contains the complete wordnet.

Further conversions are available through the converter [here](http://server1.nlp.insight-centre.org/gwn-converter/).

## Changes

We welcome changes, to make a change please read our [contributing guidelines](CONTRIBUTING.md) 
and make a pull request.

Open English Wordnet is a high-quality resource that acts as a gold-standard for natural language processing,
as such we cannot accept any automatically generated results that have not been manually validated.

Please be aware that we use the [Global WordNet Association LMF](https://globalwordnet.github.io/schemas/) and please read the guidelines for using the [format](FORMAT.md)

## License

Open English Wordnet is released under [CC-BY 4.0](LICENSE.md)

## References

The canonical citation for English Wordnet is:

* John P. McCrae, Alexandre Rademaker, Francis Bond, Ewa Rudnicka and Christiane Fellbaum (2019) [English WordNet 2019 – An Open-Source WordNet for English](https://aclanthology.org/2019.gwc-1.31/). In *Proceedings of the 10th Global WordNet Conference – GWC 2019*, Wrocław

More recent papers describing it include:

* John Philip McCrae, Alexandre Rademaker, Ewa Rudnicka, Francis Bond (2020)
[English WordNet 2020: Improving and Extending a WordNet for English using an Open-Source Methodology](https://aclanthology.org/2020.mmw-1.3/). In *Proceedings of the LREC 2020 Workshop on Multimodal Wordnets (MMW2020)*, Marseille

* John P. McCrae, Michael Wayne Goodman, Francis Bond, Alexandre Rademaker, Ewa Rudnicka, Luis Morgado Da Costa (2020) [The GlobalWordNet Formats: Updates for 2020](https://aclanthology.org/2021.gwc-1.11/). In *Proceedings of the 11th Global Wordnet Conference (GWC2021)*, University of South Africa (UNISA)

It incorporates material from:

* Christiane Fellbaum, editor (1998) *WordNet: An Electronic Lexical Database*. The MIT Press, Cambridge, MA.
* Merrick Choo Yeu Herng and Francis Bond (2021) [Taboo wordnet](https://aclanthology.org/2021.gwc-1.5/). In *Proceedings of the 11th Global Wordnet Conference (GWC2021)*, University of South Africa (UNISA).


## Contributors

* John P. **McCrae**
* Alexandre **Rademaker**
* Ewa **Rudnicka**
* Bernard **Bou**
* Daiki **Nomura**
* David **Cillessen**
* Ciara **O'Loughlin**
* Cathal **McGovern**
* Francis **Bond**
* Eric **Kafe**
* Michael Wayne **Goodman**
* Merrick **Choo** Yeu Herng
* Enejda **Nasaj**
