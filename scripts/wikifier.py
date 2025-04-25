# extract_types.py

import os
import requests

def prepare_params(text):
    return {
        'lang': 'en',
        'userKey': 'czckieznqevyvxwemjsdlluxbszhpi',
        'text': text,

        # allow lower-ranked but still relevant entities
        'pageRankSqThreshold': '0.3',
        'applyPageRankSqThreshold': 'true',

        # ignore the 50 most common terms when computing IDF
        'nTopDfValuesToIgnore': '50',

        # return Wikidata class labels and raw Q-IDs
        'wikiDataClasses': 'true',
        'wikiDataClassIds': 'true',

        # we don’t need frequency support scores here
        'support': 'false',

        # include character offsets for each mention
        'ranges': 'true',

        # lower barrier so even lightly-linked entities appear
        'minLinkFrequency': '1',

        # score how well context matches candidate page
        'includeCosines': 'true',

        # drop extremely ambiguous mentions
        'maxMentionEntropy': '2'
    }


def get_types_from_dbpedia(entity_uri):
    endpoint = "https://dbpedia.org/sparql"
    query = f"""
    SELECT ?type WHERE {{
        <{entity_uri}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type .
        FILTER(STRSTARTS(STR(?type), "http://dbpedia.org/ontology/"))
    }}
    """
    r = requests.get(endpoint, params={"query": query, "format": "json"})
    r.raise_for_status()
    results = r.json()["results"]["bindings"]
    return [res["type"]["value"].split("/")[-1] for res in results]

def extract_types_from_text(text):
    params = prepare_params(text)
    response = requests.post("http://www.wikifier.org/annotate-article", data=params)
    response.raise_for_status()
    annotations = response.json().get("annotations", [])

    result = {}
    for ann in annotations:
        if "url" not in ann or "title" not in ann:
            continue
        wiki_url = ann["url"]
        if "en.wikipedia.org/wiki/" not in wiki_url:
            continue
        entity_uri = wiki_url.replace("https://en.wikipedia.org/wiki/", "http://dbpedia.org/resource/") \
                             .replace("http://en.wikipedia.org/wiki/", "http://dbpedia.org/resource/")
        try:
            types = get_types_from_dbpedia(entity_uri)
            result[ann["title"]] = types
        except Exception as e:
            result[ann["title"]] = [f"ERROR: {e}"]
    return result

def extract_types_from_file(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    return extract_types_from_text(text)

def write_result_to_file(output_path, data):
    dir_path = os.path.dirname(output_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        for entity, types in data.items():
            out.write(f"# Entity: {entity}\n")
            for t in types:
                out.write(f"{t}\n")
            out.write("\n")
