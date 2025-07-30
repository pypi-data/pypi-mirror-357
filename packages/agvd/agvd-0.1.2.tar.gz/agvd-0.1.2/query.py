import requests
from functools import lru_cache
from exceptions import AgvdException, HTTP_STATUS_CODES

def submit_query(identifiers, threshold, id_type):
    url = "https://agvd-rps.h3abionet.org/devo/"
    headers = {'content-type': 'application/json'}
    query = '''
    mutation($input:VCFQueryInput) {
        cliVariantSearch(input:$input) {
            variantID
            mafThreshold
            agvdThresholdStatus
            usedThreshold
            clusters {
                name
                maf
            }
        }
    }'''
    variables = {"input": {id_type: identifiers, "threshold": threshold}}
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})

    if response.status_code == 200:
        return response.json()['data']['cliVariantSearch']
    else:
        raise AgvdException(HTTP_STATUS_CODES.get(response.status_code, {"message": "Unknown error"})["message"])


@lru_cache(maxsize=5000)
def submit_query_cached(key, ids, threshold, id_type):
    return submit_query(ids, threshold, id_type)


def peek_query(identifiers, id_type):
    url = "https://agvd-rps.h3abionet.org/devo/"
    headers = {'content-type': 'application/json'}
    query = '''
    mutation($input:VariantPeekInput) {
        cliVariantPeek(input:$input) {
            variantID
            status
            url
        }
    }'''
    variables = {"input": {id_type: identifiers}}
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})

    if response.status_code == 200:
        return response.json()['data']['cliVariantPeek']
    else:
        raise AgvdException(HTTP_STATUS_CODES.get(response.status_code, {"message": "Unknown error"})["message"])

def peek_variants(variants):
    id_map = {"variantID": [], "rsID": []}
    from utils import standardize_variant_id
    for vid in variants:
        try:
            std_id, id_type = standardize_variant_id(vid)
            id_map[id_type].append(std_id)
        except ValueError:
            continue
    all_results = []
    for id_type, ids in id_map.items():
        if ids:
            all_results.extend(peek_query(ids, id_type))
    return all_results