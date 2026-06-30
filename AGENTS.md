# Introduction

Open English Wordnet is an open-source fork of the Princeton WordNet project,
which constructs a machine-readable dictionary of English. Ensuring the overall
consistency and quality of the resource is a key goal.

# Validation

All commits to the repository should be first verified by running the automatic
checking script as follows

```
python scripts/validate.py
```

# English Wordnet Editor (EWE) tool

The EWE tool is used to make most changes and to explore the data correctly. 
The `ewe` binary should be available in the root of the repository. If it 
is not the repository https://github.com/jmccrae/ewe should be checked out 
and the release binary `ewe-cli` should be symlinked into the root of this folder

This can be used to examine the contents of the repository for example

```
> ./ewe word ewe
02414645-n: ewe
    female sheep
    hypernym: 02414351-n (sheep)
    mero_part: 02373012-n (udder, bag)
```

Changes can be made be made by using the `automaton` mode of EWE and giving the 
data as YAML such as follows:

```
> ./ewe automaton - <<END
- add_entry:
    synset: 00001740-n
    lemma: bar
    pos: n
END
```

# Structure of Wordnet

The word consists of entries and synsets. Entries are the lemmas and are identified
by the lemmas. A synset is identified by its code which consists of 8 digits and 
the part of speech separated by a hyphen (e.g., `00001740-n`). You should never
create new synset identifiers; the EWE tool will create new identifiers. In 
automaton scripts you may use the special identifier `last` to refer to the most
recently created synset.

Each synset must have a definition. Definitions in Wordnet are short (3-15 words)
and should consist of a genus and a differentia. For example 'ewe' is a 'sheep'
and is differentiated by the quality 'female'. 

Each synset should have at least one link. For nouns and verbs the synset must
have at least one hypernym. 

# Adding a new synset

If requested to add a new synset the following procedure should be followed

1. Find a suitable definition and consider any other lemmas that may be appropriate
2. Consider any relevant links, especially hypernyms and use the `ewe word` 
   tool to find the synset identifier
3. Identify the lexfile that this fits best in. See below for a list of lexfile
   names.
4. Run the automaton tool to make the change

```
> ./ewe automaton - <<END
- add_synset:
    definition: <ADD DEFINITION HERE>
    lexfile: <ADD LEXFILE HERE>
    pos: n
    lemmas:
    - lemma1
    - lemma2
- add_relation:
    source: last
    relation: hypernym
    target: <TARGET ID>
END
```

# Updating relations

Relations can be between synsets or between senses. Links between senses require
the lemma or sense ID to be identified.

Sense IDs can be identified by using the flag as follows

```
> ./ewe word leopard --sense-ids
14789601-n: leopard
    Sense: leopard%1:27:00::
    the pelt of a leopard
    hypernym: 14788240-n (fur, pelt)

02131037-n: leopard, Panthera pardus
    Sense: leopard%1:05:00::
    large feline of African and Asian forests usually having a tawny coat with black spots
    hypernym: 02130460-n (big cat, cat)
    hyponym: 02131250-n (leopardess); 02131321-n (panther)
```

This can be specified for the `delete_relation` action as follows

```
> ./ewe automaton - <<END
- delete_relation
    source: 00001740-n
    source_sense: "example%1:09:00::"
    target: 00001741-n
    target_sense: "target%1:10:00::'"
END
```

You can also query by lemma when updating senses

```
> ./ewe automaton - <<END
- delete_relation
    source: 00001740-n
    source_sense: lemma=example
    target: 00001741-n
    target_sense: lemma=target
END
```

The full list of relations is given in the appendix.

## Entries

Entries (or members or lemmas) are the words that are part of synset. When
moving an entry to another synset, then the `move_entry` action reduces the 
risk of data loss.

```
> ./ewe automaton - <<END
- move_entry:
    synset: 00001740-n
    lemma: bar
    target_synset: 00001741-n
END
```

Alternatively adding or removing entries can be done as follows

```yaml
- add_entry:
    synset: 00001740-n
    lemma: bar
    pos: n
- delete_entry:
    synset: 00001740-n
    lemma: bar
```

## Deleting synsets

Synsets should only be removed under a few special circumstances. Firstly,
if we wish to merge senses of existing synsets then we should identify which 
synset we will keep and which ones we will deprecate. In rare cases, there
may be a word that genuinely does not exist in English and so we can remove this
but only do this if explicitly asked. Synsets may also be removed if introduced
by errors. The command to remove a synset requires a reason with a GitHub issue
number in parentheses after and a preferred synset for annotation

```yaml
- delete_synset:
    synset: 00001740-n
    reason: "Duplicate (#123)"
    superseded_by: 00001741-n
```

## Other commands

You may change a definition

```yaml
- change_definition
    synset: 00001740-n
    definition: new definition
```

Examples may be added or removed. Sources for examples are optional

```yaml
- add_example:
    synset: 00001740-n
    example: This is an example
    source: This is a source
- delete_example:
    synset: 00001740-n
    number: 1
```

You may need to change the ILI or Wikidata identifier

```yaml
- change_ili:
    synset: 00001740-n
    ili: i1
- change_wikidata:
    synset: 00001740-n
    wikidata: Q1
```

# Appendix

## Lexfiles

noun.Tops
noun.act
noun.animal
noun.artifact
noun.attribute
noun.body
noun.cognition
noun.communication
noun.event
noun.feeling
noun.food
noun.group
noun.location
noun.motive
noun.object
noun.person
noun.phenomenon
noun.plant
noun.possession
noun.process
noun.quantity
noun.relation
noun.shape
noun.state
noun.substance
noun.time
verb.body
verb.change
verb.cognition
verb.communication
verb.competition
verb.consumption
verb.contact
verb.creation
verb.emotion
verb.motion
verb.perception
verb.possession
verb.social
verb.stative
verb.weather
adj.all
adj.pert
adj.ppl
adv.all

## Synset Relations

also
attribute
causes
domain_region
domain_topic
exemplifies
entails
has_domain_region
has_domain_topic
is_exemplified_by
holo_location
holo_member
holo_part
holo_portion
holo_substance
holonym
hypernym
hyponym
instance_hypernym
instance_hyponym
is_caused_by
is_entailed_by
mero_location
mero_member
mero_part
mero_portion
mero_substance
meronym
similar
other
feminine
masculine

## Sense Relations

antonym
also
participle
pertainym
derivation
domain_topic
has_domain_topic
domain_region
has_domain_region
exemplifies
is_exemplified_by
is_pertainym_of
similar
agent
material
event
instrument
location
by_means_of
undergoer
property
result
state
uses
destination
body_part
vehicle
other

