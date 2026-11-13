Process for releasing OEWN
--------------------------

All release artefacts (XML, WNDB and RDF) are generated with the
[EWE tool](https://github.com/jmccrae/ewe) (`ewe export`). The `ewe` binary
should be available in the root of the repository (see `AGENTS.md`). In the
commands below `20XX` is the year of the release.

## Editions

Since #1456 the names (proper nouns, part of speech `e`, `-e` synset ids,
`name.*` lexicographer files and `entries-*-name.yaml`) are kept in this
repository next to the common vocabulary. Two editions are released from it,
as before (see the 2025 `downloads.toml`):

| Edition | Files | `ewe export` option | Contents |
| --- | --- | --- | --- |
| Core | `english-wordnet-20XX.*` | `--names exclude` | No names, and nothing that refers to a name. |
| Plus | `english-wordnet-20XX-plus.*` | `--names merged` | Names as ordinary nouns (`-n` ids, `noun.*` lexfiles), as in the plus releases before names had their own part of speech. |

Relations between the common vocabulary and the names are stored only in the
name files (`names_layout = "separate"` in `settings.toml`), so the core edition
contains nothing that refers to a name. Only these two editions are released, as for 2025 (there is no separate
release with the names as `-e` synsets). Every export below is run once per
edition. The remaining `--names` values
are `include` (the default: everything as stored, with names as `-e` synsets
with part of speech `e`, which needs WN-LMF 1.5) and `only` (just the names).
Do not use `include` for WNDB, which has no part of speech for names and
leaves them out.

## 1. Prepare

1. Make sure all pull requests intended for the release are merged and
   `main` is up to date.
2. Validate the data with both checkers. Both must report no errors:

   ```
   python scripts/validate.py
   ./ewe validate
   ```

3. Update the version in `WNDB_License.txt` (this is prepended to every
   WNDB data file) and any release year mentioned in `CITATION.cff`,
   `citation.bib` and `README.md`.
4. Create a working folder for the artefacts and set a few shell variables
   so that every export uses the same metadata:

   ```
   YEAR=20XX
   mkdir -p release
   META="--version $YEAR --email english-wordnet@googlegroups.com"
   CORE="--names exclude"
   PLUS="--names merged"
   ```

`ewe` builds `wordnet.db` from `src/yaml` automatically if it is missing or
older than the sources, so no separate build step is needed.

## 2. XML release

```
./ewe export xml release/english-wordnet-$YEAR.xml $META $CORE \
    --url https://github.com/globalwordnet/english-wordnet
./ewe export xml release/english-wordnet-$YEAR-plus.xml $META $PLUS \
    --url https://github.com/globalwordnet/english-wordnet
```

Neither edition contains part of speech `e`, so both are valid against the
default `WN-LMF-1.4.dtd`. To release against WN-LMF 1.5 instead (which adds
`Lemma/@reconstructed`), add `--lmf-version 1.5` to both commands above; EWE
does not yet default to 1.5. The `DOCTYPE` then names `WN-LMF-1.5.dtd`. Check that each file is valid against the WN-LMF DTD
named in its `DOCTYPE`:

```
xmllint --noout --valid release/english-wordnet-$YEAR.xml
xmllint --noout --valid release/english-wordnet-$YEAR-plus.xml
```

Then compress them:

```
gzip -k release/english-wordnet-$YEAR.xml release/english-wordnet-$YEAR-plus.xml
```

## 3. WNDB release

```
./ewe export wndb release/oewn$YEAR/ $CORE
./ewe export wndb release/oewn$YEAR-plus/ $PLUS
(cd release && zip -r english-wordnet-$YEAR.zip oewn$YEAR/ \
    && zip -r english-wordnet-$YEAR-plus.zip oewn$YEAR-plus/)
```

