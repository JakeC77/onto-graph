# CSV and Tabular Data

## Delimiter Detection

When a CSV doesn't parse with the default comma delimiter:

1. Check the first few lines for consistent tab, pipe, or semicolon usage
2. Look for the file extension — `.tsv` = tab, `.psv` = pipe
3. If the file has a BOM (byte order mark), it's likely UTF-8 with BOM encoding
4. European systems often use semicolons (`;`) as delimiters because commas
   are decimal separators

## Multi-Row Headers

Some system exports have multi-row headers:

- Row 1: Category groupings (merged across columns in Excel, repeated in CSV)
- Row 2: Actual column names
- Row 3+: Data

Signals of multi-row headers:
- First row has many empty cells or repeated values
- Second row has more unique values than the first
- Data types in row 3+ are consistent but row 1-2 are all strings

Strategy: Skip rows until you find the row where type diversity increases.

## Encoding Issues

Common encoding problems in data room files:

| Symptom | Likely Encoding |
|---------|----------------|
| `Ã©` instead of `é` | UTF-8 read as Latin-1 |
| `\x00` between every character | UTF-16 |
| `ï»¿` at start of file | UTF-8 with BOM |
| Garbled Asian characters | Shift-JIS or GB2312 |

Try in order: UTF-8, Latin-1 (ISO-8859-1), Windows-1252, UTF-16.

## Mixed Types in Columns

When a column has mixed types (numbers and strings):

- Check for sentinel values: "N/A", "n/a", "-", "NULL", "#REF!"
- Check for units embedded in values: "$1,234", "45%", "12 months"
- Check for concatenated values: "John Smith (VP)"

These indicate the column needs preprocessing before type inference.

## Large Files

For files over 100MB:
- Profile a sample (first 10,000 rows) for type inference
- Use the full file for cardinality and uniqueness checks
- Note the sampling in the profile metadata
