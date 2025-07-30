#!/usr/bin/env python

import argparse
import logging
import math
import re
import time
import os
import json
from tqdm import tqdm
from pysam import VariantFile
import requests
import pandas as pd
from exceptions import AgvdException, HTTP_STATUS_CODES
from functools import lru_cache, partial
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def arguments():
    parser = argparse.ArgumentParser(prog="AGVD", description="AGVD Variant Query Filter")
    parser.add_argument("-k", "--KEY", help="AGVD API Key", type=str, required=True)
    parser.add_argument("-i", "--INFILE", help="Input file path (VCF, CSV, TSV, Excel)", type=str, required=True)
    parser.add_argument("-o", "--OUTPUT", help="Output file path", type=str, required=True)
    parser.add_argument("-t", "--THRESHOLD", help="Cutoff threshold", type=float, required=True)
    parser.add_argument("-b", "--BATCH", help="Batch Size", type=int, default=1000)
    parser.add_argument("-c", "--COLUMN", help="Column name for variant IDs (for CSV/TSV/Excel)", type=str, required=False)
    parser.add_argument("--CHR", help="Chromosome column name", type=str)
    parser.add_argument("--POS", help="Position column name", type=str)
    parser.add_argument("--REF", help="Reference allele column name", type=str)
    parser.add_argument("--ALT", help="Alternate allele column name", type=str)
    parser.add_argument("--verbose", help="Enable verbose output", action='store_true')
    parser.add_argument("--dry-run", help="Only validate the input file without submitting queries", action='store_true')
    parser.add_argument("--cache", help="Enable local caching of queries", action='store_true')
    parser.add_argument("--threads", help="Number of threads for parallel execution", type=int, default=4)
    return parser


def setup_logging(verbose=False):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s | %(levelname)s: %(message)s'
    )


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


@lru_cache(maxsize=5000)
def submit_query_cached(key, ids, threshold, id_type):
    return submit_query(ids, threshold, id_type)


def submit_query(identifiers, threshold, id_type):
    url = "https://agvd-rps.h3abionet.org/devo/"
    headers = {'content-type': 'application/json'}

    query = '''mutation($input:VCFQueryInput) {
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


def construct_variant_id(row, chr_col, pos_col, ref_col, alt_col):
    return f"{str(row[chr_col]).lstrip('chr')}_{int(row[pos_col])}_{row[ref_col]}_{row[alt_col]}"


def process_vcf(args):
    vcf = VariantFile(args.INFILE)
    rows = [f"{str(rec.chrom).lstrip('chr')}_{rec.pos}_{rec.ref}_{rec.alts[0]}" for rec in vcf]
    df = pd.DataFrame({'variant_id': rows})
    args.COLUMN = 'variant_id'
    args.CHR = args.POS = args.REF = args.ALT = None
    args.INFILE = args.OUTPUT + '.tmp.csv'
    df.to_csv(args.INFILE, index=False)
    process_table(args)
    os.remove(args.INFILE)


def process_table(args):
    ext = args.INFILE.split(".")[-1].lower()
    df = pd.read_csv(args.INFILE) if ext == "csv" else (
         pd.read_csv(args.INFILE, sep='\t') if ext == "tsv" else pd.read_excel(args.INFILE))

    if not args.COLUMN and not all([args.CHR, args.POS, args.REF, args.ALT]):
        raise ValueError("You must specify either --COLUMN for variant IDs or all of --CHR, --POS, --REF, and --ALT")

    if not args.COLUMN:
        df['__variant_id__'] = df.apply(lambda row: construct_variant_id(row, args.CHR, args.POS, args.REF, args.ALT), axis=1)
        variant_col = '__variant_id__'
    else:
        if args.COLUMN not in df.columns:
            raise ValueError(f"Column '{args.COLUMN}' not found in file")
        variant_col = args.COLUMN

    ids = df[variant_col].astype(str).tolist()

    id_batches = {"variantID": [], "rsID": []}
    row_map = {"variantID": [], "rsID": []}
    for idx, rid in enumerate(ids):
        try:
            std_id, id_type = standardize_variant_id(rid)
            id_batches[id_type].append(std_id)
            row_map[id_type].append(idx)
        except ValueError:
            df.loc[idx, 'AGVDCUTOFF'] = 'INVALID'

    total_success, total_fail = 0, 0

    def process_batch(batch, batch_rows, id_type):
        local_success, local_fail = 0, 0
        try:
            if args.dry_run:
                logger.info(f"Dry run: would submit {len(batch)} {id_type}s")
                return local_success, local_fail
            results = submit_query_cached(args.KEY, tuple(batch), args.THRESHOLD, id_type) if args.cache else submit_query(batch, args.THRESHOLD, id_type)
            for j, rid in enumerate(batch):
                row_idx = batch_rows[j]
                info = get_result_info(rid, results)
                df.loc[row_idx, 'THRESHOLD'] = info['usedThreshold']
                df.loc[row_idx, 'AGVDCUTOFF'] = info['status']
                df.loc[row_idx, 'African_MAF'] = info['mafThreshold']
                for cname, maf in info['clusters'].items():
                    df.loc[row_idx, f"{cname}_MAF"] = maf
                local_success += 1
        except Exception as e:
            logger.error(f"Batch failed: {e}")
            for row_idx in batch_rows:
                df.loc[row_idx, 'THRESHOLD'] = args.THRESHOLD
                df.loc[row_idx, 'AGVDCUTOFF'] = 'ERROR'
                df.loc[row_idx, 'African_MAF'] = None
                local_fail += 1
        return local_success, local_fail

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for id_type in id_batches:
            ids_batch = id_batches[id_type]
            rows = row_map[id_type]
            for i in range(0, len(ids_batch), args.BATCH):
                batch = ids_batch[i:i + args.BATCH]
                batch_rows = rows[i:i + args.BATCH]
                futures.append(executor.submit(process_batch, batch, batch_rows, id_type))

        for future in as_completed(futures):
            success, fail = future.result()
            total_success += success
            total_fail += fail

    if not args.dry_run:
        if ext == "csv":
            df.to_csv(args.OUTPUT, index=False)
        elif ext == "tsv":
            df.to_csv(args.OUTPUT, sep='\t', index=False)
        else:
            df.to_excel(args.OUTPUT, index=False)

        summary = generate_summary(len(ids), total_success, total_fail)
        summary_path = os.path.splitext(args.OUTPUT)[0] + "_summary.json"
        write_summary(summary, summary_path)
        logger.info(f"Summary written to {summary_path}")

def run(args):
    setup_logging(args.verbose)
    logger.info("Starting AGVD Variant Processing")

    if args.INFILE.lower().endswith(".vcf.gz") or args.INFILE.lower().endswith(".vcf"):
        process_vcf(args)
    else:
        process_table(args)

def main():
    args = arguments().parse_args()
    run(args)


if __name__ == '__main__':
    main()
