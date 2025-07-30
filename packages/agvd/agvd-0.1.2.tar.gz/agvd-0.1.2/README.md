# AGVD Variant Query Tool

The **AGVD Variant Query Tool** is a command-line utility for querying variant information against the African Genome Variation Database (AGVD). It supports input from VCF, CSV, TSV, or Excel files and provides threshold-based filtering and clustering of variants using AGVD's GraphQL API.

---

## 🚀 Features

- Supports VCF, CSV, TSV, and Excel input formats
- Accepts both `rsID` and `CHR_POS_REF_ALT` variant formats
- Submits queries in batches for improved performance
- Optional local caching for repeated queries
- Dry-run mode for validation without querying
- Exports enriched results and JSON summary
- Multithreaded for faster processing
- Supports "peek" query mode for quick variant lookups

---

## 📦 Requirements

- Python 3.7+
- Dependencies (installed via `pip install -r requirements.txt`):

```bash
pandas
tqdm
pysam
requests
openpyxl
```

---

## 🔧 Usage

```bash
python agvd \
  --KEY YOUR_AGVD_API_KEY \
  --INFILE path/to/input.vcf \
  --OUTPUT path/to/output.csv \
  --THRESHOLD 0.01
```

### Optional Arguments:

| Argument       | Description |
|----------------|-------------|
| `--BATCH`      | Batch size for API queries (default: 1000) |
| `--COLUMN`     | Column name with variant IDs (CSV/TSV/Excel only) |
| `--CHR`        | Chromosome column name |
| `--POS`        | Position column name |
| `--REF`        | Reference allele column name |
| `--ALT`        | Alternate allele column name |
| `--dry-run`    | Validates the file without submitting queries |
| `--verbose`    | Enables debug-level logging |
| `--cache`      | Enables local query caching |
| `--threads`    | Number of threads to use for parallel processing |
| `--peek`       | Provide a list of variant IDs (or input file) to run a quick lookup without thresholding |

---

## 📂 Input Format Examples

### VCF
Standard `.vcf` file with `#CHROM`, `POS`, `REF`, and `ALT` fields.

### CSV/TSV/Excel
Either:
- Single column with `rsID` or `CHR_POS_REF_ALT` format
- Separate columns for `--CHR`, `--POS`, `--REF`, `--ALT`

---

## 🧪 Output

- A file containing original input +:
  - `AGVDCUTOFF`: status based on MAF threshold
  - `African_MAF`: MAF value
  - `<Cluster>_MAF`: MAF per population cluster
- A `_summary.json` with success/failure statistics

---

## 🔍 Peek Mode

The **peek** mode lets you quickly retrieve availability and access URLs for variants without threshold-based filtering.

### From file:
```bash
python agvd --peek --INFILE variants.txt
```

### From inline list:
```bash
python agvd --peek rs123 rs456 chr1:12345:A:G
```

Returns:
```json
[
  {
    "id": "rs123",
    "status": "available",
    "url": "https://agvd.afrigen-d.org/variant?id=rs123"
  },
  {
    "id": "1-12345-A-G",
    "status": "unavailable",
    "url": null
  }
]
```

You can also call this in Python:
```python
from agvd.query import peek_variants
results = peek_variants(["rs123", "chr1:12345:A:G"])
```

---

## 🛠 Development

To test locally:

```bash
python agvd \
  -k test_key \
  -i examples/test.csv \
  -o out.csv \
  -t 0.05 \
  --verbose
```

To profile performance:
```bash
python -m cProfile agvd ...
```

---

## 🧾 License

MIT License © 2025 AGVD Team

---

## 📬 Contact

For support or questions, please contact: [agvd@afrigen-d.org](mailto:agvd@afrigen-d.org)
