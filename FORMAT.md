# Princeton English WordNet Format

The format is the same as that [GlobalWordNet LMF Schema](http://globalwordnet.github.io/schemas/). 
In addition, the following criteria should be followed in creating the resource

## Lexical Entry

There must be a lexical entry for each synset member in the same file as the 
synset. Its ID must be as follows 

    ewn-lemma-p

Where

* `lemma` is the lemma of the word. Any spaces should be replaced by underscores 
    (`_`). Other non-XML characters should be replaced with `-xx-` where xx is 
    a two letter code (e.g., `-lp-` for `(` and `-rp-` for `)`)
* `p` is the part of speech. One of `n` (noun), `v` (verb), `a` (adjective),
    `s` (adjective satellite) or `r` (adverb)

## Senses

Senses must have identifiers that correspond to lexical entry and are of the form

    ewn-lemma-p-XXXXXXXX-YY

* `lemma` and `p` are as for lexical entries
* `XXXXXXXX` is the offset code from Princeton WordNet's 3.1 release (see below for novel synsets)
* `YY` is the position of the word in the synset as a two letter decimal code. 
    Values for this should start from `01` and must exist for all consecutive values
    up to the size of the synset

In addition, senses should have a `dc:identifier` that gives their [sense identifier](https://wordnet.princeton.edu/documentation/senseidx5wn) as in Princeton 
WordNet.

## Synset Relations

Synset relations are followed by a comment giving all members of the synset. 

## Synsets

Synsets have an identifier as follows

    ewn-XXXXXXXX-p

* `XXXXXXXX` is the offset code from Princeton WordNet's 3.1 release. For novel
    synsets the code should start with a `2` and the number should be chosen
    increasingly
* `p` is the part of speech (see lexical entries)

Synsets should also have an `ili` link. When defining novel concepts please 
give the value `ili="in"`.

Synsets should have a `partOfSpeech` and a `dc:subject` which corresponds to the
name of the file being defined

All members of a synset should be listed in a comment before the synset

## Synset Relations

Synset relations are followed by a comment giving all members of the target 
synset.

Symmetric pairs (`hypernym` and `hyponym`) should be added, when defining the 
synset relation.

## Examples

Examples typically start and end with `&quot;`. If a source is needed for an 
example please include this after the final `&quot;` with  two dashes, e.g.,

    <Example>&quot;the harder the conflict the more glorious the triumph&quot;--Thomas Paine</Example>

## Style constraints

* Please use two spaces as indents
* Use self-closing tags whenever possible
* Use minimal whitespace
