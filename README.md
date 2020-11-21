# English WordNet

English WordNet is a lexical network of the English language grouping words into synsets and linking them according
to relationships such as hypernymy, antonymy and meronymy. It is intended to be used in natural language processing 
applications and provides deep lexical information about the English language as a graph.

English WordNet is a fork of the [Princeton Wordnet](https://wordnet.princeton.edu/) developed under
an open source methodology. The quality and veracity of the resource may differ from the Princeton 
WordNet and we welcome contributions. Contributions to this wordnet may eventually be incorporated into
future releases of Princeton WordNet. Correspondance to previous versions and wordnets in other language is provided
through the [Collaborative Interlingual Index (CILI)](http://compling.hss.ntu.edu.sg/iliomw/ili). The English WordNet is available as individual files in [GWN-LMF](http://globalwordnet.github.io/schemas/) format.

## Releases

English WordNet is released through the [English WordNet website](https://en-word.net/). The version released are

* **2020 Edition** (Released 17th April 2020). [(LMF)](https://en-word.net/static/english-wordnet-2020.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2020.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2020.zip)
* **2019 Edition** (Released 17th April 2019). [(LMF)](https://en-word.net/static/english-wordnet-2019.xml.gz)
[(RDF)](https://en-word.net/static/english-wordnet-2019.ttl.gz)
[(WNDB)](https://en-word.net/static/english-wordnet-2019.zip)

## Usage

To compile these into a single file please use the following script

    python3 scripts/merge.py

This will create a file at `wn31.xml` that contains the complete wordnet.

Further conversions are available through the converter [here](http://server1.nlp.insight-centre.org/gwn-converter/).

## Changes

We welcome changes, to make a change please read our [contributing guidelines](CONTRIBUTING.md) 
and make a pull request.

English WordNet is a high-quality resource that acts as a gold-standard for natural language processing,
as such we cannot accept any automatically generated results that have not been manually validated.

Please be aware that we use the [Global WordNet Association LMF](https://globalwordnet.github.io/schemas/) and please read the guidelines for using the [format](FORMAT.md)

## License

WordNet is released under [CC-BY 4.0](LICENSE.md)

## Contributors

* John P. McCrae
* Alexandre Rademaker
* Ewa Rudnicka
* Bernard Bou
* Daiki Nomura
* David Cillessen
* Francis Bond
