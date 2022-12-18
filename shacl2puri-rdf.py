import os
from os import path
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

def read_files(graph, folder):
    for filename in os.listdir(folder):
        file_path = path.relpath(folder + "/" + filename)
        # checking if it is a file
        if os.path.isfile(file_path):
            print("reading: " + file_path)
            file = open(file_path, 'r')
            # print(file.read())
            graph.parse(source=file_path, format=config['input']['format'])
            print(len(graph))
            file.close()
    return graph

config = get_config("config.yaml")

g = Graph()
folder = config['input']['folder']
g = read_files(g, folder)
# print(len(g))
#g.parse(config['input']['file'] , format=config['input']['format'])

#  ?path rdfs:range ?type .
sparql_datatype_properties = """
    CONSTRUCT {
        ?path rdf:type rdf:Property .
        ?path rdf:type owl:DatatypeProperty .

        ?path rdfs:comment ?desc .
        ?path rdfs:label ?name .
        ?path rdfs:isDefinedBy <http://data.europa.eu/m8g> .

    }
    WHERE {
        ?s rdf:type shacl:NodeShape .
        ?s shacl:property ?p .
        ?p shacl:path ?path .
        ?p shacl:datatype ?type .
        ?p shacl:description ?desc .
        ?p shacl:name ?name .

        ?sclass rdf:type shacl:NodeShape .
        ?sclass shacl:targetClass ?class .
        OPTIONAL {?sclass shacl:description ?classdesc .} .
        OPTIONAL {?sclass shacl:name ?classname} .

        FILTER (strstarts(str(?path), 'http://data.europa.eu/m8g/'))
        FILTER (strstarts(str(?class), 'http://data.europa.eu/m8g/'))


    }
"""
#  ?relpath rdfs:range ?relclass .
sparql_object_properties = """
    CONSTRUCT {
        ?relpath rdf:type rdf:Property .
        ?relpath rdf:type owl:ObjectProperty .

        ?relpath rdfs:comment ?reldesc .
        ?relpath rdfs:label ?relname .
        ?relpath rdfs:isDefinedBy <http://data.europa.eu/m8g> .

    }
    WHERE {
        ?sclass2 rdf:type shacl:NodeShape .
        ?sclass2 shacl:property ?rel .
        ?rel shacl:path ?relpath .
        ?rel shacl:description ?reldesc .
        ?rel shacl:name ?relname .
        ?rel shacl:class ?relclass .
        FILTER (strstarts(str(?relpath), 'http://data.europa.eu/m8g/'))

    }
"""

sparql_classes = """
    CONSTRUCT {
        ?class rdf:type owl:Class .
        ?class rdfs:comment ?classdesc .
        ?class rdfs:label ?classname .

    }
    WHERE {
        ?sclass rdf:type shacl:NodeShape .
        ?sclass shacl:targetClass ?class .
        OPTIONAL {?sclass shacl:description ?classdesc .} .
        OPTIONAL {?sclass shacl:name ?classname} .
        FILTER (strstarts(str(?class), 'http://data.europa.eu/m8g/'))


    }
"""

qres = g.query(sparql_datatype_properties)
qres2 = g.query(sparql_object_properties)
qres3 = g.query(sparql_classes)

goutput = Graph()
for triple in qres:        
    goutput.add(triple)
for triple in qres2:        
    goutput.add(triple)
# for triple in qres3:        
    # goutput.add(triple)
goutput.serialize(destination='output.ttl', format='turtle')

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
    print(filepath)
    tempgraph.serialize(destination= filepath + '.ttl', format='turtle')
    tempgraph.serialize(destination= filepath + '.nt', format='nt')
    tempgraph.serialize(destination= filepath + '.rdf', format='xml')




