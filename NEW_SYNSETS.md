# Guidelines for the addition of new synsets

New synsets should be added with some caution to Open English Wordnet. This document
describes the criteria that should be applied before introducing a new synset 
to the resource.

There are five basic criteria that need to be applied:

1. Significance
2. Non-compositionality
3. Distinction
4. Well-defined
5. Linked

All criteria can be ignored in special cases. If you think you have a special
case please [create an issue](https://github.com/globalwordnet/english-wordnet/issues/new).

NB: *Many existing synsets do not fit the criteria given below, this is not 
a reason to add more synsets of poor quality*

## Significance

A concept in Open English Wordnet should be significant, this means that it should
be possible to easily find **at least 100 examples** of the usage of the word 
with this meaning. This can be done by using a search interface such as 
[Sketch Engine](http://sketchengine.eu) or other corpus search interface.

NB: *At some point we will standardise and integrate this process into the workflow*

In the case that a new sense of an existing word is being proposed, then it 
should be possible to propose collocates that occur with this sense of the word
and these can be used to find and distinguish examples.

Open English Wordnet is a dictionary not an encyclopedia. For this reason, it should
not contain long lists of people, places, organizations, etc. Proper nouns are
generally not expected to be included in the resource and many kinds of common 
nouns for narrow domains or geographical usage should not be included, examples 
of this would include elements of different cuisines around the world. As a rule 
of thumb, if there is a Wikipedia page for this concept it should not be in
Open English Wordnet

NB: *Deeper integration of Wikipedia/Wikidata is planned to allow these concepts
to be referred to from Open English Wordnet*

## Non-compositionality

One of the goals of Open English Wordnet is to support annotation. If a word or term
is already covered by Open English Wordnet it should not be added. 

For multiword terms, this means that the meaning of the term should not be 
derivable from its components, e.g., "French Army" could be tagged with the 
synsets for "French" and "Army"; in contrast "French Academy" refers not to 
any French Academy but a specific organization.

For single words, the word should not be derived in a systematic manner, these
include:

* Converting a verb to a noun or adjective by adding '-ing' or '-ed'
* Converting an adjective to an adverb by adding '-ly'
* Productive prefixes such as 'non-', 'un-'
* Systematic polysemy: e.g., using a part to refer to a whole 
** Example: "congress" meaning the "members of congress"

## Distinction

The concept should be distinct from other concepts in the wordnet. You should
think about and check relevant synonyms. This should probably be considered in
terms of a substitution check, e.g.,

"happy" and "felicitous" are synonyms, `ewn-01052105-s` and the examples can be
substituted, e.g., "a happy life"/"a felicitous outcome". This does not mean 
that they can be substituted in every sense, e.g., "happy to help" but not
*"felicitous to help".

For verbs, two verbs are distinct if they differ in the subject, but not if the 
direct object or any other argument can be substituted with a quantifier such as
"something" or "someone". For example, "to eat" and "to eat something" are not 
distinct senses. However, "to change" and "to change something" are distinct senses
as the subject has a different semantic role.

## Well-defined

It should be possible to easily write a definition for this concept that is 
distinct from other concepts in Open English Wordnet. A good definition consists of
a *genus* and a *differentia*

* **Genus**: The type of the thing, often the hypernym
* **Differentia**: Something that makes this word unique

A good definition:

> a piece of furniture having a smooth flat top that is usually supported by one or more vertical legs

Bad definition:

> a piece of furniture

> used for eating

In addition an example should be provided with a link to a website where the 
example is used as follows:

```xml
  <Synset id="ewn-...">
    ...
    <Example dc:source="https://en.wikipedia.org/wiki/Example.com">
    The example domains have one subdomain name defined in the Domain Name System
    </Example>
    ...
  </Synset>
```

## Linked

The synset should be possible to link into the graph

* **Nouns**: A hypernym must be identified
* **Verbs**: A hypernym or an antonym must be identifier. Verbs should also have
    at least one subcategorization frame.
* **Adjectives**: They should be marked as similar to a non-satellite adjective 
    (in which case they are satellites) **or** antonyms of a non-satellite 
    adjective **or** hypernyms of an adjective
* **Adverbs**: No clear guidelines but at least one links should be proposed.

The more links that can be provided the better a synset is.

## Irregular forms

If a word has an irregular inflection that is not covered by the [rules in morphy](https://wordnet.princeton.edu/documentation/morphy7wn) then it shoule be added as a variant form:

For example:
```
child:
  n:
    form:
    - children
```

```
outwear:
  v:
    form:
    - outwore
    - outworn
```
