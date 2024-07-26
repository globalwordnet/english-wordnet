/**
 *  Open English WordNet 2023 (better maintained WordNet)
 *  Script to download, decompress, parse and process into JSON
 *  151937 terms, phrases: 67444, words: 84493, 45 concept categories
 *  119801 definiton sets ( multiple defs per term & some terms share defs)
 *  like "motion" "person", and 5 Part-of-Speech categories:
 *  ["n", "v", "r", "a", "s"]: noun, verb, adverb, adj, satellite adj*
 *  
 *  vtempest (2024) https://github.com/vtempest/wiki-phrase-tokenizer | MIT License
 */
const fs = require("fs");
const zlib = require("zlib");
const axios = require("axios");
const { XMLParser } = require("fast-xml-parser");

const OPTION_MAX_SYNONYMS = 5;
const OPTION_PRINT_SPACING = 2;
const OPTION_ADD_DEFINITIONS = 1;

const url =
  "https://github.com/globalwordnet/english-wordnet/releases/download/2023-edition/english-wordnet-2023.xml.gz";
const gzipOutputPath = "./data/english-wordnet-2023.xml.gz";
const xmlFilePath = "./data/english-wordnet-2023.xml";
const jsonOutputPath = "./data/english-wordnet-2023.json";
const outputPathDict = "./data/dictionary-152k.json";
const outputPathIndex = "./data/dictionary-index-152k.json";
const pos_categories = ["n", "v", "r", "a", "s"]; //a and s is for adjectives
const stringExampleIntro = ",  Example: ";
const categories = [
  "adj.all",
  "adj.pert",
  "adv.all",
  "noun.Tops",
  "noun.act",
  "noun.animal",
  "noun.artifact",
  "noun.attribute",
  "noun.body",
  "noun.cognition",
  "noun.communication",
  "noun.event",
  "noun.feeling",
  "noun.food",
  "noun.group",
  "noun.location",
  "noun.motive",
  "noun.object",
  "noun.person",
  "noun.phenomenon",
  "noun.plant",
  "noun.possession",
  "noun.process",
  "noun.quantity",
  "noun.relation",
  "noun.shape",
  "noun.state",
  "noun.substance",
  "noun.time",
  "verb.body",
  "verb.change",
  "verb.cognition",
  "verb.communication",
  "verb.competition",
  "verb.consumption",
  "verb.contact",
  "verb.creation",
  "verb.emotion",
  "verb.motion",
  "verb.perception",
  "verb.possession",
  "verb.social",
  "verb.stative",
  "verb.weather",
  "adj.ppl",
];

async function downloadFile(url, outputPath) {
  const writer = fs.createWriteStream(outputPath);
  const response = await axios({
    url,
    method: "GET",
    responseType: "stream",
  });

  response.data.pipe(writer);

  return new Promise((resolve, reject) => {
    writer.on("finish", resolve);
    writer.on("error", reject);
  });
}

function decompressGzip(inputPath, outputPath) {
  return new Promise((resolve, reject) => {
    const gunzip = zlib.createGunzip();
    const inputStream = fs.createReadStream(inputPath);
    const outputStream = fs.createWriteStream(outputPath);

    inputStream.pipe(gunzip).pipe(outputStream);

    outputStream.on("finish", () => {
      console.log("Decompression completed");
      resolve();
    });

    outputStream.on("error", reject);
  });
}

async function parseXMLToJSON(xmlFilePath, jsonOutputPath) {
  const oewnXML = fs.readFileSync(xmlFilePath, "utf8");

  const parser = new XMLParser({
    ignoreAttributes: false,
    allowBooleanAttributes: true,
    attributeValueProcessor: (name, val) => {
      return val.replace(/oewn[_-]/g, "").split("__")[0];
    },
    tagValueProcessor: (tagName, tagValue) => {
      if ("Pronunciation".includes(tagName)) return;
      var o = {};
      o[tagName] = tagValue;
      return o;
    },
  });

  let jObj = parser.parse(oewnXML);
  const jsstr = JSON.stringify(jObj, null, 2);

  await fs.promises.writeFile(jsonOutputPath, jsstr, "utf8");
  console.log("Parsing completed and JSON file saved");
}

