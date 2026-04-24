from utils import from_binding
from constants import DATA_GRAPH, CATALOG_ENDPOINT_URI_PREFIX
from string import Template
from typing import Optional
import datetime
from dataclasses import dataclass, field
import rdflib

from helpers import generate_uuid
# from context_query import query, update
from sudo_query import query_sudo as query, update_sudo as update
from escape_helpers import sparql_escape_uri, sparql_escape_datetime, sparql_escape_string

@dataclass
class CatalogEndpoint():
    first_url: str
    current_url: Optional[str] = None
    destination_graph: str = None

    id: str = field(default_factory=generate_uuid)
    uri: str = None
    created: datetime.datetime = field(default_factory=datetime.datetime.now)
    modified: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post_init__(self):
        if not self.uri:
            self.uri = CATALOG_ENDPOINT_URI_PREFIX + self.id
        if not self.destination_graph:
            self.destination_graph = self.uri + "/destination-graph"

    def insert(self, graph=DATA_GRAPH):
        query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX dct: <http://purl.org/dc/terms/>

INSERT DATA {
    GRAPH $graph {
        $uri a ext:CatalogEndpoint ;
            mu:uuid $uuid ;
            dct:created $created ;
            dct:modified $modified ;
            ext:firstURL $first_url ;
            $current_url
            ext:destination $destination_graph .
    }
}
        """)
        current_url = f"ext:currentURL {sparql_escape_string(self.current_url)} ;"\
            if self.current_url else ""

        self.modified = datetime.datetime.now()

        query_string = query_template.substitute(
            graph=sparql_escape_uri(graph),
            uri=sparql_escape_uri(self.uri),
            uuid=sparql_escape_string(self.id),
            created=sparql_escape_datetime(self.created),
            modified=sparql_escape_datetime(self.modified),
            current_url=current_url,
            first_url=sparql_escape_string(self.first_url),
            destination_graph=sparql_escape_uri(self.destination_graph)
        )

        update(query_string)

    def update(self, graph=DATA_GRAPH):
        query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX dct: <http://purl.org/dc/terms/>

DELETE {
    GRAPH $graph {
        $uri
            dct:modified ?old_modified ;
            ext:currentURL ?old_current_url .
    }
}
INSERT {
    GRAPH $graph {
        $uri
            $current_url
            dct:modified $modified .
    }
}
WHERE {
    GRAPH $graph {
        $uri a ext:CatalogEndpoint .
        OPTIONAL { $uri ext:currentURL ?old_current_url }
        OPTIONAL { $uri dct:modified ?old_modified }
    }
}
        """)
        current_url = f"ext:currentURL {sparql_escape_string(self.current_url)} ;"\
            if self.current_url else ""

        self.modified = datetime.datetime.now()

        query_string = query_template.substitute(
            graph=sparql_escape_uri(graph),
            uri=sparql_escape_uri(self.uri),
            modified=sparql_escape_datetime(self.modified),
            current_url=current_url,
        )

        update(query_string)

def get_catalog_endpoint(uri: str, graph=DATA_GRAPH) -> CatalogEndpoint:
    uri_query = f"VALUES ?uri {{ {sparql_escape_uri(uri)} }}"
    return get_catalog_endpoint_by_query(uri_query, graph)

def get_catalog_endpoint_by_query(uri_query, graph=DATA_GRAPH) -> CatalogEndpoint:

    query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ?id ?uri ?created ?modified ?first_url ?current_url ?destination_graph WHERE {
    GRAPH $graph {
        $uri_query
        ?uri a ext:CatalogEndpoint ;
            mu:uuid ?id ;
            dct:created ?created ;
            dct:modified ?modified ;
            ext:firstURL ?first_url ;
            ext:destination ?destination_graph .
        OPTIONAL { ?uri ext:currentURL ?current_url . }
    }
}
LIMIT 1
    """)

    query_string = query_template.substitute(
        graph=sparql_escape_uri(graph) if graph else "?g",
        uri_query=uri_query
    )

    query_res = query(query_string)
    bindings = query_res["results"]["bindings"]
    if not bindings:
        raise Exception(f"Catalog Endpoint description not found: <{uri}>")

    binding = bindings[0]
    catalog_endpoint = from_binding(
        CatalogEndpoint, binding,
    )

    return catalog_endpoint
