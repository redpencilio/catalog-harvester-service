from dataclasses import dataclass
from string import Template
import datetime
from typing import Optional
from typing import List
from enum import Enum

from helpers import query, update, generate_uuid
from escape_helpers import sparql_escape_uri, sparql_escape_datetime, sparql_escape_string

from utils import from_binding
from constants import DATA_GRAPH, DCAT_VALIDATION_REQUEST_URI_PREFIX

@dataclass
class DCATValidationRequest():
    shacl_urls: List[str]
    data_urls: List[str]
    shacl_graph: str = None
    data_graph: str = None

    uri: str = None
    id: str = None
    created: datetime.datetime = None

    def __post_init__(self):
        if not self.created:
            self.created = datetime.datetime.now()
        if not self.id:
            self.id = generate_uuid()
        if not self.uri:
            self.uri = DCAT_VALIDATION_REQUEST_URI_PREFIX + self.id
        if not self.shacl_graph:
            self.shacl_graph = f"{self.uri}/shacl-graph/{generate_uuid()}"
        if not self.data_graph:
            self.data_graph = f"{self.uri}/data-graph/{generate_uuid()}"

    def insert(self, graph=DATA_GRAPH):
        query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX dct: <http://purl.org/dc/terms/>

INSERT DATA {
    GRAPH $graph {
        $uri a ext:DCATValidationRequest ;
            mu:uuid $uuid ;
            dct:created $created ;
            dct:modified $modified ;
            $shacl_urls
            $data_urls
            $shacl_graph
            $data_graph
    }
}
        """)

        self.modified = datetime.datetime.now()

        shacl_urls = "\n".join(
            f"ext:shaclURL {sparql_escape_string(shacl_url)} ;"
            for shacl_url in self.shacl_urls
        )
        data_urls = "\n".join(
            f"ext:dataURL {sparql_escape_string(data_url)} ;"
            for data_url in self.data_urls
        )

        shacl_graph = f"ext:shaclGraph {sparql_escape_uri(self.shacl_graph)} ;" \
            if self.shacl_graph else "# no ext:shaclGraph"
        data_graph = f"ext:dataGraph {sparql_escape_uri(self.data_graph)} ;" \
            if self.data_graph else "# no ext:dataGraph"

        query_string = query_template.substitute(
            graph=sparql_escape_uri(graph),
            uri=sparql_escape_uri(self.uri),
            uuid=sparql_escape_string(self.id),
            created=sparql_escape_datetime(self.created),
            modified=sparql_escape_datetime(self.modified),
            shacl_graph=shacl_graph,
            data_graph=data_graph,
            shacl_urls=shacl_urls,
            data_urls=data_urls
        )

        update(query_string)

        return self.uri

def get_dcat_validation_request(uri, graph=DATA_GRAPH) -> DCATValidationRequest:
    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ?id ?uri ?created ?modified ?shacl_graph ?data_graph WHERE {
    GRAPH $graph {
        VALUES ?uri { $uri } .
        ?uri a ext:DCATValidationRequest ;
            mu:uuid ?id ;
            dct:created ?created ;
            dct:modified ?modified ;
            ext:shaclGraph ?shacl_graph ;
            ext:dataGraph ?data_graph .
    }
}
LIMIT 1
    """)

    query_string = query_template.substitute(
        graph=sparql_escape_uri(graph) if graph else "?g",
        uri=sparql_escape_uri(uri)
    )

    query_res = query(query_string)
    bindings = query_res["results"]["bindings"]
    if not bindings:
        raise Exception(f"Validation request not found: <{uri}>")

    binding = bindings[0]
    dcat_validation_request = from_binding(
        DCATValidationRequest, binding,
        extra=dict(
            shacl_urls=get_shacl_urls(uri),
            data_urls=get_data_urls(uri)
        )
    )

    return dcat_validation_request

def get_shacl_urls(uri, graph=DATA_GRAPH) -> List[str]:
    query_template = Template("""
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>

SELECT ?shacl_url WHERE {
    GRAPH $graph {
        $uri a ext:DCATValidationRequest ;
            ext:shaclURL ?shacl_url .
    }
}
    """)

    query_string = query_template.substitute(
        graph=sparql_escape_uri(graph) if graph else "?g",
        uri=sparql_escape_uri(uri)
    )

    query_res = query(query_string)
    return [
        binding["shacl_url"]["value"]
        for binding in query_res["results"]["bindings"]
    ]

def get_data_urls(uri, graph=DATA_GRAPH) -> List[str]:
    query_template = Template("""
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>

SELECT ?data_url WHERE {
    GRAPH $graph {
        $uri a ext:DCATValidationRequest ;
            ext:dataURL ?data_url .
    }
}
    """)

    query_string = query_template.substitute(
        graph=sparql_escape_uri(graph) if graph else "?g",
        uri=sparql_escape_uri(uri)
    )

    query_res = query(query_string)
    return [
        binding["data_url"]["value"]
        for binding in query_res["results"]["bindings"]
    ]