The license header is taken from `WNDB_License.txt` in the repository root;
use `--license-file` to override it. WNDB has no part of speech for names, so
the core edition simply has none and the plus edition writes them into
`data.noun` and `index.noun` as nouns (`--names include` would leave them out
and `--names only` is an error).

`src/sense-orders.csv` is used automatically. Rows that list synsets which are
not part of the edition being exported (the names, in the core edition) are
still applied to the others. If `ewe` prints warnings of the form `<lemma>
has different set of keys to ordering`, then `src/sense-orders.csv` is out of
sync with the synset identifiers of that edition (for example, a synset was
added or deprecated). Fix `src/sense-orders.csv` (it is checked by
`python scripts/validate.py` once #1404 is merged) before releasing, as the
sense order of the affected lemmas may otherwise not be applied.

Testing:

```
sudo cp release/oewn$YEAR/* /usr/share/wordnet
wordnet novel_lemma_in_this_edition -over
```

## 4. RDF release

```
./ewe export rdf release/english-wordnet-$YEAR.ttl $META $CORE \
    --url https://en-word.net/
./ewe export rdf release/english-wordnet-$YEAR-plus.ttl $META $PLUS \
    --url https://en-word.net/
gzip -k release/english-wordnet-$YEAR.ttl release/english-wordnet-$YEAR-plus.ttl
```

`ewe` declares every lexical entry exactly once, so the previous `rapper`
de-duplication step is no longer needed. Use `--format rdf-xml` for an
RDF/XML serialization if one is required.

## 5. StarDict release

StarDict is not generated by `ewe`, as it depends on a particular Python
library. It is generated from the XML release by `scripts/stardict.py`, which
uses [pyglossary](https://github.com/ilius/pyglossary).

```
pip install pyglossary
python scripts/stardict.py --input release/english-wordnet-$YEAR.xml \
    --output release/english-wordnet-$YEAR-stardict
python scripts/stardict.py --input release/english-wordnet-$YEAR-plus.xml \
    --output release/english-wordnet-$YEAR-plus-stardict
```

This produces `.ifo/.idx/.dict/.syn` files for each edition, which can be
zipped up for release.

## 6. YAML and JSON sources

The YAML source release is exactly the contents of this repository, zipped.
The JSON release is the same tree with each YAML file converted to JSON:

```
git archive --format=zip --prefix=english-wordnet-$YEAR-yaml/ \
    -o release/english-wordnet-$YEAR-yaml.zip HEAD
python - <<END
import glob, json, os, yaml
os.makedirs("release/json/src/yaml", exist_ok=True)
for f in glob.glob("src/yaml/*.yaml"):
    with open(f) as inp:
        data = yaml.load(inp, Loader=yaml.CSafeLoader)
    out = "release/json/" + f[:-len(".yaml")] + ".json"
    with open(out, "w") as outp:
        json.dump(data, outp, ensure_ascii=False)
END
(cd release/json && zip -r ../english-wordnet-$YEAR-json.zip .)
```

No sense index release is made: the fixed sense index offered with the 2025
release was a one-off post-release correction (#1305).

## 7. en-word.net website

The site is the `ewe_dioxus` component of the
[EWE repository](https://github.com/jmccrae/ewe/tree/main/ewe_dioxus), so it
reads the YAML source in this repository directly and rebuilds its database
automatically when the sources are newer (see its README). To publish the new
edition:

1. Copy the release files of both editions into the site's `downloads_dir`.
2. Add a `[[release]]` entry for the new version, listing those files (the
   core files and the `-plus` files, as for 2025), to the site's
   `downloads.toml` (see `downloads.toml.example` in `ewe_dioxus`).
3. Rebuild the site (`dx build --platform web --release --features oewn`)
   and restart the server.

## 8. Creating the release

Create a new release on GitHub and provide a summary of the main issues
handled. Attach the XML (`.xml.gz`), WNDB (`.zip`), RDF (`.ttl.gz`) and
StarDict (`.zip`) files of both editions, and the YAML and JSON source
archives, to the release.
