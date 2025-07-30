import logging
import re
import json
import argparse

def setup_logging(verbose=False):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s | %(levelname)s: %(message)s'
    )

def build_arg_parser():
    parser = argparse.ArgumentParser(prog="AGVD", description="AGVD Variant Query Filter")
    parser.add_argument("-k", "--KEY", type=str, required=False)
    parser.add_argument("-i", "--INFILE", type=str, required=False)
    parser.add_argument("-o", "--OUTPUT", type=str, required=False)
    parser.add_argument("-t", "--THRESHOLD", type=float, required=False)
    parser.add_argument("-b", "--BATCH", type=int, default=1000)
    parser.add_argument("-c", "--COLUMN", type=str)
    parser.add_argument("--CHR", type=str)
    parser.add_argument("--POS", type=str)
    parser.add_argument("--REF", type=str)
    parser.add_argument("--ALT", type=str)
    parser.add_argument("--verbose", action='store_true')
    parser.add_argument("--dry-run", action='store_true')
    parser.add_argument("--cache", action='store_true')
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--peek", nargs='*', help="Peek mode: List of variants or input file")
    return parser

def standardize_variant_id(raw_id):
    raw_id = raw_id.strip()
    if re.match(r"^rs\d+$", raw_id, re.IGNORECASE):
        return raw_id, "rsID"

    raw_id = raw_id.lower().replace("chr", "")
    patterns = [
        r'(?P<chr>\w+)[_|:|\-|>|\|](?P<pos>\d+)[_|:|\-|>|\|](?P<ref>\w+)[_|:|\-|>|\|](?P<alt>\w+)',
        r'(?P<chr>\w+):(?P<pos>\d+):(?P<ref>\w+):(?P<alt>\w+)',
        r'(?P<chr>\w+):(?P<pos>\d+):(?P<ref>\w+)[>](?P<alt>\w+)'
    ]
    for pattern in patterns:
        match = re.match(pattern, raw_id)
        if match:
            std_id = f"{match.group('chr')}_{match.group('pos')}_{match.group('ref')}_{match.group('alt')}"
            return std_id.upper(), "variantID"

    raise ValueError(f"Unrecognized variant ID format: {raw_id}")

def construct_variant_id(row, chr_col, pos_col, ref_col, alt_col):
    return f"{str(row[chr_col]).lstrip('chr')}_{int(row[pos_col])}_{row[ref_col]}_{row[alt_col]}"

def get_result_info(variant_id, results):
    for result in results:
        if result.get('variantID') == variant_id or result.get('rsID') == variant_id:
            return {
                "mafThreshold": result.get("mafThreshold"),
                "status": result.get("agvdThresholdStatus", "UNKNOWN"),
                "usedThreshold": result.get("usedThreshold"),
                "clusters": {c['name']: c['maf'] for c in result.get("clusters", [])}
            }
    return {"mafThreshold": None, "status": "NO MATCH", "usedThreshold": None, "clusters": {}}

def generate_summary(total, success, fail):
    return {
        "total": total,
        "successful": success,
        "failed": fail,
        "success_rate": success / total if total > 0 else 0
    }

def write_summary(summary, path):
    with open(path, 'w') as f:
        json.dump(summary, f, indent=2)

def read_variants_from_file(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]