async function processWordNetData() {
  const oewnXML = await fs.promises.readFile(jsonOutputPath, "utf8");
  const wn = JSON.parse(oewnXML);

  const { Synset, LexicalEntry } = wn.LexicalResource.Lexicon;

  let definitionsObj = {};

  // PROCESS definitions

  const processedSynset = Synset.map((s) => ({
    id: parseInt(s["@_id"]?.replace(/oewn-/g, "")),
    def: s.Definition?.Definition,
    example: s.Example?.Example,
    synonyms: s["@_members"]
      .replace(/oewn-/g, "")
      ?.split(" ")
      .map((syn) => syn.replace(/-.$/g, "").replace(/_/g, " "))
      .join(", "),
    pos: s["@_partOfSpeech"],
    cat: categories.indexOf(s["@_lexfile"]),
  }));

  processedSynset.forEach((s) => {
    const { id, ...rest } = s;
    definitionsObj[id] = rest;
  });

  //PROCESS TERMS INDEX

  let dictionaryObj = {};

  const processedLexicalEntry = LexicalEntry.map((lex) => ({
    writtenForm: lex.Lemma["@_writtenForm"],
    default_pos: lex.Lemma["@_partOfSpeech"],
    senses: Array.isArray(lex.Sense)
      ? lex.Sense.map((lex_s) =>
          parseInt(lex_s["@_synset"].replace("oewn-", ""))
        )
      : [parseInt(lex.Sense["@_synset"].replace("oewn-", ""))],
  }));

  processedLexicalEntry.forEach((lex) => {
    dictionaryObj[lex.writtenForm.toLowerCase()] = {
      defs: lex.senses,
      pos: lex.default_pos,
    };
  });

  //PROCESS SYNONYMS

  var synonymsObj = Object.keys(dictionaryObj)
    .map((word) => ({ term: word, termObj: dictionaryObj[word] }))
    .map((indexObj) => ({
      pos: indexObj.termObj.pos,
      term: indexObj.term,
      defs: indexObj.termObj.defs.map((defID) => definitionsObj[defID]),
    }))
    .map((termObj) => {
      var firstDef = termObj.defs[0];
      var synonyms = [],
        cat =
          typeof firstDef.cat == "string"
            ? categories.indexOf(firstDef.cat)
            : firstDef.cat;

      if (termObj.pos == -1 || cat == -1) console.log(termObj, firstDef);

      for (var def of termObj.defs)
        synonyms = synonyms.concat(def.synonyms.split(", "));

      //Preserve Casing for Display
      var originalCase = synonyms.filter(
        (s) => s.toLowerCase() == termObj.term && s != termObj.term
      )?.[0];

      //dedupe and remove the word being defined
      synonyms = [...new Set(synonyms)]
        .filter((s) => s.toLowerCase() != termObj.term)
        .slice(0, OPTION_MAX_SYNONYMS) //max
        .join(",");

      var defs = termObj.defs.map(
        (def) => def.def + (def.example ? stringExampleIntro + def.example : "")
      );

      var defObj = {
        term: termObj.term,
        cat,
        defs,
        pos: termObj.pos,
        syns: synonyms,
      };

      if (originalCase) defObj.caps = originalCase;
      if (!OPTION_ADD_DEFINITIONS) delete defObj.defs;
      if (!defObj.syns.length) delete defObj.syns;

      return defObj;
    });

  //dict map keyed by term
  var dictionaryMap = {};
  synonymsObj.forEach((s) => {
    const { term, ...rest } = s;
    dictionaryMap[term] = rest;
  });
  
//sort alphabetically 
dictionaryMap = Object.keys(dictionaryMap)
.sort()
.reduce((acc, key) => {
  acc[key] = dictionaryMap[key];
  return acc;
}, {});


  await fs.promises.writeFile(
    outputPathDict,
    JSON.stringify(dictionaryMap, null, OPTION_PRINT_SPACING)
  );

  var termsIndex = Object.keys(dictionaryMap).sort();
  await fs.promises.writeFile(
    outputPathIndex,
    JSON.stringify(termsIndex, null, OPTION_PRINT_SPACING)
  );
  
}

