Merging and creating new synsets
================================

This document describes procedures in Open English WordNet for merging synsets and for 
deducing if there is a need to create a new synset, for a new sense of a word.

Synsets that share a lemma
--------------------------

In the case that we are considering merging two synsets that share a lemma or for the
case of introducing a novel synset, the principle method of inferring if there is a novel
synset is based on graph positions. The graph position is defined by the characteristic
links of the synset, which are as follows

* Nouns:
  * hypernym
* Verbs:
  * hypernym
  * entails
* Adjectives:
  * pertains
  * further to be decided
* Adverbs:
  * to be decided

Two synsets with different positions in the graph should not be merged. For example,
similar definitions but clearly distinct hypernyms would not be merged.

An example of a merge based on these properties is given by [Issue #911](https://github.com/globalwordnet/english-wordnet/issues/911)

If it is decided that no merge is necessary, we should normally update definitions
or the characteristic links to make the sense distinction clearer.

Synsets that don't share a lemma
--------------------------------

In the case that the synsets don't share a lemma, we are also claiming that there
is synonymy between all the words of the synset. The steps we take to verify this
are as follows

1. Verify that the synsets would have the same characteristic links (see above)
2. Collect at least 3 examples for each of these synsets. This can be done by
   using the [CoCA](https://www.english-corpora.org/coca/) corpus and finding 
   the first 3 matching examples that fit with this sense
3. Check that all lemmas can be substituted in all cases without substantial change in meaning

For example [Issue #750](https://github.com/globalwordnet/english-wordnet/issues/750)

An example of 'self-serving' was found in the corpus

> the __self-serving__ and greedy Daffy Duck

We substitute with the candidate merge lemma:

> the __selfish__ and greedy Daffy Duck

This does not seem to substantially change the meaning so we merged these synsets
