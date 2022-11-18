from lambda_function import fetch_collection
from sample_data.nuxeo_harvests import *
from sample_data.oac_harvests import *
from sample_data.oai_harvests import *
import json

harvests = oac_harvests
#  + nuxeo_complex_object_harvests + nuxeo_nested_complex_object_harvests
for harvest in harvests:
    print(f"tests.py: {json.dumps(harvest)}")
    fetch_collection(json.dumps(harvest), {})
    print(f"Harvested: {str(harvest)}")
