#!/usr/bin/env python3
"""
Parse SQL DDL files into structured table/column/FK metadata.

Extracts from CREATE TABLE statements:
- Table names and columns (name, type, nullable)
- Primary key constraints (inline and table-level)
- Foreign key constraints (inline and table-level)
- Unique constraints
- Default values

Handles dialect variations: PostgreSQL, MySQL, SQL Server, SQLite.

Usage:
    python tools/parse_ddl.py <ddl_file> [--output <path>] [--verbose]
    python tools/parse_ddl.py <ddl_dir> --all [--output-dir <dir>] [--verbose]

Examples:
    python tools/parse_ddl.py schemas/quickbooks.sql
    python tools/parse_ddl.py schemas/quickbooks.sql --output quickbooks_schema.yaml
"""

import argparse
import os
import re
import sys
from pathlib import Path

import yaml


def strip_comments(sql: str) -> str:
    """Remove SQL comments (-- line comments and /* block comments */)."""
    # Block comments
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    # Line comments
    sql = re.sub(r'--[^\n]*', '', sql)
    return sql


def unquote(name: str) -> str:
    """Remove quotes/brackets from identifiers."""
    name = name.strip()
    # [brackets] (SQL Server)
    if name.startswith('[') and name.endswith(']'):
        return name[1:-1]
    # `backticks` (MySQL)
    if name.startswith('`') and name.endswith('`'):
        return name[1:-1]
    # "double quotes" (PostgreSQL/ANSI)
    if name.startswith('"') and name.endswith('"'):
        return name[1:-1]
    return name


def strip_schema(name: str) -> str:
    """Remove schema prefix (e.g., 'dbo.tablename' → 'tablename')."""
    if '.' in name:
        return name.split('.')[-1]
    return name


def parse_column_type(type_str: str) -> str:
    """Normalize SQL type string."""
    type_str = type_str.strip().upper()
    # Remove length/precision specs for normalization
    base = re.sub(r'\(.*?\)', '', type_str).strip()
    return type_str if type_str else "UNKNOWN"


