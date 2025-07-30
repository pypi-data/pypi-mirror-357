import logging
from core import process_vcf, process_table
from utils import setup_logging, build_arg_parser, read_variants_from_file
from query import peek_variants

def run(args):
    setup_logging(args.verbose)
    logging.info("Starting AGVD Variant Processing")
    if args.INFILE.lower().endswith(".vcf") or args.INFILE.lower().endswith(".vcf.gz"):
        process_vcf(args)
    else:
        process_table(args)

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.peek:
        identifiers = read_variants_from_file(args.INFILE) if args.INFILE else args.peek
        results = peek_variants(identifiers)
        for result in results:
            print(result)
    else:
        run(args)

if __name__ == '__main__':
    main()

