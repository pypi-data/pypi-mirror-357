import os
import pandas as pd
from tqdm import tqdm
from pysam import VariantFile
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from query import submit_query, submit_query_cached
from utils import (
    standardize_variant_id,
    construct_variant_id,
    get_result_info,
    generate_summary,
    write_summary,
)

logger = logging.getLogger(__name__)

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
        raise ValueError("Specify either --COLUMN or all of --CHR, --POS, --REF, --ALT")

    if not args.COLUMN:
        df['__variant_id__'] = df.apply(lambda row: construct_variant_id(row, args.CHR, args.POS, args.REF, args.ALT), axis=1)
        variant_col = '__variant_id__'
    else:
        if args.COLUMN not in df.columns:
            raise ValueError(f"Column '{args.COLUMN}' not found in file")
        variant_col = args.COLUMN

    ids = df[variant_col].astype(str).tolist()
    id_batches, row_map = {"variantID": [], "rsID": []}, {"variantID": [], "rsID": []}

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
            ids_batch, rows = id_batches[id_type], row_map[id_type]
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
        write_summary(summary, os.path.splitext(args.OUTPUT)[0] + "_summary.json")
        logger.info(f"Summary written to {args.OUTPUT}_summary.json")
