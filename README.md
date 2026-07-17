# Alberta Court of King's Bench Document Sorter

A Python tool for parsing, validating, and sorting legal documents according to **Alberta Court of King's Bench (CKB)** formatting rules for all jurisdictions in Alberta.

## Features

- **Parses CKB document headers** - Extracts court file number, judicial centre, parties, document type, address for service, date filed, and clerk's stamp
- **Supports all Alberta jurisdictions**:
  - Civil (Court of King's Bench)
  - Criminal (R. v. Accused)
  - Family (Divorce, Parenting, Support)
  - Surrogate (Probate, Estates)
  - Bankruptcy & Insolvency
- **CKB-compliant sorting** per Alberta Rules of Court:
  1. Judicial Centre (alphabetical: Calgary, Edmonton, Lethbridge, Medicine Hat, Red Deer, St. Paul, Wetaskiwin)
  2. Date ID (year-sequence from court file number)
  3. Case ID (sequential number)
  4. Party Type (Prosecution/Plaintiff first)
  5. Document Type (CKB precedence order)
  6. Jurisdiction (Criminal > Civil > Family > Surrogate > Bankruptcy)
- **Multiple output formats**: Markdown, JSON, HTML
- **File copying** with numbered, sortable filenames
- **Supports PDF, DOCX, TXT, RTF, MD** formats

## Installation

```bash
# Clone the repository
git clone https://github.com/scotty-teh-sysop/scotty-teh-sysop.github.io.git
cd scotty-teh-sysop.github.io

# Install dependencies
pip install pdfplumber python-docx striprtf
```

## Usage

```bash
# Basic usage - sort documents and export as Markdown
python ckb_document_sorter.py ./legal_documents ./output --format md

# Export as JSON for programmatic use
python ckb_document_sorter.py ./legal_documents ./output --format json

# Export all formats (MD, JSON, HTML)
python ckb_document_sorter.py ./legal_documents ./output --format all

# Copy files to output/sorted in CKB-compliant order with numbered prefixes
python ckb_document_sorter.py ./legal_documents ./output --copy

# Full pipeline: parse, sort, export all formats, copy files
python ckb_document_sorter.py ./legal_documents ./output --format all --copy
```

## Output Formats

### Markdown (`ckb_sorted_index.md`)
Human-readable index with full CKB header tables for each document, grouped by judicial centre and jurisdiction.

### JSON (`ckb_sorted_index.json`)
Machine-readable format with all parsed fields and computed sort keys.

### HTML (`ckb_sorted_index.html`)
Styled table view grouped by judicial centre with jurisdiction sub-sections.

### Sorted Files (`output/sorted/`)
Files copied with CKB-compliant naming: `001_Calgary_2303-12345_StatementOfClaim.pdf`

## CKB Header Fields Parsed

| Field | Patterns Matched |
|-------|-----------------|
| **COURT FILE NUMBER** | `COURT FILE NUMBER`, `COURT FILE NO.`, `FILE NUMBER`, `ACTION NO.` |
| **JUDICIAL CENTRE** | `JUDICIAL CENTRE`, `JUDICIAL DISTRICT`, `AT [CENTRE]` |
| **PLAINTIFF** | `PLAINTIFF`, `PLAINTIFFS` |
| **DEFENDANT** | `DEFENDANT`, `DEFENDANTS` |
| **PROSECUTION** | `PROSECUTION`, `CROWN`, `R. v.`, `REX v.`, `THE KING v.` |
| **ACCUSED** | `ACCUSED` |
| **DOCUMENT TYPE** | `DOCUMENT`, `TYPE OF DOCUMENT` |
| **ADDRESS FOR SERVICE** | `ADDRESS FOR SERVICE`, `CONTACT INFORMATION` |
| **DATE FILED** | `FILED ON`, `DATE FILED`, `CLERK'S STAMP` |

## Alberta Judicial Centres Supported

1. Calgary
2. Edmonton
3. Lethbridge
4. Medicine Hat
5. Red Deer
6. St. Paul
7. Wetaskiwin

## Document Type Precedence (CKB Rules)

**Civil:**
1. Originating Application
2. Statement of Claim
3. Statement of Defence
4. Counterclaim
5. Reply
6. Affidavit
7. Application
8. Order
9. Judgment
10. Notice of Appeal

**Criminal:**
11. Information
12. Indictment
13. Bail Order
14. Sentencing Order

**Family:**
15. Claim
16. Response
17. Parenting Order
18. Support Order

**General:**
19. Notice
20. Motion
21. Brief/Factum
22. Transcript
23. Exhibit
24. Correspondence

## Example Output

```markdown
## Judicial Centre: Calgary

### Jurisdiction: Civil

#### 1. 2303-12345_Statement_of_Claim.pdf

| Field | Value |
|-------|-------|
| **COURT FILE NUMBER** | 2303-12345 |
| **JUDICIAL CENTRE** | Calgary |
| **PLAINTIFF** | John Smith |
| **DEFENDANT** | Jane Doe |
| **DOCUMENT** | Statement of Claim |
| **ADDRESS FOR SERVICE** | 123 Main St, Calgary, AB |
| **DATE FILED** | January 15, 2023 |
| **CLERK'S STAMP** | FILED 2023-01-15 |

**Metadata:** Date ID: `2023-12345` | Case ID: `12345` | Year: `2023` | Seq: `12345`
**Parsed Jurisdiction:** civil | **Party Type:** plaintiff | **Doc Type:** statement_of_claim
```

## GitHub Pages Deployment

This tool is designed to be deployed to GitHub Pages. The GitHub Actions workflow (`.github/workflows/deploy.yml`) will:

1. Run the sorter on documents in `./input_docs/`
2. Generate all output formats
3. Deploy to `gh-pages` branch for GitHub Pages hosting

## Requirements

- Python 3.8+
- `pdfplumber` (PDF parsing)
- `python-docx` (DOCX parsing)
- `striprtf` (RTF parsing)

## License

MIT License - Feel free to use for legal document management in Alberta.

## References

- [Alberta Rules of Court](https://open.alberta.ca/publications/2010_124)
- [Alberta Courts - Civil Forms](https://www2.albertacourts.ca/kb/areas-of-law/civil/forms)
- [LawCentral Alberta - CKB Forms](https://www.lawcentralalberta.ca/en/alberta-court-kings-bench-civil-forms-templates-and-publications)
