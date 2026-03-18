# Data Formats — Playbook Index

Recognition heuristics and parsing guidance for common data formats
encountered in company data rooms.

## When to Load

Load specific skills during Phase 0 (Catalog) when you encounter
a format you need guidance on. Most tabular data (CSV, Excel) is
handled by `profile_source.py` directly. Load these skills for
edge cases, ambiguous formats, or non-tabular sources.

## Skills

| Skill | When to Load |
|-------|-------------|
| `csv_tabular.md` | Delimiter ambiguity, multi-row headers, encoding issues, mixed types |
| `excel_workbooks.md` | Multi-sheet workbooks, merged cells, formatting-as-data, named ranges |
| `pdf_documents.md` | Extracting structured data from PDFs, table detection, OCR needs |
| `json_api_exports.md` | Nested JSON, API pagination artifacts, schema inference |
| `database_dumps.md` | SQL dumps, Access databases, SQLite files |
| `unstructured_text.md` | Emails, memos, contracts — extracting entities and relationships |

## Routing

- **Tabular file won't parse?** → Load the format-specific skill
- **Excel with visual formatting?** → Load `excel_workbooks.md`
- **PDF with tables?** → Load `pdf_documents.md`
- **Nested or hierarchical data?** → Load `json_api_exports.md`
- **Text documents with entity mentions?** → Load `unstructured_text.md`
