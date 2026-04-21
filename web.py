from flask import request
from dcat_validation_request import DCATValidationRequest

# SAMPLE_SHACL = "https://raw.githubusercontent.com/mobilityDCAT-AP/mobilityDCAT-AP/refs/heads/gh-pages/releases/1.1.0/shaclShapes/mobilitydcat-ap_shacl_shapes.ttl"
SAMPLE_SHACL = [
    "https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/shacl/mobilitydcat-ap-shacl.ttl",
    "https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/shacl/mobilitydcat-ap-shacl-ranges.ttl",
]
# SAMPLE_DATA = "https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/sample_data/baseline-dcat-ap/positives/B-P-03-full-minimal-chain.ttl"
SAMPLE_DATA = ["https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/sample_data/mobility/positives/M-P-04-full-mobility-catalog.ttl"]
SAMPLE_DATA = ["https://raw.githubusercontent.com/mobilityDCAT-AP/validation/refs/heads/main/sample_data/mobility/positives/M-P-01-mandatory-homepage.ttl"]

@app.route("/harvest/")
def harvest():
    from harvest import run_catalog_harvesting_task

    dcat_validation_request = DCATValidationRequest(
        shacl_urls=SAMPLE_SHACL,
        data_urls=SAMPLE_DATA
    )

    dcat_validation_request.insert()

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

