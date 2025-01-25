# Contributing

By participating in this project, you agree to abide by the [code of conduct](#code-of-conduct).

## Issues

One of the easiest ways to contribute is to log an issue. If the issue refers to a single synset, please include

* The synset ID (this should be a code like ewn-00001740-n)
* The lemmas of the synset
* The definition of the synset

If the issue refers to multiple synsets please make it clear which files these belong to.

Further, if the solution to the issue is clear, please provide on the following tags for the issue:

* `definition`: The text definition should be updated
* `add relation`: The relation between two synsets (senses) is not correct
* `change relation`: A relation is wrong either in type (e.g., `hypernym` vs. `instance_hypernym`) or target
* `example`: An example should be updated
* `new synset`: A new concept should be introduced. Please first check the [guidelines for adding new sense](NEW_SYNSETS.md) before adding a new synset.
* `remove relation`: A relation should be removed
* `delete synset`: A synset should be deleted. (This is used only rarely for truly nonsense or compositional concepts)
* `synset duplicate`: Two synsets refer to the same concept and should be merged. 
* `synset member`: A new member should be added to or removed from the synset
* `synset split`: A synset represents two distinct concepts and should be split

Please refer to other dictionaries from [this list of dictionaries](DICTIONARIES.md)

## Pull Requests

We love pull requests from everyone. 

Fork, then clone the repo:

    git clone git@github.com:your-username/english-wordnet.git

Please compile all your changes into a single `wn.xml` file

    python scripts/from_yaml.py

Please ensure that your contributions are valid XML

    xmllint --noout --valid wn.xml

Please make sure that the structure is valid

    python scripts/validate.py


Push to your fork and [submit a pull request][pr].

[pr]: https://github.com/globalwordnet/english-wordnet/compare/

At this point you're waiting on us. We like to at least comment on pull requests
within three business days (and, typically, one business day). We may suggest
some changes or improvements or alternatives.

Some things that will increase the chance that your pull request is accepted:

* Make small incremental changes.
* Avoid the use of automatic tools or formatters to keep commits small and trackable.
* Write a [good commit message][commit].

[commit]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html

## Code of conduct

In order to foster an inclusive, kind, harassment-free, and cooperative community, we enforce this code of conduct on our open source projects.

### Summary

Harassment in code and discussion or violation of physical boundaries is completely unacceptable anywhere in our project. Violators will be warned by the core team. Repeat violations will result in being blocked or banned by the core team at or before the 3rd violation.

### In detail

Harassment includes offensive verbal comments related to gender identity, gender expression, sexual orientation, disability, physical appearance, body size, race, religion, sexual images, deliberate intimidation, stalking, sustained disruption, and unwelcome sexual attention.

Individuals asked to stop any harassing behavior are expected to comply immediately.

Maintainers are also subject to the anti-harassment policy.

If anyone engages in harassing behavior, including maintainers, we may take appropriate action, up to and including warning the offender, deletion of comments, removal from the project’s codebase and communication systems, and escalation to GitHub support.

If you are being harassed, notice that someone else is being harassed, or have any other concerns, please contact us immediately

We expect everyone to follow these rules anywhere in our project.

Finally, don't forget that it is human to make mistakes! We all do. Let’s work together to help each other, resolve issues, and learn from the mistakes that we will all inevitably make from time to time.

### Neutrality

Open English Wordnet aims to be a politically neutral resource, however we accept that the description of the language necessarily involves making political statements. In the case where politics are relevant to the particular word, we follow Wikipedia in the definition of political entities, states and so forth. We ask all contributors to avoid political statements when not relevant to the discussion.

### Thanks
Derived from [thoughbot's code of conduct](https://thoughtbot.com/open-source-code-of-conduct)
