import dcat_validation_request
from task_runner import TaskSuccess, TaskReschedule, TaskResult
from catalog_endpoint import get_catalog_endpoint, get_catalog_endpoint_by_query
from context_query import get_mu_headers
import rdflib
from helpers import generate_uuid
from escape_helpers import sparql_escape_uri
from utils import store_graph
import task_runner
from task import Task
from dcat_validation_request import DCATValidationRequest, get_dcat_validation_request

from constants import SHACL_VALIDATION_OPERATION, SHACL_VALIDATION_JOB_OPERATION, CATALOG_HARVEST_OPERATION, PYSHACL_SYSTEM_TRIPLES

def run_catalog_harvesting_task(dcat_validation_request_uri) -> TaskResult:

    catalog_endpoint = get_catalog_endpoint_by_query(
        f"{sparql_escape_uri(dcat_validation_request_uri)} ext:endpoint ?uri ."
    )

    if not catalog_endpoint.current_url:
        return TaskSuccess(dcat_validation_request_uri)

    data_graph = rdflib.Graph()
    data_graph.parse(catalog_endpoint.current_url)

    nexts = data_graph.query("""
PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
SELECT ?next WHERE {
    {
        ?partialCollectionView a hydra:PartialCollectionView ;
            hydra:next ?next .
    } UNION {
        ?pagedCollection a hydra:PagedCollection ;
            hydra:nextPage ?next .
    }
}
    """)

    data_graph.update("""
PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
DELETE { ?s ?p ?o }
WHERE {
    {
        ?s a hydra:PartialCollectionView .
    } UNION {
        ?s a hydra:PagedCollection .
    }
    ?s ?p ?o .
}
    """)

    data_graph = data_graph.skolemize(
        authority="http://mu.semte.ch",
        basepath='.well-known/genid/catalog-harvester/'
    )

    if nexts \
        and (next_row := [n for n in nexts][0]) \
        and (next_row.next is not catalog_endpoint.current_url):

        catalog_endpoint.current_url = next_row.next
        catalog_endpoint.update()

        store_graph(data_graph, catalog_endpoint.destination_graph)
        return TaskReschedule()

    else:
        store_graph(data_graph, catalog_endpoint.destination_graph)

        dcat_validation_request.attach_data_graph(
            uri=dcat_validation_request_uri,
            data_graph_uri=catalog_endpoint.destination_graph
        )
        task = Task(
            input=dcat_validation_request_uri,
            operation=SHACL_VALIDATION_OPERATION,
            job_operation=SHACL_VALIDATION_JOB_OPERATION,
            headers=get_mu_headers()
        )

        task.insert()

        return TaskSuccess(dcat_validation_request_uri)

task_runner.register(CATALOG_HARVEST_OPERATION, run_catalog_harvesting_task)

