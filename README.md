# English WordNet

The English WordNet as individual files in [GWN-LMF](http://globalwordnet.github.io/schemas/)
format. This Wordnet is an attempt to make it easier to provide feedback in the 
form of patches to the [Princeton Wordnet](https://wordnet.princeton.edu/). 
It is undergoing a first trial in Summer 2018.

## Download

The latest version can be accessed here

* [As WN-LMF XML](http://server1.nlp.insight-centre.org/enwordnet-update/english-wordnet-3.2.xml)
* [As RDF (TTL)](http://server1.nlp.insight-centre.org/enwordnet-update/english-wordnet-3.2.ttl) (the RDF TTL file conains only the instances - the Ontolex schema is also available [as RDF XML](https://www.w3.org/ns/lemon/ontolex))
* [As WordNet database files](http://server1.nlp.insight-centre.org/enwordnet-update/english-wordnet-3.2.zip)

Please note these files are automatically compiled from the HEAD of MASTER and 
may not be available immediately after a commit.

## Usage

To compile these into a single file please use the following script

    python3 scripts/merge.py

This will create a file at `wn31.xml` that contains the complete wordnet.

Further conversions are available through the converter [here](http://server1.nlp.insight-centre.org/gwn-converter).

## Changes

**We are currently only accepting the following changes:**

* Minor corrections to definitions, examples (e.g., spelling)
* Corrections of lemmas
* Corrections of relationship types
* Proposals for deletion of duplicate or nonextant concepts

We are not accepting any additions of synsets, lemmas or relations.

We welcome changes, to make a change please read our [contributing guidelines](CONTRIBUTING.md) 
and make a pull request.

Also please read the guidelines for [consistency of the format](FORMAT.md)

## License

WordNet is released under the [WordNet License](https://wordnet.princeton.edu/license-and-commercial-use)


