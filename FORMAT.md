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
    `s` (adjective satellite), `r` (adverb) or `e` (name, i.e., proper noun)

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

Names (proper nouns) are kept separate from the common vocabulary. Name synsets
are defined in the `name.*` files (e.g., `name.location.yaml`), have 
`partOfSpeech: e` and their IDs end in `-e` (e.g., `08337853-e`). Their entries 
have the part of speech `e` and are stored in the `entries-X-name.yaml` files
(e.g., `entries-A-name.yaml`). Names may also be added as members of a common 
noun synset, in which case their entry has part of speech `e` but refers to a 
synset ending in `-n`. Sense keys of names use the same lexicographer file 
number as the corresponding `noun.*` file.

All members of a synset should be listed in a comment before the synset

## Synset Relations

Synset relations are followed by a comment giving all members of the target 
synset.

Symmetric pairs (`hypernym` and `hyponym`) should be added, when defining the 
synset relation.

### Relations between names and the common vocabulary

How a relation between a name (a synset ending `-e`, or a sense of one) and the
common vocabulary is stored depends on the `names_layout` setting in
`settings.toml`, which [EWE](https://github.com/jmccrae/ewe) uses when saving.
Both layouts can be read.

* `merged` (the default): the relation is stored where it was made, so the
  common files (`noun.*.yaml`, `entries-a.yaml`, ...) can refer to names, and
  are only complete together with the name files.
* `separate`: the relation is stored **only in the name files**, on the name
  end, so that the common files are self-contained without the names. As the
  relation is the other way round there, it is written in its inverse form:
    * for synsets with the inverse relation: a common synset that has
      `domain_region: [08337853-e]` is listed as `has_domain_region` on the 
      name synset, `mero_member` as `holo_member`, `hypernym` as `hyponym`, and 
      so on. `also`, `similar` and `attribute` are their own inverse and are 
      stored on the name as well.
    * for senses as `is_<relation>_of` on the name sense, listing the senses that
      have the relation, e.g. a sense with `pertainym: [paris%1:15:00::]` is 
      listed as `is_pertainym_of` on the sense of `paris%1:15:00::`. The
      relations that already have an inverse name keep it (`has_domain_topic`,
      `has_domain_region`, `is_exemplified_by`), and the symmetric ones 
      (`derivation`, `antonym`, `similar`, `also`) are written on both senses 
      as before.

  The inverse is not written on the common side, and the tools add it when
  loading (`scripts/from_yaml.py` does this in `add_inverse_sense_rels` and 
  `fix_synset_rels`), so the set of relations is the same in both layouts. 
  Only the order of relations within a synset or sense may differ.

## Examples

Examples typically start and end with `&quot;`. If a source is needed for an 
example please include this after the final `&quot;` with  two dashes, e.g.,

    <Example>&quot;the harder the conflict the more glorious the triumph&quot;--Thomas Paine</Example>

## Style constraints

* Please use two spaces as indents
* Use self-closing tags whenever possible
* Use minimal whitespace
