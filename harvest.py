from context_query import get_mu_headers
import rdflib
from helpers import generate_uuid
from utils import store_graph
import task_runner
from task import Task
from dcat_validation_request import DCATValidationRequest, get_dcat_validation_request

from constants import SHACL_VALIDATION_OPERATION, SHACL_VALIDATION_JOB_OPERATION, CATALOG_HARVEST_OPERATION, PYSHACL_SYSTEM_TRIPLES

def run_catalog_harvesting_task(dcat_validation_request_uri):
    dcat_validation_request = get_dcat_validation_request(dcat_validation_request_uri)

    data_graph = rdflib.Graph()
    for data_url in dcat_validation_request.data_urls:
        data_graph.parse(data_url)

    store_graph(data_graph, dcat_validation_request.data_graph)

    shacl_graph = rdflib.Graph()
    for data_url in dcat_validation_request.data_urls:
        shacl_graph.parse(data_url)

    # TODO: this is an ugly workaround for:
    # https://github.com/RDFLib/pySHACL/blob/master/pyshacl/shapes_graph.py#L65
    # see also shacl.py in dcat-validator-service
    for t in PYSHACL_SYSTEM_TRIPLES:
        shacl_graph.add(t)

    store_graph(shacl_graph, dcat_validation_request.shacl_graph)

    task = Task(
        input=dcat_validation_request.uri,
        operation=SHACL_VALIDATION_OPERATION,
        job_operation=SHACL_VALIDATION_JOB_OPERATION,
        headers=get_mu_headers()
    )

    task.insert(SHACL_VALIDATION_JOB_OPERATION)

    return dcat_validation_request.uri

task_runner.register(CATALOG_HARVEST_OPERATION, run_catalog_harvesting_task)