def parse_create_table(statement: str) -> dict | None:
    """Parse a single CREATE TABLE statement."""

    # Extract table name
    match = re.match(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?'
        r'([^\s(]+)',
        statement, re.IGNORECASE
    )
    if not match:
        return None

    raw_name = unquote(strip_schema(match.group(1)))

    # Extract the parenthesized body
    paren_match = re.search(r'\((.*)\)', statement, re.DOTALL)
    if not paren_match:
        return None

    body = paren_match.group(1)

    # Split body into definitions, respecting nested parens
    definitions = []
    depth = 0
    current = []
    for char in body:
        if char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            definitions.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        definitions.append(''.join(current).strip())

    columns = []
    table_pks = []
    table_fks = []
    table_uniques = []

    for defn in definitions:
        defn_upper = defn.upper().strip()

        # Table-level PRIMARY KEY
        pk_match = re.match(
            r'(?:CONSTRAINT\s+\S+\s+)?PRIMARY\s+KEY\s*\(([^)]+)\)',
            defn, re.IGNORECASE
        )
        if pk_match:
            pk_cols = [unquote(c.strip()) for c in pk_match.group(1).split(',')]
            table_pks.extend(pk_cols)
            continue

        # Table-level FOREIGN KEY
        fk_match = re.match(
            r'(?:CONSTRAINT\s+\S+\s+)?FOREIGN\s+KEY\s*\(([^)]+)\)\s*'
            r'REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)'
            r'(?:\s+ON\s+DELETE\s+(\S+(?:\s+\S+)?))?'
            r'(?:\s+ON\s+UPDATE\s+(\S+(?:\s+\S+)?))?',
            defn, re.IGNORECASE
        )
        if fk_match:
            local_cols = [unquote(c.strip()) for c in fk_match.group(1).split(',')]
            ref_table = unquote(strip_schema(fk_match.group(2)))
            ref_cols = [unquote(c.strip()) for c in fk_match.group(3).split(',')]
            on_delete = fk_match.group(4).strip().upper() if fk_match.group(4) else None
            on_update = fk_match.group(5).strip().upper() if fk_match.group(5) else None

            table_fks.append({
                "columns": local_cols,
                "references_table": ref_table,
                "references_columns": ref_cols,
                "on_delete": on_delete,
                "on_update": on_update,
            })
            continue

        # Table-level UNIQUE
        uniq_match = re.match(
            r'(?:CONSTRAINT\s+\S+\s+)?UNIQUE\s*\(([^)]+)\)',
            defn, re.IGNORECASE
        )
        if uniq_match:
            uniq_cols = [unquote(c.strip()) for c in uniq_match.group(1).split(',')]
            table_uniques.extend(uniq_cols)
            continue

        # Skip CHECK, INDEX, and other non-column definitions
        if re.match(r'(?:CONSTRAINT|CHECK|INDEX|KEY|UNIQUE\s+INDEX)', defn, re.IGNORECASE):
            continue

        # Column definition
        col_match = re.match(
            r'([^\s]+)\s+(.+)',
            defn, re.IGNORECASE
        )
        if not col_match:
            continue

        col_name = unquote(col_match.group(1))
        col_rest = col_match.group(2).strip()

        # Skip if col_name looks like a keyword (table-level constraint we missed)
        if col_name.upper() in ('PRIMARY', 'FOREIGN', 'CONSTRAINT', 'CHECK',
                                 'INDEX', 'UNIQUE', 'KEY'):
            continue

        # Parse type (first word or word with parens)
        type_match = re.match(r'(\w+(?:\s*\([^)]*\))?(?:\s+\w+)*)', col_rest)
        col_type = ""
        remaining = col_rest
        if type_match:
            # Take the type, but stop at constraint keywords
            type_parts = []
            for word in col_rest.split():
                if word.upper() in ('NOT', 'NULL', 'DEFAULT', 'PRIMARY', 'REFERENCES',
                                     'UNIQUE', 'CHECK', 'AUTO_INCREMENT', 'AUTOINCREMENT',
                                     'SERIAL', 'BIGSERIAL', 'IDENTITY', 'GENERATED',
                                     'CONSTRAINT', 'COLLATE'):
                    break
                type_parts.append(word)
            col_type = ' '.join(type_parts)
            remaining = col_rest[len(col_type):].strip()

        # Handle SERIAL types (PostgreSQL)
        if col_type.upper() in ('SERIAL', 'BIGSERIAL', 'SMALLSERIAL'):
            col_type = col_type.upper()

        nullable = True
        is_pk = False
        is_fk = False
        fk_ref = None
        is_unique = False
        default_value = None

        rest_upper = remaining.upper()

        # NOT NULL
        if 'NOT NULL' in rest_upper:
            nullable = False

        # PRIMARY KEY (inline)
        if 'PRIMARY KEY' in rest_upper:
            is_pk = True
            nullable = False

        # UNIQUE (inline)
        if re.search(r'\bUNIQUE\b', rest_upper):
            is_unique = True

        # REFERENCES (inline FK)
        ref_match = re.search(
            r'REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)',
            remaining, re.IGNORECASE
        )
        if ref_match:
            is_fk = True
            ref_table = unquote(strip_schema(ref_match.group(1)))
            ref_col = unquote(ref_match.group(2).split(',')[0].strip())
            fk_ref = f"{ref_table}.{ref_col}"

        # DEFAULT
        default_match = re.search(
            r"DEFAULT\s+('(?:[^']|'')*'|[^\s,)]+)",
            remaining, re.IGNORECASE
        )
        if default_match:
            default_value = default_match.group(1).strip("'")

        # AUTO_INCREMENT / IDENTITY / SERIAL implies PK candidate
        if any(kw in rest_upper for kw in ['AUTO_INCREMENT', 'AUTOINCREMENT', 'IDENTITY']):
            nullable = False
        if col_type.upper() in ('SERIAL', 'BIGSERIAL', 'SMALLSERIAL'):
            nullable = False

        columns.append({
            "name": col_name,
            "type": parse_column_type(col_type),
            "nullable": nullable,
            "is_primary_key": is_pk,
            "is_foreign_key": is_fk,
            "fk_references": fk_ref,
            "is_unique": is_unique or is_pk,
            "default_value": default_value,
            "description": None,
        })

    # Apply table-level PKs to columns
    for col in columns:
        if col["name"] in table_pks:
            col["is_primary_key"] = True
            col["nullable"] = False
            col["is_unique"] = True

    # Apply table-level FKs to columns
    for fk in table_fks:
        for i, local_col in enumerate(fk["columns"]):
            for col in columns:
                if col["name"] == local_col:
                    col["is_foreign_key"] = True
                    ref_col = fk["references_columns"][i] if i < len(fk["references_columns"]) else fk["references_columns"][0]
                    col["fk_references"] = f"{fk['references_table']}.{ref_col}"

    # Apply table-level UNIQUEs
    for col in columns:
        if col["name"] in table_uniques:
            col["is_unique"] = True

    pk_columns = [c["name"] for c in columns if c["is_primary_key"]]

    return {
        "table_name": raw_name,
        "description": None,
        "columns": columns,
        "primary_key": pk_columns,
        "foreign_keys": table_fks,
        "indexes": None,
        "row_count_estimate": None,
        "grain": None,
        "candidate_entity_types": [],
    }


