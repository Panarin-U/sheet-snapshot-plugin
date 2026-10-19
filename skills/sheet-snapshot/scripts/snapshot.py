#!/usr/bin/env python3
"""Snapshot an .xlsx / .csv file into a self-contained HTML page that can
render the data and diff it against a file uploaded later.

Standard library only (no openpyxl / pandas needed).

Usage:
    python3 snapshot.py <input.xlsx|.csv> [-o out.html] [--key "Column A,Column B"] [--title "..."]
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"

# Built-in number formats that represent dates/times.
DATE_FMT_IDS = set(range(14, 23)) | {45, 46, 47}


def col_index(ref):
    """'AB12' -> 27 (0-based column index)."""
    n = 0
    for ch in ref:
        if ch.isalpha():
            n = n * 26 + (ord(ch.upper()) - 64)
        else:
            break
    return n - 1


def excel_date(serial, date1904=False):
    base = dt.datetime(1904, 1, 1) if date1904 else dt.datetime(1899, 12, 30)
    d = base + dt.timedelta(days=float(serial))
    d = d.replace(microsecond=0)
    if d.hour == d.minute == d.second == 0:
        return d.strftime("%Y-%m-%d")
    return d.strftime("%Y-%m-%d %H:%M:%S")


def text_of(el):
    """Concatenate all <t> text inside a shared string / inline string."""
    return "".join(t.text or "" for t in el.iter(f"{{{NS['m']}}}t"))


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    names = set(z.namelist())

    shared = []
    if "xl/sharedStrings.xml" in names:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = [text_of(si) for si in root.findall("m:si", NS)]

    # Which style indexes are date formats
    date_styles = set()
    if "xl/styles.xml" in names:
        st = ET.fromstring(z.read("xl/styles.xml"))
        custom_date = set()
        for nf in st.findall("m:numFmts/m:numFmt", NS):
            code = re.sub(r'"[^"]*"|\[[^\]]*\]', "", nf.get("formatCode", "")).lower()
            if re.search(r"[dmyhs]", code):
                custom_date.add(int(nf.get("numFmtId")))
        for i, xf in enumerate(st.findall("m:cellXfs/m:xf", NS)):
            fid = int(xf.get("numFmtId", 0))
            if fid in DATE_FMT_IDS or fid in custom_date:
                date_styles.add(i)

    wb = ET.fromstring(z.read("xl/workbook.xml"))
    pr = wb.find("m:workbookPr", NS)
    date1904 = pr is not None and pr.get("date1904") in ("1", "true")

    rels = {}
    rels_xml = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    for r in rels_xml.iter(PKG_REL):
        target = r.get("Target").lstrip("/")
        rels[r.get("Id")] = target if target.startswith("xl/") else "xl/" + target

    sheets = []
    for s in wb.findall("m:sheets/m:sheet", NS):
        if s.get("state") in ("hidden", "veryHidden"):
            continue
        root = ET.fromstring(z.read(rels[s.get(REL_NS)]))
        rows = {}
        for row in root.findall("m:sheetData/m:row", NS):
            r_idx = int(row.get("r")) - 1
            cells = {}
            for i, c in enumerate(row.findall("m:c", NS)):
                ci = col_index(c.get("r")) if c.get("r") else i
                t = c.get("t", "n")
                v = c.find("m:v", NS)
                if t == "inlineStr":
                    is_ = c.find("m:is", NS)
                    val = text_of(is_) if is_ is not None else None
                elif v is None or v.text is None:
                    val = None
                elif t == "s":
                    val = shared[int(v.text)]
                elif t == "b":
                    val = v.text == "1"
                elif t in ("str", "e"):
                    val = v.text
                else:  # number
                    num = float(v.text)
                    if int(c.get("s", 0)) in date_styles:
                        val = excel_date(num, date1904)
                    else:
                        val = int(num) if num.is_integer() else num
                if val is not None and val != "":
                    cells[ci] = val
            if cells:
                rows[r_idx] = cells
        sheets.append({"name": s.get("name"), "grid": rows})
    return sheets


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        data = list(csv.reader(f))
    grid = {}
    for r, row in enumerate(data):
        cells = {c: v for c, v in enumerate(row) if v != ""}
        if cells:
            grid[r] = cells
    return [{"name": os.path.splitext(os.path.basename(path))[0], "grid": grid}]


def to_table(sheet):
    """First non-empty row = header. Returns {name, headers, rows}."""
    grid = sheet["grid"]
    if not grid:
        return {"name": sheet["name"], "headers": [], "rows": []}
    r_ids = sorted(grid)
    max_c = max(c for cells in grid.values() for c in cells)
    header_cells = grid[r_ids[0]]
    headers = []
    for c in range(max_c + 1):
        h = header_cells.get(c)
        headers.append(str(h).strip() if h is not None else f"Column {c + 1}")
    rows = []
    for r in r_ids[1:]:
        cells = grid[r]
        rows.append([cells.get(c) for c in range(max_c + 1)])
    return {"name": sheet["name"], "headers": headers, "rows": rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--key", help="Comma-separated header names to match rows by (default: auto-detect)")
    ap.add_argument("--title")
    ap.add_argument("--source", help="Override the source label shown on the page (e.g. a Google Sheet URL)")
    args = ap.parse_args()

    ext = os.path.splitext(args.input)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        sheets = read_xlsx(args.input)
    elif ext in (".csv", ".tsv"):
        sheets = read_csv(args.input)
    else:
        sys.exit(f"Unsupported file type: {ext} (use .xlsx or .csv)")

    base = os.path.splitext(os.path.basename(args.input))[0]
    now = dt.datetime.now().astimezone()
    snapshot = {
        "title": args.title or base,
        "source": args.source or os.path.basename(args.input),
        "takenAt": now.isoformat(timespec="seconds"),
        "key": [k.strip() for k in args.key.split(",")] if args.key else None,
        "sheets": [to_table(s) for s in sheets],
    }

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", "assets", "template.html"), encoding="utf-8") as f:
        template = f.read()
    payload = json.dumps(snapshot, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("__SNAPSHOT_JSON__", payload).replace(
        "__PAGE_TITLE__", (snapshot["title"] + " snapshot").replace("<", "&lt;")
    )

    out = args.output or f"{base}-snapshot-{now.strftime('%Y%m%d-%H%M%S')}.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    for s in snapshot["sheets"]:
        print(f"  sheet '{s['name']}': {len(s['headers'])} columns, {len(s['rows'])} rows")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
