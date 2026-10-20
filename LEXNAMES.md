## Description

During WordNet development synsets are organized into forty-five lexicographer files based on syntactic category and logical groupings.
The format of the lexicographer files is described in wninput(5WN) .

A file number corresponds to each lexicographer file.
File numbers are encoded in several parts of the WordNet system as an efficient way to indicate a lexicographer file name.
The file lexnames lists the mapping between file names and numbers, and can be used by programs or end users to correlate the two.

## File Format

Each line in lexnames contains 3 tab separated fields, and is terminated with a newline character. The first field is the two digit decimal integer file number. (The first file in the list is numbered 00 .) The second field is the name of the lexicographer file that is represented by that number, and the third field is an integer that indicates the syntactic category of the synsets contained in the file. This is simply a shortcut for programs and scripts, since the syntactic category is also part of the lexicographer file's name.
Syntactic Category

The syntactic category field is encoded as follows:

1    NOUN
2    VERB
3    ADJECTIVE
4    ADVERB

 ## Lexicographer Files

The names of the lexicographer files and their corresponding file numbers are listed below along with a brief description each file's contents.

00 	adj.all 	all adjective clusters
01 	adj.pert 	relational adjectives (pertainyms)
02 	adv.all 	all adverbs (_legacy_; see the adverb files below, which all use this number)
03 	noun.Tops 	unique beginner for nouns
04 	noun.act 	nouns denoting acts or actions
05 	noun.animal 	nouns denoting animals
06 	noun.artifact 	nouns denoting man-made objects
07 	noun.attribute 	nouns denoting attributes of people and objects
08 	noun.body 	nouns denoting body parts
09 	noun.cognition 	nouns denoting cognitive processes and contents
10 	noun.communication 	nouns denoting communicative processes and contents
11 	noun.event 	nouns denoting natural events
12 	noun.feeling 	nouns denoting feelings and emotions
13 	noun.food 	nouns denoting foods and drinks
14 	noun.group 	nouns denoting groupings of people or objects
15 	noun.location 	nouns denoting spatial position
16 	noun.motive 	nouns denoting goals
17 	noun.object 	nouns denoting natural objects (not man-made)
18 	noun.person 	nouns denoting people
19 	noun.phenomenon 	nouns denoting natural phenomena
20 	noun.plant 	nouns denoting plants
21 	noun.possession 	nouns denoting possession and transfer of possession
22 	noun.process 	nouns denoting natural processes
23 	noun.quantity 	nouns denoting quantities and units of measure
24 	noun.relation 	nouns denoting relations between people or things or ideas
25 	noun.shape 	nouns denoting two and three dimensional shapes
26 	noun.state 	nouns denoting stable states of affairs
27 	noun.substance 	nouns denoting substances
28 	noun.time 	nouns denoting time and temporal relations
29 	verb.body 	verbs of grooming, dressing and bodily care
30 	verb.change 	verbs of size, temperature change, intensifying, etc.
31 	verb.cognition 	verbs of thinking, judging, analyzing, doubting
32 	verb.communication 	verbs of telling, asking, ordering, singing
33 	verb.competition 	verbs of fighting, athletic activities
34 	verb.consumption 	verbs of eating and drinking
35 	verb.contact 	verbs of touching, hitting, tying, digging
36 	verb.creation 	verbs of sewing, baking, painting, performing
37 	verb.emotion 	verbs of feeling
38 	verb.motion 	verbs of walking, flying, swimming
39 	verb.perception 	verbs of seeing, hearing, feeling
40 	verb.possession 	verbs of buying, selling, owning
41 	verb.social 	verbs of political and social activities and events
42 	verb.stative 	verbs of being, having, spatial relations
43 	verb.weather 	verbs of raining, snowing, thawing, thundering
44 	adj.ppl 	participial adjectives
50 	contrib.colloq 	contributed colloquialisms
51 	contrib.plwn 	contributed synsets from plWordNet

## Adverb Lexicographer Files

OEWN splits the legacy `adv.all` file into a set of more descriptive adverb
categories, described in [ADVERBS.md](ADVERBS.md):

adv.manner 	manner adverbs
adv.speaker_oriented 	speaker oriented adverbs
adv.frequency 	frequency adverbs
adv.temporal 	time, date adverbs
adv.spatial 	spatial, location adverbs
adv.degree 	degree, intensity adverbs
adv.domain 	domain, scope, context adverbs
adv.focus 	focus adverbs
adv.contrast 	contrastive adverbs

These files are not assigned new file numbers. Sense keys are a legacy feature
inherited from Princeton WordNet, so every one of these files keeps `02`, the
file number of the legacy `adv.all`, and no sense keys change when a synset
moves between adverb categories.
