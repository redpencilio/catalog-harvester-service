import os
from pyshacl.consts import (
    OWL_Class, RDFS_subClassOf, RDFS_Class,
    OWL_DatatypeProperty, RDF_Property
 )

GRAPH_LOAD_BATCH_SIZE = 100

MU_APPLICATION_GRAPH = os.environ.get("MU_APPLICATION_GRAPH", "http://mu.semte.ch/graphs/public")
MU_SPARQL_ENDPOINT = os.environ.get("MU_SPARQL_ENDPOINT")

DATA_GRAPH = MU_APPLICATION_GRAPH
TASKS_GRAPH = "http://mu.semte.ch/graphs/jobs"

JOB_URI_PREFIX = "http://redpencil.data.gift/id/job/"
JOB_ERROR_URI_PREFIX = "http://redpencil.data.gift/id/jobs/error/"
TASK_URI_PREFIX = "http://redpencil.data.gift/id/task/"
CONTAINER_URI_PREFIX = "http://redpencil.data.gift/id/container/"

DCAT_VALIDATION_REQUEST_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/dcat-validation-request/"

MOBILITY_DCAT_VALIDATION_JOB_OPERATION = "http://lblod.data.gift/id/jobs/concept/JobOperation/mobility-dcat-validation-job"
MOBILITY_DCAT_VALIDATION_TASK_OPERATION = "http://mu.semte.ch/vocabularies/ext/MobilityDcatValidationTask"

CATALOG_ENDPOINT_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/catalog-endpoint/"

CATALOG_HARVEST_INPUT_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/catalog-harvest-input/"
CATALOG_HARVEST_JOB_OPERATION = "http://lblod.data.gift/id/jobs/concept/JobOperation/catalog-harvest-job"
CATALOG_HARVEST_OPERATION = "http://mu.semte.ch/vocabularies/ext/CatalogHarvestJob"
# CATALOG_HARVEST_RESULT_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/shacl-validation-result/"
# CATALOG_HARVEST_RESULT_GRAPH_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/shacl-validation-result-graph/"

SHACL_VALIDATION_INPUT_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/shacl-validation-input/"
SHACL_VALIDATION_JOB_OPERATION = "http://lblod.data.gift/id/jobs/concept/JobOperation/validation-job"
SHACL_VALIDATION_OPERATION = "http://mu.semte.ch/vocabularies/ext/ShaclValidationJob"
SHACL_VALIDATION_RESULT_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/shacl-validation-result/"
SHACL_VALIDATION_RESULT_GRAPH_URI_PREFIX = "http://mu.semte.ch/vocabularies/ext/shacl-validation-result-graph/"

PYSHACL_SYSTEM_TRIPLES = [
    (OWL_Class, RDFS_subClassOf, RDFS_Class),
    (OWL_DatatypeProperty, RDFS_subClassOf, RDF_Property)
]
