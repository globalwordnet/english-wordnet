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
