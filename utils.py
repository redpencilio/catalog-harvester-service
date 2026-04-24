from itertools import islice
from string import Template
from constants import GRAPH_LOAD_BATCH_SIZE
from escape_helpers import sparql_escape_uri, sparql_escape_string
from sudo_query import query_sudo, update_sudo
import rdflib
import dataclasses

def from_binding(datacls, binding, extra={}):
    values = {
        field.name: binding[field.name]["value"]
        for field in dataclasses.fields(datacls)
        if field.name in binding
    }
    values.update(extra)
    return datacls(**values)

def batched(iterable, n, *, strict=False):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError('batched(): incomplete batch')
        yield batch

def _n3(term):
    if isinstance(term, rdflib.Literal):
        if term.datatype == rdflib.URIRef("http://www.opengis.net/ont/geosparql#wktLiteral"):
            return rdflib.Literal(
                term.value,
                datatype=rdflib.namespace.XSD.string
            ).n3()
        elif term.language:
            print(f"{term.value=}")
            print(f"{term.n3()=}")
            print(f"{term.normalize()=}")
            return sparql_escape_string(term.value)

    return term.n3()

# adapted from https://github.com/RDFLib/rdflib/issues/1704
def store_graph(g: rdflib.Graph, graph_name: str):
    """RDFlib graph to sparql"""
    for triples_batch in batched(g.triples((None, None, None)), GRAPH_LOAD_BATCH_SIZE):
        updatequery = "\n".join(
            [f"PREFIX {prefix}: {ns.n3()}" for prefix, ns in g.namespaces()]
        )
        updatequery += f"\nINSERT DATA {{\n\tGRAPH {sparql_escape_uri(graph_name)} {{\n"
        updatequery += " .\n".join(
            [f"\t\t{_n3(s)} {_n3(p)} {_n3(o)}" for (s, p, o) in triples_batch]
        )
        updatequery += f" . \n\t }}\n}}\n"

        update_sudo(updatequery)


# dump_graph_query_template = Template("""
# SELECT ?s ?p ?o WHERE
# {
#     {
#         SELECT DISTINCT ?s ?p ?o
#         FROM $graph
#         WHERE
#         {
#             ?s ?p ?o .
#         }
#         ORDER BY ASC(?s)
#     }
# }
# OFFSET $offset
# LIMIT $limit
# """)

# def load_graph(graph_uri, dest=None):
#     if not dest:
#         dest = rdflib.Graph()

#     i = 0

#     while True:
#         query_string = dump_graph_query_template.substitute(
#             graph=sparql_escape_uri(graph_uri),
#             offset=i*GRAPH_LOAD_BATCH_SIZE,
#             limit=GRAPH_LOAD_BATCH_SIZE
#         )
#         query_res = query(query_string)

#         if not query_res["results"]["bindings"]:
#             break

def listize(object):
    if isinstance(object, list):
        return object
    else:
        return [object]

