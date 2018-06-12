# English WordNet

The English WordNet as individual files in [GWN-LMF](http://globalwordnet.github.io/schemas/)
format.

## Usage

To compile these into a single file please use the following script

    python3 scripts/merge.py

This will create a file at `wn31.xml` that contains the complete wordnet.

Further conversions are available through the converter [here](http://server1.nlp.insight-centre.org:8080/gwn-converter).

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