async function main() {
  try {
    console.log("Starting download...");
    await downloadFile(url, gzipOutputPath);
    console.log("Starting decompression...");
    await decompressGzip(gzipOutputPath, xmlFilePath);
    console.log("Starting parsing...");
    await parseXMLToJSON(xmlFilePath, jsonOutputPath);
    console.log("Processing WordNet data...");
    await processWordNetData();

    // Optionally, delete the temporary files
    try {
      await fs.promises.unlink(gzipOutputPath);
      await fs.promises.unlink(xmlFilePath);
      await fs.promises.unlink(jsonOutputPath);
      console.log("Temporary files deleted");
    } catch (err) {
      console.error("Error deleting temporary files:", err);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
}

main();

/*
 * ["n", "v", "r", "a", "s"]: noun, verb, adverb, adj, satellite adj*
 * PS: 's' stands for "satellite adjective"
 * These are relational adjectives that are synonymous to a root adjective
 * They are typically derived from or related to nouns
 * Often used to express a relation or pertaining to something
 * 'a' adjective: "happy" (describes a state or quality)
 * 's' adjective: "dental" (relates to teeth, derived from the noun "tooth/teeth")


00 - all adjective clusters
01 - relational adjectives (pertainyms) eg: acoustic
02 - all adverbs
03 - unique beginner for nouns
04 - nouns denoting acts or actions eg: gift
05 - nouns denoting animals eg: tadpole
06 - nouns denoting man-made objects eg: tag
07 - nouns denoting attributes of people and objects eg: talkativeness
08 - nouns denoting body parts eg: finger
09 - nouns denoting cognitive processes and contents eg: flavor
10 - nouns denoting communicative processes and contents eg: fluency
11 - nouns denoting natural events eg: germination
12 - nouns denoting feelings and emotions eg: glee
13 - nouns denoting foods and drinks eg: gluten
14 - nouns denoting groupings of people or objects eg: government
15 - nouns denoting spatial position eg: harbor
16 - nouns denoting goals eg: incentive
17 - nouns denoting natural objects (not man-made) eg: river
18 - nouns denoting people eg: artison
19 - nouns denoting natural phenomena eg: aurora
20 - nouns denoting plants eg: asparagus
21 - nouns denoting possession and transfer of possession eg: assignment
22 - nouns denoting natural processes eg: biosynthesis
23 - nouns denoting quantities and units of measure eg: bit
24 - nouns denoting relations between people or things or ideas eg: bond
25 - nouns denoting two and three dimensional shapes eg: bulge
26 - nouns denoting stable states of affairs eg: calcification
27 - nouns denoting substances eg: calcium
28 - nouns denoting time and temporal relations eg: centenary
29 - verbs of grooming, dressing and bodily care eg: cleanse
30 - verbs of size, temperature change, intensifying, etc. eg: elongate
31 - verbs of thinking, judging, analyzing, doubting eg: elucidate
32 - verbs of telling, asking, ordering, singing eg: entice
33 - verbs of fighting, athletic activities eg: fortify
34 - verbs of eating and drinking eg: gobble
35 - verbs of touching, hitting, tying, digging eg: grate
36 - verbs of sewing, baking, painting, performing eg: ideate
37 - verbs of feeling eg: impress
38 - verbs of walking, flying, swimming eg: inspect
39 - verbs of seeing, hearing, feeling eg: listen
40 - verbs of buying, selling, owning eg: loan
41 - verbs of political and social activities and events eg: lobby
42 - verbs of being, having, spatial relations eg: locate
43 - verbs of raining, snowing, thawing, thundering eg: overcast
44 - participial adjectives
*/
