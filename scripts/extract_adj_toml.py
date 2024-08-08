import yaml
import toml

data = yaml.safe_load(open('src/yaml/adj.all.yaml'))

similars = {}
defs = {}
members = {}
ssids = []

for ssid, synset in data.items():
    if synset['partOfSpeech'] == 's':
        similars[ssid] = synset['similar'][0]
        ssids.append(ssid)
    elif synset['partOfSpeech'] == 'a':
        ssids.append(ssid)
    defs[ssid] = synset['definition'][0]
    members[ssid] = synset['members']

data = {}
i = 0
for ssid in ssids:
    if ssid not in similars:
        data[ssid] = {'definition': defs[ssid], 'members': ", ".join(members[ssid]) }
    else:
        data[ssid] = {'definition': defs[ssid], 'members': ", ".join(members[ssid]) ,
                      'hypernym': ", ".join(members[similars[ssid]]),
                      'hypernym_definition': defs[similars[ssid]]}
    if len(data) > 1000:
        with open(f"adj/adj_{i}.toml", "w") as f:
            f.write("""# - `hypernym`: For these it must be the case that "if something is X, then it is also Y". For example, if something is moribund then it is also dying. 
# - `antonym`: These words have opposite meanings, they are often prefixed with 'un-' or 'dis-'. For example, if something is moral then it is not immoral.
# - `pertainym`: The word means 'of or pertaining to X' and is often morphologically related. For example, if something is 'oceanic' then it is of or pertaining to the ocean.
# - `scalar`: The adjective refers to a value on a scale. For example, 'hot' relates to 'temperature', 'wide' relates to 'width'.
# - `quality`: This refers to an abstract noun derived from the adjective, often by a suffix such as '-ness' of '-ity'. For example, 'hot' relates to 'hotness', 'wide' relates to 'wideness'.
# - `present_participle`: This means that the adjective is derived from a verb meaning performing the action currently or repeatedly. The adjective is often the '-ing' form of the verb. For example, 'running' relates to 'run'.
# - `past_participle`: This means as a result of the verb and is mostly the '-ed' form of the verb. For example, 'run' relates to 'ran'.
# - `potential`: This means that it is possible for this verb to be done to something and is often the '-able' form of the verb. For example, 'readable' relates to 'read'.
# - `lack`: The adjective means the lack of something, and often corresponds to the '-less' form of the adjective. For example, 'careless' relates to 'care'.
# - `fullness`: The adjective means being full of something, and often corresponds to the '-ful' form of the adjective. For example, 'careful' relates to 'care'.
# - `resembles`: The adjective means it resembles something, and often corresponds to the '-like' form of the adjective. For example, 'childlike' relates to 'child'.
""")
            toml.dump(data, f)
            data = {}
            i += 1
