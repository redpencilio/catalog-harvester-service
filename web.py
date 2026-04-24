from constants import PYSHACL_SYSTEM_TRIPLES
from utils import store_graph
from catalog_endpoint import CatalogEndpoint
from flask import request
from dcat_validation_request import DCATValidationRequest
import rdflib

# SAMPLE_SHACL = "https://raw.githubusercontent.com/mobilityDCAT-AP/mobilityDCAT-AP/refs/heads/gh-pages/releases/1.1.0/shaclShapes/mobilitydcat-ap_shacl_shapes.ttl"
SAMPLE_SHACL = [
    # "https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/shacl/mobilitydcat-ap-shacl.ttl",
    # "https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/shacl/mobilitydcat-ap-shacl-ranges.ttl",
    "https://raw.githubusercontent.com/mobilityDCAT-AP/mobilityDCAT-AP/refs/heads/gh-pages/releases/1.1.0/shaclShapes/mobilitydcat-ap_shacl_shapes.ttl"
]
# SAMPLE_DATA = "https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/sample_data/baseline-dcat-ap/positives/B-P-03-full-minimal-chain.ttl"
# SAMPLE_DATA = ["https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/sample_data/mobility/positives/M-P-04-full-mobility-catalog.ttl"]
SAMPLE_DATA = ["https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/sample_data/mobility/positives/M-P-01-mandatory-homepage.ttl"]

# SAMPLE_DATA = ["https://transportdata.be/catalog.ttl"]

@app.route("/harvest/")
def harvest():
    from harvest import run_catalog_harvesting_task

    catalog_endpoint = CatalogEndpoint(
        first_url=SAMPLE_DATA[0],
        current_url=SAMPLE_DATA[0]
    )

    dcat_validation_request = DCATValidationRequest(
        shacl_urls=SAMPLE_SHACL,
        catalog_endpoint_uri=catalog_endpoint.uri
    )

    dcat_validation_request.insert()
    catalog_endpoint.insert()

    shacl_graph = rdflib.Graph()
    for shacl_url in dcat_validation_request.shacl_urls:
        shacl_graph.parse(shacl_url)

    # TODO: this is an ugly workaround for:
    # https://github.com/RDFLib/pySHACL/blob/master/pyshacl/shapes_graph.py#L65
    # see also shacl.py in dcat-validator-service
    for t in PYSHACL_SYSTEM_TRIPLES:
        shacl_graph.add(t)

    # print(shacl_graph.serialize(format='ttl'))

    shacl_graph = shacl_graph.skolemize(
        authority='http://mu.semte.ch',
        basepath='.well-known/genid/harvester-shacl/'
    )

    store_graph(shacl_graph, dcat_validation_request.shacl_graph)

    result = run_catalog_harvesting_task(dcat_validation_request.uri)

    return {
        'success': 'true',
        'meta': {
            'result': result
        }
    }


@app.route("/jobs-delta", methods=('POST',))
def process_jobs_delta():
    from task_runner import run_tasks
    import threading

    inserts = request.json[0]["inserts"]
    has_tasks = any(
        t
        for t in inserts
        if t["predicate"]["value"] == "http://www.w3.org/ns/adms#status"
        and t["object"]["value"]
        == "http://redpencil.data.gift/id/concept/JobStatus/scheduled"
    )
    if not has_tasks:
        return "Can't do anything with this delta. Skipping.", 500

    thread = threading.Thread(target=run_tasks)
    thread.start()

    return "", 200