def parse_ddl(sql: str, verbose: bool = False) -> list[dict]:
    """Parse a DDL string and return list of table definitions."""
    sql = strip_comments(sql)

    # Remove GO statements (SQL Server)
    sql = re.sub(r'\bGO\b', '', sql, flags=re.IGNORECASE)

    # Find all CREATE TABLE statements
    # Match CREATE TABLE ... up to the closing paren + semicolon or next CREATE
    pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[^\s(]+\s*\([^;]*?\)\s*;?'

    # More robust: find CREATE TABLE and match balanced parens
    tables = []
    pos = 0
    while pos < len(sql):
        match = re.search(r'CREATE\s+TABLE', sql[pos:], re.IGNORECASE)
        if not match:
            break

        start = pos + match.start()
        # Find the opening paren
        paren_start = sql.find('(', start)
        if paren_start == -1:
            pos = start + 1
            continue

        # Match balanced parens
        depth = 0
        end = paren_start
        for i in range(paren_start, len(sql)):
            if sql[i] == '(':
                depth += 1
            elif sql[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        statement = sql[start:end]
        table = parse_create_table(statement)
        if table:
            tables.append(table)
            if verbose:
                print(f"  Parsed: {table['table_name']} "
                      f"({len(table['columns'])} columns, "
                      f"{len(table['foreign_keys'])} FKs)", file=sys.stderr)

        pos = end

    return tables


def extract_cross_table_fks(tables: list[dict]) -> list[dict]:
    """Extract all FK relationships across tables."""
    relationships = []
    table_names = {t["table_name"] for t in tables}

    for table in tables:
        for fk in table.get("foreign_keys", []):
            ref_table = fk["references_table"]
            if ref_table in table_names:
                for i, local_col in enumerate(fk["columns"]):
                    ref_col = (fk["references_columns"][i]
                               if i < len(fk["references_columns"])
                               else fk["references_columns"][0])
                    relationships.append({
                        "from_table": table["table_name"],
                        "from_column": local_col,
                        "to_table": ref_table,
                        "to_column": ref_col,
                        "on_delete": fk.get("on_delete"),
                        "on_update": fk.get("on_update"),
                    })

        # Also check inline FKs on columns
        for col in table.get("columns", []):
            if col.get("is_foreign_key") and col.get("fk_references"):
                ref_parts = col["fk_references"].split(".")
                if len(ref_parts) == 2:
                    ref_table, ref_col = ref_parts
                    if ref_table in table_names:
                        # Check if already captured by table-level FK
                        already = any(
                            r["from_table"] == table["table_name"]
                            and r["from_column"] == col["name"]
                            and r["to_table"] == ref_table
                            for r in relationships
                        )
                        if not already:
                            relationships.append({
                                "from_table": table["table_name"],
                                "from_column": col["name"],
                                "to_table": ref_table,
                                "to_column": ref_col,
                                "on_delete": None,
                                "on_update": None,
                            })

    return relationships


def main():
    parser = argparse.ArgumentParser(
        description="Parse SQL DDL into structured schema metadata."
    )
    parser.add_argument("ddl_path", help="Path to DDL file or directory")
    parser.add_argument("--all", action="store_true",
                        help="Parse all .sql files in directory")
    parser.add_argument("--output", "-o", help="Output YAML path")
    parser.add_argument("--output-dir", help="Output directory (one file per DDL)")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    ddl_path = Path(args.ddl_path)

    if ddl_path.is_dir() and args.all:
        sql_files = sorted(ddl_path.glob("*.sql"))
    elif ddl_path.is_file():
        sql_files = [ddl_path]
    else:
        print(f"Not found: {args.ddl_path}", file=sys.stderr)
        sys.exit(1)

    all_tables = []
    for sql_file in sql_files:
        if args.verbose:
            print(f"Parsing: {sql_file}", file=sys.stderr)
        with open(sql_file) as f:
            sql = f.read()
        tables = parse_ddl(sql, verbose=args.verbose)
        all_tables.extend(tables)

    if not all_tables:
        print("No tables found.", file=sys.stderr)
        sys.exit(1)

    # Extract cross-table relationships
    relationships = extract_cross_table_fks(all_tables)

    output = {
        "tables": all_tables,
        "relationships": relationships,
        "total_tables": len(all_tables),
        "total_columns": sum(len(t["columns"]) for t in all_tables),
        "total_foreign_keys": len(relationships),
    }

    if args.verbose:
        print(f"\nSummary: {output['total_tables']} tables, "
              f"{output['total_columns']} columns, "
              f"{output['total_foreign_keys']} FKs", file=sys.stderr)

    if args.output:
        with open(args.output, "w") as f:
            yaml.dump(output, f, default_flow_style=False, sort_keys=False)
        if args.verbose:
            print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(yaml.dump(output, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
