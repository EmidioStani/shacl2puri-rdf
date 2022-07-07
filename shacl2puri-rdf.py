from pathlib import Path
from typing import Optional
from unicodedata import decimal

import yaml
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS


def get_config(file):
    my_path = Path(__file__).resolve()  # resolve to get rid of any symlinks
    config_path = my_path.parent / file
    with config_path.open() as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config

config = get_config("config.yaml")

g = Graph()
g.parse(config['input']['file'] , format=config['input']['format'])

sparql_datatype_properties = """
    CONSTRUCT {
        ?path rdf:type rdf:Property .
        ?path rdf:type owl:DatatypeProperty .
        ?path rdfs:range ?type .
        ?path rdfs:comment ?desc . 
    }
    WHERE {
        ?s rdf:type shacl:NodeShape .
        ?s shacl:property ?p .
        ?p shacl:path ?path .
        ?p shacl:datatype ?type .
        ?p shacl:description ?desc .
       FILTER (strstarts(str(?path), 'http://data.europa.eu/m8g/'))
    }
"""

qres = g.query(sparql_datatype_properties)
goutput = Graph()
for triple in qres:        
    goutput.add(triple)
goutput.serialize(destination='output.txt', format='turtle')

sparql_select_subjects = """
    SELECT distinct ?s
    WHERE {
        ?s ?p ?o
    }
"""
def query_same_subject(subject):
    query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o . FILTER (?s = <" + subject + "> )}"
    return query

qsubject_list = goutput.query(sparql_select_subjects)
for row in qsubject_list:
    subject= str(row[0])
    qsamesubject = goutput.query(query_same_subject(subject))
    tempgraph = Graph()
    for triple in qsamesubject:
        tempgraph.add(triple)
    filepath =  config['output']['folder'] + "/" + row[0].rsplit('/', 1)[-1]
    tempgraph.serialize(destination= filepath + '.ttl', format='turtle')
    tempgraph.serialize(destination= filepath + '.nt', format='nt')
    tempgraph.serialize(destination= filepath + '.rdf', format='xml')




