import os
from os import path
from pathlib import Path
from typing import Optional
from unicodedata import decimal
from tqdm import tqdm
from time import sleep

import yaml
import json
from rdflib import Graph, Literal, Namespace, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON, JSONLD

g = Graph()

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.addDefaultGraph("http://dbpedia.org")

query2 = """
    PREFIX dct:<http://purl.org/dc/terms/> 
    CONSTRUCT {
    ?category skos:prefLabel ?label .
    ?category skos:broader ?broader .
    } 
    where {
    ?term dct:subject ?category .
    ?category skos:prefLabel ?label .
    OPTIONAL {
    ?category skos:broader ?broader .
    }
    }
"""
offset = 10
limit = 10000

for x in tqdm(range(offset)):
    try : 
        query2_final = query2 + """OFFSET """ + str(x) + """ LIMIT """ + str(limit)
        sparql.setQuery(query2_final)
        sparql.setReturnFormat(JSONLD)
        results = sparql.query()
        triples = results.convert() # this converts directly to an RDFlib Graph object
        g += triples
    except Exception as er:
        print(er)

g.serialize(destination='taxonomy.ttl', format='turtle')