# Excel Workbooks

## Multi-Sheet Workbooks

Common patterns in data room Excel files:

- **Summary + Detail**: First sheet is a dashboard/summary, subsequent sheets
  contain the raw data. Profile the detail sheets, reference the summary.
- **By Period**: One sheet per quarter/month. Same columns, different data.
  These should be combined into a single profiled source with a period column.
- **By Entity**: One sheet per department/region/product. Same structure.
  Combine with an entity identifier column.
- **Mixed**: Some sheets are data, some are documentation, some are charts.
  Identify which sheets contain tabular data vs. narrative.

## Merged Cells

Excel merged cells create problems for tabular profiling:

- Merged cells in headers → multi-level column names
- Merged cells in data → parent-child groupings (e.g., department merged
  across all employees in that department)

Strategy: When `pandas.read_excel()` reads merged cells, the value appears
in the first cell and subsequent cells are NaN. Look for patterns of
NaN followed by data to detect merged cell structures.

## Formatting-as-Data

Some Excel files use formatting to convey meaning:

- **Color coding**: Red = overdue, green = on track (invisible to CSV export)
- **Bold/italic**: Headers, totals, subtotals
- **Number formats**: Currency, percentage, date formats that change meaning
- **Hidden rows/columns**: Filtered data that appears missing

Note: `profile_source.py` cannot detect formatting. If an Excel file's
structure doesn't make sense as flat tabular data, it may rely on
formatting. Flag this as a quality issue in the catalog.

## Named Ranges and Tables

Excel "Table" objects and named ranges can contain structured data that
doesn't start at cell A1. If a sheet appears mostly empty but the file
is large, check for off-origin data regions.

## Formulas and Calculated Columns

Some columns may contain formulas rather than raw data. When profiling:
- The profiled values are the formula results (correct for our purposes)
- But the data source is not "raw" — it's already derived
- Note this if the formula references external workbooks or data connections
